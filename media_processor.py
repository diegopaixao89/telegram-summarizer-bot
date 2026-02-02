"""
Processador de mídia para extrair contexto de imagens e links
"""
import logging
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import config
import base64
from groq import Groq

logger = logging.getLogger(__name__)

class MediaProcessor:
    def __init__(self):
        # Usar Groq Vision (GRATUITO!) para análise de imagens
        self.groq_client = Groq(api_key=config.GROQ_API_KEY)
        self.vision_model = "llama-3.2-11b-vision-preview"  # Modelo de visão gratuito do Groq
        logger.info("Groq Vision API inicializada para análise de imagens (GRATUITO)")

    async def process_photo(self, photo_bytes: bytes, caption: str = None) -> str:
        """
        Processa imagem usando Groq Vision API (GRATUITO!)
        Retorna descrição detalhada da imagem
        """
        try:
            # Converter imagem para base64
            image_base64 = base64.b64encode(photo_bytes).decode('utf-8')

            # Determinar tipo de imagem (assumir JPEG por padrão)
            media_type = "image/jpeg"
            if photo_bytes[:4] == b'\x89PNG':
                media_type = "image/png"
            elif photo_bytes[:3] == b'GIF':
                media_type = "image/gif"
            elif photo_bytes[:4] == b'RIFF':
                media_type = "image/webp"

            # Usar Groq Vision para analisar a imagem
            prompt = """Analise esta imagem em português e descreva:
1. O que você vê (pessoas, objetos, texto, memes)
2. Contexto (é um print de tweet? post? meme? foto? notícia?)
3. Se há texto na imagem, transcreva-o EXATAMENTE
4. Qual o assunto principal e tema
5. Se for relacionado a BBB ou reality show, mencione

Seja conciso mas específico (max 150 palavras)."""

            # Criar data URL para Groq
            image_url = f"data:{media_type};base64,{image_base64}"

            response = self.groq_client.chat.completions.create(
                model=self.vision_model,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }],
                temperature=0.3,
                max_tokens=400
            )

            # Extrair descrição
            image_description = response.choices[0].message.content

            # Formatar resultado
            result = f"📷 [Imagem: {image_description}"
            if caption:
                result += f" | Legenda: {caption}"
            result += "]"

            logger.info(f"Imagem analisada com Groq Vision (gratuito): {len(photo_bytes)} bytes")
            return result

        except Exception as e:
            logger.error(f"Erro ao processar imagem com Groq Vision: {e}")
            # Fallback: retornar apenas caption
            description = "📷 [Imagem"
            if caption:
                description += f": {caption}"
            description += "]"
            return description

    async def extract_link_info(self, url: str, extract_content: bool = True) -> str:
        """
        Extrai informações de um link (título, descrição e conteúdo principal)

        Args:
            url: URL para extrair
            extract_content: Se True, extrai também o conteúdo principal da página
        """
        try:
            # Timeout um pouco maior para extrair conteúdo
            timeout = aiohttp.ClientTimeout(total=10)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    if response.status != 200:
                        return f"🔗 [{self._extract_domain(url)}]"

                    # Ler conteúdo (limite de 200KB)
                    content = await response.text()
                    content = content[:200000]

                    soup = BeautifulSoup(content, 'html.parser')

                    # Extrair título
                    title = None
                    og_title = soup.find('meta', property='og:title')
                    if og_title and og_title.get('content'):
                        title = og_title['content']

                    if not title:
                        tw_title = soup.find('meta', attrs={'name': 'twitter:title'})
                        if tw_title and tw_title.get('content'):
                            title = tw_title['content']

                    if not title:
                        title_tag = soup.find('title')
                        if title_tag:
                            title = title_tag.text.strip()

                    if not title:
                        title = self._extract_domain(url)

                    if len(title) > 150:
                        title = title[:147] + "..."

                    # Extrair descrição
                    description = None
                    og_desc = soup.find('meta', property='og:description')
                    if og_desc and og_desc.get('content'):
                        description = og_desc['content']

                    if not description:
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        if meta_desc and meta_desc.get('content'):
                            description = meta_desc['content']

                    # NOVO: Extrair conteúdo principal se solicitado
                    main_content = None
                    if extract_content:
                        # Tentar encontrar conteúdo principal
                        # Priorizar tags article, main, ou divs com classes típicas de conteúdo
                        content_candidates = []

                        # 1. Tag article
                        articles = soup.find_all('article')
                        for article in articles:
                            text = article.get_text(separator=' ', strip=True)
                            if len(text) > 100:
                                content_candidates.append(text)

                        # 2. Tag main
                        if not content_candidates:
                            main_tag = soup.find('main')
                            if main_tag:
                                text = main_tag.get_text(separator=' ', strip=True)
                                if len(text) > 100:
                                    content_candidates.append(text)

                        # 3. Divs com classes comuns de conteúdo
                        if not content_candidates:
                            content_divs = soup.find_all('div', class_=re.compile(r'(content|post|article|entry|body)', re.I))
                            for div in content_divs[:3]:  # Apenas primeiras 3
                                text = div.get_text(separator=' ', strip=True)
                                if len(text) > 100:
                                    content_candidates.append(text)

                        # 4. Todos os parágrafos como fallback
                        if not content_candidates:
                            paragraphs = soup.find_all('p')
                            text = ' '.join([p.get_text(strip=True) for p in paragraphs[:10]])
                            if len(text) > 100:
                                content_candidates.append(text)

                        # Pegar o maior conteúdo encontrado
                        if content_candidates:
                            main_content = max(content_candidates, key=len)
                            # Limitar a 800 caracteres
                            if len(main_content) > 800:
                                main_content = main_content[:797] + "..."

                    # Formatar resultado
                    result = f"🔗 Link: {title}"

                    if description and len(description) > 20:
                        desc_short = description[:200]
                        if len(description) > 200:
                            desc_short += "..."
                        result += f"\n   Descrição: {desc_short}"

                    if main_content:
                        result += f"\n   Conteúdo: {main_content}"

                    logger.info(f"Link processado: {url} -> {title} (conteúdo: {len(main_content) if main_content else 0} chars)")
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
