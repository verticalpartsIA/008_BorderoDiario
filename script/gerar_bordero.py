#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Borderô Financeiro diário — VerticalParts (v3)
Estrutura por horizonte de tempo:
  - ONTEM: detalhe impecável (Emitidas + Recebimentos + Pagamentos), com status receb./concil.
  - SEMANA (seg→ontem) / MÊS vigente / ANO vigente: resumo Emitido/Recebido/Pago/Saldo.
Dados reais Omie (ListarMovimentos) + Supabase (omie_nfe_emitidas). Design system VerticalParts.

Uso:
  python3 gerar_bordero.py --dia 03/06/2026
  python3 gerar_bordero.py --dia 03/06/2026 --enviar gelson[,diego]
Sem --dia: usa ontem. Credenciais em ./.env (chmod 600, nunca versionar).
"""
import json, subprocess, os, argparse
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))

def load_env():
    env = {}
    with open(os.path.join(BASE, ".env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1); env[k] = v
    return env

ENV = load_env()
OMIE = f'"app_key":"{ENV["OMIE_APP_KEY"]}","app_secret":"{ENV["OMIE_APP_SECRET"]}"'
PAT = ENV["SUPABASE_PAT"]; REF = ENV["SUPABASE_REF"]

def brl(v):
    return ('R$ {:,.2f}'.format(float(v or 0))).replace(',', 'X').replace('.', ',').replace('X', '.')

def pdate(s):
    try: return datetime.strptime(s, '%d/%m/%Y').date()
    except Exception: return None

def omie(url, body):
    r = subprocess.run(['curl', '-s', '-X', 'POST', url, '-H', 'Content-Type: application/json', '-d', body],
                       capture_output=True, text=True)
    return json.loads(r.stdout)

def sb(q):
    r = subprocess.run(['curl', '-s', '-X', 'POST', f'https://api.supabase.com/v1/projects/{REF}/database/query',
                        '-H', f'Authorization: Bearer {PAT}', '-H', 'Content-Type: application/json',
                        '--data-binary', json.dumps({'query': q})], capture_output=True, text=True)
    return json.loads(r.stdout)

def mf(nat, extra, cap=80):
    """Lista movimentos (dedup por título+baixa). Retorna lista de dicts normalizados."""
    seen = set(); out = []; pg = 1; tp = 1
    while pg <= tp and pg <= cap:
        body = '{"call":"ListarMovimentos",%s,"param":[{"nPagina":%d,"nRegPorPagina":200,"cNatureza":"%s",%s}]}' % (OMIE, pg, nat, extra)
        d = omie('https://app.omie.com.br/api/v1/financas/mf/', body)
        if 'faultstring' in d: break
        tp = d.get('nTotPaginas', 1)
        for m in d.get('movimentos', []):
            det = m['detalhes']; res = m['resumo']
            k = (det.get('nCodTitulo'), det.get('nCodBaixa'))
            if k in seen: continue
            seen.add(k)
            out.append({
                'tit': det.get('nCodTitulo'), 'baixa': det.get('nCodBaixa'),
                'nf': det.get('cNumDocFiscal') or det.get('cNumTitulo'),
                'cod': det.get('nCodCliente'), 'categ': det.get('cCodCateg'),
                'tipo': det.get('cTipo'), 'pago': res.get('nValPago') or 0,
                'aberto': res.get('nValAberto') or 0, 'liq': res.get('cLiquidado'),
                'dtpag': pdate(det.get('dDtPagamento')), 'dtemis': pdate(det.get('dDtEmissao')),
                'conc': bool(det.get('dDtConcilia')), 'cc': det.get('nCodCC'),
            })
        pg += 1
    return out

def consolidar(movs):
    """A API lista cada título 2x (linha do título + linha da baixa), ambas c/ valor cheio.
    Consolida por nCodTitulo: valor = soma das BAIXAS efetivas (preserva parcelas reais);
    se não houver baixa, usa o valor do título. Evita contar em dobro."""
    from collections import defaultdict
    grp = defaultdict(list)
    for m in movs:
        grp[m['tit']].append(m)
    out = []
    for tit, regs in grp.items():
        baixas = [r for r in regs if r['baixa'] is not None]
        if baixas:
            pago = sum(r['pago'] for r in baixas); conc = any(r['conc'] for r in baixas)
        else:
            pago = max((r['pago'] for r in regs), default=0); conc = any(r['conc'] for r in regs)
        base = dict(regs[0])
        base['pago'] = pago; base['conc'] = conc
        base['dtpag'] = next((r['dtpag'] for r in regs if r['dtpag']), regs[0]['dtpag'])
        base['liq'] = 'S' if any(r['liq'] == 'S' for r in regs) else None
        out.append(base)
    return out

def contas_isolar():
    """Conjunto de nCodCC a EXCLUIR do caixa real: Bepay e Devoluções de Clientes (por nome)."""
    body = '{"call":"ListarContasCorrentes",%s,"param":[{"pagina":1,"registros_por_pagina":200}]}' % OMIE
    d = omie('https://app.omie.com.br/api/v1/geral/contacorrente/', body)
    contas = d.get('ListarContasCorrentes') or []
    s = set()
    for c in contas:
        u = (c.get('descricao') or '').upper()
        if 'BEPAY' in u or 'DEVOLU' in u:
            s.add(c.get('nCodCC'))
    return s

def dia_util_anterior(hoje):
    d = hoje - timedelta(days=1)
    while d.weekday() >= 5:   # 5=sábado, 6=domingo
        d -= timedelta(days=1)
    return d

def num(x):
    """Normaliza nº de doc/nota p/ casar (só dígitos da parte inteira)."""
    if x is None: return None
    s = ''.join(ch for ch in str(x).split('.')[0] if ch.isdigit())
    return int(s) if s else None

def tot(movs):
    """Totais (valor pago, qtd, conciliados) de uma lista já filtrada por período via API."""
    t = 0.0; n = 0; conc = 0
    for m in movs:
        if m['pago'] > 0:
            t += m['pago']; n += 1
            if m['conc']: conc += 1
    return {'tot': t, 'n': n, 'conc': conc}

def periodo(nat, ini, fim, excl=frozenset()):
    """Movimentos de natureza nat pagos no período [ini,fim], via filtro de API (consistente).
    Exclui liquidações em contas Bepay/Devoluções (excl) — não são caixa real."""
    movs = mf(nat, f'"dDtPagtoDe":"{ini.strftime("%d/%m/%Y")}","dDtPagtoAte":"{fim.strftime("%d/%m/%Y")}"')
    movs = [m for m in movs if m['cc'] not in excl]   # isola Bepay/Devoluções
    return consolidar(movs)                            # consolida duplicata título+baixa

def coletar(dia):
    """dia = date de referência (ontem)."""
    seg = dia - timedelta(days=dia.weekday())          # segunda da semana corrente
    mes_ini = dia.replace(day=1)
    ano_ini = dia.replace(month=1, day=1)
    iso = lambda d: d.strftime('%Y-%m-%d'); br = lambda d: d.strftime('%d/%m/%Y')
    data = {'dia': iso(dia), 'dia_br': br(dia), 'seg': iso(seg), 'mes_ini': iso(mes_ini), 'ano_ini': iso(ano_ini)}

    # --- Emitidas: lista de ONTEM + totais por janela (Supabase) ---
    em = sb(f"select numero_nf, serie, coalesce(nome_destinatario,'(sem nome)') nome, valor_total_nf, status_nfe "
            f"from omie_nfe_emitidas where data_emissao='{iso(dia)}' order by valor_total_nf desc;")
    data['emitidas'] = em if isinstance(em, list) else []
    q = sb(f"""select
      coalesce(sum(valor_total_nf) filter (where status_nfe<>'cancelada' and data_emissao between '{iso(seg)}' and '{iso(dia)}'),0) sem_v,
      count(*) filter (where status_nfe<>'cancelada' and data_emissao between '{iso(seg)}' and '{iso(dia)}') sem_n,
      coalesce(sum(valor_total_nf) filter (where status_nfe<>'cancelada' and data_emissao between '{iso(mes_ini)}' and '{iso(dia)}'),0) mes_v,
      count(*) filter (where status_nfe<>'cancelada' and data_emissao between '{iso(mes_ini)}' and '{iso(dia)}') mes_n,
      coalesce(sum(valor_total_nf) filter (where status_nfe<>'cancelada' and data_emissao between '{iso(ano_ini)}' and '{iso(dia)}'),0) ano_v,
      count(*) filter (where status_nfe<>'cancelada' and data_emissao between '{iso(ano_ini)}' and '{iso(dia)}') ano_n
      from omie_nfe_emitidas;""")
    data['emit'] = q[0] if isinstance(q, list) else {}

    # --- isolar Bepay + Devoluções de Clientes (regra de ouro: não são caixa real) ---
    excl = contas_isolar()
    print(f'  isolando {len(excl)} contas (Bepay/Devoluções) do caixa real')

    # --- Recebimentos/Pagamentos por janela, via filtro de API (consistente) ---
    print('  recebimentos: ontem / semana / mês / ano...')
    rec_d = periodo('R', dia, dia, excl); rec_w = periodo('R', seg, dia, excl); rec_m = periodo('R', mes_ini, dia, excl); rec_y = periodo('R', ano_ini, dia, excl)
    print('  pagamentos: ontem / semana / mês / ano (ano pode levar ~1min)...')
    pag_d = periodo('P', dia, dia, excl); pag_w = periodo('P', seg, dia, excl); pag_m = periodo('P', mes_ini, dia, excl); pag_y = periodo('P', ano_ini, dia, excl)

    # detalhe de ONTEM
    data['rec_dia'] = sorted([m for m in rec_d if m['pago'] > 0], key=lambda x: -x['pago'])
    pag_dia = sorted([m for m in pag_d if m['pago'] > 0], key=lambda x: -x['pago'])
    data['pag_dia'] = [m for m in pag_dia if m['tipo'] != 'FPGT']
    folha = [m for m in pag_dia if m['tipo'] == 'FPGT']
    data['folha'] = {'v': sum(m['pago'] for m in folha), 'n': len(folha)}

    # resumos por janela
    data['rec_w'] = tot(rec_w);  data['rec_m'] = tot(rec_m);  data['rec_y'] = tot(rec_y)
    data['pag_w'] = tot(pag_w);  data['pag_m'] = tot(pag_m);  data['pag_y'] = tot(pag_y)

    # --- recebido?/conciliado? das notas de ontem: cruzar c/ títulos R emitidos ontem ---
    tit = mf('R', f'"dDtEmisDe":"{br(dia)}","dDtEmisAte":"{br(dia)}"', cap=20)
    idx = {}
    for m in tit:
        k = num(m['nf'])
        if k is not None: idx[k] = m
    for nota in data['emitidas']:
        t = idx.get(num(nota['numero_nf']))
        nota['recebido'] = bool(t and (t['liq'] == 'S' or t['pago'] > 0))
        nota['conc'] = bool(t and t['conc'])
        nota['casou'] = bool(t)
    return data

def render_html(d):
    em = d['emitidas']
    emit_tot = sum(float(r['valor_total_nf']) for r in em if r['status_nfe'] != 'cancelada')
    emit_n = sum(1 for r in em if r['status_nfe'] != 'cancelada')
    rd = d['rec_dia']; pd = d['pag_dia']
    rec_dia_tot = sum(m['pago'] for m in rd); pag_dia_tot = sum(m['pago'] for m in pd)
    rec_dia_conc = sum(1 for m in rd if m['conc']); pag_dia_conc = sum(1 for m in pd if m['conc'])
    e = d['emit']
    try:
        dt = datetime.strptime(d['dia_br'], '%d/%m/%Y')
        dsem = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo'][dt.weekday()]
    except Exception:
        dsem = ''
    sim = lambda b: '<span class=ok>✓</span>' if b else '<span class=no>✕</span>'

    def linhas_emit():
        h = ''
        for r in em:
            canc = ' <span class=canc>CANC</span>' if r['status_nfe'] == 'cancelada' else ''
            h += (f"<tr><td>{r['numero_nf']}</td><td class=c>{r['serie']}</td><td>{(r['nome'] or '')[:38]}{canc}</td>"
                  f"<td class=r>{brl(r['valor_total_nf'])}</td><td class=c>{sim(r.get('recebido'))}</td><td class=c>{sim(r.get('conc'))}</td></tr>")
        return h

    def linhas_rec():
        h = ''
        for m in rd:
            h += (f"<tr><td>{m['nf'] or '-'}</td><td class=c>cód {m['cod']}</td>"
                  f"<td class=r>{brl(m['pago'])}</td><td class=c>{sim(m['conc'])}</td></tr>")
        return h

    def linhas_pag():
        h = ''
        for m in pd:
            h += (f"<tr><td>cód {m['cod']}</td><td class=c>{m['categ'] or '-'}</td>"
                  f"<td class=r>{brl(m['pago'])}</td><td class=c>{sim(m['conc'])}</td></tr>")
        return h

    def linha_resumo(lbl, emv, emn, rec, pag):
        saldo = rec['tot'] - pag['tot']
        cls = 'pos' if saldo >= 0 else 'neg'
        return (f"<tr><td class=jl>{lbl}</td>"
                f"<td class=r>{brl(emv)}<span class=q>{emn}</span></td>"
                f"<td class=r>{brl(rec['tot'])}<span class=q>{rec['n']}</span></td>"
                f"<td class=r>{brl(pag['tot'])}<span class=q>{pag['n']}</span></td>"
                f"<td class='r {cls}'>{brl(saldo)}</td></tr>")

    folha = (f"<span class=sal>💼 Salários (ontem): <b>{brl(d['folha']['v'])}</b> ({d['folha']['n']} lanç., sem nomes)</span>"
             if d['folha']['n'] > 0 else
             "<span class=salm>💼 Salários: nenhum pagamento ontem (próxima folha conforme calendário)</span>")

    return f"""<!DOCTYPE html><html lang=pt-BR><head><meta charset=utf-8><style>
