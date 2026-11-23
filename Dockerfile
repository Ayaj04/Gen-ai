FROM python:3.11-slim

WORKDIR /app

# Keep numerical libraries from creating large thread pools on 512 MB hosts.
ENV OPENBLAS_NUM_THREADS=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false

COPY app/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cache the verified ONNX files on disk without importing them at API startup.
RUN python -m app.cache_embedding_model

EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
