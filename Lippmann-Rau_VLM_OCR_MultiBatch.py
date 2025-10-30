#!/usr/bin/env python3
"""
Lippmann-Rau Archiv Karteikarten OCR mit Qwen VL
Multi-Batch-Verarbeitung für 86 Ordner à ~500 Karten
Optimiert für große Mengen (43.000+ Karten)
"""

import os
import json
import base64
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import getpass
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import pickle
import glob

# === KONFIGURATION ===
# Hauptverzeichnis mit allen Batch-Ordnern
BASE_INPUT_DIR = "/Users/zu54tav/Desktop/Karteikarten/Karteikarten_Musikarchiv_Lippmann-Rau_Eisenach/JPEG"

# Muster für Batch-Ordner (anpassen falls nötig)
# Beispiele: "Batch_001", "Batch_002", ... oder "001", "002", ...
BATCH_PATTERN = "Batch_*"  # oder "*" für alle Unterordner

# Ausgabeverzeichnisse
OUTPUT_BASE = "output_batches"
JSON_OUT_BASE = os.path.join(OUTPUT_BASE, "json")
CSV_OUT_BASE = os.path.join(OUTPUT_BASE, "csv")
FINAL_CSV = os.path.join(OUTPUT_BASE, "metadata_vlm_complete.csv")
LOG_FILE = os.path.join(OUTPUT_BASE, "vlm_errors.log")
CHECKPOINT_FILE = os.path.join(OUTPUT_BASE, "batch_checkpoint.pkl")
PROGRESS_FILE = os.path.join(OUTPUT_BASE, "batch_progress.json")

# API Konfiguration
API_URL = "https://openwebui.test.uni-jena.de/api/v1/chat/completions"

# Wähle dein Modell:
# MODEL_NAME = "qwen2.5vl:32b"        # für Qwen2.5-VL
MODEL_NAME = "qwen3-vl:8b"          # für Qwen3-VL (empfohlen für bessere OCR)
# MODEL_NAME = "qwen3-vl:32b"       # für noch bessere Ergebnisse

# Performance Einstellungen
MAX_WORKERS = 5              # Anzahl paralleler API-Aufrufe
MAX_RETRIES = 3              # Wiederholungen bei Fehlern
RETRY_DELAY = 2              # Sekunden zwischen Wiederholungen
BATCH_SIZE = 500             # Erwartete Anzahl Karten pro Batch

# Felder die extrahiert werden sollen
FIELD_KEYS = [
    "Komponist", "Signatur", "Titel", "Textanfang",
    "Verlag", "Material", "Textdichter", "Bearbeiter", "Bemerkungen"
]

# Erstelle Verzeichnisstruktur
os.makedirs(JSON_OUT_BASE, exist_ok=True)
os.makedirs(CSV_OUT_BASE, exist_ok=True)

# Thread-safe Locks
stats_lock = Lock()
log_lock = Lock()

