import sqlite3, hashlib, hmac, secrets
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
from classification import classify

DB = Path(__file__).parent / "data" / "textileloop.db"
UPLOAD_DIR = Path(__file__).parent / "data" / "uploads"
STATUSES = ["Pending", "Approved", "Scheduled", "Collected", "Processing", "Reused", "Recycled", "Disposed", "Rejected"]
SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, salt TEXT NOT NULL, pw_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS waste_records(id INTEGER PRIMARY KEY, reg_id TEXT UNIQUE NOT NULL, generator TEXT NOT NULL, institution TEXT NOT NULL,
 gen_category TEXT NOT NULL, item_type TEXT NOT NULL, material TEXT NOT NULL, cond TEXT NOT NULL, quantity_kg REAL NOT NULL CHECK(quantity_kg>0),
 location TEXT NOT NULL, contact TEXT NOT NULL, reg_date TEXT NOT NULL, description TEXT, waste_category TEXT NOT NULL, image_path TEXT, is_demo INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS recycler_directory(id INTEGER PRIMARY KEY, name TEXT NOT NULL, ftype TEXT NOT NULL, materials TEXT NOT NULL,
 collection TEXT NOT NULL, location TEXT NOT NULL, contact TEXT NOT NULL, description TEXT, is_demo INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS collection_requests(id INTEGER PRIMARY KEY, coll_id TEXT UNIQUE NOT NULL,
 waste_id INTEGER NOT NULL REFERENCES waste_records(id) ON DELETE CASCADE, recycler_id INTEGER NOT NULL REFERENCES recycler_directory(id),
 quantity_kg REAL NOT NULL CHECK(quantity_kg>0), request_date TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Pending');
CREATE TABLE IF NOT EXISTS processing_records(id INTEGER PRIMARY KEY, collection_id INTEGER UNIQUE NOT NULL REFERENCES collection_requests(id) ON DELETE CASCADE,
 outcome TEXT NOT NULL CHECK(outcome IN ('Reused','Recycled')), quantity_kg REAL NOT NULL, verified INTEGER NOT NULL DEFAULT 1, processed_date TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS status_log(id INTEGER PRIMARY KEY, collection_id INTEGER NOT NULL REFERENCES collection_requests(id) ON DELETE CASCADE,
 old_status TEXT, new_status TEXT NOT NULL, changed_by TEXT, notes TEXT, changed_at TEXT NOT NULL);
"""

def conn():
    DB.parent.mkdir(exist_ok=True)
    c = sqlite3.connect(DB)
    c.execute("PRAGMA foreign_keys=ON")
    return c

def query(sql, params=()):
    with closing(conn()) as c:
        return pd.read_sql_query(sql, c, params=params)

def _id(prefix):
    return f"{prefix}-{date.today():%Y%m%d}-{secrets.token_hex(2).upper()}"

def save_image(file_obj, reg_id):
    """Save an uploaded image or camera capture to disk and return path."""
    if file_obj is None:
        return None
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    # Determine extension
    ext = "jpg"
    name = getattr(file_obj, "name", "")
    if "." in name:
        ext = name.rsplit(".", 1)[-1].lower()
        if ext not in ("jpg", "jpeg", "png", "webp"):
            ext = "jpg"
    filename = f"{reg_id}.{ext}"
    dest = UPLOAD_DIR / filename
    
    # Read bytes from UploadedFile or BytesIO
    if hasattr(file_obj, "getvalue"):
        data = file_obj.getvalue()
    elif hasattr(file_obj, "read"):
        data = file_obj.read()
    else:
        data = bytes(file_obj)
        
    with open(dest, "wb") as f:
        f.write(data)
    return str(dest)

def _insert_waste(c, d):
    cat = classify(d["material"], d["cond"], d["gen_category"])["category"]
    reg = _id("TW")
    img_path = d.get("image_path")
    if not img_path and d.get("file_obj"):
        img_path = save_image(d["file_obj"], reg)
    c.execute("INSERT INTO waste_records(reg_id,generator,institution,gen_category,item_type,material,cond,quantity_kg,location,contact,reg_date,description,waste_category,image_path,is_demo) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
              (reg, d["generator"], d["institution"], d["gen_category"], d["item_type"], d["material"], d["cond"], d["quantity_kg"],
               d["location"], d["contact"], str(d["reg_date"]), d.get("description", ""), cat, img_path, d.get("is_demo", 0)))
    return reg

def add_waste(d):
    if d["quantity_kg"] <= 0:
        raise ValueError("Quantity must be greater than zero.")
    with closing(conn()) as c, c:
        return _insert_waste(c, d)

def remaining(waste_id):
    df = query("SELECT w.quantity_kg - COALESCE((SELECT SUM(quantity_kg) FROM collection_requests WHERE waste_id=w.id AND status!='Rejected'),0) AS r FROM waste_records w WHERE w.id=?", (int(waste_id),))
    return float(df.r[0]) if len(df) else 0.0

def add_request(waste_id, recycler_id, qty, notes=""):
    with closing(conn()) as c, c:
        total = c.execute("SELECT quantity_kg FROM waste_records WHERE id=?", (int(waste_id),)).fetchone()[0]
        used = c.execute("SELECT COALESCE(SUM(quantity_kg),0) FROM collection_requests WHERE waste_id=? AND status!='Rejected'", (int(waste_id),)).fetchone()[0]
        if qty <= 0 or qty > total - used + 1e-9:
            raise ValueError(f"Quantity must be between 0 and {total - used:.1f} kg (what is left unrequested).")
        cid = _id("CR")
        c.execute("INSERT INTO collection_requests(coll_id,waste_id,recycler_id,quantity_kg,request_date,status) VALUES(?,?,?,?,?,'Pending')",
                  (cid, int(waste_id), int(recycler_id), qty, str(date.today())))
        c.execute("INSERT INTO status_log(collection_id,old_status,new_status,changed_by,notes,changed_at) VALUES(last_insert_rowid(),NULL,'Pending','system',?,datetime('now'))",
                  (notes.strip() if notes else "Initial dispatch request initiated",))
        return cid

def set_status(req_id, new, user, notes=""):
    with closing(conn()) as c, c:
        row = c.execute("SELECT status, quantity_kg FROM collection_requests WHERE id=?", (int(req_id),)).fetchone()
        if row is None or row[0] == new:
            return
        c.execute("UPDATE collection_requests SET status=? WHERE id=?", (new, int(req_id)))
        c.execute("INSERT INTO status_log(collection_id,old_status,new_status,changed_by,notes,changed_at) VALUES(?,?,?,?,?,datetime('now'))",
                  (int(req_id), row[0], new, user, notes.strip() if notes else None))
        if new in ("Reused", "Recycled"):  # UNIQUE(collection_id) means one processing record per request
            c.execute("INSERT OR REPLACE INTO processing_records(collection_id,outcome,quantity_kg,verified,processed_date) VALUES(?,?,?,1,date('now'))", (int(req_id), new, row[1]))
        else:
            c.execute("DELETE FROM processing_records WHERE collection_id=?", (int(req_id),))

def update_waste_qty(wid, qty):
    with closing(conn()) as c, c:
        used = c.execute("SELECT COALESCE(SUM(quantity_kg),0) FROM collection_requests WHERE waste_id=? AND status!='Rejected'", (int(wid),)).fetchone()[0]
        if qty <= 0 or qty < used:
            raise ValueError(f"Quantity must be above 0 and at least the {used:.1f} kg already requested.")
        c.execute("UPDATE waste_records SET quantity_kg=? WHERE id=?", (qty, int(wid)))

def delete_waste(wid):
    with closing(conn()) as c, c:
        c.execute("DELETE FROM waste_records WHERE id=?", (int(wid),))

def requests_df(exclude_demo=False):
    sql = ("SELECT cr.id, cr.coll_id, w.id AS waste_id, w.reg_id, w.material, w.cond, w.waste_category, w.image_path, w.is_demo, "
           "w.location AS waste_location, rd.id AS recycler_id, rd.name AS destination, rd.ftype, rd.location AS recycler_location, "
           "cr.quantity_kg, cr.request_date, cr.status "
           "FROM collection_requests cr JOIN waste_records w ON w.id=cr.waste_id JOIN recycler_directory rd ON rd.id=cr.recycler_id ")
    if exclude_demo:
        sql += "WHERE w.is_demo=0 "
    sql += "ORDER BY cr.id DESC"
    return query(sql)

def log_df(req_id):
    return query("SELECT old_status, new_status, changed_by, notes, changed_at FROM status_log WHERE collection_id=? ORDER BY id", (int(req_id),))

def _hash(pw, salt):
    return hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200_000).hex()

def has_admin():
    return int(query("SELECT COUNT(*) n FROM users").n[0]) > 0

def create_admin(username, pw):
    salt = secrets.token_hex(16)
    with closing(conn()) as c, c:
        c.execute("INSERT INTO users(username,salt,pw_hash) VALUES(?,?,?)", (username, salt, _hash(pw, salt)))

def check_admin(username, pw):
    df = query("SELECT salt, pw_hash FROM users WHERE username=?", (username,))
    return len(df) == 1 and hmac.compare_digest(df.pw_hash[0], _hash(pw, df.salt[0]))

FACILITIES = [
    ("Eco Regain Solutions Pvt. Ltd.", "Upcycling organization", "All", "Confirm with facility", "Pune", "Confirm directly with the organization",
     "Pune-based. Accepts old clothes, sorts them into reusable and scrap, and makes handcrafted products such as bags and rugs. Based on published articles (Pune International Centre, Pune365). Confirm it is still operating and which materials it accepts."),
    ("ReCircle", "Textile recycling company", "All", "Through institutional collection drives", "Pune (drives); partners in Surat and Panipat", "Confirm directly with the organization",
     "Runs textile collection drives with schools and institutions, sorts items for reuse, recycling or repurposing, and sends unusable fabric to recycling partners. Based on EducationWorld and The Week reports. Confirm intake rules before dispatch."),
    ("Respun", "Textile recycling company", "All", "Through collection drives", "India", "Confirm directly with the organization",
     "Collects used clothing from individuals, collection drives, colleges and educational institutions for recycling. Based on a published profile. Confirm intake rules before dispatch."),
    ("Samajbandh", "NGO", "All", "Confirm with facility", "Pune", "Confirm directly with the organization",
     "Pune NGO working in tribal and rural areas of Maharashtra. Received old clothes from a published collection drive. Confirm what it currently accepts."),
    ("SWaCH Pune - V Collect", "NGO", "All", "Confirm via V Collect service", "Pune", "Confirm via swachcoop.com",
     "Waste picker cooperative working with Pune Municipal Corporation. Its V Collect service takes reusable items including old clothes. Confirm service area and rules."),
    ("Passco Environmental Solutions Pvt. Ltd.", "Authorized waste collection agency", "All", "Through membership of the facility", "Moshi, Pune", "Confirm directly with the operator",
     "Operator of a common biomedical waste treatment facility in Pune named in Maharashtra Pollution Control Board documents. Confirm current MPCB authorization before use."),
    ("Life Secure Enterprises", "Authorized waste collection agency", "All", "Through membership of the facility", "Talegaon Dabhade, Pune", "Confirm directly with the operator",
     "Common biomedical waste treatment facility in Talegaon Dabhade, Pune, named as an approved facility in a published document. Confirm current MPCB authorization before use."),
]

def add_recycler(name, ftype, materials, collection, location, contact, description):
    if not (name.strip() and location.strip()):
        raise ValueError("Name and location are required.")
    with closing(conn()) as c, c:
        c.execute("INSERT INTO recycler_directory(name,ftype,materials,collection,location,contact,description,is_demo) VALUES(?,?,?,?,?,?,?,0)",
                  (name.strip(), ftype, materials.strip() or "All", collection.strip() or "Confirm with facility", location.strip(), contact.strip() or "Confirm directly", description.strip()))

def init_db():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with closing(conn()) as c, c:
        c.executescript(SCHEMA)
        # column migrations
        cols_w = [row[1] for row in c.execute("PRAGMA table_info(waste_records)").fetchall()]
        if "image_path" not in cols_w:
            c.execute("ALTER TABLE waste_records ADD COLUMN image_path TEXT")
        cols_s = [row[1] for row in c.execute("PRAGMA table_info(status_log)").fetchall()]
        if "notes" not in cols_s:
            c.execute("ALTER TABLE status_log ADD COLUMN notes TEXT")
        # remove the fictional facilities from earlier versions (and requests linked to them)
        c.execute("DELETE FROM collection_requests WHERE recycler_id IN (SELECT id FROM recycler_directory WHERE name LIKE '%(DEMO)')")
        c.execute("DELETE FROM recycler_directory WHERE name LIKE '%(DEMO)'")
        if c.execute("SELECT COUNT(*) FROM recycler_directory").fetchone()[0] == 0:
            c.executemany("INSERT INTO recycler_directory(name,ftype,materials,collection,location,contact,description,is_demo) VALUES(?,?,?,?,?,?,?,0)", FACILITIES)
        if c.execute("SELECT COUNT(*) FROM waste_records").fetchone()[0] == 0:
            _seed_waste(c)

def _seed_waste(c):
    wastes = [  # sample waste records only, labelled DEMO
        ("Demo College Admin (DEMO)", "Sample College of Science", "College", "Uniforms", "Cotton", "Good condition", 120, 100, "Pune"),
        ("Demo Hostel Warden (DEMO)", "Sample Girls Hostel", "Hostel", "Bedsheets & linen", "Cotton", "Slightly damaged", 80, 70, "Pune"),
        ("Demo Tailor (DEMO)", "Sample Tailoring Shop", "Tailoring Shop", "Fabric scraps", "Cotton", "Heavily damaged", 45, 40, "Pune"),
        ("Demo Hotel Manager (DEMO)", "Sample Hotel", "Hotel", "Curtains & drapes", "Polyester", "Slightly damaged", 60, 15, "Pune"),
        ("Demo Hospital Store (DEMO)", "Sample Clinic", "Hospital", "Clothes", "Cotton", "Contaminated or potentially infectious", 25, 20, "Pune"),
    ]
    for g, inst, gc, it, m, cond, kg, ago, loc in wastes:
        _insert_waste(c, dict(generator=g, institution=inst, gen_category=gc, item_type=it, material=m, cond=cond, quantity_kg=kg, location=loc,
                              contact="demo@example.com", reg_date=date.today() - timedelta(days=ago), description="Sample record for demonstration", is_demo=1))
