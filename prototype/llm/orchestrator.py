"""
Orquestrador de Chat - Chatbot Localiza
Usa LiteLLM para multi-model support e function calling
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# LiteLLM para orquestração multi-modelo
try:
    import litellm
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("⚠️  LiteLLM não instalado. Usando modo mock.")

from llm.tools import TOOLS, execute_tool


# System prompt do chatbot
SYSTEM_PROMPT = """Você é a Liza, assistente virtual da Localiza, a maior empresa de aluguel de carros da América Latina.

🎯 **Seu objetivo:** Ajudar clientes a fazer cotações e reservas de veículos de forma rápida e amigável.

📋 **Fluxo de cotação:**
1. Pergunte onde o cliente quer RETIRAR o carro (cidade ou aeroporto)
2. Pergunte onde quer DEVOLVER (pode ser o mesmo local)
3. Pergunte as DATAS de retirada e devolução
4. Pergunte o TIPO de veículo desejado (econômico, SUV, etc)
5. Gere a COTAÇÃO usando a ferramenta gerar_cotacao
6. Ofereça ADICIONAIS (cadeirinha, GPS, proteção)

🛠️ **Ferramentas disponíveis:**
- buscar_agencias: para encontrar agências por cidade
- listar_grupos_veiculos: para mostrar tipos de carro e preços
- gerar_cotacao: para criar uma cotação
- listar_adicionais: para mostrar extras disponíveis
- adicionar_item_cotacao: para incluir adicionais na cotação

💬 **Tom de voz:**
- Seja simpática e profissional
- Use emojis com moderação
- Seja objetiva nas respostas
- Confirme os dados antes de gerar cotação

📅 **Data atual:** {data_atual}

