/*
Pour les EC
code
lib court
lib long
date de début et de fin
durée enseignement

Attention : 
retourne une ligne par type d'heure. Voir s'il faut regrouper , préciser le type d'heure, ...
*/

drop table if exists schema_fcamanager.enseignement;

drop table if exists schema_fcamanager.tmp_enseignement;
drop table if exists schema_fcamanager.tmp_pia_objet;

create table schema_fcamanager.tmp_enseignement as 
select
	om.id as id_objet,
	om.code as code_objet_maquette,
	form.id as id_formation,
	form.code as code_formation,
	form.libelle_court as libelle_formation,
	om.code_type_objet_formation,
	om.libelle_court,
	om.libelle_long,
	esp.code as code_periode,
	esp.date_debut_validite as debut_periode,
	esp.date_fin_validite as fin_periode,
	sum(fmt.volume_horaire)/3600 as nb_heure
from 
	schema_odf.objet_maquette om 
	LEFT JOIN schema_odf.espace esp ON esp.id = om.id_espace
        INNER JOIN schema_fcamanager.periode r ON r.id = esp.id and r.courante
	LEFT JOIN schema_odf.formats_enseignement fmt ON fmt.id_objet_maquette = om.id
	LEFT JOIN schema_odf.contexte ctx ON ctx.id_objet_maquette = om.id,
	schema_odf.objet_maquette form 
where
	/* filtrer sur le type EC et potentiellement d'autres */
	om.code_type_objet_formation in  ('EC','ENS','UE')
	and ctx.chemin[1] = form.id
group by
	om.id,
	om.code,
	form.id,
	form.code,
	form.libelle_court,
	om.code_type_objet_formation,
	om.libelle_court,
	om.libelle_long,
	esp.code ,
	esp.date_debut_validite ,
	esp.date_fin_validite
order by form.code
;

/* requête permettant d'extraire pour chaque enseignement le ou les PIA  correspondant */
create table schema_fcamanager.tmp_pia_objet (
  code_objet varchar(30)
, code_pia varchar(30)
, code_formation varchar(30)
);

DO $$ DECLARE
    r RECORD;
	r2 RECORD;
	uuid_chemin_item uuid;
BEGIN
	FOR r IN (
		SELECT cc.*, om.code_objet_maquette , om.id_formation, om.code_formation
		FROM schema_odf.contexte cc, 
		schema_fcamanager.tmp_enseignement om
		WHERE cc.id_objet_maquette = om.id_objet 
	) LOOP
	FOREACH uuid_chemin_item in array r.chemin LOOP	
		-- il faut vérifier que l'on se limite aux chemins correspondant au couple code_formation code_objet_maquette
		select ctx.*, om.code
		into r2 
		from schema_odf.contexte ctx, schema_odf.objet_maquette om
		where ctx.id_objet_maquette = uuid_chemin_item AND ctx.chemin[1] = r.id_formation AND ctx.id_objet_maquette = om.id;
		IF r2.temoin_inscription_administrative THEN
			-- raise info '% - % - % - %', uuid_chemin_item, r.code, r2.code, r2.temoin_inscription_administrative;
			INSERT INTO schema_fcamanager.tmp_pia_objet VALUES (r.code_objet_maquette, r2.code, r.code_formation);
		END IF;
	END LOOP;
    END LOOP;
END $$;

/* et on assemble le tout */
create table schema_fcamanager.enseignement as
SELECT tp.code_pia, te.*
FROM schema_fcamanager.tmp_enseignement te, schema_fcamanager.tmp_pia_objet tp
WHERE te.code_objet_maquette = tp.code_objet
AND te.code_formation = tp.code_formation 
ORDER BY te.code_objet_maquette
;

drop table schema_fcamanager.tmp_enseignement;
drop table schema_fcamanager.tmp_pia_objet;
