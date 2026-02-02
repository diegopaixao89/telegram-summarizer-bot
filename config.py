import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Configurações da API de IA
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configurações do banco de dados
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/messages.db")

# Configurações de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validação
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN não configurado no arquivo .env")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY não configurado no arquivo .env")
