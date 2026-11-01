## TP3 --- Du pipeline Python à l'ELT moderne avec DuckDB et dbt

### Q1. Pourquoi charger toutes les colonnes en texte, au lieu de laisser DuckDB deviner les types ?

Charger toutes les colonnes en texte permet de conserver les données
brutes sans modification. Si une quantité contient une valeur
incorrecte, par exemple du texte au lieu d'un nombre, DuckDB ne provoque
pas d'erreur pendant le chargement. On pourra ensuite convertir les
données avec `TRY_CAST` et détecter les valeurs invalides.

### Q2. Le total naïf en SQL est aussi faux que celui de l'ancien script Python. Qu'est-ce que cela vous apprend ?

Cela montre que SQL et Python ne garantissent pas automatiquement la
qualité des données. Un pipeline fiable nécessite des règles de
validation, des contrôles et des tests avant de produire un rapport.

### Q3. Si demain une règle de nettoyage est fausse, quel avantage y a-t-il à avoir gardé le brut dans l'entrepôt ?

On peut corriger la règle SQL et refaire les transformations à partir
des données originales, sans devoir récupérer le fichier CSV une
nouvelle fois. Cela permet aussi de conserver une trace des données
reçues.

### Q4. En entreprise, que faudrait-il changer dans profiles.yml et où mettre le mot de passe ?

Il faudrait remplacer le type de connexion DuckDB par l'adaptateur
correspondant, par exemple Snowflake ou BigQuery, et ajouter les
paramètres de connexion nécessaires. Le mot de passe ne doit pas être
écrit directement dans le fichier. Il faut utiliser une variable
d'environnement ou un gestionnaire de secrets pour protéger les
informations sensibles.

### Q5. La commande 1013 a toujours sa ligne dans stg_orders, avec une date vide. Pourquoi ne pas la supprimer dès le staging ?

Parce que le staging doit conserver toutes les lignes, même celles qui
contiennent des erreurs. La suppression se fait plus tard dans la couche
intermediate, où chaque ligne incorrecte reçoit un motif de rejet. Cela
permet de garder une trace des données rejetées.

### Q6. stg_orders est une vue, pas une table. Que se passe-t-il quand vous la lisez ?

Une vue est une requête SQL enregistrée. Quand on la consulte, DuckDB
exécute la requête pour produire les résultats. C'est acceptable pour le
staging parce que cette couche contient surtout des transformations
simples et permet de travailler avec les données les plus récentes.

### Q7. Par quoi dbt a-t-il remplacé {{ ref('stg_orders') }} ?

dbt remplace `{{ ref('stg_orders') }}` par la référence réelle à la vue
créée dans DuckDB, par exemple `main.stg_orders`. Cela permet à dbt de
connaître la dépendance entre les modèles et de respecter leur ordre
d'exécution.

### Q8. Expliquez row_number() over (partition by order_id order by \_row_number).

Cette fonction attribue un numéro à chaque ligne qui possède le même
`order_id`.

-   `PARTITION BY order_id` regroupe les commandes ayant le même
    identifiant.
-   `ORDER BY _row_number` conserve l'ordre original du fichier.
-   La première ligne reçoit le numéro 1.
-   Les lignes suivantes reçoivent 2, 3, etc.

On utilise `_row_number` pour savoir quelle ligne est arrivée en premier
et conserver la première commande, comme avec `duplicated(keep="first")`
en Python.

### Q9. Un analyste veut ajouter le chiffre d'affaires par produit. Quel fichier crée-t-il, dans quel dossier, et doit-il toucher à du Python ?

Il doit créer le fichier `models/marts/revenue_by_product.sql`, dans le
dossier `marts`. Il n'a pas besoin de modifier Python : il peut écrire
directement une requête SQL utilisant `ref('orders_clean')` pour
calculer le chiffre d'affaires par produit.

### Q10. Quand vous avez cassé la règle 5, quel test a échoué ? Quels modèles et quels tests ont été SKIP, et pourquoi ?

Le test `unique` sur la colonne `order_id` de `orders_clean` doit
échouer, car plusieurs lignes possèdent le même identifiant.

Les modèles et tests qui dépendent du modèle concerné, notamment le
rapport `revenue_by_country`, peuvent être ignorés (SKIP). Cela évite de
produire un rapport commercial basé sur des données contenant des
doublons.

