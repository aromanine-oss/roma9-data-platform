
---

## 📄 `README.pt-br.md` (Português)


# Territorialização e Fragmentação Partidária no Brasil

Este projeto analisa a distribuição territorial da competição partidária no Brasil,
com foco no grau de nacionalização dos partidos e na fragmentação territorial
nas eleições para a Câmara dos Deputados.

A análise cobre o período de 2012 a 2024 e é baseada exclusivamente em
dados eleitorais oficiais do Tribunal Superior Eleitoral (TSE).

**Status:** MVP em desenvolvimento

## Escopo da análise

- País: Brasil
- Cargo: Deputado Federal
- Período: 2012–2024
- Nível eleitoral: Unidade Federativa (UF)
- Unidade de análise: Partido × UF × Eleição
- Votos considerados: Votos nominais válidos, apenas 1º turno

## Dados brutos (TSE)

Os dados eleitorais utilizados neste projeto foram obtidos diretamente
do Tribunal Superior Eleitoral (TSE).

Os arquivos de origem consistem em conjuntos de dados públicos em formato CSV,
contendo a contagem de votos no nível de candidato, desagregados por
zona eleitoral e município.

A camada de dados brutos é tratada como **imutável** e preservada sem
qualquer transformação lógica, garantindo auditabilidade e reprodutibilidade.

- Fonte: Conjuntos de dados eleitorais públicos do TSE
- Formato: CSV
- Cobertura: Eleições de 2012 a 2024
- Granularidade original:
  - Candidato
  - Zona eleitoral
  - Município
  - Ano da eleição
- Transformações aplicadas: Nenhuma

## Fluxo de ingestão de dados

O processo de ingestão segue um fluxo canônico e reproduzível,
independente da implementação exploratória inicial.

1. Download dos arquivos CSV públicos a partir do site do TSE
2. Armazenamento dos arquivos originais no Cloud Storage
3. Carga dos arquivos CSV no BigQuery como tabelas brutas
4. Uso do dataset bruto do BigQuery como **fonte única da verdade**
   para todas as transformações analíticas posteriores

## Princípios da camada raw

- O dataset raw é imutável
- Nenhum filtro, agregação ou enriquecimento é aplicado nesta etapa
- Toda a lógica analítica é aplicada apenas nas camadas downstream
- A camada raw existe exclusivamente para preservar a fidelidade dos dados

```mermaid
graph LR
    TSE[TSE - Arquivos CSV públicos]
    GCS[Cloud Storage]
    BQ_RAW[BigQuery - Dataset raw]

    TSE --> GCS
    GCS --> BQ_RAW
