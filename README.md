# Gaming Business Software

# ⚠️ Work in Progress
This project is under active development and not production-ready yet.

Eine moderne Business-Software für Gaming-Softwareentwicklungsfirmen mit Dark Mode Design.

## Features

- Modernes Dark Mode Design
- Dashboard mit Übersicht über wichtige Informationen
- Login-System mit Online-Datenbank-Anbindung
- To-Do-Listen-Management
- Echtzeit-Chat mit Benachrichtigungen
- Stempeluhr-System
- Kalender-Integration
- Dateiverwaltungssystem

## Installation

1. Stellen Sie sicher, dass Python 3.8+ installiert ist
2. Installieren Sie MongoDB und starten Sie den MongoDB-Server
3. Klonen Sie das Repository
4. Installieren Sie die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```
5. Kopieren Sie `.env.example` zu `.env` und passen Sie die Konfiguration an

## Konfiguration

Die `.env`-Datei enthält wichtige Konfigurationseinstellungen:

- `DEBUG_MODE`: Aktiviert den Debug-Modus (überspringt Login)
- `DB_CONNECTION_STRING`: MongoDB-Verbindungsstring
- `DB_NAME`: Name der Datenbank

## Starten der Anwendung

```bash
python main.py
```

## Entwicklung

Der Debug-Modus kann in der `.env`-Datei aktiviert werden, um das Login zu überspringen.

## Systemanforderungen

- Python 3.8+
- MongoDB
- PySide6
- Weitere Abhängigkeiten siehe `requirements.txt`
