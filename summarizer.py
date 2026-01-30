import logging
from typing import List, Dict
from groq import Groq
import config

logger = logging.getLogger(__name__)


class Summarizer:
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"  # Modelo rápido e gratuito

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

    async def summarize(self, messages: List[Dict]) -> str:
        """Gera resumo das mensagens usando Groq"""
        if not messages:
            return "Nenhuma mensagem para resumir."

        # Se tem muitas mensagens, divide em blocos
        if len(messages) > 800:
            return await self._summarize_in_chunks(messages)

        formatted_messages = self._format_messages(messages)

        prompt = f"""Você é um assistente especializado em resumir conversas de grupos do Telegram de forma profissional e detalhada.

Analise as seguintes {len(messages)} mensagens e forneça um resumo estruturado e elaborado:

MENSAGENS:
{formatted_messages}

Por favor, forneça um resumo ELABORADO seguindo EXATAMENTE esta estrutura:

📋 RESUMO EXECUTIVO
Escreva um parágrafo bem elaborado (5-7 linhas) que sintetize o contexto geral da conversa,
destacando o clima, principais discussões e conclusões gerais. Seja descritivo e contextual.

🔥 TOP 5 ASSUNTOS MAIS DISCUTIDOS
Liste os 5 tópicos que mais geraram engajamento e discussão, ordenados por relevância:
1. [Assunto mais falado] - Breve contexto e principais pontos discutidos
2. [Segundo assunto] - Contexto e pontos principais
3. [Terceiro assunto] - Contexto e pontos principais
4. [Quarto assunto] - Contexto e pontos principais
5. [Quinto assunto] - Contexto e pontos principais

💡 INSIGHTS E DESTAQUES
Identifique insights importantes, frases marcantes, opiniões relevantes ou informações valiosas
compartilhadas na conversa. Seja específico e cite exemplos quando relevante.

👥 MEMBROS MAIS ATIVOS
Identifique os 3-5 membros do grupo que:
- Mais enviaram mensagens (volume)
- Mais participaram ativamente das discussões e pautas (engajamento e relevância)
Liste o nome de cada membro e indique o tipo de participação (ex: "muito ativo nas discussões", "trouxe informações importantes", "engajou em vários tópicos").

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
                        "content": "Você é um assistente especializado em resumir conversas de grupos, identificando pontos-chave e informações importantes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=4500
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

        final_prompt = f"""Você é um amigo fofoqueiro contando as novidades do grupo de forma descontraída e divertida!

Analise estas conversas e conte tudo que rolou como se você fosse um amigo contando as fofocas mais cabeludas:

{combined}

Use linguagem SUPER COLOQUIAL, informal e natural! Fale como as pessoas do grupo falam, use gírias, expressões típicas.
Seja animado, divertido e empolgado ao contar. Imagine que você está no bar contando pro seu amigo o que rolou no grupo.

🍿 O QUE ROLOU
(5-7 linhas contando de forma bem descontraída o que aconteceu. Ex: "Cara, o grupo tava FERVEEEENDO hoje! Olha só...")

🔥 AS 5 TRETAS/ASSUNTOS MAIS BOMBADOS
(Conte cada assunto de forma animada. Ex: "1. Mano, o pessoal SURTOU com...")
1. [Assunto] - Conta aí o que rolou, coloquial
2. [Assunto] - O que galera falou
3. [Assunto] - Continua...
4. [Assunto]
5. [Assunto]

💎 AS MELHORES DO DIA
(Frases marcantes, opiniões polêmicas, informações bombadas. Conta com entusiasmo!)

👥 QUEM MAIS FERVEU NO GRUPO
(Lista os 3-5 membros mais ativos, descontraído. Ex: "Fulano não parou de falar, tava em TODAS!")

🔗 LINKS RELEVANTES
(Se tiver link importante, lista. Senão: "Nada de link relevante hoje")

---
Foram {len(messages)} mensagens! O grupo tava ON FIRE! 🔥

IMPORTANTE: Use gírias, seja informal, coloquial e divertido! Fale como um amigo contando fofoca mesmo!"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": final_prompt}],
                temperature=0.4,
                max_tokens=3500
            )
            logger.info(f"Resumo final gerado para {len(messages)} mensagens")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao gerar resumo final: {e}")
            return f"❌ Erro ao gerar resumo final: {str(e)}\n\nResumos parciais:\n{combined}"
