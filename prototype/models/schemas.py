"""
Schemas Pydantic para o Chatbot Localiza
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# === Enums ===

class GrupoVeiculo(str, Enum):
    ECONOMICO = "A"
    COMPACTO = "B"
    INTERMEDIARIO = "C"
    SEDAN = "D"
    SUV = "E"
    PICKUP = "F"
    LUXO = "G"


class TipoAdicional(str, Enum):
    CADEIRINHA_BEBE = "cadeirinha_bebe"
    CADEIRINHA_INFANTIL = "cadeirinha_infantil"
    GPS = "gps"
    CONDUTOR_ADICIONAL = "condutor_adicional"
    PROTECAO_BASICA = "protecao_basica"
    PROTECAO_PREMIUM = "protecao_premium"


# === Agências ===

class Agencia(BaseModel):
    id: str
    nome: str
    cidade: str
    estado: str
    endereco: str
    aeroporto: bool = False
    horario_abertura: str = "08:00"
    horario_fechamento: str = "20:00"


# === Veículos ===

class Veiculo(BaseModel):
    id: str
    grupo: GrupoVeiculo
    nome: str
    marca: str
    capacidade_passageiros: int
    capacidade_malas: int
    ar_condicionado: bool = True
    direcao_hidraulica: bool = True
    cambio_automatico: bool = False


# === Cotação ===

class DadosCotacao(BaseModel):
    agencia_retirada_id: str
    agencia_devolucao_id: Optional[str] = None  # Se None, mesmo local
    data_retirada: date
    hora_retirada: str = "10:00"
    data_devolucao: date
    hora_devolucao: str = "10:00"
    grupo_veiculo: GrupoVeiculo


class ItemCotacao(BaseModel):
    descricao: str
    valor_unitario: float
    quantidade: int
    valor_total: float


class Cotacao(BaseModel):
    id: str
    dados: DadosCotacao
    veiculo_exemplo: str
    itens: List[ItemCotacao]
    subtotal_diarias: float
    taxa_limpeza: float = 50.0
    taxa_one_way: float = 0.0  # Se retirada != devolução
    total: float
    validade: datetime


# === Adicionais ===

class Adicional(BaseModel):
    tipo: TipoAdicional
    nome: str
    descricao: str
    valor_diaria: float


# === Chat ===

class MensagemChat(BaseModel):
    role: str = Field(..., description="user ou assistant")
    content: str


class RequestChat(BaseModel):
    session_id: str
    mensagem: str
    historico: List[MensagemChat] = []


class ResponseChat(BaseModel):
    session_id: str
    resposta: str
    acao_executada: Optional[str] = None
    dados: Optional[dict] = None


# === Reserva ===

class DadosCliente(BaseModel):
    nome: str
    cpf: str
    email: str
    telefone: str
    cnh: str


class Reserva(BaseModel):
    id: str
    cotacao_id: str
    cliente: DadosCliente
    adicionais: List[TipoAdicional] = []
    total_final: float
    status: str = "confirmada"
    created_at: datetime
