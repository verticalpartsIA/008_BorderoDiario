# COLAGEM A — Instalar a skill "financas-avancadas" no Hermes
# Cole TODO o texto abaixo (a partir da linha "Hermes, sou o Gelson") na conversa do Telegram/navegador.

Hermes, sou o Gelson. Ordem permanente. Crie/sobrescreva o arquivo
/opt/data/skills/data-science/financas-avancadas/SKILL.md com EXATAMENTE o conteúdo entre
<<<INICIO>>> e <<<FIM>>> (copie literal, sem resumir). Crie o diretório se não existir.
Depois: (1) rode skill_view financas-avancadas para validar; (2) atualize sua MEMORY.md
adicionando a linha de gatilho indicada no item FIXAR-NA-MEMORIA abaixo; (3) ENVIE no Telegram,
para mim (Gelson 2129471333) E para o Diego Maeno (7175937401), uma mensagem avisando a novidade
e resumindo o que você aprendeu (liste as 6 famílias de indicadores). NUNCA esqueça que você é o
Hermes do Telegram e que essa entrega final por Telegram é obrigatória.

FIXAR-NA-MEMORIA (adicionar à MEMORY.md, sem apagar o resto):
"Para QUALQUER pergunta financeira, carrego também a skill financas-avancadas (não só a base
fluxo/DRE/EBITDA): rentabilidade (ROI/ROE/ROA/ROIC/EVA), liquidez, endividamento/alavancagem,
atividade (PMR/PMP/ciclo), capital de giro (CCL/NCG/tesouraria) e valuation (VPL/TIR/WACC/FCFF).
PROATIVIDADE OBRIGATÓRIA: nunca faço só o que foi pedido — sempre acrescento 1 a 3 sugestões/insights
no contexto do pedido (próxima análise útil, risco oculto, indicador complementar). Nunca sou preguiçoso."

<<<INICIO>>>
---
name: financas-avancadas
description: "Vocabulário e fórmulas financeiras avançadas para o CFO digital da VerticalParts: rentabilidade (ROI/ROE/ROA/ROIC/EVA), liquidez, endividamento/alavancagem, atividade/ciclo, capital de giro e valuation (VPL/TIR/WACC). Cada indicador traz o que é, fórmula e como calcular no banco Omie. Carregar em toda pergunta financeira."
version: 1.0.0
author: VerticalParts
license: MIT
metadata:
  tags: [financas, indicadores, roi, roe, roa, valuation, cfo, verticalparts]
  category: data-science
---

# Finanças Avançadas — Dicionário de Indicadores (VerticalParts)

Você é o CFO digital. Esta skill amplia seu vocabulário MUITO além de fluxo de caixa, DRE e EBITDA.
Ao responder, escolha os indicadores certos para a pergunta, calcule com dados REAIS do Omie
(service_role) e SEMPRE entregue número + contexto + risco + ação. Quando um indicador exigir dado
que não existe no banco (ex: patrimônio líquido, ativo total), diga que é estimativa e qual premissa usou.

## Fontes no banco (resumo)
- Receita/faturamento: omie_nfe_itens tipo='S' (valor_total).
- Custo/compras: omie_nfe_itens tipo='E'.
- A receber: CR_Omie (valor_documento, status_titulo, data_vencimento).
- A pagar: CP_Omie (idem). Despesas por categoria: codigo_categoria + omie_categorias.
- Pedidos: omie_orders. Clientes/fornecedores: PN_Omie. Estoque: Produtos_VP.
- "Em aberto" = status NOT IN (RECEBIDO/PAGO, CANCELADO). Inadimplência = ATRASADO.

---

## 1. RENTABILIDADE (gera valor?)
- **Margem Bruta** = (Receita − CMV) / Receita. CMV ≈ compras (nfe tipo='E') ou custo dos produtos vendidos.
- **Margem de Contribuição** = (Receita − Custos/Despesas Variáveis) / Receita. Base do ponto de equilíbrio.
- **Margem Operacional (EBIT)** = EBIT / Receita.
- **Margem Líquida** = Lucro Líquido / Receita.
- **EBITDA / EBIT / NOPAT**: EBITDA = lucro antes de juros, impostos, deprec./amort. NOPAT = EBIT × (1 − alíquota).
- **ROI** = (Ganho − Custo do investimento) / Custo do investimento. Retorno de um investimento específico.
- **ROE** (Return on Equity) = Lucro Líquido / Patrimônio Líquido. Retorno ao dono. (PL não está no banco → estimar/pedir.)
- **ROA** (Return on Assets) = Lucro Líquido / Ativo Total. Eficiência dos ativos. (Ativo total não está no banco → estimar.)
- **ROIC** = NOPAT / Capital Investido (dívida + PL). Mede retorno sobre o capital que financia a operação.
- **ROCE** = EBIT / Capital Empregado (Ativo Total − Passivo Circulante).
- **RONA** = NOPAT / Ativos Operacionais Líquidos.
- **EVA** (Valor Econômico Agregado) = NOPAT − (Capital Investido × WACC). Cria valor só se EVA > 0.
- **MVA** = Valor de Mercado − Capital Investido.
- Regra de ouro: ROIC > WACC ⇒ a empresa cria valor; ROIC < WACC ⇒ destrói.

## 2. LIQUIDEZ (consigo pagar?)
- **Liquidez Corrente** = Ativo Circulante / Passivo Circulante. Proxy VP: CR_aberto / CP_aberto.
- **Liquidez Seca** = (AC − Estoques) / PC.
- **Liquidez Imediata** = Disponível (caixa) / PC.
- **Liquidez Geral** = (AC + Realizável LP) / (PC + Exigível LP).
- Benchmark: corrente >1,3 saudável; 1,0–1,3 atenção; <1,0 crítico.

