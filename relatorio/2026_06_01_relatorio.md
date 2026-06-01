# RELATÓRIO — Hermes do Telegram (CFO digital): relatório matinal, conserto do ETL e skills

**Data:** 2026-06-01
**Autor:** Claude (Claude Code) a pedido de Gelson Simões
**Escopo:** trabalho realizado **no Hermes do Telegram** (agente CFO, container `vpautomation-hermes`) —
NÃO confundir com a "Verti"/Hermes do WhatsApp do Pós-Venda 360 (ver `2026_06_01_relatorio_verti.md`).

---

## 0. TL;DR
Pedido inicial: o Hermes enviar um **relatório matinal às 08:30** para Gelson e Diego com o que foi
**vendido** e **comprado** no dia útil anterior + acumulado do mês. Ao validar os dados, descobrimos que
o **ETL Omie→Supabase estava quebrado havia semanas** (vendas/pedidos congelados). Consertamos a causa
raiz, atualizamos os dados, criamos um agendamento de frescor 5x/dia, **ativamos o relatório matinal**
(determinístico, no banco) e criamos **3 skills fortes** para turbinar o Hermes.

---

## 1. Relatório matinal — NO AR ✅
- **O que envia (08:30, seg–sex, pula feriados):** duas mensagens no Telegram para Gelson (2129471333)
  e Diego (7175937401):
  1. **VENDAS do dia útil anterior, item a item** (produto + valor), via `omie_orders` + `omie_order_items`.
  2. **COMPRAS do dia** por fornecedor/valor (`CP_Omie` + `PN_Omie`) + **acumulado do mês** + **fechamento
     do mês anterior** no 1º dia útil de cada mês.
- **Lógica de "dia útil anterior"** pula fim de semana **e feriados** (tabela `feriados_vp` 2026–2027;
  ex.: Corpus Christi 04/06). Segunda mostra sexta, etc.
- **Arquitetura (determinística, sem depender do sandbox do Hermes):**
  - Função plpgsql `public.enviar_relatorio_matinal(p_dry, p_chats)` monta o texto e envia via `net.http_post`
    para a API do Telegram (mesmo bot do Hermes → chega como "Hermes").
  - Funções de apoio: `eh_dia_util`, `dia_util_anterior`, `primeiro_dia_util`, `fmt_brl` (R$ pt-BR).
  - Agendamento: `cron.job` **`relatorio-matinal-0830`** (`30 11 * * 1-5` UTC = 08:30 BRT).
  - Token do bot guardado no **Vault** (`telegram_bot_token`).
- **Validado:** dry-run conferido + envio real ao Gelson com retorno **HTTP 200 / `ok:true`**.
  1º disparo automático: 02/06 08:30. Exemplo real (29/05): Vendas R$ 101.193,81 (31 produtos) / Compras R$ 11.523,50.

---

## 2. Conserto do ETL Omie→Supabase (causa raiz dos dados parados)
**Sintoma:** vendas/pedidos congelados (pedidos paravam em 08/05; NF de saída em 2024), só compras/CR atualizavam.

**Causa raiz:** a função `omie_get_secret()` lê do **Vault**, e faltavam os segredos `project_url` e
`edge_invoke_key`. Os 7 crons que populam as tabelas (jobids 98–104) montam a URL via esses segredos →
com eles nulos, o `net.http_post` falhava (`null value in column "url"`) e **nenhuma Edge Function de sync
era chamada**. (O job 112 `omie-sync-3h` "funcionava" mas só grava NDJSON num bucket de Storage, não nas tabelas.)

**Correções aplicadas:**
1. Repostos no **Vault**: `project_url` e `edge_invoke_key` (= Function Secret `EDGE_INVOKE_KEY`).
2. **Reabilitado** o módulo `order_items` (estava `is_enabled=false`) — é o detalhe de produto das vendas.
3. **Atualização das vendas:** invocada `sync-omie-orders` na "cauda" → `omie_orders` 25.509 → 25.748,
   última data 08/05 → **29/05**, com produto. NF de venda (`omie_nfe_emitidas`) também atualizada (29/05).
