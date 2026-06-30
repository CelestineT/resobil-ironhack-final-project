# Registre des traitements de données à caractère personnel — RESOBIL

*Conforme à l'article 30 du RGPD (registre des activités de traitement)*

## Traitement n°1 : Gestion des membres de la coopérative

| Champ | Détail |
|---|---|
| Responsable de traitement | RESOBIL (Réseau Oyili Bininga du Cameroun) |
| Finalité | Gestion administrative des adhésions, suivi des activités, accompagnement socio-économique des membres |
| Base légale | Exécution d'une mission d'intérêt collectif / consentement à l'adhésion |
| Catégories de données | Identité (nom, prénom), coordonnées (téléphone, WhatsApp, email), localisation (village, antenne), données socio-économiques (niveau d'éducation, activité principale, nb enfants à charge) |
| Catégories de personnes concernées | Membres de la coopérative (2000+) |
| Destinataires | Coordinatrices d'antenne, équipe digitale RESOBIL, Présidente |
| Transferts hors UE | Oui — hébergement Azure (région à préciser), traitement par l'équipe consultante basée en France |
| Durée de conservation | Durée d'adhésion + 5 ans (archivage légal coopératif) |
| Mesures de sécurité | Connexion chiffrée TLS à la base Azure MySQL, accès par rôle (RBAC), anonymisation des exports d'analyse (`extract_resobil.py --anonymize`) |

## Traitement n°2 : Suivi de production agricole et animale

| Champ | Détail |
|---|---|
| Finalité | Pilotage agricole, statistiques de rendement, aide à la décision |
| Base légale | Intérêt légitime de la coopérative |
| Catégories de données | Données de production liées à un membre indirectement (via antenne) — pas de donnée personnelle directe sauf rattachement au membre |
| Durée de conservation | 5 ans |

## Traitement n°3 : Enquêtes de satisfaction et impact social

| Champ | Détail |
|---|---|
| Finalité | Mesure d'impact, reporting bailleurs de fonds (OIF, AWDF, etc.) |
| Base légale | Intérêt légitime / obligation contractuelle vis-à-vis des bailleurs |
| Catégories de données | Avis, ressenti, indicateurs d'impact agrégés |
| Anonymisation | Les exports destinés aux bailleurs sont agrégés au niveau antenne, sans identification individuelle |

## Traitement n°4 : API REST et exports BigQuery

| Champ | Détail |
|---|---|
| Finalité | Mise à disposition de données pour le pilotage (dashboards Power BI/Google Sheets) |
| Mesures spécifiques | L'API ne doit jamais exposer les champs PII bruts en environnement de démonstration ; utiliser le mode `--anonymize` du script d'extraction avant tout export vers un environnement cloud externe (BigQuery) |
| Droits des personnes | Droit d'accès, de rectification et d'effacement exercé via la coordinatrice d'antenne ou la Présidente RESOBIL |

## Mesures organisationnelles

- Accès à la base Azure MySQL restreint par compte nominatif (pas de compte partagé).
- Logs d'extraction conservés (voir `logs/`) pour traçabilité (qui a extrait quoi, quand).
- Sensibilisation des coordinatrices à la confidentialité des données collectées sur le terrain.

*Document à compléter avec les coordonnées du DPO ou référent RGPD désigné par RESOBIL avant publication finale.*
