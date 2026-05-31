# RELATÓRIO FINAL — Hermes (VerticalParts AI)

**Data:** 2026-05-31
**Autor:** Claude (Claude Code) a pedido de Gelson Simões
**Objetivo da sessão:** transformar o Hermes (agente AI no Telegram) num CFO digital confiável,
que consulta o banco real, domina linguagem financeira avançada e emite relatórios em PDF/HTML.

---

## 0. TL;DR — estado final

O Hermes está **100% operacional como CFO digital**. Responde com dados reais do ERP Omie,
domina indicadores financeiros avançados (ROI/ROE/ROA/ROIC/EVA/valuation), tem 12+ comandos "/",
é proativo (sempre sugere algo a mais) e emite Gráfico, Borderô e DRE em PNG+PDF+HTML, entregando
os arquivos direto no Telegram.

---

## 1. INFRAESTRUTURA (mapa do Hermes)

- **VPS:** srv1510643.hstgr.cloud (72.61.48.156), Ubuntu 24.04, root: `230520@#HOVPn`.
- **Container:** `vpautomation-hermes` (imagem ghcr.io/hostinger/hvps-hermes-agent). Porta 32768→4860.
- **Dados persistentes (HERMES_HOME):** `/opt/data/` no container. Contém:
  - `config.yaml` (modelo, quick_commands, toolsets) · `memories/MEMORY.md` (memória cross-canal,
    limite ~2200 chars) · `SOUL.md` (identidade) · `.env` (chaves) · `skills/` (skills) ·
    `reports/` (PDFs gerados) · `.hermes/telegram_token` (token persistido).
- **LLM:** claude-haiku-4-5 (provider anthropic). Também tem chave OpenRouter.
- **Canal:** Telegram. Usuários: Gelson (2129471333), Diego Maeno (7175937401).
  Bot token: `8211134154:AAFeJaAtSxOgGm3V0BIeN4SIyBRHD3dxXjY`.
- **Banco:** Supabase bd_Omie `kgecbycsyrtdhmdziuul` (service_role no .env como SUPABASE_SERVICE_KEY).

### ⚠️ DESCOBERTA CRÍTICA — o sandbox isolado
O Hermes **executa código Python/Bash num SANDBOX isolado** (hostname `fffa6df3a0f0`,
imagem nikolaik/python-nodejs), NÃO no filesystem do container `vpautomation-hermes`.
Consequência: instalar libs/variáveis via `docker exec` no container **NÃO chega ao Hermes**.
A forma correta é mandar o PRÓPRIO Hermes se configurar (ele tem terminal, pip e internet no sandbox).
Essa confusão custou várias tentativas — não repetir.

---

## 2. PROBLEMAS ENCONTRADOS E CORRIGIDOS (ordem cronológica)

1. **Tabelas "vazias" / chave anon**
   - Sintoma: Hermes dizia que CR_Omie/CP_Omie/omie_orders estavam vazias (0 registros).
   - Causa: usava a chave **anon** (RLS bloqueia → retorna 0 silenciosamente). A service_role no
     .env funcionava (HTTP 200, 25.509 pedidos), mas skills/memória mandavam usar anon.
   - Fix: forçar uso de `$SUPABASE_SERVICE_KEY` em todo lugar; substituir a anon por service_role
     em skills, sessões e state.db.

2. **Contagens erradas (31.808 pedidos)**
   - Causa: memória envenenada com números antigos + método errado (contava por MAX(id)).
   - Fix: MEMORY.md reescrita com contagens reais e regra "contar com HEAD + Prefer: count=exact,
     ler Content-Range; nunca por MAX(id)".

3. **Skill `supabase-omie-verticalparts` desatualizada**
   - Continha anon key hardcoded, schema inventado (valor/status) e narrativa falsa
     ("ETL quebrado / culpe o n8n / dados vazios").
   - Fix: reescrita (v2) com service_role, schema real e proibição de citar n8n/quebrado.
   - Também removida a skill redundante `supabase-data-access` (mesma intoxicação).

