drop table if exists schema_fcamanager.periode;

create table schema_fcamanager.periode as
select id
, code
, (first_value(code) over (order by annee_universitaire desc) = code) as courante
from schema_odf.espace
where temoin_active
and type_espace = 'P'
;
