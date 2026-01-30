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

✅ DECISÕES E ACORDOS
Liste decisões tomadas, acordos firmados ou ações definidas durante a conversa.
Se não houver, escreva "Nenhuma decisão formal foi tomada."

❓ PERGUNTAS E DÚVIDAS EM ABERTO
Liste perguntas importantes que ficaram sem resposta ou dúvidas não resolvidas.
Se não houver, escreva "Todas as perguntas foram respondidas."

👥 PARTICIPANTES MAIS ATIVOS
Liste os 3-5 participantes que mais contribuíram, mencionando brevemente o tipo de contribuição.

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
                max_tokens=3500
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