4. **Limpeza de dados pré-2024 (no Supabase, feito pelo Gelson no SQL Editor)**
   - DELETE em CP_Omie/CR_Omie com data_vencimento < 2024-01-01 e datas corrompidas (>2100, ex: 2424).
   - Resultado: CP 26.716→26.091, CR 12.566→12.490. Banco começa em 2024.

5. **Relatórios não chegavam / SVG**
   - Hermes salvava em /tmp e só passava o caminho (inacessível); gerava SVG (Telegram não mostra).
   - Fix: regra de entrega — sempre ENVIAR o arquivo (sendPhoto/sendDocument), PNG para preview,
     PDF/HTML para documento. Nunca só o caminho.

6. **Libs ausentes (matplotlib/Pillow/reportlab)**
   - Tentativas via docker exec falharam porque iam para o container, não para o sandbox.
   - Fix definitivo: o Hermes instalou no SEU sandbox (pip via get-pip, internet OK).

7. **TELEGRAM_BOT_TOKEN ausente no sandbox**
   - O token estava no .env do container, mas o sandbox não herdava.
   - Fix: token passado ao Hermes; ele persistiu em `/opt/data/.hermes/telegram_token` (chmod 600)
     e gravou na memória a regra de ler do arquivo.

---

## 3. ARQUITETURA DE CONHECIMENTO ("Penta Inteligente")

| Camada | Onde | Conteúdo |
|--------|------|----------|
| Memória (kernel) | MEMORY.md (~2k chars, cross-canal) | Identidade CFO, service_role, contar certo, schema, gatilho de skills |
| Skill verticalparts-cfo | /opt/data/skills/.../verticalparts-cfo | Playbooks: caixa, NCG, ciclo, inadimplência, liquidez, endividamento, PE, ABC, crescimento |
| Skill financas-avancadas | /opt/data/skills/.../financas-avancadas | ROI/ROE/ROA/ROIC/EVA, liquidez, alavancagem, atividade, capital de giro, valuation (VPL/TIR/WACC), unit economics, DuPont, Z-Score |
| Skill relatorios-pdf | /opt/data/skills/.../relatorios-pdf | Gráfico (matplotlib), Borderô (CP/CR), DRE completo — em PNG+PDF+HTML, enviados no Telegram |
| Quick commands "/" | config.yaml | /saude /caixa /rentabilidade /ciclo /inadimplencia /folha /dre /valuation /compras /risco /grafico /bordero |
| Proatividade | memória + skills | Toda resposta termina com "💡 Sugiro também:" (1-3 sugestões no contexto) |

---

## 4. CONHECIMENTO DE NEGÓCIO GRAVADO

### Schema / status reais (bd_Omie)
- CR_Omie / CP_Omie: valor em **valor_documento**; status em **status_titulo**.
  - CR: RECEBIDO, A VENCER, ATRASADO, VENCE HOJE, CANCELADO.
  - CP: PAGO, A VENCER, ATRASADO, CANCELADO. NÃO existe "A RECEBER".
  - Em aberto = NOT IN (RECEBIDO/PAGO, CANCELADO). Inadimplência = ATRASADO.
- Nome do cliente/fornecedor: JOIN PN_Omie por codigo_cliente_omie → nome_fantasia/razao_social.
- Faturamento real = omie_nfe_itens tipo='S' (saída). Compra/entrada = tipo='E'.
- Contagens reais (31/05/2026): omie_orders 25.509 · CR 12.490 · CP 26.091 · nfe_itens 45.609 ·
  PN_Omie 13.827 · Produtos_VP 4.140 · sellers 99.
- Horizonte 2024+; HÁ vencimentos futuros (compra/venda parcelada). "Total" ≠ "recorte por mês".

### Folha de pagamento (regra gravada)
- Categorias de SALÁRIO: **2.03.78 (Operacional)** e **2.03.87 (Administrativo)**.
  Complementos: 2.03.91 Pró-Labore; encargos 2.03.71/72 FGTS, 2.03.73/74 INSS, 2.03.08/59/60 IRRF;
  benefícios 2.03.68 Assist. Médica; 2.03.69 Pensão. **NÃO usar 2.01.01 como salário.**
