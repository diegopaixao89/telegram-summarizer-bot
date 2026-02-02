import logging
from typing import List, Dict
from groq import Groq
import config
from context_enricher import ContextEnricher

logger = logging.getLogger(__name__)


class Summarizer:
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"  # Modelo rápido e gratuito
        self.context_enricher = ContextEnricher()
        logger.info("✨ Summarizer inicializado com Context Enricher v1.4.0")

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

        # Se tem muitas mensagens, divide em blocos
        if len(messages) > 800:
            return await self._summarize_in_chunks(messages)

        # Enriquecer contexto cultural (aumentado para 10 para incluir mais nomes de pessoas)
        cultural_context = await self.context_enricher.enrich_context(messages, max_searches=10)

        formatted_messages = self._format_messages(messages)
        top_users_context = self._get_top_users_with_context(messages, top_n=5)

        prompt = f"""Você é um assistente especializado em resumir conversas de grupos do Telegram de forma profissional e EXTREMAMENTE DETALHADA.

REGRAS CRÍTICAS:
- SEMPRE mencione nomes específicos de pessoas, programas, filmes, séries, empresas
- NUNCA use termos genéricos como "programas de TV", "atores", "celebridades" sem especificar QUEM ou O QUÊ
- Se mencionarem um programa, escreva o NOME COMPLETO do programa
- Se mencionarem atores/participantes, escreva os NOMES e use o CONTEXTO fornecido para explicar quem são
- Se mencionarem produtos/marcas, escreva os NOMES das marcas
- Cite frases exatas quando relevante (entre aspas)
- Seja ESPECÍFICO, CONCRETO e DETALHADO
- USE O CONTEXTO CULTURAL fornecido abaixo para adicionar informações sobre pessoas, programas e termos mencionados

Analise as seguintes {len(messages)} mensagens e forneça um resumo estruturado e elaborado:

MENSAGENS:
{formatted_messages}

TOP USUÁRIOS E SUAS MENSAGENS (para contexto):
{top_users_context}
{cultural_context}
Por favor, forneça um resumo ELABORADO e DETALHADO seguindo EXATAMENTE esta estrutura:

📋 RESUMO EXECUTIVO
Escreva um parágrafo bem elaborado (7-10 linhas) que sintetize o contexto geral da conversa com DETALHES ESPECÍFICOS.
Mencione nomes, títulos, contextos concretos. NUNCA generalize sem especificar.
Exemplo BOM: "O grupo discutiu intensamente sobre BBB26, focando nas atitudes de Milena e Chai..."
Exemplo RUIM: "O grupo discutiu sobre programas de TV..."

🔥 TOP 5 ASSUNTOS MAIS DISCUTIDOS
Liste os 5 tópicos que mais geraram engajamento com MÁXIMO DETALHAMENTO:
1. [Assunto ESPECÍFICO com nomes próprios] - Explique em detalhes QUEM, O QUÊ, ONDE, POR QUÊ foi discutido. Cite exemplos concretos.
2. [Segundo assunto ESPECÍFICO] - Detalhes completos com nomes e contexto
3. [Terceiro assunto ESPECÍFICO] - Contexto detalhado
4. [Quarto assunto ESPECÍFICO] - Pontos principais com detalhes
5. [Quinto assunto ESPECÍFICO] - Informações concretas

💡 INSIGHTS E DESTAQUES
Identifique insights importantes e frases marcantes COM CITAÇÕES EXATAS (entre aspas).
Mencione QUEM disse, SOBRE O QUÊ especificamente. Seja MUITO específico.

👥 TOP 5 MEMBROS MAIS ATIVOS
IMPORTANTE: Use EXATAMENTE este formato para cada membro:
1. @username (X msgs) - Frase resumindo sobre o que ele/ela falou
2. @username (X msgs) - Frase resumindo sobre o que ele/ela falou
3. @username (X msgs) - Frase resumindo sobre o que ele/ela falou
4. @username (X msgs) - Frase resumindo sobre o que ele/ela falou
5. @username (X msgs) - Frase resumindo sobre o que ele/ela falou

Exemplo:
1. @joao (45 msgs) - Discutindo sobre prazos do projeto e organização da sprint
2. @maria (32 msgs) - Compartilhando memes e links sobre tecnologia

Para cada membro, analise suas mensagens e crie UMA FRASE (máx 15 palavras) que resuma os principais tópicos que ele discutiu.

🔗 LINKS E RECURSOS RELEVANTES
Liste APENAS os links mais importantes e relevantes compartilhados, com breve descrição.
Inclua somente links que agregam valor real à discussão.
Se não houver links relevantes, escreva "Nenhum link relevante foi compartilhado."

Seja detalhado, elaborado e profissional. Use linguagem clara e bem estruturada."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em resumir conversas de grupos com MÁXIMO DETALHAMENTO. SEMPRE mencione nomes específicos, títulos completos, citações exatas. NUNCA generalize sem especificar detalhes concretos."
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
            logger.info(f"Resumo gerado com sucesso para {len(messages)} mensagens")
            return summary

        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {e}")
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
            response = self.client.chat.completions.create(
                model=self.model,
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
        chunk_size = 400  # Mensagens por bloco
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
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=800
                )
                chunk_summaries.append(f"**Bloco {i}:** {response.choices[0].message.content}")
                logger.info(f"Bloco {i}/{len(chunks)} resumido")
            except Exception as e:
                logger.error(f"Erro ao resumir bloco {i}: {e}")
                chunk_summaries.append(f"**Bloco {i}:** Erro ao processar")

        # Resumo final consolidado
        combined = "\n\n".join(chunk_summaries)
        top_users_context = self._get_top_users_with_context(messages, top_n=5)

        final_prompt = f"""Analise as conversas e faça um resumo em tom descontraído e natural, como se estivesse contando pra um amigo.

