# 🛒 Supermarket Data Product

Sistema completo de extração, transformação e gestão de dados de notas fiscais eletrônicas (NFe) de supermercados. Integra dados brutos em HTML/PDF, normaliza-os através de staging tables, e fornece uma dimensão de produtos padronizada para análises.

---

## 📋 Visão Geral

Este projeto implementa um pipeline ETL (Extract, Transform, Load) para processar notas fiscais eletrônicas de estabelecimentos comerciais, estruturando os dados em camadas:

```
Dados Brutos (HTML/PDF)
       ↓
  [Loaders] → Extração de cabeçalho e itens
       ↓
 Staging Layer (PostgreSQL)
       ↓
  [Fixes] → Limpeza e normalização
       ↓
 Analytics Layer (Dimensões)
       ↓
  [Audits] → Validação e controle de qualidade
```

### Características principais

- ✅ **Carregamento incremental**: Evita duplicatas via constraints únicos e verificação de notas já processadas
- ✅ **Suporte multi-formato**: HTML e PDF (para futuras extensões)
- ✅ **Deduplicação automática**: Item-level com índice único `(id_nota, item_index)`
- ✅ **Normalização de produtos**: Aplicação de regras de limpeza e mapeamento canônico
- ✅ **Dimensão de produtos**: 12 categorias com 479+ produtos estruturados
- ✅ **Auditoria integrada**: Validação de contagens, gaps e conformidade

---

## 🗂️ Estrutura de Pastas

### `loaders/` - Extração de Dados

Responsável por ler arquivos HTML/PDF e extrair dados estruturados para staging tables.

| Arquivo | Função |
|---------|--------|
| **`nf_data_load_html.py`** | Extrator principal de HTML. Parseia estrutura XML-based das NF-e, extrai cabeçalho e itens com normalização de produto |
| **`nf_data_load_html_split.py`** | Variante que processa arquivos HTML pré-divididos (`_header.html`, `_item.html`) |
| **`nf_data_loader_pdf.py`** | Extrator alternativo para formato PDF (usando `pdfplumber`) |

#### Fluxo típico (nf_data_load_html.py)

```python
1. extract_header(html_path)
   → Regex: chave, data_emissao, estabelecimento, CNPJ
   
2. extract_html_data(html_path)
   → CSS selectors: produto, codigo_produto, quantidade, valor_unitario
   
3. nota_exists() 
   → Check: produto já está em stg_nf_header?
   
4. INSERT INTO staging.stg_nf_header/stg_nf_item
   → ON CONFLICT DO NOTHING (idempotência)
```

#### Configuração

```env
DB_HOST=localhost
DB_NAME=roma9_platform
DB_USER=postgres
DB_PASS=xxx
DB_PORT=5432
```

**Diretórios de entrada:**
- `data/Notas Fiscais/2026/{mes}/` (HTML/PDF)

---

### `products/` - Gestão de Dimensão de Produtos

Define estrutura dimensional e mantém catálogo de produtos canônicos.

| Arquivo | Função |
|---------|--------|
| **`DIM_produtos.sql`** | DDL: tabelas `dim_categoria_produto`, `dim_produto`, `dim_produto_descricao` com ~360 inserts iniciais |
| **`add_missing_products.sql`** | DML: insere produtos descobertos dinamicamente nas notas fiscais (127+ novos) |
| **`crud_produtos.py`** | CRUD CLI para gestão manual de categorias e produtos |
| **`manutencao_produtos.py`** | Utilitários para manutenção: análise de duplicatas, categorização, etc. |

#### Estrutura de Dados

**`dim_categoria_produto`** (12 categorias)
```
1 - Frutas e Verduras
2 - Carnes e Aves
3 - Frios e Laticínios
...
12 - Pets
```

**`dim_produto`**
```
produto_id | nome_canonico         | categoria_id
1          | Abacate / Avocado     | 1
32         | Queijo Mussarela      | 3
...
479        | Vinho Undurraga       | 7
```

