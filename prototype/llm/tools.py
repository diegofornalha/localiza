"""
Function Calling Tools - Chatbot Localiza
Define as ferramentas que o LLM pode invocar
"""
import json
from typing import Any, Dict, List
from datetime import date
from models.schemas import GrupoVeiculo, DadosCotacao, TipoAdicional
from services.agencias import AgenciasService
from services.carros import CarrosService
from services.cotacao import CotacaoService


# === Definição das Tools (OpenAI Function Calling Format) ===

TOOLS: List[Dict] = [
    {
        "type": "function",
        "function": {
            "name": "buscar_agencias",
            "description": "Busca agências da Localiza por cidade ou estado. Use quando o cliente mencionar um local para retirada ou devolução.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cidade": {
                        "type": "string",
                        "description": "Nome da cidade ou sigla do estado (ex: 'São Paulo', 'SP', 'Belo Horizonte')"
                    },
                    "apenas_aeroportos": {
                        "type": "boolean",
                        "description": "Se True, retorna apenas agências em aeroportos",
                        "default": False
                    }
                },
                "required": ["cidade"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_grupos_veiculos",
            "description": "Lista os grupos de veículos disponíveis com preços. Use quando o cliente perguntar sobre tipos de carro ou preços.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "gerar_cotacao",
            "description": "Gera uma cotação de aluguel. Use quando tiver todos os dados: local de retirada, local de devolução, datas e tipo de veículo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agencia_retirada_id": {
                        "type": "string",
                        "description": "ID da agência de retirada (obtido de buscar_agencias)"
                    },
                    "agencia_devolucao_id": {
                        "type": "string",
                        "description": "ID da agência de devolução. Se omitido, será o mesmo da retirada."
                    },
                    "data_retirada": {
                        "type": "string",
                        "description": "Data de retirada no formato YYYY-MM-DD"
                    },
                    "hora_retirada": {
                        "type": "string",
                        "description": "Hora de retirada no formato HH:MM (padrão 10:00)",
                        "default": "10:00"
                    },
                    "data_devolucao": {
                        "type": "string",
                        "description": "Data de devolução no formato YYYY-MM-DD"
                    },
                    "hora_devolucao": {
                        "type": "string",
                        "description": "Hora de devolução no formato HH:MM (padrão 10:00)",
                        "default": "10:00"
                    },
                    "grupo_veiculo": {
                        "type": "string",
                        "enum": ["A", "B", "C", "D", "E", "F", "G"],
                        "description": "Código do grupo: A=Econômico, B=Compacto, C=Intermediário, D=Sedan, E=SUV, F=Pickup, G=Luxo"
                    }
                },
                "required": ["agencia_retirada_id", "data_retirada", "data_devolucao", "grupo_veiculo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_adicionais",
            "description": "Lista os adicionais disponíveis (cadeirinha, GPS, proteção, etc). Use quando o cliente perguntar sobre extras ou adicionais.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adicionar_item_cotacao",
            "description": "Adiciona um item adicional a uma cotação existente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cotacao_id": {
                        "type": "string",
                        "description": "ID da cotação"
                    },
                    "adicional": {
                        "type": "string",
                        "enum": ["cadeirinha_bebe", "cadeirinha_infantil", "gps", "condutor_adicional", "protecao_basica", "protecao_premium"],
                        "description": "Tipo do adicional a ser incluído"
                    }
                },
                "required": ["cotacao_id", "adicional"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obter_cotacao",
            "description": "Obtém os detalhes de uma cotação existente pelo ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cotacao_id": {
                        "type": "string",
                        "description": "ID da cotação"
                    }
                },
                "required": ["cotacao_id"]
            }
        }
    }
]


# === Execução das Tools ===

