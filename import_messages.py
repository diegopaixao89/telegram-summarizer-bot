"""
Script para importar mensagens do backup JSON para o banco de dados
"""
import json
import os
import logging
from database import Database
import asyncio

logger = logging.getLogger(__name__)

async def import_backup_messages():
    """Importa mensagens do arquivo messages_backup.json se existir"""
    backup_file = 'messages_backup.json'

    if not os.path.exists(backup_file):
        logger.info("Nenhum arquivo de backup encontrado. Pulando importação.")
        return 0

    try:
        # Ler arquivo de backup
        with open(backup_file, 'r', encoding='utf-8') as f:
            messages = json.load(f)

        if not messages:
            logger.info("Arquivo de backup vazio.")
            return 0

        # Conectar ao banco
        db = Database()

        # Verificar se já tem mensagens (evitar duplicação)
        count = await db.get_messages_count(messages[0]['chat_id'])
        if count > 0:
            logger.info(f"Banco já tem {count} mensagens. Pulando importação.")
            return 0

        # Importar mensagens
        imported = 0
        for msg in messages:
            await db.save_message(msg)
            imported += 1

        logger.info(f"✅ {imported} mensagens importadas do backup!")

        # Renomear arquivo de backup para evitar reimportação
        os.rename(backup_file, f'{backup_file}.imported')

        return imported

    except Exception as e:
        logger.error(f"Erro ao importar backup: {e}")
        return 0

if __name__ == "__main__":
    # Permite executar o script manualmente
    asyncio.run(import_backup_messages())
