with source as (

    select *
    from {{ source('tse', 'tse_votacao_nominal_municipio_zona') }}

),

renamed as (

    select
        SAFE_CAST(ANO_ELEICAO AS INT64)                 AS election_year,
		SAFE.PARSE_DATE('%d/%m/%Y', DT_ELEICAO)		    AS election_date,
		SAFE_CAST(CD_ELEICAO AS INT64)					AS election_cod,
		SAFE_CAST(NR_TURNO AS INT64)                    AS election_round,
                
	    SG_UF								            AS state_abbreviation,
		SAFE_CAST(SQ_COLIGACAO AS INT64)				AS coalition_id, --This attribute was renamed to avoid confusion with federation_id. It's the same for both (caligation/federation)
				
		CASE WHEN  UPPER(TP_AGREMIACAO) = 'COLIGAÇÃO' 
				THEN 'Coligação'
			   WHEN  UPPER(TP_AGREMIACAO) = 'PARTIDO ISOLADO' 
				THEN 'Partido Isolado'
			   ELSE 'FEDERAÇÃO' 
		  END AS coalition_type,

		CASE WHEN  UPPER(TP_AGREMIACAO) = 'COLIGAÇÃO' 
				THEN NM_COLIGACAO
			   WHEN  UPPER(TP_AGREMIACAO) = 'PARTIDO ISOLADO' 
				THEN NM_COLIGACAO
			   ELSE NULL
		  END 											AS coligation_name,
		
		CASE WHEN  UPPER(TP_AGREMIACAO) = 'COLIGAÇÃO' 
				THEN DS_COMPOSICAO_COLIGACAO
			   WHEN  UPPER(TP_AGREMIACAO) = 'PARTIDO ISOLADO' 
				THEN DS_COMPOSICAO_COLIGACAO
			   ELSE NULL
		  END 			   						    	AS coligation_decomp,
        
        SAFE_CAST(NULLIF(NR_FEDERACAO, '-1') AS INT64)  AS federation_id,
				
		NULLIF(NM_FEDERACAO, '#NULO#')                AS federation_name,
		NULLIF(SG_FEDERACAO, '#NULO#')				  AS federation_acr,
		NULLIF(DS_COMPOSICAO_FEDERACAO, '#NULO#')     AS federation_decomp,
						       
        current_timestamp()               			  AS ingested_at
    from source

)

select *
from renamed
