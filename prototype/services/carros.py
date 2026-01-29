"""
Mock Service - Carros/Veículos Localiza
Simula a API de veículos para o protótipo
"""
from typing import List, Optional, Dict
from models.schemas import Veiculo, GrupoVeiculo, Adicional, TipoAdicional


# Base de dados mock de veículos por grupo
VEICULOS_DB: List[Veiculo] = [
    # Grupo A - Econômico
    Veiculo(
        id="mobi", grupo=GrupoVeiculo.ECONOMICO, nome="Mobi", marca="Fiat",
        capacidade_passageiros=4, capacidade_malas=1
    ),
    Veiculo(
        id="kwid", grupo=GrupoVeiculo.ECONOMICO, nome="Kwid", marca="Renault",
        capacidade_passageiros=4, capacidade_malas=1
    ),
    # Grupo B - Compacto
    Veiculo(
        id="hb20", grupo=GrupoVeiculo.COMPACTO, nome="HB20", marca="Hyundai",
        capacidade_passageiros=5, capacidade_malas=2
    ),
    Veiculo(
        id="onix", grupo=GrupoVeiculo.COMPACTO, nome="Onix", marca="Chevrolet",
        capacidade_passageiros=5, capacidade_malas=2
    ),
    Veiculo(
        id="polo", grupo=GrupoVeiculo.COMPACTO, nome="Polo", marca="Volkswagen",
        capacidade_passageiros=5, capacidade_malas=2
    ),
    # Grupo C - Intermediário
    Veiculo(
        id="virtus", grupo=GrupoVeiculo.INTERMEDIARIO, nome="Virtus", marca="Volkswagen",
        capacidade_passageiros=5, capacidade_malas=3
    ),
    Veiculo(
        id="cronos", grupo=GrupoVeiculo.INTERMEDIARIO, nome="Cronos", marca="Fiat",
        capacidade_passageiros=5, capacidade_malas=3
    ),
    # Grupo D - Sedan
    Veiculo(
        id="corolla", grupo=GrupoVeiculo.SEDAN, nome="Corolla", marca="Toyota",
        capacidade_passageiros=5, capacidade_malas=3, cambio_automatico=True
    ),
    Veiculo(
        id="civic", grupo=GrupoVeiculo.SEDAN, nome="Civic", marca="Honda",
        capacidade_passageiros=5, capacidade_malas=3, cambio_automatico=True
    ),
    # Grupo E - SUV
    Veiculo(
        id="creta", grupo=GrupoVeiculo.SUV, nome="Creta", marca="Hyundai",
        capacidade_passageiros=5, capacidade_malas=4, cambio_automatico=True
    ),
    Veiculo(
        id="tracker", grupo=GrupoVeiculo.SUV, nome="Tracker", marca="Chevrolet",
        capacidade_passageiros=5, capacidade_malas=4, cambio_automatico=True
    ),
    Veiculo(
        id="compass", grupo=GrupoVeiculo.SUV, nome="Compass", marca="Jeep",
        capacidade_passageiros=5, capacidade_malas=4, cambio_automatico=True
    ),
    # Grupo F - Pickup
    Veiculo(
        id="strada", grupo=GrupoVeiculo.PICKUP, nome="Strada", marca="Fiat",
        capacidade_passageiros=2, capacidade_malas=0
    ),
    Veiculo(
        id="toro", grupo=GrupoVeiculo.PICKUP, nome="Toro", marca="Fiat",
        capacidade_passageiros=5, capacidade_malas=0, cambio_automatico=True
    ),
    # Grupo G - Luxo
    Veiculo(
        id="bmw-320i", grupo=GrupoVeiculo.LUXO, nome="320i", marca="BMW",
        capacidade_passageiros=5, capacidade_malas=3, cambio_automatico=True
    ),
]


# Preços por diária por grupo
PRECOS_DIARIA: Dict[GrupoVeiculo, float] = {
    GrupoVeiculo.ECONOMICO: 89.90,
    GrupoVeiculo.COMPACTO: 119.90,
    GrupoVeiculo.INTERMEDIARIO: 149.90,
    GrupoVeiculo.SEDAN: 199.90,
    GrupoVeiculo.SUV: 249.90,
    GrupoVeiculo.PICKUP: 229.90,
    GrupoVeiculo.LUXO: 449.90,
}


# Adicionais disponíveis
ADICIONAIS_DB: List[Adicional] = [
    Adicional(
        tipo=TipoAdicional.CADEIRINHA_BEBE,
        nome="Cadeirinha para Bebê",
        descricao="Para crianças de 0 a 1 ano (até 13kg)",
        valor_diaria=25.00
    ),
    Adicional(
        tipo=TipoAdicional.CADEIRINHA_INFANTIL,
        nome="Cadeirinha Infantil",
        descricao="Para crianças de 1 a 7 anos (9 a 36kg)",
        valor_diaria=25.00
    ),
    Adicional(
        tipo=TipoAdicional.GPS,
        nome="GPS",
        descricao="Navegador GPS com mapas atualizados",
        valor_diaria=20.00
    ),
    Adicional(
        tipo=TipoAdicional.CONDUTOR_ADICIONAL,
        nome="Condutor Adicional",
        descricao="Adicionar outro motorista autorizado",
        valor_diaria=30.00
    ),
    Adicional(
        tipo=TipoAdicional.PROTECAO_BASICA,
        nome="Proteção Básica",
        descricao="Cobertura de danos ao veículo com participação",
        valor_diaria=40.00
    ),
    Adicional(
        tipo=TipoAdicional.PROTECAO_PREMIUM,
        nome="Proteção Premium",
        descricao="Cobertura total + terceiros + vidros + pneus",
        valor_diaria=80.00
    ),
]


class CarrosService:
    """Serviço de Carros (Mock)"""

    @staticmethod
    def listar_por_grupo(grupo: GrupoVeiculo) -> List[Veiculo]:
        """Lista veículos de um grupo específico"""
        return [v for v in VEICULOS_DB if v.grupo == grupo]

    @staticmethod
    def buscar_por_id(veiculo_id: str) -> Optional[Veiculo]:
        """Busca veículo por ID"""
        for v in VEICULOS_DB:
            if v.id == veiculo_id:
                return v
        return None

    @staticmethod
    def listar_grupos() -> List[Dict]:
        """Lista grupos disponíveis com preços"""
        grupos = []
        for grupo in GrupoVeiculo:
            veiculos = [v for v in VEICULOS_DB if v.grupo == grupo]
            if veiculos:
                grupos.append({
                    "codigo": grupo.value,
                    "nome": grupo.name.replace("_", " ").title(),
                    "preco_diaria": PRECOS_DIARIA[grupo],
                    "exemplo": veiculos[0].nome,
                    "veiculos_disponiveis": len(veiculos)
                })
        return grupos

    @staticmethod
    def obter_preco_diaria(grupo: GrupoVeiculo) -> float:
        """Retorna preço da diária para um grupo"""
        return PRECOS_DIARIA.get(grupo, 0.0)

    @staticmethod
    def listar_adicionais() -> List[Adicional]:
        """Lista adicionais disponíveis"""
        return ADICIONAIS_DB

    @staticmethod
    def obter_adicional(tipo: TipoAdicional) -> Optional[Adicional]:
        """Obtém um adicional pelo tipo"""
        for ad in ADICIONAIS_DB:
            if ad.tipo == tipo:
                return ad
        return None

    @staticmethod
    def verificar_disponibilidade(grupo: GrupoVeiculo, agencia_id: str) -> bool:
        """Verifica disponibilidade (sempre True no mock)"""
        # Em produção, consultaria sistema de frotas
        return True