# === PROMPT FÜR STRUKTURIERTE EXTRAKTION ===
EXTRACTION_PROMPT = """Du bist ein Experte für die Digitalisierung historischer Archivkarteikarten. 

Analysiere diese Karteikarte aus dem Lippmann-Rau Musikarchiv Eisenach und extrahiere ALLE vorhandenen Informationen in folgende Felder:

**WICHTIGE REGELN:**
1. Extrahiere EXAKT was auf der Karte steht, ohne zu interpretieren
2. Komponisten-Namen haben oft das Format "Nachname, Vorname" (z.B. "Zimmermann, Rolf")
3. Signaturen haben folgende Formate:
   - Spez.XX.XXX (z.B. Spez.12.433)
   - Spez.XX.XXX [buchstabe] (z.B. Spez.16.734 w)
   - TOB XXXX (z.B. TOB 1728)
   - RTSO XXXX (z.B. RTSO 3953)
   - RTOB XXXX (z.B. RTOB 3891)
4. Wenn ein Feld leer ist, gib einen leeren String "" zurück
5. Beachte die Labels auf der Karte: "Komponist:", "Titel:", "Signatur:", etc.
6. Bei handschriftlichem Text: bestmögliche Transkription
7. Bei unleserlichen Stellen: markiere mit [unleserlich]

**FELDER:**
- Komponist: Name des Komponisten
- Signatur: Archiv-Signatur (siehe Formate oben)
- Titel: Titel des Musikstücks
- Textanfang: Anfang des Liedtexts oder zusätzliche Informationen
- Verlag: Verlagsangabe
- Material: Art des Materials (z.B. "1 Part. u. Stimmen", "2 Part. u. Mater.")
- Textdichter: Name des Textdichters
- Bearbeiter: Name des Bearbeiters
- Bemerkungen: Zusätzliche Bemerkungen

**AUSGABEFORMAT:**
Antworte NUR mit einem validen JSON-Objekt (KEINE Markdown-Codeblöcke, KEINE Erklärungen):

{
  "Komponist": "...",
  "Signatur": "...",
  "Titel": "...",
  "Textanfang": "...",
  "Verlag": "...",
  "Material": "...",
  "Textdichter": "...",
  "Bearbeiter": "...",
  "Bemerkungen": "..."
}
"""

# === HILFSFUNKTIONEN ===

def encode_image_to_base64(image_path):
    """Kodiert ein Bild als Base64-String."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_vlm_api(image_path, api_key, max_retries=MAX_RETRIES):
    """
    Ruft das VLM API auf und gibt die strukturierten Daten zurück.
    Mit automatischer Wiederholung bei Fehlern.
    """
    for attempt in range(max_retries):
        try:
            base64_image = encode_image_to_base64(image_path)
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": EXTRACTION_PROMPT
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 1000
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                # Parse JSON aus der Antwort (bereinige Markdown)
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                data = json.loads(content)
                return data, None
            else:
                raise Exception("Keine Antwort vom API erhalten")
                
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            if attempt < max_retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)
    
    return None, "Max retries erreicht"

def log_error(batch_name, filename, message, details=None):
    """Schreibt Fehler in die Logdatei (thread-safe)."""
    with log_lock:
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"[{datetime.now().isoformat()}] Batch: {batch_name} | Datei: {filename}\n")
            log.write(f"⚠️  {message}\n")
            if details:
                log.write(f"Details: {details}\n")
            log.write("-" * 80 + "\n")

def validate_signature(signature):
    """Validiert ob eine Signatur ein gültiges Format hat."""
    if not signature:
        return False
    
    import re
    patterns = [
        r'^Spez\.\d{1,2}\.\d{3,4}(\s+[a-z])?$',
        r'^(RTSO|RTOB|TOB)\s+\d{3,4}$'
    ]
    
    return any(re.match(pattern, signature) for pattern in patterns)

def format_time(seconds):
    """Formatiert Sekunden in lesbares Format."""
    return str(timedelta(seconds=int(seconds)))

def save_checkpoint(data):
    """Speichert den aktuellen Fortschritt."""
    with open(CHECKPOINT_FILE, 'wb') as f:
        pickle.dump(data, f)

def load_checkpoint():
    """Lädt den gespeicherten Fortschritt."""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'rb') as f:
                return pickle.load(f)
        except:
            return {}
    return {}

def save_progress(progress):
    """Speichert Fortschritt in JSON."""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def load_progress():
    """Lädt Fortschritt aus JSON."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# === WORKER FUNKTION ===

