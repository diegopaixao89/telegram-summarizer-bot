"""
Processador de mídia para extrair contexto de imagens e links
"""
import logging
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from groq import AsyncGroq
import config
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

class MediaProcessor:
    def __init__(self):
        self.groq_client = AsyncGroq(api_key=config.GROQ_API_KEY)

    async def process_photo(self, photo_bytes: bytes, caption: str = None) -> str:
        """
        Processa imagem usando Groq Vision
        Retorna descrição da imagem
        """
        try:
            # Groq ainda não tem vision API pública, então vamos usar OCR básico
            # Por enquanto, retorna placeholder
            description = "📷 [Imagem enviada"
            if caption:
                description += f": {caption}"
            description += "]"

            logger.info(f"Imagem processada: {len(photo_bytes)} bytes")
            return description

        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            return "📷 [Imagem]"

    async def extract_link_info(self, url: str) -> str:
        """
        Extrai informações de um link (título, descrição)
        """
        try:
            # Timeout curto para não travar
            timeout = aiohttp.ClientTimeout(total=5)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; TelegramBot/1.0)'
                }

                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    if response.status != 200:
                        return f"🔗 [{self._extract_domain(url)}]"

                    # Ler apenas primeiros 100KB para não sobrecarregar
                    content = await response.text()
                    content = content[:100000]

                    soup = BeautifulSoup(content, 'html.parser')

                    # Tentar extrair título
                    title = None

                    # 1. OpenGraph title
                    og_title = soup.find('meta', property='og:title')
                    if og_title and og_title.get('content'):
                        title = og_title['content']

                    # 2. Twitter title
                    if not title:
                        tw_title = soup.find('meta', attrs={'name': 'twitter:title'})
                        if tw_title and tw_title.get('content'):
                            title = tw_title['content']

                    # 3. Title tag
                    if not title:
                        title_tag = soup.find('title')
                        if title_tag:
                            title = title_tag.text.strip()

                    # 4. Fallback para domínio
                    if not title:
                        title = self._extract_domain(url)

                    # Limitar tamanho do título
                    if len(title) > 100:
                        title = title[:97] + "..."

                    # Tentar extrair descrição
                    description = None
                    og_desc = soup.find('meta', property='og:description')
                    if og_desc and og_desc.get('content'):
                        description = og_desc['content']

                    if not description:
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        if meta_desc and meta_desc.get('content'):
                            description = meta_desc['content']

                    # Formatar resultado
                    result = f"🔗 Link: {title}"
                    if description and len(description) > 20:
                        desc_short = description[:150]
                        if len(description) > 150:
                            desc_short += "..."
                        result += f" - {desc_short}"

                    logger.info(f"Link processado: {url} -> {title}")
                    return result

        except asyncio.TimeoutError:
            logger.warning(f"Timeout ao processar link: {url}")
            return f"🔗 [{self._extract_domain(url)}]"
        except Exception as e:
            logger.error(f"Erro ao processar link {url}: {e}")
            return f"🔗 [{self._extract_domain(url)}]"

    def _extract_domain(self, url: str) -> str:
        """Extrai domínio de uma URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remover www.
            domain = domain.replace('www.', '')
            return domain
        except:
            return url[:50]

    def extract_urls_from_text(self, text: str) -> list:
        """
        Extrai todas as URLs de um texto
        """
        if not text:
            return []

        # Regex para encontrar URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)

        return urls

    async def enrich_message_text(self, text: str) -> str:
        """
        Enriquece texto extraindo informações de links
        """
        if not text:
            return text

        urls = self.extract_urls_from_text(text)

        if not urls:
            return text

        # Processar apenas primeiros 3 links para não sobrecarregar
        enriched_text = text
        for url in urls[:3]:
            try:
                link_info = await self.extract_link_info(url)
                # Substituir URL pelo info do link
                enriched_text = enriched_text.replace(url, link_info)
            except Exception as e:
                logger.error(f"Erro ao enriquecer link {url}: {e}")
                continue

        return enriched_text
