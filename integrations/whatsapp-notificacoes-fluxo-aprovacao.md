# Notificações de WhatsApp por etapa de fluxo de aprovação — guia de replicação

> Implementado originalmente no **VPRequisições** (`verticalpartsIA/003_requisicoes`),
> setembro/2026. Este documento existe para que **outra sessão de Claude**, atuando em
> **outra solução** VerticalParts, entenda o que foi feito e replique o mesmo padrão —
> sem reinventar do zero, sem adivinhar credenciais, e sabendo exatamente como tirar
> dúvida quando precisar.
>
> Se você é uma sessão de Claude lendo isto porque o Gelson pediu para "fazer a mesma
> coisa" em outro projeto: leia a **Seção 1 (protocolo de dúvidas)** antes de tudo.

---

## 1. Protocolo de comunicação entre sessões Claude (leia primeiro)

Este sistema foi implementado por uma sessão de Claude que roda dentro da VPS da
VerticalParts (o Gelson se refere a ela como **"Claude VPS"**). Você — a sessão que
está lendo este documento agora, em outro projeto/solução — **não tem acesso direto**
a essa sessão. A única forma de comunicação entre vocês dois é através de **GitHub
Issues neste mesmo repositório**: `verticalpartsIA/008_BorderoDiario`.

Se, ao implementar isso na sua solução, você tiver qualquer dúvida real (não uma
suposição que dá pra resolver lendo o código de `003_requisicoes` referenciado
abaixo):

1. **Não adivinhe.** Principalmente valores de credenciais, IDs de instância, ou
   decisões de negócio (quem deve ser avisado em qual etapa, etc.).
2. Explique a dúvida com clareza para o Gelson e peça a ele, literalmente:
   > "Gelson, cole essa dúvida no Claude VPS pra ele poder me esclarecer."
3. O Gelson vai repassar sua pergunta para a sessão Claude VPS (ela é quem mantém o
   contexto operacional de toda a VerticalParts). A resposta virá de volta **em
   forma de uma Issue** (ou comentário em issue existente) neste repositório:
   👉 https://github.com/verticalpartsIA/008_BorderoDiario/issues
4. Abra a issue com o prefixo `[Dúvida <nome do seu projeto>]` no título e a label
   `question`, para ficar rastreável. Aguarde a resposta lá antes de prosseguir em
   qualquer ponto incerto — **não prossiga adivinhando**.
5. **Nunca cole valor real de credencial (API key, token, senha) numa Issue.** Este
   repositório é **público**. Peça a variável por nome; o valor real vem do cofre
   central de credenciais ou diretamente do Gelson por um canal seguro — nunca por
   aqui.

Esse protocolo existe porque as duas sessões de Claude (a desta solução nova e a
"Claude VPS") não compartilham memória nem contexto entre si — o Gelson é o único
elo humano entre as duas, e o GitHub Issues é o único canal assíncrono confiável.

---

## 2. Contexto e objetivo

O VPRequisições (sistema interno de requisições de compra/viagem/serviço/manutenção)
tem um fluxo de aprovação em várias etapas (V1 Aberto → V2 Cotação → V3 Aprovação →
V4 Compra → V5 Recebimento). Cada vez que uma requisição muda de etapa, as pessoas
certas (gestor, comprador, aprovador por alçada, e o próprio solicitante) recebem uma
mensagem de WhatsApp automática com um link direto para agir.

O objetivo deste documento é permitir reaproduzir esse mesmo padrão de "avisar por
WhatsApp a cada mudança de etapa de um fluxo" em **qualquer outra solução** da
VerticalParts que tenha um fluxo de aprovação parecido (ex.: outro sistema com
etapas tipo "aguardando aprovação", "aguardando compra", etc.).

---

## 3. Infraestrutura de envio (Evolution API)

O envio real de WhatsApp usa uma instância **Evolution API** já em produção,
compartilhada entre projetos VerticalParts (é a mesma usada pelo pv360/Verti). Você
**não precisa subir uma instância nova** — só precisa das credenciais de acesso a
ela.

- **Não peça o endpoint/instância/API key adivinhando ou reaproveitando valores que
  você tenha visto em outro contexto.** Peça ao Gelson (via protocolo da Seção 1 se
  a sua sessão atual não tiver acesso direto ao cofre de credenciais do projeto).
- A forma de envio é uma chamada HTTP simples: `POST {EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}`,
  header `apikey: {EVOLUTION_APIKEY}`, body `{ "number": "<DDI+DDD+número só dígitos>", "text": "<mensagem>" }`.

---

