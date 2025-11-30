# ----------------------------------------------------
# 1️⃣ Fase de build — instala dependências com cache
# ----------------------------------------------------
FROM python:3.10-slim AS build

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Instala dependências necessárias para compilação
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ curl && \
    rm -rf /var/lib/apt/lists/*

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------------
# 2️⃣ Fase final — imagem limpa para produção
# ----------------------------------------------------
FROM python:3.10-slim

WORKDIR /app

# Copia dependências instaladas
COPY --from=build /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=build /usr/local/bin /usr/local/bin

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=America/Recife

# Copia os arquivos do projeto
COPY . .

# Cria diretórios necessários
RUN mkdir -p logs backups data fotos

# Expor a porta padrão Streamlit
EXPOSE 8501

# Comando final de execução
CMD sh -c 'streamlit run app/dashboard.py --server.address=0.0.0.0 --server.port="${PORT:-8501}"'
