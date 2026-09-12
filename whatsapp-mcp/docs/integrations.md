# Integrações corporativas

Este documento define como os sistemas VerticalParts devem conversar com o gateway WhatsApp sem depender diretamente da Evolution API.

## VP Click — 005_vpclick

Integração pretendida:

- adicionar ação de automação `send_whatsapp`;
- disparar por `status_changed`, `priority_changed`, `assignee_changed`, `due_date_arrives`, `task_created`, `task_moved` e demais gatilhos já existentes;
- resolver o destinatário por usuário/responsável;
- registrar `task_id` como referência de origem.

Exemplos:

- tarefa concluída -> avisar solicitante;
- prazo próximo -> lembrar responsável;
- tarefa bloqueada -> avisar gestor;
- atribuição alterada -> avisar novo responsável.

## VP Requisições — 003_requisicoes

Integração pretendida:

- avisar quando uma requisição entra em aprovação;
- identificar aprovador designado;
- enviar resumo e link seguro;
- registrar aprovação/rejeição somente após validação segura;
- avisar comprador após aprovação;
- avisar solicitante sobre rejeição, compra e recebimento.

O gateway não deve decidir regras de alçada. Ele apenas transporta e registra a interação. A regra de negócio continua pertencendo ao VP Requisições.

## VP Pós-Venda 360 — 004_sac_posvenda360

O Pós-Venda já contém a implementação mais madura de WhatsApp na VerticalParts e servirá como referência funcional para:

- recebimento via webhook;
- histórico;
- ticket vinculado;
- resposta automática;
- transcrição de áudio;
- tratamento de `@lid`;
- persistência das mensagens.

A migração para o gateway central deverá ser gradual. O fluxo atual não será removido até o novo serviço passar por homologação end-to-end.

## Borderô / Hermes — 008_BorderoDiario

Integração pretendida:

- enviar borderôs, relatórios, alertas financeiros e arquivos;
- permitir que Hermes solicite envio por WhatsApp sem conhecer a Evolution API;
- manter o Telegram atual funcionando em paralelo;
- futuramente receber respostas operacionais pelo mesmo gateway.

## Contrato de evento proposto

Os sistemas internos deverão emitir eventos com formato semelhante a:

```json
{
  "source": "vpclick",
  "event": "task.completed",
  "record_id": "uuid-ou-codigo",
  "recipient": {
    "user_id": "uuid-opcional",
    "phone": "5511999999999"
  },
  "template": "task_completed",
  "data": {
    "title": "Tarefa X",
    "url": "https://..."
  },
  "idempotency_key": "vpclick:task.completed:uuid:versao"
}
```

O formato final será versionado antes de integrar produção.

## Regra de acoplamento

Nenhum sistema novo deve chamar diretamente endpoints `/message/*` da Evolution API. Chamadas diretas existentes serão mantidas temporariamente até migração controlada.
