# COLAGEM D — Correção: ENVIAR os relatórios no Telegram (visualização real)
# Cole o texto a partir de "Hermes, sou o Gelson" na conversa.

Hermes, sou o Gelson. Problema: você está SALVANDO os relatórios em /tmp dentro do container e só
me passando o caminho do arquivo. Eu NÃO consigo abrir isso — /tmp fica dentro do Docker, fora do
meu computador. E SVG não pré-visualiza no Telegram. Corrija de forma PERMANENTE:

REGRA DEFINITIVA DE ENTREGA (grave na MEMORY.md e na skill relatorios-pdf):
1. NUNCA entregue um relatório apenas como caminho de arquivo. SEMPRE envie o ARQUIVO em si para o
   meu chat no Telegram, como anexo. Citar /tmp/... ou /opt/... NÃO conta como entrega.
2. Para visualização IMEDIATA: gere também um PNG e envie como FOTO (sendPhoto) — aparece direto no
   chat, sem precisar baixar. NUNCA use SVG (Telegram não mostra).
3. Para o documento completo: gere PDF e/ou HTML e envie como DOCUMENTO (sendDocument).
4. Ordem de entrega de todo relatório: (a) 1 PNG de preview no chat; (b) o PDF anexo; (c) se eu pedir,
   o HTML anexo. Sempre seguido de um resumo executivo + "💡 Sugiro também:".

COMO ENVIAR (use o bot token que já está no seu ambiente — variável TELEGRAM_BOT_TOKEN):
```python
import os, requests
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = "2129471333"  # Gelson (use o chat_id de quem pediu)
def tg_photo(path, caption=""):
    with open(path, "rb") as f:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                      data={"chat_id": CHAT_ID, "caption": caption[:1024]},
                      files={"photo": f}, timeout=120)
def tg_doc(path, caption=""):
    with open(path, "rb") as f:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendDocument",
                      data={"chat_id": CHAT_ID, "caption": caption[:1024]},
                      files={"document": f}, timeout=120)
# Ex.: tg_photo("/opt/data/reports/dre.png","DRE Abril/2026"); tg_doc("/opt/data/reports/dre.pdf")
```
Se você já tem uma ferramenta nativa de enviar arquivo no Telegram, pode usá-la — o importante é o
arquivo CHEGAR no meu chat.

GERAÇÃO DE IMAGEM (PNG, não SVG):
- matplotlib: salve com fig.savefig("/opt/data/reports/nome.png", dpi=150, bbox_inches="tight").
- Para o DRE/Borderô (que são tabelas), gere uma IMAGEM da tabela renderizada (matplotlib table ou
  desenhe via PIL), OU converta o PDF para PNG da 1ª página (pdftoppm -png arquivo.pdf saida) e envie
  esse PNG como preview. O essencial: eu PRECISO ver a tabela como imagem no chat.

AGORA, FAÇA O TESTE REAL:
- Regenere o DRE de Abril/2026 e me ENVIE no Telegram nesta ordem: (1) PNG do DRE (preview visível no
  chat), (2) PDF anexo, (3) HTML anexo. Depois confirme aqui "enviado" e me diga o tamanho de cada arquivo.
