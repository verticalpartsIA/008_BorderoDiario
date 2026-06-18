# Relatório de Atividades — 18/06/2026

**Autor:** Claude Code (assistente de engenharia) · **Solicitante:** Gelson Simões
**Temas:** Borderô — filtro CFOP de vendas reais · novo horário 10:00 BRT · envio manual 17/06

---

## 1. Resumo executivo do dia

| # | Entrega | Status |
|---|---|---|
| 1 | **Filtro CFOP** no Borderô: exclui NFs sem receita de caixa (remessas, comodatos, devoluções de compra etc.) | ✅ em produção |
| 2 | **Novo horário do cron**: 06:00 BRT → **10:00 BRT** (seg-sex) | ✅ em produção |
| 3 | Borderô manual do **17/06** gerado e enviado ao Gelson (primeiro com filtro CFOP ativo) | ✅ msg 1001 |
| 4 | Descrições dos CFOPs 5.107/6.107/5.108/6.108 corrigidas; 6.109 e 6.110 (Zona Franca) documentados | ✅ |
| 5 | Preview do envio de amanhã (19/06) enviado ao Gelson em PDF | ✅ msgs 999 e 1000 |

---

## 2. Filtro CFOP — somente vendas reais

### Problema
O total de "Emitido" do Borderô incluía NFs que **não representam entrada de caixa**: remessas para
conserto, transferências entre filiais, comodatos, devoluções de compra emitidas pela VP etc.
Exemplo concreto: a NF de **Retorno de Remessa para Conserto** da MULTITEC ELEVADORES
(R$ 14.391,80 — CFOP 5.915) estava somando no faturamento do dia 17/06.

### Investigação na API Omie
Consultou-se `https://app.omie.com.br/api/v1/produtos/cfop/` (ListarCFOP, 676 registros).
O CFOP está em `det[0].prod.CFOP` — nível de item, não de cabeçalho.
Série 5.xxx = saídas intraestado; série 6.xxx = saídas interestaduais. Ambas representam receita
quando são de venda real.

### Solução
Adicionado o conjunto `CFOP_EXCLUIR` em `gerar_bordero.py`. Toda NF cujo primeiro item tenha
CFOP nessa lista é descartada antes de entrar nos totais.

```python
CFOP_EXCLUIR = {
    '5.151', '5.152', '6.151', '6.152',   # transferências entre filiais
    '5.901', '5.902', '6.901', '6.902',   # remessa/retorno industrialização
    '5.915', '5.916', '6.915', '6.916',   # remessa/retorno conserto
    '5.912', '5.913', '6.912', '6.913',   # remessa/retorno demonstração
    '5.908', '5.909', '6.908', '6.909',   # remessa/retorno comodato
    '5.117', '6.117',                      # venda p/ entrega futura (receita só na NF real)
    '5.949', '6.949',                      # amostras grátis e remessas sem receita
    '5.201', '5.202', '6.201', '6.202',   # devoluções de compra emitidas pela VP
}
```

### CFOPs que passam (vendas reais)

| CFOP | Descrição |
|---|---|
| 5.101 / 6.101 | Venda de produto industrializado |
| 5.102 / 6.102 | Venda de mercadoria adquirida ou recebida de terceiros |
| 5.107 / 6.107 | Venda de produção do estabelecimento, destinada a não contribuinte |
| 5.108 / 6.108 | Venda de mercadoria adquirida ou recebida de terceiros, destinada a não contribuinte |
| 6.109 | Venda de produção p/ Zona Franca de Manaus / Áreas de Livre Comércio |
| 6.110 | Venda de mercadoria adquirida p/ Zona Franca de Manaus / Áreas de Livre Comércio |

### Resultado do teste (últimos 30 dias)

| Métrica | Valor |
|---|---|
| Total NFs saída (tpNF=1) | 100 |
| Excluídas pelo filtro | 6 (amostras 5.949 ×3, entrega futura 5.117 ×1, retorno conserto 6.916 ×1, devolução compra ×1) |
| Incluídas | 94 |

**CFOPs encontrados nas NFs incluídas:**