## 4. Variáveis de ambiente necessárias

Nomes exatos usados no VPRequisições (adapte o prefixo ao nome do seu projeto se
fizer sentido, mas mantenha os mesmos 4 papéis):

| Variável | Para que serve | Tem fallback no código? |
|---|---|---|
| `EVOLUTION_API_URL` | URL base da instância Evolution API | Sim — cai num default hardcoded se ausente |
| `EVOLUTION_APIKEY` | Chave de autenticação da Evolution API | **Não** — se ausente, todo envio é silenciosamente pulado (`skipped_no_apikey`) |
| `EVOLUTION_INSTANCE` | Nome da instância dentro da Evolution API | Sim — cai num default hardcoded se ausente |
| `<PROJETO>_BASE_URL` (ex. `VPREQ_BASE_URL`) | URL pública do seu app, usada nos links dentro da mensagem (ex. "🔗 Aprovar: ...") | Sim, mas **cuidado**: se o fallback for um domínio antigo/temporário, os links das mensagens apontam pro lugar errado. Sempre configure explicitamente. |

**Onde conseguir os valores reais:** cofre central de credenciais da VerticalParts
(Supabase Vault, ver instruções em `verticalpartsIA/001_vpsistema` →
`Instruções/COFRE_CREDENCIAIS.md`) ou perguntando ao Gelson diretamente. **Nunca**
adivinhe, reaproveite um valor de outro projeto sem confirmar, ou commite o valor
real em qualquer repositório — principalmente este (`008_BorderoDiario`), que é
**público**.

---

## 5. Padrão de arquitetura de código

Dois arquivos por feature, mesmo padrão usado em outras integrações do mesmo
projeto (ex. `features/vpclick/`):

```
src/features/whatsapp/
├── client.ts   # tipo dos estágios + wrapper fino, chamado pela UI
└── server.ts   # lógica de verdade: resolve destinatários, monta texto, envia, loga
```

### `client.ts` — chamado pela tela (nunca bloqueia o fluxo principal)

```ts
import { notifyWhatsappStage } from "@/features/whatsapp/server";

export type WhatsappStage =
  | "LIDER_CIENCIA"
  | "COMPRADOR_COTAR"
  | "APROVACAO_PENDENTE"
  | "COMPRA_APROVADA";
  // ... + estágios de aviso ao próprio solicitante (ver seção 6)

export interface WhatsappNotifyInput {
  stage: WhatsappStage;
  requisitionId: string;
  ticketNumber: string;
  title: string;
  module: string;
  requesterName: string;
  requesterId?: string;
  requesterDepartment?: string;
  totalValue?: number;
  rejectionReason?: string;
}

export async function notifyWhatsappClient(input: WhatsappNotifyInput): Promise<void> {
  await notifyWhatsappStage({ data: input });
}
```

**Regra de uso na UI, sempre:**
```ts
void notifyWhatsappClient({ ...input }).catch(console.warn);
```
Nunca `await` bloqueando a ação principal (aprovar/cotar/comprar) — o WhatsApp é um
efeito colateral, e uma falha de envio **nunca pode impedir** a ação de negócio.

### `server.ts` — regras principais (server function, roda no backend)

- `sendWhatsappText(number, text, context)`: normaliza o número (só dígitos), se
  vazio → loga `skipped_no_number` e sai; se sem `EVOLUTION_APIKEY` → loga
  `skipped_no_apikey` e sai (nunca lança exceção); faz o `fetch` e loga
  `sent`/`error` com o status HTTP e corpo da resposta (truncado).
- Resolução de destinatários por papel: `getUserIdsByRole("comprador")`,
  `getUserIdsByRoleAndTier("aprovador", tier)` — consulta direta em `user_roles`.
- Resolução do "líder que dá ciência": aprovador pessoal designado
  (`profiles.approver_id`) ou, na falta, os gestores do departamento
  (`department_managers`) — mesma regra usada no resto do fluxo de aprovação, **não
  duplique essa lógica**, reaproveite a already existente no seu projeto se houver
  algo equivalente.
- Alçada por valor: busca thresholds configuráveis (`settings` table:
  `tier1_max`/`tier2_max`) com fallback pra default, calcula o tier e filtra
  aprovadores por `approval_tier`.
- **Nunca lança exceção pro chamador.** Todo o corpo do handler principal é
  `try/catch`, e mesmo o `catch` loga a tentativa (com `status: "error"`) em vez de
  deixar sem rastro.

