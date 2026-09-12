# RAG MCP WhatsApp VerticalParts — SPEC + SDD + Retrieval + Fine-Tuning Ready

> Documento canônico para qualquer LLM, agente ou automação que precise entender, projetar, implementar, revisar ou operar o MCP WhatsApp da VerticalParts.
>
> Este documento trata exclusivamente de WhatsApp: envio, recebimento, gatilhos, prazos, devoluções, aprovações, links de ação, respostas, auditoria, segurança, idempotência, entrega, leitura, escalonamento e automações relacionadas ao canal WhatsApp.

---

# 0. REGRA DE OURO — PERGUNTE PRIMEIRO QUAL É O PLANO DO WHATSAPP

Quando o usuário pedir algo genérico como:

- “coloque WhatsApp nessa função”;
- “mande mensagem quando acontecer isso”;
- “quero avisar o gestor”;
- “crie um gatilho de WhatsApp”;
- “use o MCP WhatsApp nesse módulo”;
- “faça o WhatsApp cobrar essa tarefa”;

A LLM não deve começar pela implementação.

Primeiro deve descobrir o plano daquele uso do WhatsApp.

A pergunta central é:

> Qual é o plano desse uso de WhatsApp: o que dispara a mensagem, quem deve recebê-la, qual ação essa pessoa precisa executar, qual link deve abrir, qual prazo existe e o que deve acontecer se ela não agir ou não responder?

Se parte dessas informações já estiver explícita, não repita perguntas desnecessárias. Complete somente as lacunas que alteram a arquitetura ou a regra de envio.

O objetivo é impedir uma implementação tecnicamente correta, porém sem propósito de negócio claro.

---

# PARTE I — PLANO DE USO DO WHATSAPP

## 1. Questionário mínimo que a LLM deve resolver

Antes de criar uma nova automação de WhatsApp, identificar:

1. Origem: qual evento ou ação inicia o fluxo?
2. Motivo: por que a mensagem precisa existir?
3. Destinatário: quem deve receber?
4. Resolução do destinatário: de onde vem o telefone correto?
5. Momento: quando exatamente deve disparar?
6. Frequência: uma vez, recorrente, lembrete, escalonamento?
7. Conteúdo: quais informações são necessárias para a pessoa entender o contexto?
8. CTA: o que o destinatário deve fazer depois de ler?
9. Link: existe endereço web específico para executar a ação?
10. Prazo: até quando a ação deve ser realizada?
11. Retorno esperado: o sistema espera clique, resposta, alteração de status, envio de documento ou nenhuma resposta?
12. Ausência de ação: o que acontece se a pessoa ignorar a mensagem?
13. Escalonamento: alguém superior deve ser avisado?
14. Urgência: normal, importante, urgente ou crítica?
15. Janela de envio: pode enviar à noite, fim de semana ou feriado?
16. Idempotência: como impedir mensagem duplicada para o mesmo evento?
17. Auditoria: qual registro de negócio deve ficar associado à mensagem?
18. Privacidade: há dado pessoal, financeiro, contratual ou sensível que não deve aparecer no texto?
19. Resposta recebida: quem deve tratar uma eventual resposta pelo WhatsApp?
20. Critério de sucesso: o que prova que o fluxo cumpriu sua função?

## 2. Plano de Uso WhatsApp — estrutura canônica

Toda nova função relevante deve conseguir ser descrita assim:

```yaml
whatsapp_plan:
  name: "approval_requested"
  purpose: "Acordar o aprovador e levá-lo à tela correta"
  trigger:
    type: "business_event"
    event: "approval.requested"
  recipient:
    role: "approver"
    source: "record_owner_or_rule"
  message:
    template: "approval_requested"
    urgency: "important"
  action:
    expected: "open_url_and_decide"
    url: "https://sistema.exemplo/registro/123/aprovar"
  deadline:
    due_at: "2026-09-15T17:00:00-03:00"
  followup:
    enabled: true
    remind_before_minutes: 120
    overdue_after_minutes: 60
  escalation:
    enabled: true
    after_minutes: 180
    to_role: "manager"
  idempotency_key: "approval.requested:123:v1"
  audit:
    record_type: "approval"
    record_id: "123"
```

O formato concreto pode evoluir, mas a semântica acima deve permanecer reconhecível.

## 3. Pergunte somente o que falta

Exemplo ruim:

Usuário: “Quando uma tarefa vencer, mande WhatsApp para o responsável com o link da tarefa.”

Resposta ruim da LLM: fazer vinte perguntas, inclusive “quem recebe?” e “qual é a ação esperada?”, embora isso já esteja dito.

Resposta correta: identificar que destinatário, gatilho e CTA já existem e perguntar somente por lacunas importantes, por exemplo:

- com quanto tempo de antecedência deve lembrar?
- deve repetir depois do vencimento?
- existe escalonamento para gestor?
- há horário em que não devemos enviar?

---

# PARTE II — IDENTIDADE E ARQUITETURA DO MCP WHATSAPP

## 4. Missão

