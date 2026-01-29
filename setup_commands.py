"""
Script para configurar o menu de comandos do bot no Telegram
"""
import asyncio
from telegram import Bot, BotCommand
import config


async def setup_commands():
    """Configura os comandos do bot que aparecem no menu"""
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

    commands = [
        BotCommand("start", "Iniciar o bot e ver instruções"),
        BotCommand("resumo", "Resumo das últimas 100 mensagens"),
        BotCommand("resumo_hoje", "Resumo das mensagens de hoje"),
        BotCommand("resumo_rapido", "Resumo rápido (últimas 50)"),
        BotCommand("resumo_personalizado", "Resumo personalizado (use: /resumo_personalizado <N>)"),
        BotCommand("stats", "Ver estatísticas do grupo"),
    ]

    await bot.set_my_commands(commands)
    print("Comandos configurados com sucesso!")
    print("\nComandos disponiveis:")
    for cmd in commands:
        print(f"  /{cmd.command} - {cmd.description}")


if __name__ == "__main__":
    asyncio.run(setup_commands())
