# Plano de Implementação - Chatbot IA Localiza

## Visão Geral

Este plano detalha as fases de implementação do chatbot com IA Generativa para reservas da Localiza.

**Duração estimada:** 12-16 semanas
**Equipe sugerida:** 4-6 engenheiros

---

## Fase 1: Fundação (Semanas 1-3)

### 1.1 Setup do Projeto

```bash
# Estrutura inicial
chatbot-localiza/
├── apps/
│   ├── api/              # API Gateway + Orquestrador
│   ├── workers/          # Processadores de fila
│   └── web/              # Dashboard admin
├── packages/
│   ├── core/             # Lógica compartilhada
│   ├── llm-router/       # Integração LLMs
│   └── rag-engine/       # Pipeline RAG
├── infra/
│   ├── k8s/              # Manifests Kubernetes
│   ├── terraform/        # IaC
│   └── docker/           # Dockerfiles
└── docs/
```

### 1.2 Infraestrutura Base

| Tarefa | Tecnologia | Prioridade |
|--------|------------|------------|
| Setup Kubernetes cluster | EKS/GKE | P0 |
| Deploy Redis cluster | Redis Sentinel | P0 |
| Setup Qdrant | Docker/K8s | P0 |
| CI/CD pipeline | GitHub Actions | P1 |
| Observabilidade | Datadog/Grafana | P1 |

### 1.3 Entregáveis

- [ ] Ambiente de dev configurado
- [ ] Redis rodando (sessions, cache, queue)
- [ ] Qdrant rodando
- [ ] Pipeline CI/CD básico
- [ ] Documentação de setup

---

## Fase 2: Core Services (Semanas 4-6)

### 2.1 API Gateway

```typescript
// Estrutura do Gateway
interface GatewayConfig {
  rateLimiting: {
    windowMs: 60000,
    max: 100  // requests por minuto
  },
  auth: {
    type: 'jwt',
    publicEndpoints: ['/health', '/webhook']
  }
}
```

**Tarefas:**
- [ ] Rate limiting por IP/usuário
- [ ] Autenticação JWT
- [ ] Webhook WhatsApp
- [ ] Webhook Web
- [ ] Health checks

### 2.2 Orquestrador

```typescript
// Fluxo do Orquestrador
interface ConversationState {
  sessionId: string;
  userId?: string;
  currentStep: 'greeting' | 'intent' | 'cotacao' | 'adicionais' | 'confirmacao' | 'reserva';
  context: {
    local?: string;
    dataRetirada?: Date;
    dataDevolucao?: Date;
    grupoVeiculo?: string;
    adicionais?: string[];
    cotacaoId?: string;
  };
  history: Message[];
}
```

**Tarefas:**
- [ ] Session Manager (Redis)
- [ ] Context Manager
- [ ] State Machine do fluxo
- [ ] Integração com BullMQ

### 2.3 Entregáveis

- [ ] Gateway funcionando
- [ ] Orquestrador com state machine
- [ ] Testes unitários (>80% coverage)
- [ ] Documentação API (OpenAPI)

---

## Fase 3: Inteligência (Semanas 7-9)

### 3.1 LLM Router (LiteLLM)

```python
# Configuração LiteLLM
from litellm import Router

router = Router(
    model_list=[
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "gpt-4-turbo",
                "api_key": os.getenv("OPENAI_API_KEY")
            }
        },
        {
            "model_name": "claude",
            "litellm_params": {
                "model": "claude-3-sonnet",
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            }
        }
    ],
    fallbacks=[{"gpt-4": ["claude"]}],
    routing_strategy="least-busy"
)
```

**Tarefas:**
- [ ] Setup LiteLLM
- [ ] Configurar providers (OpenAI, Anthropic)
- [ ] Implementar fallback
- [ ] Roteamento por custo/latência
- [ ] Cache de respostas

### 3.2 RAG Engine (LlamaIndex + Qdrant)

```python
# Setup RAG
from llama_index import VectorStoreIndex
from llama_index.vector_stores import QdrantVectorStore

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="localiza_faq"
)

index = VectorStoreIndex.from_vector_store(vector_store)
query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="compact"
)
```

**Tarefas:**
- [ ] Indexar FAQ do portal
- [ ] Indexar políticas e regras
- [ ] Query engine com filtros
- [ ] Hybrid search (semântico + keyword)
- [ ] Reranking

### 3.3 Function Calling

```python
# Tools para o LLM
tools = [
    {
        "name": "buscar_agencias",
        "description": "Busca agências disponíveis por cidade/aeroporto",
        "parameters": {"cidade": "string", "tipo": "string"}
    },
    {
        "name": "gerar_cotacao",
        "description": "Gera cotação de aluguel",
        "parameters": {
            "agencia_retirada": "string",
            "data_retirada": "date",
            "data_devolucao": "date",
            "grupo_veiculo": "string"
        }
    },
    {
        "name": "adicionar_item",
        "description": "Adiciona item à reserva (cadeirinha, GPS, etc)",
        "parameters": {"cotacao_id": "string", "item": "string"}
    },
    {
        "name": "confirmar_reserva",
        "description": "Confirma e efetiva a reserva",
        "parameters": {"cotacao_id": "string"}
    }
]
```

