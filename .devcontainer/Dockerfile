# Dockerfile
FROM python:3.11-slim

# Sett arbeidsmappe i containeren
WORKDIR /app

# Kopier krav og installer dem
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Kopier resten av koden
COPY . .

# Kjør appen med uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
