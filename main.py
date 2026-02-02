"""
Main entry point - Bot + Health Check HTTP Server
"""
import os
import asyncio
import logging
import random
from aiohttp import web
from telegram.ext import Application
from telegram.error import Conflict
from bot import start, stats, resumo, resumo_hoje, resumo_personalizado, resumo_rapido, save_message, post_init, db
from telegram.ext import CommandHandler, MessageHandler, filters
from telegram import Update
import config
from import_messages import import_backup_messages

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Health check endpoint
async def health_check(request):
    return web.Response(text="OK", status=200)

async def start_health_server():
    """Start HTTP server for Railway health checks"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)

    port = int(os.getenv('PORT', 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Health check server started on port {port}")

    # Keep server running
    await asyncio.Event().wait()

async def start_bot():
    """Start Telegram bot with conflict handling"""
    # Random startup delay (5-20s) to avoid multiple instances starting simultaneously
    startup_delay = random.uniform(5, 20)
    logger.info(f"Waiting {startup_delay:.1f}s before starting to avoid conflicts...")
    await asyncio.sleep(startup_delay)

    # Initialize database BEFORE starting the bot
    logger.info("Initializing database...")
    os.makedirs('./data', exist_ok=True)
    await db.initialize()
    logger.info("Database initialized successfully!")

    # Import backup messages if available
    logger.info("Checking for backup messages...")
    imported_count = await import_backup_messages()
    if imported_count > 0:
        logger.info(f"Imported {imported_count} messages from backup!")

    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("resumo", resumo))
    application.add_handler(CommandHandler("resumo_hoje", resumo_hoje))
    application.add_handler(CommandHandler("resumo_personalizado", resumo_personalizado))
    application.add_handler(CommandHandler("resumo_rapido", resumo_rapido))
    # Handler para TODAS as mensagens (texto, foto, vídeo, etc), exceto comandos
    application.add_handler(MessageHandler(~filters.COMMAND, save_message))

    logger.info("Starting Telegram bot...")
    await application.initialize()
    await application.start()

    # Start polling with conflict retry logic
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        try:
            logger.info(f"Starting polling (attempt {retry_count + 1}/{max_retries})...")
            await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            logger.info("✅ Bot polling started successfully!")
            break
        except Conflict as e:
            retry_count += 1
            wait_time = min(30 * retry_count, 300)  # Max 5 minutes
            logger.warning(f"⚠️  Conflict detected (attempt {retry_count}/{max_retries}): {e}")
            logger.info(f"Waiting {wait_time}s for other instance to stop...")
            await asyncio.sleep(wait_time)

            if retry_count >= max_retries:
                logger.error("❌ Max retries reached. Another instance is persistently running.")
                logger.error("Please check Koyeb and ensure only 1 instance is configured.")
                raise

    # Keep bot running
    await asyncio.Event().wait()

async def main():
    """Run both health server and bot"""
    await asyncio.gather(
        start_health_server(),
        start_bot()
    )

if __name__ == "__main__":
    asyncio.run(main())
