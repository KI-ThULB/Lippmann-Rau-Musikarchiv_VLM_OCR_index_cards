#!/usr/bin/env python3
"""
🎯 ELEGANTE LÖSUNG: Nur fehlgeschlagene Dateien direkt verarbeiten
- Liest Error-Log
- Verarbeitet nur die Dateien die fehlgeschlagen sind
- Keine Duplikate, keine Kopien nötig
"""

import os
import re
import json
import base64
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import getpass
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle

# === KONFIGURATION (gleich wie Hauptskript) ===
BASE_INPUT_DIR = "/Users/zu54tav/Desktop/Karteikarten/Karteikarten_Musikarchiv_Lippmann-Rau_Eisenach/scripts/jpeg_output"
OUTPUT_BASE = "output_batches"
CSV_OUT_BASE = os.path.join(OUTPUT_BASE, "csv")
JSON_OUT_BASE = os.path.join(OUTPUT_BASE, "json")
LOG_FILE = os.path.join(OUTPUT_BASE, "vlm_errors.log")

API_BASE_URL = "https://openrouter.ai/api/v1"
API_ENDPOINT = f"{API_BASE_URL}/chat/completions"
MODEL_NAME = "qwen/qwen3-vl-8b-instruct"

MAX_WORKERS = 5
MAX_RETRIES = 3
RETRY_DELAY = 2

# === EXTRACTION PROMPT ===
EXTRACTION_PROMPT = """Du bist ein Experte für die Digitalisierung historischer Archivkarteikarten. 

Analysiere diese Karteikarte aus dem Lippmann-Rau Musikarchiv Eisenach und extrahiere ALLE vorhandenen Informationen in folgende Felder:

**WICHTIGE REGELN:**
1. Extrahiere EXAKT was auf der Karte steht, ohne zu interpretieren
2. Komponisten-Namen haben oft das Format "Nachname, Vorname" (z.B. "Zimmermann, Rolf")
3. Signaturen haben folgende Formate:
   - Spez.XX.XXX (z.B. Spez.12.433)
   - TOB XXXX, RTSO XXXX, RTOB XXXX
4. Wenn ein Feld leer ist, gib einen leeren String "" zurück
5. Beachte die Labels auf der Karte

**FELDER:**
- Komponist: Name des Komponisten
- Signatur: Archiv-Signatur
- Titel: Titel des Musikstücks
- Textanfang: Anfang des Liedtexts
- Verlag: Verlagsangabe
- Material: Art des Materials
- Textdichter: Name des Textdichters
- Bearbeiter: Name des Bearbeiters
- Bemerkungen: Zusätzliche Bemerkungen

**AUSGABEFORMAT:**
Antworte NUR mit einem validen JSON-Objekt (KEINE Markdown-Codeblöcke):

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

FIELD_KEYS = [
    "Komponist", "Signatur", "Titel", "Textanfang",
    "Verlag", "Material", "Textdichter", "Bearbeiter", "Bemerkungen"
]

# === HILFSFUNKTIONEN ===

def encode_image_to_base64(image_path):
    """Kodiert ein Bild als Base64-String."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_vlm_api(image_path, api_key, max_retries=MAX_RETRIES):
    """Ruft das VLM API auf."""
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
            
            response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=120)
            
            if response.status_code != 200:
                error_body = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get("error", {}).get("message", error_body)
                except:
                    error_msg = error_body
                raise Exception(f"API-Fehler ({response.status_code}): {error_msg}")
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
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
                raise Exception("Keine 'choices' in API-Antwort")
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"     ⚠️  Versuch {attempt + 1}/{max_retries} fehlgeschlagen, Wiederholung...")
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            return None, str(e)
    
    return None, "Max retries erreicht"

def extract_failed_files_from_log(log_file):
    """Extrahiert alle fehlgeschlagenen Dateien aus dem Error-Log."""
    failed_files = {}  # {batch_name: {filename: full_path}}
    
    if not os.path.exists(log_file):
        print(f"❌ Log-Datei nicht gefunden: {log_file}")
        return failed_files
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern: [timestamp] Batch: batch_XXX | Datei: filename.jpg
    pattern = r'\[.*?\]\s+Batch:\s+(\w+)\s+\|\s+Datei:\s+([^\n]+\.jpg)'
    matches = re.findall(pattern, content)
    
    base_path = Path(BASE_INPUT_DIR)
    
    for batch_name, filename in matches:
        file_path = base_path / batch_name / filename
        
        if file_path.exists():
            if batch_name not in failed_files:
                failed_files[batch_name] = {}
            failed_files[batch_name][filename] = file_path
        else:
            print(f"⚠️  Datei nicht gefunden: {file_path}")
    
    return failed_files

def format_time(seconds):
    """Formatiert Sekunden in lesbares Format."""
    from datetime import timedelta
    return str(timedelta(seconds=int(seconds)))

def process_single_card(image_path, api_key, batch_name, filename):
    """Verarbeitet eine einzelne Karteikarte."""
    start_time = time.time()
    
    try:
        data, error = call_vlm_api(str(image_path), api_key)
        
        if error:
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
        
        # Speichere JSON
        batch_json_dir = Path(JSON_OUT_BASE) / batch_name
        batch_json_dir.mkdir(exist_ok=True)
        json_path = batch_json_dir / f"{Path(filename).stem}.json"
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {
            "filename": filename,
            "batch": batch_name,
            "success": True,
            "data": data,
            "duration": time.time() - start_time,
            "has_komponist": bool(data.get("Komponist", "").strip()),
            "has_signatur": bool(data.get("Signatur", "").strip())
        }
        
    except Exception as e:
        return {
            "filename": filename,
            "batch": batch_name,
            "success": False,
            "error": str(e),
            "duration": time.time() - start_time
        }

