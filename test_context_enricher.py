#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para o Context Enricher
Testa a extração de termos culturais e busca de contexto
"""

import asyncio
import logging
import sys
from context_enricher import ContextEnricher

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_basic():
    """Teste básico de extração e busca"""
    print("=" * 60)
    print("TESTE 1: Extracao e Busca Basica")
    print("=" * 60)

    enricher = ContextEnricher()

    # Mensagens de teste
    messages = [
        {
            'text': 'Viram o BBB ontem? O Gay da shoppe ta causando muito!',
            'username': 'joao',
            'timestamp': '2026-01-31 10:00:00'
        },
        {
            'text': 'BBB ta muito bom esse ano, concordo! Ja assistiu?',
            'username': 'maria',
            'timestamp': '2026-01-31 10:01:00'
        },
        {
            'text': 'O Oscar vai ser em marco, quem vai assistir?',
            'username': 'pedro',
            'timestamp': '2026-01-31 10:02:00'
        },
        {
            'text': 'Oscar e sempre bom! Quero ver quem vai ganhar melhor filme',
            'username': 'ana',
            'timestamp': '2026-01-31 10:03:00'
        }
    ]

    # Testar enriquecimento
    result = await enricher.enrich_context(messages, max_searches=3)

    print("\nRESULTADO:")
    print(result if result else "Nenhum contexto encontrado")

    # Ver estatísticas do cache
    stats = enricher.get_cache_stats()
    print("\nCACHE STATS:")
    print(f"Total: {stats['total_entries']}")
    print(f"Validos: {stats['valid_entries']}")
    print(f"Expirados: {stats['expired_entries']}")

    return enricher


async def test_cache(enricher):
    """Teste de cache - segunda chamada deve ser instantânea"""
    print("\n" + "=" * 60)
    print("TESTE 2: Verificacao de Cache")
    print("=" * 60)

    messages = [
        {
            'text': 'BBB e muito legal, adoro assistir!',
            'username': 'carlos',
            'timestamp': '2026-01-31 10:05:00'
        },
        {
            'text': 'Tambem gosto do BBB, melhor reality',
            'username': 'julia',
            'timestamp': '2026-01-31 10:06:00'
        }
    ]

    import time
    start = time.time()
    result = await enricher.enrich_context(messages, max_searches=3)
    elapsed = time.time() - start

    print(f"\nTempo: {elapsed:.3f}s (deve ser <0.1s se usou cache)")
    print("\nRESULTADO:")
    print(result if result else "Nenhum contexto encontrado")

    stats = enricher.get_cache_stats()
    print("\nCACHE STATS:")
    print(f"Total: {stats['total_entries']}")
    print(f"Validos: {stats['valid_entries']}")


async def test_patterns():
    """Teste de padrões de extração"""
    print("\n" + "=" * 60)
    print("TESTE 3: Padroes de Extracao")
    print("=" * 60)

    enricher = ContextEnricher()

    messages = [
        {'text': 'Rock in Rio foi incrivel!', 'username': 'u1', 'timestamp': '10:00'},
        {'text': 'Copa do Mundo esta chegando', 'username': 'u2', 'timestamp': '10:01'},
        {'text': 'Globo vai transmitir o jogo', 'username': 'u3', 'timestamp': '10:02'},
        {'text': 'Netflix lancou serie nova', 'username': 'u4', 'timestamp': '10:03'},
        {'text': 'A Fazenda comecou ontem', 'username': 'u5', 'timestamp': '10:04'},
    ]

    # Apenas extrair candidatos (não buscar)
    candidates = enricher._extract_candidates(messages)
    print("\nTERMOS EXTRAIDOS:")
    for term in set(candidates):
        print(f"  - {term}")

    # Ranquear
    top = enricher._rank_candidates(candidates, 3)
    print("\nTOP 3 TERMOS:")
    for i, term in enumerate(top, 1):
        print(f"  {i}. {term}")


async def test_no_cultural_terms():
    """Teste com mensagens sem termos culturais"""
    print("\n" + "=" * 60)
    print("TESTE 4: Sem Termos Culturais")
    print("=" * 60)

    enricher = ContextEnricher()

    messages = [
        {'text': 'Oi, tudo bem?', 'username': 'u1', 'timestamp': '10:00'},
        {'text': 'Sim, e voce?', 'username': 'u2', 'timestamp': '10:01'},
        {'text': 'Vamos marcar um encontro', 'username': 'u3', 'timestamp': '10:02'},
    ]

    result = await enricher.enrich_context(messages, max_searches=3)

    print("\nRESULTADO:")
    print(result if result else "OK - Nenhum contexto (esperado)")


async def main():
    """Executa todos os testes"""
    print("\nINICIANDO TESTES DO CONTEXT ENRICHER\n")

    try:
        # Teste 1
        enricher = await test_basic()

        # Teste 2 (usa o mesmo enricher para testar cache)
        await test_cache(enricher)

        # Teste 3
        await test_patterns()

        # Teste 4
        await test_no_cultural_terms()

        print("\n" + "=" * 60)
        print("TODOS OS TESTES CONCLUIDOS COM SUCESSO!")
        print("=" * 60)

    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
