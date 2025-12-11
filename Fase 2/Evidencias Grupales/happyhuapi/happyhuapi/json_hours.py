import json
from pathlib import Path
from datetime import datetime
import tempfile
import os


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "hours_db.json"


if not DB_FILE.exists():
    DB_FILE.write_text(json.dumps({}, ensure_ascii=False, indent=2))

def _atomic_write(path: Path, data: str):
    
    dirpath = path.parent
    with tempfile.NamedTemporaryFile("w", dir=dirpath, delete=False, encoding="utf-8") as tf:
        tf.write(data)
        tempname = tf.name
    os.replace(tempname, str(path))

def load_db():
    
    try:
        with DB_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_db(obj: dict):
    
    txt = json.dumps(obj, ensure_ascii=False, indent=2)
    _atomic_write(DB_FILE, txt)

def add_reservation(date_str: str, start: str, end: str, booking_id: int | None = None) -> None:
    
    db = load_db()
    if date_str not in db:
        db[date_str] = []

    # evitar duplicados exactos
    entry = {"start": start, "end": end}
    if booking_id is not None:
        entry["booking_id"] = int(booking_id)

    # comprueba solapamiento simple
    for e in db[date_str]:
        # convertir a minutos para comparar
        def to_mins(hm):
            hh, mm = map(int, hm.split(":"))
            return hh * 60 + mm
        s1, e1 = to_mins(start), to_mins(end)
        s2, e2 = to_mins(e["start"]), to_mins(e["end"])
        if (s1 < e2) and (e1 > s2):
            raise ValueError("El horario se solapa con otra reserva en JSON.")

    db[date_str].append(entry)
    save_db(db)

def remove_reservation_by_booking_id(booking_id: int) -> bool:
    
    db = load_db()
    changed = False
    for date, lst in list(db.items()):
        newlst = [e for e in lst if e.get("booking_id") != booking_id]
        if len(newlst) != len(lst):
            db[date] = newlst
            changed = True
    if changed:
        save_db(db)
    return changed

def list_reservations(date_str: str | None = None):
    
    db = load_db()
    if date_str:
        return db.get(date_str, [])
    return db
