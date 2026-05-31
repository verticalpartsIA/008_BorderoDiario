---
name: supabase-omie-verticalparts
description: "Consulta dados do ERP Omie (contas a receber/pagar, produtos, pedidos, NFe) no Supabase da VerticalParts. Schema real, autenticação service_role, contagem correta e contexto financeiro brasileiro."
version: 2.0.0
author: VerticalParts
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [supabase, omie, erp, financeiro, verticalparts]
  category: data-science
---

# Supabase + Omie ERP (VerticalParts) — v2

A VerticalParts usa o ERP Omie com dados espelhados no Supabase. Esta skill ensina a consultar
contas a receber (CR_Omie), a pagar (CP_Omie), produtos, pedidos e NF-e — com dados REAIS.

> ⚠️ Esta skill foi reescrita em 31/05/2026. A versão antiga estava ERRADA (usava chave anon,
> schema inventado e dizia que os dados estavam "quebrados/n8n"). NADA disso é verdade.
> Os dados ESTÃO no banco e são acessíveis. Ignore qualquer menção a "ETL quebrado", "n8n",
> "sync falhou" ou "contactar Diego por dados vazios" — isso era diagnóstico errado.

---

## 1. Autenticação — SEMPRE service_role (nunca anon)

As credenciais já estão no ambiente do Hermes (env). USE-AS:

```bash
# $SUPABASE_URL e $SUPABASE_SERVICE_KEY já existem no ambiente.
# NUNCA use a chave anon — o RLS bloqueia e retorna 0 linhas (falso "vazio").
echo "$SUPABASE_URL"            # https://kgecbycsyrtdhmdziuul.supabase.co
test -n "$SUPABASE_SERVICE_KEY" && echo "service key OK"
```

Toda requisição leva os dois headers:
```
-H "apikey: $SUPABASE_SERVICE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_KEY"
```

---

## 2. CONTAR registros corretamente (crítico)

O PostgREST NÃO retorna COUNT no corpo. Para contar, faça **HEAD** com `Prefer: count=exact`
e leia o número após a barra no header **Content-Range**. NUNCA conte por faixa de ID (MAX id) —
isso superestima por causa de registros excluídos.

```bash
contar() {  # uso: contar NOME_DA_TABELA
  curl -s -I -X HEAD \
    -H "apikey: $SUPABASE_SERVICE_KEY" \
    -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
    -H "Prefer: count=exact" -H "Range: 0-0" \
    "$SUPABASE_URL/rest/v1/$1?select=*" | grep -i content-range
  # resposta: content-range: 0-0/25509  → o total é 25509
}
contar omie_orders   # deve dar /25509
```

---

## 3. Contagens reais (verificadas 31/05/2026)

| Tabela | Linhas | O que é |
|--------|--------|---------|
| CR_Omie | 12.490 | Contas a receber |
| CP_Omie | 26.091 | Contas a pagar |
| omie_orders | 25.509 | Pedidos de venda |
| omie_order_items | 61.385 | Itens dos pedidos |
| omie_nfe_itens | 45.609 | Itens de NF (E=compra, S=venda) |
| PN_Omie | 13.827 | Clientes + fornecedores |
| Produtos_VP | 4.140 | Catálogo/estoque |
| sellers | 99 | Vendedores |

Horizonte: dados de **01/01/2024 em diante** (pré-2024 removido). Há vencimentos FUTUROS
(compras e vendas parceladas) — "quanto pago em jan/2027" é respondível.

---

## 4. Schema REAL (colunas que existem de verdade)

### CR_Omie / CP_Omie
`codigo_lancamento_omie, codigo_cliente_omie, codigo_categoria, data_emissao,
data_vencimento, data_previsao, valor_documento, status_titulo, numero_parcela,
numero_documento_fiscal, observacao` (CR ainda tem numero_pedido, codigo_pedido_omie)

- **valor_documento** = valor da PARCELA (não use "valor")
- **status_titulo** (não "status"):
  - CR: `RECEBIDO`, `A VENCER`, `ATRASADO`, `VENCE HOJE`, `CANCELADO`
  - CP: `PAGO`, `A VENCER`, `ATRASADO`, `CANCELADO`
  - **NÃO existe "A RECEBER"/"aberto"/"pendente"**. Em aberto = NOT IN (RECEBIDO/PAGO, CANCELADO). Inadimplência = `ATRASADO`.
- **Nome do cliente/fornecedor NÃO está aqui.** JOIN com PN_Omie por `codigo_cliente_omie` → `nome_fantasia`/`razao_social`.

### omie_orders
`codigo_pedido_omie, numero_pedido, codigo_cliente_omie, codigo_vendedor_omie, etapa,
data_inclusao, data_previsao, valor_total_pedido, numero_nf` (etapa 00=aberto … 70=entregue)

### omie_nfe_itens
`numero_nfe, tipo (E/S), data_emissao, codigo_produto, descricao, quantidade,
valor_unitario, valor_total, nome_parceiro` — Faturamento real = tipo='S'.

### PN_Omie
`codigo_cliente_omie, razao_social, nome_fantasia, cnpj_cpf, cidade, estado`

---

## 5. Receitas de consulta

### Quanto a pagar em um mês (ex: jan/2027)
```bash
curl -s -H "apikey: $SUPABASE_SERVICE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
 "$SUPABASE_URL/rest/v1/CP_Omie?select=valor_documento,data_vencimento,status_titulo&data_vencimento=gte.2027-01-01&data_vencimento=lte.2027-01-31&status_titulo=neq.CANCELADO" \
 | jq '[.[] | select(.status_titulo!="PAGO") | .valor_documento|tonumber] | add'
```

### Inadimplência (a receber atrasado) com nome do cliente
```bash
# 1) pega os atrasados
curl -s -H "apikey: $SUPABASE_SERVICE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
 "$SUPABASE_URL/rest/v1/CR_Omie?select=codigo_cliente_omie,valor_documento&status_titulo=eq.ATRASADO" > cr.json
# 2) pega nomes em PN_Omie e cruze por codigo_cliente_omie (nome_fantasia/razao_social)
```

### Faturamento do mês (NF saída)
```bash
curl -s -H "apikey: $SUPABASE_SERVICE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
 "$SUPABASE_URL/rest/v1/omie_nfe_itens?select=valor_total,data_emissao&tipo=eq.S&data_emissao=gte.2026-05-01" \
 | jq '[.[].valor_total|tonumber] | add'
```

### Paginação (acima de 1000 linhas)
Use o header `Range` (ex: `Range: 0-999`, depois `1000-1999`...) com `Range-Unit: items`.

---

## 6. Regras de ouro
- Só atendo Gelson e Diego. Nunca peço chaves a ninguém.
- Não excluo dados, não aprovo pagamentos sem confirmação humana.
- Se uma consulta vier vazia: confira se usou a **service_role** (não anon) e o **status_titulo** certo,
  ANTES de dizer que "não há dados". Os dados existem.

## Contatos
- Gelson Simões (Telegram 2129471333) — Consultor Estratégico
- Diego Maeno (+55 11 99462-1946 / Telegram 7175937401) — CEO
