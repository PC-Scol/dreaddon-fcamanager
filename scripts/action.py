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

# # Fonction pour convertir les dates du format DD/MM/YYYY au format Oracle
# def convertir_date(date_str):
#     try:
#         date_obj = datetime.strptime(date_str, "%d/%m/%Y")
#         return date_obj.strftime("%d-%m-%Y")
#     except ValueError:
#         return None

# Fonction pour convertir les dates du format YYYY-MM-DD au format Oracle
def convertir_date(date_str):
    try:
        date_obj = datetime.strptime(date_str,'')
        return date_obj.strftime("%d-%m-%Y")
    except ValueError:
        print(ValueError)
        return None

# Charger les paramètres
parametres = lire_parametres('config.param')

# Extraire les valeurs de paramètres
COD_LOG_SRC = int(parametres.get('COD_LOG_SRC', 9999))
COD_PER_CRE_ACV = int(parametres.get('COD_PER_CRE_ACV', 1))
COD_ROL_CRE_ACV = int(parametres.get('COD_ROL_CRE_ACV', 10))
PREFIXE = parametres.get('PREFIXE', 'PEG-')

# Constantes pour les colonnes supplémentaires
TEM_STAT_ACN = 1
TEM_EMA_ACN = 1

# Nom des fichiers
input_csv = 'PIA.csv'
output_sql = 'output_actions.sql'

# Structure des requêtes SQL pour ZFCA_ACTION
merge_template_action = """
MERGE INTO ZFCA_ACTION a
USING (SELECT '{cod_ref_com_acn}' AS COD_REF_COM_ACN, '{cod_ref_com_acv}' AS COD_REF_COM_ACV FROM DUAL) b
ON (a.COD_REF_COM_ACN = b.COD_REF_COM_ACN AND a.COD_REF_COM_ACV = b.COD_REF_COM_ACV )
WHEN MATCHED THEN
    UPDATE SET a.LIB_ACN = '{lib_acn}', a.LIC_ACN = '{lic_acn}', a.COD_LOG_SRC = {COD_LOG_SRC}, a.TEM_EN_SVE_ACN = 1, a.COD_ROL_CRE_ACN = {COD_ROL_CRE_ACV}, a.COD_PER_CRE_ACN = {COD_PER_CRE_ACV}, a.COD_ANU_ACN = '{cod_anu_acn}', a.DAT_DEB_VAL_ACN = TO_DATE('{debut_periode}', 'YYYY-MM-DD'), a.DAT_FIN_VAL_ACN = TO_DATE('{fin_periode}', 'YYYY-MM-DD'), a.TEM_STAT_ACN = {TEM_STAT_ACN}, a.TEM_EMA_ACN = {TEM_EMA_ACN}
WHEN NOT MATCHED THEN
    INSERT (ID, COD_REF_COM_ACN, COD_REF_COM_ACV, LIB_ACN, LIC_ACN, COD_LOG_SRC, TEM_EN_SVE_ACN, COD_ROL_CRE_ACN, COD_PER_CRE_ACN, COD_ANU_ACN, DAT_CRE_ACN, DAT_DEB_VAL_ACN, DAT_FIN_VAL_ACN, TEM_STAT_ACN, TEM_EMA_ACN)
    VALUES (action_id_seq.NEXTVAL, b.COD_REF_COM_ACN, b.COD_REF_COM_ACV, '{lib_acn}', '{lic_acn}', {COD_LOG_SRC}, 1, {COD_ROL_CRE_ACV}, {COD_PER_CRE_ACV}, '{cod_anu_acn}', SYSDATE, TO_DATE('{debut_periode}', 'YYYY-MM-DD'), TO_DATE('{fin_periode}', 'YYYY-MM-DD'), {TEM_STAT_ACN}, {TEM_EMA_ACN});
"""

# Lire le fichier CSV et générer les requêtes SQL
with open(input_csv, newline='', encoding='utf-8') as csvfile, open(output_sql, 'a', encoding='utf-8') as sqlfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    
    # Afficher les en-têtes de colonnes
    print(f"En-têtes disponibles : {reader.fieldnames}")
    
    # Générer les requêtes MERGE pour ZFCA_ACTION
    sqlfile.write("\n-- Insertion ou mise à jour dans ZFCA_ACTION\n")
    for row in reader:
        cod_ref_com_acv = PREFIXE + row['code']
        lib_acn = row['libelle_long'].replace("'", "''")
        lic_acn = row['libelle_long'].replace("'", "''")
        cod_anu_acn = row['code_periode'][:4]
        cod_ref_com_acn = f"{PREFIXE}{row['code']}-{cod_anu_acn}"
        # debut_periode = convertir_date(row['debut_periode'])
        # fin_periode = convertir_date(row['fin_periode'])
        debut_periode = row['debut_periode']
        fin_periode = row['fin_periode']
        
        sqlfile.write(merge_template_action.format(
            cod_ref_com_acn=cod_ref_com_acn,
            cod_ref_com_acv=cod_ref_com_acv,
            lib_acn=lib_acn,
            lic_acn=lic_acn,
            COD_LOG_SRC=COD_LOG_SRC,
            COD_ROL_CRE_ACV=COD_ROL_CRE_ACV,
            COD_PER_CRE_ACV=COD_PER_CRE_ACV,
            cod_anu_acn=cod_anu_acn,
            debut_periode=debut_periode,
            fin_periode=fin_periode,
            TEM_STAT_ACN=TEM_STAT_ACN,
            TEM_EMA_ACN=TEM_EMA_ACN
        ))
        sqlfile.write("\n")

print(f"Le fichier SQL '{output_sql}' a été mis à jour avec les commandes pour ZFCA_ACTION.")
