# Inteligência do Hermes — VerticalParts Financeiro

> Objetivo: o Hermes (Telegram) responder com a MESMA precisão que o Copiloto
> do dashboard https://vpdashboarddre.vpsistema.com.
> Fonte de dados: Supabase `kgecbycsyrtdhmdziuul` (BD Omie).
> Atualizado em 2026-05-31 com colunas e status REAIS verificados no banco.

---

## 🎯 ESTRATÉGIA RECOMENDADA — reusar o cérebro que já existe

O dashboard `bd_omie` já tem um **motor de IA financeira completo e testado**:
endpoint `POST /api/claude` com **24 ferramentas** (inadimplência, contas a pagar,
caixa projetado, NCG, ciclo financeiro, liquidez, endividamento, ponto de
equilíbrio, curva ABC, risco de clientes, simulação de crescimento, etc.),
rodando em `claude-haiku-4-5` com loop de tool-use.

**Melhor caminho:** o Hermes NÃO deve duplicar isso. Ele deve ter **uma única
ferramenta** que repassa a pergunta para o `/api/claude` do dashboard.

```
Telegram → Hermes → POST https://vpdashboarddre.vpsistema.com/api/claude
                     body: { question, context, history }
         ← resposta em texto (streaming) → Telegram
```

Vantagens:
- Uma só fonte de verdade — Hermes e dashboard respondem IGUAL.
- Zero manutenção duplicada (as 24 tools vivem em um lugar só).
- Já está testado em produção.

Ponto a resolver: o `/api/claude` hoje não tem autenticação. Antes de expor ao
Hermes, adicionar um header secreto (ex: `x-hermes-secret`) no endpoint.

**Plano B (se preferir Hermes autônomo):** dar a ele a service_role key +
o system prompt abaixo + a biblioteca de queries da seção 4. Mais trabalho e
risco de divergência, mas independe do dashboard estar no ar.

---

## 1. SYSTEM PROMPT (espelha o `buildSystemContext` do dashboard)

```
Você é o Copiloto Estratégico da VerticalParts — um CFO/CO digital que ajuda a
diretoria a tomar decisões, respondendo pelo Telegram (Gelson e Diego Maeno).

IDENTIDADE:
- Fale como executivo sênior: direto, analítico, orientado a ação.
- Português brasileiro impecável. Dinheiro sempre em R$ (ex: R$ 1.234.567,89).
- Conciso: 2-4 parágrafos ou bullets. Destaque riscos e oportunidades.

CONTEXTO DE NEGÓCIO:
- VerticalParts é distribuidora B2B de peças para elevadores.
- Importa (China, Europa) e vende nacional, à vista e PARCELADO.
- Compra parcelado em até ~10 meses; vende parcelado. Margem, giro de estoque,
  prazo de recebimento e câmbio são críticos.

DADOS (Supabase kgecbycsyrtdhmdziuul, via service_role):
- CR_Omie = contas a receber | CP_Omie = contas a pagar (passado E futuro)
- omie_orders = pedidos | omie_nfe_itens = NF (tipo E=compra, S=venda)
- PN_Omie = clientes/fornecedores | sellers = vendedores | Produtos_VP = catálogo

REGRAS CRÍTICAS:
1. Horizonte: trabalhe de 01/01/2024 em diante. O FUTURO importa — "quanto pago
   em janeiro/2027" é respondível (filtre data_vencimento no mês pedido).
2. Os nomes de cliente/fornecedor NÃO estão em CR_Omie/CP_Omie — estão em
   PN_Omie. Faça JOIN por codigo_cliente_omie.
3. valor_documento é o valor de CADA parcela. numero_parcela identifica
   parcelamento. Some por período para fluxo de caixa.
4. STATUS REAIS dos títulos (decorar):
   - Em aberto a vencer: 'A VENCER' e 'VENCE HOJE'
   - Vencido não pago (inadimplência): 'ATRASADO'
   - Quitado: 'RECEBIDO' (CR) / 'PAGO' (CP)
   - Anulado: 'CANCELADO'
   → "Em aberto" = status NOT IN ('RECEBIDO','PAGO','CANCELADO').
   → NÃO existe o status "A RECEBER". Não use.
5. Faturamento real = NF saída (omie_nfe_itens tipo='S'). Pedido em aberto não
   é faturamento.
6. Há datas corrompidas no Omie (ex: vencimento ano 2424). Ignore vencimentos
   após 2100 (filtre data_vencimento <= '2100-01-01').
7. Conte sempre com COUNT(*) real — nunca estime por MAX(id).
```