def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Executa uma tool e retorna o resultado como string JSON"""

    try:
        if tool_name == "buscar_agencias":
            cidade = arguments.get("cidade", "")
            apenas_aeroportos = arguments.get("apenas_aeroportos", False)

            if apenas_aeroportos:
                agencias = AgenciasService.buscar_aeroportos(cidade)
            else:
                agencias = AgenciasService.buscar_por_cidade(cidade)

            if not agencias:
                return json.dumps({
                    "sucesso": False,
                    "mensagem": f"Nenhuma agência encontrada em '{cidade}'. Cidades disponíveis: {', '.join(AgenciasService.listar_cidades())}"
                }, ensure_ascii=False)

            return json.dumps({
                "sucesso": True,
                "total": len(agencias),
                "agencias": [
                    {
                        "id": ag.id,
                        "nome": ag.nome,
                        "cidade": ag.cidade,
                        "estado": ag.estado,
                        "endereco": ag.endereco,
                        "aeroporto": ag.aeroporto,
                        "horario": f"{ag.horario_abertura} - {ag.horario_fechamento}"
                    }
                    for ag in agencias
                ]
            }, ensure_ascii=False)

        elif tool_name == "listar_grupos_veiculos":
            grupos = CarrosService.listar_grupos()
            return json.dumps({
                "sucesso": True,
                "grupos": grupos
            }, ensure_ascii=False)

        elif tool_name == "gerar_cotacao":
            try:
                dados = DadosCotacao(
                    agencia_retirada_id=arguments["agencia_retirada_id"],
                    agencia_devolucao_id=arguments.get("agencia_devolucao_id"),
                    data_retirada=date.fromisoformat(arguments["data_retirada"]),
                    hora_retirada=arguments.get("hora_retirada", "10:00"),
                    data_devolucao=date.fromisoformat(arguments["data_devolucao"]),
                    hora_devolucao=arguments.get("hora_devolucao", "10:00"),
                    grupo_veiculo=GrupoVeiculo(arguments["grupo_veiculo"])
                )
                cotacao = CotacaoService.gerar_cotacao(dados)
                texto = CotacaoService.formatar_cotacao_texto(cotacao)

                return json.dumps({
                    "sucesso": True,
                    "cotacao_id": cotacao.id,
                    "total": cotacao.total,
                    "texto_formatado": texto
                }, ensure_ascii=False)

            except ValueError as e:
                return json.dumps({
                    "sucesso": False,
                    "erro": str(e)
                }, ensure_ascii=False)

        elif tool_name == "listar_adicionais":
            adicionais = CarrosService.listar_adicionais()
            return json.dumps({
                "sucesso": True,
                "adicionais": [
                    {
                        "tipo": ad.tipo.value,
                        "nome": ad.nome,
                        "descricao": ad.descricao,
                        "valor_diaria": ad.valor_diaria
                    }
                    for ad in adicionais
                ]
            }, ensure_ascii=False)

        elif tool_name == "adicionar_item_cotacao":
            cotacao_id = arguments["cotacao_id"]
            adicional = TipoAdicional(arguments["adicional"])

            cotacao = CotacaoService.adicionar_item(cotacao_id, adicional)
            if not cotacao:
                return json.dumps({
                    "sucesso": False,
                    "erro": f"Cotação {cotacao_id} não encontrada ou adicional inválido"
                }, ensure_ascii=False)

            texto = CotacaoService.formatar_cotacao_texto(cotacao)
            return json.dumps({
                "sucesso": True,
                "cotacao_id": cotacao.id,
                "novo_total": cotacao.total,
                "texto_formatado": texto
            }, ensure_ascii=False)

        elif tool_name == "obter_cotacao":
            cotacao_id = arguments["cotacao_id"]
            cotacao = CotacaoService.obter_cotacao(cotacao_id)

            if not cotacao:
                return json.dumps({
                    "sucesso": False,
                    "erro": f"Cotação {cotacao_id} não encontrada"
                }, ensure_ascii=False)

            texto = CotacaoService.formatar_cotacao_texto(cotacao)
            return json.dumps({
                "sucesso": True,
                "cotacao_id": cotacao.id,
                "total": cotacao.total,
                "texto_formatado": texto
            }, ensure_ascii=False)

        else:
            return json.dumps({
                "sucesso": False,
                "erro": f"Tool desconhecida: {tool_name}"
            }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "sucesso": False,
            "erro": f"Erro ao executar {tool_name}: {str(e)}"
        }, ensure_ascii=False)