- Vence no **5º dia útil** do mês (contar pulando fins de semana E feriados).
- Junho/2026: 5º dia útil = **08/06** (Corpus Christi 04/06 é feriado). Folha salários ≈
  **R$ 158.443,58** (Adm 91.197,00 + Op 67.246,58). [Confirmar com Gelson se Corpus Christi é folga.]

### Estrutura do DRE (tabela dre_category_map)
- Mapeia cada categoria do Omie (codigo) → linha do DRE (codigo_dre, dre_descricao, dre_sinal).
- Linhas: 1.01.01 Receita Bruta(+) · 1.01.02 Impostos(−) · 1.01.03 Deduções(−) ·
  1.21.02 Custo Serviços(−) · 1.21.03 Outros Custos(−) · 2.01.01 Desp.Variáveis(−) ·
  2.11.01 Pessoal(−) · 2.11.02 Administrativas(−) · 2.11.04 Vendas/Mkt(−) · 2.11.05 Outros Tributos(−) ·
  1.11.02 Receitas Financeiras(+) · 2.11.03 Desp.Financeiras(−) · 1.11.01 Outras Receitas(+).
  Ignorar 3.01.xx (balanço). Subtotais calculados: Rec.Líquida, Lucro Bruto, EBITDA, Resultado Líquido.

---

## 5. CRÉDITO DE ACESSO (lembrete de segurança)
- service_role bd_Omie e bot token estão no .env/credenciais. Uso restrito; não versionar em repo público.
- O Hermes só atende Gelson e Diego; não exclui dados, não aprova pagamentos sem confirmação humana.

---

## 6. PENDÊNCIAS / PRÓXIMOS PASSOS
- [ ] Confirmar se Corpus Christi (04/06) é folga na VP (ajusta o 5º dia útil).
- [ ] Validar visualmente o DRE de Abril enviado (números batendo).
- [ ] Testar /folha e /bordero end-to-end.
- [ ] PERSISTÊNCIA DO SANDBOX: as libs e o token vivem no sandbox; se o sandbox for RECRIADO,
      podem sumir. Solução definitiva: pré-instalar matplotlib/Pillow/reportlab/requests e injetar
      TELEGRAM_BOT_TOKEN no Dockerfile/config do sandbox (nikolaik/python-nodejs). Hoje sobrevive a
      restart, não necessariamente a recriação.
- [ ] Cron do relatório financeiro diário 8h (seg-sex) no Telegram (COLAGEM já preparada).
- [ ] Outros sistemas VP (Requisições, Pós-Venda 360, PRD, Click): dar acesso quando desejado.

---

## 7. ARQUIVOS DESTA PASTA (vpHermes/hermes/)
- vps-discovery.md — mapa inicial da VPS e do Hermes.
- hermes-inteligencia.md — primeiro spec de inteligência financeira.
- limpeza-pre2024.sql — script de saneamento do banco.
- COLAGEM-1-memory-kernel.md / COLAGEM-2-skill-cfo.md — base CFO.
- COLAGEM-A-skill-financas-avancadas.md — indicadores avançados.
- COLAGEM-B-slash-commands-e-proatividade.md — comandos "/" + proatividade + folha.
- COLAGEM-C-skill-relatorios-pdf.md — relatórios PDF/HTML (Gráfico/Borderô/DRE).
- COLAGEM-D-correcao-envio.md — regra de ENVIAR arquivo no Telegram.
- COLAGEM-E-instalar-libs.md — instalação de libs (lição do sandbox).
- MEMORY-novo.md / SKILL-novo.md — versões aplicadas.
- RELATORIO-FINAL-HERMES.md — este documento.

*Fim. Para a próxima sessão: o Hermes é autônomo — dê a meta e deixe-o se auto-configurar no
sandbox dele; não tente instalar pelo host.*
