# RESOBIL — Modèle de données Merise (MCD / MLD)

## 1. Modèle Conceptuel de Données (MCD) — description textuelle

### Entités principales

| Entité | Description | Identifiant |
|---|---|---|
| ANTENNE | Antenne locale RESOBIL (branche régionale) | id_antenne |
| MEMBRE | Membre de la coopérative | id_membre |
| COORDINATRICE | Coordinatrice rattachée à une antenne | id_coo |
| ACTIVITE_ANTENNE | Activité organisée par une antenne | id_activite_antenne |
| ACTIVITE_MENSUELLE | Suivi mensuel d'une activité | id_activite_mensuelle |
| EVENEMENT_COLLECTIF | Événement collectif (réunion, formation collective) | id_evenement |
| FORMATION | Catalogue des formations proposées | id_formation |
| MEMBRE_FORMATION | Inscription d'un membre à une formation | id_membre, id_formation |
| PROJET | Projet financé/suivi par la coopérative | id_projet |
| PRODUCTION_AGRICOLE | Données de production agricole | id_production_agricole |
| PRODUCTION_ANIMALE | Données de production animale | id_production_animale |
| SUIVI_PRODUCTION_AGRICOLE | Suivi périodique de production | id_suivi_production_agricole |
| COMMERCE_ANTENNE | Activité commerciale rattachée à une antenne | id_commerce |
| SATISFACTION_MEMBRE | Enquête de satisfaction | id_satisfaction |
| IMPACT_SOCIAL | Indicateurs d'impact social | id_impact |
| VERSEMENT | Mouvements financiers (cotisations, dons) | id_versement |
| BESOIN_FORMATION_DIGITALE | Besoins numériques exprimés par les membres | id_besoin |

### Relations (associations) et cardinalités

- ANTENNE (1,n) — POSSEDE — MEMBRE (1,1) : un membre appartient à une seule antenne ; une antenne a plusieurs membres (table de liaison `membre_antenne` avec rôle, date_debut, date_fin → association porteuse de propriétés, donc modélisée comme entité associative).
- ANTENNE (1,1) — ENCADREE_PAR — COORDINATRICE (0,n) : une coordinatrice peut suivre plusieurs antennes dans le temps.
- ANTENNE (1,n) — ORGANISE — ACTIVITE_ANTENNE (1,1)
- ACTIVITE_ANTENNE (1,n) — DECLINEE_EN — ACTIVITE_MENSUELLE (1,1)
- ANTENNE (1,n) — TIENT — EVENEMENT_COLLECTIF (1,1)
- MEMBRE (0,n) — PARTICIPE — EVENEMENT_COLLECTIF (0,n) (association n,n si table de jonction participants)
- MEMBRE (0,n) — SUIT — FORMATION (0,n) via MEMBRE_FORMATION (association porteuse : date_inscription, resultat, certificat)
- ANTENNE (1,n) — PORTE — PROJET (0,n), PROJET (0,1) — DIRIGE_PAR — MEMBRE (chef_projet)
- ANTENNE (1,n) — GENERE — PRODUCTION_AGRICOLE / PRODUCTION_ANIMALE (1,1)
- PRODUCTION_AGRICOLE (1,n) — SUIVIE_PAR — SUIVI_PRODUCTION_AGRICOLE (1,1)
- ANTENNE (1,n) — EXPLOITE — COMMERCE_ANTENNE (1,1)
- MEMBRE (1,1) — EXPRIME — SATISFACTION_MEMBRE (0,n)
- ANTENNE (1,1) — MESURE — IMPACT_SOCIAL (0,n)
- MEMBRE (1,n) — EFFECTUE — VERSEMENT (0,n)
- MEMBRE (1,1) — EXPRIME — BESOIN_FORMATION_DIGITALE (0,n)

## 2. Règles de gestion (extrait, C1/C2)

- RG1 : Un membre est rattaché à une seule antenne active à la fois (contrôlé par `actif` + `date_fin` dans `membre_antenne`).
- RG2 : Une coordinatrice peut être affectée successivement à plusieurs antennes, jamais à deux antennes simultanément actives.
- RG3 : Un projet doit avoir un chef de projet identifié parmi les membres de l'antenne porteuse.
- RG4 : Les données de production (agricole/animale) sont rattachées à une période (`periode_de_production`) et ne peuvent être saisies pour une date future.
- RG5 : Toute donnée à caractère personnel (téléphone, email, village de résidence) est soumise au registre RGPD (voir `rgpd_register.md`).

## 3. Modèle Logique de Données (MLD) — passage au relationnel

Le passage MCD → MLD suit les règles standard :
- Chaque entité devient une table, l'identifiant devient clé primaire.
- Les associations (1,n)–(1,1) : la clé primaire du côté (1,1)... en réalité ici c'est l'inverse classique : la clé étrangère est placée côté "n" (ex : `id_antenne` dans `membre`, `production_agricole`, `activite_antenne`, etc.) — conforme à ce qui est observé dans le schéma Azure MySQL fourni.
- Les associations (n,n) porteuses de données (ex : `membre_formation`, `membre_antenne`) deviennent des tables de liaison avec clé primaire composite ou clé technique + clés étrangères vers les deux entités liées.

Ceci correspond exactement au schéma physique déjà implémenté sur Azure Database for MySQL (cf. captures `Tables_RESOBIL.png` et `Tables_RESOBIL_2.png`).

## 4. Justification pour le jury (C1 — Concevoir un schéma)

Ce schéma a été conçu en respectant la 3ème forme normale (3NF) : pas de dépendance transitive (ex. les coordonnées d'un membre ne sont stockées que dans `membre`, pas dupliquées dans `production_agricole`), atomicité des attributs, et clé primaire unique par entité. Les enums (`statut ENUM(...)`) garantissent l'intégrité des valeurs métier (ex. statut d'antenne : actif/inactif/en_creation).
