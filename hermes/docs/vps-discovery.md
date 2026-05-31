# VPS Hermes — Descobertas da Sessão

**Data:** 2026-05-31  
**VPS:** srv1510643.hstgr.cloud  
**IP:** 72.61.48.156  
**OS:** Ubuntu 24.04.4 LTS  
**Usuário:** root

---

## Onde o Hermes está instalado

### Hermes roda dentro de um container Docker

O Hermes **não está instalado diretamente** no sistema — ele vive dentro de um container Docker.

Caminho do overlay filesystem:
```
/var/lib/docker/rootfs/overlayfs/
  257544c07c864e6fe44088f6fd0e4ac87c1154f9ba1e66332b0146a137b7f936/opt/hermes/
```

Estrutura interna do container:
```
/opt/hermes/
├── hermes_cli                          ← CLI principal
├── agent/
│   └── transports/
│       └── hermes_tools_mcp_server.py  ← servidor MCP de ferramentas
├── plugins/
│   ├── hermes-achievements
│   └── kanban/systemd/hermes-kanban-dispatcher.service
├── .venv/                              ← ambiente Python 3.13
│   └── bin/
│       ├── hermes
│       ├── hermes-agent
│       └── hermes-acp
└── tests/
```

**Versão:** `hermes_agent-0.14.0`  
**Runtime:** Python 3.13

---

## VP Bot — Telegram Bot (frontend do Hermes)

O bot do Telegram que se comunica com o Hermes está em:

```
/opt/vp-bot/
└── .env    ← arquivo de configuração/credenciais
```

**Este é o arquivo a editar** para corrigir a chave do Supabase.

---

## Serviços rodando na VPS

| Serviço | Status | Observação |
|---------|--------|------------|
| `docker.service` | ✅ running | Hermes roda aqui dentro |
| `nginx.service` | ✅ running | Reverse proxy |
| `tor@default.service` | ✅ running | Rede Tor |
| `warp-svc.service` | ✅ running | Cloudflare Zero Trust |
| `ssh.service` | ✅ running | Acesso remoto |
| `cron.service` | ✅ running | Agendamentos |
| PM2 | ❌ vazio | Nenhum processo Node.js gerenciado |

---

## Problema identificado — Tabelas "vazias" no Hermes

### Causa
O Hermes (ou o vp-bot) está conectando ao Supabase com a **chave `anon`** (pública).

Todas as tabelas do projeto `kgecbycsyrtdhmdziuul` têm **RLS habilitado** com políticas que exigem:
- Role `authenticated` — para leitura geral
- Role `service_role` — para acesso total (bypassa RLS)

A chave `anon` não satisfaz nenhuma dessas condições → Supabase retorna **0 linhas silenciosamente**.

### Fix
Editar `/opt/vp-bot/.env` e substituir a chave `anon` pela `service_role`:

```bash
# Ver o conteúdo atual:
cat /opt/vp-bot/.env

# Editar:
nano /opt/vp-bot/.env
```

Trocar a linha que contém `SUPABASE_KEY` ou `SUPABASE_ANON_KEY` pelo valor da **service_role key**:

> Supabase Dashboard → Project Settings → API → `service_role` secret  
> (começa com `eyJ...` — chave mais longa)

Depois reiniciar o container/bot:
```bash
# Ver containers rodando:
docker ps

# Reiniciar o container do Hermes:
docker restart <nome-do-container>

# OU reiniciar o vp-bot se for um serviço separado:
systemctl restart vp-bot   # se existir como serviço
# ou
cd /opt/vp-bot && pm2 restart all
```

### Verificação após o fix
Pedir ao Hermes no Telegram:
```
quantos pedidos tem na tabela omie_orders?
```
Resposta esperada: **25.509**

---

## Como acessar a VPS

```bash
ssh root@srv1510643.hstgr.cloud
# ou pelo IP:
ssh root@72.61.48.156
```

**Nota:** Chaves SSH locais (`~/.ssh/id_ed25519` e `~/.ssh/id_rsa`) **não funcionam** nessa VPS.  
Usar painel Hostinger → Terminal web, ou senha root.

---

## Comandos úteis na VPS

```bash
# Ver containers Docker rodando
docker ps

# Ver logs do Hermes (container)
docker logs <container-id> --tail 50

# Entrar dentro do container do Hermes
docker exec -it <container-id> bash

# Ver conteúdo do .env do bot
cat /opt/vp-bot/.env

# Ver estrutura do bot
ls -la /opt/vp-bot/
```

---

## Próximos passos

- [ ] Verificar conteúdo de `/opt/vp-bot/.env` (qual chave Supabase está sendo usada)
- [ ] Trocar chave `anon` → `service_role` no `.env`
- [ ] Identificar o container Docker do Hermes com `docker ps`
- [ ] Reiniciar o bot e testar consulta ao Supabase
- [ ] Verificar se há 2 processos zumbi (`=> There are 2 zombie processes`)