def process_single_card(image_path, api_key, batch_name):
    """Verarbeitet eine einzelne Karteikarte."""
    start_time = time.time()
    filename = image_path.name
    
    try:
        data, error = call_vlm_api(str(image_path), api_key)
        
        if error:
            log_error(batch_name, filename, error)
            return {
                "filename": filename,
                "batch": batch_name,
                "success": False,
                "error": error,
                "duration": time.time() - start_time
            }
        
        # Füge Metadaten hinzu
        data["Datei"] = filename
        data["Batch"] = batch_name
        
        # Speichere JSON (in batch-spezifischem Unterordner)
        batch_json_dir = Path(JSON_OUT_BASE) / batch_name
        batch_json_dir.mkdir(exist_ok=True)
        json_path = batch_json_dir / f"{image_path.stem}.json"
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            "filename": filename,
            "batch": batch_name,
            "success": True,
            "data": data,
            "duration": time.time() - start_time,
            "has_komponist": bool(data.get("Komponist", "").strip()),
            "has_signatur": bool(data.get("Signatur", "").strip()),
            "valid_signatur": validate_signature(data.get("Signatur", ""))
        }
        
    except Exception as e:
        log_error(batch_name, filename, f"Unerwarteter Fehler: {str(e)}")
        return {
            "filename": filename,
            "batch": batch_name,
            "success": False,
            "error": str(e),
            "duration": time.time() - start_time
        }

# === BATCH-VERARBEITUNG ===

def process_single_batch(batch_dir, api_key, batch_number, total_batches):
    """Verarbeitet einen einzelnen Batch-Ordner."""
    
    batch_name = batch_dir.name
    print(f"\n{'=' * 80}")
    print(f"📦 BATCH {batch_number}/{total_batches}: {batch_name}")
    print(f"{'=' * 80}")
    
    # Lade Checkpoint für diesen Batch
    checkpoint = load_checkpoint()
    processed_files = checkpoint.get(batch_name, set())
    
    # Finde alle Bilder
    all_files = sorted(list(batch_dir.glob("*.jpg")) + list(batch_dir.glob("*.jpeg")))
    image_files = [f for f in all_files if f.name not in processed_files]
    
    total = len(image_files)
    already_processed = len(all_files) - total
    
    if already_processed > 0:
        print(f"📌 {already_processed} Karten bereits verarbeitet (wird fortgesetzt)")
    
    if total == 0:
        if already_processed > 0:
            print(f"✅ Batch vollständig verarbeitet ({already_processed} Karten)")
        else:
            print(f"⚠️  Keine Bilder gefunden")
        return None
    
    print(f"📚 Verarbeite {total} neue Karteikarten...")
    
    # Statistiken
    records = []
    success_count = 0
    error_count = 0
    komponist_count = 0
    signatur_count = 0
    valid_signatur_count = 0
    
    batch_start = time.time()
    last_update = time.time()
    processed_count = 0
    
    # Parallele Verarbeitung
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_file = {
            executor.submit(process_single_card, img_path, api_key, batch_name): img_path 
            for img_path in image_files
        }
        
        for future in as_completed(future_to_file):
            result = future.result()
            processed_count += 1
            
            if result["success"]:
                success_count += 1
                records.append(result["data"])
                processed_files.add(result["filename"])
                
                if result.get("has_komponist"):
                    komponist_count += 1
                if result.get("has_signatur"):
                    signatur_count += 1
                if result.get("valid_signatur"):
                    valid_signatur_count += 1
            else:
                error_count += 1
            
            # Progress Update
            current_time = time.time()
            if current_time - last_update >= 5 or processed_count % 10 == 0:
                elapsed = current_time - batch_start
                avg_time = elapsed / processed_count
                remaining = total - processed_count
                eta_seconds = remaining * avg_time
                eta = format_time(eta_seconds)
                
                cards_per_min = (processed_count / elapsed) * 60 if elapsed > 0 else 0
                
                print(f"  📊 [{processed_count}/{total}] | "
                      f"✓ {success_count} | ✗ {error_count} | "
                      f"{cards_per_min:.1f}/min | "
                      f"ETA: {eta}")
                
                last_update = current_time
                
                # Checkpoint alle 50 Karten
                if processed_count % 50 == 0:
                    checkpoint[batch_name] = processed_files
                    save_checkpoint(checkpoint)
    
    # Batch-Statistiken
    batch_duration = time.time() - batch_start
    
    print(f"\n  ⏱️  Batch-Dauer: {format_time(batch_duration)}")
    print(f"  ⚡ Durchschnitt: {batch_duration / total:.2f}s pro Karte")
    print(f"  ✅ Erfolgreich: {success_count}/{total} ({success_count/total*100:.1f}%)")
    
    if success_count > 0:
        print(f"  📝 Komponisten: {komponist_count} ({komponist_count/success_count*100:.1f}%)")
        print(f"  🔖 Signaturen: {signatur_count} ({signatur_count/success_count*100:.1f}%)")
    
    # Speichere Batch-CSV
    if records:
        df = pd.DataFrame(records)
        cols = ["Datei", "Batch", "Signatur", "Komponist"] + \
               [k for k in FIELD_KEYS if k not in ["Signatur", "Komponist"] and k in df.columns]
        df = df[cols]
        
        csv_filename = f"{batch_name}.csv"
        csv_path = os.path.join(CSV_OUT_BASE, csv_filename)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        
        print(f"  💾 CSV gespeichert: {csv_filename}")
        
        # Update Checkpoint
        checkpoint[batch_name] = processed_files
        save_checkpoint(checkpoint)
        
        return {
            "batch_name": batch_name,
            "total_cards": len(all_files),
            "processed": total,
            "success": success_count,
            "errors": error_count,
            "duration": batch_duration,
            "csv_file": csv_path,
            "komponist_found": komponist_count,
            "signatur_found": signatur_count,
            "valid_signatur": valid_signatur_count
        }
    
    return None