⚠️ **Importante:**
- Sempre use as ferramentas para buscar dados reais
- Não invente preços ou agências
- Se não encontrar uma agência, sugira cidades próximas
- Para efetivar reservas, direcione o cliente ao site ou app
"""


class ChatOrchestrator:
    """Orquestrador de conversas com LLM + Function Calling"""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        fallback_model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        self.model = model
        self.fallback_model = fallback_model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Configurar LiteLLM
        if LITELLM_AVAILABLE:
            litellm.set_verbose = False
            # Configurar fallbacks
            litellm.success_callback = []
            litellm.failure_callback = []

    def _get_system_prompt(self) -> str:
        """Retorna o system prompt com data atual"""
        return SYSTEM_PROMPT.format(
            data_atual=datetime.now().strftime("%d/%m/%Y")
        )

    def _format_messages(
        self,
        user_message: str,
        history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Formata mensagens para a API"""
        messages = [
            {"role": "system", "content": self._get_system_prompt()}
        ]

        # Adicionar histórico
        for msg in history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Adicionar mensagem atual
        messages.append({"role": "user", "content": user_message})

        return messages

    async def chat(
        self,
        user_message: str,
        history: List[Dict[str, str]] = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário e retorna a resposta.
        Suporta function calling para executar ações.
        """
        if history is None:
            history = []

        messages = self._format_messages(user_message, history)
        tool_calls_made = []

        # Se LiteLLM não está disponível, usar modo mock
        if not LITELLM_AVAILABLE:
            return await self._mock_response(user_message, messages)

        try:
            # Primeira chamada ao LLM
            response = await self._call_llm(messages)

            # Verificar se há tool calls
            message = response.choices[0].message

            # Loop de function calling (máximo 5 iterações para evitar loops infinitos)
            max_iterations = 5
            iteration = 0

            while message.tool_calls and iteration < max_iterations:
                iteration += 1

                # Adicionar resposta do assistente com tool calls
                messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })

                # Executar cada tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # Executar a função
                    result = execute_tool(function_name, arguments)
                    tool_calls_made.append({
                        "function": function_name,
                        "arguments": arguments,
                        "result": json.loads(result)
                    })

                    # Adicionar resultado da tool
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

                # Nova chamada ao LLM com os resultados
                response = await self._call_llm(messages)
                message = response.choices[0].message

            # Retornar resposta final
            return {
                "resposta": message.content or "Desculpe, não consegui processar sua mensagem.",
                "tool_calls": tool_calls_made,
                "model_used": response.model if hasattr(response, 'model') else self.model,
                "tokens_used": {
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                    "total": response.usage.total_tokens if response.usage else 0
                }
            }

        except Exception as e:
            # Tentar fallback
            try:
                return await self._fallback_response(messages, str(e))
            except Exception as fallback_error:
                return {
                    "resposta": f"Desculpe, estou com dificuldades técnicas. Por favor, tente novamente em alguns instantes. 🙏",
                    "erro": str(fallback_error),
                    "tool_calls": []
                }

    async def _call_llm(self, messages: List[Dict]) -> Any:
        """Chama o LLM via LiteLLM"""
        return completion(
            model=self.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

    async def _fallback_response(
        self,
        messages: List[Dict],
        original_error: str
    ) -> Dict[str, Any]:
        """Tenta responder usando modelo de fallback"""
        print(f"⚠️ Usando fallback. Erro original: {original_error}")

        response = completion(
            model=self.fallback_model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        message = response.choices[0].message

        return {
            "resposta": message.content or "Por favor, reformule sua pergunta.",
            "tool_calls": [],
            "model_used": self.fallback_model,
            "fallback": True
        }

    async def _mock_response(
        self,
        user_message: str,
        messages: List[Dict]
    ) -> Dict[str, Any]:
        """Resposta mock quando LiteLLM não está disponível"""
        user_lower = user_message.lower()

        # Detectar intenção e executar tools manualmente
        if any(word in user_lower for word in ["agência", "agencia", "onde", "local", "cidade"]):
            # Extrair cidade (simplificado)
            for cidade in ["são paulo", "sp", "belo horizonte", "bh", "rio", "rj"]:
                if cidade in user_lower:
                    result = execute_tool("buscar_agencias", {"cidade": cidade})
                    data = json.loads(result)
                    if data.get("sucesso"):
                        agencias = data.get("agencias", [])
                        texto = "Encontrei estas agências:\n\n"
                        for ag in agencias:
                            emoji = "✈️" if ag["aeroporto"] else "🏢"
                            texto += f"{emoji} **{ag['nome']}**\n"
                            texto += f"   📍 {ag['endereco']}\n"
                            texto += f"   🕐 {ag['horario']}\n\n"
                        return {
                            "resposta": texto,
                            "tool_calls": [{"function": "buscar_agencias", "arguments": {"cidade": cidade}}],
                            "model_used": "mock"
                        }

        if any(word in user_lower for word in ["preço", "preco", "valor", "quanto", "grupo", "tipo"]):
            result = execute_tool("listar_grupos_veiculos", {})
            data = json.loads(result)
            grupos = data.get("grupos", [])
            texto = "Confira nossos grupos de veículos:\n\n"
            for g in grupos:
                texto += f"🚗 **Grupo {g['codigo']} - {g['nome']}**\n"
                texto += f"   Ex: {g['exemplo']} | R$ {g['preco_diaria']:.2f}/dia\n\n"
            return {
                "resposta": texto,
                "tool_calls": [{"function": "listar_grupos_veiculos", "arguments": {}}],
                "model_used": "mock"
            }

        if any(word in user_lower for word in ["adicional", "cadeirinha", "gps", "proteção", "seguro"]):
            result = execute_tool("listar_adicionais", {})
            data = json.loads(result)
            adicionais = data.get("adicionais", [])
            texto = "Nossos adicionais disponíveis:\n\n"
            for ad in adicionais:
                texto += f"➕ **{ad['nome']}** - R$ {ad['valor_diaria']:.2f}/dia\n"
                texto += f"   {ad['descricao']}\n\n"
            return {
                "resposta": texto,
                "tool_calls": [{"function": "listar_adicionais", "arguments": {}}],
                "model_used": "mock"
            }

        # Resposta padrão
        return {
            "resposta": """Olá! 👋 Sou a Liza, assistente virtual da Localiza!

Posso te ajudar a:
🚗 Fazer uma **cotação** de aluguel
📍 Encontrar **agências** perto de você
💰 Ver **preços** e tipos de veículos
➕ Incluir **adicionais** (cadeirinha, GPS, proteção)

Por onde você gostaria de começar? Me conta qual cidade você precisa do carro! 😊""",
            "tool_calls": [],
            "model_used": "mock"
        }
