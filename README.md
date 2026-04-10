# Resumildo — Bot de Resumos do Telegram

Bot inteligente para Telegram que coleta mensagens de grupos e gera resumos elaborados usando IA (Groq / LLaMA 3.3 70B).

**Status:** Em produção no Koyeb (24/7) | **Bot:** [@resumildobot](https://t.me/resumildobot)

---

## Screenshot

> Exemplo de resumo gerado pelo `/resumo` em um grupo ativo

![Exemplo de resumo](docs/screenshots/resumo-exemplo.png)

---

## 🎯 Funcionalidades

### 📊 Resumos Inteligentes
- **Resumo Completo** (`/resumo`) - Analisa últimas 2000 mensagens
- **Resumo Rápido** (`/resumo_rapido`) - Análise de 500 mensagens
- **Resumo Hoje** (`/resumo_hoje`) - Apenas mensagens do dia
- **Resumo Personalizado** (`/resumo_personalizado N`) - Define quantidade de mensagens

### 📋 Estrutura dos Resumos
- 📋 **Resumo Executivo** - Contexto geral da conversa
- 🔥 **TOP 5 Assuntos** - Tópicos mais discutidos
- 💡 **Insights e Destaques** - Frases marcantes e insights
- 👥 **TOP 5 Membros Ativos** - Usuários com @ e resumo personalizado do que falaram
- 🔗 **Links Relevantes** - URLs importantes compartilhadas

### 🎨 Processamento de Mídia
- 📷 **Imagens** - Captura e contextualiza com legendas
- 🔗 **Links** - Extrai título, descrição e domínio automaticamente
- 📄 **Documentos** - Identifica PDFs, Word, etc
- 🎥 **Vídeos** - Reconhece e salva com contexto
- 🎵 **Áudios** - Marca mensagens de voz e áudio
- 🎭 **Stickers** - Identifica com emoji

### 📈 Estatísticas
- `/stats` - Mostra total de mensagens coletadas

---

## 🚀 Tecnologias

- **Python 3.11**
- **python-telegram-bot** - Bot API do Telegram
- **Groq AI** - IA para geração de resumos (LLaMA 3.3 70B)
- **SQLite** (aiosqlite) - Banco de dados local
- **BeautifulSoup4** - Parser HTML para links
- **aiohttp** - HTTP client assíncrono
- **Docker** - Containerização

---

## 📦 Estrutura do Projeto

```
telegram-summarizer-bot/
├── bot.py                    # Lógica principal do bot e handlers
├── main.py                   # Entry point com health check
├── database.py               # Gerenciamento SQLite
├── summarizer.py             # Geração de resumos com Groq AI
├── media_processor.py        # Processamento de imagens e links
├── import_messages.py        # Importação de mensagens antigas
├── config.py                 # Configurações e variáveis de ambiente
├── requirements.txt          # Dependências Python
├── Dockerfile                # Container Docker
├── messages_backup.json      # Backup de mensagens antigas
└── data/
    └── messages.db           # Banco de dados SQLite
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
GROQ_API_KEY=sua_chave_aqui
PORT=8080
DATABASE_PATH=./data/messages.db
LOG_LEVEL=INFO
```

### Obter Credenciais

1. **Telegram Bot Token:**
   - Fale com [@BotFather](https://t.me/BotFather)
   - `/newbot` → siga instruções
   - Guarde o token

2. **Groq API Key:**
   - Acesse [console.groq.com](https://console.groq.com)
   - Crie conta grátis
   - Gere nova API key

---

## 🏃 Como Executar

### Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/diegopaixao89/telegram-summarizer-bot.git
cd telegram-summarizer-bot

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# 5. Execute o bot
python main.py
```

### Docker

```bash
# Build
docker build -t telegram-summarizer-bot .

# Run
docker run -d \
  -e TELEGRAM_BOT_TOKEN=seu_token \
  -e GROQ_API_KEY=sua_chave \
  -p 8080:8080 \
  --name resumildo \
  telegram-summarizer-bot
```

---

## ☁️ Deploy no Koyeb

### Configuração Automática

1. **Fork/Push para GitHub**
2. **Criar conta no Koyeb:** [koyeb.com](https://koyeb.com)
3. **Conectar GitHub:** Autorizar acesso ao repositório
4. **Criar serviço:**
   - Repository: `seu-usuario/telegram-summarizer-bot`
   - Branch: `main`
   - Builder: **Dockerfile**
   - Port: `8080`

5. **Adicionar variáveis de ambiente:**
   - `TELEGRAM_BOT_TOKEN`
   - `GROQ_API_KEY`
   - `PORT` = `8080`

6. **Deploy!** - Automático a cada push

### CI/CD Automático

Toda vez que você fizer push para `main`:
1. Koyeb detecta automaticamente
2. Build do Docker image
3. Deploy da nova versão
4. Zero downtime

---

## 🔧 Configuração do Bot no Telegram

### 1. Desabilitar Privacy Mode

**IMPORTANTE:** Para o bot coletar todas as mensagens:

```
1. @BotFather → /mybots
2. Selecione seu bot
3. Bot Settings → Group Privacy
4. Turn OFF
5. Remover bot do grupo
6. Adicionar novamente
7. Tornar ADMINISTRADOR
```

### 2. Adicionar ao Grupo

1. Abra o grupo
2. Adicionar membros → procure `@resumildobot`
3. Adicione ao grupo
4. Promova a **Administrador** com permissão de ler mensagens

### 3. Testar

```
/start@resumildobot
/stats@resumildobot
```

---

## 📊 Banco de Dados

### Estrutura

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    chat_id INTEGER NOT NULL,
    user_id INTEGER,
    username TEXT,
    first_name TEXT,
    text TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(message_id, chat_id)
);
```

### Backup e Restauração

O bot importa automaticamente `messages_backup.json` na primeira inicialização.

---

## 🎨 Exemplos de Resumo

### TOP 5 Membros Ativos
```
1. @joao (89 msgs) - Liderando discussões sobre arquitetura e prazos
2. @maria (67 msgs) - Compartilhando links e organizando reuniões
3. @pedro (54 msgs) - Tirando dúvidas técnicas sobre backend
4. @ana (41 msgs) - Coordenando sprint e alinhamentos
5. @lucas (38 msgs) - Contribuindo com ideias e resolvendo bugs
```

---

## 🔐 Segurança

### Boas Práticas

1. **Nunca commite credenciais**
   - Use `.env` local
   - Variáveis de ambiente em produção

2. **Revogue tokens expostos**
   - Se credenciais vazarem, revogue imediatamente
   - Telegram: @BotFather → API Token → Revoke
   - Groq: Console → Delete key → Criar nova

---

## 🐛 Troubleshooting

### Bot não responde
- Verificar status no Koyeb (deve estar Healthy)
- Aguardar 2-3 minutos após deploy

### "Conflict: terminated by other getUpdates"
- Duas instâncias rodando simultaneamente
- Aguardar 1-2 minutos para resolver

### Bot não coleta mensagens
- Privacy Mode deve estar OFF
- Bot deve ser administrador
- Remover e readicionar após mudar Privacy Mode

---

## 📝 Changelog

### v1.3.0 (30/01/2026)
- ✨ TOP 5 membros com @ e resumo personalizado
- 🎨 Melhor contextualização dos usuários

### v1.2.0 (30/01/2026)
- ✨ Processamento de imagens, links e mídia
- 📦 BeautifulSoup4 para extração de metadados

### v1.1.0 (30/01/2026)
- ✨ Importação automática de mensagens antigas
- 🐛 Fix: inicialização do banco

### v1.0.0 (29/01/2026)
- 🎉 Release inicial
- ✨ Comandos básicos de resumo
- ✨ Integração com Groq AI

---

## 📄 Licença

MIT License

---

## 🙏 Agradecimentos

- **Groq** - API de IA gratuita
- **Telegram** - Bot API
- **Koyeb** - Hospedagem gratuita
- **Claude Sonnet 4.5** - Assistência no desenvolvimento

---

**Desenvolvido com ❤️ usando Python e IA**
