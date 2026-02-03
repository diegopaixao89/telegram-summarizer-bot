# 📘 Guia Completo - Bot Telegram Resumildo

**Última atualização:** 03/02/2026
**Status:** ✅ ONLINE e OPERACIONAL
**Bot:** @resumildobot

---

## 📋 Índice

1. [Informações Gerais](#informações-gerais)
2. [Credenciais](#credenciais)
3. [Arquitetura](#arquitetura)
4. [Como Funciona](#como-funciona)
5. [Deploy e Manutenção](#deploy-e-manutenção)
6. [Troubleshooting](#troubleshooting)
7. [Histórico de Sessões](#histórico-de-sessões)

---

## 📌 Informações Gerais

### Bot
- **Username:** @resumildobot
- **Função:** Resumidor inteligente de conversas do Telegram
- **IA:** Google Gemini 2.5 Flash
- **Hospedagem:** Koyeb (gratuito, 24/7)
- **Repositório:** https://github.com/diegopaixao89/telegram-summarizer-bot

### Comandos Disponíveis
```
/start@resumildobot              - Boas-vindas
/resumo@resumildobot             - Resumo completo (2000 msgs)
/resumo_rapido@resumildobot      - Resumo rápido (100 msgs)
/resumo_hoje@resumildobot        - Mensagens desde 00:00 de hoje
/resumo_personalizado N          - N mensagens customizado
/stats@resumildobot              - Estatísticas do grupo
/debug@resumildobot              - Verificar configuração
```

---

## 🔐 Credenciais

### Telegram Bot Token
```
Token: 8543784435:AAGSgZ14cIO7kOsCc53toM2k5pTirqWmHac
Obtido em: @BotFather
```

### Google Gemini API Key
```
API Key: AIzaSyA3cFv1VOw-Lq6RF9wTi94gSeGpC7OSnvM
Obtido em: https://aistudio.google.com/app/apikey
Modelo: Gemini 2.5 Flash
Limite: 60 requisições/minuto (gratuito)
```

### Koyeb (Produção)
```
Dashboard: https://app.koyeb.com
App Name: telegram-bot-resumildo (verificar nome exato no dashboard)
Região: Washington, D.C
```

### Variáveis de Ambiente Necessárias
```bash
TELEGRAM_BOT_TOKEN=8543784435:AAGSgZ14cIO7kOsCc53toM2k5pTirqWmHac
GEMINI_API_KEY=AIzaSyA3cFv1VOw-Lq6RF9wTi94gSeGpC7OSnvM
```

---

## 🏗️ Arquitetura

### Stack Tecnológico
- **Linguagem:** Python 3.11+
- **Framework Bot:** python-telegram-bot 21.0
- **IA:** Google Gemini 2.5 Flash (google-generativeai)
- **Banco de Dados:** SQLite (aiosqlite)
- **Processamento Web:** BeautifulSoup4 + lxml
- **Imagens:** Pillow (PIL)
- **Container:** Docker
- **Deploy:** Koyeb (CI/CD automático via GitHub)

### Estrutura de Arquivos
```
telegram-summarizer-bot/
├── bot.py                    # Lógica principal e handlers
├── main.py                   # Entry point + health check HTTP
├── database.py               # Gerenciamento SQLite
├── summarizer.py             # Geração de resumos com IA
├── media_processor.py        # Processamento de mídia e imagens
├── context_enricher.py       # Enriquecimento de contexto
├── config.py                 # Configurações e variáveis
├── requirements.txt          # Dependências Python
├── Dockerfile                # Container Docker
├── .env                      # Variáveis locais (NÃO commitar)
├── .gitignore                # Arquivos ignorados pelo git
├── CREDENCIAIS.md            # Credenciais (NÃO commitar)
├── README.md                 # Documentação geral
├── CHANGELOG.md              # Histórico de versões
├── SESSAO_*.md               # Documentação de cada sessão
└── data/
    └── messages.db           # Banco SQLite
```

### Fluxo de Funcionamento
```
1. Usuário envia mensagem no grupo
   ↓
2. Bot coleta e salva no SQLite
   ↓
3. Usuário solicita resumo (/resumo_rapido)
   ↓
4. Bot busca mensagens do banco
   ↓
5. Envia para Gemini 2.5 Flash
   ↓
6. Gemini gera resumo inteligente
   ↓
7. Bot retorna resumo formatado
```

---

## ⚙️ Como Funciona

### Coleta de Mensagens
- Bot precisa ser **administrador do grupo**
- Privacy Mode deve estar **desabilitado** (via @BotFather)
- Coleta automática de todas as mensagens
- Armazenamento em SQLite local

### Geração de Resumos
- Usa **Gemini 2.5 Flash** (modelo gratuito e rápido)
- Prompts jornalísticos profissionais
- Pirâmide invertida (mais importante primeiro)
- Inclui TOP 5 assuntos e membros ativos
- Links formatados como hyperlinks markdown

### Processamento de Mídia
- **Imagens:** Gemini Vision analisa e descreve
- **Links:** Extração de título e descrição
- **Documentos:** Registra nome e tipo
- **Vídeos/Áudio:** Identifica e contextualiza
- **Stickers:** Detecta emojis relacionados

---

## 🚀 Deploy e Manutenção

### Deploy Local (Teste)
```bash
# 1. Clonar repositório
cd Desktop/telegram-summarizer-bot

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar .env
# Copiar .env.example para .env
# Adicionar TELEGRAM_BOT_TOKEN e GEMINI_API_KEY

# 5. Rodar bot
python main.py
```

### Deploy Produção (Koyeb)

#### Atualizar Variáveis de Ambiente
1. Acesse https://app.koyeb.com
2. Selecione o app do bot
3. Settings → Environment Variables
4. Adicione/Atualize as variáveis necessárias
5. Clique em "Deploy" para reiniciar

#### Fazer Deploy de Código Novo
```bash
# 1. Commitar mudanças
cd Desktop/telegram-summarizer-bot
git add .
git commit -m "Descrição das mudanças"

# 2. Push para GitHub
git push origin main

# 3. Koyeb detecta automaticamente e faz redeploy
# Aguardar 2-5 minutos
```

#### Monitorar Deploy
- **Dashboard:** Ver status "Building" → "Deploying" → "Healthy"
- **Logs:** Verificar inicialização e erros
- **Teste:** Enviar comando no Telegram após status "Healthy"

### Comandos Git Úteis
```bash
# Ver status
git status

# Ver últimos commits
git log --oneline -10

# Ver diferenças
git diff

# Criar branch
git checkout -b nome-da-branch

# Voltar para main
git checkout main

# Ver branches
git branch -a
```

---

## 🔧 Troubleshooting

### Problema: Bot não responde
**Possíveis causas:**
- Múltiplas instâncias rodando (conflito)
- Privacy Mode ativo
- Bot não é administrador do grupo
- Koyeb offline

**Solução:**
1. Parar todas as instâncias locais
2. Aguardar 2-3 minutos
3. Verificar @BotFather: Privacy Mode = OFF
4. Adicionar bot como admin no grupo
5. Verificar status no Koyeb

### Problema: Erro 404 no Gemini
**Causa:** Modelo Gemini descontinuado

**Solução:**
- Verificar que está usando `gemini-2.5-flash`
- Modelos 1.5 foram descontinuados em 2026
- Ver SESSAO_2026-02-03.md para detalhes

### Problema: "GEMINI_API_KEY missing"
**Solução:**
1. Verificar arquivo .env local
2. Verificar variáveis no Koyeb
3. Obter nova key em: https://aistudio.google.com/app/apikey

### Problema: Banco de dados vazio após deploy
**Causa:** Container efêmero no Koyeb

**Solução:**
- Normal, mensagens antigas se perdem no redeploy
- Bot coleta novas mensagens automaticamente
- Se necessário, usar backup (messages_backup.json)

### Problema: Conflito "terminated by other getUpdates"
**Causa:** Duas instâncias rodando simultaneamente

**Solução:**
1. Parar instância local (Ctrl+C)
2. Aguardar 2-3 minutos
3. Telegram limpa conexão antiga automaticamente

---

## 📚 Histórico de Sessões

### 29-30/01/2026 - Criação Inicial
- ✅ Bot criado e funcionando localmente
- ✅ Deploy no Koyeb (primeira tentativa Fly.io falhou)
- ✅ 888 mensagens importadas
- ✅ Comandos básicos implementados
- **Modelo:** Groq (LLaMA 3.3 70B)

### 02/02/2026 - Migração para Gemini
- ✅ Removido Groq completamente
- ✅ Implementado Google Gemini 1.5 Flash
- ✅ Gemini Vision para análise de imagens
- ✅ Prompts jornalísticos profissionais
- ✅ Foco em mensagens recentes
- **Commits:** 2009d99 a 8ccb439

### 03/02/2026 - Correção Crítica
- 🔴 **Problema:** Bot offline - erro 404 Gemini 1.5
- ✅ **Causa:** Gemini 1.5 descontinuado em 2026
- ✅ **Solução:** Atualizado para Gemini 2.5 Flash
- ✅ Configurada GEMINI_API_KEY no Koyeb
- ✅ Bot restaurado e 100% operacional
- **Commits:** 415b2e5, 26fe6ab, c39331a
- **Tempo:** ~25 minutos

---

## 🎯 Modelos Gemini (Status 2026)

### ❌ Descontinuados (Retornam 404)
- Gemini 1.0 (todas versões)
- Gemini 1.5 Flash
- Gemini 1.5 Pro

### ✅ Ativos e Gratuitos
- **Gemini 2.5 Flash** ← **EM USO**
  - Limite: 60 requisições/minuto
  - Uso: Resumos de texto + Vision

- **Gemini 2.5 Pro**
  - Limite: 10 requisições/minuto
  - Uso: Tarefas complexas (não usado no bot)

- **Gemini 2.5 Flash Lite**
  - Limite: Maior que Flash
  - Uso: Tarefas simples (não usado no bot)

---

## 🔗 Links Importantes

### Produção
- **Bot Telegram:** https://t.me/resumildobot
- **Koyeb Dashboard:** https://app.koyeb.com
- **GitHub Repo:** https://github.com/diegopaixao89/telegram-summarizer-bot

### Ferramentas
- **Google AI Studio:** https://aistudio.google.com/app/apikey
- **BotFather:** https://t.me/BotFather
- **Gemini Docs:** https://ai.google.dev/gemini-api/docs/models

### Documentação Técnica
- **Python Telegram Bot:** https://python-telegram-bot.org
- **Koyeb Docs:** https://www.koyeb.com/docs
- **Gemini API:** https://ai.google.dev/api/models

---

## 📊 Estatísticas do Projeto

### Desenvolvimento
- **Início:** 29/01/2026
- **Sessões:** 3 principais
- **Commits:** 15+
- **Tempo total:** ~20 horas

### Tecnologias
- **Linguagem:** Python 3.11+
- **IA:** Google Gemini 2.5 Flash
- **Banco:** SQLite
- **Deploy:** Koyeb + Docker
- **CI/CD:** GitHub Actions automático

### Status Atual
- ✅ **100% operacional**
- ✅ **Rodando 24/7 na nuvem**
- ✅ **Gratuito (sem custos)**
- ✅ **Resumos inteligentes funcionando**
- ✅ **Análise de imagens ativa**

---

## ⚠️ Notas Importantes

### Segurança
- **NUNCA** commitar arquivo `.env`
- **NUNCA** commitar `CREDENCIAIS.md`
- Ambos estão no `.gitignore`
- Se credenciais vazarem, revogar imediatamente

### Boas Práticas
- Sempre commitar com mensagens descritivas
- Testar localmente antes de fazer push
- Aguardar deploy terminar antes de testar
- Documentar mudanças significativas

### Backup
- Banco SQLite é efêmero no Koyeb
- Mensagens antigas somem após redeploy
- Bot coleta novas automaticamente
- Sistema de backup disponível (import_messages.py)

---

## 🎉 Próximas Melhorias (Opcional)

### Funcionalidades
- [ ] OCR para extrair texto de imagens
- [ ] Transcrição de áudios (Whisper)
- [ ] Resumos agendados automáticos
- [ ] Dashboard web de visualização
- [ ] Exportar resumos em PDF
- [ ] Análise de sentimento

### Técnicas
- [ ] Testes automatizados (pytest)
- [ ] CI/CD com GitHub Actions
- [ ] Monitoramento (Sentry)
- [ ] Métricas (Prometheus)
- [ ] Cache de resumos

---

## 💡 Dicas Finais

1. **Sempre verifique** o status no Koyeb antes de debugar
2. **Aguarde 2-5 minutos** após deploy para testar
3. **Consulte os logs** no Koyeb em caso de erro
4. **Documente tudo** que fizer (criar arquivo SESSAO_*.md)
5. **Teste localmente** antes de fazer deploy em produção

---

**Desenvolvido com ❤️ usando Python + Google Gemini 2.5 Flash**

**Última revisão:** 03/02/2026
**Próxima revisão:** Quando houver mudanças significativas
