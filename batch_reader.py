import csv
import os
import openpyxl


def read_credentials(filepath: str) -> list:
    ext = os.path.splitext(filepath)[1].lower()
    return _read_csv(filepath) if ext == ".csv" else _read_xlsx(filepath)


def _read_xlsx(filepath: str) -> list:
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active
    creds = []
    for row in ws.iter_rows(values_only=True):
        if not row or row[0] is None:
            continue
        u = str(row[0]).strip()
        p = str(row[1]).strip() if len(row) > 1 and row[1] is not None else ""
        if u.lower() in ("username", "user", "id", "userid"):
            continue
        if u and p:
            creds.append((u, p))
    wb.close()
    return creds


def _read_csv(filepath: str) -> list:
    creds = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if not row or not row[0].strip():
                continue
            u = row[0].strip()
            p = row[1].strip() if len(row) > 1 else ""
            if u.lower() in ("username", "user", "id", "userid"):
                continue
            if u and p:
                creds.append((u, p))
    return creds