---

## 2. MAPA DE DADOS (colunas REAIS verificadas)

### CR_Omie — Contas a Receber (12.566 linhas)
`codigo_lancamento_omie, codigo_cliente_omie, codigo_categoria, data_emissao,
data_vencimento, data_previsao, data_registro, valor_documento, status_titulo,
numero_parcela, numero_documento_fiscal, numero_pedido, observacao, categorias(jsonb)`
- **Nome do cliente:** JOIN PN_Omie ON codigo_cliente_omie → razao_social/nome_fantasia
- Status: RECEBIDO (11.088) · A VENCER (1.074) · CANCELADO (282) · ATRASADO (120) · VENCE HOJE (2)
- Cobertura: pré-2024 = 76 títulos · futuro = 733 · venc_max = 2027-12

### CP_Omie — Contas a Pagar (26.716 linhas)
`codigo_lancamento_omie, codigo_cliente_omie, codigo_categoria, data_emissao,
data_entrada, data_vencimento, data_previsao, valor_documento, status_titulo,
numero_parcela, numero_documento_fiscal, observacao, categorias(jsonb)`
- **Nome do fornecedor:** JOIN PN_Omie ON codigo_cliente_omie
- Cobertura: pré-2024 = 624 títulos · futuro = 2.868 · jan/2027 = 63 · ⚠️ tem data corrompida (2424)

### omie_orders — Pedidos (25.509)
`codigo_pedido_omie, numero_pedido, codigo_cliente_omie, codigo_vendedor_omie,
etapa, status, data_inclusao, data_previsao, valor_total_pedido, valor_mercadorias,
numero_nf, chave_nfe, codigo_categoria`

### omie_nfe_itens — Itens de NF (45.609)
`numero_nfe, tipo(E/S), data_emissao, codigo_produto, descricao, quantidade,
valor_unitario, valor_total, cnpj_parceiro, nome_parceiro, chave_nfe`

### PN_Omie — Pessoas (13.827)
`codigo_cliente_omie, razao_social, nome_fantasia, cnpj_cpf, tags, cidade, estado,
total_a_receber, credito_disponivel, vendedor_padrao, num_parcelas_padrao`

### Apoio
`sellers` (omie_codigo→name) · `dre_category_map` (codigo→dre_descricao) ·
`omie_categorias` · `Produtos_VP` (4.140)

---

## 3. BIBLIOTECA DE QUERIES (SQL correto, com JOINs e status reais)

### "Quanto tenho que pagar em janeiro de 2027?"
```sql
SELECT COUNT(*) AS titulos, SUM(valor_documento) AS total
FROM "CP_Omie"
WHERE data_vencimento BETWEEN '2027-01-01' AND '2027-01-31'
  AND status_titulo NOT IN ('PAGO','CANCELADO');
```

### "Quanto a receber nos próximos 90 dias?"
```sql
SELECT COUNT(*) AS titulos, SUM(valor_documento) AS total
FROM "CR_Omie"
WHERE data_vencimento BETWEEN CURRENT_DATE AND CURRENT_DATE + 90
  AND data_vencimento <= '2100-01-01'
  AND status_titulo NOT IN ('RECEBIDO','CANCELADO');
```

### "Qual minha inadimplência hoje?" (atrasados)
```sql
SELECT cr.codigo_cliente_omie,
       COALESCE(pn.nome_fantasia, pn.razao_social) AS cliente,
       SUM(cr.valor_documento) AS em_atraso
FROM "CR_Omie" cr
LEFT JOIN "PN_Omie" pn ON pn.codigo_cliente_omie = cr.codigo_cliente_omie
WHERE cr.status_titulo = 'ATRASADO'
GROUP BY 1,2 ORDER BY em_atraso DESC;
```

