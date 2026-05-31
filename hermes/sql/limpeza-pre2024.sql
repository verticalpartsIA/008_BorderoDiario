-- =====================================================================
-- LIMPEZA / SANEAMENTO — projeto kgecbycsyrtdhmdziuul (BD Omie)
-- Decisão Gelson (2026-05-31): APAGAR TUDO com vencimento < 2024-01-01
--   (inclui os pré-2024 ainda em aberto — 0 em CP, 5 em CR ~R$23.755).
-- + Saneamento de datas corrompidas (vencimento com ano absurdo, ex: 2424).
-- =====================================================================
-- ⚠️  Este banco alimenta o dashboard em produção (vpdashboarddre).
-- ⚠️  Faça SNAPSHOT antes (Supabase → Database → Backups).
-- ⚠️  Rode no SQL Editor do Supabase, passo a passo.
-- =====================================================================

-- PASSO 1 — SIMULAÇÃO (não apaga). Confirme os números.
SELECT 'CP venc < 2024 (apagar)'      AS caso, COUNT(*) FROM "CP_Omie" WHERE data_vencimento < '2024-01-01'
UNION ALL
SELECT 'CR venc < 2024 (apagar)',     COUNT(*) FROM "CR_Omie" WHERE data_vencimento < '2024-01-01'
UNION ALL
SELECT 'CP datas corrompidas (>2100)', COUNT(*) FROM "CP_Omie" WHERE data_vencimento > '2100-01-01'
UNION ALL
SELECT 'CR datas corrompidas (>2100)', COUNT(*) FROM "CR_Omie" WHERE data_vencimento > '2100-01-01';
-- Esperado aprox.: CP<2024 ~624 | CR<2024 ~76 | CP>2100 >=1 | CR>2100 0

-- PASSO 2 — Ver as datas corrompidas para decidir (corrigir ano ou apagar)
SELECT codigo_lancamento_omie, codigo_cliente_omie, data_emissao,
       data_vencimento, valor_documento, status_titulo, numero_documento_fiscal
FROM "CP_Omie" WHERE data_vencimento > '2100-01-01'
ORDER BY data_vencimento;

-- =====================================================================
-- PASSO 3 — EXECUÇÃO (descomente após conferir PASSOS 1-2 e fazer backup)
-- =====================================================================
-- BEGIN;
--
--   -- 3a. Apagar tudo com vencimento anterior a 2024
--   DELETE FROM "CP_Omie" WHERE data_vencimento < '2024-01-01';
--   DELETE FROM "CR_Omie" WHERE data_vencimento < '2024-01-01';
--
--   -- 3b. Datas corrompidas: OPÇÃO A — corrigir o ano (recomendado se o
--   --     restante da data faz sentido; ex: 2424-09-02 -> 2024-09-02).
--   --     Ajuste manualmente conforme o que o PASSO 2 mostrar. Exemplo:
--   -- UPDATE "CP_Omie"
--   --   SET data_vencimento = make_date(2024, EXTRACT(MONTH FROM data_vencimento)::int,
--   --                                         EXTRACT(DAY   FROM data_vencimento)::int)
--   --   WHERE data_vencimento > '2100-01-01';
--   --
--   --     OPÇÃO B — se não der para inferir o ano certo, apagar:
--   -- DELETE FROM "CP_Omie" WHERE data_vencimento > '2100-01-01';
--   -- DELETE FROM "CR_Omie" WHERE data_vencimento > '2100-01-01';
--
--   -- 3c. Conferência pós-limpeza
--   SELECT 'CP total' AS t, COUNT(*),
--          MIN(data_vencimento) AS venc_min, MAX(data_vencimento) AS venc_max FROM "CP_Omie"
--   UNION ALL
--   SELECT 'CR total', COUNT(*),
--          MIN(data_vencimento), MAX(data_vencimento) FROM "CR_Omie";
--
-- COMMIT;   -- ou ROLLBACK; se algo divergir
-- =====================================================================

-- NOTA: omie_nfe_itens já foi saneado de pré-2024 em sessão anterior.
-- omie_orders: NÃO incluído aqui (pedidos antigos podem ter parcelas a
-- receber ainda vivas em CR_Omie de 2024+). Avaliar à parte se necessário.