Cada estágio é um `if (stage === "...")` dentro de uma única server function
(`notifyWhatsappStage`), recebendo um payload validado por `zod` com o `stage` como
`z.enum([...])`. Adote o mesmo padrão: **um enum central de estágios**, não uma
função por estágio.

---

## 6. Estágios implementados no VPRequisições (referência completa)

| Estágio | Quando dispara | Quem recebe |
|---|---|---|
| `LIDER_CIENCIA` | Requisição criada (qualquer módulo) | Aprovador pessoal do solicitante, ou gestores do departamento |
| `COMPRADOR_COTAR` | Gestor dá ciência | Todos com `role=comprador` |
| `APROVACAO_PENDENTE` | Cotação finalizada | `role=aprovador` filtrado pelo tier calculado do valor total |
| `COMPRA_APROVADA` | Aprovação financeira concedida | Todos com `role=comprador` |
| `REQUISITANTE_CIENCIA_OK` | Gestor dá ciência | O próprio solicitante |
| `REQUISITANTE_REPROVADO_GESTOR` | Gestor reprova | O próprio solicitante (inclui motivo + aviso que pode editar/reenviar) |
| `REQUISITANTE_APROVADO_FINANCEIRO` | Aprovação financeira concedida | O próprio solicitante |
| `REQUISITANTE_REPROVADO_FINANCEIRO` | Aprovação financeira negada | O próprio solicitante (inclui motivo + aviso que pode editar/reenviar) |
| `REQUISITANTE_COMPRADO` | Compra finalizada (V4) | O próprio solicitante |

**Decisão de produto importante, validada com o Gelson**: além de avisar quem
precisa **agir** na próxima etapa, o solicitante original é avisado em **toda**
mudança de status da própria requisição dele (aprovado, reprovado, comprado) —
inclusive reprovações, porque reprovar às vezes só pede um ajuste + reenvio, não é
definitivo. Ao replicar em outro projeto, considere se esse mesmo par
"quem-age / quem-solicitou" faz sentido lá também.

**Pontos de disparo no código** (para referência de "onde plugar" — adapte aos
arquivos equivalentes do seu projeto): `src/routes/{trips,products,services,
maintenance,freight,rental}.tsx` (criação → `LIDER_CIENCIA`), `src/routes/
approval.tsx` (ciência do gestor, aprovação/reprovação financeira — 6 pontos, com
duplicação entre a fila normal e a de "decisão em lote"), `src/routes/quoting.tsx`
(fim da cotação → `APROVACAO_PENDENTE`), `src/routes/purchasing.tsx` (finalização da
compra → `REQUISITANTE_COMPRADO`).

---

## 7. Esquema de banco

### Coluna de número de WhatsApp por usuário

```sql
alter table public.profiles
  add column if not exists whatsapp_number text;
-- Formato: DDI+DDD+número, só dígitos (ex.: 5511999999999) — mesmo formato aceito
-- pela Evolution API.
```

### Log persistente de tentativas de envio (auditoria/observabilidade)

Sem isso, a única forma de diagnosticar "por que não chegou a mensagem" é acessar o
log do processo Node no servidor — inviável remotamente. **Crie este log desde o
início**, não deixe pra depois:

```sql
create table if not exists public.whatsapp_notification_log (
  id                uuid primary key default gen_random_uuid(),
  stage             text not null,
  requisition_id    uuid references public.requisitions(id) on delete set null, -- adapte à tabela do seu fluxo
  ticket_number     text,
  recipient_number  text,
  status            text not null check (status in ('sent', 'error', 'skipped_no_apikey', 'skipped_no_number')),
  http_status       int,
  error_detail      text,
  created_at        timestamptz not null default now()
);

create index if not exists whatsapp_notification_log_requisition_id_idx
  on public.whatsapp_notification_log (requisition_id);
create index if not exists whatsapp_notification_log_created_at_idx
  on public.whatsapp_notification_log (created_at desc);

alter table public.whatsapp_notification_log enable row level security;

-- Gravação sempre via service role (bypassa RLS) — a policy abaixo só cobre leitura
-- para quem for investigar.
create policy whatsapp_notification_log_select_admin
on public.whatsapp_notification_log
for select
to authenticated
using (private.has_any_role(array['admin']::public.app_role[]));

grant select on public.whatsapp_notification_log to authenticated;
```

---

## 8. Passo a passo para replicar em outra solução

1. **Mapeie as etapas do seu fluxo** (equivalente ao V1→V5 do VPRequisições) e, para
   cada mudança de etapa, decida: quem precisa agir a seguir? o solicitante/dono
   original também deve ser avisado?
