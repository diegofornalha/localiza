"""
Mock Service - Cotação Localiza
Simula a API de cotação para o protótipo
"""
from typing import Optional, List
from datetime import datetime, date
from uuid import uuid4
from models.schemas import (
    Cotacao, DadosCotacao, ItemCotacao, GrupoVeiculo, TipoAdicional
)
from services.carros import CarrosService
from services.agencias import AgenciasService


# Cache de cotações em memória (em produção seria Redis)
COTACOES_CACHE: dict = {}


class CotacaoService:
    """Serviço de Cotação (Mock)"""

    @staticmethod
    def calcular_dias(data_retirada: date, data_devolucao: date) -> int:
        """Calcula número de dias da locação"""
        delta = data_devolucao - data_retirada
        dias = delta.days
        return max(1, dias)  # Mínimo 1 diária

    @staticmethod
    def gerar_cotacao(dados: DadosCotacao) -> Cotacao:
        """Gera uma cotação com base nos dados fornecidos"""

        # Validar agência de retirada
        agencia_retirada = AgenciasService.buscar_por_id(dados.agencia_retirada_id)
        if not agencia_retirada:
            raise ValueError(f"Agência de retirada não encontrada: {dados.agencia_retirada_id}")

        # Verificar se é one-way
        agencia_devolucao_id = dados.agencia_devolucao_id or dados.agencia_retirada_id
        is_one_way = agencia_devolucao_id != dados.agencia_retirada_id

        if is_one_way:
            agencia_devolucao = AgenciasService.buscar_por_id(agencia_devolucao_id)
            if not agencia_devolucao:
                raise ValueError(f"Agência de devolução não encontrada: {agencia_devolucao_id}")

        # Calcular dias
        dias = CotacaoService.calcular_dias(dados.data_retirada, dados.data_devolucao)

        # Obter preço da diária
        preco_diaria = CarrosService.obter_preco_diaria(dados.grupo_veiculo)

        # Obter veículo exemplo
        veiculos = CarrosService.listar_por_grupo(dados.grupo_veiculo)
        veiculo_exemplo = veiculos[0].nome if veiculos else "Veículo do grupo"

        # Montar itens
        itens = [
            ItemCotacao(
                descricao=f"Diária Grupo {dados.grupo_veiculo.value} ({veiculo_exemplo} ou similar)",
                valor_unitario=preco_diaria,
                quantidade=dias,
                valor_total=preco_diaria * dias
            )
        ]

        subtotal_diarias = preco_diaria * dias
        taxa_limpeza = 50.0
        taxa_one_way = 150.0 if is_one_way else 0.0

        itens.append(ItemCotacao(
            descricao="Taxa de Limpeza e Higienização",
            valor_unitario=taxa_limpeza,
            quantidade=1,
            valor_total=taxa_limpeza
        ))

        if is_one_way:
            itens.append(ItemCotacao(
                descricao="Taxa de Devolução em Local Diferente",
                valor_unitario=taxa_one_way,
                quantidade=1,
                valor_total=taxa_one_way
            ))

        total = subtotal_diarias + taxa_limpeza + taxa_one_way

        # Criar cotação
        cotacao = Cotacao(
            id=str(uuid4())[:8].upper(),
            dados=dados,
            veiculo_exemplo=veiculo_exemplo,
            itens=itens,
            subtotal_diarias=subtotal_diarias,
            taxa_limpeza=taxa_limpeza,
            taxa_one_way=taxa_one_way,
            total=total,
            validade=datetime.now().replace(hour=23, minute=59, second=59)
        )

        # Cachear
        COTACOES_CACHE[cotacao.id] = cotacao

        return cotacao

    @staticmethod
    def adicionar_item(cotacao_id: str, adicional_tipo: TipoAdicional) -> Optional[Cotacao]:
        """Adiciona um item adicional à cotação"""

        if cotacao_id not in COTACOES_CACHE:
            return None

        cotacao = COTACOES_CACHE[cotacao_id]
        adicional = CarrosService.obter_adicional(adicional_tipo)

        if not adicional:
            return None

        # Calcular dias da locação
        dias = CotacaoService.calcular_dias(
            cotacao.dados.data_retirada,
            cotacao.dados.data_devolucao
        )

        # Adicionar item
        item = ItemCotacao(
            descricao=adicional.nome,
            valor_unitario=adicional.valor_diaria,
            quantidade=dias,
            valor_total=adicional.valor_diaria * dias
        )

        cotacao.itens.append(item)
        cotacao.total += item.valor_total

        return cotacao

    @staticmethod
    def obter_cotacao(cotacao_id: str) -> Optional[Cotacao]:
        """Obtém cotação pelo ID"""
        return COTACOES_CACHE.get(cotacao_id)

    @staticmethod
    def formatar_cotacao_texto(cotacao: Cotacao) -> str:
        """Formata cotação para exibição em texto"""

        agencia_retirada = AgenciasService.buscar_por_id(cotacao.dados.agencia_retirada_id)
        agencia_devolucao_id = cotacao.dados.agencia_devolucao_id or cotacao.dados.agencia_retirada_id
        agencia_devolucao = AgenciasService.buscar_por_id(agencia_devolucao_id)

        texto = f"""
📋 **COTAÇÃO #{cotacao.id}**

🚗 **Veículo:** {cotacao.veiculo_exemplo} ou similar (Grupo {cotacao.dados.grupo_veiculo.value})

📍 **Retirada:** {agencia_retirada.nome if agencia_retirada else 'N/A'}
   📅 {cotacao.dados.data_retirada.strftime('%d/%m/%Y')} às {cotacao.dados.hora_retirada}

📍 **Devolução:** {agencia_devolucao.nome if agencia_devolucao else 'N/A'}
   📅 {cotacao.dados.data_devolucao.strftime('%d/%m/%Y')} às {cotacao.dados.hora_devolucao}

💰 **Valores:**
"""
        for item in cotacao.itens:
            texto += f"   • {item.descricao}: R$ {item.valor_total:.2f}\n"

        texto += f"""
━━━━━━━━━━━━━━━━━━━━━━
💵 **TOTAL: R$ {cotacao.total:.2f}**

⏰ Cotação válida até {cotacao.validade.strftime('%d/%m/%Y às %H:%M')}
"""
        return texto.strip()
