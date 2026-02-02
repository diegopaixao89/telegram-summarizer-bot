import logging
import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import config
from database import Database
from summarizer import Summarizer
from media_processor import MediaProcessor

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

# Inicializar componentes
db = Database()
summarizer = Summarizer()
media_processor = MediaProcessor()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    await update.message.reply_text(
        "🤖 *Bot de Resumos do Telegram*\n\n"
        "Olá! Eu monitoro as mensagens deste grupo e posso gerar resumos sob demanda.\n\n"
        "📋 *Comandos disponíveis:*\n"
        "• `/resumo` - Resumo das últimas 100 mensagens\n"
        "• `/resumo_hoje` - Resumo das mensagens de hoje\n"
        "• `/resumo_personalizado <N>` - Resumo das últimas N mensagens\n"
        "• `/resumo_rapido` - Resumo curto das últimas 50 mensagens\n"
        "• `/stats` - Estatísticas do grupo\n\n"
        "Adicione-me como administrador para eu começar a coletar mensagens!",
        parse_mode='Markdown'
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra estatísticas do grupo"""
    chat_id = update.effective_chat.id
    count = await db.get_messages_count(chat_id)

    await update.message.reply_text(
        f"📊 *Estatísticas do Grupo*\n\n"
        f"Total de mensagens armazenadas: *{count}*\n"
        f"Bot ativo desde o início da coleta.",
        parse_mode='Markdown'
    )


async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera resumo das últimas 2000 mensagens"""
    chat_id = update.effective_chat.id

    # Enviar mensagem de processamento
    processing_msg = await update.message.reply_text(
        "⏳ Analisando as últimas 2000 mensagens... Isso pode levar até 2 minutos. Por favor, aguarde."
    )

    try:
        messages = await db.get_last_n_messages(chat_id, 2000)

        if not messages:
            await processing_msg.edit_text(
                "❌ Nenhuma mensagem encontrada. Certifique-se de que o bot está coletando mensagens."
            )
            return

        summary = await summarizer.summarize(messages)

        # Enviar resumo (sem parse_mode para evitar conflitos com caracteres especiais)
        header = f"📝 RESUMO - Últimas {len(messages)} mensagens\n\n"
        await processing_msg.edit_text(header + summary)

    except Exception as e:
        logger.error(f"Erro ao gerar resumo: {e}")
        await processing_msg.edit_text(
            f"❌ Erro ao gerar resumo: {str(e)}"
        )


async def resumo_hoje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera resumo das mensagens de hoje"""
    chat_id = update.effective_chat.id

    processing_msg = await update.message.reply_text(
        "⏳ Analisando mensagens de hoje... Por favor, aguarde."
    )

    try:
        messages = await db.get_messages_today(chat_id)

        if not messages:
            await processing_msg.edit_text(
                "❌ Nenhuma mensagem de hoje encontrada."
            )
            return

        summary = await summarizer.summarize(messages)

        today = datetime.now().strftime("%d/%m/%Y")
        header = f"📅 RESUMO DO DIA - {today}\nTotal: {len(messages)} mensagens\n\n"
        await processing_msg.edit_text(header + summary)

    except Exception as e:
        logger.error(f"Erro ao gerar resumo do dia: {e}")
        await processing_msg.edit_text(
            f"❌ Erro ao gerar resumo: {str(e)}"
        )


async def resumo_personalizado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera resumo de N mensagens personalizadas"""
    chat_id = update.effective_chat.id

    # Validar argumento
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "❌ Uso correto: `/resumo_personalizado <número>`\n"
            "Exemplo: `/resumo_personalizado 200`",
            parse_mode='Markdown'
        )
        return

    n = int(context.args[0])

    if n < 10 or n > 1000:
        await update.message.reply_text(
            "❌ O número deve estar entre 10 e 1000 mensagens."
        )
        return

    processing_msg = await update.message.reply_text(
        f"⏳ Analisando as últimas {n} mensagens... Por favor, aguarde."
    )

    try:
        messages = await db.get_last_n_messages(chat_id, n)

        if not messages:
            await processing_msg.edit_text(
                "❌ Nenhuma mensagem encontrada."
            )
            return

        summary = await summarizer.summarize(messages)

        header = f"📝 RESUMO PERSONALIZADO - {len(messages)} mensagens\n\n"
        await processing_msg.edit_text(header + summary)

    except Exception as e:
        logger.error(f"Erro ao gerar resumo personalizado: {e}")
        await processing_msg.edit_text(
            f"❌ Erro ao gerar resumo: {str(e)}"
        )


