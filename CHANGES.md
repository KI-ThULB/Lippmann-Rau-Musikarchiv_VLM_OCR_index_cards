# 📦 Lippmann-Rau Multi-Batch OCR - Übersicht

## ✨ Neue Features gegenüber deinem Original-Skript

### 🎯 Hauptverbesserungen

1. **Multi-Ordner-Verarbeitung**
   - Verarbeitet automatisch alle 86 Batch-Ordner
   - Kein manuelles Umkopieren mehr nötig
   - Flexible Batch-Ordner-Erkennung via `BATCH_PATTERN`

2. **Pro-Batch-CSV**
   - Jeder Batch erzeugt seine eigene CSV
   - Einfachere Fehlersuche und Teilauswertungen
   - Batch-Name als Spalte für Nachverfolgbarkeit

3. **Automatische Zusammenführung**
   - Alle Batch-CSVs werden automatisch zur Gesamt-CSV kombiniert
   - `metadata_vlm_complete.csv` enthält alle ~43.000 Einträge
   - Zusätzlich: Manuelles Merge-Skript als Backup

4. **Batch-Level-Checkpoints**
   - Fortschritt wird pro Batch und gesamt gespeichert
   - Bei Abbruch: Nächster Start setzt bei letztem Batch fort
   - Bereits verarbeitete Batches werden übersprungen

5. **Verbesserte Verzeichnisstruktur**
   ```
   output_batches/
   ├── csv/           ← 86 einzelne Batch-CSVs
   ├── json/
   │   ├── Batch_001/ ← JSON-Dateien organisiert nach Batch
   │   ├── Batch_002/
   │   └── ...
   └── metadata_vlm_complete.csv  ← FINALE GESAMT-CSV
   ```

6. **Qwen3-VL-Unterstützung**
   - Aktualisiert für neueste Qwen3-VL-Modelle
   - Bessere OCR-Leistung (32 Sprachen)
   - Optimiert für handschriftlichen Text
   - Abwärtskompatibel mit Qwen2.5-VL

### 📊 Zusätzliche Tools

#### `analyze_results.py` - Umfassende Datenanalyse
- Vollständigkeitsstatistiken pro Feld
- Batch-Vergleiche
- Top-Komponisten-Liste
- Signatur-Muster-Analyse
- Identifikation problematischer Karten
- Exportiert 5+ Analyse-CSVs

#### `merge_csvs.py` - Manuelles CSV-Merging
- Backup-Tool falls Auto-Merge fehlschlägt
- Validiert alle Batch-CSVs
- Zeigt Statistiken während des Merge

### 🔧 Konfigurationsoptionen

**Original hatte:**
- Ein INPUT_DIR
- Ein OUTPUT_CSV

**Neu:**
- `BASE_INPUT_DIR` - Hauptverzeichnis mit allen Batches
- `BATCH_PATTERN` - Flexibles Matching von Batch-Ordnern
- `OUTPUT_BASE` - Organisierte Ausgabestruktur
- Modellauswahl: Qwen2.5-VL oder Qwen3-VL

### ⚡ Performance-Verbesserungen

1. **Batch-Level-Parallelität**
   - Jeder Batch wird komplett verarbeitet bevor zum nächsten gewechselt wird
   - Besseres Checkpoint-Management
   - Reduzierter Memory-Footprint

2. **Optimiertes Logging**
   - Batch-Name im Error-Log
   - Strukturierte JSON-Outputs pro Batch
   - Separate Verzeichnisse für bessere Organisation

3. **Progress-Tracking**
   - Gesamtfortschritt über alle Batches
   - ETA-Berechnung berücksichtigt mehrere Batches
   - `batch_progress.json` für Übersicht

### 📝 Verbesserter Prompt

**Neue Regeln im Prompt:**
- Explizite Anweisung für handschriftlichen Text
- Markierung unleserlicher Stellen mit `[unleserlich]`
- Strikte "NUR JSON"-Anweisung (keine Markdown-Blöcke)
- Klarere Signatur-Format-Beispiele

### 🛡️ Robustheit

1. **Fehlerbehandlung**
   - Batch-Level: Ein fehlerhafter Batch bricht nicht alles ab
   - Card-Level: Fehlerhafte Karten werden geloggt, aber Batch läuft weiter
   - API-Level: Exponentielles Backoff bei Retry