@page{{size:A4;margin:0.8cm 0.9cm}}
*{{font-family:'Inter','Helvetica Neue',Arial,'DejaVu Sans',sans-serif;box-sizing:border-box}}
body{{font-size:8.6pt;color:#1a1a1f;margin:0;line-height:1.3}}
.hdr{{background:#0f0f0f;color:#fff;padding:11px 15px;border-radius:6px;border-left:5px solid #F5C400}}
.hdr h1{{margin:0;font-size:15pt;font-weight:700}} .hdr h1 b{{color:#F5C400}}
.hdr .sub{{font-size:8.5pt;color:#c9c9cf;margin-top:3px}}
.cards{{display:table;width:100%;border-spacing:7px 0;margin:9px 0}}
.card{{display:table-cell;width:33.3%;background:#fff;border:1px solid #e7e7ec;border-top:3px solid #F5C400;border-radius:6px;padding:8px 11px;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
.card.green{{border-top-color:#22c55e}} .card.red{{border-top-color:#ef4444}}
.card .t{{font-size:7.5pt;color:#71717a;text-transform:uppercase;letter-spacing:.4px;font-weight:600}}
.card .v{{font-size:15pt;font-weight:800;color:#0f0f0f;margin:2px 0}}
.card.green .v{{color:#15803d}} .card.red .v{{color:#b91c1c}}
.card .d{{font-size:7.5pt;color:#8a8a93}}
h2{{font-size:9pt;color:#0f0f0f;border-bottom:2px solid #F5C400;padding-bottom:2px;margin:12px 0 4px;font-weight:700}}
table{{width:100%;border-collapse:collapse;font-size:7.9pt;margin-top:3px}}
th{{background:#0f0f0f;color:#fff;text-align:left;padding:3px 6px;font-size:7.2pt;text-transform:uppercase;letter-spacing:.3px}}
td{{border-bottom:1px solid #eee;padding:2.4px 6px}}
td.r{{text-align:right;font-variant-numeric:tabular-nums}} td.c{{text-align:center;color:#71717a}}
tr.tot td{{background:#fffbe6;font-weight:800;border-bottom:0}}
.canc{{color:#b91c1c;font-weight:bold;font-size:6.3pt}}
.ok{{color:#15803d;font-weight:bold}} .no{{color:#b91c1c}}
table.res td.jl{{font-weight:700;color:#0f0f0f}}
table.res .q{{color:#a1a1aa;font-size:6.6pt;margin-left:5px}}
table.res .pos{{color:#15803d;font-weight:800}} table.res .neg{{color:#b91c1c;font-weight:800}}
.cols{{display:table;width:100%;border-spacing:8px 0}} .col{{display:table-cell;width:50%;vertical-align:top}}
.sal{{background:#fffbe6;border-left:3px solid #F5C400;padding:5px 10px;border-radius:4px;display:inline-block}}
.salm{{color:#8a8a93;font-style:italic}} .salwrap{{margin:8px 0}}
.foot{{margin-top:10px;font-size:6.8pt;color:#a1a1aa;text-align:center;border-top:1px solid #ececf0;padding-top:5px}}
</style></head><body>
<div class=hdr><h1>⚡ Borderô Financeiro — <b>VerticalParts</b></h1>
<div class=sub>Referência (ontem): <b>{d['dia_br']} ({dsem})</b> · gerado automaticamente às 06:00 · dados Omie em tempo real</div></div>

<div class=cards>
 <div class=card><div class=t>📤 Emitido (ontem)</div><div class=v>{brl(emit_tot)}</div><div class=d>{emit_n} notas</div></div>
 <div class="card green"><div class=t>💚 Recebido (ontem)</div><div class=v>{brl(rec_dia_tot)}</div><div class=d>{len(rd)} títulos · conc. {rec_dia_conc}/{len(rd)}</div></div>
 <div class="card red"><div class=t>💸 Pago (ontem)</div><div class=v>{brl(pag_dia_tot)}</div><div class=d>{len(pd)} títulos · conc. {pag_dia_conc}/{len(pd)}</div></div>
</div>

<h2>📊 Resumo por período (Emitido · Recebido · Pago · Saldo)</h2>
<table class=res><tr><th>Período</th><th style="text-align:right">Emitido</th><th style="text-align:right">Recebido</th><th style="text-align:right">Pago</th><th style="text-align:right">Saldo</th></tr>
{linha_resumo(f"Semana (desde {datetime.strptime(d['seg'],'%Y-%m-%d').strftime('%d/%m')})", e.get('sem_v',0), e.get('sem_n',0), d['rec_w'], d['pag_w'])}
{linha_resumo("Mês de " + datetime.strptime(d['dia_br'],'%d/%m/%Y').strftime('%m/%Y'), e.get('mes_v',0), e.get('mes_n',0), d['rec_m'], d['pag_m'])}
{linha_resumo("Ano " + d['dia_br'][-4:], e.get('ano_v',0), e.get('ano_n',0), d['rec_y'], d['pag_y'])}
</table>
<div style="font-size:6.8pt;color:#a1a1aa;margin-top:2px">números pequenos = qtd de títulos · saldo = recebido − pago</div>

<div class=salwrap>{folha}</div>

<h2>📤 Notas Emitidas ONTEM — todas ({emit_n} válidas)</h2>
<table><tr><th>NF</th><th>Sér.</th><th>Cliente</th><th style="text-align:right">Valor</th><th>Receb.</th><th>Concil.</th></tr>
{linhas_emit()}
<tr class=tot><td colspan=3>TOTAL EMITIDO</td><td class=r>{brl(emit_tot)}</td><td></td><td></td></tr></table>

<h2>💚 Recebimentos ONTEM — todos ({len(rd)})</h2>
<table><tr><th>Doc</th><th>Cliente (cód)</th><th style="text-align:right">Valor</th><th>Concil.</th></tr>
{linhas_rec()}
<tr class=tot><td colspan=2>TOTAL RECEBIDO ({rec_dia_conc}/{len(rd)} conciliados)</td><td class=r>{brl(rec_dia_tot)}</td><td></td></tr></table>

<h2>💸 Pagamentos ONTEM — todos ({len(pd)})</h2>
<table><tr><th>Fornecedor (cód)</th><th>Categoria</th><th style="text-align:right">Valor</th><th>Concil.</th></tr>
{linhas_pag()}
<tr class=tot><td colspan=2>TOTAL PAGO ({pag_dia_conc}/{len(pd)} conciliados)</td><td class=r>{brl(pag_dia_tot)}</td><td></td></tr></table>

<div class=foot>Hermes · CFO digital · VerticalParts — dados Omie · Bepay e "Devoluções de Clientes" isolados (não são caixa real) · Cc/Concil. = conciliado (✓) · Receb. = título já liquidado<br>
⚠️ Posição de caixa/saldo bancário NÃO incluída: depende de conciliação bancária (em implantação). Nome do cliente só nas emitidas; demais por código Omie (privacidade).</div>
</body></html>"""

def gerar_pdf(html, pdf_path):
    open('/tmp/bordero_render.html', 'w', encoding='utf-8').write(html)
    subprocess.run(['xvfb-run', '-a', 'wkhtmltopdf', '-q', '--encoding', 'utf-8',
                    '--enable-local-file-access', '/tmp/bordero_render.html', pdf_path], check=True)
    try:
        info = subprocess.run(['pdfinfo', pdf_path], capture_output=True, text=True).stdout
        pages = [l for l in info.splitlines() if l.startswith('Pages:')]
        print('PDF:', pdf_path, '|', pages[0] if pages else '?')
    except Exception:
        print('PDF gerado:', pdf_path)

def enviar(pdf_path, chat_id, caption):
    token = ENV['TELEGRAM_BOT_TOKEN']
    r = subprocess.run(['curl', '-s', '-X', 'POST', f'https://api.telegram.org/bot{token}/sendDocument',
                        '-F', f'chat_id={chat_id}',
                        '-F', f'document=@{pdf_path};type=application/pdf;filename={os.path.basename(pdf_path)}',
                        '-F', f'caption={caption}'], capture_output=True, text=True)
    try:
        resp = json.loads(r.stdout); ok = resp.get('ok'); mid = resp.get('result', {}).get('message_id')
        print(f'  → chat {chat_id}: ok={ok} message_id={mid}'); return ok
    except Exception:
        print('  → resposta inesperada:', r.stdout[:200]); return False

def alerta_falha(msg):
    """Em caso de erro no cron, avisa o Gelson no Telegram (não fica falha silenciosa)."""
    try:
        token = ENV['TELEGRAM_BOT_TOKEN']
        subprocess.run(['curl', '-s', '-X', 'POST', f'https://api.telegram.org/bot{token}/sendMessage',
                        '-d', f'chat_id={ENV["CHAT_GELSON"]}',
                        '--data-urlencode', f'text=🚨 Borderô das 06:00 FALHOU: {msg[:600]}'], capture_output=True)
    except Exception:
        pass

def run(dia, destinos):
    print(f'Coletando borderô de {dia.strftime("%d/%m/%Y")} ...')
    d = coletar(dia)
    print(f"  emitidas: {len(d['emitidas'])} | recebidos: {len(d['rec_dia'])} | pagamentos: {len(d['pag_dia'])}")
    html = render_html(d)
    pdf_path = f"/root/Bordero-VerticalParts-{d['dia']}.pdf"
    gerar_pdf(html, pdf_path)
    if destinos:
        cap = f"⚡ Borderô Financeiro — {dia.strftime('%d/%m/%Y')} (dia útil anterior). Dados Omie reais. — Hermes / VerticalParts"
        chats = {'gelson': ENV['CHAT_GELSON'], 'diego': ENV['CHAT_DIEGO']}
        for who in [x.strip().lower() for x in destinos.split(',')]:
            if who in chats: print(f'Enviando a {who}...'); enviar(pdf_path, chats[who], cap)
            else: print(f'  destino desconhecido: {who}')
    else:
        print('(--enviar não informado: PDF gerado, NADA enviado)')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dia', help='DD/MM/AAAA; sem isto usa o dia útil anterior')
    ap.add_argument('--enviar', help='gelson,diego')
    args = ap.parse_args()
    dia = datetime.strptime(args.dia, '%d/%m/%Y').date() if args.dia else dia_util_anterior(datetime.now().date())
    try:
        run(dia, args.enviar)
    except Exception as ex:
        import traceback; traceback.print_exc()
        alerta_falha(f'{type(ex).__name__}: {ex}')
        raise

if __name__ == '__main__':
    main()
