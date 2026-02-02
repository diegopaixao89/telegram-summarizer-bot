import logging
from typing import List, Dict
from groq import Groq
import config
from context_enricher import ContextEnricher
from media_processor import MediaProcessor

logger = logging.getLogger(__name__)


class Summarizer:
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"  # Modelo rápido e gratuito
        self.context_enricher = ContextEnricher()
        self.media_processor = MediaProcessor()
        logger.info("✨ Summarizer inicializado com Context Enricher v1.4.0 + Media Processor")

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

        prompt = f"""Você é um JORNALISTA ESPECIALIZADO em resumir conversas de grupos.

PRINCÍPIOS JORNALÍSTICOS FUNDAMENTAIS:

1. CONTEXTO É REI
   - SEMPRE explique quem são as pessoas mencionadas
   - Se não souber quem é alguém (ex: "Sarah"), use os links e contexto para descobrir
   - Conecte os pontos: se falaram de Sarah e compartilharam link do Twitter, o link provavelmente explica quem é Sarah!

2. LINGUAGEM NATURAL (NÃO ROBÓTICA)
   - Escreva como se estivesse CONTANDO uma história para um amigo
   - EVITE: "indicando", "sugerindo", "demonstrando", "expressando"
   - USE: verbos diretos e linguagem fluida
   - Exemplo RUIM: "A discussão sugere um possível conflito"
   - Exemplo BOM: "Rolou um conflito entre..."

3. PIRÂMIDE INVERTIDA
   - Comece com o MAIS IMPORTANTE
   - Responda: QUEM fez O QUÊ? POR QUÊ? QUANDO? COMO?
   - Depois entre nos detalhes

4. ELIMINE REDUNDÂNCIAS
   - NUNCA repita a mesma informação
   - Se já disse algo no Resumo Executivo, não repita nos Assuntos
   - Cada seção deve trazer informação NOVA

5. INVESTIGAÇÃO
   - Use os LINKS compartilhados para entender o contexto
   - Use as IMAGENS para entender sobre o que estão falando
   - Conecte as informações disponíveis

Analise as seguintes {len(messages)} mensagens e forneça um resumo estruturado e elaborado:

MENSAGENS:
{formatted_messages}

TOP USUÁRIOS E SUAS MENSAGENS (para contexto):
{top_users_context}
{cultural_context}
Por favor, forneça um resumo seguindo EXATAMENTE esta estrutura:

📋 O QUE ACONTECEU
Em 2-3 parágrafos NATURAIS, conte a história do que aconteceu.
- Comece respondendo: QUEM fez/disse O QUÊ?
- Por que isso importa? Qual o contexto?
- Se mencionar nomes (Sarah, Arthur, etc), EXPLIQUE quem são usando links/imagens compartilhados
- Escreva fluido, SEM palavras como "indicando", "sugerindo", "demonstrando"
- Se faltou contexto para entender algo, DIGA isso claramente

Exemplo BOM:
"Rolou uma treta pesada sobre a Sarah do BBB26. A @brubscansada tava pistola, dizendo que a Sarah fica analisando todo mundo. A Pati foi direto ao ponto: chamou a Sarah de otária e disse que quer ver a Ana acabar com ela no jogo."

Exemplo RUIM:
"O grupo expressou sentimentos negativos em relação a Sarah, indicando um possível conflito."

🔥 PRINCIPAIS TÓPICOS
Liste APENAS os tópicos DIFERENTES do que já foi dito acima.
Para CADA tópico, conte de forma NATURAL e FLUIDA:
- Use linguagem coloquial mas clara
- Conecte com informações dos links/imagens
- Explique POR QUÊ isso foi discutido

💡 FRASES QUE MARCARAM
APENAS citações EXATAS que foram importantes.
Formato: "Frase exata" - @username sobre [contexto específico]

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
                        "content": """Você é um JORNALISTA experiente resumindo conversas de grupo.

ESTILO DE ESCRITA:
- Natural e fluido, como se estivesse contando para um amigo
- Linguagem clara e direta, SEM termos robóticos
- Conecte informações dos links/imagens para dar contexto
- EXPLIQUE quem são as pessoas mencionadas
- EVITE: "indicando", "sugerindo", "demonstrando", "expressando"
- USE: verbos diretos e linguagem coloquial mas profissional

Você é um contador de histórias, não um robô."""
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

        final_prompt = f"""Você é um JORNALISTA contando o que rolou no grupo de forma natural e clara.

ESTILO: Converse com o leitor como se estivesse explicando para um amigo que não leu as mensagens.

REGRAS DE OURO:
1. Use os LINKS e IMAGENS para entender o contexto
2. EXPLIQUE quem são as pessoas mencionadas
3. Conecte os pontos - se alguém compartilhou link sobre Sarah, use isso para explicar quem é Sarah
4. Linguagem NATURAL - nada de "indicando", "sugerindo", "demonstrando"
5. Seja ESPECÍFICO mas FLUIDO

{combined}

TOP USUÁRIOS E SUAS MENSAGENS (para contexto):
{top_users_context}
{cultural_context}

📋 O QUE ROLOU
Em 2-3 parágrafos naturais, conte a história do que aconteceu no grupo.
- Responda: QUEM fez O QUÊ? POR QUÊ?
- Explique quem são as pessoas mencionadas (use links/imagens)
- Escreva fluido, como se estivesse contando pra alguém
- Se faltar contexto, diga claramente

🔥 TOP 5 ASSUNTOS
Liste os tópicos principais de forma NATURAL:
1-5. Para cada um, conte como se estivesse explicando para alguém. Use os links/imagens para adicionar contexto.

💡 FRASES QUE MARCARAM
Citações exatas importantes:
"Frase" - @usuario sobre [contexto]

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
