# COLAGEM C — Instalar a skill "relatorios-pdf" no Hermes (PDF + HTML)
# Cole TODO o texto abaixo (a partir de "Hermes, sou o Gelson") na conversa do Telegram/navegador.

Hermes, sou o Gelson. Ordem permanente. Crie/sobrescreva o arquivo
/opt/data/skills/data-science/relatorios-pdf/SKILL.md com EXATAMENTE o conteúdo entre <<<INICIO>>>
e <<<FIM>>> (copie literal, sem resumir). Crie o diretório se não existir. Depois:
(1) garanta as libs: `pip install --quiet reportlab matplotlib jinja2` (HTML é nativo do Python);
(2) rode skill_view relatorios-pdf para validar;
(3) adicione 3 quick commands "/": /grafico, /bordero, /dre (prompts no fim desta ordem);
(4) acrescente à MEMORY.md a linha do item FIXAR-NA-MEMORIA;
(5) gere um DRE de TESTE do mês atual em PDF E em HTML e me ENVIE os dois no Telegram (anexos),
e avise o Diego (7175937401) que agora você emite Gráfico, Borderô e DRE em PDF e HTML.
NUNCA esqueça: você é o Hermes do Telegram — relatórios são ENTREGUES como arquivo no Telegram.

FIXAR-NA-MEMORIA (adicionar, sem apagar o resto):
"Gero relatórios em PDF e HTML (skill relatorios-pdf): GRÁFICOS (matplotlib), BORDERÔ completo
de CP/CR e DRE completo (estrutura em dre_category_map: codigo→codigo_dre/dre_descricao/dre_sinal).
Salvo em /opt/data/reports/ e ENVIO o arquivo no Telegram. Sempre ofereço exportar (PDF ou HTML)."

<<<INICIO>>>
---
name: relatorios-pdf
description: "Geração de relatórios financeiros em PDF e HTML para a VerticalParts: gráficos (matplotlib), Borderô completo de contas a pagar/receber e DRE completo (Demonstração de Resultado). Dados reais do Omie no Supabase. Carregar quando pedirem PDF, HTML, relatório, borderô, DRE, gráfico ou exportação."
version: 1.1.0
author: VerticalParts
license: MIT
metadata:
  tags: [pdf, html, relatorio, bordero, dre, grafico, financeiro, verticalparts]
  category: data-science
---

# Relatórios PDF/HTML — VerticalParts (SPEC SDD)

Você gera 3 tipos de relatório com dados REAIS (service_role) em DOIS formatos à escolha do usuário:
PDF (impressão/anexo) e HTML (abrir no navegador). ENTREGA o arquivo no Telegram.
Pasta de saída: /opt/data/reports/ (crie se não existir). Nome: tipo_AAAA-MM-DD_HHMM.(pdf|html).
Stack: Python — reportlab (PDF), Jinja2/string template (HTML), matplotlib (gráficos; no HTML
embuta a imagem em base64 <img src="data:image/png;base64,...">).
Identidade visual VerticalParts: primária amarelo #F5C400, texto #1A1A1A, fundo #F4F5F7. Cabeçalho
com "VERTICALPARTS" + título + período + data de emissão; rodapé com página e "Gerado por Hermes — uso interno".

## REGRAS GERAIS (SDD — inquebráveis)
- Pergunte/declare: formato (PDF ou HTML — se não disser, gere os DOIS) e período (mês/ano ou intervalo; default mês atual).
- VALIDE os totais (count=exact/somatório) antes de imprimir. Número errado em relatório é inaceitável.
- Dinheiro em R$ 1.234.567,89 (pt-BR). Datas dd/mm/aaaa. Em aberto = status NOT IN (RECEBIDO/PAGO, CANCELADO).
- Nome do cliente/fornecedor via JOIN PN_Omie (codigo_cliente_omie → nome_fantasia/razao_social). Nunca "Cliente 12345".
- Ao terminar: salve, ENVIE no Telegram como anexo, e dê resumo executivo + "💡 Sugiro também:".

---

## RELATÓRIO 1 — GRÁFICO (PDF/HTML)
1 página com 1+ gráficos. Temas e fontes:
- Evolução de receita: omie_nfe_itens tipo='S' por mês (SUM valor_total).
- Fluxo de caixa 12m: CR (em aberto) vs CP (em aberto) por mês de data_vencimento.
- Aging CR: faixas 0-7/8-15/16-30/31-60/60+ dias dos ATRASADO.
- Top 10 clientes: CR agrupado por cliente (JOIN PN_Omie).
- Mix por categoria/família: Produtos_VP ou nfe.
Procedimento: consulte → matplotlib (barras/linha/pizza, eixos em R$, título claro) → embuta no PDF
(reportlab) e/ou no HTML (img base64) com cabeçalho/rodapé padrão → envie.

