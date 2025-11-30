# Nome do arquivo: Dockerfile

FROM python:3.10-slim

LABEL maintainer="Caio Felipe <caiofelipead@gmail.com>"
LABEL description="Scout Pro - Sistema de Scouting SCR"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . .

# Cria diretórios necessários
RUN mkdir -p logs backups data fotos

# Expor a porta padrão HTTP
EXPOSE  $PORT

# Comando padrão: Streamlit ouvindo na porta 80
ENV PORT=8501
CMD ["sh", "-c", "streamlit run app/dashboard.py --server.address=0.0.0.0 --server.port=${PORT}"]
