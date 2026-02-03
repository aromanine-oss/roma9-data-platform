# roma9-data-platform

Personal data platform projetada como um produto analítico de longo prazo, não como uma demo.

Este repositório representa a espinha dorsal da minha plataforma pessoal de dados, construída para suportar análises escaláveis, versionadas e de baixo custo ao longo do tempo.
Seu foco principal é engenharia de dados e modelagem analítica, com produtos analíticos orientados a domínio construídos sobre um data lake consistente e um data warehouse com dbt.

Como exemplo concreto da plataforma em funcionamento, o repositório inclui um data warehouse analítico completo construído a partir de dados públicos em CSV: ingestão, carga, transformação com dbt e visualização no Looker Studio.
Embora intencionalmente simples (uma tabela fato e um pequeno conjunto de dimensões), esse warehouse representa um produto analítico ponta a ponta totalmente funcional.

## Como navegar neste repositório

Este repositório é organizado como uma plataforma analítica de longo prazo, composta por três camadas bem definidas: fundação da plataforma, produtos analíticos e experimentação.

Para quem está visitando o projeto pela primeira vez, o caminho de leitura recomendado é:

1. **Visão geral da plataforma (este README)**
2. **Fundação da plataforma**
   - `data-lake/`
   - `scripts/ingestion/`
3. **Fundação analítica (Data Warehouse)**
   - `dbt/`
4. **Produto analítico entregue**
   - `analytics/politics/party-territorialization/`
5. **Análises orientadas a domínio**
   - `analytics/`
6. **Experimentos e pesquisa**
   - `notebooks/`, `analytics/experiments/`

## Objetivos

### Plataforma (core)
1. Construir um data lake escalável, versionado e de baixo custo
2. Criar pipelines confiáveis e transformações analíticas com dbt
3. Manter uma fundação analítica consistente, validada por um data warehouse ponta a ponta entregue

### Produtos analíticos
4. Realizar análises de redes sociais (NSA/SNA) sobre dados de votação e padrões políticos
5. Aplicar NLP a discursos políticos e outros conjuntos textuais
6. Visualizar resultados analíticos por meio de dashboards

### Exploração e experimentação
7. Explorar LLMs em contextos analíticos e experimentais, ancorados em dados reais
8. Manter um laboratório de dados de longo prazo para projetos futuros e pesquisa

## Estado atual e roadmap

### Estado atual
- Data lake em camadas
- Ingestão reproduzível a partir de CSVs públicos
- Data warehouse dimensional modelado com dbt
- Pelo menos um produto analítico orientado a domínio já entregue
- Dashboards validando a coerência ponta a ponta

### Roadmap
- Expandir o warehouse com novos marts orientados a domínio
- Evoluir produtos com novos fatos, dimensões e métricas
- Aprimorar qualidade de dados, documentação e testes
- Explorar casos analíticos avançados (NSA, NLP, LLMs) ancorados na plataforma