O MCP WhatsApp é a camada corporativa responsável por permitir que LLMs e automações usem WhatsApp por intenções de negócio, sem precisar conhecer detalhes internos de endpoint, instância, API key, JID ou payload do provedor.

A experiência desejada é semântica:

- verificar se um número possui WhatsApp;
- enviar uma mensagem;
- consultar mensagens recentes;
- lembrar um responsável;
- solicitar uma aprovação;
- notificar uma devolução;
- avisar que há uma pendência;
- cobrar uma ação vencida;
- enviar documento ou relatório quando essa capability existir;
- receber uma mensagem e encaminhá-la ao contexto correto.

## 5. Três responsabilidades separadas

A arquitetura deve preservar três caminhos distintos.

### 5.1 MCP — comando explícito

```text
Usuário -> LLM -> MCP WhatsApp -> camada de WhatsApp -> destinatário
```

Exemplo:

“Use o MCP WhatsApp e avise João que o documento está disponível.”

### 5.2 Gateway de eventos — gatilho automático

```text
Evento do sistema -> gateway de eventos -> política -> WhatsApp -> destinatário
```

Exemplo:

Uma aprovação muda para `aguardando_aprovador` e o sistema emite `approval.requested`.

### 5.3 Webhook — acontecimento recebido

```text
WhatsApp -> webhook -> deduplicação -> auditoria -> correlação -> roteamento
```

Exemplo:

O destinatário responde à conversa; a mensagem recebida deve ser associada ao contato e, quando possível, ao processo que originou a interação.

## 6. Princípio de acoplamento

Sistemas consumidores não devem precisar saber:

- endpoint de envio;
- formato interno de JID;
- chave de API;
- nome da instância;
- detalhes do payload do provedor;
- particularidades de transporte.

Eles devem expressar intenção, evento, destinatário e contexto.

## 7. Tools atuais do MCP

A primeira versão documentada possui:

### `whatsapp_status`

Consulta o estado da instância corporativa de WhatsApp.

### `whatsapp_verificar_numero`

Normaliza o telefone e verifica existência/endereçamento no WhatsApp.

Formatos brasileiros aceitos pela implementação atual incluem exemplos como:

- `011997663780`
- `11997663780`
- `5511997663780`

O formato interno deve ser normalizado antes do uso.

### `whatsapp_enviar_texto`

Envia uma mensagem de texto. A escrita deve respeitar o controle de homologação e pode permanecer bloqueada por configuração até a liberação de produção.

### `whatsapp_buscar_mensagens`

Consulta histórico recente de um telefone ou identificador remoto compatível.

## 8. Backlog semântico de tools

Capabilities planejadas ou desejáveis:

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

Regra: a LLM deve descobrir as tools realmente disponíveis na sessão e nunca fingir que um item do backlog já está implementado.

---

# PARTE III — SPEC: REQUISITOS FUNCIONAIS

## 9. FR-WA-001 — Descoberta de capability

Antes de chamar uma função:

1. observar as tools disponíveis;
2. escolher a tool mais específica;
3. ler o schema de entrada;
4. não inventar tool;
5. se a capability não existir, declarar a limitação e propor a evolução correta.

## 10. FR-WA-002 — Classificação da intenção

Toda solicitação deve ser classificada em uma ou mais intenções:

- consulta de status;
- verificação de número;
- mensagem manual;
- notificação transacional;
- lembrete;
- cobrança de prazo;
- solicitação de ação;
- aprovação;
- devolução/retorno;
- escalonamento;
- follow-up;
- envio de documento;
- envio de mídia;
- consulta de conversa;
- tratamento de resposta;
- alerta crítico;
- confirmação de conclusão.

## 11. FR-WA-003 — Resolução do destinatário

Não enviar apenas porque existe um nome textual.

O destinatário deve ser resolvido de forma confiável por um ou mais identificadores:

- user_id;
- contact_id;
- telefone cadastrado;
- telefone explicitamente informado pelo usuário;
- relação de responsável registrada no evento.

Se houver dois contatos possíveis, a LLM deve desambiguar antes do envio.

## 12. FR-WA-004 — Normalização e verificação de telefone

Antes de mensagens críticas ou primeiro contato automatizado:

- remover formatação visual;
- normalizar DDI/DDD/número;
- tratar zero de chamada brasileiro quando aplicável;
- verificar existência no WhatsApp quando a capability estiver disponível;
- registrar o telefone normalizado na auditoria, não credenciais.

A apresentação ao usuário pode ser amigável; o transporte deve usar representação consistente.

## 13. FR-WA-005 — Mensagem deve ter propósito e CTA

Notificação operacional não deve existir apenas para “informar”. Quando houver ação esperada, declarar de forma objetiva:

- o que aconteceu;
- o que a pessoa deve fazer;
- até quando;
- onde deve clicar.

Exemplo estrutural:

```text
Olá, {nome}.
A aprovação de {assunto} está aguardando sua decisão.
Prazo: {prazo}.
Acesse: {url}
```

## 14. FR-WA-006 — Link de ação

Quando a mensagem acorda alguém para executar uma atividade, preferir deep link para a tela exata do registro.