async def resumo_rapido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera resumo rápido das mensagens das últimas 12 horas"""
    chat_id = update.effective_chat.id

    processing_msg = await update.message.reply_text(
        "⚡ Gerando resumo das últimas 12 horas..."
    )

    try:
        # Pegar apenas mensagens das últimas 12 horas (contexto recente)
        messages = await db.get_messages_last_hours(chat_id, hours=12)

        # Limitar a 200 mensagens máximo (do mais recente pro mais velho)
        if len(messages) > 200:
            messages = messages[:200]

        # Se não tiver mensagens recentes, pega últimas 150
        if not messages or len(messages) < 5:
            messages = await db.get_last_n_messages(chat_id, 150)
            if len(messages) > 150:
                messages = messages[:150]

        if not messages:
            await processing_msg.edit_text(
                "❌ Nenhuma mensagem encontrada."
            )
            return

        # Usar summarize normal em vez de quick_summary para ter contexto enriquecido
        summary = await summarizer.summarize(messages)

        header = f"⚡ RESUMO RÁPIDO - {len(messages)} mensagens\n\n"
        await processing_msg.edit_text(header + summary)

    except Exception as e:
        logger.error(f"Erro ao gerar resumo rápido: {e}")
        await processing_msg.edit_text(
            f"❌ Erro: {str(e)}"
        )


async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Salva cada mensagem do grupo no banco de dados, incluindo mídia"""
    message = update.message

    # Ignorar se não houver mensagem
    if not message:
        return

    # Ignorar mensagens de comandos
    if message.text and message.text.startswith('/'):
        return

    # Processar texto da mensagem
    message_text = None

    # 1. Mensagens com texto
    if message.text:
        message_text = message.text
        # Enriquecer com informações de links
        message_text = await media_processor.enrich_message_text(message_text)

    # 2. Mensagens com foto
    elif message.photo:
        try:
            # Pegar a foto de maior resolução
            photo = message.photo[-1]
            photo_file = await context.bot.get_file(photo.file_id)
            photo_bytes = await photo_file.download_as_bytearray()

            # Processar imagem
            caption = message.caption or ""
            photo_description = await media_processor.process_photo(bytes(photo_bytes), caption)
            message_text = photo_description

        except Exception as e:
            logger.error(f"Erro ao processar foto: {e}")
            message_text = "📷 [Imagem]"

    # 3. Mensagens com link (mas sem texto)
    elif message.caption:
        message_text = message.caption
        message_text = await media_processor.enrich_message_text(message_text)

    # 4. Outros tipos de mídia
    elif message.document:
        file_name = message.document.file_name if message.document.file_name else "arquivo"
        caption = message.caption or ""
        message_text = f"📄 [Documento: {file_name}]"
        if caption:
            message_text += f" {caption}"

    elif message.video:
        caption = message.caption or ""
        message_text = f"🎥 [Vídeo]"
        if caption:
            message_text += f" {caption}"

    elif message.voice:
        message_text = "🎤 [Mensagem de voz]"

    elif message.audio:
        title = message.audio.title or "áudio"
        message_text = f"🎵 [Áudio: {title}]"

    elif message.sticker:
        emoji = message.sticker.emoji or ""
        message_text = f"🎭 [Sticker {emoji}]"

    # Ignorar se não conseguiu extrair nada
    if not message_text:
        return

    message_data = {
        'message_id': message.message_id,
        'chat_id': message.chat_id,
        'user_id': message.from_user.id if message.from_user else None,
        'username': message.from_user.username if message.from_user else None,
        'first_name': message.from_user.first_name if message.from_user else None,
        'text': message_text,
        'timestamp': message.date.isoformat() if message.date else datetime.now().isoformat()
    }

    await db.save_message(message_data)
    logger.debug(f"Mensagem salva: {message.message_id} de {message_data['username']}")


async def post_init(application: Application):
    """Inicialização após o bot estar pronto"""
    # Criar diretório data se não existir
    os.makedirs('./data', exist_ok=True)

    # Inicializar banco de dados
    await db.initialize()
    logger.info("Bot inicializado com sucesso!")


def main():
    """Função principal"""
    # Criar aplicação
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # Registrar handlers de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("resumo", resumo))
    application.add_handler(CommandHandler("resumo_hoje", resumo_hoje))
    application.add_handler(CommandHandler("resumo_personalizado", resumo_personalizado))
    application.add_handler(CommandHandler("resumo_rapido", resumo_rapido))

    # Registrar handler para salvar todas as mensagens
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_message))

    # Iniciar bot
    logger.info("Iniciando bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