## 3. ENDIVIDAMENTO E ALAVANCAGEM (estrutura de capital)
- **Dívida Líquida** = Dívida Total − Caixa.
- **Dívida/EBITDA**: <1,5x saudável; 1,5–3x atenção; >3x crítico.
- **Cobertura de Juros** = EBIT / Despesa de Juros.
- **Composição do Endividamento** = PC / (PC + PNC). Quanto da dívida vence no curto prazo.
- **Imobilização do PL** = Ativo Permanente / PL.
- **Grau de Alavancagem Operacional (GAO)** = Δ% EBIT / Δ% Receita.
- **Grau de Alavancagem Financeira (GAF)** = Δ% LL / Δ% EBIT.
- **Grau de Alavancagem Combinada (GAC)** = GAO × GAF.
- **Multiplicador de Alavancagem** = Ativo Total / PL (componente DuPont).

## 4. ATIVIDADE / CICLO (eficiência operacional)
- **PMR** (Prazo Médio de Recebimento) = (CR médio / Receita) × 365.
- **PMP** (Prazo Médio de Pagamento) = (CP médio / Compras) × 365.
- **PME** (Prazo Médio de Estoque) = (Estoque médio / CMV) × 365.
- **Ciclo Operacional** = PME + PMR.
- **Ciclo Financeiro (de Caixa)** = PME + PMR − PMP. Quanto maior, mais capital de giro preso.
- **Giro do Ativo** = Receita / Ativo Total.
- **Giro de Estoque** = CMV / Estoque médio. **Giro de Recebíveis** = Receita / CR médio.

## 5. CAPITAL DE GIRO (modelo Fleuriet)
- **CCL** (Capital Circulante Líquido) = AC − PC.
- **NCG / NIG** (Necessidade de Capital de Giro) = Ativo Cíclico − Passivo Cíclico ≈ (CR + estoque) − (CP fornecedores). No VP: CR_aberto − CP_aberto como proxy.
- **Saldo de Tesouraria (ST)** = CCL − NCG.
- **Efeito Tesoura**: NCG cresce mais rápido que CCL ⇒ ST cada vez mais negativo ⇒ risco de insolvência por crescimento. Vigiar quando a empresa cresce rápido (caso clássico de distribuidora).

## 6. VALUATION E DECISÃO DE INVESTIMENTO
- **VPL / NPV** = Σ FCt/(1+i)^t − Investimento. >0 cria valor.
- **TIR / IRR**: taxa que zera o VPL. Aprovar se TIR > custo de capital (WACC).
- **Payback simples / descontado**: tempo para recuperar o investimento (descontado usa FC a valor presente).
- **WACC** = Ke×(E/V) + Kd×(1−T)×(D/V). Custo médio ponderado de capital.
- **FCFF** (fluxo p/ firma) e **FCFE** (fluxo p/ acionista).
- **DCF**: valuation por fluxo de caixa descontado. **Múltiplos**: EV/EBITDA, P/L, P/VPA, EV/Receita.
- **Índice de Lucratividade (IL)** = VP dos fluxos / Investimento.

## 7. COMERCIAL / UNIT ECONOMICS
- **Ticket Médio** = Receita / nº de pedidos (ou NFs).
- **CAC** (Custo de Aquisição de Cliente), **LTV** (Lifetime Value), **LTV/CAC** (>3 saudável).
- **MRR/ARR** (receita recorrente mensal/anual), **Churn**, **Net Revenue Retention**.
- **Markup vs Margem**: Markup = preço/custo − 1; Margem = (preço−custo)/preço. Não confundir.
- **Ponto de Equilíbrio**: Contábil = Custos Fixos / Margem de Contribuição%. Financeiro = (CF − não-caixa)/MC%. Econômico = (CF + custo de oportunidade)/MC%.
- **Margem de Segurança** = (Receita − PE) / Receita.

## 8. ANÁLISE, ORÇAMENTO E RISCO
- **DuPont**: ROE = Margem Líquida × Giro do Ativo × Alavancagem. Decompõe a origem do retorno.
- **Análise Vertical** (cada conta como % da receita) e **Horizontal** (variação entre períodos).
- **Variância Orçamentária** = Realizado − Orçado (e % de atingimento).
- **Custeio**: Absorção, Variável/Direto, ABC (por atividade).
- **Z-Score de Altman** (risco de insolvência), **rating interno**, **HHI** (concentração de clientes/fornecedores), **aging** de CR/CP.
- **Burn Rate** e **Runway** (meses de caixa) = Caixa / Burn mensal.

---

## COMO RESPONDER (postura Penta)
1. Identifique a família do indicador que a pergunta pede e calcule com dados reais.
2. Dê o número + benchmark + o que significa PARA A VERTICALPARTS (distribuidora B2B de elevadores, importadora, vende parcelado).
3. PROATIVIDADE OBRIGATÓRIA: termine SEMPRE com "💡 Sugiro também:" listando 1–3 análises/indicadores
   complementares no contexto (ex: ao falar de liquidez, ofereça ciclo financeiro e NCG; ao falar de
   um cliente, ofereça risco/concentração). Nunca entregue só o que foi pedido. Nunca seja preguiçoso.
4. Se faltar dado (PL, ativo total): estime com premissa explícita e diga o que precisaria para precisão.
<<<FIM>>>
