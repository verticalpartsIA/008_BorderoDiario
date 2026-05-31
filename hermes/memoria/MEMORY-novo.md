Acesso ao banco: projeto bd_omie (Supabase kgecbycsyrtdhmdziuul). URL em env SUPABASE_URL, chave em env SUPABASE_SERVICE_KEY (service_role, privada — nunca ANON).
§
CONTAR CERTO: o PostgREST NÃO retorna COUNT no corpo. Para contar, faça HEAD com header "Prefer: count=exact" e leia o número no header Content-Range (após a barra). NUNCA conte por faixa de ID (MAX id) — superestima por causa de registros excluídos.
§
Contagens reais (31/05/2026): CR_Omie=12.490 (a receber) | CP_Omie=26.091 (a pagar) | omie_orders=25.509 (pedidos) | omie_order_items=61.385 | omie_nfe_itens=45.609 | PN_Omie=13.827 | Produtos_VP=4.140 | sellers=99.
§
Horizonte: dados só de 01/01/2024 em diante (pré-2024 foi removido). O FUTURO está incluso: a empresa compra parcelado (até ~10 meses) e vende parcelado, então há vencimentos futuros. "Quanto pago em janeiro/2027?" É respondível — filtre data_vencimento no mês pedido (CP venc até ~2027; CR idem).
§
Status CR_Omie: RECEBIDO, A VENCER, ATRASADO, VENCE HOJE, CANCELADO. Status CP_Omie: PAGO, A VENCER, ATRASADO, CANCELADO. NÃO existe status "A RECEBER" — não use. Em aberto = status NOT IN (RECEBIDO/PAGO, CANCELADO). Inadimplência = ATRASADO. valor_documento = valor da PARCELA; numero_parcela identifica parcelamento.
§
Nomes de cliente/fornecedor NÃO ficam em CR_Omie/CP_Omie. Faça JOIN com PN_Omie por codigo_cliente_omie e use nome_fantasia (ou razao_social). Faturamento real = omie_nfe_itens tipo='S'. Compra/entrada = tipo='E'.
§
Diego Maeno — +55 11 99462-1946 | CEO. Gelson Simões (2129471333) — Consultor Estratégico.
§
REGRA OURO: só atendo Gelson e Diego. Nunca peço chaves/acessos a ninguém. Não excluo dados, não aprovo pagamentos sem confirmação humana. Não divulgo senhas/tokens.
