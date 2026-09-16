# Deploy planejado — WhatsApp MCP

## Destino

- VPS VerticalParts / Hostinger
- serviço dedicado do MCP
- DNS planejado: `whatsapp-mcp.vpsistema.com`
- endpoint MCP: `https://whatsapp-mcp.vpsistema.com/mcp`

## Sequência de homologação

1. Instalar o pacote em diretório isolado na VPS.
2. Configurar `.env` fora do Git.
3. Executar em `stdio` e validar tools localmente.
4. Executar em `streamable-http` somente em `127.0.0.1:8010`.
5. Testar leitura de status e histórico.
6. Testar envio com `WHATSAPP_MCP_ALLOW_WRITES=true` apenas para número controlado.
7. Criar serviço systemd.
8. Criar DNS.
9. Publicar via Nginx/HTTPS.
10. Adicionar autenticação.
11. Conectar no Claude.ai como `VerticalParts WhatsApp`.
12. Confirmar herança no Claude Code.

## Exemplo local

```bash
cd whatsapp-mcp
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
verticalparts-whatsapp-mcp
```

## Exemplo HTTP interno

```env
MCP_TRANSPORT=streamable-http
MCP_HOST=127.0.0.1
MCP_PORT=8010
```

O proxy reverso deve encaminhar apenas o caminho MCP necessário. A porta interna não deve ser publicada diretamente na internet.

## Systemd

A unidade systemd será criada na VPS somente depois de validar a instalação real e os caminhos definitivos. Não há arquivos de produção hardcoded neste repositório nesta fase.

## Critério de pronto da fase 1

A fase 1 está homologada quando Claude consegue, pelo MCP:

- consultar estado da instância;
- verificar um telefone;
- consultar histórico de um contato;
- enviar uma mensagem de teste autorizada;
- gerar log de auditoria;
- continuar operacional após restart da VPS.
