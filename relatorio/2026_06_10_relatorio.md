# Relatório de Atividades — 10/06/2026

**Autor:** Claude Code (assistente de engenharia) · **Solicitante:** Gelson Simões
**Temas:** Borderô v4 (conciliação de compras + correções críticas de dados) · desligamento do
relatório matinal do Hermes · **nova ponte Telegram ↔ Claude (Fable 5)** com conversa por **voz**

---

## 1. Resumo executivo do dia

| # | Entrega | Status |
|---|---|---|
| 1 | Borderô: migração das emitidas p/ Omie ao vivo (fim do "buraco do espelho") | ✅ aprovado pelo Gelson |
| 2 | Relatório matinal 08:30 do Hermes **desativado** a pedido | ✅ reversível |
| 3 | Borderô v4: **conciliação de NF de fornecedor** (compras × Contas a Pagar) | ✅ teste msg 877 |
| 4 | **Fix crítico tpNF**: faturamento estava inflado com notas de compra | ✅ números reais validados |
| 5 | Borderô v4.1: **nome fantasia** em todas as seções (fim dos códigos) | ✅ aprovado ("ficou excelente") |
| 6 | **Ponte Telegram ↔ Claude Fable 5** substitui o Hermes no bot | ✅ NO AR |
| 7 | **Conversa por VOZ** no Telegram (ouvir e falar), 100% local | ✅ NO AR, demo msg 896 |

---

## 2. Borderô Financeiro — manhã: fim do "buraco do espelho"

O cron das 06:00 vinha entregando pontualmente (08/06 → msgs 864/865; 09/06 → msgs 870/871),
mas os **valores acumulados** estavam errados. Causa raiz: a tabela espelho `omie_nfe_emitidas`
do Supabase estava **grosseiramente incompleta** no 1º trimestre/2026 (ex.: janeiro com R$ 8,2 mil
registrados contra R$ 8,21 milhões reais) porque o ETL Omie→Supabase está parado (Vault sem
credenciais). Resultado: "Emitido no ano" aparecia como R$ 11,5M — parecia que a empresa recebia
mais do que emitia.

**Correção:** as notas emitidas passaram a ser lidas **direto da API do Omie** (`ListarNF`),
eliminando a dependência do espelho morto. O script puxa o ano uma vez e fatia por janela
(dia/semana/mês/ano). PDF de teste enviado e **aprovado pelo Gelson** (msg 876).

## 3. Relatório matinal do Hermes — desativado a pedido

O Gelson recebeu a mensagem das 08:30 e pediu a **interrupção definitiva** desse processo.
O disparo não era do container do Hermes, e sim de um **pg_cron no Supabase**
(job `relatorio-matinal-0830`, jobid 114). Ação: `cron.alter_job(114, active := false)` —
**desligado sem apagar** (função, estado e agendamento preservados; reativável com um comando).
A partir de agora o **Borderô das 06:00 é o único relatório diário automático**.

## 4. Borderô v4 — conciliação de NF de FORNECEDOR (pedido do dia)

Nova seção no PDF: **"📥 Compras — NF de Fornecedor registradas ONTEM · conciliação c/ Contas a Pagar"**.

### Descobertas técnicas que viabilizaram (sem depender do ETL morto)
- `ListarNF` com `tpNF:"0"` lista as **notas de entrada** (fornecedor contra a VP); nesse caso
  `nfDestInt.cRazao` carrega o **fornecedor**.
- Filtro por **data de REGISTRO** (`dRegInicial/dRegFinal`), não de emissão: nota de fornecedor
  emitida semana passada que chegou ontem aparece no borderô de ontem — sem buracos.
- **Cada NF de entrada já traz os títulos do Contas a Pagar embutidos** (campo `titulos[]` com
  `nCodTitulo`, valor, vencimento, categoria) → o vínculo NF ↔ financeiro é direto e confiável.
- Status de pagamento por título via `ConsultarContaPagar` (PAGO / A VENCER / ATRASADO / CANCELADO).

