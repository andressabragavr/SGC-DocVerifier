FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema (se precisar compilar algo)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar pacotes Python necessários
RUN pip install --no-cache-dir fastapi uvicorn pydantic requests openai langgraph rapidfuzz python-dotenv

# Copiar código
COPY . .

EXPOSE 8000

CMD ["uvicorn", "agent.app:app", "--host", "0.0.0.0", "--port", "8000"]
