FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para banco de dados
RUN mkdir -p /app/data

# Comando para executar o bot
CMD ["python", "bot.py"]