4. **Frescor diário garantido:** novo `cron.job` **`sync-omie-tail-vendas-5x`** (`0 2,10,14,18,22 * * *`,
   5x/dia) que puxa sempre a "cauda" (registros novos) de `sync-omie-orders` e `sync-omie-nfe`.
   As funções puxam páginas ascendentes sem filtro de data, então o cron mira `start_page = total_pages − N`.
   Testado: `net.http_post` retornando **200**.

---

## 3. Skills fortes criadas no Hermes (turbinar o agente)
Inspiradas em dois repositórios de referência (cookbooks de equity research e de séries temporais),
**adaptadas a empresa privada** (a VP não é listada em bolsa). Escritas em `/opt/data/skills/data-science/`:
- **`verticalparts-cfo`** (v2) — núcleo/identidade do CFO digital (estava perdida); aponta as fontes de dados certas.
- **`analise-estrategica`** — relatório institucional, DRE gerencial, **valuation EV/EBITDA e DCF**,
  indicadores avançados (ROI/ROE/ROIC/EVA, liquidez, ciclo, NCG, Efeito Tesoura) e **cenários bull/base/bear
  ponderados por probabilidade**.
- **`projecao-financeira`** — **fluxo de caixa futuro** (parcelas reais de CR/CP), runway, previsão de vendas
  por tendência e **sensibilidade cambial** das importações (China/Europa).
A `MEMORY.md` do Hermes foi atualizada para carregar essas skills em qualquer pergunta financeira.

---

## 4. Realidade dos dados (regras gravadas)
- Horizonte de análise: **01/01/2024 → futuro** (pré-2024 não serve). As Edge Functions já usam esse piso.
- **VENDAS com produto (atual):** `omie_orders` + `omie_order_items` (data_inclusao).
- ⚠️ `omie_nfe_itens` tipo='S' está **congelada em 2024** — não usar para vendas recentes.
- **COMPRAS:** `CP_Omie` (valor + fornecedor + categoria). ⚠️ **Compras com detalhe de PRODUTO não têm
  fonte viva** (a tabela `omie_notas_entrada` não existe; a NF de entrada não é sincronizada). Pendência.
- ⚠️ Há **datas corrompidas** (ano 2424/2043) em CP/CR — sempre filtrar `data <= '2030-01-01'`.

---

## 5. Pendências / próximos passos
- [ ] **Compras com produto (fase 2):** construir tabela + sync de NF de entrada do Omie.
- [ ] **NFe de saída congelada em 2024** (`omie_nfe_itens` tipo='S'): investigar (provável bug da função
      ou mudança de emissão); hoje contornado usando pedidos/`omie_nfe_emitidas`.
- [ ] **Materialized views de dashboard apagadas** (`mv_dashboard_operational`, `mv_pipeline_funil`,
      `mv_abc_produtos`): afeta o dashboard (não o Hermes) — refresh-jobs do pg_cron falhando.
- [ ] Sanear de vez as datas corrompidas em CP/CR (script `limpeza-pre2024.sql`).
- [ ] Evoluir o relatório matinal com indicadores das novas skills (ex.: alerta de caixa, tendência).

---

## 6. Referência rápida (infra criada/alterada — projeto Supabase bd_Omie `kgecbycsyrtdhmdziuul`)
- Vault: `project_url`, `edge_invoke_key`, `telegram_bot_token`.
- Funções: `enviar_relatorio_matinal`, `eh_dia_util`, `dia_util_anterior`, `primeiro_dia_util`, `fmt_brl`. Tabela `feriados_vp`.
- pg_cron: **114 `relatorio-matinal-0830`** (08:30 BRT) e **113 `sync-omie-tail-vendas-5x`** (5x/dia).
- Skills Hermes: `verticalparts-cfo`, `analise-estrategica`, `projecao-financeira` (`/opt/data/skills/data-science/`).

*Gerado por Claude (Claude Code) em 2026-06-01, a pedido de Gelson Simões. Obrigado pela parceria! 🤝*
