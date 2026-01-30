# 🚀 Deploy Bot Telegram no Koyeb - Guia Completo

## ✅ Preparação (Já Feito)
- [x] Código no GitHub
- [x] Dockerfile configurado
- [x] Health check server implementado
- [x] Variáveis de ambiente definidas

---

## 📋 PASSO A PASSO - DEPLOY NO KOYEB

### **PASSO 1: Criar Conta no Koyeb**

1. Acesse: **https://app.koyeb.com/auth/signup**
2. Escolha uma das opções:
   - ✅ **Sign up with GitHub** (RECOMENDADO - mais rápido)
   - Sign up with email
3. Confirme sua conta se necessário

---

### **PASSO 2: Conectar GitHub ao Koyeb**

1. No dashboard do Koyeb, clique em **"Create App"**
2. Escolha **"GitHub"** como source
3. Se for a primeira vez:
   - Clique em **"Connect GitHub"**
   - Autorize o Koyeb a acessar seus repositórios
   - Selecione **"Only select repositories"**
   - Escolha: **telegram-summarizer-bot**
   - Clique em **"Install & Authorize"**

---

### **PASSO 3: Configurar o Deploy**

#### 3.1 - Selecionar Repositório
- **Repository:** `diegopaixao89/telegram-summarizer-bot`
- **Branch:** `main`

#### 3.2 - Builder
- **Builder:** Docker
- **Dockerfile:** Deixe como `Dockerfile` (já detecta automaticamente)

#### 3.3 - Nome do App
- **App name:** `telegram-bot-resumildo` (ou qualquer nome que preferir)

#### 3.4 - Região
- **Region:** `Frankfurt (FRA)` ou `Washington D.C. (WAS)`
  - (Escolha a mais próxima do Brasil)

#### 3.5 - Instance Type
- **Type:** `Nano` (Free tier - suficiente para o bot)
- **Replicas:** 1

---

### **PASSO 4: Adicionar Variáveis de Ambiente (IMPORTANTE!)**

Na seção **"Environment Variables"**, clique em **"Add Variable"** e adicione:

#### Variável 1:
- **Name:** `TELEGRAM_BOT_TOKEN`
- **Value:** `8543784435:AAGSgZ14cIO7kOsCc53toM2k5pTirqWmHac`
- **Type:** Secret (marque como secret/confidencial)

#### Variável 2:
- **Name:** `GROQ_API_KEY`
- **Value:** `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`
- **Type:** Secret (marque como secret/confidencial)

#### Variável 3:
- **Name:** `PORT`
- **Value:** `8080`
- **Type:** Plain text

---

### **PASSO 5: Configurar Health Check (Opcional mas Recomendado)**

Na seção **"Health checks"**:
- **Port:** `8080`
- **Path:** `/health`
- **Protocol:** HTTP

---

### **PASSO 6: Deploy!**

1. Revise todas as configurações
2. Clique no botão **"Deploy"** no final da página
3. Aguarde o build e deploy (5-10 minutos)

---

## 🔍 VERIFICAR STATUS DO DEPLOY

### Durante o Deploy:
- Você verá o status "Building..." → "Deploying..." → "Healthy"
- Pode clicar em **"View Logs"** para acompanhar em tempo real

### Após o Deploy:
- Status deve estar: **✅ Healthy** (verde)
- Se estiver amarelo ou vermelho, veja os logs para diagnosticar

---

## 🧪 TESTAR O BOT

1. Abra o Telegram
2. Vá no grupo onde o bot está
3. Envie: `/stats@resumildobot`
4. O bot deve responder com as estatísticas

Se não responder:
- Aguarde 1-2 minutos (pode estar inicializando)
- Verifique os logs no Koyeb
- Teste: `/start@resumildobot`

---

## 📊 MONITORAMENTO

### Ver Logs:
1. No Koyeb dashboard
2. Clique no seu app
3. Vá na aba **"Logs"**
4. Logs em tempo real aparecerão

### Ver Métricas:
1. Aba **"Metrics"**
2. Veja CPU, RAM, Network

---

## 🔄 ATUALIZAÇÕES FUTURAS

Quando você fizer mudanças no código:

1. Commit e push para o GitHub:
   ```bash
   cd ~/Desktop/telegram-summarizer-bot
   git add .
   git commit -m "Sua mensagem"
   git push
   ```

2. O Koyeb vai automaticamente:
   - Detectar o push
   - Fazer rebuild
   - Fazer redeploy
   - **Deploy automático!** 🎉

---

## ⚠️ IMPORTANTE - DEPOIS DO DEPLOY

### REVOGAR CREDENCIAIS (Segurança!)

Suas credenciais foram expostas durante o desenvolvimento. Depois que confirmar que está tudo funcionando:

#### 1. Revogar Token do Telegram:
1. Abra Telegram → @BotFather
2. `/mybots`
3. Selecione "Resumildo"
4. API Token → **Revoke current token**
5. Copie o novo token
6. No Koyeb: Settings → Environment Variables → Edite `TELEGRAM_BOT_TOKEN`
7. Salve (vai fazer redeploy automático)

#### 2. Revogar Groq API Key:
1. Acesse: https://console.groq.com/keys
2. Delete a key atual
3. Crie nova key
4. No Koyeb: Settings → Environment Variables → Edite `GROQ_API_KEY`
5. Salve

---

## 🆘 TROUBLESHOOTING

### Erro: "Build failed"
- Verifique se o Dockerfile está correto
- Veja os logs do build
- Verifique se requirements.txt está correto

### Erro: "Health checks failing"
- Verifique se a porta 8080 está correta
- Verifique se o health check path é `/health`
- **Pode ignorar se o bot estiver funcionando**

### Bot não responde:
- Verifique logs no Koyeb
- Confirme que as variáveis de ambiente estão corretas
- Teste remover e adicionar o bot no grupo novamente
- Verifique Privacy Mode no @BotFather

---

## 📝 COMANDOS DO BOT

- `/start@resumildobot` - Iniciar e ver instruções
- `/resumo@resumildobot` - Resumo de 2000 mensagens
- `/resumo_rapido@resumildobot` - Resumo de 500 mensagens
- `/resumo_hoje@resumildobot` - Resumo do dia
- `/resumo_personalizado@resumildobot <N>` - Resumo de N mensagens
- `/stats@resumildobot` - Estatísticas do grupo

---

## 🎯 PRÓXIMOS PASSOS

- [ ] Deploy no Koyeb
- [ ] Testar todos os comandos
- [ ] Verificar Privacy Mode no @BotFather
- [ ] Revogar credenciais antigas
- [ ] Adicionar bot como admin no grupo (permissão de ler mensagens)

---

## 💰 LIMITES DO FREE TIER KOYEB

- ✅ 1 Web Service gratuito
- ✅ Nano instance (512MB RAM, 0.1 vCPU)
- ✅ Deploy ilimitado
- ✅ 100GB de tráfego/mês
- ✅ Mais que suficiente para um bot de Telegram!

---

**Criado:** 30/01/2026
**Bot:** @resumildobot
**Repositório:** https://github.com/diegopaixao89/telegram-summarizer-bot
