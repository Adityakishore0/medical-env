FROM python:3.11-slim
LABEL maintainer="medical-ai-doctor-team"
LABEL description="Free AI Doctor OpenEnv — Healthcare for Everyone"
LABEL version="1.0.0"
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY env/ ./env/
COPY data/ ./data/
COPY main.py .
COPY inference.py .
COPY openenv.yaml .
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]