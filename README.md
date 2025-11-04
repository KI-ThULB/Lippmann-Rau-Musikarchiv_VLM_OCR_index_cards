# Lippmann-Rau Archiv OCR - Multi-Batch-Verarbeitung via VLM

Automatisierte Metadaten-Extraktion von 43.372 digitalisierten Karteikarten (JPGs) mit dem Vision Language Model qwen3-vl-8b-instruct. Verarbeitung wird in diesem Workflow über die OpenRouter API kostenpflichtig abgwickelt. Mehr hierzu: Siehe **WICHTIGE INFO** am Ende. 

## 📋 Übersicht

- **86 Batch-Ordner** mit je ~500 Karteikarten
- **Parallele Verarbeitung** mit konfigurierbaren Workers
- **Checkpoint-System** für unterbrechbare Verarbeitung
- **Pro-Batch-CSV** + finale Gesamt-CSV
- **Umfassende Fehlerbehandlung** und Logging

## 🚀 Schnellstart

### 1. Installation

```bash
pip install pandas requests
```

### 2. Konfiguration anpassen

Öffne `Lippmann-Rau_VLM_OCR_MultiBatch.py` und passe an:

```python
# Zeile 22-23: Dein Verzeichnis
BASE_INPUT_DIR = "/pfad/zu/deinen/JPEG-Ordnern"

# Zeile 27: Batch-Ordner-Muster
BATCH_PATTERN = "Batch_*"  # oder "*" für alle Unterordner

# Zeile 34-36: Modellauswahl
MODEL_NAME = "qwen3-vl:8b"          # empfohlen
# MODEL_NAME = "qwen2.5vl:32b"      # dein aktuelles Modell
# MODEL_NAME = "qwen3-vl:32b"       # beste Qualität

# Zeile 39: Performance
MAX_WORKERS = 5  # bei starkem Server: 8-10
```

### 3. Verarbeitung starten

```bash
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
```

**Wichtig:** Bei Unterbrechung (Ctrl+C) wird der Fortschritt gespeichert!

## 📁 Verzeichnisstruktur

### Eingabe (anpassen!)
```
/dein/pfad/JPEG/
├── Batch_001/
│   ├── karte_001.jpg
│   ├── karte_002.jpg
│   └── ...
├── Batch_002/
│   └── ...
└── ...
```

### Ausgabe (automatisch erstellt)
```
output_batches/
├── csv/
│   ├── Batch_001.csv
│   ├── Batch_002.csv
│   └── ...
├── json/
│   ├── Batch_001/
│   │   ├── karte_001.json
│   │   └── ...
│   └── ...
├── metadata_vlm_complete.csv    ← FINALE GESAMT-CSV
├── batch_progress.json
└── vlm_errors.log
```

## 🎯 Extrahierte Felder

Jede Karteikarte wird in diese Felder extrahiert:

| Feld | Beschreibung | Beispiel |
|------|--------------|----------|
| **Datei** | Dateiname | `karte_12345.jpg` |
| **Batch** | Batch-Ordner | `Batch_042` |
| **Komponist** | Name | `Zimmermann, Rolf` |
| **Signatur** | Archiv-Signatur | `Spez.12.433` |
| **Titel** | Werktitel | `Sonate für Violine` |
| **Textanfang** | Liedtext/Incipit | `Es war einmal...` |
| **Verlag** | Verlagsangabe | `Peters Leipzig` |
| **Material** | Materialart | `1 Part. u. Stimmen` |
| **Textdichter** | Autor des Textes | `Goethe, Johann W.` |
| **Bearbeiter** | Arrangeur | `Müller, Hans` |
| **Bemerkungen** | Zusatzinfos | `Handschriftlich` |

## ⚙️ Erweiterte Konfiguration

### Performance-Tuning

```python
# Für schnellen Server mit guter API
MAX_WORKERS = 10
MAX_RETRIES = 2

# Für langsame/instabile Verbindung
MAX_WORKERS = 3
MAX_RETRIES = 5
RETRY_DELAY = 5
```

### Modellauswahl

| Modell | Vorteile | Nachteile |
|--------|----------|-----------|
| `qwen3-vl:8b` | ✅ Beste OCR<br>✅ 32 Sprachen<br>✅ Schnell | Benötigt neuere API |
| `qwen2.5vl:32b` | ✅ Sehr gut<br>✅ Getestet | Langsamer |
| `qwen3-vl:32b` | ✅ Beste Qualität | 🐌 Am langsamsten |

**Empfehlung:** Start mit `qwen3-vl:8b`, bei Problemen zurück auf `qwen2.5vl:32b`

### Batch-Ordner-Muster

Verschiedene Namenskonventionen:

```python
# Beispiel 1: "Batch_001", "Batch_002", ...
BATCH_PATTERN = "Batch_*"

# Beispiel 2: "001", "002", "003", ...
BATCH_PATTERN = "[0-9][0-9][0-9]"

# Beispiel 3: Alle Unterordner
BATCH_PATTERN = "*"
```

## 📊 Analyse der Ergebnisse

Nach der Verarbeitung:

```bash
python3 analyze_results.py
```

