# Stage 1: build React frontend
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ ./
RUN npm run build


# Stage 2: Python API + static files (lite mode — no PyTorch)
FROM python:3.11-slim

WORKDIR /app

COPY requirements-render.txt ./
RUN pip install --no-cache-dir -r requirements-render.txt

COPY . .
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

RUN chmod +x start.sh \
    && mkdir -p results/recordings

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8000
ENV LITE_MODE=1
ENV OMP_NUM_THREADS=1

EXPOSE 8000

CMD ["./start.sh"]
