with source as (

    select
            *
    from {{ ref('int_votacao_nominal') }}


)
select * from source