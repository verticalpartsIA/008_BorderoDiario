# Relatório de Atividades — 18/06/2026

## Contexto

Sessão focada no **Borderô Financeiro** (`/root/bordero/gerar_bordero.py`).
Gelson solicitou que o Borderô passe a exibir **somente NFs que representam receita real de venda** — excluindo notas fiscais de remessa, transferência, comodato, amostras e similares, que movimentam estoque mas não geram caixa.

---

## Investigação — CFOPs na API Omie

Consultou-se a API `https://app.omie.com.br/api/v1/produtos/cfop/` (ListarCFOP, 676 registros em 14 páginas) para localizar os CFOPs de interesse:

| CFOP | Descrição | Encontrado |
|---|---|---|
| 5.101 | Venda de Produção do Estabelecimento | ✅ |
| 5.102 | Venda de Mercadoria Adquirida/Recebida de Terceiros | ✅ |
| 5.405 | Venda Merc. Adq/Rec. Terceiros, S.T., Contrib. Substituído | ✅ |
| 5.406 | — | ❌ Não cadastrado no Omie da VP |

**Conclusão conceitual:** CFOPs série 5.xxx = saídas intraestado; série 6.xxx = saídas interestaduais. Ambas representam receita quando são de venda real.

O CFOP está no campo `det[0].prod.CFOP` da resposta da API `ListarNF` — nível de item, não de cabeçalho.

---

## Alteração — Filtro de CFOP no Borderô

### Arquivo modificado

`/root/bordero/gerar_bordero.py`

### O que mudou

**1. Adicionada constante `CFOP_EXCLUIR`** (logo após a função `brl()`):

```python
CFOP_EXCLUIR = {
    '5.151', '5.152', '6.151', '6.152',   # transferências entre filiais
    '5.901', '5.902', '6.901', '6.902',   # remessa/retorno industrialização
    '5.915', '5.916', '6.915', '6.916',   # remessa/retorno conserto
    '5.912', '5.913', '6.912', '6.913',   # remessa/retorno demonstração
    '5.908', '5.909', '6.908', '6.909',   # remessa/retorno comodato
    '5.117', '6.117',                      # venda p/ entrega futura (receita só na NF real)
    '5.949', '6.949',                      # amostras grátis e remessas sem receita
    '5.201', '5.202', '6.201', '6.202',   # devoluções de compra emitidas pela VP
}
```

**2. Filtro aplicado em `nfe_omie()`:** extrai o CFOP de `det[0].prod.CFOP` e pula a NF se estiver na lista.

**3. Campo `cfop` adicionado** ao dict de cada NF retornada (referência futura).

### Resultado do teste (últimos 30 dias)

- Total NFs saída (tpNF=1): **100**
- **Excluídas pelo filtro**: 6 (amostras 5.949 × 3, entrega futura 5.117 × 1, retorno conserto 6.916 × 1, outro × 1)
- **Incluídas**: 94

### CFOPs presentes nas NFs incluídas

| CFOP | Qtd | Descrição |
|---|---|---|
| 5.101 | 39 | Venda de Produção do Estabelecimento |
| 5.102 | 2 | Venda de Mercadoria Adq./Recebida de Terceiros |
| 6.101 | 33 | Venda de Produção do Estabelecimento (interestadual) |
| 6.102 | 1 | Venda de Mercadoria (interestadual) |
| 6.107 | 15 | Venda de Produção p/ Não Contribuinte (interestadual) |
| 6.108 | 1 | Venda de Mercadoria p/ Não Contribuinte (interestadual) |
| 5.201 | 1 | Devolução de Compra → agora excluída (adicionada na sessão) |
| 6.201 | 1 | Devolução de Compra interestadual → agora excluída |
| 5.917 | 1 | Remessa por conta e ordem de terceiros (monitorar) |

---

## Status Final

| Item | Status |
|---|---|
| Filtro CFOP implementado em gerar_bordero.py | ✅ |
| 5.201 / 5.202 / 6.201 / 6.202 adicionados à exclusão | ✅ |
| CFOPs de venda real preservados (5.101, 5.102, 6.101, 6.102, 6.107, 6.108…) | ✅ |
| CFOP 5.917 (1 NF) | ⚠️ Monitorar — pode ser legítimo ou não |

---

*Hermes · CFO digital · VerticalParts — sessão 18/06/2026*
