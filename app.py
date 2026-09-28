from flask import Flask, request
import os
import asyncio
import discord
import logging

# --- Logging konfigurieren ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Flask App Setup ---
app = Flask(__name__)
# Verhindert, dass Flask eine Meldung ausgibt, wenn die Route das erste Mal aufgerufen wird.
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME', 'localhost:5000') # Wird von Render überschrieben

# --- Discord Bot Setup ---
TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
if not TOKEN:
    logging.error("DISCORD_BOT_TOKEN Umgebungsvariable nicht gefunden!")
    # Hier könnten Sie die App stoppen oder eine Fehlermeldung anzeigen
    # exit() # Nicht empfohlen, da es den Server beendet.

# Intents: Stellen Sie sicher, dass die benötigten Intents aktiviert sind
# Beispiel: Wenn Ihr Bot Nachrichten lesen soll:
intents = discord.Intents.default()
intents.message_content = True # Dies ist oft notwendig für Bots, die Nachrichten lesen

client = discord.Client(intents=intents)

# --- Asynchroner Bot-Start ---
# Wir brauchen einen Weg, den Bot zu starten und die Anwendung am Laufen zu halten.
# Eine einfache Möglichkeit ist, den Bot erst zu starten, wenn die App angepingt wird.
# Aber besser ist es, ihn direkt zu starten, wenn Gunicorn die app:app lädt.

bot_task = None
loop = None

async def start_bot_async():
    try:
        await client.start(TOKEN)
    except discord.errors.LoginFailure:
        logging.error("Ungültiger Discord Token.")
    except Exception as e:
        logging.error(f"Fehler beim Starten des Bots: {e}")

# --- Flask Route zum Überprüfen ---
@app.route('/')
def index():
    # Diese Route wird von UptimeRobot oder anderen Ping-Diensten aufgerufen.
    # Sie stellt sicher, dass die Instanz lebt.
    if client.is_closed():
         status = "Client ist geschlossen."
    elif client.is_ready():
         status = f"Bot ist bereit als {client.user}."
    else:
         status = "Bot wird gerade initialisiert."
    return f"<h1>Render Bot Service</h1><p>{status}</p>"

# --- Bot Events (Beispiele) ---
@client.event
async def on_ready():
    logging.info(f'Bot gestartet als {client.user} auf Render.com!')
    # Wenn Sie hier Dinge tun wollen, die nicht blockieren, ist das gut.
    # Z.B. await client.change_presence(...)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$renderhello'):
        await message.channel.send('Hallo! Dein Bot läuft auf Render!')
    # Füge hier deine eigentliche Bot-Logik ein

# --- Hauptfunktion für Gunicorn ---
# Diese Funktion wird von Gunicorn aufgerufen, um die Flask-App zu erhalten.
def run_app():
    global loop, bot_task
    # Da Render die PORT-Variable setzt, ist sie hier wichtig.
    port = int(os.environ.get('PORT', 5000)) # Standard-Port, falls nicht gesetzt

    # Der Bot muss im Hintergrund laufen.
    # Wir müssen einen asyncio-Eventloop starten und dort den Bot laufen lassen.
    # Dies ist komplex, da Gunicorn auch einen eigenen Eventloop hat.
    # Einfacher Ansatz: den Bot erst über die Route starten.
    # Besserer Ansatz: versuchen, den Bot hier zu starten.
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Wenn bereits ein Loop läuft (was bei Gunicorn der Fall sein könnte),
        # erstellen wir eine neue Aufgabe.
        bot_task = loop.create_task(start_bot_async())
        logging.info("Bot-Task erstellt auf laufendem Loop.")
    else:
        # Wenn kein Loop läuft, starten wir einen neuen.
        bot_task = loop.create_task(start_bot_async())
        logging.info("Neuer Bot-Task und Loop gestartet.")

    # Gunicorn wird dann die Flask App von hier aus starten.
    # Gunicorn sucht nach einer "app" Objekt in der angegebenen Datei (hier app.py)
    # und bindet sich an den von Render vorgegebenen Port.
    # Wir geben hier nichts zurück, sondern lassen Gunicorn die Arbeit machen.
    pass # Gunicorn lädt die App selbst.

# Wenn diese Datei direkt ausgeführt wird (nicht über Gunicorn/Render),
# starten wir Flask und versuchen den Bot zu starten.
if __name__ == '__main__':
    # Versuchen, den Bot zu starten, wenn die Datei direkt ausgeführt wird (lokale Tests)
    if TOKEN:
        loop = asyncio.get_event_loop()
        bot_task = loop.create_task(start_bot_async())
        logging.info("Lokaler Bot-Startversuch...")

    port = int(os.environ.get('PORT', 5000))
    # Starte den Flask-Entwicklungsserver für lokale Tests
    # ACHTUNG: Dieser Flask-Server ist NICHT für Produktion! Gunicorn ist es.
    # Aber dieser Teil hilft beim Testen der bot_task Logik lokal.
    try:
        app.run(host='0.0.0.0', port=port, debug=True) # Debug=True für lokale Tests
    except Exception as e:
        logging.error(f"Fehler beim Starten des Flask-Entwicklungsservers: {e}")
    finally:
        # Sicherstellen, dass der Bot-Task sauber beendet wird, wenn der Server stoppt.
        if bot_task and not bot_task.done():
            bot_task.cancel()
            try:
                loop.run_until_complete(bot_task)
            except asyncio.CancelledError:
                pass
        if loop and loop.is_running():
             loop.stop()