## RELATÓRIO 2 — BORDERÔ COMPLETO (PDF/HTML)
Relação detalhada de títulos para conferência/pagamento ou cobrança, com totais.
Parâmetros: tipo (pagar=CP_Omie / receber=CR_Omie), período (data_vencimento de..até), status (default em aberto).
Colunas: Vencimento | Documento (numero_documento_fiscal) | Favorecido/Cliente | Categoria | Parcela | Status | Valor.
Agrupar por data de vencimento; subtotal por dia; TOTAL GERAL + contagem. ATRASADO em vermelho.
Resumo no topo: total no período, nº de títulos, maior favorecido.
Query base (adapte tabela/datas):
  SELECT cp.data_vencimento, cp.numero_documento_fiscal, cp.numero_parcela, cp.valor_documento,
         cp.status_titulo, COALESCE(pn.nome_fantasia, pn.razao_social) AS favorecido,
         c.descricao AS categoria
  FROM "CP_Omie" cp
  LEFT JOIN "PN_Omie" pn ON pn.codigo_cliente_omie = cp.codigo_cliente_omie
  LEFT JOIN omie_categorias c ON c.codigo = cp.codigo_categoria
  WHERE cp.data_vencimento BETWEEN :ini AND :fim
    AND cp.status_titulo NOT IN ('PAGO','CANCELADO')
  ORDER BY cp.data_vencimento, cp.valor_documento DESC;
(Para "a receber": CP_Omie→CR_Omie e 'PAGO'→'RECEBIDO'. Acima de 1000 linhas, pagine com header Range.)

## RELATÓRIO 3 — DRE COMPLETO (PDF/HTML)
A ESTRUTURA do DRE está na tabela dre_category_map. Campos:
  codigo (= categoria do lançamento, casa com CP_Omie/CR_Omie.codigo_categoria),
  codigo_dre (linha do DRE), dre_descricao (nome da linha), dre_sinal ('+'/'-'), dre_nivel.
Cada categoria do Omie é mapeada para uma linha do DRE. Linhas REAIS (codigo_dre → descrição, sinal):
  RECEITAS / DEDUÇÕES
   1.01.01 (+) Receita Bruta de Vendas      (17 categorias 1.01.xx — vendas de peças, serviços, locação)
   1.01.02 (-) Impostos                      (2.06.xx — impostos sobre vendas)
   1.01.03 (-) Deduções de Receita           (devoluções/abatimentos)
  CUSTOS (CPV/CSP)
   1.21.02 (-) Custo dos Serviços Prestados
   1.21.03 (-) Outros Custos                 (21 categorias — inclui custo de mercadoria/importação)
  DESPESAS OPERACIONAIS (fixas e variáveis)
   2.01.01 (-) Despesas Variáveis            2.01.02 (+) Recuperação de Desp. Variáveis
   2.11.01 (-) Despesas com Pessoal          (70 categorias — SALÁRIOS, encargos, pró-labore, etc.)
   2.11.02 (-) Despesas Administrativas      (53 categorias)
   2.11.04 (-) Despesas de Vendas e Marketing
   2.11.05 (-) Outros Tributos               2.11.10 (+) Recuperação de Desp. Fixas
  RESULTADO FINANCEIRO
   1.11.02 (+) Receitas Financeiras          2.11.03 (-) Despesas Financeiras
  OUTRAS
   1.11.01 (+) Outras Receitas               1.11.03 (-) Outras Deduções de Receita
  (Ignore 3.01.xx Ativos/Serviços — são movimentações de balanço, NÃO entram no DRE de resultado.)

Subtotais a CALCULAR (não vêm prontos — você soma):
  (=) RECEITA LÍQUIDA  = Receita Bruta − Impostos − Deduções
  (−) CPV/Custos       = Custo Serviços + Outros Custos
  (=) LUCRO BRUTO      = Receita Líquida − Custos             → Margem Bruta %
  (−) Despesas Operac. = Pessoal + Administrativas + Vendas/Mkt + Variáveis + Outros Tributos − Recuperações
  (=) EBITDA           = Lucro Bruto − Despesas Operacionais  → Margem EBITDA %
  (±) Result. Financeiro = Receitas Financeiras − Despesas Financeiras
  (+) Outras Receitas/Deduções
  (=) RESULTADO LÍQUIDO                                       → Margem Líquida %