### Q11. Équivalents dbt des contrôles du TP1

  -----------------------------------------------------------------------------------
  Contrôle du TP1 (Python)                Son équivalent dbt
  --------------------------------------- -------------------------------------------
  `check_schema`                          Déclaration de la source dans `sources.yml`
                                          et vérification des colonnes utilisées dans
                                          le staging

  Les règles 1 à 6 dans `clean_orders`    Modèle `int_orders_checked.sql`

  `check_reject_rate`                     Test singulier
                                          `assert_reject_rate_below_20_percent.sql`

  `rejected_orders.csv`                   Table `orders_rejected`

  `PIPELINE STOPPED, rien n’est publié`   Échec d'un test dans `dbt build`, avec
                                          blocage des étapes dépendantes
  -----------------------------------------------------------------------------------

### Q12. Le test unitaire n'a pas eu besoin de load_raw.py ni d'aucun fichier CSV. D'où venaient ses données ?

Les données venaient directement du fichier YAML
`int_orders_checked.yml`, dans la section `given`. Les lignes sont
écrites manuellement pour tester le comportement du modèle.

C'est important pour la CI parce que le test peut être exécuté
automatiquement sans charger de fichier CSV ni dépendre des données
réelles. Il est donc rapide, reproductible et indépendant.

### Q13. Demain, la colonne country arrive vide dans la source. Avec le graphe, citez tous les modèles touchés.

Les modèles concernés sont :

1.  `stg_orders`
2.  `int_orders_checked`
3.  `orders_clean`
4.  `orders_rejected`
5.  `revenue_by_country`

Le graphe de lignage permet d'identifier rapidement les dépendances.
Sans ce graphe, il faudrait rechercher manuellement les références dans
les nombreux fichiers SQL, ce qui prendrait beaucoup plus de temps.

### Q14. Comparaison entre le pipeline Python et le pipeline dbt

  ---------------------------------------------------------------------------------------
  Élément                 Pipeline Python (TP1)   Pipeline dbt (TP3)
  ----------------------- ----------------------- ---------------------------------------
  Jour 2 : contrôle qui   `check_reject_rate`     `assert_reject_rate_below_20_percent`
  arrête la chaîne                                

  Jour 3 : erreur         Colonne `unit_price`    Erreur DuckDB : référence à
                          manquante dans la       `unit_price` inexistante dans la source
                          source                  

  Rapport de la veille    Oui, si le pipeline     Dans notre exécution, non pour le jour
  conservé ?              s'arrête avant la       2 : les modèles marts ont été
                          publication du nouveau  reconstruits malgré l'échec du test
                          rapport                 

  Code de sortie          1                       1
  ---------------------------------------------------------------------------------------

**Résultats réellement observés :**

-   Jour 2 : les 6 commandes ont été rejetées avec `invalid_unit_price`.
    Le test du taux de rejet a échoué. `orders_clean` contenait 0 ligne
    et `orders_rejected` contenait 6 lignes. Le total du rapport était
    vide (`NULL`, affiché `NaN`).
-   Jour 3 : DuckDB a signalé une erreur parce que la source contient
    `price` au lieu de `unit_price`. Le modèle `stg_orders` n'a pas pu
    être construit et les opérations dépendantes ont été ignorées.
-   Jour 1 restauré : tous les tests sont repassés avec succès.

**Remarque :** le comportement observé au jour 2 est différent de celui
annoncé dans la fiche du TP. Dans notre exécution, dbt a construit les
marts malgré l'échec du test. Il ne faut donc pas affirmer que l'ancien
rapport a été conservé.

### Q15. Au jour 2, orders_rejected a aussi été SKIP. Est-ce un problème ? Proposez une solution.

Oui, cela peut poser un problème : les données rejetées du jour 2
risquent de ne pas être conservées dans la table de quarantaine si le
modèle est ignoré.

Une solution consiste à séparer le traitement de la quarantaine du
rapport commercial. On peut enregistrer les lignes rejetées dans une
table indépendante, avec un identifiant de lot ou la date de chargement,
avant de lancer le contrôle du taux de rejet. Ainsi, on conserve les
données rejetées du jour 2 tout en empêchant la publication d'un rapport
non fiable.

------------------------------------------------------------------------

### Vérification finale du TP3

**Résultat de `dbt build` après restauration des données du jour 1 :**

``` text
Completed successfully
Done. PASS=16 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=16
```

**Vérification des résultats :**

  Indicateur                   Résultat
  -------------------------- ----------
  Commandes propres                  30
  Commandes rejetées                  5
  Chiffre d'affaires total      8835.40
  Tests réussis                      16
  Tests échoués                       0

**Commit Git :**

``` text
1987831 Move the transformation to SQL with dbt and DuckDB
```

Le pipeline ELT avec DuckDB et dbt est opérationnel sur les données du
jour 1.
