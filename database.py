import aiosqlite
import logging
from datetime import datetime
from typing import List, Dict
import config

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path

    async def initialize(self):
        """Inicializa o banco de dados e cria tabelas"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER,
                    username TEXT,
                    first_name TEXT,
                    text TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(message_id, chat_id)
                )
            """)
            await db.commit()
            logger.info("Banco de dados inicializado")

    async def save_message(self, message_data: Dict):
        """Salva uma mensagem no banco de dados"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO messages
                    (message_id, chat_id, user_id, username, first_name, text, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    message_data['message_id'],
                    message_data['chat_id'],
                    message_data['user_id'],
                    message_data['username'],
                    message_data['first_name'],
                    message_data['text'],
                    message_data['timestamp']
                ))
                await db.commit()
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")

    async def get_last_n_messages(self, chat_id: int, n: int = 100) -> List[Dict]:
        """Recupera as últimas N mensagens de um chat (do mais novo pro mais velho)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM messages
                WHERE chat_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (chat_id, n)) as cursor:
                rows = await cursor.fetchall()
                # Retorna do mais recente pro mais velho (DESC)
                return [dict(row) for row in rows]

    async def get_messages_today(self, chat_id: int) -> List[Dict]:
        """Recupera mensagens de hoje de um chat (do mais novo pro mais velho)"""
        today = datetime.now().date()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM messages
                WHERE chat_id = ?
                AND DATE(timestamp) = ?
                ORDER BY timestamp DESC
            """, (chat_id, today)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_messages_last_hours(self, chat_id: int, hours: int = 12) -> List[Dict]:
        """Recupera mensagens das últimas N horas (do mais novo pro mais velho)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM messages
                WHERE chat_id = ?
                AND timestamp >= datetime('now', '-' || ? || ' hours')
                ORDER BY timestamp DESC
            """, (chat_id, hours)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_messages_count(self, chat_id: int) -> int:
        """Conta total de mensagens armazenadas de um chat"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT COUNT(*) FROM messages WHERE chat_id = ?
            """, (chat_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0
