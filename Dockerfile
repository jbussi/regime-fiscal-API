# Usa uma imagem oficial leve do Python
FROM python:3.11-slim

# Evita que o Python escreva arquivos .pyc e bufferize o output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto
COPY . .

# Expõe a porta interna que o Uvicorn vai rodar
EXPOSE 8000

# Comando para rodar a aplicação em produção (sem --reload)
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]