import logging
from typing import List, Dict
from groq import Groq
import google.generativeai as genai
import config
from context_enricher import ContextEnricher
from media_processor import MediaProcessor

logger = logging.getLogger(__name__)


class Summarizer:
    def __init__(self):
        # Groq para fallback e análise de imagens
        self.groq_client = Groq(api_key=config.GROQ_API_KEY)
        self.groq_model = "llama-3.3-70b-versatile"

        # Google Gemini como modelo principal (melhor qualidade, gratuito)
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("✨ Summarizer inicializado com Google Gemini 1.5 Flash (principal) + Groq (fallback)")
        else:
            self.gemini_model = None
            logger.warning("⚠️  GEMINI_API_KEY não configurada, usando apenas Groq")

        self.context_enricher = ContextEnricher()
        self.media_processor = MediaProcessor()
        logger.info("✨ Context Enricher v1.4.0 + Media Processor ativos")

    def _format_messages(self, messages: List[Dict]) -> str:
        """Formata mensagens para o prompt"""
        formatted = []
        for msg in messages:
            username = msg.get('username') or msg.get('first_name') or 'Usuário'
            text = msg.get('text', '')
            timestamp = msg.get('timestamp', '')

            if text:
                formatted.append(f"[{timestamp}] {username}: {text}")

        return "\n".join(formatted)

    def _get_top_users_with_context(self, messages: List[Dict], top_n: int = 5) -> str:
        """Agrupa mensagens por usuário e retorna TOP N com contexto"""
        user_messages = {}

        for msg in messages:
            username = msg.get('username')
            first_name = msg.get('first_name') or 'Usuário'
            text = msg.get('text', '')

            if not text:
                continue

            # Usar username com @ se disponível, senão usar first_name
            user_key = f"@{username}" if username else first_name

            if user_key not in user_messages:
                user_messages[user_key] = []
            user_messages[user_key].append(text)

        # Ordenar por número de mensagens
        sorted_users = sorted(user_messages.items(), key=lambda x: len(x[1]), reverse=True)[:top_n]

        # Formatar para o prompt
        result = []
        for i, (user, msgs) in enumerate(sorted_users, 1):
            msg_count = len(msgs)
            # Pegar uma amostra das mensagens do usuário (max 10 para não sobrecarregar)
            sample_msgs = msgs[:10] if len(msgs) > 10 else msgs
            msgs_text = " | ".join(sample_msgs)
            result.append(f"{i}. {user} ({msg_count} msgs): {msgs_text[:300]}...")

        return "\n".join(result)

    async def summarize(self, messages: List[Dict]) -> str:
        """Gera resumo das mensagens usando Groq"""
        if not messages:
            return "Nenhuma mensagem para resumir."

        # Se tem muitas mensagens, divide em blocos para evitar limite de tokens
        if len(messages) > 250:
            return await self._summarize_in_chunks(messages)

        # Enriquecer contexto cultural (aumentado para 10 para incluir mais nomes de pessoas)
        cultural_context = await self.context_enricher.enrich_context(messages, max_searches=10)

        formatted_messages = self._format_messages(messages)
        top_users_context = self._get_top_users_with_context(messages, top_n=5)

        prompt = f"""Analise estas {len(messages)} mensagens de grupo e crie um resumo jornalístico profissional.

REGRAS CRÍTICAS:
1. NÃO REPITA informações entre seções - cada seção deve ter conteúdo ÚNICO
2. Use linguagem direta e natural - evite "indicando", "sugerindo", "demonstrando"
3. SEMPRE contextualize pessoas mencionadas usando links/imagens compartilhados
4. Tom profissional, sem introduções informais como "E aí, você não acompanhou"
5. FOQUE EM EVENTOS RECENTES - Se algo é mencionado repetidamente mas parece antigo, indique isso ou omita
6. VERIFIQUE COERÊNCIA - Não invente informações, relate apenas o que está claro nas mensagens

PERÍODO: Mensagens recentes (últimas 24h prioritariamente)

MENSAGENS (com timestamp):
{formatted_messages}

TOP USUÁRIOS:
{top_users_context}

CONTEXTO ADICIONAL:
{cultural_context}

---
ESTRUTURA DO RESUMO:

📋 O QUE ACONTECEU
Escreva 2-3 parágrafos objetivos respondendo: QUEM disse/fez O QUÊ e POR QUÊ importa.
- Contextualize nomes próprios (ex: "Breno, eliminado do BBB26...")
- Conecte informações de links/imagens para dar contexto
- Seja direto: "Fulano criticou X" em vez de "O grupo expressou sentimentos sobre X"

🔥 PRINCIPAIS TÓPICOS
Liste 3-5 tópicos NÃO mencionados acima, cada um com 1-2 frases explicando:
- O que foi discutido
- Por que foi relevante
SEM repetir informações da seção anterior.

💡 FRASES MARCANTES
Máximo 3-5 citações textuais importantes:
"Citação exata" - @username (contexto em 3-5 palavras)

👥 TOP 5 ATIVOS
1. @username (X msgs) - Resumo dos tópicos que discutiu (máx 12 palavras)
2. @username (X msgs) - Resumo dos tópicos que discutiu (máx 12 palavras)
3. @username (X msgs) - Resumo dos tópicos que discutiu (máx 12 palavras)
4. @username (X msgs) - Resumo dos tópicos que discutiu (máx 12 palavras)
5. @username (X msgs) - Resumo dos tópicos que discutiu (máx 12 palavras)

🔗 LINKS RELEVANTES
Liste apenas links importantes com descrição breve. Se não houver, omita esta seção."""

        try:
            # Tentar com Gemini primeiro (melhor qualidade)
            if self.gemini_model:
                try:
                    logger.info("Gerando resumo com Google Gemini 1.5 Flash...")
                    full_prompt = f"""Você é um jornalista profissional criando resumos objetivos de conversas.

ESTILO:
- Direto e sintético - sem redundâncias
- Tom profissional, não coloquial demais
- Contextualize nomes usando informações disponíveis
- Cada seção deve ter informação NOVA, não repetir o que já foi dito
- Evite termos vagos: seja específico com nomes, datas, eventos

---

{prompt}"""

                    response = self.gemini_model.generate_content(
                        full_prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.3,
                            max_output_tokens=6000,
                        )
                    )

                    summary = response.text
                    logger.info(f"✅ Resumo gerado com Gemini para {len(messages)} mensagens")
                    return summary

                except Exception as e:
                    logger.warning(f"⚠️  Erro com Gemini, tentando Groq: {e}")
                    # Fallback para Groq
                    pass

            # Fallback: usar Groq
            logger.info("Gerando resumo com Groq (fallback)...")
            response = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {
                        "role": "system",
                        "content": """Você é um jornalista profissional criando resumos objetivos de conversas.

ESTILO:
- Direto e sintético - sem redundâncias
- Tom profissional, não coloquial demais
- Contextualize nomes usando informações disponíveis
- Cada seção deve ter informação NOVA, não repetir o que já foi dito
- Evite termos vagos: seja específico com nomes, datas, eventos"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=6000
            )

            summary = response.choices[0].message.content
            logger.info(f"✅ Resumo gerado com Groq para {len(messages)} mensagens")
            return summary

        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo: {e}")
            return f"❌ Erro ao gerar resumo: {str(e)}"

    async def quick_summary(self, messages: List[Dict]) -> str:
        """Gera um resumo rápido e curto"""
        if not messages:
            return "Nenhuma mensagem para resumir."

        formatted_messages = self._format_messages(messages)

        prompt = f"""Resuma brevemente (máximo 5 linhas) as seguintes {len(messages)} mensagens de grupo:

{formatted_messages}

Foque apenas nos pontos mais importantes."""

        try:
            # Tentar Gemini primeiro
            if self.gemini_model:
                try:
                    response = self.gemini_model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.3,
                            max_output_tokens=500,
                        )
                    )
                    return response.text
                except Exception as e:
                    logger.warning(f"Erro com Gemini no quick_summary, usando Groq: {e}")

            # Fallback Groq
            response = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Erro ao gerar resumo rápido: {e}")
            return f"❌ Erro: {str(e)}"

    async def _summarize_in_chunks(self, messages: List[Dict]) -> str:
        """Resume mensagens em blocos para evitar limite de tokens"""
        chunk_size = 200  # Mensagens por bloco (reduzido para evitar limite Groq)
        chunks = [messages[i:i + chunk_size] for i in range(0, len(messages), chunk_size)]

        logger.info(f"Dividindo {len(messages)} mensagens em {len(chunks)} blocos")

        # Enriquecer contexto cultural (uma vez para todas as mensagens)
        cultural_context = await self.context_enricher.enrich_context(messages, max_searches=10)

        # Resumir cada bloco
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            formatted = self._format_messages(chunk)

            prompt = f"""Resuma este bloco de {len(chunk)} mensagens de grupo, focando em:
- Principais tópicos discutidos
- Pontos importantes
- Decisões ou acordos

MENSAGENS:
{formatted}

Seja conciso mas completo."""

            try:
                # Tentar Gemini primeiro
                if self.gemini_model:
                    try:
                        response = self.gemini_model.generate_content(
                            prompt,
                            generation_config=genai.types.GenerationConfig(
                                temperature=0.3,
                                max_output_tokens=800,
                            )
                        )
                        chunk_summaries.append(f"**Bloco {i}:** {response.text}")
                        logger.info(f"Bloco {i}/{len(chunks)} resumido com Gemini")
                        continue
                    except Exception as e:
                        logger.warning(f"Erro com Gemini no bloco {i}, usando Groq: {e}")

                # Fallback Groq
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=800
                )
                chunk_summaries.append(f"**Bloco {i}:** {response.choices[0].message.content}")
                logger.info(f"Bloco {i}/{len(chunks)} resumido com Groq")
            except Exception as e:
                logger.error(f"Erro ao resumir bloco {i}: {e}")
                chunk_summaries.append(f"**Bloco {i}:** Erro ao processar")

        # Resumo final consolidado
        combined = "\n\n".join(chunk_summaries)
        top_users_context = self._get_top_users_with_context(messages, top_n=5)

        final_prompt = f"""Consolide estes resumos parciais em um resumo final objetivo e profissional.

IMPORTANTE:
- NÃO repita informações entre seções
- Seja específico com nomes e eventos
- Contextualize pessoas mencionadas
- Tom profissional, direto

RESUMOS PARCIAIS:
{combined}

CONTEXTO:
{top_users_context}
{cultural_context}

---
ESTRUTURA:

📋 O QUE ACONTECEU
2-3 parágrafos objetivos: QUEM fez/disse O QUÊ e POR QUÊ importa.
Contextualize nomes próprios usando informações disponíveis.

🔥 PRINCIPAIS TÓPICOS
3-5 tópicos NÃO mencionados acima (1-2 frases cada).

💡 FRASES MARCANTES
3-5 citações importantes: "Citação" - @user (contexto breve)

👥 TOP 5 ATIVOS
1. @username (X msgs) - Tópicos discutidos (máx 12 palavras)
2. @username (X msgs) - Tópicos discutidos (máx 12 palavras)
3. @username (X msgs) - Tópicos discutidos (máx 12 palavras)
4. @username (X msgs) - Tópicos discutidos (máx 12 palavras)
5. @username (X msgs) - Tópicos discutidos (máx 12 palavras)

🔗 LINKS RELEVANTES
Links importantes com descrição. Omita se não houver.

---
Total: {len(messages)} mensagens"""

        try:
            # Tentar Gemini primeiro
            if self.gemini_model:
                try:
                    response = self.gemini_model.generate_content(
                        final_prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.3,
                            max_output_tokens=5000,
                        )
                    )
                    logger.info(f"✅ Resumo final gerado com Gemini para {len(messages)} mensagens")
                    return response.text
                except Exception as e:
                    logger.warning(f"⚠️  Erro com Gemini no resumo final, usando Groq: {e}")

            # Fallback Groq
            response = self.groq_client.chat.completions.create(
                model=self.groq_model,
                messages=[{"role": "user", "content": final_prompt}],
                temperature=0.3,
                max_tokens=5000
            )
            logger.info(f"✅ Resumo final gerado com Groq para {len(messages)} mensagens")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo final: {e}")
            return f"❌ Erro ao gerar resumo final: {str(e)}\n\nResumos parciais:\n{combined}"
