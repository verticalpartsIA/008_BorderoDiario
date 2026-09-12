# VP Automations Hub

> Hub técnico e operacional das automações da VerticalParts.
>
> **Hermes AI Agent (Telegram)** · **Evolution API (WhatsApp)** · **n8n** · **VerticalParts WhatsApp MCP**

---

## Visão atual

Este repositório deixou de ser apenas documentação do Borderô/Hermes e passa a funcionar como o hub central das automações e canais inteligentes da VerticalParts.

O que já existe continua preservado: Hermes no Telegram, Evolution API, n8n, rotinas financeiras, integração do Pós-Venda 360 e documentação operacional.

A nova camada `whatsapp-mcp/` é aditiva e não altera o código existente. Ela nasce para transformar o WhatsApp em uma capacidade corporativa reutilizável por Claude Web, Claude Code e sistemas internos.

Objetivo final:

```text
"Use o MCP WhatsApp e avise o responsável."
"Use o MCP WhatsApp e peça aprovação desta requisição."
"Use o MCP WhatsApp e envie o borderô."
"Use o MCP WhatsApp e veja se o cliente respondeu."
```

Sem precisar ensinar ao agente qual endpoint da Evolution usar, qual instância chamar ou como montar o payload.

---

## Arquitetura VerticalParts

```text
                         USUÁRIOS / SISTEMAS
                                  |
             +--------------------+--------------------+
             |                    |                    |
             v                    v                    v
       Claude Web/Code          Hermes               n8n
             |                 Telegram                |
             |                    |                    |
             +--------------------+--------------------+
                                  |
                                  v
                       VP Automations Hub
                                  |
                  +---------------+---------------+
                  |                               |
                  v                               v
        VerticalParts WhatsApp MCP          automações existentes
                  |
                  v
             Evolution API
                  |
                  v
               WhatsApp
                  |
                  v
               Webhooks
                  |
        +---------+----------+----------+----------+
        |                    |          |          |
        v                    v          v          v
    Pós-Venda             VP Click  Requisições  Borderô
```

Princípio de arquitetura:

- MCP = comandos explícitos de Claude/humano.
- Eventos = gatilhos automáticos dos sistemas.
- Webhooks = acontecimentos vindos do WhatsApp.
- Evolution API = adaptador de transporte, escondido dos consumidores.

---

## Repositórios e tecnologias de origem