| CFOP | Qtd | Descrição |
|---|---|---|
| 5.101 | 39 | Venda de Produção do Estabelecimento |
| 6.101 | 33 | Venda de Produção do Estabelecimento (interestadual) |
| 6.107 | 15 | Venda de Produção p/ Não Contribuinte (interestadual) |
| 5.102 | 2 | Venda de Mercadoria Adq./Recebida de Terceiros |
| 6.108 | 1 | Venda de Mercadoria p/ Não Contribuinte (interestadual) |
| 6.102 | 1 | Venda de Mercadoria (interestadual) |
| 5.917 | 1 | Remessa por conta e ordem de terceiros — ⚠️ monitorar |

**Impacto no dia 17/06:**
- Antes do filtro: R$ 261.808,06 (7 NFs)
- Após o filtro: **R$ 247.416,26** (6 NFs) — MULTITEC excluída

---

## 3. Novo horário do Borderô — 10:00 BRT

### Motivação
O horário de **06:00 BRT** antecipava o relatório, mas o movimento financeiro do dia anterior
só fica completamente conciliado no início do expediente. O Gelson definiu que **10:00 BRT**
é o horário ideal: chega no começo da manhã de trabalho e ainda dá tempo para o Financeiro
conciliar notas emitidas fora do horário de expediente.

### Alteração no crontab
```
# Antes
CRON_TZ=UTC
0 9 * * 1-5 /root/bordero/run_cron.sh   # 06:00 BRT

# Depois
CRON_TZ=UTC
0 13 * * 1-5 /root/bordero/run_cron.sh  # 10:00 BRT
```

Vigente a partir de **19/06/2026 (sexta-feira)** — primeiro disparo com o novo horário.

---

## 4. Borderô manual do dia 17/06

O Gelson enviou o JSON com os dados do Omie do dia 17/06 (quarta-feira). O PDF foi gerado
diretamente do JSON, aplicando o filtro CFOP, e enviado via bot do Telegram (msg **1001**).

**Números finais do dia 17/06:**

| Indicador | Valor |
|---|---|
| 📤 Emitido (6 NFs) | R$ 247.416,26 |
| 💚 Recebido (29 títulos, 17 conciliados) | R$ 219.019,18 |
| 💸 Pago (12 títulos, 9 conciliados) | R$ 80.086,20 |
| 💼 Saldo do dia | R$ 138.932,98 |

> ⚠️ **Ponto de atenção:** GAME STATION aparece 4× nos recebimentos com o mesmo Doc/NF 507
> e valor R$ 9.000,00 cada (R$ 36.000,00 total). Pode ser 4 parcelas reais ou duplicação
> de registro no Omie — vale verificar.

---

## 5. Estado final dos automatismos da VP (18/06/2026, fim do dia)

| Automatismo | Mecanismo | Horário | Status |
|---|---|---|---|
| Borderô PDF seg-sex (Gelson+Diego) | cron VPS `/root/bordero/` | **10:00 BRT** | 🟢 filtro CFOP ativo |
| Bot Telegram (perguntas livres, texto e voz) | `telegram-claude.service` + Opus 4.8 | on-demand | 🟢 no ar |
| pv360 auto-reply WhatsApp | Evolution API | on-demand | 🟢 inalterado |
| Relatório matinal 08:30 | pg_cron Supabase job 114 | — | 🔴 desativado (reversível) |
| Hermes (container) | docker `vpautomation-hermes` | — | ⏸️ desligado (substituído) |
| ETL Omie→Supabase (bd_Omie) | pg_cron jobs 98-104 | — | 🔴 parado (Vault sem credenciais) |

## 6. Pendências que ficam

1. **CFOP 5.917** (1 NF) — monitorar se é operação legítima de receita ou remessa.
2. **GAME STATION** — verificar se os 4 lançamentos do Doc 507 são parcelas reais ou duplicação.
3. **Conciliação bancária / posição de caixa** no Borderô — aguarda implantação no Omie.
4. **ETL Omie→Supabase**: corrigir credenciais do Vault (jobs 98-104).
5. **Incidente 04/06**: revogação do token do bot no @BotFather segue pendente.

---

*Relatório gerado pelo Claude Code (Sonnet 4.6) na sessão de 18/06/2026, a pedido do Gelson.*
*Sem segredos neste documento — credenciais ficam exclusivamente em `.env`/Vault.*
