# Arquitetura Chatbot IA Generativa - Localiza

## Visão Geral

Arquitetura para chatbot com IA Generativa que realiza todas as etapas de reserva da Localiza: tirar dúvidas, gerar cotações, incluir adicionais e efetivar reservas.

**Requisitos de escala:** 100k mensagens em picos (feriados/alta temporada)

---

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ARQUITETURA CHATBOT LOCALIZA                         │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────┐     ┌──────────────┐
                    │   WhatsApp   │     │     Web      │
                    └──────┬───────┘     └──────┬───────┘
                           │                    │
                           └─────────┬──────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │     API GATEWAY       │
                         │   (Kong / AWS ALB)    │
                         │                       │
                         │  • Rate Limiting      │
                         │  • Auth               │
                         │  • Roteamento         │
                         └───────────┬───────────┘
                                     │
                                     ▼
┌───────────────┐        ┌───────────────────────┐        ┌───────────────┐
│               │        │                       │        │               │
│  REDIS #1     │◄──────►│     ORQUESTRADOR      │◄──────►│  REDIS #2     │
│  Sessions     │        │   (Session Manager)   │        │  Cache        │
│               │        │                       │        │               │
│ • Contexto    │        │  • Contexto conversa  │        │ • FAQ cache   │
│ • Estado      │        │  • Estado do fluxo    │        │ • Cotações    │
│ • Histórico   │        │  • Histórico          │        │   recentes    │
│ • TTL 30min   │        │                       │        │ • Reduz LLM   │
│               │        └───────────┬───────────┘        │               │
└───────────────┘                    │                    └───────────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │     REDIS #3          │
                         │   Queue (BullMQ)      │
                         │                       │
                         │  • Fila de mensagens  │
                         │  • Gerencia picos     │
                         │  • Retry automático   │
                         └───────────┬───────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            │                        │                        │
            ▼                        ▼                        ▼
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│   LLM ROUTER      │    │    RAG ENGINE     │    │   FUNCTION CALL   │
│   (LiteLLM)       │    │   (LlamaIndex)    │    │                   │
│                   │    │                   │    │                   │
│ ┌───────────────┐ │    │ ┌───────────────┐ │    │  • Cotação        │
│ │ GPT-4         │ │    │ │    Qdrant     │ │    │  • Reserva        │
│ │ Claude        │ │    │ │  (Vector DB)  │ │    │  • Agências       │
│ │ Fallback      │ │    │ └───────────────┘ │    │  • Carros         │
│ └───────────────┘ │    │                   │    │  • Adicionais     │
│                   │    │  • FAQ Portal     │    │  • Preços         │
│                   │    │  • Políticas      │    │                   │
│                   │    │  • Regras         │    │                   │
└───────────────────┘    └───────────────────┘    └─────────┬─────────┘
                                                           │
                                                           ▼
                                       ┌─────────────────────────────────┐
                                       │         APIs LOCALIZA           │
                                       │                                 │
                                       │  ┌───────────┐  ┌───────────┐   │
                                       │  │ Agências  │  │  Cotação  │   │
                                       │  └───────────┘  └───────────┘   │
                                       │  ┌───────────┐  ┌───────────┐   │
                                       │  │  Carros   │  │ Adicionais│   │
                                       │  └───────────┘  └───────────┘   │
                                       │  ┌───────────┐  ┌───────────┐   │
                                       │  │  Preços   │  │  Reserva  │   │
                                       │  └───────────┘  └───────────┘   │
                                       └─────────────────────────────────┘
                                                           │
                                                           ▼
                                       ┌─────────────────────────────────┐
                                       │        HANDOFF HUMANO           │
                                       │   (quando solicitado/falha)     │
                                       └─────────────────────────────────┘
```

---

## Stack Tecnológica

### Orquestração & LLM

| Componente | Tecnologia | Função |
|------------|------------|--------|
| LLM Router | **LiteLLM** | Proxy multi-provider (GPT, Claude, fallback) |
| RAG | **LlamaIndex** | Pipeline de retrieval otimizado |
| Vector DB | **Qdrant** | Armazenamento vetorial (Rust, alta performance) |

### Infraestrutura

| Componente | Tecnologia | Função |
|------------|------------|--------|
| Gateway | **Kong / AWS ALB** | Rate limit, auth, roteamento |
| Cache/Sessions | **Redis** | Contexto, cache, filas |
| Queue | **BullMQ** | Gerenciamento de filas (picos) |
| Containers | **Kubernetes + HPA** | Orquestração e auto-scaling |

---

## Posicionamento do Redis

O Redis atua em **3 funções** conectadas ao Orquestrador:

```
                         Orquestrador
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
   ┌───────────┐        ┌───────────┐        ┌───────────┐
   │  REDIS    │        │  REDIS    │        │  REDIS    │
   │ Sessions  │        │  Cache    │        │  Queue    │
   │           │        │           │        │ (BullMQ)  │
   │ db 0      │        │ db 1      │        │ db 2      │
   └───────────┘        └───────────┘        └───────────┘