IMPORTANTE: Seja ESPECÍFICO! Mencione nomes de pessoas, programas, filmes, séries, marcas. NUNCA generalize dizendo apenas "programas de TV" ou "atores" sem especificar QUAIS.

{combined}

TOP USUÁRIOS E SUAS MENSAGENS (para contexto):
{top_users_context}
{cultural_context}
Use linguagem informal mas SEM EXAGERAR. Seja natural, use algumas gírias quando fizer sentido, mas mantenha a clareza.
Escreva de forma leve e fluida, como uma conversa normal. SEMPRE com detalhes específicos.

📋 O QUE ROLOU
(7-10 linhas contando de forma tranquila o que aconteceu com DETALHES ESPECÍFICOS. Mencione nomes, títulos, contextos concretos. Ex: "O grupo tava discutindo bastante sobre BBB26, principalmente sobre as atitudes da Milena e do Chai...")

🔥 TOP 5 ASSUNTOS
CADA assunto deve ter DETALHES ESPECÍFICOS com nomes próprios:
1. [Assunto ESPECÍFICO com nomes] - Explique o que foi discutido com detalhes concretos
2. [Assunto ESPECÍFICO] - Principais pontos com nomes e contexto
3. [Assunto ESPECÍFICO] - Detalhes completos
4. [Assunto ESPECÍFICO] - Informações concretas
5. [Assunto ESPECÍFICO] - Contexto detalhado

💡 DESTAQUES
Frases interessantes COM CITAÇÕES EXATAS (entre aspas) e mencionando QUEM disse. Seja específico sobre O QUÊ foi dito.

👥 TOP 5 MEMBROS MAIS ATIVOS
IMPORTANTE: Use EXATAMENTE este formato:
1. @username (X msgs) - Frase resumindo sobre o que falou
2. @username (X msgs) - Frase resumindo sobre o que falou
3. @username (X msgs) - Frase resumindo sobre o que falou
4. @username (X msgs) - Frase resumindo sobre o que falou
5. @username (X msgs) - Frase resumindo sobre o que falou

Exemplo:
1. @joao (45 msgs) - Falando sobre prazos e organização do projeto
2. @maria (32 msgs) - Compartilhando memes e links sobre tecnologia

🔗 LINKS RELEVANTES
Se tiver algum link importante, lista aqui com descrição breve.

---
Total: {len(messages)} mensagens analisadas

Mantenha o tom leve e natural, mas sem forçar muito a barra. Seja você mesmo contando pra um amigo."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": final_prompt}],
                temperature=0.3,
                max_tokens=5000
            )
            logger.info(f"Resumo final gerado para {len(messages)} mensagens")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao gerar resumo final: {e}")
            return f"❌ Erro ao gerar resumo final: {str(e)}\n\nResumos parciais:\n{combined}"