### 3.4 Entregáveis

- [ ] LLM Router funcionando
- [ ] RAG com FAQ indexado
- [ ] Function calling implementado
- [ ] Testes de integração
- [ ] Métricas de latência

---

## Fase 4: Integrações (Semanas 10-11)

### 4.1 APIs Localiza

| API | Endpoint | Método |
|-----|----------|--------|
| Agências | `/api/v1/agencias` | GET |
| Carros | `/api/v1/carros` | GET |
| Cotação | `/api/v1/cotacoes` | POST |
| Adicionais | `/api/v1/adicionais` | GET |
| Reserva | `/api/v1/reservas` | POST |
| Preços | `/api/v1/precos` | GET |

**Tarefas:**
- [ ] Client HTTP resiliente
- [ ] Circuit breaker
- [ ] Retry com backoff
- [ ] Cache de dados estáticos
- [ ] Mapeamento de erros

### 4.2 Canais

**WhatsApp (Twilio/Meta):**
- [ ] Webhook de entrada
- [ ] Envio de mensagens
- [ ] Templates aprovados
- [ ] Media handling

**Web:**
- [ ] WebSocket para chat
- [ ] REST fallback
- [ ] Widget embeddable

### 4.3 Entregáveis

- [ ] Integrações APIs funcionando
- [ ] WhatsApp conectado
- [ ] Web chat funcionando
- [ ] Testes E2E

---

## Fase 5: Escala & Produção (Semanas 12-14)

### 5.1 Kubernetes + HPA

```yaml
# HPA Configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chatbot-orquestrador
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: orquestrador
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: queue_size
      target:
        type: AverageValue
        averageValue: "100"
```

### 5.2 Observabilidade

```yaml
# Métricas essenciais
metrics:
  - messages_processed_total
  - llm_latency_seconds
  - llm_tokens_used
  - cache_hit_ratio
  - queue_size
  - error_rate
  - handoff_rate
```

**Tarefas:**
- [ ] Dashboards Grafana
- [ ] Alertas críticos
- [ ] Log aggregation
- [ ] Distributed tracing

### 5.3 Load Testing

```bash
# Usando script da skill
python scripts/api_load_tester.py \
  --target http://chatbot-api \
  --concurrent 1000 \
  --duration 300 \
  --ramp-up 60
```

**Cenários:**
- [ ] 10k msg/min (normal)
- [ ] 50k msg/min (pico médio)
- [ ] 100k msg/min (pico alto)

### 5.4 Entregáveis

- [ ] HPA configurado e testado
- [ ] Dashboards prontos
- [ ] Load test passando
- [ ] Runbook de operações

---

## Fase 6: Go-Live (Semanas 15-16)

### 6.1 Rollout Strategy

```
Semana 15:
├── Dia 1-2: Deploy em staging
├── Dia 3-4: Testes de aceitação
└── Dia 5: Go/No-go decision

Semana 16:
├── Dia 1: Canary 5% tráfego
├── Dia 2: Canary 25% tráfego
├── Dia 3: Canary 50% tráfego
├── Dia 4: 100% tráfego
└── Dia 5: Hypercare
```

### 6.2 Checklist Go-Live

**Infra:**
- [ ] Recursos provisionados
- [ ] Backups configurados
- [ ] DR testado
- [ ] Secrets rotacionados

**Segurança:**
- [ ] Pentest realizado
- [ ] LGPD compliance
- [ ] Rate limiting ativo
- [ ] WAF configurado

**Operações:**
- [ ] Runbook completo
- [ ] Equipe de plantão
- [ ] Rollback testado
- [ ] Comunicação pronta

---

## Estimativa de Custos (Mensal)

### Infraestrutura

| Recurso | Especificação | Custo/mês |
|---------|---------------|-----------|
| Kubernetes (EKS) | 3 nodes m5.xlarge | $500 |
| Redis | r6g.large | $200 |
| Qdrant | 2 pods 8GB | $150 |
| Load Balancer | ALB | $50 |
| **Subtotal Infra** | | **$900** |

### LLM APIs (100k msg/mês)

| Provider | Volume | Custo/mês |
|----------|--------|-----------|
| GPT-4 | 70% tráfego | $2,000 |
| Claude | 20% tráfego | $400 |
| GPT-3.5 (cache miss) | 10% | $50 |
| **Subtotal LLM** | | **$2,450** |

### Total Estimado

| Item | Custo |
|------|-------|
| Infraestrutura | $900 |
| LLM APIs | $2,450 |
| Observabilidade | $200 |
| **Total/mês** | **$3,550** |

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| API Localiza instável | Média | Alto | Circuit breaker + cache |
| Custo LLM acima do esperado | Alta | Médio | Cache agressivo + roteamento |
| Latência alta em picos | Média | Alto | HPA + queue |
| Alucinação do LLM | Média | Alto | Guardrails + confirmação |
| Falha no handoff | Baixa | Alto | Fallback automático |

---

## Próximos Passos

1. **Imediato:** Validar arquitetura com time de infra
2. **Semana 1:** Kickoff e setup ambiente
3. **Semana 2:** Começar Fase 1

---

*Plano criado usando skill: senior-backend*
*Data: Janeiro 2026*