```

### Redis #1 - Sessions

| Campo | Descrição |
|-------|-----------|
| **Contexto** | Dados da conversa atual |
| **Estado** | Etapa do fluxo (cotação, confirmação, etc) |
| **Histórico** | Últimas mensagens |
| **TTL** | 30 minutos (expira sessão inativa) |

### Redis #2 - Cache

| Campo | Descrição |
|-------|-----------|
| **FAQ** | Respostas frequentes do RAG |
| **Cotações** | Cotações recentes (evita recalcular) |
| **Benefício** | Reduz chamadas para LLM e APIs |

### Redis #3 - Queue (BullMQ)

| Campo | Descrição |
|-------|-----------|
| **Fila** | Mensagens aguardando processamento |
| **Picos** | Absorve 100k mensagens em alta temporada |
| **Retry** | Re-tentativa automática em falhas |

---

## Fluxo de Atendimento

```
  Cliente          Gateway         Orquestrador         Redis           LLM/RAG          APIs
     │                │                  │                │                │               │
     │── Mensagem ───►│                  │                │                │               │
     │                │── Valida/Auth ──►│                │                │               │
     │                │                  │── Busca sessão►│                │               │
     │                │                  │◄── Contexto ───│                │               │
     │                │                  │                │                │               │
     │                │                  │── Check cache ►│                │               │
     │                │                  │◄── Cache miss ─│                │               │
     │                │                  │                │                │               │
     │                │                  │── Classifica ─────────────────►│               │
     │                │                  │◄── Intenção: Cotação ──────────│               │
     │                │                  │                │                │               │
     │                │                  │── Busca dados ─────────────────────────────────►│
     │                │                  │◄── Agências, Carros, Preços ───────────────────│
     │                │                  │                │                │               │
     │                │                  │── Formata resposta ───────────►│               │
     │                │                  │◄── Texto natural ──────────────│               │
     │                │                  │                │                │               │
     │                │                  │── Salva sessão►│                │               │
     │                │                  │── Salva cache ►│                │               │
     │                │                  │                │                │               │
     │◄───────────────│◄── Resposta ────│                │                │               │
```

---

## Escalabilidade (100k mensagens/pico)

### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chatbot-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: chatbot-orquestrador
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Estratégia de Escala

| Cenário | Pods | Redis | LLM |
|---------|------|-------|-----|
| Normal | 2 | 1 cluster | GPT-4 |
| Pico médio | 6 | 1 cluster | GPT-4 + Claude |
| Pico alto (feriado) | 20 | 1 cluster | GPT-4 + Claude + Fallback local |

---

## Custos Estimados (LLM)

| Provider | Input/1M tokens | Output/1M tokens | Uso sugerido |
|----------|-----------------|------------------|--------------|
| GPT-4 | $30 | $60 | Principal |
| GPT-3.5 | $0.50 | $1.50 | FAQ simples |
| Claude Sonnet | $3 | $15 | Fallback |
| Llama (local) | Infra | Infra | Emergência |

### Otimizações de Custo

1. **Cache agressivo** - FAQ e cotações frequentes
2. **Roteamento inteligente** - GPT-3.5 para perguntas simples
3. **Fallback local** - Llama para picos extremos
4. **Compressão de contexto** - Limitar histórico enviado

---

## Segurança

| Item | Implementação |
|------|---------------|
| **Dados do cliente** | Não passar para LLM (tratativa no orquestrador) |
| **LGPD** | Anonimização em logs |
| **Auth** | OAuth 2.0 / JWT |
| **Rate Limit** | Por usuário/IP no Gateway |
| **Fraude** | Validação de padrões suspeitos |

---

## Handoff para Humano

Transferência automática quando:

- Cliente solicita explicitamente
- IA não consegue resolver após 3 tentativas
- Detecção de frustração/sentimento negativo
- Assuntos fora do escopo definido

---

## Requisitos Levantados

### Funcionais

- [x] Idioma: Português
- [x] Canais: WhatsApp, Web
- [x] Fluxo: Cotação → Adicionais → Confirmação → Reserva
- [x] APIs existentes disponíveis (tempo real)
- [x] Não precisa login para cotar
- [x] Adicionais: cadeirinha, GPS, etc.

### Não-Funcionais

- [x] 100k mensagens em picos
- [x] Alta temporada e feriados previsíveis
- [x] FAQ do portal de clientes disponível
- [x] Confirmar antes de efetivar reserva
- [x] Handoff humano sob demanda
- [x] Proteção contra uso malicioso

---

*Documento de arquitetura - Desafio Senior AI Engineer - Localiza*