### "Fluxo de caixa projetado por mês (12 meses)"
```sql
WITH meses AS (
  SELECT to_char(d,'YYYY-MM') AS mes
  FROM generate_series(date_trunc('month',CURRENT_DATE),
                       date_trunc('month',CURRENT_DATE)+INTERVAL '11 months',
                       INTERVAL '1 month') d)
SELECT m.mes,
  COALESCE((SELECT SUM(valor_documento) FROM "CR_Omie"
    WHERE to_char(data_vencimento,'YYYY-MM')=m.mes
      AND status_titulo NOT IN ('RECEBIDO','CANCELADO')),0) AS a_receber,
  COALESCE((SELECT SUM(valor_documento) FROM "CP_Omie"
    WHERE to_char(data_vencimento,'YYYY-MM')=m.mes
      AND status_titulo NOT IN ('PAGO','CANCELADO')),0) AS a_pagar
FROM meses m ORDER BY m.mes;
```

### "Compras parceladas a pagar no futuro"
```sql
SELECT COALESCE(pn.nome_fantasia,pn.razao_social) AS fornecedor,
       cp.numero_documento_fiscal, cp.numero_parcela,
       cp.data_vencimento, cp.valor_documento
FROM "CP_Omie" cp
LEFT JOIN "PN_Omie" pn ON pn.codigo_cliente_omie = cp.codigo_cliente_omie
WHERE cp.numero_parcela IS NOT NULL AND cp.numero_parcela <> ''
  AND cp.data_vencimento BETWEEN CURRENT_DATE AND '2100-01-01'
  AND cp.status_titulo NOT IN ('PAGO','CANCELADO')
ORDER BY cp.data_vencimento;
```

### "Vendas parceladas a receber (carteira futura)"
```sql
SELECT COALESCE(pn.nome_fantasia,pn.razao_social) AS cliente,
       cr.numero_parcela, cr.data_vencimento, cr.valor_documento
FROM "CR_Omie" cr
LEFT JOIN "PN_Omie" pn ON pn.codigo_cliente_omie = cr.codigo_cliente_omie
WHERE cr.numero_parcela IS NOT NULL AND cr.numero_parcela <> ''
  AND cr.data_vencimento >= CURRENT_DATE
  AND cr.status_titulo NOT IN ('RECEBIDO','CANCELADO')
ORDER BY cr.data_vencimento;
```

### "Faturamento do mês" (NF saída)
```sql
SELECT to_char(data_emissao,'YYYY-MM') AS mes, SUM(valor_total) AS faturamento
FROM omie_nfe_itens
WHERE tipo='S' AND data_emissao >= date_trunc('month',CURRENT_DATE)
GROUP BY 1;
```

### "Top 10 clientes a receber em aberto"
```sql
SELECT COALESCE(pn.nome_fantasia,pn.razao_social) AS cliente,
       SUM(cr.valor_documento) AS em_aberto
FROM "CR_Omie" cr
LEFT JOIN "PN_Omie" pn ON pn.codigo_cliente_omie = cr.codigo_cliente_omie
WHERE cr.status_titulo NOT IN ('RECEBIDO','CANCELADO')
GROUP BY 1 ORDER BY em_aberto DESC LIMIT 10;
```

---

## 4. CONEXÃO (para o .env do Hermes — Plano B)

```
SUPABASE_URL=https://kgecbycsyrtdhmdziuul.supabase.co
SUPABASE_SERVICE_KEY=<service_role do projeto BD OMIE>   # ver credenciais_master seção 4 [6]
```
> NÃO colar a chave neste arquivo (vai pro git). Configurar direto no servidor.

---

## 5. CHECKLIST DE VALIDAÇÃO (perguntar no Telegram, conferir no banco)

- [ ] "Quantos pedidos temos?" → **25.509** (não ~31.808)
- [ ] "Quanto a pagar em jan/2027?" → ~63 títulos
- [ ] "Qual a inadimplência atual?" → 120 títulos ATRASADO em CR
- [ ] "Fluxo de caixa dos próximos 6 meses?" → bater com o dashboard
- [ ] "Top 5 clientes devedores?" → nomes reais (não "Cliente 12345")

---

## 6. PRÓXIMOS PASSOS PARA APLICAR

1. [ ] Limpar pré-2024 (script `limpeza-pre2024.sql`) + corrigir datas corrompidas
2. [ ] Decidir: Hermes chama /api/claude (recomendado) OU Hermes autônomo
3. [ ] Se /api/claude: adicionar header secreto ao endpoint e liberar CORS p/ Hermes
4. [ ] Inspecionar container `vpautomation-hermes` para ver onde injetar prompt/tool
5. [ ] Aplicar e rodar o checklist de validação
