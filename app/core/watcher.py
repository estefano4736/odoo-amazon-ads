import os
import glob
import json
import shutil
import asyncio
import pandas as pd
from datetime import datetime
from app.core.db import db
from process_ads_report import process_ads_report_file

DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

def get_kdp_report_path(test_mode=False):
    if test_mode or os.environ.get("ENV") == "testing" or os.environ.get("TESTING") == "true":
        return "./data/kdp_sales_report_test.json"
    return "./data/kdp_sales_report.json"

def get_processed_log_path(test_mode=False):
    if test_mode or os.environ.get("ENV") == "testing" or os.environ.get("TESTING") == "true":
        return "./data/processed_downloads_test.json"
    return "./data/processed_downloads.json"

def get_uploads_dir(test_mode=False):
    if test_mode or os.environ.get("ENV") == "testing" or os.environ.get("TESTING") == "true":
        return "./data/uploads_test"
    return "./data/uploads"

# Ensure default directories exist
os.makedirs(get_uploads_dir(False), exist_ok=True)
os.makedirs(os.path.dirname(get_processed_log_path(False)), exist_ok=True)

def load_processed(test_mode=False):
    path = get_processed_log_path(test_mode)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()

def save_processed(processed, test_mode=False):
    path = get_processed_log_path(test_mode)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(list(processed), f, indent=4)

def parse_kdp_royalty_file(file_path: str) -> dict:
    """Fuzzy parses KDP royalty reports (Excel/CSV) and aggregates total royalties and units sold per ASIN."""
    try:
        if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
            # KDP Monthly reports might contain multiple sheets, we read the main one
            xls = pd.ExcelFile(file_path)
            sheet_name = None
            for s in xls.sheet_names:
                s_lower = s.lower()
                if "royalty" in s_lower or "regal" in s_lower or "sales" in s_lower or "ventas" in s_lower:
                    sheet_name = s
                    break
            if not sheet_name:
                sheet_name = xls.sheet_names[0]
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="latin1")

        # Normalize headers
        cols = [str(c).strip().lower() for c in df.columns]
        
        asin_col = None
        royalty_col = None
        units_col = None
        title_col = None
        date_col = None

        for c in df.columns:
            c_clean = str(c).strip().lower()
            
            # Check date independently first to prevent "royalty date" from being matched as royalty_col
            if "date" in c_clean or "fecha" in c_clean or "month" in c_clean or "mes" in c_clean:
                if not date_col and "asin" not in c_clean and "title" not in c_clean:
                    date_col = c
                    continue
            
            if "asin" in c_clean:
                asin_col = c
            elif "royalty" in c_clean or "regalía" in c_clean or "regalia" in c_clean:
                # Prioritize 'net' or 'total' royalty if multiple
                if not royalty_col or "net" in c_clean or "total" in c_clean:
                    royalty_col = c
            elif "units" in c_clean or "unidades" in c_clean or "quantity" in c_clean or "cantidad" in c_clean:
                units_col = c
            elif "title" in c_clean or "título" in c_clean or "titulo" in c_clean or "nombre" in c_clean:
                title_col = c

        if not asin_col:
            print(f"[Watcher-KDP] Could not find ASIN column in KDP report: {file_path}")
            return {}

        books_data = {}
        for _, row in df.iterrows():
            asin = str(row[asin_col]).strip()
            if not asin or pd.isna(row[asin_col]):
                continue

            # Parse royalty value
            roy = 0.0
            if royalty_col and pd.notna(row[royalty_col]):
                try:
                    val_str = str(row[royalty_col]).replace("$", "").replace(",", "").strip()
                    roy = float(val_str)
                except ValueError:
                    pass

            # Parse units
            units = 0
            if units_col and pd.notna(row[units_col]):
                try:
                    units = int(float(row[units_col]))
                except ValueError:
                    pass

            title = str(row[title_col]).strip() if title_col and pd.notna(row[title_col]) else ""
            
            # Parse date if available
            row_date = None
            if date_col and pd.notna(row[date_col]):
                try:
                    dt = pd.to_datetime(row[date_col])
                    row_date = dt.strftime("%Y-%m-%d")
                except Exception:
                    pass

            if asin not in books_data:
                books_data[asin] = {
                    "asin": asin,
                    "title": title,
                    "units": 0,
                    "royalties": 0.0,
                    "daily": {}
                }
            books_data[asin]["units"] += units
            books_data[asin]["royalties"] += roy
            
            if row_date:
                if row_date not in books_data[asin]["daily"]:
                    books_data[asin]["daily"][row_date] = {
                        "units": 0,
                        "royalties": 0.0
                    }
                books_data[asin]["daily"][row_date]["units"] += units
                books_data[asin]["daily"][row_date]["royalties"] += roy

        # Round royalties
        for asin in books_data:
            books_data[asin]["royalties"] = round(books_data[asin]["royalties"], 2)
            for d_str in books_data[asin]["daily"]:
                books_data[asin]["daily"][d_str]["royalties"] = round(books_data[asin]["daily"][d_str]["royalties"], 2)

        return books_data
    except Exception as e:
        print(f"[Watcher-KDP] Error parsing KDP file {file_path}: {e}")
        return {}

