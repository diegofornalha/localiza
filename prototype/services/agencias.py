"""
Mock Service - Agências Localiza
Simula a API de agências para o protótipo
"""
from typing import List, Optional
from models.schemas import Agencia


# Base de dados mock de agências
AGENCIAS_DB: List[Agencia] = [
    # Belo Horizonte
    Agencia(
        id="bh-confins",
        nome="Aeroporto Confins",
        cidade="Confins",
        estado="MG",
        endereco="Aeroporto Internacional de Confins, MG-010",
        aeroporto=True,
        horario_abertura="06:00",
        horario_fechamento="23:00"
    ),
    Agencia(
        id="bh-savassi",
        nome="Savassi",
        cidade="Belo Horizonte",
        estado="MG",
        endereco="Av. Getúlio Vargas, 1492 - Savassi",
        aeroporto=False
    ),
    Agencia(
        id="bh-pampulha",
        nome="Pampulha",
        cidade="Belo Horizonte",
        estado="MG",
        endereco="Av. Portugal, 4000 - Pampulha",
        aeroporto=False
    ),
    # São Paulo
    Agencia(
        id="sp-gru",
        nome="Aeroporto Guarulhos",
        cidade="Guarulhos",
        estado="SP",
        endereco="Aeroporto Internacional de Guarulhos, Rod. Hélio Smidt",
        aeroporto=True,
        horario_abertura="06:00",
        horario_fechamento="23:00"
    ),
    Agencia(
        id="sp-congonhas",
        nome="Aeroporto Congonhas",
        cidade="São Paulo",
        estado="SP",
        endereco="Aeroporto de Congonhas, Av. Washington Luís",
        aeroporto=True,
        horario_abertura="06:00",
        horario_fechamento="22:00"
    ),
    Agencia(
        id="sp-paulista",
        nome="Paulista",
        cidade="São Paulo",
        estado="SP",
        endereco="Av. Paulista, 1000 - Bela Vista",
        aeroporto=False
    ),
    Agencia(
        id="sp-faria-lima",
        nome="Faria Lima",
        cidade="São Paulo",
        estado="SP",
        endereco="Av. Faria Lima, 2500 - Pinheiros",
        aeroporto=False
    ),
    # Rio de Janeiro
    Agencia(
        id="rj-galeao",
        nome="Aeroporto Galeão",
        cidade="Rio de Janeiro",
        estado="RJ",
        endereco="Aeroporto Internacional Tom Jobim - Ilha do Governador",
        aeroporto=True,
        horario_abertura="06:00",
        horario_fechamento="23:00"
    ),
    Agencia(
        id="rj-santos-dumont",
        nome="Santos Dumont",
        cidade="Rio de Janeiro",
        estado="RJ",
        endereco="Aeroporto Santos Dumont - Centro",
        aeroporto=True,
        horario_abertura="06:00",
        horario_fechamento="22:00"
    ),
    Agencia(
        id="rj-copacabana",
        nome="Copacabana",
        cidade="Rio de Janeiro",
        estado="RJ",
        endereco="Av. Atlântica, 1500 - Copacabana",
        aeroporto=False
    ),
]


class AgenciasService:
    """Serviço de Agências (Mock)"""

    @staticmethod
    def buscar_por_cidade(cidade: str) -> List[Agencia]:
        """Busca agências por cidade (case insensitive, partial match)"""
        cidade_lower = cidade.lower()
        return [
            ag for ag in AGENCIAS_DB
            if cidade_lower in ag.cidade.lower() or cidade_lower in ag.estado.lower()
        ]

    @staticmethod
    def buscar_por_id(agencia_id: str) -> Optional[Agencia]:
        """Busca agência por ID"""
        for ag in AGENCIAS_DB:
            if ag.id == agencia_id:
                return ag
        return None

    @staticmethod
    def buscar_aeroportos(cidade: Optional[str] = None) -> List[Agencia]:
        """Busca agências em aeroportos"""
        aeroportos = [ag for ag in AGENCIAS_DB if ag.aeroporto]
        if cidade:
            cidade_lower = cidade.lower()
            aeroportos = [
                ag for ag in aeroportos
                if cidade_lower in ag.cidade.lower() or cidade_lower in ag.estado.lower()
            ]
        return aeroportos

    @staticmethod
    def listar_todas() -> List[Agencia]:
        """Lista todas as agências"""
        return AGENCIAS_DB

    @staticmethod
    def listar_cidades() -> List[str]:
        """Lista cidades únicas com agências"""
        cidades = set()
        for ag in AGENCIAS_DB:
            cidades.add(f"{ag.cidade}/{ag.estado}")
        return sorted(list(cidades))
