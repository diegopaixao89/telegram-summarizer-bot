"""
Main entry point - Bot + Health Check HTTP Server
"""
import os
import asyncio
import logging
from aiohttp import web
from telegram.ext import Application
from bot import start, stats, resumo, resumo_hoje, resumo_personalizado, resumo_rapido, save_message, post_init
from telegram.ext import CommandHandler, MessageHandler, filters
from telegram import Update
import config

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
    """Start Telegram bot"""
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("resumo", resumo))
    application.add_handler(CommandHandler("resumo_hoje", resumo_hoje))
    application.add_handler(CommandHandler("resumo_personalizado", resumo_personalizado))
    application.add_handler(CommandHandler("resumo_rapido", resumo_rapido))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_message))

    logger.info("Starting Telegram bot...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

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
