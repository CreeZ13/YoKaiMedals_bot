# Base image Python
FROM python:3.10-slim
# Cartella di lavoro nel container
WORKDIR /app
# Copia tutto il progetto, inclusa la cartella data
COPY . /app
# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt
# Comando per avviare il bot
CMD ["python", "main.py"]
