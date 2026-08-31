# Stage 1: build React frontend
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ ./
RUN npm run build


# Stage 2: Python API + static files
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-render.txt ./

# CPU-only PyTorch keeps image smaller; install separately for better caching
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements-render.txt

COPY . .
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

RUN chmod +x start.sh \
    && mkdir -p results/recordings models

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8000
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

EXPOSE 8000

CMD ["./start.sh"]