### O que a conciliação verifica, nota a nota
1. **Tem título no Contas a Pagar?** (✓/✕ — pega compra lançada sem financeiro)
2. **O valor do título confere com o valor da NF?** (✓/⚠ — pega divergência de lançamento)
3. **Status do pagamento** (PAGO / A VENCER com data / ATRASADO / SEM TÍTULO)

No teste (03/06): 2 NFs de fornecedor, **2/2 perfeitamente conciliadas**. A seção mostra ainda o
acumulado de compras da semana, do mês e do ano. PDF de teste: msg **877**.

## 5. Fix CRÍTICO — `tpNF` (faturamento estava inflado com compras)

Ao validar a nova seção, as notas de fornecedor **apareceram também na tabela de "Notas Emitidas"**.
Causa: `ListarNF` **sem** o filtro `tpNF` devolve **saída E entrada misturadas** — ou seja, desde a
migração da manhã o "Emitido" somava as compras. Correção: `tpNF:"1"` na consulta de emitidas.

**Números reais de 2026 (até 09/06), após a separação:**

| Indicador | Antes (misturado) | Depois (correto) |
|---|---|---|
| Emitido (vendas, tpNF=1) | R$ 32.240.505,84 | **R$ 23.854.566,83** (1.189 NFs) |
| Compras (entrada, tpNF=0) | — | **R$ 8.385.939,01** (366 NFs) |
| Saldo do ano (receb − pago) | −R$ 7,0M | **+R$ 1,2M** ✅ |

Prova de consistência: 23,85M + 8,39M = **32,24M exatos** (o total antigo). O saldo anual positivo
(recebido R$ 17,9M − pago R$ 16,7M) passou a fazer sentido com a realidade da empresa.

## 6. Borderô v4.1 — nome fantasia em todas as seções

Pedido do Gelson: parar de trabalhar com códigos Omie nas tabelas. Padrão único para **todas** as
seções (entrada ou saída): **NF + nome fantasia + valor + conciliação**.
- Recebimentos: "cód 603299233" → **INFRAMERICA**, VIVACE LOCAÇÕES, LEADER ELEVADORES…
- Pagamentos: coluna "Categoria" (2.06.93…) → **FEDEX, AIR LIQUIDE, LEROY MERLIN, SANTANDER**…
- Resolução via `ConsultarCliente` (nome_fantasia, fallback razão social), com cache — ~35
  consultas/dia, só para os movimentos de ontem.
- A regra antiga de privacidade ("nome só nas emitidas") foi **revogada pelo Gelson** e o registro
  foi atualizado na memória do projeto para nenhuma versão futura regredir.

PDF de teste: msg **878**. **Aprovado pelo Gelson: "isso ficou excelente".**
O cron de 11/06 às 06:00 já sai no formato v4.1.

---

## 7. Ponte Telegram ↔ Claude (Fable 5) — o bot ganhou um cérebro novo

### Problema
O Hermes (container `vpautomation-hermes`, modelo Haiku) vinha dando **respostas desconexas** no
Telegram. O Gelson pediu: *"preciso de respostas reais coletadas na fonte para qualquer pergunta"*
— e quis falar **com o Claude**, no modelo **Fable 5**.

### Solução implantada (`/root/telegram-claude/`)
- **`bridge.py`** — daemon que escuta o bot (long-poll `getUpdates`); cada mensagem dispara
  `claude -p` (modelo **claude-fable-5**) dentro do VPS, com acesso real a Omie, Supabase e à
  memória dos projetos. Resposta volta pelo próprio bot.
- **Whitelist:** apenas Gelson e Diego. Qualquer outro chat é ignorado e logado.
- **Sessão por chat** (`--resume`): a conversa tem memória; `/reset` recomeça.
- **`workspace/CLAUDE.md`** — "alma" da ponte: formato Telegram (texto puro, pt-BR, R$),
  manual de consulta ao Omie (tpNF, deduplicação título+baixa, ConsultarCliente…) e as REGRAS
  de negócio (Bepay/Devoluções isolados, salários sem nomes, nunca inventar números, não
  informar saldo bancário até a conciliação bancária entrar).
