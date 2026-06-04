# script/ — Borderô Financeiro diário (VerticalParts)

Automação que gera o **Borderô Financeiro** diário em PDF (identidade visual VerticalParts) com
dados reais do **Omie** + **Supabase (bd_Omie)** e envia por **Telegram** a Gelson e Diego.

## Arquivos
| Arquivo | Função |
|---|---|
| `gerar_bordero.py` | Coleta dados (Omie `ListarMovimentos` + Supabase `omie_nfe_emitidas`), monta o HTML e gera o PDF (wkhtmltopdf), opcionalmente envia ao Telegram. |
| `run_cron.sh` | Wrapper chamado pelo cron às 06:00 BRT. Loga em `cron.log` e dispara alerta no Telegram em caso de falha. |
| `.env.example` | Modelo das credenciais. Copie para `.env` (chmod 600) e preencha. **Nunca** versione o `.env`. |

## Uso manual
```bash
python3 gerar_bordero.py --dia 03/06/2026                 # gera o PDF, NÃO envia
python3 gerar_bordero.py --dia 03/06/2026 --enviar gelson  # gera e envia ao Gelson
python3 gerar_bordero.py --enviar gelson,diego             # usa o dia útil anterior
```

## Agendamento (determinístico — não depende de Claude nem do Hermes)
```cron
CRON_TZ=UTC
0 9 * * 1-5 /root/bordero/run_cron.sh   # 09:00 UTC = 06:00 BRT, seg a sex
```
- Mostra sempre o **dia útil anterior** (sex→qui, seg→sex). Descanso sábado/domingo.

## Estrutura do relatório
- **Ontem (detalhe):** notas emitidas (cliente, valor, recebido?, conciliado?), recebimentos e pagamentos.
- **Resumo por período:** Semana (seg→ontem) / Mês / Ano — Emitido · Recebido · Pago · Saldo.

## Regras de negócio (críticas)
- **Bepay** e **Devoluções de Clientes** são isolados (não são caixa real) — pela conta de liquidação (`nCodCC`).
- A API do Omie lista **cada título 2×** (linha do título + linha da baixa); o script **consolida por `nCodTitulo`** para não contar em dobro.
- Posição de caixa/saldo bancário não entra (depende de conciliação bancária).

Dependências de sistema: `wkhtmltopdf`, `xvfb-run`, `python3`, `curl`.
