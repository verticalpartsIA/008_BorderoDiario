# VP Automations Hub

> Engineering reference for the VerticalParts automation stack:
> **Hermes AI Agent** · **Evolution API (WhatsApp)** · **n8n**

---

## Repositórios de origem

| Ferramenta | GitHub Oficial | Docs Oficiais |
|-----------|---------------|---------------|
| Hermes Agent | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/) |
| Evolution API | [EvolutionAPI/evolution-api](https://github.com/EvolutionAPI/evolution-api) | [doc.evolution-api.com](https://doc.evolution-api.com/) |
| n8n | [n8n-io/n8n](https://github.com/n8n-io/n8n) | [docs.n8n.io](https://docs.n8n.io/) |

---

## Estrutura do repositório

```
vp-automations-hub/
├── hermes/                   # Hermes AI Agent — config, Telegram, Docker
│   ├── README.md
│   ├── config-reference.md   # Referência completa do config.yaml
│   ├── telegram-setup.md     # Setup do gateway Telegram
│   ├── docker-deployment.md  # Backend Docker para terminal
│   ├── soul-template.md      # Template SOUL.md para VerticalParts
│   └── verticalparts-setup.md # Como rodamos na VP (vpautomation-hermes)
│
├── evolution-api/            # Evolution API v2 — WhatsApp, webhooks
│   ├── README.md
│   ├── docker-setup.md       # docker-compose + variáveis de ambiente
│   ├── instance-management.md # Criar, conectar, gerenciar instâncias
│   ├── send-messages.md      # Endpoints de envio (texto, mídia, etc.)
│   ├── webhooks.md           # Eventos, configuração, payloads
│   ├── at-lid-limitation.md  # Problema @lid — WhatsApp privacy feature
│   └── verticalparts-pv360.md # Nossa instância pv360 — configuração e ops
│
├── n8n/                      # n8n — workflows, webhooks, Docker
│   ├── README.md
│   ├── docker-setup.md       # docker-compose para n8n self-hosted
│   ├── webhook-nodes.md      # Como usar Webhook como trigger
│   └── verticalparts-setup.md # Nossa instância vpautomation-n8n
│
├── integrations/             # Guias de integração entre as ferramentas
│   ├── evolution-to-n8n.md   # Evolution API webhook → n8n workflow
│   ├── whatsapp-auto-reply.md # Auto-reply Claude via WhatsApp
│   └── full-stack-architecture.md # Arquitetura completa VP
│
└── ops/                      # Operações VPS, Docker, troubleshooting
    ├── vps-infrastructure.md  # Infraestrutura Docker no VPS
    ├── docker-commands.md    # Comandos Docker úteis
    └── troubleshooting.md    # Problemas comuns e soluções
```

---

## Stack VerticalParts — Produção

```
VPS: 72.61.48.156 (Hostinger KVM 2 vCPU / 8GB RAM)
OS:  Ubuntu 22.04 LTS

Containers ativos:
  vpautomation-hermes       ← Hermes AI Agent (Telegram, Traefik HTTPS)
  evolution-api             ← Evolution API v2.2.3 porta 8080 (pv360 conectado)
  evolution_api             ← Evolution API v2 porta 8081 (reserva, vazio)
  vpautomation-n8n          ← n8n automações porta 5678
  traefik                   ← Reverse proxy HTTPS (Let's Encrypt)
  vp-infra (postgres+redis) ← Infraestrutura compartilhada

Domínio: srv1510643.hstgr.cloud
Hermes URL: https://vpautomation-hermes.srv1510643.hstgr.cloud

Infra de apoio:
  Supabase jkbklzlbhhfnamaeislb   ← pv360 database + Realtime
  GitHub: github.com/verticalpartsIA
  Hostinger Node.js               ← Deploy automático (push → main)
```

---

## Links rápidos internos

- [Hermes — Relatório final (CFO digital)](relatorio/RELATORIO-FINAL-HERMES.md)
- [Hermes — Configuração e colagens](hermes/README.md)
- [Hermes — Setup VerticalParts](hermes/verticalparts-setup.md)
- [Evolution API — Instância pv360](evolution-api/verticalparts-pv360.md)
- [Problema @lid WhatsApp](evolution-api/at-lid-limitation.md)
- [Arquitetura completa](integrations/full-stack-architecture.md)
- [Troubleshooting VPS](ops/troubleshooting.md)

---

*Atualizado em: 2026-05-31*
