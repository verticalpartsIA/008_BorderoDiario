# COLAGEM B — Comandos "/" (quick_commands) + Proatividade + Folha de pagamento
# Cole TODO o texto (a partir de "Hermes, sou o Gelson") na conversa.

Hermes, sou o Gelson. Ordem permanente. Faça as 4 coisas abaixo e, ao final, me avise no Telegram
(e ao Diego 7175937401) confirmando o que foi configurado.

1) CRIE COMANDOS RÁPIDOS "/" (quick_commands) no seu config, só para uso meu e do Diego, com estes
atalhos do "novo mundo financeiro" (quando eu digitar "/" devem aparecer). Para cada um, o prompt já
deve carregar as skills verticalparts-cfo e financas-avancadas e responder com dados reais + sugestões:

- /saude        → "Diagnóstico completo de saúde financeira: liquidez corrente/seca, ciclo financeiro, NCG, saldo de tesouraria e efeito tesoura. Aponte riscos e ações."
- /caixa        → "Projeção de caixa D+30/D+60/D+90 com entradas (CR) e saídas (CP) reais. Alerta se saldo negativo."
- /rentabilidade→ "Calcule margem bruta, de contribuição, operacional, líquida, EBITDA e estime ROI/ROIC/ROE/ROA com premissas explícitas. Diga se cria ou destrói valor (ROIC vs WACC)."
- /ciclo        → "PMR, PMP, PME, ciclo operacional e financeiro. Quanto de capital de giro está preso. Ação para encurtar o ciclo."
- /inadimplencia→ "CR ATRASADO total + top 10 clientes por nome (JOIN PN_Omie) + % sobre o CR. Régua de cobrança sugerida."
- /folha        → "Folha do mês: some categorias 2.03.78 (Operacional) e 2.03.87 (Administrativo); some também 2.03.91 Pró-Labore e encargos 2.03.7x. Liste favorecidos e o 5º dia útil considerando feriados."
- /dre          → "DRE gerencial do mês e dos últimos 12 meses (receita NF saída, custos por categoria, EBITDA, margens). Análise vertical e horizontal."
- /valuation    → "Esboce valuation: EBITDA 12m, múltiplo EV/EBITDA de referência (distribuição B2B), e o que melhoraria o valor."
- /compras      → "Itens em ruptura com demanda (Produtos_VP) + último custo (nfe tipo='E') + fornecedor + alerta de câmbio para importados. Priorize por curva ABC."
- /risco        → "Mapa de risco: concentração de clientes (HHI), inadimplência, Dívida/EBITDA, efeito tesoura. Classifique CRÍTICO/ALTO/MÉDIO/BAIXO."

2) REGRA DE PROATIVIDADE (grave permanente e siga SEMPRE): é PROIBIDO entregar só o que foi pedido.
Toda resposta termina com "💡 Sugiro também:" propondo de 1 a 3 próximos passos/indicadores no
contexto do meu pedido, que eu possa reaproveitar. Você nunca é preguiçoso e nunca espera eu pedir
o óbvio — antecipe. Ex: se eu perguntar um saldo, ofereça a tendência; se eu pedir um cliente, ofereça
o risco dele.

3) GRAVE O CONHECIMENTO DA FOLHA DE PAGAMENTO (na skill verticalparts-cfo, seção própria, ou em
/opt/data/docs/folha-verticalparts.md):
- Categorias de SALÁRIO reais no Omie: 2.03.78 = Salários Operacional; 2.03.87 = Salários Administrativo.
  Complementos: 2.03.91 Pró-Labore; 2.03.69 Pensão Alimentícia; encargos 2.03.71 FGTS Op, 2.03.72 FGTS Adm,
  2.03.73 INSS Op, 2.03.74 INSS Adm, 2.03.08/59/60 IRRF; benefícios 2.03.68 Assistência Médica.
  (NÃO use 2.01.01 como "salários" — é outra coisa.)
- A folha vence no 5º dia útil do mês. Calcule o 5º dia útil considerando fins de semana E feriados
  nacionais (ex.: junho/2026 tem Corpus Christi em 04/06, então o 5º dia útil cai em 08/06/2026).
- Para valor da folha de um mês: SUM(valor_documento) das categorias 2.03.78 + 2.03.87 com
  data_vencimento no mês; liste favorecidos (são os funcionários). Cruze nomes com os colaboradores
  conhecidos quando útil. Junho/2026: Salários ≈ R$ 158.443,58 (63 títulos: Adm R$91.197 + Op R$67.246,58).
- Colaboradores-chave (vpsistema): Diego Maeno (CEO), Gelson Simões (Consultor Estratégico),
  Bianca Maeno (Jurídico/Compras), Milene Gusmão (Financeiro), Marcus Braz (Comercial),
  Rafael Nunes (Comercial), Guilherme Garcia (Ger. Comercial), Alexandre Schmidt (Engenharia),
  Vinicius Leite (Projetos), Mauricio Araujo (Operacional), Danilo Oliveira (Logística),
  Juliana Anderson (Administrativo), Giovanna Maeno (Marketing).

4) Ao terminar tudo, ENVIE no Telegram para Gelson (2129471333) E Diego (7175937401) uma mensagem:
"📚 Aprendi finanças avançadas (ROI, ROE, ROA, ROIC, EVA, liquidez, alavancagem, ciclo, NCG/tesouraria,
valuation VPL/TIR/WACC), criei 10 comandos rápidos com '/', passei a ser proativo (sempre sugiro algo a
mais) e gravei a regra da folha (5º dia útil + categorias 2.03.78/2.03.87). Podem me testar!"