- **Serviço systemd** `telegram-claude.service` (enabled, restart automático) — sobrevive a
  reboot do VPS.
- **Hermes desligado** (`docker stop`, reversível). Atenção: religá-lo conflita com a ponte
  (Telegram permite um só consumidor por bot) — é um OU outro.

### Validação
Pergunta-teste *"quantas NFs de venda emitimos em 09/06?"* → **5 notas, R$ 121.720,09**, batendo
exatamente com o borderô. ~60s por resposta com consulta ao Omie (~US$ 0,32). O Gelson conversou
com a ponte minutos após a subida; Diego foi avisado (msg 886).

## 8. Conversa por VOZ — diretriz "100% Claude"

O Gelson pediu para **falar por áudio e ouvir as respostas**. Diretriz dada e registrada em
memória permanente: **a única IA do projeto é o Claude** — Gemini e OpenAI vetados para projetos
novos (a chave OpenAI da VP estava inclusive sem crédito; a do Gemini fica restrita aos legados).

Como a API da Anthropic ainda não processa áudio, a conversão som↔texto usa **código aberto
rodando 100% dentro do VPS** — nenhum áudio sai do servidor e não há mensalidade:
- **Ouvido:** faster-whisper (modelo `small`, CPU) — transcrição pt-BR com precisão de centavos
  em valores falados.
- **Voz:** Piper com a voz brasileira `pt_BR-faber-medium` → OGG/Opus nativo do Telegram.
- Limpeza de fala: emojis/markdown removidos, "R$ 1.234,56" é lido "1.234,56 reais", "NF" vira
  "nota fiscal".

### Fluxo
1. Gelson/Diego manda **áudio** → ponte transcreve e confirma por texto ("🎙️ Entendi: …")
2. Claude (Fable 5) consulta a fonte e responde **curto, em estilo falado**
3. Resposta chega **em voz** + por escrito quando há valores (registro exato dos números)

Desempenho: TTS ~6s · STT ~5–15s · demo de voz entregue ao Gelson (msg **896**).

---

## 9. Estado final dos automatismos da VP (10/06/2026, fim do dia)

| Automatismo | Mecanismo | Status |
|---|---|---|
| Borderô PDF 06:00 seg-sex (Gelson+Diego) | cron VPS `/root/bordero/` | 🟢 v4.1 no ar |
| Relatório matinal 08:30 | pg_cron Supabase job 114 | 🔴 desativado a pedido (reversível) |
| Bot Telegram (perguntas livres, texto e voz) | `telegram-claude.service` + Claude Fable 5 | 🟢 no ar |
| Hermes (container) | docker `vpautomation-hermes` | ⏸️ desligado (substituído pela ponte) |
| pv360 auto-reply WhatsApp | Evolution API | 🟢 inalterado |
| ETL Omie→Supabase (bd_Omie) | pg_cron jobs 98-104 | 🔴 parado (Vault sem credenciais) — pendente |

## 10. Pendências que ficam

1. **Conciliação bancária / posição de caixa** no Borderô — aguarda implantação da conciliação no Omie.
2. **ETL Omie→Supabase**: corrigir credenciais do Vault (jobs 98-104) — espelho segue desatualizado
   (mitigado: Borderô e ponte leem o Omie ao vivo).
3. **Versionar `/root/bordero/` e `/root/telegram-claude/`** neste repositório (sem `.env`).
4. Incidente de segurança de 04/06 (token do bot exposto no histórico deste repo): **revogação do
   token no @BotFather segue pendente** de autorização do Gelson.

---

*Relatório gerado pelo Claude Code (Opus 4.8) na sessão de 10/06/2026, a pedido do Gelson.*
*Sem segredos neste documento — credenciais ficam exclusivamente em `.env`/Vault (lição de 04/06).*
