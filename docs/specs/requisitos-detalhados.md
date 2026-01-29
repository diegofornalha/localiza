# Requisitos Detalhados - Chatbot IA Localiza

**Versão:** 1.0
**Data:** Janeiro 2026
**Baseado em:** Análise aprofundada do site localiza.com e benchmark da Liza

---

## 1. Contexto de Negócio

### 1.1 Benchmark Atual - Chatbot Liza

A Localiza já possui a assistente virtual **Liza** em produção. Dados coletados:

| Métrica | Valor | Fonte |
|---------|-------|-------|
| **Volume diário** | 4.000 atendimentos/dia | Divulgação Localiza |
| **Volume mensal** | ~120.000 atendimentos | Calculado |
| **NPS** | >85 | Divulgação Localiza |
| **Resolução digital** | 92% | Divulgação Localiza |
| **Disponibilidade** | 24/7 | Observado no site |
| **Canais atuais** | Web (chat flutuante) | Observado no site |

### 1.2 Maturidade Digital da Localiza

| Iniciativa | Status |
|------------|--------|
| **Fast Retirada Digital** | 1M+ contratos, retirada em 5 min |
| **PWA** | Implementado (Service Worker + Manifest) |
| **Casos de IA internos** | 400+ em desenvolvimento |
| **Portal do Cliente** | Ativo com FAQ estruturado |

### 1.3 Oportunidade

O novo chatbot deve **expandir** as capacidades da Liza atual para:
- ✅ Novos canais (WhatsApp)
- ✅ Fluxo completo de reserva (não apenas cotação)
- ✅ Integração com Fast Retirada
- ✅ Escalabilidade para picos (feriados)

---

## 2. Requisitos Funcionais

### 2.1 Canais de Atendimento

| Canal | Prioridade | Justificativa |
|-------|------------|---------------|
| **WhatsApp** | P0 | 99% dos brasileiros usam, canal preferido |
| **Web** | P0 | Já existe, manter compatibilidade |
| **App Mobile** | P1 | Futuro, após validação |

### 2.2 Fluxos Suportados

