# Usa uma imagem oficial leve do Python baseada em Debian Linux
FROM python:3.11-slim

# Evita que o Python escreva arquivos .pyc no disco e bufferize o output de logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho interno do contêiner
WORKDIR /app

# Instala as dependências de sistema necessárias para compilar pacotes C
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia primeiro apenas o arquivo de dependências para aproveitar o cache de camadas do Docker
COPY requirements.txt .

# Instala as dependências do Python isoladas dentro do contêiner
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código-fonte do projeto para dentro do contêiner
COPY . .

# COMANDO ATUALIZADO: Suporta a porta do Railway ou cai para 8000 se rodar local
CMD ["sh", "-c", "uvicorn src.app:app --host 0.0.0.0 --port ${PORT:-8000}"]