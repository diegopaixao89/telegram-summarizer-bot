"""
Main entry point que roda o bot + servidor HTTP para health check
"""
import asyncio
import threading
from aiohttp import web
import bot

# Servidor HTTP simples para health check
async def health_check(request):
    return web.Response(text="Bot is running!", status=200)

async def start_web_server():
    """Inicia servidor HTTP para health check do Railway"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("Health check server running on port 8080")

def run_bot():
    """Roda o bot do Telegram"""
    bot.main()

if __name__ == "__main__":
    # Iniciar servidor HTTP em thread separada
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_web_server())

    # Rodar servidor em background
    threading.Thread(target=lambda: loop.run_forever(), daemon=True).start()

    # Rodar bot no thread principal
    print("Starting Telegram bot...")
    run_bot()
