import csv
from datetime import datetime

# Fonction pour lire les paramètres depuis le fichier .param
def lire_parametres(fichier_param):
    parametres = {}
    with open(fichier_param, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=')
                parametres[key] = value
    return parametres

# Charger les paramètres
parametres = lire_parametres('config.param')

# Extraire les valeurs de paramètres
COD_LOG_SRC = int(parametres.get('COD_LOG_SRC', 9999))
COD_PER_CRE_ACV = int(parametres.get('COD_PER_CRE_ACV', 1))
TEM_EN_SVE_ACV = int(parametres.get('TEM_EN_SVE_ACV', 1))
TEM_STAT_ACV = int(parametres.get('TEM_STAT_ACV', 1))
COD_ROL_CRE_ACV = int(parametres.get('COD_ROL_CRE_ACV', 10))
COD_TYP_ACV = int(parametres.get('COD_TYP_ACV', 1))
PREFIXE = parametres.get('PREFIXE', 'PEG-')
annee_univ = parametres.get('annee_univ', '-2024')  # Valeur par défaut si non spécifiée

# Nom des fichiers
input_csv = 'Enseignement_PIA.csv'
output_sql = 'output_enseignement.sql'

# Structure des requêtes SQL pour ZFCA_ENSEIGNEMENT
merge_template_enseignement = """
MERGE INTO ZFCA_ENSEIGNEMENT e
USING (SELECT '{cod_ref_com_ens}' AS COD_REF_COM_ENS FROM DUAL) b
ON (e.COD_REF_COM_ENS = b.COD_REF_COM_ENS)
WHEN MATCHED THEN
    UPDATE SET e.LIC_ENS = '{lib_ens}', 
               e.LIB_ENS = '{lib_long_ens}', 
               e.COD_LOG_SRC = {COD_LOG_SRC}, 
               e.COD_PER_CRE_ENS = {COD_PER_CRE_ACV},
               e.COD_ROL_CRE_ENS = {COD_ROL_CRE_ACV}, 
               e.COD_TYP_ENS = 8, 
               e.DAT_DEB_ENS = TO_DATE('{debut_periode}', 'DD-MM-YYYY'), 
               e.DAT_FIN_ENS = TO_DATE('{fin_periode}', 'DD-MM-YYYY'),
               e.TEM_ENS_CONVENTIONNABLE = 1, 
               e.TEM_ENS_FACTURABLE = 1, 
               e.TEM_UTI_GRP = 1, 
               e.TYP_EMA_ENS = 'D', 
               e.TEM_EMA_ENS = 1
WHEN NOT MATCHED THEN
    INSERT (COD_ENS, LIC_ENS, LIB_ENS, COD_LOG_SRC, COD_PER_CRE_ENS, COD_ROL_CRE_ENS, COD_TYP_ENS, COD_REF_COM_ENS, DAT_CRE_ENS, DAT_DEB_ENS, DAT_FIN_ENS, TEM_EN_SVE_ENS,
            TEM_ENS_CONVENTIONNABLE, TEM_ENS_FACTURABLE, TEM_UTI_GRP, TYP_EMA_ENS, TEM_EMA_ENS)
    VALUES (ZFCA_ENSEIGNEMENT_ID_SEQ.NEXTVAL, '{lib_ens}', '{lib_long_ens}', {COD_LOG_SRC}, {COD_PER_CRE_ACV}, {COD_ROL_CRE_ACV}, 8, '{cod_ref_com_ens}', SYSDATE,
            TO_DATE('{debut_periode}', 'DD-MM-YYYY'), TO_DATE('{fin_periode}', 'DD-MM-YYYY'), 1, 1, 1, 1, 'D', 1);
"""

# Structure des requêtes SQL pour ZFCA_ACTION_ENSEIGNEMENT
merge_template_action_enseignement = """
MERGE INTO ZFCA_ACTION_ENSEIGNEMENT a
USING (SELECT (SELECT ID FROM ZFCA_ACTION WHERE COD_REF_COM_ACN = '{cod_ref_com_acn}') AS COD_ACN,
              (SELECT COD_ENS FROM ZFCA_ENSEIGNEMENT WHERE COD_REF_COM_ENS = '{cod_ref_com_ens}') AS COD_ENS,
              '{cod_ref_com_acn}' AS COD_REF_COM_ACN,
              '{cod_ref_com_ens}' AS COD_REF_COM_ENS
       FROM DUAL) b
ON (a.COD_ACN = b.COD_ACN AND a.COD_ENS = b.COD_ENS)
WHEN MATCHED THEN
    UPDATE SET a.COD_REF_COM_ACN = b.COD_REF_COM_ACN, a.COD_REF_COM_ENS = b.COD_REF_COM_ENS
WHEN NOT MATCHED THEN
    INSERT (COD_ACN, COD_ENS, COD_REF_COM_ACN, COD_REF_COM_ENS)
    VALUES (b.COD_ACN, b.COD_ENS, b.COD_REF_COM_ACN, b.COD_REF_COM_ENS);
"""

# Lire le fichier CSV et générer les requêtes SQL
with open(input_csv, newline='', encoding='utf-8') as csvfile, open(output_sql, 'a', encoding='utf-8') as sqlfile:
    reader = csv.DictReader(csvfile, delimiter=',')

    # Afficher les en-têtes de colonnes
    print(f"En-têtes disponibles : {reader.fieldnames}")

    # Générer les requêtes MERGE pour ZFCA_ENSEIGNEMENT
    sqlfile.write("\n-- Insertion ou mise à jour dans ZFCA_ENSEIGNEMENT\n")
    for row in reader:
        # Formater les variables nécessaires
        cod_ref_com_ens = row['code_objet_maquette'] + annee_univ
        lib_ens = row['libelle_court'].replace("'", "''").replace("&", "&&")
        lib_long_ens = row['libelle_long'].replace("'", "''").replace("&", "&&")
        debut_periode = datetime.strptime(row['debut_periode'], '%Y-%m-%d').strftime('%d-%m-%Y')
        fin_periode = datetime.strptime(row['fin_periode'], '%Y-%m-%d').strftime('%d-%m-%Y')

        cod_anu_acn = row['code_periode'][:4]
        cod_ref_com_acn = f"{PREFIXE}{row['code_pia']}-{cod_anu_acn}"

        # Écrire la requête MERGE pour ZFCA_ENSEIGNEMENT
        sqlfile.write(merge_template_enseignement.format(
            cod_ref_com_ens=cod_ref_com_ens,
            lib_ens=lib_ens,
            lib_long_ens=lib_long_ens,
            COD_LOG_SRC=COD_LOG_SRC,
            COD_PER_CRE_ACV=COD_PER_CRE_ACV,
            COD_ROL_CRE_ACV=COD_ROL_CRE_ACV,
            debut_periode=debut_periode,
            fin_periode=fin_periode
        ))
        sqlfile.write("\n")

        # Écrire la requête MERGE pour ZFCA_ACTION_ENSEIGNEMENT
        sqlfile.write(merge_template_action_enseignement.format(
            cod_ref_com_acn=cod_ref_com_acn,
            cod_ref_com_ens=cod_ref_com_ens
        ))
        sqlfile.write("\n")

print(f"Le fichier SQL '{output_sql}' a été mis à jour avec les commandes pour ZFCA_ENSEIGNEMENT et ZFCA_ACTION_ENSEIGNEMENT.")
