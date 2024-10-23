drop table if exists schema_fcamanager.pia;

create table schema_fcamanager.pia as
select
	om.code,
	form.code as code_formation,
	esp.code as code_periode,
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
	LEFT JOIN schema_odf.contexte ctx ON ctx.id_objet_maquette = om.id,
	schema_odf.objet_maquette form 
where
	/* filtrer sur les PIA */
	ctx.temoin_inscription_administrative_active is true
	/* jointure pour récupérer la formation, premier élément du chemin */
	and ctx.chemin[1] = form.id
order by 
	om.code
;
