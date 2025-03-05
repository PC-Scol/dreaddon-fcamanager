drop table if exists schema_fcamanager.periode;

create table schema_fcamanager.periode as
select id
, code
, (now() between date_debut_validite and date_fin_validite) tem_dates
, false courante
from schema_odf.espace
where temoin_active
and type_espace = 'P'
;

-- sélectioner comme courante la première période dont la période de validité
-- englobe la date du jour
with codes as (
select min(code) min
from schema_fcamanager.periode
where tem_dates
)
update schema_fcamanager.periode
set courante = true
from codes
where code = codes.min
;