Evitar:

- mandar apenas o endereço da página inicial;
- pedir que o usuário procure manualmente o item;
- incluir ação sensível diretamente na URL sem proteção;
- expor dados secretos no query string.

## 15. FR-WA-007 — Gatilho por evento

Um gatilho deve representar acontecimento de negócio, não detalhe de interface.

Preferir:

- `approval.requested`
- `task.due_soon`
- `task.overdue`
- `proposal.returned`
- `contract.signed`
- `worklog.missing`

Evitar eventos frágeis como:

- `button_clicked`
- `modal_opened`
- `screen_loaded`

A mensagem deve ser causada por mudança significativa de estado.

## 16. FR-WA-008 — Mensagem por prazo

Para tarefas e ações com vencimento, o plano deve definir:

- data/hora de vencimento;
- lembrete antecipado;
- tolerância após vencimento;
- quantidade máxima de lembretes;
- horário permitido de envio;
- regra de cancelamento do lembrete quando a tarefa for concluída;
- escalonamento quando permanecer pendente.

Nunca enviar lembrete de uma tarefa já concluída porque um job antigo não foi cancelado ou revalidado.

## 17. FR-WA-009 — Mensagem de devolução/retorno

Quando um processo muda de mão, a mensagem deve informar claramente:

- o que retornou;
- quem realizou a ação anterior quando apropriado;
- qual é o novo responsável;
- qual é o próximo passo;
- link para o registro.

Exemplos:

- proposta devolvida pelo cliente;
- cotação respondida pelo fornecedor;
- contrato assinado;
- formulário preenchido;
- diário de obra respondido;
- documento rejeitado e devolvido para correção.

## 18. FR-WA-010 — Aprovação segura

WhatsApp pode avisar que há uma aprovação e levar o aprovador à ação segura.

Uma decisão sensível não deve ser executada apenas porque chegou uma mensagem textual “aprovo”.

Quando houver aprovação mediada pelo WhatsApp, exigir no mínimo:

- `approval_id`;
- aprovador esperado;
- telefone/JID autorizado;
- token aleatório de uso único quando aplicável;
- expiração;
- estado atual da aprovação;
- registro de uso;
- idempotency key;
- trilha de auditoria.

O caminho preferencial é: WhatsApp desperta o aprovador -> aprovador abre link seguro -> sistema valida identidade e estado -> decisão é registrada.

## 19. FR-WA-011 — Idempotência

Todo gatilho automático deve possuir chave idempotente.

Exemplo:

`task.due_soon:task-123:2026-09-15T15:00:v1`

A mesma chave não deve gerar duas mensagens efetivas.

A idempotência deve ser validada antes do envio e registrada depois do envio.

## 20. FR-WA-012 — Retry seguro

Falha de transporte não significa necessariamente que a mensagem não foi enviada.

Antes de reenviar após timeout:

1. verificar se existe `message_id` conhecido;
2. verificar estado persistido do evento;
3. consultar status quando possível;
4. repetir somente se houver evidência suficiente de não envio;
5. usar backoff;
6. limitar tentativas.

## 21. FR-WA-013 — Cancelamento de mensagem pendente

Se o motivo da mensagem deixar de existir antes do disparo, cancelar.

Exemplos:

- tarefa foi concluída antes do lembrete;
- aprovação foi realizada;
- contrato foi assinado;
- diário foi enviado;
- pendência foi corrigida.

Toda rotina agendada deve revalidar o estado atual imediatamente antes do envio.

## 22. FR-WA-014 — Escalonamento

Escalonamento não é spam progressivo.

Definir:

- condição objetiva;
- tempo de espera;
- destinatário seguinte;
- mensagem apropriada ao novo destinatário;
- limite de níveis;
- regra de encerramento.

Exemplo:

```text
T0: responsável recebe tarefa
T-2h: responsável recebe lembrete
T+1h: responsável recebe atraso
T+4h: gestor recebe escalonamento
```

## 23. FR-WA-015 — Horário silencioso

O plano deve definir política de horário.

Por padrão, mensagens não críticas podem ser adiadas para janela útil quando caírem em horário inconveniente.

Alertas críticos podem possuir exceção explicitamente configurada.

A LLM não deve inventar o que é “crítico”; isso precisa estar na política do fluxo.

## 24. FR-WA-016 — Templates internos

Mensagens recorrentes devem usar templates internos versionados.

Cada template deve ter:

- `template_id`;
- versão;
- propósito;
- campos obrigatórios;
- texto-base;
- CTA esperado;
- nível de urgência;
- restrições de dado;
- exemplo renderizado.

Mudança substancial no significado deve criar nova versão.

## 25. FR-WA-017 — Personalização controlada

Personalizar somente com dados disponíveis e necessários.

Permitido:

- nome;
- título da tarefa;
- código do registro;
- prazo;
- responsável;
- link seguro;
- resumo curto.

Não inventar nome, valor, prazo ou status ausente.

## 26. FR-WA-018 — Conteúdo mínimo necessário