async def process_detected_file(file_path: str, filename: str, test_mode=False):
    """Detects type of file and runs appropriate parser."""
    print(f"[Watcher] Processing new file: {filename} (test_mode={test_mode})")
    uploads_dir = get_uploads_dir(test_mode)
    os.makedirs(uploads_dir, exist_ok=True)
    dest_path = os.path.join(uploads_dir, filename)
    shutil.copy2(file_path, dest_path)
    
    # 1. Check if Seller Central Business Report (SalesDashboard)
    if "salesdashboard" in filename.lower():
        try:
            from app.api.bulk import run_sales_dashboard_process_from_file
            res = await run_sales_dashboard_process_from_file(dest_path, filename, test_mode=test_mode)
            print(f"[Watcher] [OK] Business report parsed successfully: {res.get('message')}")
        except Exception as err:
            print(f"[Watcher] [ERROR] Business report parser failed: {err}")

    # 2. Check if Sponsored Products Search Term Report / Ads Report
    elif "sponsored_products" in filename.lower() or "search_term" in filename.lower() or "término" in filename.lower():
        try:
            ads_output_path = 'data/ads_report_test.json' if test_mode else 'data/ads_report.json'
            res = process_ads_report_file(dest_path, output_path=ads_output_path)
            print(f"[Watcher] [OK] Ads report parsed successfully. Total spend: ${res.get('total_spend'):,.2f}")
        except Exception as err:
            print(f"[Watcher] [ERROR] Ads report parser failed: {err}")

    # 3. Check if KDP Royalty Report (Prior_Month_Royalties or starts with KDP)
    elif "prior_month" in filename.lower() or "kdp_" in filename.lower() or "royalt" in filename.lower() or "regal" in filename.lower():
        try:
            kdp_data = parse_kdp_royalty_file(dest_path)
            if kdp_data:
                # Save parsed royalties to JSON
                report_path = get_kdp_report_path(test_mode)
                os.makedirs(os.path.dirname(report_path), exist_ok=True)
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(kdp_data, f, indent=4)
                print(f"[Watcher] ✓ KDP royalty report parsed successfully. Found {len(kdp_data)} books saved to {report_path}.")
                
                # Write to Odoo Database
                try:
                    from app.core.db import db
                    books_list = []
                    kdp_books_ref = {
                        "B0GGSD7SM5": {"price": 149.00, "title": "La Dieta del ADN: Aprende a Hackear tus Genes", "format": "eBook"},
                        "B0GHD59D1Z": {"price": 99.00, "title": "PRUEBA: La Dieta del ADN", "format": "eBook"},
                        "B0GLFSHL3R": {"price": 149.00, "title": "The DNA Diet: How to Hack Your Genes", "format": "eBook"}
                    }
                    for asin, book_info in kdp_data.items():
                        ref = kdp_books_ref.get(asin, {})
                        price = ref.get("price", 149.00)
                        title = ref.get("title", book_info.get("title") or f"Libro {asin}")
                        fmt = ref.get("format", "eBook")
                        units = book_info.get("units", 0)
                        royalties = book_info.get("royalties", 0.0)
                        books_list.append({
                            "asin": asin,
                            "title": title,
                            "format": fmt,
                            "royalty_pct": 0.70,
                            "price": price,
                            "units": units,
                            "sales": round(units * price, 2),
                            "royalties": royalties,
                            "net_profit": royalties
                        })
                    db.write_books(books_list)
                    print("[Watcher - Odoo DB] Synchronized KDP books successfully.")
                    
                    # Send Odoo Discuss Notification
                    summary_html = f"""
                    <p>Se ha procesado e ingestado un nuevo reporte de regalías <b>Kindle KDP Royalty Report</b> con éxito:</p>
                    <ul>
                        <li><b>Archivo:</b> <code>{filename}</code></li>
                        <li><b>Libros Sincronizados:</b> {len(books_list)}</li>
                        <li><b>Total Unidades:</b> {sum(b['units'] for b in books_list)}</li>
                        <li><b>Regalías Totales:</b> ${sum(b['royalties'] for b in books_list):,.2f} MXN</li>
                    </ul>
                    <p>Las regalías de libros ya están actualizadas en Odoo.</p>
                    """
                    db.post_discuss_message(
                        channel_name="Amazon Ads Optimization",
                        subject="Reporte de Regalías KDP Ingestado",
                        message_html=summary_html
                    )
                except Exception as db_err:
                    print(f"[Watcher - Odoo DB] Error writing books or sending notification: {db_err}")
            else:
                print(f"[Watcher] [ERROR] KDP royalty report parsing returned no valid ASIN data.")
        except Exception as err:
            print(f"[Watcher] [ERROR] KDP royalty report parser failed: {err}")

