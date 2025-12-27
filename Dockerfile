FROM python:3.11-slim

LABEL mantainer="https://github.com/denisms7"

# Evita arquivos .pyc e melhora logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV LANG C.UTF-8

WORKDIR /app

# Dependências do sistema (opcional, mas seguro)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Porta padrão do Streamlit
EXPOSE 8501
