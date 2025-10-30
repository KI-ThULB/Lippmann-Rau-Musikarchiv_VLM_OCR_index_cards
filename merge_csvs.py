#!/usr/bin/env python3
"""
CSV-Zusammenführungs-Tool
Kombiniert alle Batch-CSVs zu einer Gesamt-CSV
(Falls die automatische Zusammenführung nicht funktioniert hat)
"""

import pandas as pd
import glob
from pathlib import Path

# Konfiguration
CSV_DIR = "output_batches/csv"
OUTPUT_FILE = "output_batches/metadata_vlm_complete_MANUAL.csv"

def merge_csv_files():
    """Führt alle CSV-Dateien im Verzeichnis zusammen."""
    
    print("🔗 CSV-ZUSAMMENFÜHRUNG")
    print("=" * 80)
    
    # Finde alle CSV-Dateien
    csv_pattern = str(Path(CSV_DIR) / "*.csv")
    csv_files = sorted(glob.glob(csv_pattern))
    
    if not csv_files:
        print(f"❌ Keine CSV-Dateien gefunden in: {CSV_DIR}")
        return
    
    print(f"📂 Gefunden: {len(csv_files)} CSV-Dateien\n")
    
    # Lade und kombiniere alle CSVs
    all_dfs = []
    errors = []
    
    for csv_file in csv_files:
        filename = Path(csv_file).name
        try:
            df = pd.read_csv(csv_file, encoding="utf-8-sig")
            all_dfs.append(df)
            print(f"✓ {filename:30s} {len(df):6,} Zeilen")
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"✗ {filename:30s} FEHLER: {e}")
    
    if not all_dfs:
        print("\n❌ Keine CSV-Dateien erfolgreich geladen")
        return
    
    print(f"\n{'=' * 80}")
    
    # Kombiniere alle DataFrames
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Sortiere nach Batch und Dateiname
    if 'Batch' in combined_df.columns:
        combined_df = combined_df.sort_values(['Batch', 'Datei'])
    
    # Speichere
    combined_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    
    print(f"✅ Gesamt-CSV erstellt: {OUTPUT_FILE}")
    print(f"📊 Gesamt-Einträge: {len(combined_df):,}")
    
    # Statistiken
    if 'Batch' in combined_df.columns:
        print(f"📦 Batches: {combined_df['Batch'].nunique()}")
    
    # Zeige Vollständigkeit
    print(f"\n📋 VOLLSTÄNDIGKEIT:")
    for col in combined_df.columns:
        if col not in ['Datei', 'Batch']:
            filled = (combined_df[col].fillna('').str.strip() != '').sum()
            percentage = (filled / len(combined_df)) * 100
            print(f"  {col:15s}: {filled:6,} ({percentage:5.1f}%)")
    
    if errors:
        print(f"\n⚠️  FEHLER bei {len(errors)} Datei(en):")
        for filename, error in errors:
            print(f"  - {filename}: {error}")
    
    print(f"\n{'=' * 80}")

if __name__ == "__main__":
    import sys
    
    # Optional: Pfad als Argument
    if len(sys.argv) > 1:
        CSV_DIR = sys.argv[1]
    
    try:
        merge_csv_files()
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()
