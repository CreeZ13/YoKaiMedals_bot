# --- Stage 1: base ---
FROM python:3.10-slim

# Setta la working directory
WORKDIR /app

# Copia i file principali del progetto
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice del bot
COPY . .

# Crea la cartella /data dove sarà montato il volume persistente
RUN mkdir -p /data

# Copia i file iniziali nella cartella /data
# Solo al primo deploy servirà a inizializzare il volume
COPY ./data/database.db /data/database.db
COPY ./data/yokai_list.json /data/yokai_list.json
COPY ./data/admin_actions.log /data/admin_actions.log

# Setta le variabili d'ambiente (possono essere sovrascritte da .env o fly.toml)
ENV DB_PATH=/data/database.db
ENV LOG_PATH=/data/admin_actions.log
ENV YOKAI_JSON_PATH=/data/yokai_list.json

# Comando per avviare il bot
CMD ["python", "main.py"]
