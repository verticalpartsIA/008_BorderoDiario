# COLAGEM E — Instalar libs de imagem no container (PNG preview)
# Cole o texto a partir de "Hermes, sou o Gelson" na conversa.

Hermes, sou o Gelson. Ordem: instale no seu container as bibliotecas necessárias para gerar PNG e
PDF, valide cada uma e me confirme. Faça nesta sequência e me reporte o resultado de cada passo:

1) PYTHON (no seu venv):
   pip install --quiet --upgrade matplotlib Pillow reportlab requests
   Depois valide:
   python -c "import matplotlib, PIL, reportlab, requests; print('matplotlib', matplotlib.__version__, '| PIL', PIL.__version__, '| reportlab OK')"

2) POPPLER (para converter PDF->PNG via pdftoppm), caso queira preview a partir do PDF:
   - Tente: apt-get update && apt-get install -y poppler-utils
   - Se não tiver apt (imagem slim) ou não tiver permissão, tudo bem: pode pular — o preview PNG
     será gerado direto pelo matplotlib/PIL (não depende do poppler).
   Valide se instalou: pdftoppm -v

3) TESTE DE FOGO (gera e ENVIA no meu Telegram um PNG simples):
   import matplotlib; matplotlib.use("Agg")
   import matplotlib.pyplot as plt, os, requests
   os.makedirs("/opt/data/reports", exist_ok=True)
   fig, ax = plt.subplots(figsize=(6,3)); ax.bar(["A","B","C"],[3,7,5], color="#F5C400")
   ax.set_title("Teste Hermes — PNG OK"); fig.savefig("/opt/data/reports/teste.png", dpi=150, bbox_inches="tight")
   TOKEN=os.getenv("TELEGRAM_BOT_TOKEN")
   with open("/opt/data/reports/teste.png","rb") as f:
       r=requests.post(f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                       data={"chat_id":"2129471333","caption":"✅ Teste de PNG no Telegram"},
                       files={"photo":f}, timeout=120)
   print("status:", r.status_code, r.json().get("ok"))

4) Me confirme: (a) versões instaladas; (b) se o poppler entrou ou foi pulado; (c) se a FOTO de
   teste chegou no meu Telegram (deve aparecer um gráfico de barras amarelo). Se a foto chegou,
   regenere o DRE de Abril/2026 e envie como PNG (preview) + PDF (anexo) seguindo a regra de entrega.

OBS IMPORTANTE: tudo que instalar deve ir no /opt/data (HERMES_HOME) ou no venv persistente, para
não se perder em reinício. Se o pip instalar fora do persistente e sumir após restart, me avise que
ajustamos para instalar em /opt/data com PYTHONUSERBASE.