**`dim_produto_descricao`** (Lookup Table)
```
descricao (raw from NFe)          → produto_id (FK)
"QUEIJO MUSSARELA GALBANI 500G"  → 32
"QUEIJO MOZZ BOFATA IMPORTADO"   → 32
```

---

### `fixes/` - Limpeza e Normalização

Scripts corretivos para melhorar qualidade de dados na dimensão de produtos.

| Arquivo | Função |
|---------|--------|
| **`fix_dim_produto_canonical_names.py`** | Limpa 127+ nomes canônicos com regex patterns (bebidas, carnes, lácteos, etc.) e remoção de tokens (*PR*, KG, CX, LT, etc.) |
| **`classify_missing_product_categories.py`** | Auto-classifica novos produtos em categorias usando keyword matching |
| **`migrate_add_item_index_stg_nf_item.py`** | Migração: adiciona coluna `item_index` e índice único para deduplicação |
| **`update_canonical_names_mapping.py`** | Aplica mapeamento DE-PARA de nomes canônicos (caso-a-caso) |
| **`update_canonical_names_fuzzy.py`** | Busca fuzzy para atualizar nomes com similaridade mínima (0.7) |
| **`verify_manual_fixes.py`** | Verifica status das correções aplicadas |

#### Exemplo: Cleaning com Patterns

```python
"COCA COLA SAC" 
  → SPECIAL_CANONICAL_MAP: matches /COCA\s*COLA/ 
  → "Refrigerante Coca-Cola"

"CALDO KNORR ZERO SAL GALINHA CX 48G"
  → Remove tokens: CX, G, "ZERO SAL"
  → Apply title case
  → "Caldo Knorr Galinha 48G"
```

---

### `audits/` - Auditoria e Validação

Valida integridade e completude dos dados durante o pipeline.

| Arquivo | Função |
|---------|--------|
| **`audit_nf_item_counts.py`** | Compara contagens: itens em HTML vs banco de dados (detecta gaps na ingestão) |
| **`audit_nf_missing_items.py`** | Identifica notas fiscais com items faltando vs contagem esperada |
| **`audit_nf_item_counts_results.json`** | Output: relatório JSON das discrepâncias |
| **`audit_nf_missing_items_results.json`** | Output: lista de gaps por nota fiscal |

#### Exemplo de Auditoria

```json
{
  "source_type": "single",
  "source_path": "data/Notas Fiscais/2026/abr/nf_001.html",
  "id_nota": "35260412345678901234567890123456789012345",
  "data_emissao": "2026-04-15",
  "html_item_count": 12,
  "db_item_count": 11,
  "status": "GAP"  // ← falta 1 item no banco
}
```

---

## 🚀 Como Usar

### 1. Setup Inicial

```bash
# Clonar e configurar ambiente
cd roma9-data-platform
python -m venv .venv
source .venv/Scripts/activate  # Windows
pip install -r requirements.txt

# Configurar .env
export DB_HOST=localhost
export DB_NAME=roma9_platform
export DB_USER=postgres
export DB_PASS=xxx
export DB_PORT=5432
```

### 2. Criar Schema de Produtos

```bash
# Criar dimensão de produtos
psql -h $DB_HOST -d $DB_NAME -U $DB_USER < products/DIM_produtos.sql

# Adicionar produtos faltando (após primeira ingestão)
psql -h $DB_HOST -d $DB_NAME -U $DB_USER < products/add_missing_products.sql
```

### 3. Carregar Notas Fiscais

```bash
# Carregamento incremental de HTML (abril/2026)
python loaders/nf_data_load_html.py

# Output esperado:
# [18:30] Conectando ao PostgreSQL...
# [18:31] Processando: data/Notas Fiscais/2026/abr/nf_001.html
# [18:31] ID Nota: 35260412345678901234567890123456789012345
# [18:32] ✓ 12 itens inseridos (ou ignorados se duplicado)
# [18:45] Total: 456 notas, 3,892 itens
```