| Ferramenta | GitHub Oficial | Docs Oficiais |
|-----------|---------------|---------------|
| Hermes Agent | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/) |
| Evolution API | [EvolutionAPI/evolution-api](https://github.com/EvolutionAPI/evolution-api) | [doc.evolution-api.com](https://doc.evolution-api.com/) |
| n8n | [n8n-io/n8n](https://github.com/n8n-io/n8n) | [docs.n8n.io](https://docs.n8n.io/) |
| MCP | Model Context Protocol | implementação Python no módulo `whatsapp-mcp/` |

---

## Estrutura do repositório

```text
008_BorderoDiario/
├── hermes/                    # Hermes AI Agent — Telegram, config, Docker e conhecimento
├── evolution-api/             # Evolution API v2 — WhatsApp, mensagens, instâncias e webhooks
├── n8n/                       # Workflows e webhooks de automação
├── integrations/              # Integrações atuais entre Hermes, Evolution, n8n e sistemas VP
├── ops/                       # Operação da VPS e troubleshooting
├── relatorio/                 # Relatórios do Hermes/CFO digital
│
└── whatsapp-mcp/              # NOVO — gateway corporativo de WhatsApp via MCP
    ├── src/verticalparts_whatsapp_mcp/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── evolution.py
    │   ├── audit.py
    │   └── server.py
    ├── docs/
    │   ├── architecture.md
    │   ├── deploy.md
    │   ├── integrations.md
    │   ├── security.md
    │   └── tools.md
    ├── .env.example
    ├── pyproject.toml
    └── README.md
```

---

## VerticalParts WhatsApp MCP

O módulo `whatsapp-mcp/` é o novo ponto único de acesso ao WhatsApp corporativo.

### Primeira versão

Tools implementadas na fundação:

- `whatsapp_status`
- `whatsapp_verificar_numero`
- `whatsapp_enviar_texto`
- `whatsapp_buscar_mensagens`

A escrita nasce bloqueada por padrão com `WHATSAPP_MCP_ALLOW_WRITES=false` até a homologação.

### Próximas capacidades

- envio de mídia, documentos, áudio, localização e contatos;
- conversas e marcação de leitura;
- sugestões e resumos por IA;
- follow-ups e pendências;
- aprovações seguras;
- integração por gatilho com VP Click;
- aprovação e acompanhamento no VP Requisições;
- consolidação gradual do WhatsApp do Pós-Venda 360;
- envio de Borderô e relatórios do Hermes.

### Endpoint planejado

```text
https://whatsapp-mcp.vpsistema.com/mcp
```

O DNS só será criado depois da homologação local, HTTPS e autenticação.

---

## Sistemas que alimentarão o WhatsApp MCP

### 005_vpclick

O VP Click já possui motor de automações. A evolução planejada é adicionar a ação `send_whatsapp` aos gatilhos existentes, como mudança de status, responsável, prioridade e vencimento.

### 003_requisicoes

O MCP será usado para avisos de aprovação, rejeição, compra e recebimento. Aprovações por WhatsApp terão token único, expiração, validação de identidade e idempotência; uma mensagem livre como `aprovo` não será suficiente para decisão financeira.

### 004_sac_posvenda360

É a referência funcional mais madura do WhatsApp atual: webhook, histórico, tickets, resposta automática, transcrição de áudio e tratamento de JID. A migração será gradual, sem desligar o fluxo existente antes da homologação.

### 008_BorderoDiario / Hermes

O Hermes continuará falando pelo Telegram. O novo MCP acrescentará a possibilidade de enviar relatórios, arquivos e avisos também por WhatsApp sem ensinar ao Hermes os detalhes da Evolution API.

---

## Stack VerticalParts — Produção atual

```text
VPS: Hostinger / srv1510643

Serviços existentes:
  vpautomation-hermes       <- Hermes AI Agent / Telegram
  evolution-api             <- Evolution API / WhatsApp
  evolution_api             <- instância/serviço de reserva
  vpautomation-n8n          <- automações n8n
  traefik / nginx           <- reverse proxy / HTTPS conforme serviço
  vp-infra                  <- PostgreSQL + Redis de apoio
```

Infra de apoio inclui Supabase, GitHub, Hostinger e os sites `vpsistema.com`.

Nenhuma credencial deve ser armazenada neste README ou em código versionado.

---

## Segurança

O novo MCP não será publicado como endpoint aberto.

Requisitos antes de produção:

- segredos somente em variáveis de ambiente/secret store;
- autenticação no endpoint MCP;
- Evolution API protegida da internet sempre que possível;
- auditoria de ações;
- escrita desabilitada durante homologação;
- rotação de qualquer credencial antiga que tenha sido exposta em documentação ou histórico;
- validação forte para aprovações e ações financeiras.

Detalhes: [`whatsapp-mcp/docs/security.md`](whatsapp-mcp/docs/security.md).

---

## Links rápidos internos

- [WhatsApp MCP — visão geral](whatsapp-mcp/README.md)
- [WhatsApp MCP — arquitetura](whatsapp-mcp/docs/architecture.md)
- [WhatsApp MCP — tools](whatsapp-mcp/docs/tools.md)
- [WhatsApp MCP — integrações](whatsapp-mcp/docs/integrations.md)
- [WhatsApp MCP — segurança](whatsapp-mcp/docs/security.md)
- [WhatsApp MCP — deploy](whatsapp-mcp/docs/deploy.md)
- [Hermes — Relatório final (CFO digital)](relatorio/RELATORIO-FINAL-HERMES.md)
- [Hermes — Configuração](hermes/README.md)
- [Hermes — Setup VerticalParts](hermes/verticalparts-setup.md)
- [Evolution API — Instância atual](evolution-api/verticalparts-pv360.md)
- [Evolution API — mensagens](evolution-api/send-messages.md)
- [Evolution API — webhooks](evolution-api/webhooks.md)
- [Arquitetura de automações existente](integrations/full-stack-architecture.md)
- [Troubleshooting VPS](ops/troubleshooting.md)

---

## Regra de evolução

O módulo WhatsApp MCP é aditivo. Nenhum código existente do Hermes, Borderô, Evolution, n8n ou Pós-Venda será modificado ou removido sem homologação específica.

A ordem de implantação será:

```text
MCP isolado
-> Evolution em leitura
-> envio controlado
-> auditoria
-> HTTPS + autenticação
-> Claude.ai
-> VP Pós-Venda
-> VP Click
-> VP Requisições
-> Borderô/Hermes
```

---

Atualizado em: 2026-09-11

## Contributors

- Gelson Simões — criador e responsável pelas soluções VerticalParts

**Feito por Gelson Simões**
