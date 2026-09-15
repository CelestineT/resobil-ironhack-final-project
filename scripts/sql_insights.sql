-- -- =============================================================
-- RESOBIL — 10 SQL Insight Scripts (final validated versions)
-- Database: resobil_full (MySQL 8.4)
-- Competence RNCP: C2 (SQL queries for data collection)
-- =============================================================

-- ---------------------------------------------------------------
-- INSIGHT 1: Top 10 antennes by number of active members
-- Business value: identify the most dynamic branches
-- ---------------------------------------------------------------
SELECT 
    a.nom AS antenne_name,
    a.localisation,
    COUNT(m.id_membre) AS total_members,
    a.nb_membres_actifs,
    ROUND(a.nb_membres_actifs / COUNT(m.id_membre) * 100, 1) AS active_rate_pct
FROM antenne a
LEFT JOIN membre m ON m.localite = a.localisation
GROUP BY a.id_antenne, a.nom, a.localisation, a.nb_membres_actifs
ORDER BY a.nb_membres_actifs DESC
LIMIT 10;


-- ---------------------------------------------------------------
-- INSIGHT 2: Digital tools access among members
-- Business value: diagnose the digital divide within the network,
-- to prioritize equipment and digital training investments
-- ---------------------------------------------------------------
SELECT 
    acces_smartphone,
    acces_internet,
    COUNT(*) AS nb_membres,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM besoins_formations_digitale), 1) AS pct_membres
FROM besoins_formations_digitale
GROUP BY acces_smartphone, acces_internet
ORDER BY nb_membres DESC;


-- ---------------------------------------------------------------
-- INSIGHT 3: Total agricultural production by crop type
-- Business value: identify the most produced / most profitable crops
-- ---------------------------------------------------------------
SELECT 
    type_de_cultures,
    COUNT(*) AS nb_records,
    ROUND(SUM(quantite_recolte_sacs), 2) AS total_recolte_sacs,
    ROUND(AVG(quantite_recolte_sacs), 2) AS avg_recolte_sacs,
    ROUND(SUM(revenus_estimes_fcfa), 2) AS total_revenus_fcfa
FROM production_agricole
WHERE type_de_cultures IS NOT NULL
GROUP BY type_de_cultures
ORDER BY total_revenus_fcfa DESC;


-- ---------------------------------------------------------------
-- INSIGHT 4: Member distribution by education level
-- Business value: assess training needs and literacy profile
-- ---------------------------------------------------------------
SELECT 
    niveau_education,
    COUNT(*) AS nb_membres,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM membre), 1) AS percentage
FROM membre
WHERE niveau_education IS NOT NULL 
  AND niveau_education != ''
GROUP BY niveau_education
ORDER BY nb_membres DESC;


-- ---------------------------------------------------------------
-- INSIGHT 5: Financial overview by type of transaction
-- Business value: monitor financial health across the network
-- ---------------------------------------------------------------
SELECT 
    type_versement,
    COUNT(*) AS nb_transactions,
    ROUND(SUM(montant), 2) AS total_amount_fcfa,
    ROUND(AVG(montant), 2) AS avg_amount_fcfa,
    MIN(date_versement) AS first_transaction,
    MAX(date_versement) AS last_transaction
FROM finance
GROUP BY type_versement
ORDER BY total_amount_fcfa DESC;


-- ---------------------------------------------------------------
-- INSIGHT 6: Micro-credit need expressed by members
-- Business value: quantify the potential demand for micro-credit
-- across the network, to size a future financing scheme
-- Note: the demande_micro_credit table (formal requests) contains
-- only 1 row — using the declared need in membre instead, a far
-- more representative table (678 rows)
-- ---------------------------------------------------------------
SELECT 
    besoin_de_micro_credit,
    COUNT(*) AS nb_membres,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM membre), 1) AS pct_membres,
    ROUND(AVG(montant_estime_micro_credit), 0) AS avg_montant_estime_fcfa,
    ROUND(SUM(montant_estime_micro_credit), 0) AS total_montant_estime_fcfa
