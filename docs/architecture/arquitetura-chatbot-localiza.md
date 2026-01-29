# Arquitetura Chatbot IA - Localiza

## Visão Geral

Chatbot com IA Generativa para reservas de veículos: dúvidas, cotações, adicionais e reservas.

**Capacidade:** 100k mensagens/dia

---

## Arquitetura

```
                              ┌──────────────┐
                              │   Web Chat   │
                              │   (React)    │
                              └──────┬───────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │     API GATEWAY       │
                         │  Rate Limit • Auth    │
                         └───────────┬───────────┘
                                     │
                                     ▼
┌───────────────┐        ┌───────────────────────┐        ┌───────────────┐
│    REDIS      │◄──────►│     ORQUESTRADOR      │◄──────►│    REDIS      │
│   Sessions    │        │      (FastAPI)        │        │    Cache      │
└───────────────┘        └───────────┬───────────┘        └───────────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            │                        │                        │
            ▼                        ▼                        ▼
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│    LLM ROUTER     │    │    RAG ENGINE     │    │  FUNCTION CALL    │
│    (LiteLLM)      │    │   (LlamaIndex)    │    │                   │
│                   │    │                   │    │  • Cotação        │
│  GPT-4o • Claude  │    │  Qdrant (Vector)  │    │  • Reserva        │
│  Llama (fallback) │    │  FAQ • Políticas  │    │  • Agências       │
└───────────────────┘    └───────────────────┘    └─────────┬─────────┘
                                                           │
                                                           ▼
                                             ┌─────────────────────────┐
                                             │     APIs LOCALIZA       │
                                             │  Agências • Veículos    │
                                             │  Cotações • Reservas    │
                                             └─────────────────────────┘
```

---

## Componentes

| Componente | Tecnologia | Função |
|------------|------------|--------|
| **Frontend** | React | Widget de chat web |
| **Gateway** | Kong | Rate limit, autenticação |
| **Orquestrador** | FastAPI | Gerencia conversa |
| **LLM** | LiteLLM | Multi-provider |
| **RAG** | LlamaIndex + Qdrant | Busca FAQ/políticas |
| **Cache** | Redis | Sessões e cache |
| **Infra** | Kubernetes | Auto-scaling |

---

## Fluxo

```
Usuário → Gateway → Orquestrador → LLM/RAG → APIs Localiza → Resposta
```

1. Usuário envia mensagem
2. Gateway valida e roteia
3. Orquestrador recupera contexto (Redis)
4. LLM classifica intenção
5. RAG busca informações se necessário
6. Function Call executa ação (cotação, reserva)
7. LLM formata resposta
8. Retorna ao usuário

---

## Escalabilidade

- **HPA**: 2 a 20 pods conforme demanda
- **LLM Fallback**: GPT → Claude → Llama local
- **Cache**: Reduz chamadas LLM em ~30%

---

## Handoff Humano

Transfere para atendente quando:
- Cliente solicita
- IA não resolve
- Detecta frustração

---

*Chatbot Localiza - Visão Macro*
