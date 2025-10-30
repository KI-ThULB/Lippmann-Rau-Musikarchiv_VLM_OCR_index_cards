#!/usr/bin/env python3
"""
Analyse-Tool für Lippmann-Rau OCR-Ergebnisse
Generiert Statistiken und Qualitätsberichte
"""

import pandas as pd
import json
from pathlib import Path
from collections import Counter
import re

# Konfiguration
CSV_FILE = "output_batches/metadata_vlm_complete.csv"
OUTPUT_DIR = "output_batches/analysis"

def analyze_ocr_results(csv_path):
    """Analysiert die OCR-Ergebnisse und erstellt einen Bericht."""
    
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    
    print("📊 ANALYSE DER OCR-ERGEBNISSE")
    print("=" * 80)
    
    # Lade Daten
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    total_cards = len(df)
    
    print(f"\n📚 Gesamt-Karteikarten: {total_cards:,}\n")
    
    # === BATCH-VERTEILUNG ===
    print("📦 BATCH-VERTEILUNG")
    print("-" * 80)
    batch_counts = df['Batch'].value_counts().sort_index()
    print(f"Anzahl Batches: {len(batch_counts)}")
    print(f"Durchschnitt pro Batch: {batch_counts.mean():.1f}")
    print(f"Min/Max: {batch_counts.min()} / {batch_counts.max()}\n")
    
    # === VOLLSTÄNDIGKEIT ===
    print("✓ VOLLSTÄNDIGKEIT DER FELDER")
    print("-" * 80)
    
    fields = ["Komponist", "Signatur", "Titel", "Textanfang", 
              "Verlag", "Material", "Textdichter", "Bearbeiter", "Bemerkungen"]
    
    completeness = {}
    for field in fields:
        if field in df.columns:
            filled = df[field].notna().sum()
            non_empty = (df[field].fillna('').str.strip() != '').sum()
            percentage = (non_empty / total_cards) * 100
            completeness[field] = {
                'count': non_empty,
                'percentage': percentage
            }
            print(f"{field:15s}: {non_empty:6,} ({percentage:5.1f}%)")
    
    # === SIGNATUR-ANALYSE ===
    print(f"\n🔖 SIGNATUR-ANALYSE")
    print("-" * 80)
    
    if 'Signatur' in df.columns:
        signaturen = df['Signatur'].fillna('').str.strip()
        valid_signaturen = signaturen[signaturen != '']
        
        # Analysiere Signatur-Muster
        patterns = {
            'Spez': r'^Spez\.\d+\.\d+',
            'TOB': r'^TOB\s+\d+',
            'RTSO': r'^RTSO\s+\d+',
            'RTOB': r'^RTOB\s+\d+',
            'Andere': r'.'
        }
        
        pattern_counts = {}
        for name, pattern in patterns.items():
            if name == 'Andere':
                count = len(valid_signaturen) - sum(pattern_counts.values())
            else:
                count = valid_signaturen.str.match(pattern).sum()
            pattern_counts[name] = count
            print(f"{name:10s}: {count:6,} ({count/len(valid_signaturen)*100:5.1f}%)")
    
    # === KOMPONISTEN-ANALYSE ===
    print(f"\n👤 KOMPONISTEN-ANALYSE")
    print("-" * 80)
    
    if 'Komponist' in df.columns:
        komponisten = df['Komponist'].fillna('').str.strip()
        valid_komponisten = komponisten[komponisten != '']
        
        print(f"Einzigartige Komponisten: {valid_komponisten.nunique():,}")
        print(f"\nTop 10 häufigste Komponisten:")
        top_komponisten = valid_komponisten.value_counts().head(10)
        for i, (name, count) in enumerate(top_komponisten.items(), 1):
            print(f"  {i:2d}. {name:40s} {count:4d} Karten")
    
    # === QUALITÄTSPRÜFUNG ===
    print(f"\n🔍 QUALITÄTSPRÜFUNG")
    print("-" * 80)
    
    # Leere Datensätze (alle Felder leer)
    all_empty = df[fields].fillna('').apply(lambda row: all(str(val).strip() == '' for val in row), axis=1)
    empty_count = all_empty.sum()
    print(f"Komplett leere Datensätze: {empty_count:,} ({empty_count/total_cards*100:.1f}%)")
    
    # Datensätze mit nur 1-2 Feldern
    field_counts = df[fields].fillna('').apply(lambda row: sum(str(val).strip() != '' for val in row), axis=1)
    sparse_count = (field_counts <= 2).sum() - empty_count
    print(f"Spärliche Datensätze (1-2 Felder): {sparse_count:,} ({sparse_count/total_cards*100:.1f}%)")
    
    # Vollständige Datensätze (>=6 Felder)
    complete_count = (field_counts >= 6).sum()
    print(f"Vollständige Datensätze (≥6 Felder): {complete_count:,} ({complete_count/total_cards*100:.1f}%)")
    
    # === TEXTLÄNGEN ===
    print(f"\n📏 TEXTLÄNGEN-STATISTIK")
    print("-" * 80)
    
    for field in ['Titel', 'Textanfang', 'Bemerkungen']:
        if field in df.columns:
            lengths = df[field].fillna('').str.len()
            non_zero = lengths[lengths > 0]
            if len(non_zero) > 0:
                print(f"{field:15s}: Ø {non_zero.mean():5.1f} Zeichen (Min: {non_zero.min()}, Max: {non_zero.max()})")
    
    # === SPEICHERE DETAILLIERTE BERICHTE ===
    
    # 1. Vollständigkeits-Report
    completeness_df = pd.DataFrame.from_dict(completeness, orient='index')
    completeness_df.to_csv(f"{OUTPUT_DIR}/field_completeness.csv", encoding="utf-8-sig")
    
    # 2. Batch-Statistiken
    batch_stats = df.groupby('Batch').agg({
        'Datei': 'count',
        'Komponist': lambda x: (x.fillna('').str.strip() != '').sum(),
        'Signatur': lambda x: (x.fillna('').str.strip() != '').sum(),
        'Titel': lambda x: (x.fillna('').str.strip() != '').sum()
    }).rename(columns={
        'Datei': 'Total',
        'Komponist': 'Mit_Komponist',
        'Signatur': 'Mit_Signatur',
        'Titel': 'Mit_Titel'
    })
    batch_stats.to_csv(f"{OUTPUT_DIR}/batch_statistics.csv", encoding="utf-8-sig")
    
    # 3. Problematische Datensätze
    problematic = df[all_empty | (field_counts <= 2)]
    if len(problematic) > 0:
        problematic[['Datei', 'Batch']].to_csv(
            f"{OUTPUT_DIR}/problematic_cards.csv", 
            index=False, 
            encoding="utf-8-sig"
        )
        print(f"\n⚠️  {len(problematic)} problematische Karteikarten in: {OUTPUT_DIR}/problematic_cards.csv")
    
    # 4. Komponisten-Liste
    if 'Komponist' in df.columns:
        komponisten_freq = valid_komponisten.value_counts()
        komponisten_freq.to_csv(
            f"{OUTPUT_DIR}/komponisten_frequency.csv",
            header=['Anzahl'],
            encoding="utf-8-sig"
        )
    
    # 5. Fehlende Signaturen
    missing_sig = df[df['Signatur'].fillna('').str.strip() == ''][['Datei', 'Batch', 'Komponist', 'Titel']]
    if len(missing_sig) > 0:
        missing_sig.to_csv(
            f"{OUTPUT_DIR}/missing_signatures.csv",
            index=False,
            encoding="utf-8-sig"
        )
    
    print(f"\n{'=' * 80}")
    print(f"📁 Berichte gespeichert in: {OUTPUT_DIR}/")
    print(f"   ├── field_completeness.csv")
    print(f"   ├── batch_statistics.csv")
    print(f"   ├── komponisten_frequency.csv")
    if len(problematic) > 0:
        print(f"   ├── problematic_cards.csv")
    if len(missing_sig) > 0:
        print(f"   └── missing_signatures.csv")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    import sys
    
    csv_file = sys.argv[1] if len(sys.argv) > 1 else CSV_FILE
    
    try:
        analyze_ocr_results(csv_file)
    except FileNotFoundError:
        print(f"❌ CSV-Datei nicht gefunden: {csv_file}")
        print(f"   Bitte erst die OCR-Verarbeitung ausführen.")
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