### 4. Normalizar Nomes de Produtos

```bash
# Limpar nomes canônicos (dry-run)
python fixes/fix_dim_produto_canonical_names.py --dry-run

# Aplicar limpeza
python fixes/fix_dim_produto_canonical_names.py

# Aplicar mapeamento DE-PARA
python fixes/update_canonical_names_fuzzy.py
```

### 5. Auditar Dados

```bash
# Gerar relatório de discrepâncias
python audits/audit_nf_item_counts.py

# Verificar gaps
python audits/audit_nf_missing_items.py

# Ver resultados
cat audits/audit_nf_item_counts_results.json | jq '.[] | select(.status=="GAP")'
```

---

## 🔍 Schemas PostgreSQL

### `staging` Schema

**`stg_nf_header`**
```sql
PK: id_nota (VARCHAR)
Columns: chave, data_emissao, estabelecimento, cnpj, created_at
```

**`stg_nf_item`**
```sql
PK: (id_nota, item_index)  -- composite unique key
Columns: id_nota, item_index, produto, codigo_produto, 
         quantidade, valor_unitario, valor_total, created_at
```

### `analytics` Schema

**`dim_categoria_produto`**
```sql
PK: categoria_id
Columns: nome_categoria (12 categorias)
```

**`dim_produto`**
```sql
PK: produto_id
Columns: nome_canonico, categoria_id (FK)
```

**`dim_produto_descricao`**
```sql
PK: (descricao, produto_id)
Columns: descricao (raw), produto_id (FK to dim_produto)
Purpose: Lookup table para produto_descricao (NFe) → produto canônico
```

---

## 📊 Fluxo de Dados Completo

```
┌─────────────────────────────────────────────────────────────┐
│ INPUT: data/Notas Fiscais/2026/{mes}/*.html               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
       ┌─────────────────────┐
       │ extract_header()    │  → chave, data_emissao, CNPJ
       │ extract_html_data() │  → [produto, qty, valor, ...]
       └─────────────────────┘
                 │
                 ▼
       ┌─────────────────────────────┐
       │ Check: nota_exists()        │  ← idempotência
       │ (stg_nf_header.id_nota)     │
       └─────────────────────────────┘
                 │
                 ├─ YES: SKIP (já carregada)
                 │
                 └─ NO: INSERT
                     │
                     ▼
         ┌──────────────────────────┐
         │ staging.stg_nf_header    │
         │ staging.stg_nf_item      │
         └──────────────────────────┘
                     │
                     ▼
         ┌──────────────────────────────┐
         │ Normalize produto:            │
         │  1. Lookup descrição em       │
         │     dim_produto_descricao    │
         │  2. Se não encontrado:       │
         │     → INSERT novo canônico   │
         │  3. Auto-classificar         │
         │     categoria (keyword)      │
         └──────────────────────────────┘
                     │
                     ▼
         ┌──────────────────────────────┐
         │ analytics.dim_produto        │
         │ + dim_categoria_produto      │
         └──────────────────────────────┘
                     │
                     ▼
         ┌──────────────────────────────┐
         │ AUDITS:                      │
         │  • Item count gaps           │
         │  • Categorization coverage   │
         │  • Canonical name quality    │
         └──────────────────────────────┘
```

---

## 🛠️ Principais Funções

### `nf_data_load_html.py`

**`extract_header(html_path: Path) → tuple`**
- Extrai: `(id_nota, chave, estabelecimento, data_emissao, cnpj)`
- Usa regex sobre conteúdo HTML

**`extract_html_data(html_path: Path) → list[dict]`**
- Retorna: `[{produto, codigo_produto, quantidade, valor_unitario, item_index}, ...]`
- Usa CSS selectors e enumerate para `item_index`

**`normalize_text(value: str) → str`**
- Remove acentos, converte para UPPER, normaliza espaços
- Idempotente para comparações

