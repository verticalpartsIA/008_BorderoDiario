# CLAUDE.md — VerticalParts WhatsApp MCP

Leia este arquivo antes de alterar qualquer coisa dentro de `whatsapp-mcp/`.

## Missão

Construir e manter o gateway corporativo de WhatsApp da VerticalParts como uma camada única entre Claude/sistemas internos e a Evolution API.

O usuário não deve precisar explicar endpoints, instância, JID, payload ou credenciais. A interface deve expressar intenções de negócio por tools MCP e eventos versionados.

## Escopo

Este módulo pode criar e editar arquivos somente dentro de `whatsapp-mcp/`, salvo instrução explícita em contrário.

Não alterar automaticamente:

- código do Hermes;
- rotinas existentes do Borderô;
- configuração atual da Evolution API;
- workflows n8n;
- código existente de outros módulos deste repositório;
- repositórios VP Click, VP Requisições ou Pós-Venda 360.

Esses projetos são integrações externas e devem ser modificados apenas em tarefas próprias, depois que o MCP central estiver homologado.

## Fontes de referência no próprio repositório

Antes de reinventar comportamento, consulte:

- `../evolution-api/send-messages.md`
- `../evolution-api/webhooks.md`
- `../evolution-api/instance-management.md`
- `../integrations/full-stack-architecture.md`
- `../integrations/whatsapp-auto-reply.md`
- documentação do Hermes em `../hermes/`

O Pós-Venda 360 contém implementação real de webhook, histórico, auto-reply, áudio e tratamento de `@lid`, mas não deve ser copiado cegamente. Extraia comportamento genérico e preserve regras específicas no sistema de origem.

## Princípios

1. MCP = comandos explícitos.
2. Eventos = gatilhos automáticos dos sistemas.
3. Webhooks = acontecimentos recebidos do WhatsApp.
4. Evolution API = detalhe interno escondido dos consumidores.
5. Nenhuma credencial em Git.
6. Escritas bloqueadas por padrão durante homologação.
7. Toda escrita gera auditoria.
8. Aprovação financeira exige validação forte e idempotência.
9. Não quebrar fluxos existentes para migrar mais rápido.
10. Mudanças devem ser pequenas, testáveis e reversíveis.

## Convenção de tools

Prefixo obrigatório: `whatsapp_`.

As tools devem ser semânticas e documentadas. Evite criar uma tool genérica do tipo `call_evolution_api`; o objetivo é justamente impedir que agentes precisem conhecer a API subjacente.

## Primeira fase

Manter funcionais e testadas:

- `whatsapp_status`
- `whatsapp_verificar_numero`
- `whatsapp_enviar_texto`
- `whatsapp_buscar_mensagens`

Antes de liberar `whatsapp_enviar_texto` em produção, validar autenticação do MCP e manter destinatário de teste controlado.

## DNS planejado

`https://whatsapp-mcp.vpsistema.com/mcp`

Não assumir que DNS, SSL ou serviço systemd já existem. Verifique a infraestrutura real antes de fazer deploy.

## Definition of Done

Uma mudança só está pronta quando:

- não contém segredo;
- possui tratamento de erro;
- não quebra tools existentes;
- possui teste ou procedimento de validação;
- mantém auditoria para escritas;
- documentação é atualizada quando contrato público muda.
