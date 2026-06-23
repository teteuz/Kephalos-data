"""
Scenario Seed Generator
Generates a rich synthetic narrative document when no source files are provided.
Zep's graph extractor then derives entities from this text — no PDFs needed.
"""

from typing import Optional
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger

logger = get_logger('kephalosdata.scenario_seed')

_SYSTEM_PROMPT = """Você é um gerador de cenários para simulação social com agentes autônomos.

Sua tarefa: dado um cenário, escreva uma REPORTAGEM NARRATIVA jornalística extensa com {agent_count} personagens fictícios e realistas. O texto deve ser denso o suficiente para que um sistema de extração de entidades consiga identificar cada personagem, suas relações e papéis.

REGRAS OBRIGATÓRIAS:
1. Todos os personagens são 100% fictícios — nomes brasileiros verossímeis, nunca pessoas reais.
2. Cada personagem deve aparecer pelo menos 3 vezes no texto em contextos diferentes.
3. Inclua personagens com perspectivas OPOSTAS sobre o cenário (favoráveis, contrários, neutros, oportunistas).
4. Especifique profissão, idade aproximada, cidade e posição no ecossistema do cenário.
5. Descreva relações explícitas entre personagens: "X é sócio de Y", "Z concorre com W", "A contratou B".
6. O texto deve ter NO MÍNIMO 2500 palavras — quanto mais rico, melhor a simulação.
7. NÃO use marcadores, listas ou JSON. Escreva em prosa narrativa corrida, como uma grande reportagem.
8. Inclua conflitos, alianças, histórias de fundo e comportamentos esperados em redes sociais.

ESTRUTURA SUGERIDA (adapte ao cenário):
- Parágrafo introdutório apresentando o cenário
- Seção 1: protagonistas e suas motivações
- Seção 2: opositores e céticos
- Seção 3: atores secundários (fornecedores, parceiros, reguladores, mídia, público)
- Seção 4: dinâmicas e conflitos entre grupos
- Seção 5: perspectivas e tensões futuras"""

_USER_PROMPT = """Cenário para simular: {scenario}

Objetivo da simulação: {requirement}

Gere a reportagem narrativa com exatamente {agent_count} personagens distintos, todos pertinentes a este cenário específico.
Lembre-se: mínimo de 2500 palavras, prosa corrida, sem listas."""


def generate_scenario_seed(
    scenario: str,
    requirement: str,
    agent_count: int = 25
) -> str:
    """
    Generate a rich narrative document for a scenario without source files.

    Args:
        scenario: Short scenario description (e.g. "abrir uma academia em São Paulo em 2026")
        requirement: Simulation objective/directive
        agent_count: Number of synthetic characters to generate (default 25)

    Returns:
        Plain text narrative that Zep will extract entities from.
    """
    logger.info(f"Gerando seed sintético para: '{scenario[:80]}...' com {agent_count} personagens")

    llm = LLMClient()

    system = _SYSTEM_PROMPT.format(agent_count=agent_count)
    user = _USER_PROMPT.format(
        scenario=scenario,
        requirement=requirement,
        agent_count=agent_count
    )

    try:
        text = llm.chat(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            temperature=0.85,
            max_tokens=6000
        )
        logger.info(f"Seed gerado: {len(text)} caracteres")
        return text
    except Exception as e:
        logger.error(f"Erro ao gerar seed sintético: {e}")
        # Fallback — return the requirement itself so the pipeline doesn't break
        return requirement
