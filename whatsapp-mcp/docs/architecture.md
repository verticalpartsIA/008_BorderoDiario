# Arquitetura — VerticalParts WhatsApp MCP

## Princípio central

O projeto separa três responsabilidades:

1. MCP: comandos explícitos de Claude Web/Claude Code.
2. Gateway de eventos: gatilhos dos sistemas internos.
3. Webhook receiver: eventos recebidos da Evolution/WhatsApp.

Essa separação evita acoplamento entre os sistemas de negócio e a Evolution API.

## Fluxos

### Comando humano

```text
Usuário -> Claude -> MCP WhatsApp -> Evolution API -> WhatsApp
```

### Gatilho de sistema

```text
VP Click / Requisições / Pós-Venda / Borderô
                 -> gateway/evento
                 -> política
                 -> Evolution API
                 -> WhatsApp
```

### Mensagem recebida

```text
WhatsApp -> Evolution API -> webhook central
         -> persistência/auditoria
         -> roteamento por contexto
         -> sistema responsável / IA / humano
```

## Componentes planejados

- `server.py`: tools MCP.
- `evolution.py`: único adaptador para Evolution API.
- `audit.py`: trilha de auditoria.
- futura camada `events/`: contratos de eventos corporativos.
- futura camada `approvals/`: solicitações e decisões seguras.
- futura camada `webhooks/`: ingestão de mensagens e status.
- futura camada `contacts/`: resolução de pessoa/telefone/JID.

## Integrações-alvo

- 005_vpclick: gatilhos de tarefa, prazo, responsável e status.
- 003_requisicoes: solicitações de aprovação, rejeição, compra e recebimento.
- 004_sac_posvenda360: atendimento, conversas, tickets e histórico.
- 008_BorderoDiario: relatórios, Hermes e automações financeiras.

## DNS e publicação

Planejado:

- `whatsapp-mcp.vpsistema.com`
- `/mcp` para Streamable HTTP.
- `/health` para health check do serviço/proxy.

A publicação deve ocorrer atrás de HTTPS e autenticação. A Evolution API não deve ser exposta diretamente ao Claude ou aos sistemas consumidores.
