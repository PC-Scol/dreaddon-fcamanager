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

# Nom des fichiers
input_csv = 'PIA.csv'
output_sql = 'output_activite.sql'

# Template pour les requêtes SQL
merge_template = """
MERGE INTO ZFCA_ACTIVITE a
USING (SELECT '{code}' AS COD_REF_COM_ACV FROM DUAL) b
ON (a.COD_REF_COM_ACV = b.COD_REF_COM_ACV )
WHEN MATCHED THEN
    UPDATE SET a.LIB_ACV = '{libelle_long}', 
               a.LIC_ACV = '{libelle_court}', 
               a.COD_LOG_SRC = {COD_LOG_SRC}, 
               a.TEM_EN_SVE_ACV = {TEM_EN_SVE_ACV}, 
               a.COD_PER_CRE_ACV = {COD_PER_CRE_ACV}, 
               a.COD_ROL_CRE_ACV = {COD_ROL_CRE_ACV}, 
               a.TEM_STAT_ACV = {TEM_STAT_ACV}, 
               a.COD_TYP_ACV = {COD_TYP_ACV}
WHEN NOT MATCHED THEN
    INSERT (ID, COD_REF_COM_ACV, LIB_ACV, LIC_ACV, COD_LOG_SRC, COD_PER_CRE_ACV, 
            TEM_EN_SVE_ACV, COD_ROL_CRE_ACV, TEM_STAT_ACV, DAT_CRE_ACV, COD_TYP_ACV)
    VALUES (activite_id_seq.NEXTVAL, '{code}', '{libelle_long}', '{libelle_court}', 
            {COD_LOG_SRC}, {COD_PER_CRE_ACV}, {TEM_EN_SVE_ACV}, {COD_ROL_CRE_ACV}, 
            {TEM_STAT_ACV}, SYSDATE, {COD_TYP_ACV});
"""

# Lire le fichier CSV et générer les requêtes SQL
try:
    with open(input_csv, newline='', encoding='utf-8') as csvfile, open(output_sql, 'w', encoding='utf-8') as sqlfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        
        # Afficher les en-têtes de colonnes
        print(f"En-têtes disponibles : {reader.fieldnames}")
        
        # Suivi des codes déjà traités pour éviter les doublons
        seen_codes = set()

        # Générer la requête d'insertion dans LOGICIEL_SOURCE
        sqlfile.write("-- Insertion dans LOGICIEL_SOURCE\n")
        sqlfile.write("""
MERGE INTO LOGICIEL_SOURCE ls
USING (SELECT 9999 AS ID, 'PEGASE' AS LIB_LOG_SRC, 'PEGA' AS COD_LOG_SRC, 0 AS TEM_REF_PRINCIPAL FROM DUAL) src
ON (ls.COD_LOG_SRC = src.COD_LOG_SRC)
WHEN NOT MATCHED THEN
    INSERT (ID, LIB_LOG_SRC, COD_LOG_SRC, TEM_REF_PRINCIPAL)
    VALUES (src.ID, src.LIB_LOG_SRC, src.COD_LOG_SRC, src.TEM_REF_PRINCIPAL);
\n
""")
        
        # Générer les requêtes MERGE pour ZFCA_ACTIVITE
        sqlfile.write("-- Insertion ou mise à jour dans ZFCA_ACTIVITE\n")
        for row in reader:
            try:
                # Construire le code de référence en ajoutant le préfixe
                code = PREFIXE + row['code']

                # Éviter les doublons
                if code in seen_codes:
                    continue
                seen_codes.add(code)

                # Récupérer les libellés et échapper les apostrophes
                libelle_long = row['libelle_long'].replace("'", "''")
                libelle_court = row['libelle_court'].replace("'", "''")

                # Générer la requête MERGE pour chaque ligne
                sqlfile.write(merge_template.format(
                    code=code,
                    libelle_long=libelle_long,
                    libelle_court=libelle_court,
                    COD_LOG_SRC=COD_LOG_SRC,
                    COD_PER_CRE_ACV=COD_PER_CRE_ACV,
                    TEM_EN_SVE_ACV=TEM_EN_SVE_ACV,
                    COD_ROL_CRE_ACV=COD_ROL_CRE_ACV,
                    TEM_STAT_ACV=TEM_STAT_ACV,
                    COD_TYP_ACV=COD_TYP_ACV
                ))
                sqlfile.write("\n")
            except KeyError as e:
                # Tracer les erreurs liées à des colonnes manquantes
                print(f"Erreur dans la ligne avec le code '{row.get('code', 'N/A')}': {e}")
                sqlfile.write(f"-- Erreur avec le code '{row.get('code', 'N/A')}': {e}\n")

    print(f"Le fichier SQL '{output_sql}' a été généré avec succès.")

except FileNotFoundError as e:
    print(f"Erreur : le fichier '{input_csv}' est introuvable ({e})")
except Exception as e:
    print(f"Erreur inattendue : {e}")
