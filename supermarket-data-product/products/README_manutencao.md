# Manutenção Mensal de Produtos

## Fluxo de Acompanhamento Mensal

### 1. Carregar Novas Notas Fiscais
```bash
# Executar o loader de HTML
python supermarket-data-product/loaders/nf_data_load_html.py
```

### 2. Verificar Produtos Não Mapeados
```bash
# Executar relatório mensal
python supermarket-data-product/products/manutencao_produtos.py
```

### 3. Se houver produtos não mapeados:
- Analisar os produtos listados
- Decidir se são novos produtos ou variações de existentes
- Atualizar `supermarket-data-product/products/DIM_produtos.sql` com:
  - Novos produtos canônicos em `analytics.dim_produto`
  - Novos mapeamentos em `analytics.dim_produto_descricao`

### 4. Aplicar Atualizações
```sql
-- Executar no banco PostgreSQL
\i supermarket-data-product/products/DIM_produtos.sql
```

### 5. Validar
```bash
# Executar novamente para confirmar
python supermarket-data-product/products/manutencao_produtos.py
```

## Função de Banco de Dados

A função `analytics.relatorio_produtos_nao_mapeados()` está disponível para consultas diretas:

```sql
SELECT * FROM analytics.relatorio_produtos_nao_mapeados();
```

Esta função retorna:
- `produto_descricao`: Descrição do produto na nota fiscal
- `quantidade_itens`: Número de ocorrências
- `valor_total`: Valor total gasto com o produto
- `data_primeira_ocorrencia`: Primeira vez que apareceu
- `data_ultima_ocorrencia`: Última vez que apareceu

## CRUD Interativo de Produtos

Para facilitar a manutenção e correção de categorizações incorretas, foi criado um sistema CRUD interativo:

```bash
# Executar interface interativa
python supermarket-data-product/products/crud_produtos.py
```

### Funcionalidades Disponíveis:

1. **Listar categorias**: Ver todas as categorias disponíveis
2. **Listar produtos**: Navegar pelos produtos com paginação
3. **Buscar produto**: Encontrar produtos por nome parcial
4. **Editar categoria**: Alterar a categoria de um produto existente
5. **Ver descrições**: Listar todas as descrições mapeadas para um produto
6. **Adicionar produto**: Criar novo produto canônico
7. **Adicionar mapeamento**: Mapear nova descrição para produto existente
8. **Ver produtos não mapeados**: Usar relatório de produtos sem mapeamento

### Exemplo de Uso:

```
=== PRODUTOS NAO MAPEADOS ===
Descrição: BANANA PRATA KG
Quantidade: 5
Valor Total: R$ 12,50
Primeira ocorrência: 2024-01-15
Última ocorrência: 2024-03-20

# No CRUD:
1. Verificar se "Banana" já existe como produto canônico
2. Se sim, adicionar mapeamento "BANANA PRATA KG" → "Banana"
3. Se não, criar novo produto "Banana Prata" na categoria "Frutas"
```

### Vantagens sobre edição manual:

- **Interface intuitiva**: Menu interativo em português
- **Validações automáticas**: Verifica existência de produtos/categorias
- **Busca rápida**: Localizar produtos por nome parcial
- **Paginação**: Navegar grandes listas de produtos
- **Transações seguras**: Commits automáticos após validações

## Estratégia de Mapeamento

### Para Novos Produtos:
1. Identificar categoria apropriada (1-11)
2. Adicionar produto canônico em `analytics.dim_produto`
3. Mapear todas as variações conhecidas em `analytics.dim_produto_descricao`

### Para Variações de Produtos Existentes:
1. Apenas adicionar novo mapeamento em `analytics.dim_produto_descricao`
2. Apontar para produto canônico existente

### Regras de Normalização:
- Remover sufixos "KG", "kg"
- Converter "PAO" para "PÃO"
- Converter "QJ"/"QJO" para "QUEIJO"
- Colapsar espaços múltiplos
