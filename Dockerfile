FROM python:3.9-slim

WORKDIR /app

# Copiar requirements.txt
COPY requirements.txt .

# Actualizar pip, setuptools y wheel al iniciar
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar tu código
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
