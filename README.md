# Telegram Summarizer Bot

Bot do Telegram que resume conversas de grupos com alto volume de mensagens usando IA.

## Funcionalidades

- Coleta mensagens do grupo automaticamente
- Gera resumos sob demanda usando Groq API (gratuito e rápido)
- Identifica pontos importantes, decisões e tópicos principais
- Armazena histórico de mensagens em SQLite

## Comandos

- `/resumo` - Resumo das últimas 100 mensagens
- `/resumo_hoje` - Resumo das mensagens de hoje
- `/resumo_personalizado <número>` - Resumo das últimas N mensagens

## Setup

### 1. Obter Token do Bot Telegram

1. Abra o Telegram e busque por `@BotFather`
2. Envie `/newbot`
3. Siga as instruções e copie o token gerado

### 2. Obter API Key do Groq

1. Acesse https://console.groq.com
2. Crie uma conta (gratuita)
3. Gere uma API key em "API Keys"

### 3. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione suas credenciais:

```
TELEGRAM_BOT_TOKEN=seu_token_aqui
GROQ_API_KEY=sua_chave_aqui
```

### 4. Executar com Docker

```bash
# Build e start
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar o bot
docker-compose down
```

### 5. Adicionar o Bot ao Grupo

1. Adicione o bot ao seu grupo do Telegram
2. Dê permissão de administrador (para ler mensagens)
3. O bot começará a coletar mensagens automaticamente

## Estrutura do Projeto

```
telegram-summarizer-bot/
├── bot.py              # Arquivo principal do bot
├── config.py           # Configurações
├── database.py         # Gerenciamento do banco de dados
├── summarizer.py       # Integração com Groq API
├── requirements.txt    # Dependências Python
├── Dockerfile          # Configuração Docker
├── docker-compose.yml  # Orquestração Docker
├── .env.example        # Exemplo de variáveis de ambiente
├── .env                # Suas credenciais (não commitar)
└── data/               # Banco de dados SQLite
```

## Desenvolvimento Local (sem Docker)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar bot
python bot.py
```

## Tecnologias

- **Python 3.11**
- **python-telegram-bot** - SDK oficial do Telegram
- **Groq API** - IA para sumarização (gratuito, muito rápido)
- **SQLite** - Banco de dados local
- **Docker** - Containerização

## Custos

- **Telegram Bot**: Gratuito
- **Groq API**: Gratuito (rate limits generosos)
- **Hospedagem**: Docker local (gratuito)

## Próximos Passos

- [ ] Adicionar suporte para múltiplos grupos
- [ ] Implementar resumos periódicos automáticos
- [ ] Adicionar detecção de idioma
- [ ] Dashboard web para visualizar resumos
- [ ] Exportar resumos para PDF
