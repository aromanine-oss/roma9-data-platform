{{ config(
    materialized = 'incremental',
    unique_key   = 'coalizao_partido_sk',
    on_schema_change = 'fail'
) }}

with source as (

    select
        election_year,
        election_round,
        state_abbreviation,

        party_id,

        coalition_id,
        coalition_type,
        coligation_name       as coalition_name,
        coligation_decomp     as coalition_decomp,

        federation_id,
        federation_name,
        federation_decomp

    from {{ ref('stg_tse__partido_coalizao') }}

),

deduplicated as (

    -- Garante 1 linha por partido dentro da coalizão por turno
    select distinct
        *
    from source

)

select

    -- 🔑 Surrogate key (grain completo)
    {{ dbt_utils.generate_surrogate_key([
        'election_year',
        'election_round',
        'state_abbreviation',
        'coalition_id',
        'party_id',
        'coalition_name',
        'coalition_decomp'
    ]) }} as coalizao_partido_sk,

    -- 🔎 Natural key (debug / lineage)
    {{ dbt_utils.generate_surrogate_key([
        'election_year',
        'election_round',
        'state_abbreviation',
        'coalition_id',
        'party_id',
        'coalition_name',
        'coalition_decomp'
    ]) }} as coalizao_partido_nk,

    -- 📦 Contexto eleitoral
    election_year,
    election_round,
    state_abbreviation,

    -- 🏛️ Partido
    party_id,

    -- 🤝 Coalizão
    coalition_id,
    coalition_type,
    coalition_name,
    coalition_decomp,

    -- 🧱 Federação
    federation_id,
    federation_name,
    federation_decomp,

    -- 🕒 Metadados
    current_timestamp as created_at,
    current_timestamp as updated_at

from deduplicated
