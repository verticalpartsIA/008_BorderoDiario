# Ferramentas MCP

## v0.1

### whatsapp_status
Consulta o estado da instância Evolution usada pelo gateway corporativo.

### whatsapp_verificar_numero
Normaliza o telefone e verifica sua existência/endereçamento no WhatsApp.

Entrada principal: `numero`.

### whatsapp_enviar_texto
Envia texto pelo número corporativo.

Entradas: `numero`, `mensagem`.

Proteção inicial: a ferramenta recusa envios enquanto `WHATSAPP_MCP_ALLOW_WRITES=false`.

### whatsapp_buscar_mensagens
Consulta o histórico recente de um telefone ou `remoteJid`.

Entradas: `contato`, `limite`.

## Backlog de ferramentas

- `whatsapp_enviar_midia`
- `whatsapp_enviar_documento`
- `whatsapp_enviar_audio`
- `whatsapp_enviar_localizacao`
- `whatsapp_enviar_contato`
- `whatsapp_responder_mensagem`
- `whatsapp_marcar_como_lida`
- `whatsapp_listar_conversas`
- `whatsapp_contato_360`
- `whatsapp_resumir_conversa`
- `whatsapp_sugerir_resposta`
- `whatsapp_encontrar_pendencias`
- `whatsapp_followup`
- `whatsapp_solicitar_aprovacao`
- `whatsapp_consultar_aprovacao`
- `whatsapp_enviar_relatorio`

## Convenção

As tools devem representar intenção de negócio e esconder detalhes da Evolution API. Claude e sistemas consumidores não devem precisar saber endpoint, API key, instância ou formato interno de JID.