**Generiert:**
- `field_completeness.csv` - Vollständigkeit pro Feld
- `batch_statistics.csv` - Statistiken pro Batch
- `komponisten_frequency.csv` - Häufigste Komponisten
- `problematic_cards.csv` - Karteikarten mit wenig Daten
- `missing_signatures.csv` - Karten ohne Signatur

## 🔧 Problemlösung

### Problem: "Keine Batch-Ordner gefunden"

**Lösung:**
1. Prüfe `BASE_INPUT_DIR` - ist der Pfad korrekt?
2. Passe `BATCH_PATTERN` an (siehe oben)
3. Teste manuell:
   ```python
   from pathlib import Path
   list(Path("/dein/pfad").glob("*"))
   ```

### Problem: "API-Fehler" oder Timeouts

**Lösung:**
1. Reduziere `MAX_WORKERS` (z.B. auf 3)
2. Erhöhe `RETRY_DELAY` (z.B. auf 5)
3. Prüfe API-Limit deines Servers
4. Teste mit einem kleinen Batch zuerst

### Problem: Schlechte OCR-Qualität

**Lösungen:**
- ✅ Wechsle zu `qwen3-vl` (bessere OCR)
- ✅ Prüfe Bildqualität (mindestens 300 DPI empfohlen)
- ✅ Passe Prompt an für spezifische Probleme
- ✅ Setze `temperature: 0.0` für konsistentere Ergebnisse

### Problem: Verarbeitung unterbrochen

**Gut!** Das Skript speichert automatisch:
- ✅ Bereits verarbeitete Karten (Checkpoint)
- ✅ Abgeschlossene Batches (Progress)

Einfach neu starten → macht da weiter, wo es aufgehört hat.

## 📈 Performance-Erwartungen

### Testlauf (1 Batch = 500 Karten)

Empfohlene Reihenfolge:
1. **Test mit 1 Batch** (10-20 Minuten)
2. Prüfe Qualität der Ergebnisse
3. Falls gut → starte alle 86 Batches

### Hochrechnung (43.000 Karten)

| Workers | Modell | Geschätzte Dauer |
|---------|--------|------------------|
| 5 | qwen3-vl:8b | ~24-36 Stunden |
| 10 | qwen3-vl:8b | ~12-18 Stunden |
| 5 | qwen2.5vl:32b | ~36-48 Stunden |

**Tipp:** Lasse das Skript über Nacht laufen!

## 🎓 Workflow-Empfehlung

### Phase 1: Test (Tag 1)
```bash
# 1. Einen Batch testen
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
# [Ctrl+C nach 1-2 Batches]

# 2. Ergebnisse prüfen
python3 analyze_results.py

# 3. CSV öffnen und Stichproben kontrollieren
```

### Phase 2: Vollständige Verarbeitung (Tag 2-3)
```bash
# Alle Batches verarbeiten
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
# [Über Nacht laufen lassen]
```

### Phase 3: Auswertung (Tag 4)
```bash
# Finale Analyse
python3 analyze_results.py

# Manuelle Nachbearbeitung der problematischen Karten
# (siehe problematic_cards.csv)
```

## 🔐 API-Key-Verwaltung

### Sicherer Umgang

**Nicht empfohlen:**
```python
api_key = "sk-123456..."  # Hardcoded im Skript
```

**Empfohlen (aktuell):**
```bash
# Wird beim Start sicher abgefragt
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
# → API-Key: [eingeben ohne Echo]
```

**Alternative (Umgebungsvariable):**
```python
# In der Konfiguration:
import os
API_KEY = os.getenv('QWEN_API_KEY')

# Terminal:
export QWEN_API_KEY="sk-..."
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
```

## 📞 Support

Bei Problemen:
1. Prüfe `vlm_errors.log` für Details
2. Teste mit reduziertem `MAX_WORKERS`
3. Prüfe API-Status deines Servers
4. Kontrolliere Bildqualität einer Stichprobe

## 🎉 Nach erfolgreicher Verarbeitung

**Du erhältst:**
- ✅ `metadata_vlm_complete.csv` mit ~43.000 Einträgen
- ✅ 86 einzelne Batch-CSVs (für Zwischenauswertungen)
- ✅ JSON-Dateien aller Karten (für Re-Processing)
- ✅ Umfassende Statistiken und Qualitätsberichte

**Nächste Schritte:**
1. Import in Datenbank (Excel, Access, SQL)
2. Qualitätskontrolle anhand der Analyse-Reports
3. Nachbearbeitung problematischer Karten
4. Veröffentlichung im Archivkatalog

**WICHTIGE INFO**
- Das Haupt-Skript sowie alle zugehörigen Files und Dokumentationen wurden mit Unterstützung von KI-Tools erstellt (Claude Sonnet 4,5 sowie ChatGPT)
- Bitte je nach eigenem Anwendungsfall Skripte, Pfade und Dateibenennungen anpassen
- Workflow wird hier über Open-Router API abgewickelt
- kostenpflichtiger Workflow (hier ca. 2.649 für den Prompt + 1.000 Tokens für die Fertigstellung der Datenverarbeitung / pro JPG = ~ 0,0011 $ / pro Karte) (Stand: 01.11.2025)
- Gesamtkosten der Verarbeitung aller 43.372 Karten belief sich hier auf ca. 17,60 $.
  
  