2. **Wiederaufnahme**
   - Checkpoint auf Datei-Level (wie Original)
   - **NEU:** Checkpoint auf Batch-Level
   - `batch_progress.json` trackt abgeschlossene Batches

3. **Validierung**
   - Prüft Batch-Ordner-Existenz vor Start
   - Warnt bei fehlenden Batches
   - Validiert CSV-Output nach jedem Batch

## 🚦 Schnellstart-Vergleich

### Original-Workflow
```bash
# Für jeden der 86 Batches:
1. Ordner manuell kopieren nach INPUT_DIR
2. python3 script.py
3. CSV umbenennen zu Batch_XX.csv
4. Nächsten Batch kopieren...
5. Am Ende alle CSVs manuell mergen
```

### Neuer Workflow
```bash
# Einmalig:
1. BASE_INPUT_DIR setzen
2. BATCH_PATTERN anpassen (falls nötig)
3. python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
   → Läuft durch alle 86 Batches automatisch
   → Erzeugt 86 CSVs + 1 Gesamt-CSV
4. python3 analyze_results.py
   → Umfassende Statistiken
```

## 📈 Erwartete Zeiteinsparung

**Original-Ansatz:** ~50-60 Stunden
- 86 × (Kopieren + Verarbeitung + CSV-Handling) + Finales Mergen

**Neuer Ansatz:** ~24-36 Stunden
- Automatische Batch-Verarbeitung ohne manuelle Eingriffe
- **~40-50% Zeiteinsparung!**

## 🎓 Empfohlene Nutzung

### Phase 1: Setup (15 Minuten)
1. Konfiguration anpassen (siehe README.md)
2. Test mit 1-2 Batches
3. Qualität prüfen

### Phase 2: Produktion (24-36 Stunden)
```bash
python3 Lippmann-Rau_VLM_OCR_MultiBatch.py
# Über Nacht laufen lassen - komplett unbeaufsichtigt
```

### Phase 3: Analyse (30 Minuten)
```bash
python3 analyze_results.py
# Prüfe die generierten Statistiken
# Identifiziere problematische Karten
```

### Phase 4: Nachbearbeitung (individuell)
- Import in Datenbank
- Manuelle Korrektur problematischer Karten
- Qualitätssicherung

## 📚 Dateien-Übersicht

| Datei | Beschreibung | Verwendung |
|-------|--------------|------------|
| **Lippmann-Rau_VLM_OCR_MultiBatch.py** | Haupt-Skript | Täglich - Verarbeitung |
| **analyze_results.py** | Analyse-Tool | Nach Verarbeitung |
| **merge_csvs.py** | Manuelles Merge | Bei Bedarf/Fehler |
| **README.md** | Dokumentation | Referenz |

## 🔄 Migration von deinem Original-Skript

**Was bleibt gleich:**
- ✅ API-Aufbau
- ✅ Prompt-Struktur (leicht verbessert)
- ✅ Fehlerbehandlung-Logik
- ✅ Parallele Verarbeitung
- ✅ Checkpoint-System

**Was ist neu:**
- 🆕 Multi-Batch-Loop
- 🆕 Batch-spezifische Outputs
- 🆕 Automatisches CSV-Merging
- 🆕 Analyse-Tools
- 🆕 Batch-Level-Progress-Tracking

**Migration:**
Dein Original-Skript kann parallel weiterlaufen - die neuen Skripte schreiben in `output_batches/`, nicht in deine bisherigen Verzeichnisse.

## ⚠️ Wichtige Hinweise

1. **API-Limits:** Prüfe die Rate-Limits deiner API
2. **Speicherplatz:** ~86 × 500 JSON + CSVs = ca. 2-5 GB
3. **Internet:** Stabile Verbindung für 24-36h empfohlen
4. **Backup:** Erste Testläufe mit Kopie der Daten

## 🎉 Viel Erfolg!

Bei Fragen oder Problemen:
- Prüfe `README.md` für detaillierte Anleitung
- Check `vlm_errors.log` für Fehlerdetails
- Nutze `analyze_results.py` für Qualitätsprüfung

**Happy Digitizing! 📚🎵**