# === HAUPTPROGRAMM ===

def process_all_batches():
    """Verarbeitet alle Batch-Ordner."""
    
    print("🎵 Lippmann-Rau Archiv Multi-Batch OCR")
    print("=" * 80)
    print(f"🤖 Modell: {MODEL_NAME}")
    print(f"⚡ Parallele Verarbeitung mit {MAX_WORKERS} Workern")
    print("=" * 80)
    
    # API-Key abfragen
    print("\n🔑 Bitte gib deinen API-Key ein:")
    api_key = getpass.getpass("API-Key: ")
    
    if not api_key:
        print("❌ Kein API-Key angegeben. Abbruch.")
        return
    
    # Lösche alte Logs
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    # Finde alle Batch-Ordner
    base_path = Path(BASE_INPUT_DIR)
    
    # Methode 1: Suche nach Muster (z.B. "Batch_*")
    batch_dirs = sorted(list(base_path.glob(BATCH_PATTERN)))
    
    # Methode 2: Falls ALLE Unterordner Batches sind
    if not batch_dirs:
        batch_dirs = sorted([d for d in base_path.iterdir() if d.is_dir()])
    
    if not batch_dirs:
        print(f"❌ Keine Batch-Ordner gefunden in: {BASE_INPUT_DIR}")
        print(f"   Gesucht nach Muster: {BATCH_PATTERN}")
        return
    
    total_batches = len(batch_dirs)
    print(f"\n📦 {total_batches} Batch-Ordner gefunden")
    
    # Lade Fortschritt
    progress = load_progress()
    completed_batches = progress.get("completed_batches", [])
    
    # Verarbeite jeden Batch
    overall_start = time.time()
    batch_results = []
    
    for idx, batch_dir in enumerate(batch_dirs, 1):
        batch_name = batch_dir.name
        
        # Überspringe bereits abgeschlossene Batches
        if batch_name in completed_batches:
            print(f"\n✅ Batch {idx}/{total_batches}: {batch_name} (bereits abgeschlossen)")
            continue
        
        try:
            result = process_single_batch(batch_dir, api_key, idx, total_batches)
            
            if result:
                batch_results.append(result)
                completed_batches.append(batch_name)
                
                # Speichere Fortschritt
                progress["completed_batches"] = completed_batches
                progress["last_updated"] = datetime.now().isoformat()
                save_progress(progress)
                
        except KeyboardInterrupt:
            print("\n\n⏸️  Verarbeitung durch Benutzer unterbrochen.")
            print("💾 Fortschritt wurde gespeichert.")
            return
        except Exception as e:
            print(f"\n❌ Fehler bei Batch {batch_name}: {e}")
            log_error(batch_name, "BATCH", f"Kritischer Fehler: {e}")
            continue
    
    # === FINALE ZUSAMMENFÜHRUNG ===
    
    print(f"\n{'=' * 80}")
    print("📊 ZUSAMMENFÜHRUNG ALLER CSV-DATEIEN")
    print(f"{'=' * 80}")
    
    # Sammle alle Batch-CSVs
    csv_files = sorted(glob.glob(os.path.join(CSV_OUT_BASE, "*.csv")))
    
    if not csv_files:
        print("❌ Keine CSV-Dateien gefunden zum Zusammenführen")
        return
    
    print(f"📝 Füge {len(csv_files)} CSV-Dateien zusammen...")
    
    # Lade und kombiniere alle CSVs
    all_dfs = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding="utf-8-sig")
            all_dfs.append(df)
        except Exception as e:
            print(f"⚠️  Fehler beim Laden von {csv_file}: {e}")
    
    if all_dfs:
        # Kombiniere alle DataFrames
        combined_df = pd.concat(all_dfs, ignore_index=True)
        combined_df.to_csv(FINAL_CSV, index=False, encoding="utf-8-sig")
        
        print(f"✅ Gesamt-CSV erstellt: {FINAL_CSV}")
        print(f"   📊 Gesamt-Einträge: {len(combined_df):,}")
    
    # === FINALE STATISTIKEN ===
    
    total_elapsed = time.time() - overall_start
    
    print(f"\n{'=' * 80}")
    print("🎉 VERARBEITUNG ABGESCHLOSSEN")
    print(f"{'=' * 80}")
    print(f"⏱️  Gesamtdauer: {format_time(total_elapsed)}")
    print(f"📦 Verarbeitete Batches: {len(batch_results)}/{total_batches}")
    
    if batch_results:
        total_cards = sum(r["total_cards"] for r in batch_results)
        total_success = sum(r["success"] for r in batch_results)
        total_errors = sum(r["errors"] for r in batch_results)
        
        print(f"📚 Gesamt-Karteikarten: {total_cards:,}")
        print(f"✅ Erfolgreich: {total_success:,} ({total_success/total_cards*100:.1f}%)")
        print(f"❌ Fehler: {total_errors:,}")
        print(f"⚡ Durchschnitt: {total_elapsed / total_cards:.2f}s pro Karte")
        print(f"🚀 Geschwindigkeit: {(total_cards / total_elapsed) * 3600:.0f} Karten/Stunde")
    
    print(f"\n📂 Ausgabeverzeichnis: {OUTPUT_BASE}/")
    print(f"   ├── csv/ ({len(csv_files)} Batch-CSVs)")
    print(f"   ├── json/ (JSON-Dateien nach Batch)")
    print(f"   └── {os.path.basename(FINAL_CSV)} (Gesamt-CSV)")
    
    if total_errors > 0:
        print(f"\n⚠️  Fehlerprotokoll: {LOG_FILE}")
    
    print(f"{'=' * 80}")
    
    # Lösche Checkpoint nach erfolgreichem Abschluss
    if len(completed_batches) == total_batches:
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
        print("✅ Alle Batches erfolgreich verarbeitet!")

if __name__ == "__main__":
    try:
        process_all_batches()
    except KeyboardInterrupt:
        print("\n\n⏸️  Verarbeitung abgebrochen durch Benutzer.")
        print("💾 Fortschritt wurde gespeichert. Beim nächsten Start wird fortgesetzt.")
    except Exception as e:
        print(f"\n❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()