WhatsApp é canal de acionamento, não deve virar dump de banco de dados.

Preferir:

- contexto curto;
- ação clara;
- prazo;
- link.

Quando o conteúdo for longo, enviar resumo e apontar para a tela ou documento adequado.

## 27. FR-WA-019 — Dados sensíveis

Evitar enviar pelo texto:

- segredo de acesso;
- token reutilizável;
- credencial;
- dados pessoais desnecessários;
- informações financeiras completas quando um resumo basta;
- documentos confidenciais sem controle adequado.

O link pode levar a uma área autenticada onde o usuário autorizado vê os detalhes.

## 28. FR-WA-020 — Mensagens recebidas

Ao receber mensagem:

1. validar evento do webhook;
2. deduplicar por identificador da mensagem;
3. identificar telefone/JID;
4. extrair tipo e conteúdo;
5. registrar metadados necessários;
6. correlacionar com conversa/processo quando possível;
7. decidir rota de atendimento;
8. registrar resultado do roteamento.

## 29. FR-WA-021 — Resposta textual não é ação de negócio por padrão

Uma resposta “ok”, “feito”, “sim”, “não”, “aprovo” ou “pode seguir” não deve alterar automaticamente um registro sensível sem contrato explícito e validação forte.

A resposta pode:

- ser registrada;
- notificar um responsável;
- alimentar triagem;
- sugerir próxima ação;
- iniciar um fluxo seguro de confirmação.

## 30. FR-WA-022 — Correlação de conversa

Quando a mensagem foi originada por um evento de negócio, manter referência suficiente para saber:

- qual evento iniciou;
- qual registro estava envolvido;
- quem recebeu;
- qual mensagem foi enviada;
- qual resposta chegou;
- qual estado final foi alcançado.

## 31. FR-WA-023 — Mídia e documento

Quando essas capabilities existirem:

- validar tipo e tamanho;
- usar nome de arquivo compreensível;
- evitar arquivo temporário exposto publicamente sem expiração;
- auditar envio;
- não considerar “enviado” sinônimo de “lido”.

## 32. FR-WA-024 — Falhas explícitas

Distinguir:

- número inválido;
- número sem WhatsApp;
- instância desconectada;
- autenticação inválida;
- escrita bloqueada;
- timeout;
- erro do provedor;
- mensagem rejeitada;
- destinatário não resolvido;
- template com dados ausentes;
- evento duplicado.

Nunca responder “enviado” se a chamada falhou.

## 33. FR-WA-025 — Auditoria

Toda escrita deve registrar, no mínimo:

- timestamp;
- ação/tool;
- ator/origem;
- evento;
- telefone/JID normalizado;
- template/versão quando aplicável;
- registro de negócio relacionado;
- idempotency key;
- `message_id` retornado;
- resultado;
- erro quando houver.

Não registrar segredo ou conteúdo sensível desnecessário.

## 34. FR-WA-026 — Observabilidade

Métricas desejáveis:

- eventos recebidos;
- mensagens tentadas;
- mensagens enviadas;
- falhas;
- duplicatas bloqueadas;
- destinatários inválidos;
- tempo evento -> envio;
- entregas confirmadas quando disponíveis;
- leituras quando disponíveis;
- ações concluídas após mensagem;
- escalonamentos;
- follow-ups cancelados porque a ação já ocorreu.

A melhor métrica não é “quantas mensagens enviamos”; é “quantas ações corretas foram destravadas com o mínimo de mensagens”.

---

# PARTE IV — MOTIVOS CANÔNICOS PARA DISPARAR WHATSAPP

## 35. Família A — Gatilhos de aprovação

1. Aprovação solicitada: um responsável precisa avaliar algo.
2. Aprovação próxima do prazo: ainda não houve decisão.
3. Aprovação vencida: prazo passou e ação continua pendente.
4. Aprovação rejeitada: solicitante precisa corrigir ou tomar ciência.
5. Aprovação concluída: próximo responsável precisa continuar o fluxo.
6. Aprovação escalonada: gestor superior precisa assumir ou cobrar.

## 36. Família B — Tarefas e prazos

7. Nova tarefa atribuída.
8. Responsável da tarefa alterado.
9. Prazo se aproximando.
10. Tarefa vencida.
11. Tarefa bloqueada por dependência.
12. Tarefa desbloqueada e pronta para execução.
13. Tarefa concluída e solicitante deve ser avisado.
14. Tarefa reaberta e volta a exigir ação.
15. Prioridade aumentada e responsável precisa ser alertado.
16. SLA próximo de estourar.
17. SLA estourado e gestor deve ser escalonado.

## 37. Família C — Propostas, cotações e documentos

18. Proposta disponível para avaliação.
19. Proposta acessada pelo destinatário, quando essa informação for útil ao fluxo.
20. Proposta devolvida com resposta ou pedido de revisão.
21. Proposta revisada e novamente disponível.
22. Solicitação de cotação enviada a fornecedor.
23. Cotação recebida e responsável interno precisa analisar.
24. Cotação não respondida dentro do prazo.
25. Documento rejeitado e devolvido para correção.
26. Documento corrigido e reenviado.
27. Documento final disponível para consulta.