async def watch_downloads_loop():
    """Background loop watching for new files in Downloads folder."""
    print(f"[Watcher] Starting background Downloads watcher on: {DOWNLOADS_DIR}")
    
    while True:
        try:
            # Check files in Downloads directory matching common report names
            patterns = [
                os.path.join(DOWNLOADS_DIR, "SalesDashboard*.csv"),
                os.path.join(DOWNLOADS_DIR, "Sponsored_Products*.xlsx"),
                os.path.join(DOWNLOADS_DIR, "Sponsored_Products*.csv"),
                os.path.join(DOWNLOADS_DIR, "Prior_Month_Royalties*.xlsx"),
                os.path.join(DOWNLOADS_DIR, "Prior_Month_Royalties*.csv"),
                os.path.join(DOWNLOADS_DIR, "KDP_*.xlsx"),
                os.path.join(DOWNLOADS_DIR, "KDP_*.csv")
            ]
            
            files = []
            for pattern in patterns:
                files.extend(glob.glob(pattern))
                
            new_files_found = False
            for f_path in files:
                filename = os.path.basename(f_path)
                file_test_mode = "test" in filename.lower()
                
                processed = load_processed(test_mode=file_test_mode)
                if filename not in processed:
                    await process_detected_file(f_path, filename, test_mode=file_test_mode)
                    processed.add(filename)
                    save_processed(processed, test_mode=file_test_mode)
                    new_files_found = True
                    
        except Exception as e:
            print(f"[Watcher] Loop error: {e}")
            
        await asyncio.sleep(5.0)

def start_watcher(loop=None):
    """Utility to run watcher loop in background."""
    if loop is None:
        loop = asyncio.get_event_loop()
    loop.create_task(watch_downloads_loop())
