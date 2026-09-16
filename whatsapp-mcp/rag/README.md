# WhatsApp MCP RAG

Ponto de entrada para qualquer LLM que vá projetar, implementar, revisar ou operar funções do MCP WhatsApp.

Leia nesta ordem:

1. `RAG_MCP_WHATSAPP_VERTICALPARTS.md` — documento canônico com Plano de Uso WhatsApp, SPEC, SDD, gatilhos, prazos, devoluções, aprovações, eventos, templates, webhooks, segurança, auditoria, testes e comportamento esperado da LLM.
2. `fine_tuning_seed.jsonl` — exemplos supervisionados para few-shot, avaliação, testes de comportamento e preparação de dataset.

Regra central: antes de implementar uma nova função de WhatsApp, a LLM deve descobrir o plano daquele uso quando faltarem informações que alterem o desenho, principalmente gatilho, destinatário, ação esperada, link, prazo, follow-up, escalonamento, resposta esperada e critério de sucesso.

Este material é política de conhecimento e comportamento. Para capabilities realmente disponíveis no runtime, consulte as tools expostas pelo MCP e o código atual do módulo.