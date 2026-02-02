import logging
import re
import asyncio
from typing import List, Dict, Set, Tuple
from collections import Counter
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ContextEnricher:
    """Enriquece contexto de mensagens buscando informações culturais na web"""

    def __init__(self):
        self.cache = {}  # Cache simples com TTL de 24h
        self.cache_ttl = timedelta(hours=24)

        # Padrões regex para identificar termos culturais brasileiros
        self.cultural_patterns = [
            r'\b(BBB|Big Brother Brasil?)\b',
            r'\b(A Fazenda)\b',
            r'\b(Domingão|Faustão|Caldeirão|Fantástico)\b',
            r'\b(Oscar|Grammy|Emmy|Golden Globe)\b',
            r'\b(Rock in Rio|Lollapalooza|Festival)\b',
            r'\b(Copa do Mundo|Olimpíadas?|Mundial)\b',
            r'\b(Globo|SBT|Record|Band)\b',
            r'\b(Netflix|Disney\+|Amazon Prime|HBO)\b',
            r'\w+\s+da\s+(shoppe|casa|semana|vez)',  # Ex: "Gay da shoppe"
            r'\b(menina|garota|cara|cara)\s+(com|da|do)\s+\w+',  # Ex: "menina com armadura"
        ]

        # Stop words para filtrar termos irrelevantes
        self.stop_words = {
            'o', 'a', 'de', 'da', 'do', 'e', 'é', 'para', 'com', 'em', 'os', 'as',
            'um', 'uma', 'no', 'na', 'por', 'que', 'foi', 'não', 'mas', 'são',
            'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas', 'meu', 'seu',
            'hoje', 'ontem', 'amanhã', 'agora', 'sempre', 'nunca', 'muito', 'pouco',
            'bem', 'mal', 'sim', 'não', 'talvez', 'quando', 'onde', 'como', 'porque'
        }

    async def enrich_context(self, messages: List[Dict], max_searches: int = 5) -> str:
        """
        Extrai termos culturais das mensagens e busca contexto na web

        Args:
            messages: Lista de mensagens do grupo
            max_searches: Máximo de pesquisas a realizar

        Returns:
            String formatada com contexto cultural encontrado
        """
        if not messages:
            return ""

        # Extrair candidatos a termos culturais
        candidates = self._extract_candidates(messages)

        if not candidates:
            logger.info("Nenhum termo cultural identificado")
            return ""

        # Ranquear e selecionar top candidatos
        top_candidates = self._rank_candidates(candidates, max_searches)

        logger.info(f"Termos culturais identificados: {', '.join(top_candidates)}")

        # Buscar contexto para cada termo (em paralelo)
        search_tasks = [self._search_duckduckgo(term) for term in top_candidates]
        results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Filtrar resultados válidos
        context_entries = []
        cache_hits = 0

        for term, result in zip(top_candidates, results):
            if isinstance(result, Exception):
                logger.warning(f"Erro ao buscar contexto para '{term}': {result}")
                continue

            if result:
                if result.get('cached'):
                    cache_hits += 1
                context_entries.append(f"- \"{term}\": {result['context']}")

        logger.info(f"Contexto enriquecido: {len(context_entries)} termos pesquisados (cache hits: {cache_hits}/{len(top_candidates)})")

        if not context_entries:
            return ""

        # Formatar contexto para o prompt
        context_text = "\n".join(context_entries)
        return f"""
CONTEXTO CULTURAL E REFERÊNCIAS:
Use as informações abaixo para enriquecer seu resumo quando mencionar estes termos:

{context_text}

(Fonte: DuckDuckGo Instant Answers)
"""

    def _extract_candidates(self, messages: List[Dict]) -> List[str]:
        """
        Extrai candidatos a termos culturais das mensagens

        Returns:
            Lista de termos candidatos com prioridade para nomes de pessoas
        """
        candidates = []
        all_text = " ".join([msg.get('text', '') for msg in messages])

        # 1. Buscar padrões conhecidos (programas, eventos, etc)
        for pattern in self.cultural_patterns:
            matches = re.finditer(pattern, all_text, re.IGNORECASE)
            for match in matches:
                term = match.group(0).strip()
                if term:
                    # Adicionar com peso extra (repetir 2x para aumentar prioridade)
                    candidates.append(term)
                    candidates.append(term)

        # 2. Buscar palavras capitalizadas que aparecem frequentemente
        # (possíveis nomes próprios, marcas, eventos, PESSOAS)
        words = re.findall(r'\b[A-ZÀ-Ü][a-zà-ü]+\b', all_text)
        word_counts = Counter(words)

        # Adicionar palavras que aparecem 2+ vezes (reduzido de 3 para pegar mais nomes)
        for word, count in word_counts.items():
            if count >= 2 and word.lower() not in self.stop_words:
                # Adicionar múltiplas vezes baseado na frequência (priorizar mais mencionados)
                for _ in range(min(count, 5)):  # Max 5x para não dominar
                    candidates.append(word)

        # 3. Buscar frases com padrão "X da/do Y" (ex: "Gay da shoppe")
        phrase_pattern = r'\b([A-ZÀ-Ü][a-zà-ü]+)\s+(da|do)\s+([a-zà-ü]+)\b'
        phrase_matches = re.finditer(phrase_pattern, all_text)
        for match in phrase_matches:
            phrase = match.group(0)
            candidates.append(phrase)
            candidates.append(phrase)  # Peso extra

        # 4. NOVO: Buscar nomes mencionados em contexto de BBB/reality
        # Padrões como "o Arthur", "a Milena", "do Chai"
        reality_names_pattern = r'\b(?:o|a|do|da)\s+([A-ZÀ-Ü][a-zà-ü]+)\b'
        reality_matches = re.finditer(reality_names_pattern, all_text)
        for match in reality_matches:
            name = match.group(1)
            if name.lower() not in self.stop_words:
                # Peso extra para nomes em contexto de reality (repetir 3x)
                for _ in range(3):
                    candidates.append(name)

        return candidates

    def _rank_candidates(self, candidates: List[str], top_n: int) -> List[str]:
        """
        Ranqueia candidatos por frequência e relevância

        Args:
            candidates: Lista de termos candidatos
            top_n: Número de termos a retornar

        Returns:
            Lista dos top_n termos mais relevantes
        """
        # Contar frequência
        counter = Counter([c.lower() for c in candidates])

        # Ordenar por frequência (descendente)
        ranked = sorted(counter.items(), key=lambda x: x[1], reverse=True)

        # Retornar top N (título case)
        return [term.title() for term, _ in ranked[:top_n]]

    async def _search_duckduckgo(self, query: str) -> Dict:
        """
        Busca contexto sobre um termo no DuckDuckGo Instant Answer API

        Args:
            query: Termo a pesquisar

        Returns:
            Dict com contexto encontrado ou vazio se não encontrar
        """
        # Verificar cache primeiro
        cache_key = query.lower()
        if cache_key in self.cache:
            cached_entry = self.cache[cache_key]
            # Verificar TTL
            if datetime.now() - cached_entry['timestamp'] < self.cache_ttl:
                logger.debug(f"Cache hit para '{query}'")
                return {
                    'context': cached_entry['context'],
                    'cached': True
                }
            else:
                # Cache expirado, remover
                del self.cache[cache_key]

        # Melhorar query para pessoas (adicionar contexto BBB se for nome próprio)
        search_query = query
        # Se for um nome simples (palavra única capitalizada), adicionar "BBB" para contexto
        if query and query[0].isupper() and ' ' not in query and len(query) > 2:
            search_query = f"{query} BBB participante"
            logger.debug(f"Query expandida: '{query}' -> '{search_query}'")

        # Fazer pesquisa
        url = "https://api.duckduckgo.com/"
        params = {
            'q': search_query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    # Status 202 significa que a API está processando mas não retorna dados imediatamente
                    # Vamos aceitar apenas 200 como sucesso
                    if response.status != 200:
                        logger.debug(f"DuckDuckGo retornou status {response.status} para '{query}' (nenhum resultado disponível)")
                        return {}

                    try:
                        data = await response.json()
                    except Exception as e:
                        logger.debug(f"Erro ao parsear JSON para '{query}': {e}")
                        return {}

                    # Extrair contexto da resposta
                    context = None

                    # Tentar Abstract primeiro (melhor descrição)
                    if data.get('Abstract'):
                        context = data['Abstract']
                    # Depois Definition
                    elif data.get('Definition'):
                        context = data['Definition']
                    # Ou relacionados
                    elif data.get('RelatedTopics') and len(data['RelatedTopics']) > 0:
                        first_topic = data['RelatedTopics'][0]
                        if isinstance(first_topic, dict) and 'Text' in first_topic:
                            context = first_topic['Text']

                    if context:
                        # Limitar tamanho do contexto (max 300 chars)
                        if len(context) > 300:
                            context = context[:297] + "..."

                        # Adicionar ao cache
                        self.cache[cache_key] = {
                            'context': context,
                            'timestamp': datetime.now()
                        }

                        logger.debug(f"Contexto encontrado para '{query}': {context[:50]}...")
                        return {
                            'context': context,
                            'cached': False
                        }
                    else:
                        logger.debug(f"DuckDuckGo não retornou contexto para '{query}'")
                        return {}

        except asyncio.TimeoutError:
            logger.warning(f"Timeout ao buscar contexto para '{query}'")
            return {}
        except Exception as e:
            logger.error(f"Erro ao buscar contexto para '{query}': {e}")
            return {}

    def clear_cache(self):
        """Limpa o cache de contextos"""
        self.cache.clear()
        logger.info("Cache de contextos limpo")

    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        now = datetime.now()
        valid_entries = sum(1 for entry in self.cache.values()
                          if now - entry['timestamp'] < self.cache_ttl)

        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self.cache) - valid_entries
        }
