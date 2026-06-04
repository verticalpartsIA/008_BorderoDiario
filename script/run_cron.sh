#!/bin/bash
# Borderô diário — executado pelo cron às 09:00 UTC (06:00 BRT), seg a sex.
# Determinístico: NÃO depende de Claude nem do Hermes. Alerta de falha embutido no .py.
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
cd /root/bordero || exit 1
LOG=/root/bordero/cron.log
echo "===== $(date -u +'%Y-%m-%d %H:%M:%S UTC') iniciando borderô =====" >> "$LOG"
/usr/bin/python3 /root/bordero/gerar_bordero.py --enviar gelson,diego >> "$LOG" 2>&1
RC=$?
echo "----- fim (exit $RC) -----" >> "$LOG"
# rede de segurança: se o .py morrer antes do alerta interno, avisa mesmo assim
if [ $RC -ne 0 ]; then
  TG=$(grep -E '^TELEGRAM_BOT_TOKEN=' .env | cut -d= -f2-)
  CH=$(grep -E '^CHAT_GELSON=' .env | cut -d= -f2-)
  curl -s -X POST "https://api.telegram.org/bot${TG}/sendMessage" \
    -d "chat_id=${CH}" --data-urlencode "text=🚨 Borderô das 06:00 falhou (exit $RC). Ver /root/bordero/cron.log" >/dev/null
fi
