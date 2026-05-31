Hermes, sou o Gelson. Ordem direta — leia com atenção e GRAVE NA SUA MEMÓRIA PERMANENTE, substituindo qualquer informação antiga que contradiga o que está aqui. Tudo abaixo é a verdade definitiva sobre o banco da VerticalParts.

1) CHAVE DE ACESSO
- Use SEMPRE a variável de ambiente $SUPABASE_SERVICE_KEY (é a chave service_role). Ela está no seu ambiente e FUNCIONA.
- NUNCA use chave anon. Apague da sua memória qualquer "anon key". Se você encontrar uma anon key salva em qualquer lugar, ignore e não a use.
- URL: $SUPABASE_URL (https://kgecbycsyrtdhmdziuul.supabase.co). Headers em toda chamada: apikey e Authorization Bearer com a $SUPABASE_SERVICE_KEY.

2) OS DADOS EXISTEM — PROIBIDO dizer o contrário
- O banco está cheio e acessível. É PROIBIDO responder "vazio", "0 por sincronização", "ETL falhou", "n8n", "quebrado" ou pedir para eu consultar o Supabase por você. Você consegue consultar sozinho.
- Se uma consulta vier vazia, o erro é SEU (chave anon, status errado ou filtro errado). Corrija e refaça antes de responder.

3) CONTAGENS REAIS (decore)
- omie_orders = 25.509 pedidos | CR_Omie = 12.490 (a receber) | CP_Omie = 26.091 (a pagar)
- omie_order_items = 61.385 | omie_nfe_itens = 45.609 | PN_Omie = 13.827 | Produtos_VP = 4.140 | sellers = 99
- Esqueça os números antigos 31.808 / 30.300 / 62.819 — eram ERRADOS.

4) COMO CONTAR CERTO
- Faça HEAD com header "Prefer: count=exact" e leia o número depois da barra no header Content-Range (ex: 0-0/25509 → total 25509).
- NUNCA conte por faixa de ID (MAX id) — isso superestima.

5) HORIZONTE E O FUTURO
- Dados de 01/01/2024 em diante. Há vencimentos FUTUROS porque a empresa COMPRA parcelado (até ~10 meses) e VENDE parcelado.
- "Quanto pago em janeiro de 2027" é respondível: filtre CP_Omie por data_vencimento entre 2027-01-01 e 2027-01-31 (resposta correta: 63 títulos, R$ 484.327,14).
- ATENÇÃO à diferença: "quantos pedidos temos" (TOTAL, sem filtro de data = 25.509) é diferente de "pedidos em janeiro/2027" (filtrar data_inclusao, que dá 0 porque não se lança pedido de venda com meses de antecedência). Quando eu perguntar o total, não filtre por data.

6) SCHEMA E STATUS REAIS
- CR_Omie e CP_Omie: o valor está em valor_documento (não "valor"); o status está em status_titulo (não "status").
- Status CR_Omie: RECEBIDO, A VENCER, ATRASADO, VENCE HOJE, CANCELADO.
- Status CP_Omie: PAGO, A VENCER, ATRASADO, CANCELADO.
- NÃO existe status "A RECEBER"/"aberto"/"pendente". "Em aberto" = status NOT IN (RECEBIDO/PAGO, CANCELADO). Inadimplência = ATRASADO.
- O nome do cliente/fornecedor NÃO está em CR_Omie/CP_Omie. Faça JOIN com PN_Omie por codigo_cliente_omie e use nome_fantasia (ou razao_social). Nunca responda "Cliente 12345".
- Faturamento real = tabela omie_nfe_itens com tipo='S' (saída). Compra/entrada = tipo='E'.

7) CONFIRME QUE ENTENDEU
Depois de gravar isso na memória, me responda apenas com:
- o total de pedidos (deve ser 25.509)
- o total a pagar em janeiro/2027 (deve ser R$ 484.327,14)
- a inadimplência atual (soma de CR_Omie com status ATRASADO), com os 3 maiores clientes pelo nome.
