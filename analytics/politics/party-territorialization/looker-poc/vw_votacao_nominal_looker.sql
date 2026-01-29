select
    f.election_key, f.candidate_key, --Só para facilitar o debug dos joins
    -- Grain
    e.election_year                 as ano_eleicao,
    case when e.election_round  = 1 
        then '1º Turno'
            else '2º Turno'
    end                            as turno,
    e.election_desc                 as eleicao_Nome,
    
    o.office_name                   as cargo,
    
    -- Candidato    
    c.candidate_id  ,
    c.party_acr                     as Partido ,
    c.candidate_name                as NomeCandidato,
    c.candidate_ballot_name         as NomeUrna,
    f.qty_nominal_votes             as quantidade_votos_nominais,
    f.qty_valid_votes               as quantidade_votos_validos,
    --Partido/Coalizao
    pc.state_abbreviation            as Estado,
    
    pc.party_id                      as NumeroPartido,
    pc.party_acr                     as SiglaPartido,
    pc.party_name                    as NomePartido,
    
    pc.coalition_type                as TipoCoalizao,
    pc.coalition_name                as NomeCoalizao,
    pc.coalition_decomp              as PartidosCoalizao,
    

    'Final' as Final
from `roma9-data-platform.roma9_dw.fct_votacao_nominal` f

join `roma9-data-platform.roma9_dw.dim_election` e
    on f.election_key = e.election_key


join `roma9-data-platform.roma9_dw.dim_candidate` c
    on f.candidate_key = c.candidate_key

join `roma9-data-platform.roma9_dw.dim_office` o
    on f.office_key = o.office_key

join roma9-data-platform.roma9_dw.dim_party_coalition pc
    on f.coalition_key = pc.coalizao_partido_sk