## 38. Família D — Contratos e assinaturas

28. Contrato disponível para leitura/assinatura.
29. Contrato visualizado e ainda não assinado, quando o fluxo exigir acompanhamento.
30. Prazo de assinatura próximo do fim.
31. Contrato assinado e responsável interno deve prosseguir.
32. Assinatura recusada ou devolvida com observação.
33. Link seguro de assinatura perto de expirar.

## 39. Família E — Campo, obra, vistoria e diário

34. Diário de obra solicitado ao responsável.
35. Diário de obra recebido.
36. Diário de obra não respondido até o horário definido.
37. Medição pronta para avaliação.
38. Marco de execução atingido e alguém precisa conferir.
39. Vistoria agendada.
40. Vistoria próxima do horário.
41. Vistoria concluída com pendências.
42. Pendência de obra atribuída.
43. Pendência corrigida aguardando validação.
44. Não conformidade crítica registrada.
45. Evidência/foto/documento solicitado e ainda ausente.

## 40. Família F — Atendimento e retorno

46. Cliente respondeu e há ação interna pendente.
47. Fornecedor respondeu e há análise pendente.
48. Prestador respondeu e há validação pendente.
49. Mensagem ficou sem resposta por período definido.
50. Follow-up agendado chegou ao momento de execução.
51. Conversa precisa de intervenção humana.
52. Informação prometida ficou pronta e deve ser devolvida ao contato.
53. Atendimento transferido para novo responsável.
54. Pendência foi resolvida e contato deve ser informado.

## 41. Família G — Operação e exceção

55. Processo entrou em estado de erro e exige ação humana.
56. Integração falhou repetidamente e responsável técnico precisa ser avisado.
57. Registro ficou parado além do tempo aceitável.
58. Material/documento esperado chegou e libera próxima etapa.
59. Data importante foi alterada e envolvidos precisam ser notificados.
60. Evento foi cancelado ou reagendado.
61. Acesso/link temporário está prestes a expirar.
62. Etapa crítica concluída e próximo dono do processo precisa assumir.
63. Confirmação humana é necessária antes de continuar uma ação de risco.
64. Alerta de segurança operacional exige leitura imediata.

Estes motivos são padrões, não regras universais. Cada implementação deve passar pelo Plano de Uso WhatsApp.

---

# PARTE V — SDD: CONTRATO DE EVENTOS

## 42. Evento corporativo de WhatsApp

Formato recomendado:

```json
{
  "version": "1.0",
  "source": "sistema-origem",
  "event": "task.due_soon",
  "occurred_at": "2026-09-12T14:30:00-03:00",
  "record": {
    "type": "task",
    "id": "task-123",
    "title": "Enviar ficha técnica"
  },
  "recipient": {
    "user_id": "user-456",
    "contact_id": null,
    "phone": "5511999999999",
    "role": "assignee"
  },
  "notification": {
    "template": "task_due_soon",
    "template_version": 1,
    "urgency": "important"
  },
  "action": {
    "type": "open_url",
    "label": "Abrir tarefa",
    "url": "https://sistema.exemplo/tarefas/task-123"
  },
  "deadline": {
    "due_at": "2026-09-12T17:00:00-03:00"
  },
  "data": {
    "minutes_remaining": 150
  },
  "idempotency_key": "task.due_soon:task-123:2026-09-12T14:30:v1"
}
```

## 43. Campos obrigatórios conceituais

Todo evento automático deve possuir:

- origem;
- nome do evento;
- timestamp;
- registro relacionado;
- destinatário resolvível;
- template ou intenção;
- ação esperada quando houver;
- idempotency key.

## 44. Validação do evento

Antes do envio:

```text
receber evento
  -> validar versão
  -> validar campos
  -> verificar idempotência
  -> revalidar estado de negócio
  -> resolver destinatário
  -> normalizar/verificar telefone
  -> aplicar política de horário
  -> renderizar template
  -> validar conteúdo
  -> enviar
  -> persistir message_id
  -> auditar resultado
```

## 45. Máquina de estados da notificação

Estados recomendados:

```text
planned
  -> queued
  -> sending
  -> sent
  -> delivered        (quando disponível)
  -> read             (quando disponível)
  -> acted            (ação de negócio concluída)
```

Estados alternativos:

```text
queued -> cancelled
sending -> failed
sent -> expired
sent -> escalated
sent -> superseded
```

`acted` deve vir de evidência do processo, não apenas de leitura da mensagem.

---

# PARTE VI — SDD: GATILHOS, PRAZOS E FOLLOW-UP

## 46. Agendamento robusto

Nunca confiar apenas no job agendado criado no passado.

No momento de disparar:

1. carregar estado atual;
2. confirmar que a condição ainda vale;
3. confirmar destinatário atual;
4. confirmar prazo atual;
5. verificar se já houve mensagem equivalente;
6. enviar somente se ainda necessário.

## 47. Política de lembrete

Exemplo configurável:

```yaml
reminders:
  before_due:
    - 24h
    - 2h
  after_due:
    - 1h
  escalation:
    after: 4h
    max_levels: 1
```

Isso é apenas um modelo. A LLM deve perguntar a regra adequada quando não estiver definida.

## 48. Supressão inteligente

Não enviar:

- lembrete após conclusão;
- aprovação após decisão;
- cobrança após resposta válida;
- follow-up se o responsável foi substituído sem recalcular destinatário;
- mensagem duplicada pelo mesmo evento;
- alerta já coberto por evento mais novo que o tornou obsoleto.

---

# PARTE VII — SDD: TEMPLATES DE MENSAGEM

## 49. Estrutura recomendada

Uma mensagem operacional boa costuma ter quatro blocos:

```text
1. contexto: o que aconteceu
2. responsabilidade: por que estou recebendo
3. ação: o que preciso fazer
4. caminho: link e prazo
```

## 50. Template — aprovação

```text
Olá, {nome}.
{assunto} está aguardando sua avaliação.
Prazo: {prazo}.
Acesse para decidir: {url}
```

## 51. Template — prazo próximo

```text
Olá, {nome}.
A tarefa “{titulo}” vence em {tempo_restante}.
Acesse para concluir: {url}
```

## 52. Template — vencido

```text
Olá, {nome}.
A tarefa “{titulo}” venceu em {data_hora} e ainda consta como pendente.
Acesse: {url}
```

## 53. Template — devolução

```text
Olá, {nome}.
{objeto} retornou para sua análise.
Motivo/resumo: {resumo}
Próxima ação: {acao}
Acesse: {url}
```

## 54. Template — ausência de resposta

```text
Olá, {nome}.
Ainda não recebemos o retorno de {objeto}, solicitado em {data}.
Prazo atual: {prazo}.
Acesse: {url}
```

## 55. Template — escalonamento

```text
Olá, {gestor}.
{objeto} permanece pendente há {tempo} com {responsavel}.
Prazo original: {prazo}.
Acesse: {url}
```

## 56. Regras de texto

- ser direto;
- identificar o contexto sem excesso de dados;
- usar prazo concreto;
- colocar link acionável;
- evitar jargão técnico do transporte;
- evitar ameaças ou tom agressivo;
- não fingir urgência inexistente;
- não usar “último aviso” sem regra real;
- não expor informação desnecessária.

---

# PARTE VIII — WEBHOOK E RESPOSTAS RECEBIDAS

## 57. Pipeline de entrada

```text
webhook recebido
  -> validar estrutura
  -> identificar event/message id
  -> deduplicar
  -> ignorar eventos não suportados
  -> extrair remetente
  -> normalizar identidade remota
  -> extrair texto/mídia
  -> persistir metadados necessários
  -> correlacionar contexto
  -> aplicar regra de roteamento
  -> encaminhar para tratamento
```

## 58. Tipos de conteúdo

O receiver deve estar preparado, conforme capabilities implementadas, para:

- texto;
- áudio;
- imagem;
- documento;
- vídeo;
- localização;
- contato;
- reação;
- mensagem citada/respondida.

Não presumir que toda mensagem possui texto simples.

## 59. Identidade remota

O canal pode apresentar identificadores diferentes do telefone canônico. A camada central deve esconder esses detalhes dos consumidores e resolver telefone/JID de forma consistente.

Quando houver `@lid` ou outro identificador alternativo, preservar capacidade de correlação sem forçar os sistemas consumidores a conhecer a implementação interna.

## 60. Roteamento de resposta

Uma resposta pode ser roteada por:

- conversa ativa;
- último evento correlacionado;
- token/contexto da mensagem original;
- contato;
- registro explicitamente citado;
- fila humana padrão quando não for possível determinar contexto com segurança.

Em ambiguidade, não alterar processo automaticamente.

---

# PARTE IX — SEGURANÇA, PRIVACIDADE E GOVERNANÇA

## 61. Escrita controlada

Durante homologação, a escrita pode permanecer bloqueada por configuração.

Antes de liberar envio real, validar:

- autenticação do MCP;
- instância correta;
- destinatário de teste controlado;
- auditoria;
- tratamento de erro;
- idempotência;
- limites de envio;
- política de conteúdo.

## 62. Segredos

Nunca versionar ou mostrar:

- API keys;
- tokens;
- senhas;
- secrets de proxy;
- credenciais da instância.

## 63. LGPD e minimização

Armazenar apenas o necessário para:

- entrega;
- correlação;
- auditoria;
- suporte;
- segurança.

Definir política de retenção para mensagens e anexos antes de consolidar grande volume histórico.

## 64. Opt-out e preferência de canal

Fluxos externos devem respeitar políticas aplicáveis de consentimento, relacionamento e opt-out.

Se um contato não deve receber determinada classe de mensagem, a política de envio precisa impedir o disparo antes do provedor.

## 65. Anti-spam operacional

Mesmo mensagens legítimas podem virar ruído.

Controles recomendados:

- deduplicação;
- limite por evento;
- limite por destinatário/tempo;
- agrupamento de notificações quando apropriado;
- cancelamento de lembrete obsoleto;
- escalonamento em vez de repetição infinita;
- prioridade definida pelo negócio.

---

# PARTE X — FINE-TUNING READY / COMPORTAMENTO DA LLM

## 66. Regra comportamental principal

Quando o usuário pedir “adicione WhatsApp” sem especificação suficiente, a resposta esperada da LLM é descobrir o Plano de Uso WhatsApp antes de codificar.

### Exemplo positivo 1

Usuário:

“Quero WhatsApp na aprovação.”

LLM:

“Qual é o plano dessa aprovação pelo WhatsApp? Preciso saber o evento que dispara, quem é o aprovador, qual link ele deve abrir, prazo, lembrete/escalonamento e o que acontece se ele não agir.”

### Exemplo positivo 2

Usuário:

“Quando a tarefa faltar 2 horas para vencer, envie WhatsApp ao responsável com o link; se vencer, espere 1 hora e avise o gestor.”

LLM:

Não deve perguntar novamente gatilho, responsável, prazo de lembrete e escalonamento. Deve confirmar somente lacunas relevantes, como resolução de telefone, janela de envio e idempotência, caso ainda não estejam padronizadas.

### Exemplo positivo 3

Usuário:

“Avise o cliente que a proposta foi revisada.”

LLM:

Deve descobrir se existe ação esperada, qual URL abre a proposta, como o cliente é resolvido e se há prazo para resposta.

### Exemplo positivo 4

Usuário:

“O montador não enviou o diário até 18h. Cobre pelo WhatsApp.”

LLM:

Deve interpretar como gatilho temporal condicionado: às 18h verificar novamente se o diário continua ausente; somente então enviar. Não deve programar envio cego sem revalidar estado.

### Exemplo positivo 5

Usuário:

“Use o MCP WhatsApp e consulte se 011997663780 existe.”

LLM:

Deve usar a tool real de verificação, deixar a normalização para a camada do MCP e retornar o resultado sem inventar identidade do titular.

### Exemplo positivo 6

Usuário:

“Envie para Carlos: contrato pronto.”

LLM:

Se houver mais de um Carlos ou nenhum telefone resolvido, deve desambiguar antes do envio. Nome não é identificador suficiente.

### Exemplo positivo 7

Usuário:

“Depois que o fornecedor responder a cotação, avise o comprador.”

LLM:

Deve modelar evento de retorno, resolver o comprador atual e incluir link da análise. A mensagem deve ocorrer uma vez por resposta relevante, com idempotência.

### Exemplo positivo 8

Usuário:

“Se ele não responder, mande de novo a cada 10 minutos.”

LLM:

Deve questionar essa política e propor limite/follow-up razoável, pois repetição ilimitada cria spam e não melhora governança. Precisa definir máximo de tentativas e escalonamento.

### Exemplo positivo 9

Usuário:

“Quando chegar ‘aprovo’ pelo WhatsApp, aprove a compra.”

LLM:

Não deve implementar decisão sensível baseada em texto livre. Deve propor identificação do aprovador, estado da aprovação, token/link seguro, expiração, idempotência e auditoria.

### Exemplo positivo 10

Usuário:

“Envie o mesmo aviso para 200 contatos.”

LLM:

Deve identificar se é fluxo transacional ou disparo em massa, verificar política de envio, consentimento, limites e risco de spam antes de executar.

## 67. Anti-exemplos proibidos

### Anti-exemplo A

Usuário: “adicione WhatsApp”.

Errado: começar a programar `sendText` sem saber gatilho, destinatário ou propósito.

### Anti-exemplo B

Evento de tarefa concluída recebido duas vezes.

Errado: enviar duas mensagens sem idempotência.

### Anti-exemplo C

Lembrete programado para uma tarefa agora concluída.

Errado: enviar porque o cron disparou sem revalidar estado.

### Anti-exemplo D

Timeout no envio.

Errado: reenviar imediatamente sem verificar se a primeira mensagem foi aceita.

### Anti-exemplo E

Usuário “Carlos” possui dois telefones possíveis.

Errado: escolher o primeiro arbitrariamente.

### Anti-exemplo F

Mensagem “aprovo”.

Errado: executar aprovação financeira ou contratual somente com esse texto.

### Anti-exemplo G

Tool de envio de documento não existe na sessão.

Errado: fingir que enviou o arquivo.

### Anti-exemplo H

Número não verificado e mensagem crítica.

Errado: afirmar sucesso sem retorno real do provedor.

---

# PARTE XI — TESTES DE ACEITAÇÃO

## 68. Checklist da LLM antes de desenhar uma função

A LLM deve conseguir responder:

- Sei o gatilho?
- Sei por que a mensagem existe?
- Sei quem recebe?
- Sei de onde vem o telefone?
- Sei qual ação é esperada?
- Existe link correto?
- Existe prazo?
- Existe follow-up?
- Existe escalonamento?
- Existe janela de envio?
- Existe idempotency key?
- Existe critério de cancelamento?
- Existe auditoria?
- Sei o que fazer com a resposta recebida?
- Sei o que prova sucesso?

