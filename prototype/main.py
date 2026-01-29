"""
Chatbot Localiza - API Principal
FastAPI + LiteLLM + Function Calling
"""
import os
import sys
from typing import Dict, List, Optional
from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Adicionar diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.schemas import RequestChat, ResponseChat, MensagemChat
from llm.orchestrator import ChatOrchestrator
from services.agencias import AgenciasService
from services.carros import CarrosService


# === FastAPI App ===

app = FastAPI(
    title="Chatbot Localiza API",
    description="API do chatbot de cotação e reserva de veículos da Localiza",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Orquestrador
orchestrator = ChatOrchestrator(
    model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
    fallback_model=os.getenv("LLM_FALLBACK", "gpt-3.5-turbo")
)

# Sessões em memória (em produção seria Redis)
sessions: Dict[str, List[MensagemChat]] = {}


# === Schemas ===

class ChatRequest(BaseModel):
    mensagem: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    resposta: str
    tool_calls: Optional[List[dict]] = None
    model_used: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


# === Endpoints ===

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check e informações da API"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal de chat.
    Recebe uma mensagem e retorna a resposta do chatbot.
    """
    # Criar ou recuperar sessão
    session_id = request.session_id or str(uuid4())

    if session_id not in sessions:
        sessions[session_id] = []

    # Obter histórico da sessão
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in sessions[session_id]
    ]

    # Processar mensagem
    try:
        result = await orchestrator.chat(
            user_message=request.mensagem,
            history=history,
            session_id=session_id
        )

        # Salvar no histórico
        sessions[session_id].append(
            MensagemChat(role="user", content=request.mensagem)
        )
        sessions[session_id].append(
            MensagemChat(role="assistant", content=result["resposta"])
        )

        # Limitar histórico a últimas 20 mensagens
        if len(sessions[session_id]) > 20:
            sessions[session_id] = sessions[session_id][-20:]

        return ChatResponse(
            session_id=session_id,
            resposta=result["resposta"],
            tool_calls=result.get("tool_calls"),
            model_used=result.get("model_used")
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar mensagem: {str(e)}"
        )


@app.delete("/chat/{session_id}")
async def clear_session(session_id: str):
    """Limpa o histórico de uma sessão"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"Sessão {session_id} encerrada"}
    raise HTTPException(status_code=404, detail="Sessão não encontrada")


# === Endpoints de Debug/Demo ===

@app.get("/demo/agencias")
async def demo_agencias(cidade: str = "São Paulo"):
    """Demo: Lista agências por cidade"""
    agencias = AgenciasService.buscar_por_cidade(cidade)
    return {
        "cidade": cidade,
        "total": len(agencias),
        "agencias": [ag.model_dump() for ag in agencias]
    }


@app.get("/demo/grupos")
async def demo_grupos():
    """Demo: Lista grupos de veículos"""
    return {
        "grupos": CarrosService.listar_grupos()
    }


@app.get("/demo/adicionais")
async def demo_adicionais():
    """Demo: Lista adicionais disponíveis"""
    adicionais = CarrosService.listar_adicionais()
    return {
        "adicionais": [ad.model_dump() for ad in adicionais]
    }


# === Main ===

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"""
╔═══════════════════════════════════════════════════════════╗
║           🚗 CHATBOT LOCALIZA - PROTÓTIPO                 ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║   API rodando em: http://{host}:{port}                    ║
║   Documentação:   http://{host}:{port}/docs               ║
║                                                           ║
║   Endpoints:                                              ║
║   • POST /chat        - Enviar mensagem                   ║
║   • GET  /demo/agencias - Listar agências                 ║
║   • GET  /demo/grupos   - Listar grupos de veículos       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )
