# Relatório de Atividades — 18/06/2026

## Contexto

Sessão focada no **Borderô Financeiro** ().
Gelson solicitou que o Borderô passe a exibir **somente NFs que representam receita real de venda** — excluindo notas fiscais de remessa, transferência, comodato, amostras e similares, que movimentam estoque mas não geram caixa.

---

## Investigação — CFOPs na API Omie

### O que foi feito

Consultou-se a API  (ListarCFOP, 676 registros em 14 páginas) para localizar os CFOPs de interesse:

| CFOP | Descrição | Encontrado |
|---|---|---|
| 5.101 | Venda de Produção do Estabelecimento | ✅ |
| 5.102 | Venda de Mercadoria Adquirida/Recebida de Terceiros | ✅ |
| 5.405 | Venda Merc. Adq/Rec. Terceiros, S.T., Contrib. Substituído | ✅ |
| 5.406 | — | ❌ Não cadastrado no Omie da VP |

### Conclusão conceitual

CFOPs série **5.xxx** = saídas dentro do estado (intraestado). CFOPs série **6.xxx** = saídas para outros estados. Ambas representam receita, desde que sejam de **venda real**.

O Borderô precisava excluir:
- Transferências entre filiais (5.151, 5.152, 6.151, 6.152)
- Remessas/retornos de industrialização, conserto, demonstração, comodato
- Encomendas para entrega futura (a receita vem depois, na NF real)
- Amostras grátis e outras remessas sem contraprestação financeira

---

## Alteração — Filtro de CFOP no Borderô

### Arquivo modificado

 — versão v4 (10/06/2026)

### O que mudou

1. **Adicionada constante ** (logo após a função ):



2. **Filtro aplicado na função **: antes de adicionar cada NF à lista, extrai o CFOP do primeiro item () e pula a NF se o CFOP estiver na lista de exclusão.

3. **Campo  adicionado** ao dicionário de cada NF retornado (para referência futura).

### Resultado do teste (últimos 30 dias, 1ª página da API)

- Total de NFs saída (tpNF=1): **100**
- **Excluídas pelo filtro**: 6
  - 3× CFOP 5.949 (amostras grátis)
  - 1× CFOP 5.117 (encomenda entrega futura)
  - 1× CFOP 6.916 (retorno de conserto)
  - 1× outro
- **Incluídas (venda real)**: 94

### CFOPs encontrados nas NFs incluídas

| CFOP | Qtd | Descrição |
|---|---|---|
| 5.101 | 39 | Venda de Produção do Estabelecimento |
| 5.102 | 2 | Venda de Mercadoria Adq./Recebida de Terceiros |
| 6.101 | 33 | Venda de Produção do Estabelecimento (interestadual) |
| 6.102 | 1 | Venda de Mercadoria (interestadual) |
| 6.107 | 15 | Venda de Produção p/ Não Contribuinte (interestadual) |
| 6.108 | 1 | Venda de Mercadoria p/ Não Contribuinte (interestadual) |
| 5.201 | 1 | ⚠️ Devolução de Compra (VP devolve p/ fornecedor) |
| 5.917 | 1 | ⚠️ Remessa por conta e ordem de terceiros |
| 6.201 | 1 | ⚠️ Devolução de Compra (interestadual) |

---

## Pendências

- **5.201 / 6.201** (Devolução de Compra): NF emitida pela VP ao devolver mercadoria ao fornecedor. Não é receita de venda — é saída de estoque sem caixa. Aguardando confirmação do Gelson para incluir na lista de exclusão.
- **5.917** (Remessa por conta e ordem de terceiros): 1 NF encontrada. Precisa investigar se é operação legítima de receita ou não.
- Pendente de sessão anterior: decisão sobre 5.201/6.201 e 5.917 ainda não tomada.

---

## Status

| Item | Status |
|---|---|
| Filtro CFOP no Borderô | ✅ Implementado e testado |
| Relatório salvo em relatorio/ | ✅ Este documento |
| Exclusão 5.201/6.201 | ⏳ Aguardando confirmação |

---

*Hermes · CFO digital · VerticalParts — sessão 18/06/2026*
