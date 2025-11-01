#!/usr/bin/env python3
"""
🔄 CSV-Zusammenführung: Original + RETRY-Dateien
Kombiniert die existierende metadata_vlm_complete.csv mit allen neuen RETRY-CSVs
und entfernt Duplikate intelligent.
"""

import pandas as pd
import glob
import os
from pathlib import Path
from datetime import datetime

# === KONFIGURATION ===
CSV_DIR = "/Users/zu54tav/Downloads/Lippmann-Rau-Cards_project_latest/output_batches/csv/retry"
FINAL_CSV = os.path.join(CSV_DIR, "metadata_vlm_complete.csv")
OUTPUT_CSV = os.path.join(CSV_DIR, "metadata_vlm_complete_UPDATED.csv")
BACKUP_CSV = os.path.join(CSV_DIR, "metadata_vlm_complete_BACKUP.csv")

# === HILFSFUNKTIONEN ===

def format_number(num):
    """Formatiert Zahlen mit Tausender-Trennzeichen."""
    return f"{num:,.0f}"

def main():
    print("🔄 CSV-Zusammenführung: Original + RETRY")
    print("=" * 80)
    
    # 1. Überprüfe ob Dateiverzeichnis existiert
    if not os.path.exists(CSV_DIR):
        print(f"❌ Verzeichnis nicht gefunden: {CSV_DIR}")
        return
    
    print(f"\n📁 Arbeitsverzeichnis: {CSV_DIR}")
    
    # 2. Überprüfe ob Original-CSV existiert
    if not os.path.exists(FINAL_CSV):
        print(f"❌ Original-CSV nicht gefunden: {FINAL_CSV}")
        return
    
    print(f"✓ Original-CSV gefunden: {os.path.basename(FINAL_CSV)}")
    
    # 3. Finde alle RETRY-CSVs
    retry_csvs = sorted(glob.glob(os.path.join(CSV_DIR, "*_RETRY.csv")))
    
    if not retry_csvs:
        print("⚠️  Keine RETRY-CSV-Dateien gefunden!")
        print("   (Erwartet: batch_XXX_RETRY.csv Dateien)")
        return
    
    print(f"✓ {len(retry_csvs)} RETRY-CSV-Dateien gefunden:")
    for csv in retry_csvs[:5]:
        print(f"   • {os.path.basename(csv)}")
    if len(retry_csvs) > 5:
        print(f"   • ... und {len(retry_csvs) - 5} weitere")
    
    # 4. Lade Original-CSV
    print(f"\n📖 Lade Original-CSV...")
    try:
        df_original = pd.read_csv(FINAL_CSV, encoding="utf-8-sig")
        print(f"   ✓ {format_number(len(df_original))} Einträge geladen")
    except Exception as e:
        print(f"❌ Fehler beim Laden: {e}")
        return
    
    # 5. Lade alle RETRY-CSVs
    print(f"\n📖 Lade RETRY-CSVs...")
    all_dfs = [df_original]
    retry_total = 0
    
    for csv_file in retry_csvs:
        try:
            df = pd.read_csv(csv_file, encoding="utf-8-sig")
            all_dfs.append(df)
            retry_total += len(df)
            print(f"   ✓ {os.path.basename(csv_file)}: {len(df)} Einträge")
        except Exception as e:
            print(f"   ⚠️  Fehler bei {os.path.basename(csv_file)}: {e}")
    
    print(f"   📊 RETRY-Einträge gesamt: {format_number(retry_total)}")
    
    # 6. Kombiniere alle DataFrames
    print(f"\n🔗 Kombiniere DataFrames...")
    combined_df = pd.concat(all_dfs, ignore_index=True)
    print(f"   ✓ Kombinierte Einträge (mit Duplikaten): {format_number(len(combined_df))}")
    
    # 7. Entferne Duplikate (neueste Daten behalten)
    print(f"\n🔍 Suche Duplikate...")
    
    # Überprüfe ob "Datei" Spalte existiert
    if "Datei" not in combined_df.columns:
        print(f"⚠️  'Datei' Spalte nicht gefunden. Spalten: {list(combined_df.columns)}")
        # Fallback: Verwende erste Spalte
        file_col = combined_df.columns[0]
        print(f"   Verwende stattdessen: {file_col}")
    else:
        file_col = "Datei"
    
    duplicates = combined_df[file_col].duplicated(keep=False).sum()
    print(f"   Gefundene Duplikate: {duplicates // 2}")
    
    # Entferne Duplikate (keep="last" = neueste/aktualisierte Daten behalten)
    df_deduplicated = combined_df.drop_duplicates(subset=[file_col], keep="last")
    
    removed = len(combined_df) - len(df_deduplicated)
    print(f"   ✓ Entfernte Duplikate: {removed}")
    print(f"   ✓ Finale Einträge: {format_number(len(df_deduplicated))}")
    
    # 8. Speichere Backup der Original-CSV
    print(f"\n💾 Erstelle Backup...")
    try:
        # Nur wenn noch kein Backup existiert
        if not os.path.exists(BACKUP_CSV):
            import shutil
            shutil.copy2(FINAL_CSV, BACKUP_CSV)
            print(f"   ✓ Backup erstellt: {os.path.basename(BACKUP_CSV)}")
        else:
            print(f"   ⓘ Backup existiert bereits")
    except Exception as e:
        print(f"   ⚠️  Fehler beim Backup: {e}")
    
    # 9. Speichere neue CSV
    print(f"\n💾 Speichere aktualisierte CSV...")
    try:
        df_deduplicated.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
        print(f"   ✓ Gespeichert: {os.path.basename(OUTPUT_CSV)}")
    except Exception as e:
        print(f"   ❌ Fehler beim Speichern: {e}")
        return
    
    # 10. Statistiken
    print(f"\n{'=' * 80}")
    print("📊 ZUSAMMENFASSUNG")
    print(f"{'=' * 80}")
    
    original_count = len(df_original)
    new_count = len(df_deduplicated)
    added = new_count - original_count
    
    print(f"\nEinträge:")
    print(f"  📖 Original:        {format_number(original_count):>8}")
    print(f"  ➕ Neu (RETRY):      {format_number(retry_total):>8}")
    print(f"  🔄 Zusammengeführt: {format_number(len(combined_df)):>8}")
    print(f"  ⚠️  Duplikate:       {format_number(removed):>8}")
    print(f"  ✅ Final:            {format_number(new_count):>8}")
    print(f"  {'─' * 50}")
    print(f"  📈 Nettogewinn:     {format_number(added):>8} ({added/original_count*100:.1f}%)")
    
    # 11. Spalten-Info
    print(f"\nSpalten ({len(df_deduplicated.columns)}):")
    for col in df_deduplicated.columns:
        non_null = df_deduplicated[col].notna().sum()
        null_pct = (1 - non_null/len(df_deduplicated))*100
        print(f"  • {col:20} | {non_null:>6} Einträge | {null_pct:>5.1f}% leer")
    
    # 12. Qualitäts-Check
    print(f"\n✅ Qualitäts-Checks:")
    
    # Check: Keine Duplikate mehr
    duplicates_check = df_deduplicated[file_col].duplicated().sum()
    if duplicates_check == 0:
        print(f"  ✓ Keine Duplikate")
    else:
        print(f"  ⚠️  {duplicates_check} Duplikate gefunden!")
    
    # Check: Alle notwendigen Spalten
    expected_cols = ["Datei", "Batch", "Signatur", "Komponist"]
    missing = [col for col in expected_cols if col not in df_deduplicated.columns]
    if not missing:
        print(f"  ✓ Alle erwarteten Spalten vorhanden")
    else:
        print(f"  ⚠️  Fehlende Spalten: {missing}")
    
    # Check: Datentypen
    if df_deduplicated["Datei"].dtype == "object":
        print(f"  ✓ Datentypen korrekt")
    
    # 13. Nächste Schritte
    print(f"\n{'=' * 80}")
    print("🚀 NÄCHSTE SCHRITTE")
    print(f"{'=' * 80}")
    print(f"\n1. Überprüfe die neue Datei:")
    print(f"   open {OUTPUT_CSV}")
    print(f"\n2. Wenn alles OK ist, ersetze die Original:")
    print(f"   mv {OUTPUT_CSV} {FINAL_CSV}")
    print(f"\n3. Oder: Komm to Git!")
    print(f"   git add output_batches/csv/")
    print(f"   git commit -m 'data: Merge retry results with original CSV'")
    print(f"   git push origin main")
    
    # 14. Vergleich
    print(f"\n{'=' * 80}")
    print("📈 VERGLEICH")
    print(f"{'=' * 80}")
    
    print(f"\n📁 Original-Datei:")
    print(f"   {FINAL_CSV}")
    orig_size = os.path.getsize(FINAL_CSV) / (1024*1024)
    print(f"   Größe: {orig_size:.2f} MB")
    
    print(f"\n📁 Aktualisierte Datei:")
    print(f"   {OUTPUT_CSV}")
    new_size = os.path.getsize(OUTPUT_CSV) / (1024*1024)
    print(f"   Größe: {new_size:.2f} MB")
    
    size_diff = new_size - orig_size
    print(f"   Differenz: {size_diff:+.2f} MB")
    
    # 15. Timestamp
    print(f"\n⏰ Erstellt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Abgebrochen durch Benutzer.")
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
