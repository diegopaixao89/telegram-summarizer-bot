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

        prompt = f"""Você é um assistente especializado em resumir conversas de grupos do Telegram.

Analise as seguintes {len(messages)} mensagens e forneça um resumo estruturado:

MENSAGENS:
{formatted_messages}

Por favor, forneça:

📋 RESUMO EXECUTIVO
(3-5 linhas resumindo o conteúdo geral)

💬 PRINCIPAIS TÓPICOS
(Liste os tópicos mais discutidos)

✅ DECISÕES E ACORDOS
(Se houver decisões ou acordos importantes)

❓ PERGUNTAS SEM RESPOSTA
(Perguntas que ficaram sem resposta clara)

🔗 LINKS E RECURSOS
(URLs ou recursos importantes compartilhados)

👥 PARTICIPANTES MAIS ATIVOS
(Quem mais contribuiu na conversa)

Mantenha o resumo conciso, objetivo e em português."""

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
                temperature=0.3,
                max_tokens=2000
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