```
┌─────────────────────────────────────────────────────────────────┐
│                     JORNADA DO CLIENTE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Entrada]                                                      │
│      │                                                          │
│      ▼                                                          │
│  ┌───────────────────┐                                          │
│  │ Identificar       │                                          │
│  │ Intenção          │                                          │
│  └─────────┬─────────┘                                          │
│            │                                                    │
│  ┌─────────┴─────────┬─────────────────┬──────────────────┐     │
│  │                   │                 │                  │     │
│  ▼                   ▼                 ▼                  ▼     │
│ [FAQ]           [Cotação]        [Reserva          [Suporte]    │
│                     │             Existente]                    │
│                     ▼                                           │
│              ┌──────────────┐                                   │
│              │ Coletar      │                                   │
│              │ • Local      │                                   │
│              │ • Data       │                                   │
│              │ • Grupo      │                                   │
│              └──────┬───────┘                                   │
│                     ▼                                           │
│              ┌──────────────┐                                   │
│              │ Gerar        │                                   │
│              │ Cotação      │◄──── API Localiza                 │
│              └──────┬───────┘                                   │
│                     ▼                                           │
│              ┌──────────────┐                                   │
│              │ Adicionais   │                                   │
│              │ • Cadeirinha │                                   │
│              │ • GPS        │                                   │
│              │ • Seguro     │                                   │
│              └──────┬───────┘                                   │
│                     ▼                                           │
│              ┌──────────────┐                                   │
│              │ Confirmar    │                                   │
│              │ (Opt-in)     │◄──── Obrigatório antes de         │
│              └──────┬───────┘      efetivar                     │
│                     ▼                                           │
│              ┌──────────────┐                                   │
│              │ Efetivar     │                                   │
│              │ Reserva      │◄──── API Localiza                 │
│              └──────┬───────┘                                   │
│                     ▼                                           │
│              ┌──────────────┐                                   │
│              │ Fast         │                                   │
│              │ Retirada?    │◄──── Integração diferenciada      │
│              └──────────────┘                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Funcionalidades por Fluxo

#### FAQ / Tirar Dúvidas
| Funcionalidade | Descrição | Fonte de Dados |
|----------------|-----------|----------------|
| Perguntas frequentes | Respostas sobre políticas, documentos, combustível | Portal do Cliente (FAQ) |
| Informações de agências | Endereço, horário, telefone | API Agências |
| Grupos de veículos | Características, capacidade, categorias | API Carros |
| Promoções ativas | Cupons, descontos vigentes | API Marketing |

#### Cotação
| Funcionalidade | Descrição | Validação |
|----------------|-----------|-----------|
| Local de retirada | Cidade, aeroporto ou agência específica | API Agências (disponibilidade) |
| Local de devolução | Mesmo local ou diferente | API Agências + regras de one-way |
| Data e hora | Retirada e devolução | Disponibilidade em tempo real |
| Grupo de veículo | Econômico → Luxo | API Carros + disponibilidade |
| Preço calculado | Diária × dias + taxas | API Preços |

#### Adicionais
| Adicional | Preço Médio | Regras |
|-----------|-------------|--------|
| Cadeirinha bebê | R$25/dia | Idade da criança |
| Cadeirinha infantil | R$25/dia | Peso da criança |
| GPS | R$20/dia | - |
| Condutor adicional | R$30/dia | CNH válida |
| Proteção básica | R$40/dia | Cobertura de danos |
| Proteção premium | R$80/dia | Cobertura total + terceiros |

#### Reserva
| Funcionalidade | Descrição | Requisito |
|----------------|-----------|-----------|
| Confirmação explícita | Cliente deve confirmar antes de efetivar | Obrigatório |
| Dados do cliente | Nome, CPF, CNH | Login ou coleta |
| Forma de pagamento | Cartão de crédito | Não processa no chatbot* |
| Comprovante | Número da reserva, QR Code | Envio por WhatsApp/Email |

*Pagamento: Redirecionar para checkout seguro ou Fast Retirada

---

## 3. Requisitos Não-Funcionais

### 3.1 Performance

| Métrica | Target | Justificativa |
|---------|--------|---------------|
| **Latência p50** | <2s | Expectativa de chat instantâneo |
| **Latência p99** | <5s | Tolerância para casos complexos |
| **Throughput normal** | 10k msg/min | Baseado em 120k/mês + margem |
| **Throughput pico** | 100k msg/min | Feriados e alta temporada |

### 3.2 Disponibilidade

| Métrica | Target | Justificativa |
|---------|--------|---------------|
| **Uptime** | 99.9% | ~8.7h downtime/ano |
| **RTO** | 15 min | Recovery Time Objective |
| **RPO** | 5 min | Recovery Point Objective |

### 3.3 Escalabilidade

| Cenário | Volume | Estratégia |
|---------|--------|------------|
| **Normal** | 4k/dia | 2 pods, GPT-4 |
| **Promoção** | 20k/dia | 6 pods, GPT-4 + Claude |
| **Feriado** | 100k/dia | 20 pods, GPT-4 + Claude + Fallback |

### 3.4 Qualidade

| Métrica | Target | Benchmark Atual |
|---------|--------|-----------------|
| **NPS** | ≥85 | Liza: 85 |
| **Resolução digital** | ≥90% | Liza: 92% |
| **Taxa de handoff** | <10% | Liza: 8% |
| **Satisfação (CSAT)** | ≥4.5/5 | A definir |

---

## 4. Requisitos de Segurança

### 4.1 LGPD Compliance

| Requisito | Implementação |
|-----------|---------------|
| **Consentimento** | Opt-in antes de coletar dados |
| **Anonimização** | Logs sem CPF/CNH em texto claro |
| **Retenção** | Sessões expiram em 30 min |
| **Direito ao esquecimento** | API para deletar histórico |

### 4.2 Proteção contra Fraude

| Ameaça | Mitigação |
|--------|-----------|
| **Prompt injection** | Sanitização de input, guardrails |
| **Abuso de API** | Rate limiting por IP/usuário |
| **Dados sensíveis** | Não enviar CPF/cartão para LLM |
| **Reservas fraudulentas** | Validação de CNH, limite por CPF |

---

## 5. Integrações

### 5.1 APIs Localiza (Existentes)

| API | Método | Uso |
|-----|--------|-----|
| `/api/v1/agencias` | GET | Buscar agências por cidade/aeroporto |
| `/api/v1/carros` | GET | Listar grupos e veículos disponíveis |
| `/api/v1/precos` | GET | Calcular preço por período |
| `/api/v1/cotacoes` | POST | Criar cotação |
| `/api/v1/adicionais` | GET | Listar adicionais disponíveis |
| `/api/v1/reservas` | POST | Efetivar reserva |

### 5.2 Canais

| Canal | Provider | Integração |
|-------|----------|------------|
| **WhatsApp** | Meta Business API / Twilio | Webhook + envio de templates |
| **Web** | Nativo | WebSocket + REST fallback |

### 5.3 Base de Conhecimento

| Fonte | Tipo | Atualização |
|-------|------|-------------|
| **FAQ Portal** | Texto estruturado | Semanal |
| **Políticas** | PDF/Texto | Sob demanda |
| **Regras de negócio** | Documentos internos | Sob demanda |

---

## 6. Critérios de Aceite

### 6.1 MVP (Fase 1)

- [ ] Chatbot responde FAQ com >85% de acurácia
- [ ] Fluxo completo de cotação funcionando
- [ ] Integração WhatsApp operacional
- [ ] Latência p50 <2s
- [ ] Handoff para humano funcionando

### 6.2 Produção (Fase 2)

- [ ] Efetivação de reservas integrada
- [ ] Adicionais incluídos no fluxo
- [ ] Escala para 100k msg/min testada
- [ ] NPS ≥85 em piloto
- [ ] Resolução digital ≥90%

### 6.3 Expansão (Fase 3)

- [ ] Fast Retirada integrado
- [ ] Proatividade (lembretes, upsell)
- [ ] Analytics avançado
- [ ] A/B testing de prompts

---

## 7. Riscos e Dependências

### 7.1 Riscos

| Risco | Prob. | Impacto | Mitigação |
|-------|-------|---------|-----------|
| API Localiza instável | Média | Alto | Circuit breaker + cache |
| Custo LLM excede budget | Alta | Médio | Roteamento + cache agressivo |
| Alucinação do LLM | Média | Alto | Guardrails + confirmação obrigatória |
| Adoção baixa WhatsApp | Baixa | Médio | Marketing + incentivos |

### 7.2 Dependências

| Dependência | Owner | Status |
|-------------|-------|--------|
| Acesso APIs Localiza | Time Backend | A confirmar |
| Conta WhatsApp Business | Time Marketing | A confirmar |
| FAQ estruturado | Time Conteúdo | Disponível |
| Ambiente cloud | Time Infra | A provisionar |

---

## 8. Glossário

| Termo | Definição |
|-------|-----------|
| **Grupo de veículo** | Categoria (A, B, C...) que agrupa carros similares |
| **One-way** | Retirada em uma agência, devolução em outra |
| **Fast Retirada** | Processo digital para retirar carro em <5 min |
| **Adicional** | Item opcional (GPS, cadeirinha, seguro extra) |
| **Handoff** | Transferência para atendente humano |

---

*Documento elaborado com base em análise do site localiza.com e dados públicos sobre a assistente Liza*
*Senior AI Engineer Challenge - Janeiro 2026*