**`simplify_product_text(value: str) → str`**
- Variante agressiva para produto (remove unidades)

**`get_conn() → psycopg2.connection`**
- Factory pattern com env vars

### `fix_dim_produto_canonical_names.py`

**`clean_name(raw_name: str) → str`**
- 3-pass cleaning:
  1. SPECIAL_CANONICAL_MAP (regex patterns)
  2. Remove REMOVE_TOKENS (unidades, promoções)
  3. Title case + character mapping (PAO→Pão, ACUCAR→Açúcar)

**`update_canonical(produto_id: int, new_name: str) → None`**
- Executa UPDATE com logging

---

## 📈 Estatísticas

| Métrica | Valor |
|---------|-------|
| **Categorias de Produto** | 12 |
| **Produtos Canônicos** | 479+ |
| **Mapeamentos Descrição** | 500+ |
| **Nomes Normalizados** | 127 (via fix_dim_produto_canonical_names) |
| **Padrões Regex** | 30+ (bebidas, carnes, lácteos, etc.) |
| **Tokens Removíveis** | 20+ (PCT, KG, CX, LT, PROMO, etc.) |

---

## 🔧 Troubleshooting

### ❌ `UnicodeDecodeError: 'cp1252'`
**Solução:** `nf_data_load_html.py` já trata encoding misto (UTF-8 + CP1252). Verifique se arquivo HTML está corrompido.

### ❌ `psycopg2.errors.UniqueViolation` em `stg_nf_item`
**Causa:** Falta de `item_index` para deduplicação (versão antiga).  
**Solução:** Execute `fixes/migrate_add_item_index_stg_nf_item.py` primeiro.

### ❌ Produtos não estão sendo categorizado
**Causa:** Novo produto sem padrão em `SPECIAL_CANONICAL_MAP`.  
**Solução:** Execute `fixes/classify_missing_product_categories.py` ou adicione regra manualmente.

### ❌ Auditoria mostra GAP de items
**Causa:** NFe tem 10 items em HTML mas só 8 foram carregados.  
**Solução:** Verifique se há erros no parser (`extract_html_data`) ou verificar integridade HTML.

---

## 📝 Notas de Operação

### Manutenção Regular

```bash
# Weekly: validar qualidade
0 2 * * 1 cd /path && python audits/audit_nf_item_counts.py

# Monthly: adicionar novos produtos descobertos
0 3 1 * * cd /path && psql -U postgres < products/add_missing_products.sql

# As-needed: limpar nomes canônicos
python fixes/fix_dim_produto_canonical_names.py --dry-run  # preview
python fixes/fix_dim_produto_canonical_names.py  # apply
```

### Performance

- **Carregamento**: ~200 notas/min (html parsing) + ~50 inserts/sec (DB)
- **Limpeza nomes**: ~100 updates/sec (regex + normalize_text)
- **Auditoria**: ~2000 comparações/sec (SQL JOIN)

### Idempotência

- Todas as operações de INSERT usam `ON CONFLICT DO NOTHING`
- Duplicatas são ignoradas via constraint único `(id_nota, item_index)`
- Safe para reprocessamento sem limpeza manual

---

## 👥 Contribuindo

Ao adicionar novo loader (ex: XML):

1. Seguir padrão: `extract_header()` + `extract_html_data()` + `main()`
2. Implementar mesmos checks: `nota_exists()`, `validate_data_emissao()`
3. Adicionar audit em `audits/`
4. Documentar em README

---

## 📄 Licença

Parte do projeto roma9-data-platform. Ver LICENSE.

---

## 📞 Contato

Para questões sobre dados de produtos ou dimensões:
- Veja `products/README_manutencao.md` para CRUD manual
- Consulte `audits/` para relatórios de qualidade

---

**Última atualização:** Abril 2026  
**Status:** Ativo - 219 produtos, 479+ canônicos em operação
