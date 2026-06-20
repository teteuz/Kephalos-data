FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Install CPU-only torch first to prevent camel-ai from pulling in CUDA/GPU libs
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD sh -c "gunicorn wsgi:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 300 --graceful-timeout 30 --keep-alive 5"
