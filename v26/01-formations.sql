/* Besoin pour les formations (diplomes?)
 et pour les PIA
code
lib court
lib long
date de début et de fin de l'accréditation : ceci est dans les diplomes, avec le tableau de uuid periode valididté
durée en mois et en heure de la formation
domaine SISE
nb crédit ECTS
niveau LMD
niveau en entrée et en sortie
Diplome donné par la formation
Numéro RNCP
*/

drop table if exists schema_fcamanager.formation;

create table schema_fcamanager.formation as
select
	om.code,
	esp.code code_periode,
	om.libelle_court,
	om.libelle_long,
	esp.date_debut_validite as debut_periode,
	esp.date_fin_validite as fin_periode,
	'' as debut_accreditation,
	'' as fin_accreditation,
	esp.date_fin_validite - esp.date_debut_validite as duree_formation_jour,
	om.code_domaine_formation, /* aller chercher le libellé et le code SISE, fournir la nomenclature */
	ctx.credit_ects as nb_credit_ects,
	om.code_niveau_diplome, /* fournir la nomenclature en plus, ajouter code_sise et libellé */
	'' as niveau_entree,
	'' as niveau_sortie,
	'' as diplomes,
	'' numero_rncp	
from 
	schema_odf.objet_maquette om
	LEFT JOIN schema_odf.espace esp ON esp.id = om.id_espace
        INNER JOIN schema_fcamanager.periode r ON r.id = esp.id and r.courante
	LEFT JOIN schema_odf.contexte ctx ON ctx.id_objet_maquette = om.id
where
	om.code_type_objet_formation = 'FORMATION' 
;