FROM membre
GROUP BY besoin_de_micro_credit;


-- ---------------------------------------------------------------
-- INSIGHT 7: Multi-dimensional social impact overview
-- Business value: compare several facets of perceived impact in a
-- single view, to identify the least developed dimension
-- (e.g. access to new markets vs. self-confidence)
-- ---------------------------------------------------------------
SELECT 
    COUNT(*) AS nb_reponses,
    ROUND(SUM(CASE WHEN gain_confiance = 'oui' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_gain_confiance,
    ROUND(SUM(CASE WHEN sentiment_respect = 'oui' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_sentiment_respect,
    ROUND(SUM(CASE WHEN nouveaux_contacts = 'oui' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_nouveaux_contacts,
    ROUND(SUM(CASE WHEN amelioration_gestion = 'oui' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS pct_amelioration_gestion,
    ROUND(AVG(nombre_contacts), 1) AS avg_nouveaux_contacts_noues
FROM impact_social;


-- ---------------------------------------------------------------
-- INSIGHT 8: Objective achievement rate by type of collective event
-- Business value: assess the operational effectiveness of events
-- organized by RESOBIL — useful for prioritizing the formats that
-- work best
-- Note: membre_formation and formation_antenne are empty, replaced
-- by evenement_collectif (36+ rows, well populated)
-- ---------------------------------------------------------------
SELECT 
    nom_type_evenement,
    COUNT(*) AS nb_evenements,
    ROUND(AVG(nb_participantes), 1) AS avg_participantes,
    SUM(CASE WHEN objectifs_atteints = 1 THEN 1 ELSE 0 END) AS nb_objectifs_atteints,
    ROUND(SUM(CASE WHEN objectifs_atteints = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS taux_reussite_pct,
    ROUND(AVG(budget_prevu_fcfa), 0) AS avg_budget_prevu_fcfa
FROM evenement_collectif
GROUP BY nom_type_evenement
ORDER BY nb_evenements DESC;


-- ---------------------------------------------------------------
-- INSIGHT 9: Agricultural production profitability by antenne
-- Business value: identify the most profitable branches agriculturally
-- (actual profit margin, not just volume produced)
-- Note: commerce_antenne and production_animale are empty, replaced
-- by suivi_production_agricole (36 rows, rich in financial indicators)
-- ---------------------------------------------------------------
SELECT 
    a.nom AS antenne_name,
    COUNT(*) AS nb_suivis,
    ROUND(SUM(s.chiffre_affaire), 0) AS total_chiffre_affaire_fcfa,
    ROUND(SUM(s.cout_total_production), 0) AS total_couts_fcfa,
    ROUND(SUM(s.marge_beneficiaire), 0) AS total_marge_fcfa,
    ROUND(AVG(s.marge_beneficiaire), 0) AS avg_marge_fcfa
FROM suivi_production_agricole s
JOIN antenne a ON a.id_antenne = s.id_antenne
GROUP BY a.id_antenne, a.nom
ORDER BY total_marge_fcfa DESC;


-- ---------------------------------------------------------------
-- INSIGHT 10: Crop losses — volumes and main causes
-- Business value: identify the most frequent causes of agricultural
-- losses, to target priority corrective actions
-- ---------------------------------------------------------------
SELECT 
    cause_des_pertes,
    COUNT(*) AS nb_cas,
    ROUND(SUM(pertes_eventuelles_sac), 1) AS total_pertes_sacs,
    ROUND(AVG(pertes_eventuelles_sac), 1) AS avg_pertes_sacs
FROM suivi_production_agricole
WHERE pertes_eventuelles_sac > 0 
  AND cause_des_pertes IS NOT NULL
GROUP BY cause_des_pertes
ORDER BY total_pertes_sacs DESC;