def main():
    print("🔄 Retry-Verarbeitung für fehlgeschlagene Dateien")
    print("=" * 80)
    
    # Extrahiere fehlgeschlagene Dateien
    print(f"\n📂 Lese Error-Log: {LOG_FILE}")
    failed_files = extract_failed_files_from_log(LOG_FILE)
    
    total_failed = sum(len(files) for files in failed_files.values())
    
    if not failed_files or total_failed == 0:
        print("✅ Keine fehlgeschlagenen Dateien gefunden!")
        return
    
    print(f"\n✓ {total_failed} fehlgeschlagene Dateien gefunden in {len(failed_files)} Batches")
    
    # Zeige Zusammenfassung
    print(f"\n📊 ÜBERSICHT:")
    for batch_name in sorted(failed_files.keys()):
        count = len(failed_files[batch_name])
        print(f"   • {batch_name}: {count} Dateien")
    
    # API-Key abfragen
    print(f"\n🔑 Bitte gib deinen API-Key ein:")
    api_key = getpass.getpass("API-Key: ")
    
    if not api_key:
        print("❌ Kein API-Key angegeben. Abbruch.")
        return
    
    # Verarbeite alle Batches
    all_records = []
    overall_start = time.time()
    
    for batch_idx, (batch_name, files_dict) in enumerate(sorted(failed_files.items()), 1):
        total_batches = len(failed_files)
        print(f"\n{'=' * 80}")
        print(f"📦 BATCH {batch_idx}/{total_batches}: {batch_name}")
        print(f"{'=' * 80}")
        print(f"📚 Verarbeite {len(files_dict)} Dateien...")
        
        records = []
        success_count = 0
        error_count = 0
        
        batch_start = time.time()
        last_update = time.time()
        processed_count = 0
        
        # Parallele Verarbeitung
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(
                    process_single_card, 
                    file_path, 
                    api_key, 
                    batch_name, 
                    filename
                ): filename 
                for filename, file_path in files_dict.items()
            }
            
            for future in as_completed(futures):
                result = future.result()
                processed_count += 1
                
                if result["success"]:
                    success_count += 1
                    records.append(result["data"])
                    all_records.append(result["data"])
                else:
                    error_count += 1
                
                # Progress Update
                current_time = time.time()
                if current_time - last_update >= 5 or processed_count % 10 == 0:
                    elapsed = current_time - batch_start
                    avg_time = elapsed / processed_count
                    remaining = len(files_dict) - processed_count
                    eta_seconds = remaining * avg_time
                    eta = format_time(eta_seconds)
                    
                    cards_per_min = (processed_count / elapsed) * 60 if elapsed > 0 else 0
                    
                    print(f"  📊 [{processed_count}/{len(files_dict)}] | "
                          f"✓ {success_count} | ✗ {error_count} | "
                          f"{cards_per_min:.1f}/min | ETA: {eta}")
                    
                    last_update = current_time
        
        # Batch-Statistiken
        batch_duration = time.time() - batch_start
        
        print(f"\n  ⏱️  Batch-Dauer: {format_time(batch_duration)}")
        print(f"  ⚡ Durchschnitt: {batch_duration / len(files_dict):.2f}s pro Karte")
        print(f"  ✅ Erfolgreich: {success_count}/{len(files_dict)} ({success_count/len(files_dict)*100:.1f}%)")
        
        # Speichere Batch-CSV
        if records:
            df = pd.DataFrame(records)
            cols = ["Datei", "Batch", "Signatur", "Komponist"] + \
                   [k for k in FIELD_KEYS if k not in ["Signatur", "Komponist"] and k in df.columns]
            df = df[cols]
            
            csv_filename = f"{batch_name}_RETRY.csv"
            csv_path = os.path.join(CSV_OUT_BASE, csv_filename)
            df.to_csv(csv_path, index=False, encoding="utf-8-sig")
            
            print(f"  💾 CSV gespeichert: {csv_filename}")
    
    # === ABSCHLUSS ===
    
    total_elapsed = time.time() - overall_start
    
    print(f"\n{'=' * 80}")
    print("🎉 RETRY-VERARBEITUNG ABGESCHLOSSEN")
    print(f"{'=' * 80}")
    
    if all_records:
        print(f"✅ Gesamt verarbeitet: {len(all_records)} Dateien")
        print(f"⏱️  Gesamtdauer: {format_time(total_elapsed)}")
        print(f"⚡ Durchschnitt: {total_elapsed / len(all_records):.2f}s pro Datei")
        print(f"\n💾 CSV-Dateien befinden sich in: {CSV_OUT_BASE}/")
        print(f"   Benenne RETRY-CSVs zu den ursprünglichen Batch-Namen um")
        print(f"   oder führe die Zusammenführung erneut durch")
    else:
        print("❌ Keine Dateien konnten verarbeitet werden")
    
    print(f"{'=' * 80}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Verarbeitung abgebrochen durch Benutzer.")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
