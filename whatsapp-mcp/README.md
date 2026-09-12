# VerticalParts WhatsApp MCP

Camada corporativa de WhatsApp da VerticalParts, hospedada dentro do VP Automations Hub sem alterar o código existente do Hermes, Evolution API, n8n ou Pós-Venda 360.

## Objetivo

Permitir que Claude Web, Claude Code e sistemas internos usem uma interface única para WhatsApp, sem precisar conhecer endpoints, instâncias, chaves ou detalhes da Evolution API.

Experiência desejada:

- `Use o MCP WhatsApp e avise o responsável que a tarefa foi concluída.`
- `Use o MCP WhatsApp e peça aprovação da requisição.`
- `Use o MCP WhatsApp e envie o borderô para o destinatário.`
- `Use o MCP WhatsApp e mostre as últimas mensagens deste contato.`

## Arquitetura

```text
Claude Web / Claude Code
          |
          v
VerticalParts WhatsApp MCP
          |
          +---- comando humano
          +---- gatilho de sistema
          |
          v
     Evolution API
          |
          v
       WhatsApp
          |
          v
       Webhook
          |
          +---- Pós-Venda 360
          +---- VP Click
          +---- VP Requisições
          +---- Borderô/Hermes
```

O MCP é a interface de comando. Webhooks/eventos são a interface de acontecimentos. Ambos reutilizam a mesma camada Evolution.

## Endpoint planejado

- DNS: `whatsapp-mcp.vpsistema.com`
- MCP: `https://whatsapp-mcp.vpsistema.com/mcp`
- Health: `https://whatsapp-mcp.vpsistema.com/health`

O DNS e o deploy serão ativados somente após os testes locais e a proteção de autenticação.

## Ferramentas da primeira versão

- `whatsapp_status`
- `whatsapp_verificar_numero`
- `whatsapp_enviar_texto`
- `whatsapp_buscar_mensagens`

Próximas fases:

- mídia, documento, áudio, localização e contato;
- respostas e marcação de leitura;
- sumarização e sugestão de resposta;
- aprovações seguras;
- gatilhos de VP Click, VP Requisições, Pós-Venda e Borderô;
- auditoria central e políticas por sistema/origem.

## Segurança

Nenhuma credencial deve ser versionada. O MCP deve receber as credenciais via ambiente e, antes de publicação externa, ficar protegido por autenticação no proxy/MCP.

Ações de aprovação não serão baseadas apenas em texto livre recebido no WhatsApp. Devem validar identidade, telefone autorizado, registro alvo, token de uso único, expiração e idempotência.

## Estrutura

```text
whatsapp-mcp/
├── src/verticalparts_whatsapp_mcp/
│   ├── __init__.py
│   ├── config.py
│   ├── evolution.py
│   └── server.py
├── docs/
│   ├── architecture.md
│   ├── integrations.md
│   ├── security.md
│   └── tools.md
├── .env.example
└── pyproject.toml
```

## Desenvolvimento

```bash
cd whatsapp-mcp
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
verticalparts-whatsapp-mcp
```

Por padrão o servidor usa `stdio`. Para deploy remoto, executar com `MCP_TRANSPORT=streamable-http`.

## Regra de convivência com o repositório

Este módulo é aditivo. Ele não substitui nem altera o Hermes existente, as rotinas do Borderô, a Evolution API atual ou os fluxos n8n já em produção. Integrações existentes serão migradas apenas quando testadas e aprovadas individualmente.
