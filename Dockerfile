FROM python:3.10-slim

WORKDIR /app

# Instala dependências do sistema para o ReportLab e ferramentas básicas
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    zlib1g-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as bibliotecas do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Expõe a porta para o Streamlit
EXPOSE 8501

# Comando para rodar o Streamlit no Render
CMD ["sh", "-c", "streamlit run app.py --server.port $PORT --server.address 0.0.0.0"]