Como calcular o REALIZADO (regime COMPETÊNCIA = data_emissao; CAIXA = data_pagamento; default competência, declare qual usou):
  -- DESPESAS/CUSTOS (a pagar)
  SELECT m.codigo_dre, m.dre_descricao, m.dre_sinal, SUM(cp.valor_documento) AS valor
  FROM "CP_Omie" cp JOIN dre_category_map m ON m.codigo = cp.codigo_categoria
  WHERE cp.data_emissao BETWEEN :ini AND :fim AND cp.status_titulo <> 'CANCELADO'
  GROUP BY 1,2,3;
  -- RECEITAS (a receber) — Receita Bruta pode também vir de omie_nfe_itens tipo='S'
  SELECT m.codigo_dre, m.dre_descricao, m.dre_sinal, SUM(cr.valor_documento) AS valor
  FROM "CR_Omie" cr JOIN dre_category_map m ON m.codigo = cr.codigo_categoria
  WHERE cr.data_emissao BETWEEN :ini AND :fim AND cr.status_titulo <> 'CANCELADO'
  GROUP BY 1,2,3;
Una os dois conjuntos, aplique o dre_sinal e monte os subtotais acima na ordem.
Estrutura (sempre reconsulte para não fixar errado):
  SELECT codigo_dre, dre_descricao, dre_sinal, COUNT(*) FROM dre_category_map
  WHERE codigo_dre IS NOT NULL GROUP BY 1,2,3 ORDER BY 1;

Layout PDF/HTML: tabela Conta | Valor | % sobre Receita Líquida (análise vertical). Linhas de
subtotal (Receita Líquida, Lucro Bruto, EBITDA, Resultado Líquido) em NEGRITO e fundo amarelo claro.
Se pedirem, coluna do mês anterior + variação % (análise horizontal). 2ª página: pizza de composição
das despesas operacionais por grupo (Pessoal, Administrativas, Vendas/Mkt, Variáveis).

---

## TEMPLATE HTML (base — reutilize para os 3 relatórios)
Gere um HTML autossuficiente (CSS embutido, gráficos em base64) assim:
  html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
  <title>{titulo} — VerticalParts</title>
  <style>
    body{{font-family:Arial,Helvetica,sans-serif;color:#1A1A1A;background:#F4F5F7;margin:0;padding:24px}}
    .wrap{{max-width:1000px;margin:auto;background:#fff;padding:28px;border-radius:12px;box-shadow:0 1px 6px #0002}}
    header{{border-bottom:4px solid #F5C400;padding-bottom:12px;margin-bottom:18px}}
    h1{{margin:0;font-size:22px}} .sub{{color:#666;font-size:13px}}
    table{{width:100%;border-collapse:collapse;font-size:13px}}
    th,td{{padding:8px 10px;border-bottom:1px solid #eee;text-align:left}}
    td.v,th.v{{text-align:right;font-variant-numeric:tabular-nums}}
    tr.tot{{font-weight:bold;background:#FFF7CC}}
    .neg{{color:#C62828}}
    footer{{margin-top:18px;color:#888;font-size:11px;text-align:center}}
  </style></head><body><div class="wrap">
    <header><h1>{titulo}</h1><div class="sub">Período: {periodo} · Emitido em {hoje}</div></header>
    {conteudo}
    <footer>Gerado por Hermes — uso interno · VerticalParts</footer>
  </div></body></html>'''
Salve em /opt/data/reports/ e envie no Telegram. Para PDF, monte equivalente com reportlab.

## CHECKLIST DE QUALIDADE (antes de enviar)
[ ] Período correto e declarado.  [ ] Totais conferidos.  [ ] Nomes reais.  [ ] R$ pt-BR.
[ ] Cabeçalho/rodapé padrão.  [ ] Formato pedido (PDF e/ou HTML).  [ ] Salvo e ENVIADO no Telegram.
[ ] Resumo executivo + "💡 Sugiro também:".

## PROATIVIDADE
Sempre que eu apresentar números relevantes, ofereça gerar o relatório ("Quer em PDF ou HTML?").
Nunca seja preguiçoso; antecipe o formato e o recorte mais úteis ao pedido.
<<<FIM>>>

QUICK COMMANDS para adicionar (config.yaml, seção quick_commands):
- /grafico → "Carregue relatorios-pdf. Pergunte o tema e o formato (PDF/HTML); gere o relatório de gráfico e envie no Telegram."
- /bordero → "Carregue relatorios-pdf. Gere o Borderô. Pergunte: pagar ou receber? período? formato (PDF/HTML)? Default: CP em aberto do mês atual. Subtotais por dia + total geral. Envie no Telegram."
- /dre     → "Carregue relatorios-pdf. Gere o DRE completo do mês atual (ou período pedido) em PDF e HTML, com grupos, subtotais (Rec.Líquida, Lucro Bruto, EBITDA, Resultado), margens e análise vertical; 2ª página com pizza de despesas. Envie no Telegram."
