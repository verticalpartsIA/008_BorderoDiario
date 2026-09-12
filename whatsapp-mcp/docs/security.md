# Segurança — VerticalParts WhatsApp MCP

## Regras obrigatórias

1. Nenhuma API key, token, senha ou service role pode ser versionada.
2. O endpoint MCP público deve exigir autenticação antes de liberar ferramentas.
3. A Evolution API deve permanecer acessível apenas pela camada interna/gateway sempre que possível.
4. Toda ação de escrita deve gerar auditoria.
5. Aprovações de negócio exigem identidade verificável e não podem depender apenas de texto livre recebido no WhatsApp.

## Controle de escrita

A primeira versão nasce com:

`WHATSAPP_MCP_ALLOW_WRITES=false`

Assim, consultas podem ser homologadas sem permitir envio acidental. O envio só deve ser liberado após:

- autenticação externa pronta;
- teste com destinatário controlado;
- auditoria validada;
- confirmação da instância correta;
- rotação de credenciais antigas expostas em documentação/histórico.

## Aprovações

Uma aprovação por WhatsApp deverá usar no mínimo:

- `approval_id`;
- usuário/aprovador esperado;
- telefone/JID autorizado;
- token aleatório de uso único;
- expiração;
- registro de `used_at`;
- decisão recebida;
- idempotency key;
- trilha de auditoria.

A mensagem `aprovo` isolada não deve executar uma decisão financeira.

## Auditoria mínima

Registrar:

- timestamp;
- ferramenta/ação;
- ator/origem;
- sistema de origem;
- telefone/JID;
- registro de negócio relacionado;
- message_id retornado pela Evolution;
- resultado;
- erro quando houver.

Não registrar segredos nem conteúdo sensível desnecessário.

## LGPD e retenção

O gateway deve armazenar apenas os dados necessários para operação e auditoria. Políticas de retenção de conversas e anexos devem ser definidas antes da consolidação de todos os sistemas no serviço central.
