with source as (

    select *
    from {{ source('tse', 'tse_votacao_nominal_municipio_zona') }}

),

renamed as (

    select
        SAFE_CAST(ANO_ELEICAO AS INT64)                 AS election_year,
		SAFE_CAST(CD_ELEICAO AS INT64)					AS election_cod,
		DS_ELEICAO										AS election_desc,
		SAFE.PARSE_DATE('%d/%m/%Y', DT_ELEICAO)		    AS election_date,
		SAFE_CAST(NR_TURNO AS INT64)                    AS election_round,
        SAFE_CAST(CD_MUNICIPIO AS INT64)             	AS municipality_id,
        NM_MUNICIPIO              						AS municipality_name,
		SAFE_CAST(NR_ZONA AS INT64)                     AS zone_number,
        SAFE_CAST(SQ_CANDIDATO AS INT64)                AS candidate_id,
        SAFE_CAST(NR_CANDIDATO AS INT64)                AS candidate_nr, 
        NM_CANDIDATO              					    AS candidate_name,
        NM_SOCIAL_CANDIDATO							    AS candidate_social_name,
        COALESCE(NM_URNA_CANDIDATO, 'Não informado')    AS candidate_ballot_name,
		SAFE_CAST(QT_VOTOS_NOMINAIS AS INT64) 		    AS qty_votes,
		SAFE_CAST(QT_VOTOS_NOMINAIS_VALIDOS AS INT64)   AS qty_valid_votes,
	    SG_UF								            AS state_abbreviation,
		SAFE_CAST(NR_PARTIDO AS INT64)		    		AS party_id,
		SG_PARTIDO										AS party_acr,
		NM_PARTIDO                  					AS party_name,
		cd_cargo										AS office_id,
		ds_cargo										AS office_name,
		SAFE_CAST(NR_FEDERACAO AS INT64)				AS federation_id,
		NM_FEDERACAO									AS federation_name,
		SG_FEDERACAO									AS federation_acr,
		DS_COMPOSICAO_FEDERACAO							AS federation_decomp,
		SAFE_CAST(SQ_COLIGACAO AS INT64)				AS federation_sq,
		NM_COLIGACAO									AS coligation_name,
		DS_COMPOSICAO_COLIGACAO					    	AS coligation_decomp,
        current_timestamp()               				AS ingested_at
    from source

)

select *
from renamed
