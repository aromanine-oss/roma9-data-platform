# Sprint Preview — Sprint 7: Análise de Competitividade Eleitoral

## 📊 Backlog Priorizado

### 🔄 Em aberto
1. **[DAT] Produto de dados — Painel analítico eleitoral** — Desenvolvimento de dashboard consolidado para visualização das análises eleitorais
2. **README: artigo analítico sobre nacionalização e fragmentação** — Documentação analítica dos resultados obtidos das métricas implementadas

### ✅ Concluído recentemente
- **Métrica NEP: fragmentação partidária por estado** — Implementação de métrica de número efetivo de partidos
- **Métrica PNS: nacionalização partidária** — Cálculo de nacionalização do sistema partidário
- **Notebook: validação das métricas e análise exploratória** — Análise exploratória das métricas implementadas
- **[TEST] Testes de qualidade de dados nas camadas Bronze e Silver** — Validação da qualidade dos dados nas camadas de transformação

---

## 🎯 Sprint 7: Análise de Competitividade Eleitoral

### Issues da Sprint

1. **Implementar modelo dbt para métrica de diferença percentual entre 1º e 2º colocados**
   - Criar cálculo de margem de vitória por município
   - Garantir consistência histórica nos diferentes anos eleitorais

2. **Criar modelo dbt para participação relativa do candidato no total de votos municipais**
   - Implementar métrica de representatividade local por candidato
   - Validar cálculos em diferentes granularidades territoriais

3. **Implementar modelo de concentração de votos com Top N candidatos**
   - Desenvolver métrica de dispersão/concentração do eleitorado
   - Permitir configuração dinâmica do número de candidatos (Top N)

4. **Adicionar testes de validação das métricas de competitividade em múltiplos níveis**
   - Criar testes dbt para validação das métricas em nível municipal
   - Implementar testes de consistência em nível estadual e nacional

5. **Atualizar modelo dimensional para suportar cálculos derivados de competitividade**
   - Refinar fct_votacao_nominal para incluir campos necessários às novas métricas
   - Garantir performance das consultas analíticas

6. **Criar camada analítica Silver para métricas de competitividade eleitoral**
   - Desenvolver modelos intermediários para cálculos de margem e concentração
   - Estruturar dados para consumo otimizado via BI

### 📈 Objetivos da Sprint
- Evoluir a plataforma para análises comparativas de competitividade eleitoral
- Habilitar identificação de cenários de alta competitividade vs hegemonia
- Estruturar base para futuras análises preditivas de comportamento eleitoral

### 🎯 Critérios de Aceite
- Métricas validadas em diferentes níveis de granularidade (município, estado, eleição)
- Modelos dbt com testes de qualidade implementados
- Camada analítica otimizada para consumo via ferramentas de BI
- Documentação técnica atualizada dos novos modelos