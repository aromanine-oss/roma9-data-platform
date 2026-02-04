create or replace table roma9_dw.fct_votacao_nominal_bi
partition by RANGE_BUCKET(
  ano_eleicao,
  GENERATE_ARRAY(1989, 2030, 1)
)
cluster by Estado, SiglaPartido as
select
  *
from roma9_dw.vw_votacao_nominal_looker;
