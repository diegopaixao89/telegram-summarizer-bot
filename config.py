import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env (para ambiente local)
# No Koyeb, as variáveis são injetadas diretamente como environment variables
load_dotenv()

# Configurações do Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")

# Configurações da API de IA
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

# Debug: printar se as keys foram carregadas (sem mostrar os valores)
print(f"[CONFIG] TELEGRAM_BOT_TOKEN: {'✅ Loaded' if TELEGRAM_BOT_TOKEN else '❌ Missing'}")
print(f"[CONFIG] GROQ_API_KEY: {'✅ Loaded' if GROQ_API_KEY else '❌ Missing'}")
print(f"[CONFIG] GEMINI_API_KEY: {'✅ Loaded' if GEMINI_API_KEY else '❌ Missing'}")

# Configurações do banco de dados
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/messages.db")

# Configurações de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Validação
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN não configurado no arquivo .env")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY não configurado no arquivo .env")

# Log de configuração de IAs (não obrigatório mas recomendado)
import logging
logger = logging.getLogger(__name__)

if GEMINI_API_KEY:
    logger.info("✅ GEMINI_API_KEY configurada - Usando Google Gemini 1.5 Flash")
else:
    logger.warning("⚠️  GEMINI_API_KEY NÃO CONFIGURADA - Usando apenas Groq (limite 100k tokens/dia)")
    logger.warning("⚠️  Obtenha sua key gratuita em: https://aistudio.google.com/app/apikey")