2. **Confirme com o Gelson** (ou, se a dúvida for técnica sobre este padrão em si,
   via protocolo da Seção 1) as regras de negócio — não assuma. Ex.: quem tem alçada
   de valor, se existe conceito de "tier"/alçada no seu fluxo, etc.
3. Peça/obtenha as variáveis de ambiente (Seção 4) para o seu projeto — normalmente
   um novo "slug" no cofre central de credenciais, ou reaproveitando a mesma
   instância Evolution API compartilhada (não precisa ser uma instância nova).
4. Crie a tabela de log (Seção 7) **antes** de ligar os envios de verdade — sem ela
   você não terá visibilidade de nada.
5. Crie `src/features/whatsapp/{client,server}.ts` seguindo o padrão da Seção 5,
   com o enum de estágios específico do seu projeto.
6. Conecte (`void notifyWhatsappClient(...).catch(console.warn)`) em cada ponto de
   mudança de etapa do seu fluxo.
7. Valide com type-check (`tsc --noEmit` ou equivalente) antes de subir.
8. Faça um teste end-to-end real (uma requisição/registro de teste passando por
   cada etapa) e **confira o log** (`whatsapp_notification_log`) — não confie só em
   "não deu erro na tela", porque o envio é silencioso por design.

---

## 9. Armadilhas conhecidas (encontradas em produção no VPRequisições)

- **`EVOLUTION_APIKEY` ausente falha em silêncio.** Sem toast, sem erro visível.
  Só o log de auditoria (Seção 7) mostra `skipped_no_apikey`. Confirme a variável
  logo após o deploy.
- **Aprovador com tier nulo nunca recebe nada** se o seu fluxo filtra por
  alçada/tier — a query de destinatários é um filtro exato (`approval_tier=eq.N`),
  então qualquer registro com tier nulo cai fora silenciosamente. Audite os
  registros de papel/alçada antes de assumir que "está tudo coberto".
- **`BASE_URL` errado polui os links dentro da mensagem.** Se a variável de URL
  pública do app não estiver configurada, o fallback hardcoded pode ser um domínio
  antigo/temporário — os links dentro da mensagem apontam pro lugar errado mesmo com
  o envio funcionando.
- **Cobertura incompleta de números de WhatsApp cadastrados** é o gap mais comum:
  configurar tudo corretamente não adianta se boa parte dos usuários não tem
  `whatsapp_number` preenchido. Rode uma auditoria de cobertura antes de considerar
  o sistema "pronto".
- **Teste end-to-end real é obrigatório** — o comportamento correto (código válido,
  sem erro de compilação) não garante que uma mensagem de verdade saiu; só o log de
  tentativas confirma isso.

---

## 10. Segurança — regras para este repositório

- Este repositório (`008_BorderoDiario`) é **público**. Nenhum valor real de
  credencial (API key, token, senha, connection string) deve ser commitado aqui —
  nem neste documento, nem em código de exemplo, nem em uma Issue.
- Se precisar documentar um valor real para uso interno, ele vai no cofre central de
  credenciais (Supabase Vault) — nunca em texto puro num repositório Git, público ou
  privado.
- Ao abrir uma Issue de dúvida (Seção 1), revise antes de enviar: nenhum
  número de telefone real de cliente, nenhuma chave, nenhum dado pessoal sensível.
- **Este documento, de propósito, não contém nome, celular ou função de nenhum
  colaborador.** Ele descreve o padrão por **papel** (`comprador`, `aprovador`,
  `solicitante`) e por coluna de banco (`profiles.whatsapp_number`), nunca por
  pessoa — porque cada projeto que replicar isso vai ter seu próprio quadro de
  colaboradores. Dados reais de pessoas (nome/cargo/celular) não devem ser
  adicionados aqui em nenhuma atualização futura; eles vivem no banco de cada
  projeto e na documentação interna de RH, não neste repositório público.

---

## 11. Referências

- Código-fonte real (fonte da verdade, sempre prefira ler o código atual a este
  documento se houver divergência): `verticalpartsIA/003_requisicoes` —
  `src/features/whatsapp/{client,server}.ts`, `database/026_profiles_whatsapp_number.sql`,
  `database/028_whatsapp_notification_log.sql`, e os pontos de disparo em
  `src/routes/{approval,quoting,purchasing,trips,products,services,maintenance,
  freight,rental}.tsx`.
- Protocolo de comunicação entre sessões Claude: Seção 1 deste documento.
- Cofre central de credenciais: `verticalpartsIA/001_vpsistema` →
  `Instruções/COFRE_CREDENCIAIS.md`.
