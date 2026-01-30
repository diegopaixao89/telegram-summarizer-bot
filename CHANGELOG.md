# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.3.0] - 2026-01-30

### ✨ Adicionado
- TOP 5 Membros Ativos agora mostra `@username` de cada membro
- Contagem de mensagens para cada usuário ativo
- Resumo personalizado de uma linha sobre o que cada membro discutiu
- Função `_get_top_users_with_context()` para agrupar mensagens por usuário
- Melhor análise contextual dos usuários mais participativos

### 🎨 Melhorado
- Formato mais claro e informativo da seção de membros ativos
- Instruções aprimoradas no prompt para IA gerar resumos personalizados

### Exemplo
Antes:
```
- João participou bastante das discussões
- Maria trouxe informações importantes
```

Depois:
```
1. @joao (45 msgs) - Discutindo prazos do projeto e organização da sprint
2. @maria (32 msgs) - Compartilhando memes e links sobre tecnologia
```

---

## [1.2.0] - 2026-01-30

### ✨ Adicionado
- **Processamento de Mídia Completo:**
  - 📷 Imagens: Captura com legendas
  - 🔗 Links: Extração automática de título, descrição e domínio
  - 📄 Documentos: Identificação de PDFs, Word, etc
  - 🎥 Vídeos: Reconhecimento e contextualização
  - 🎵 Áudios: Marcação de mensagens de voz
  - 🎭 Stickers: Identificação com emojis

- Arquivo `media_processor.py` com:
  - `process_photo()` - Processa imagens
  - `extract_link_info()` - Extrai metadados de URLs
  - `enrich_message_text()` - Enriquece texto com info de links
  - `extract_urls_from_text()` - Detecta URLs em mensagens

### 🔧 Modificado
- `bot.py`: Handler `save_message()` agora processa todos tipos de mídia
- `main.py`: Handler aceita TODOS tipos de mensagens (não só texto)
- `requirements.txt`: Adicionadas dependências:
  - `beautifulsoup4>=4.12.0`
  - `lxml>=5.0.0`

### 📦 Dependências
- BeautifulSoup4 para parsing HTML
- lxml para parsing rápido de XML/HTML

---

## [1.1.0] - 2026-01-30

### ✨ Adicionado
- **Sistema de Importação de Mensagens Antigas:**
  - Arquivo `import_messages.py` para importar backup JSON
  - `messages_backup.json` com 888 mensagens antigas
  - Importação automática na primeira inicialização
  - Previne reimportação duplicada (renomeia após importar)

### 🐛 Corrigido
- **Inicialização do Banco de Dados:**
  - Banco agora é inicializado ANTES do bot começar
  - Correção do erro "no such table: messages"
  - Garantia de que tabelas existem antes de receber updates

### 🔧 Modificado
- `main.py`:
  - Adicionado `import_backup_messages()` após init do DB
  - Logs informativos sobre importação
  - Criação de diretório `./data` antes de tudo

### 📊 Dados
- 888 mensagens históricas de 29/01 a 30/01 importadas
- Período: 2026-01-29 21:14:43 até 2026-01-30 04:24:42

---

## [1.0.0] - 2026-01-29

### 🎉 Release Inicial

#### ✨ Funcionalidades Core
- Bot Telegram funcional com handlers
- Coleta automática de mensagens
- Armazenamento em SQLite (aiosqlite)
- Comandos básicos:
  - `/start` - Boas-vindas
  - `/resumo` - Resumo de 2000 mensagens
  - `/resumo_rapido` - Resumo de 500 mensagens
  - `/resumo_hoje` - Mensagens do dia
  - `/resumo_personalizado N` - N mensagens
  - `/stats` - Estatísticas do grupo

#### 🤖 Integração IA
- Groq API (LLaMA 3.3 70B Versatile)
- Resumos estruturados com:
  - Resumo Executivo
  - TOP 5 Assuntos
  - Insights e Destaques
  - Membros Mais Ativos
  - Links Relevantes

#### 🎨 Funcionalidades Avançadas
- Resumo em chunks para + de 800 mensagens
- Tom natural e descontraído nos resumos
- Análise de engagement e relevância
- TOP 5 assuntos mais discutidos

#### 🗄️ Banco de Dados
- SQLite com estrutura:
  - Tabela `messages` com campos:
    - id, message_id, chat_id
    - user_id, username, first_name
    - text, timestamp
  - Índice único em (message_id, chat_id)

#### ☁️ Deploy
- Dockerfile configurado
- Health check HTTP na porta 8080
- Deploy no Koyeb (24/7)
- CI/CD automático com GitHub

#### 📦 Dependências Iniciais
- python-telegram-bot==21.0
- groq>=1.0.0
- python-dotenv==1.0.1
- aiosqlite==0.20.0
- aiohttp>=3.11.0

---

## Formato do Versionamento

Seguimos [Semantic Versioning](https://semver.org/):
- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Novas funcionalidades compatíveis
- **PATCH**: Correções de bugs compatíveis

---

## Tipos de Mudanças

- ✨ **Adicionado**: Novas funcionalidades
- 🔧 **Modificado**: Mudanças em funcionalidades existentes
- 🐛 **Corrigido**: Correções de bugs
- ❌ **Removido**: Funcionalidades removidas
- 🔒 **Segurança**: Vulnerabilidades corrigidas
- 📦 **Dependências**: Atualizações de pacotes

---

**Última atualização:** 30/01/2026