Se respostas essenciais forem “não”, perguntar antes de implementar.

## 69. Testes mínimos de engenharia

Um fluxo automatizado deve testar:

1. número válido;
2. número inválido;
3. número sem WhatsApp;
4. destinatário ambíguo;
5. evento válido;
6. evento duplicado;
7. evento obsoleto;
8. tarefa concluída antes do lembrete;
9. timeout de envio;
10. retry sem duplicidade;
11. template com campo ausente;
12. horário silencioso;
13. escalonamento;
14. resposta recebida;
15. resposta duplicada;
16. resposta ambígua;
17. aprovação com token expirado;
18. aprovação por pessoa errada;
19. auditoria sem segredo;
20. indisponibilidade da instância.

## 70. Definition of Done

Uma nova função WhatsApp só está pronta quando:

- Plano de Uso WhatsApp está definido;
- gatilho é inequívoco;
- destinatário é resolvido de modo seguro;
- mensagem possui propósito claro;
- CTA e link foram testados quando aplicável;
- idempotência existe;
- revalidação de estado existe para gatilhos temporais;
- erro e retry estão tratados;
- auditoria existe;
- segredo não foi versionado;
- testes positivos e negativos passaram;
- documentação foi atualizada;
- homologação foi feita com destinatário controlado antes da liberação ampla.

---

# PARTE XII — PROMPT CANÔNICO PARA QUALQUER LLM

```text
Você está trabalhando com o MCP WhatsApp da VerticalParts.

OBJETIVO
Usar WhatsApp como canal de ação operacional: avisar a pessoa certa, no momento certo, com contexto suficiente, uma ação clara e um caminho seguro para executá-la.

REGRA PRINCIPAL
Quando o usuário pedir uma nova função de WhatsApp e o plano não estiver completo, pergunte primeiro qual é o plano daquele uso: gatilho, destinatário, motivo, ação esperada, link, prazo, follow-up, escalonamento, resposta esperada e critério de sucesso. Não comece pela implementação se essas decisões alterarem o desenho.

REGRAS
1. Descubra e use somente tools realmente disponíveis.
2. Não invente tool, envio, entrega, leitura, contato, número ou resultado.
3. Resolva destinatário antes de enviar.
4. Normalize e, quando apropriado, verifique o número.
5. Use eventos de negócio, não cliques de interface, como gatilhos.
6. Todo gatilho automático precisa de idempotência.
7. Todo lembrete agendado deve revalidar o estado antes de enviar.
8. Uma mensagem operacional deve dizer o que aconteceu, o que a pessoa precisa fazer, prazo e link quando aplicável.
9. Não execute aprovação sensível apenas por texto livre recebido no WhatsApp.
10. Em timeout, verifique estado antes de retry.
11. Não envie segredo ou dado sensível desnecessário.
12. Toda escrita deve ser auditável.
13. Evite spam: limite lembretes, cancele notificações obsoletas e use escalonamento com política definida.
14. Quando a capability não existir, diga isso e descreva corretamente a evolução necessária.
15. O sucesso do WhatsApp não é apenas enviar mensagem; é destravar a ação correta sem duplicidade e com rastreabilidade.
```

---

# PARTE XIII — RESUMO ULTRACURTO

```text
Antes de implementar: descubra o Plano de Uso WhatsApp.
Pergunte somente o que falta.
Gatilho -> revalidar estado -> resolver destinatário -> idempotência -> renderizar -> enviar -> auditar.
Mensagem boa = contexto + ação + prazo + link.
Prazo exige cancelamento quando resolvido.
Sem resposta exige política de follow-up/escalonamento, não spam infinito.
Resposta textual não autoriza ação sensível por padrão.
Timeout não autoriza retry cego.
Use somente tools reais.
```

---

# PARTE XIV — FONTES INTERNAS DE VERDADE DO MÓDULO

Ao trabalhar dentro de `whatsapp-mcp/`, consultar conforme a tarefa:

- `CLAUDE.md` — missão, limites e Definition of Done;
- `README.md` — visão geral e capabilities;
- `docs/architecture.md` — separação MCP, eventos e webhook;
- `docs/tools.md` — tools atuais e backlog;
- `docs/security.md` — regras de escrita, aprovação, auditoria e privacidade;
- `docs/integrations.md` — contrato de evento e padrões de gatilho;
- `src/verticalparts_whatsapp_mcp/server.py` — contrato efetivamente implementado das tools;
- `src/verticalparts_whatsapp_mcp/evolution.py` — adaptador de transporte;
- `src/verticalparts_whatsapp_mcp/audit.py` — auditoria disponível.

A implementação real prevalece para dizer o que está disponível hoje. Este RAG prevalece como política de desenho e comportamento para novas funções.

---

# FIM DO DOCUMENTO CANÔNICO

Uma LLM não precisa reler o documento inteiro em toda chamada. Deve usá-lo como política e índice, recuperando as seções necessárias ao tipo de trabalho solicitado.