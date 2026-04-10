import os
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder="templates")

# ─── DATABASE ──────────────────────────────────────────────────────────────────
# On Render.com, use /tmp for writable storage
DB_PATH = os.environ.get("DB_PATH", "digisupply.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            hospitalId TEXT,
            customer TEXT,
            product TEXT,
            qty INTEGER,
            date TEXT,
            status TEXT,
            value REAL,
            notes TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS inventory (
            id TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            stock INTEGER,
            reorder INTEGER,
            unit TEXT,
            supplier TEXT
        );
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            hospitalId TEXT,
            customer TEXT,
            product TEXT,
            issue TEXT,
            priority TEXT,
            details TEXT DEFAULT '',
            date TEXT,
            engineer TEXT DEFAULT 'Unassigned',
            status TEXT
        );
    """)

    # Seed orders
    if c.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0:
        orders = [
            ("ORD-001","H001","Lilavati Hospital","MicroQuark USB Spirometer",2,"2025-01-05","Delivered",180000,""),
            ("ORD-002","H002","Kokilaben Hospital","Suction Machine - Dominant Flex",3,"2025-01-12","Delivered",96000,""),
            ("ORD-003","H003","Fortis Healthcare","AED Plus (ZOLL)",2,"2025-01-18","Delivered",300000,""),
            ("ORD-004","H004","Nanavati Hospital","Scoop Stretcher (Spencer)",5,"2025-02-01","Delivered",125000,""),
            ("ORD-005","H001","Lilavati Hospital","Rad-97 Table-top Pulse Oximeter",8,"2025-02-10","Delivered",320000,""),
            ("ORD-006","H006","Wockhardt Hospital","Steam Sterilizer (Belimed)",1,"2025-02-14","Delivered",850000,""),
            ("ORD-007","H007","HN Reliance Hospital","Suction Machine - Vario-18",4,"2025-02-20","Delivered",120000,""),
            ("ORD-008","H002","Kokilaben Hospital","Autopulse NXT (ZOLL)",1,"2025-03-01","Delivered",650000,""),
            ("ORD-009","H003","Fortis Healthcare","Rad-G Handheld Pulse Oximeter",5,"2025-03-05","Delivered",110000,""),
            ("ORD-010","H004","Nanavati Hospital","Rad-97 with NIBP Pulse Oximeter",3,"2025-03-08","Delivered",165000,""),
            ("ORD-011","H005","Breach Candy Hospital","AED 3 (ZOLL)",2,"2025-03-12","Delivered",320000,""),
            ("ORD-012","H007","HN Reliance Hospital","Rad-97 Table-top Pulse Oximeter",3,"2025-03-15","Delivered",120000,""),
            ("ORD-013","H001","Lilavati Hospital","911 Emergency Backpack",5,"2025-03-18","Delivered",42500,""),
            ("ORD-014","H006","Wockhardt Hospital","EMMA Capnograph (Masimo)",1,"2025-03-22","Delivered",95000,""),
            ("ORD-015","H002","Kokilaben Hospital","MicroQuark USB Spirometer",1,"2025-03-28","Delivered",90000,""),
            ("ORD-016","H001","Lilavati Hospital","AED Plus (ZOLL)",1,"2025-04-02","Dispatched",150000,""),
            ("ORD-017","H003","Fortis Healthcare","Suction Machine - Dominant Flex",2,"2025-04-04","Dispatched",64000,""),
            ("ORD-018","H004","Nanavati Hospital","Rad-97 with NIBP Pulse Oximeter",3,"2025-04-07","Processing",165000,""),
            ("ORD-019","H002","Kokilaben Hospital","Scoop Stretcher (Spencer)",4,"2025-04-09","Processing",100000,""),
            ("ORD-020","H005","Breach Candy Hospital","Autopulse NXT (ZOLL)",1,"2025-04-11","Received",650000,""),
            ("ORD-021","H007","HN Reliance Hospital","AED 3 (ZOLL)",2,"2025-04-14","Received",320000,""),
            ("ORD-022","H006","Wockhardt Hospital","Rad-G Handheld Pulse Oximeter",6,"2025-04-16","Processing",132000,""),
            ("ORD-023","H001","Lilavati Hospital","Steam Sterilizer (Belimed)",1,"2025-04-18","Received",850000,""),
            ("ORD-024","H003","Fortis Healthcare","911 Emergency Backpack",8,"2025-04-20","Dispatched",68000,""),
            ("ORD-025","H004","Nanavati Hospital","MicroQuark USB Spirometer",1,"2025-04-23","Received",90000,""),
            ("ORD-026","H002","Kokilaben Hospital","ROOT Monitor (Masimo)",1,"2025-04-25","Processing",180000,""),
            ("ORD-027","H005","Breach Candy Hospital","Suction Machine - Vario-18",3,"2025-04-27","Received",84000,""),
            ("ORD-028","H007","HN Reliance Hospital","EMMA Capnograph (Masimo)",2,"2025-04-29","Received",190000,""),
        ]
        c.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)", orders)

    # Seed inventory
    if c.execute("SELECT COUNT(*) FROM inventory").fetchone()[0] == 0:
        inventory = [
            ("PRD-001","MicroQuark USB Spirometer","PFT & Spirometry",8,3,"Units","COSMED, Italy"),
            ("PRD-002","QuarkPFT with Body Plethysmograph","PFT & Spirometry",3,2,"Units","COSMED, Italy"),
            ("PRD-003","K5 Wireless CPET","PFT & Spirometry",2,1,"Units","COSMED, Italy"),
            ("PRD-004","Q-NRG Max Metabolic Monitor","PFT & Spirometry",2,1,"Units","COSMED, Italy"),
            ("PRD-005","AED Plus (ZOLL)","Defibrillator",6,3,"Units","ZOLL, USA"),
            ("PRD-006","PowerHeart G5 (ZOLL)","Defibrillator",4,2,"Units","ZOLL, USA"),
            ("PRD-007","AED 3 (ZOLL)","Defibrillator",5,2,"Units","ZOLL, USA"),
            ("PRD-008","M2 Defibrillator (ZOLL)","Defibrillator",3,2,"Units","ZOLL, USA"),
            ("PRD-009","R-SERIES Defibrillator (ZOLL)","Defibrillator",2,2,"Units","ZOLL, USA"),
            ("PRD-010","X-SERIES Defibrillator (ZOLL)","Defibrillator",2,1,"Units","ZOLL, USA"),
            ("PRD-011","Autopulse NXT (ZOLL)","Chest Compression",3,2,"Units","ZOLL, USA"),
            ("PRD-012","AED Trainer (Laerdal)","Training Equipment",10,4,"Units","Laerdal"),
            ("PRD-013","Prestan CPR Manikin with Feedback","Training Equipment",8,3,"Units","Laerdal"),
            ("PRD-014","Rad-97 Table-top Pulse Oximeter","Pulse Oximeter",12,5,"Units","Masimo, USA"),
            ("PRD-015","Rad-97 with NIBP Pulse Oximeter","Pulse Oximeter",8,4,"Units","Masimo, USA"),
            ("PRD-016","Rad-97 with Capnography","Pulse Oximeter",4,2,"Units","Masimo, USA"),
            ("PRD-017","Rad-G Handheld Pulse Oximeter","Pulse Oximeter",15,6,"Units","Masimo, USA"),
            ("PRD-018","Rad-57 Spot Check SpCO","Pulse Oximeter",6,3,"Units","Masimo, USA"),
            ("PRD-019","ROOT Monitor (Masimo)","Patient Monitoring",3,2,"Units","Masimo, USA"),
            ("PRD-020","EMMA Capnograph (Masimo)","Patient Monitoring",4,2,"Units","Masimo, USA"),
            ("PRD-021","Radius VSM (Masimo)","Patient Monitoring",3,2,"Units","Masimo, USA"),
            ("PRD-022","LiDCO Hemodynamic Monitor","Patient Monitoring",2,1,"Units","Masimo, USA"),
            ("PRD-023","Suction Machine - Dominant Flex","Suction Pump",10,4,"Units","Medela, Switzerland"),
            ("PRD-024","Suction Machine - Vario-18","Suction Pump",7,3,"Units","Spencer, Italy"),
            ("PRD-025","Suction Machine - Blanco","Suction Pump",6,3,"Units","Spencer, Italy"),
            ("PRD-026","Suction Machine - AmbuJet","Suction Pump",8,4,"Units","Spencer, Italy"),
            ("PRD-027","Vacuum Assisted Delivery","Suction Pump",4,2,"Units","Medela, Switzerland"),
            ("PRD-028","Carrera TEC Auto-loading Stretcher","Ambulance & Emergency",4,2,"Units","Spencer, Italy"),
            ("PRD-029","KINETIX Electric Stretcher","Ambulance & Emergency",3,2,"Units","Spencer, Italy"),
            ("PRD-030","Scoop Stretcher (Spencer)","Ambulance & Emergency",10,4,"Units","Spencer, Italy"),
            ("PRD-031","Shell Basket Stretcher","Ambulance & Emergency",6,3,"Units","Spencer, Italy"),
            ("PRD-032","Evacuation Chair","Ambulance & Emergency",5,2,"Units","Spencer, Italy"),
            ("PRD-033","911 Emergency Backpack","Bags & Backpacks",12,5,"Units","Spencer, Italy"),
            ("PRD-034","Emergency Bag","Bags & Backpacks",15,6,"Units","Spencer, Italy"),
            ("PRD-035","B-Bak Spine Board with Immobiliser","Ambulance & Emergency",7,3,"Units","Spencer, Italy"),
            ("PRD-036","Steam Sterilizer (Belimed)","CSSD",2,1,"Units","Belimed, Switzerland"),
            ("PRD-037","Washer Disinfector (Belimed)","CSSD",2,1,"Units","Belimed, Switzerland"),
            ("PRD-038","Heat Sealing Machine","CSSD",5,2,"Units","Belimed, Switzerland"),
            ("PRD-039","Endoscopic Washer (Belimed)","CSSD",2,1,"Units","Belimed, Switzerland"),
            ("PRD-040","Plasma Sterilizer (ASP)","CSSD",2,1,"Units","ASP"),
            ("PRD-041","CSSD Disposables","CSSD",200,50,"Packs","Medovation"),
            ("PRD-042","First Aid Kit (St. John's)","First Aid",30,10,"Units","St. John's"),
            ("PRD-043","Gel Position Pads (Oasis)","First Aid",20,8,"Sets","Oasis"),
            ("PRD-044","Fibre-optic Laryngoscope","Laryngoscopes",6,2,"Units","Oasis"),
            ("PRD-045","MRI Compatible Equipment","MRI",4,2,"Units","Various"),
            ("PRD-046","Negative Pressure Thopaz+ Digital","Thoracic",3,2,"Units","Medela, Switzerland"),
            ("PRD-047","Symphony Breast Pump (Medela)","Maternity",5,3,"Units","Medela, Switzerland"),
            ("PRD-048","IVTM Temperature Management","Temperature Management",3,1,"Units","ZOLL, USA"),
        ]
        c.executemany("INSERT INTO inventory VALUES (?,?,?,?,?,?,?)", inventory)

    # Seed tickets
    if c.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 0:
        tickets = [
            ("SRV-001","H001","Lilavati Hospital","AED Plus (ZOLL)","Electrode pads worn out","High","","2025-01-08","Rahul Patil","Resolved"),
            ("SRV-002","H002","Kokilaben Hospital","Rad-97 Table-top Pulse Oximeter","Display flickering","Medium","","2025-01-15","Sameer Joshi","Resolved"),
            ("SRV-003","H003","Fortis Healthcare","AED Plus (ZOLL)","Battery not charging","High","","2025-01-22","Rahul Patil","Resolved"),
            ("SRV-004","H004","Nanavati Hospital","Steam Sterilizer (Belimed)","Temperature alarm triggering","High","","2025-02-03","Priya Nair","Resolved"),
            ("SRV-005","H006","Wockhardt Hospital","Autopulse NXT (ZOLL)","Belt alignment issue","Medium","","2025-02-10","Sameer Joshi","Resolved"),
            ("SRV-006","H002","Kokilaben Hospital","Rad-97 Table-top Pulse Oximeter","SpO2 sensor inaccurate","Medium","","2025-02-14","Rahul Patil","Resolved"),
            ("SRV-007","H005","Breach Candy Hospital","Rad-97 with NIBP Pulse Oximeter","Rainbow SpO2 sensor damaged","High","","2025-02-20","Priya Nair","Resolved"),
            ("SRV-008","H003","Fortis Healthcare","ROOT Monitor (Masimo)","NIBP hose assembly leaking","Medium","","2025-03-02","Sameer Joshi","Resolved"),
            ("SRV-009","H007","HN Reliance Hospital","Suction Machine - Dominant Flex","Motor noise during operation","Medium","","2025-03-08","Rahul Patil","Resolved"),
            ("SRV-010","H001","Lilavati Hospital","MicroQuark USB Spirometer","Flow sensor reading off","Low","","2025-03-12","Priya Nair","Resolved"),
            ("SRV-011","H004","Nanavati Hospital","Scoop Stretcher (Spencer)","Wheel and axle broken","Medium","","2025-03-18","Sameer Joshi","Resolved"),
            ("SRV-012","H006","Wockhardt Hospital","AED 3 (ZOLL)","Printer paper jam","Low","","2025-03-25","Rahul Patil","Resolved"),
            ("SRV-013","H002","Kokilaben Hospital","Suction Machine - Vario-18","Canister seal leaking","Medium","","2025-04-02","Sameer Joshi","Resolved"),
            ("SRV-014","H001","Lilavati Hospital","AED Plus (ZOLL)","Battery pack not holding charge","High","","2025-04-05","Rahul Patil","In Progress"),
            ("SRV-015","H003","Fortis Healthcare","Rad-97 with NIBP Pulse Oximeter","NIBP cuff not inflating","Medium","","2025-04-08","Priya Nair","In Progress"),
            ("SRV-016","H005","Breach Candy Hospital","EMMA Capnograph (Masimo)","CO2 sensor calibration off","Medium","","2025-04-12","Sameer Joshi","Assigned"),
            ("SRV-017","H007","HN Reliance Hospital","Scoop Stretcher (Spencer)","Fastening belt worn out","Low","","2025-04-15","Unassigned","Reported"),
            ("SRV-018","H004","Nanavati Hospital","Steam Sterilizer (Belimed)","Door gasket needs replacement","High","","2025-04-18","Rahul Patil","Assigned"),
            ("SRV-019","H006","Wockhardt Hospital","MicroQuark USB Spirometer","Mouthpiece adapter broken","Low","","2025-04-22","Unassigned","Reported"),
            ("SRV-020","H002","Kokilaben Hospital","Autopulse NXT (ZOLL)","Device not powering on","High","","2025-04-25","Rahul Patil","In Progress"),
        ]
        c.executemany("INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?,?,?)", tickets)

    conn.commit()
    conn.close()

PRODUCT_PRICES = {
    "MicroQuark USB Spirometer":90000,"QuarkPFT with Body Plethysmograph":450000,
    "K5 Wireless CPET":850000,"Q-NRG Max Metabolic Monitor":620000,
    "AED Plus (ZOLL)":150000,"PowerHeart G5 (ZOLL)":180000,"AED 3 (ZOLL)":160000,
    "M2 Defibrillator (ZOLL)":280000,"R-SERIES Defibrillator (ZOLL)":320000,
    "X-SERIES Defibrillator (ZOLL)":420000,"Autopulse NXT (ZOLL)":650000,
    "AED Trainer (Laerdal)":25000,"Prestan CPR Manikin with Feedback":18000,
    "Rad-97 Table-top Pulse Oximeter":40000,"Rad-97 with NIBP Pulse Oximeter":55000,
    "Rad-97 with Capnography":75000,"Rad-G Handheld Pulse Oximeter":22000,
    "Rad-57 Spot Check SpCO":48000,"ROOT Monitor (Masimo)":180000,
    "EMMA Capnograph (Masimo)":95000,"Radius VSM (Masimo)":120000,
    "LiDCO Hemodynamic Monitor":350000,"Suction Machine - Dominant Flex":32000,
    "Suction Machine - Vario-18":28000,"Suction Machine - Blanco":24000,
    "Suction Machine - AmbuJet":26000,"Vacuum Assisted Delivery":45000,
    "Carrera TEC Auto-loading Stretcher":180000,"KINETIX Electric Stretcher":220000,
    "Scoop Stretcher (Spencer)":25000,"Shell Basket Stretcher":18000,
    "Evacuation Chair":35000,"911 Emergency Backpack":8500,"Emergency Bag":4500,
    "B-Bak Spine Board with Immobiliser":22000,"Steam Sterilizer (Belimed)":850000,
    "Washer Disinfector (Belimed)":750000,"Heat Sealing Machine":45000,
    "Endoscopic Washer (Belimed)":680000,"Plasma Sterilizer (ASP)":920000,
    "CSSD Disposables":2500,"First Aid Kit (St. John's)":1800,
    "Gel Position Pads (Oasis)":3500,"Fibre-optic Laryngoscope":85000,
    "MRI Compatible Equipment":120000,"Negative Pressure Thopaz+ Digital":280000,
    "Symphony Breast Pump (Medela)":95000,"IVTM Temperature Management":380000,
}

HOSPITALS = [
    {"id":"H001","name":"Lilavati Hospital","password":"lila123","contact":"Dr. Mehta"},
    {"id":"H002","name":"Kokilaben Hospital","password":"koki123","contact":"Dr. Shah"},
    {"id":"H003","name":"Fortis Healthcare","password":"fort123","contact":"Dr. Gupta"},
    {"id":"H004","name":"Nanavati Hospital","password":"nana123","contact":"Dr. Joshi"},
    {"id":"H005","name":"Breach Candy Hospital","password":"breach123","contact":"Dr. Patel"},
    {"id":"H006","name":"Wockhardt Hospital","password":"wock123","contact":"Dr. Iyer"},
    {"id":"H007","name":"HN Reliance Hospital","password":"hnr123","contact":"Dr. Desai"},
]

ORDER_FLOW = ["Received","Processing","Dispatched","Delivered"]
SVC_FLOW   = ["Reported","Assigned","In Progress","Resolved"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/login/hospital", methods=["POST"])
def login_hospital():
    data = request.json
    h = next((x for x in HOSPITALS if x["id"]==data.get("id") and x["password"]==data.get("password")),None)
    if h: return jsonify({"ok":True,"hospital":{k:v for k,v in h.items() if k!="password"}})
    return jsonify({"ok":False,"error":"Invalid credentials"}),401

@app.route("/api/login/staff", methods=["POST"])
def login_staff():
    data = request.json
    if data.get("username")=="summit_admin" and data.get("password")=="summit@123":
        return jsonify({"ok":True})
    return jsonify({"ok":False,"error":"Invalid credentials"}),401

@app.route("/api/hospitals")
def get_hospitals():
    return jsonify([{k:v for k,v in h.items() if k!="password"} for h in HOSPITALS])

@app.route("/api/orders")
def get_orders():
    conn = get_db()
    hid = request.args.get("hospitalId")
    if hid:
        rows = conn.execute("SELECT * FROM orders WHERE hospitalId=? ORDER BY date DESC",(hid,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM orders ORDER BY date DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/orders", methods=["POST"])
def add_order():
    data = request.json
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    new_id = f"ORD-{count+1:03d}"
    value = PRODUCT_PRICES.get(data["product"],0) * int(data["qty"])
    conn.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)",(
        new_id,data["hospitalId"],data["customer"],data["product"],
        int(data["qty"]),data["date"],"Received",value,data.get("notes","")
    ))
    conn.commit()
    row = conn.execute("SELECT * FROM orders WHERE id=?",(new_id,)).fetchone()
    conn.close()
    return jsonify(dict(row))

@app.route("/api/orders/<oid>/advance", methods=["POST"])
def advance_order(oid):
    conn = get_db()
    o = conn.execute("SELECT * FROM orders WHERE id=?",(oid,)).fetchone()
    if not o: conn.close(); return jsonify({"error":"Not found"}),404
    idx = ORDER_FLOW.index(o["status"])
    if idx < len(ORDER_FLOW)-1:
        conn.execute("UPDATE orders SET status=? WHERE id=?",(ORDER_FLOW[idx+1],oid))
        conn.commit()
    row = conn.execute("SELECT * FROM orders WHERE id=?",(oid,)).fetchone()
    conn.close()
    return jsonify(dict(row))

@app.route("/api/inventory")
def get_inventory():
    conn = get_db()
    rows = conn.execute("SELECT * FROM inventory ORDER BY category,name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/inventory", methods=["POST"])
def add_inventory():
    data = request.json
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    new_id = f"PRD-{count+1:03d}"
    conn.execute("INSERT INTO inventory VALUES (?,?,?,?,?,?,?)",(
        new_id,data["name"],data["category"],int(data["stock"]),
        int(data["reorder"]),data.get("unit","Units"),data["supplier"]
    ))
    conn.commit()
    row = conn.execute("SELECT * FROM inventory WHERE id=?",(new_id,)).fetchone()
    conn.close()
    return jsonify(dict(row))

@app.route("/api/inventory/<iid>", methods=["PUT"])
def update_inventory(iid):
    data = request.json
    conn = get_db()
    conn.execute("""UPDATE inventory SET name=?,category=?,stock=?,reorder=?,unit=?,supplier=?
                    WHERE id=?""",(data["name"],data["category"],int(data["stock"]),
                    int(data["reorder"]),data.get("unit","Units"),data["supplier"],iid))
    conn.commit()
    row = conn.execute("SELECT * FROM inventory WHERE id=?",(iid,)).fetchone()
    conn.close()
    return jsonify(dict(row))

@app.route("/api/tickets")
def get_tickets():
    conn = get_db()
    hid = request.args.get("hospitalId")
    if hid:
        rows = conn.execute("SELECT * FROM tickets WHERE hospitalId=? ORDER BY date DESC",(hid,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM tickets ORDER BY date DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/tickets", methods=["POST"])
def add_ticket():
    data = request.json
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    new_id = f"SRV-{count+1:03d}"
    conn.execute("INSERT INTO tickets VALUES (?,?,?,?,?,?,?,?,?,?)",(
        new_id,data["hospitalId"],data["customer"],data["product"],
        data["issue"],data.get("priority","Medium"),data.get("details",""),
        data["date"],"Unassigned","Reported"
    ))
    conn.commit()
    row = conn.execute("SELECT * FROM tickets WHERE id=?",(new_id,)).fetchone()
    conn.close()
    return jsonify(dict(row))

@app.route("/api/tickets/<tid>/advance", methods=["POST"])
def advance_ticket(tid):
    conn = get_db()
    t = conn.execute("SELECT * FROM tickets WHERE id=?",(tid,)).fetchone()
    if not t: conn.close(); return jsonify({"error":"Not found"}),404
    idx = SVC_FLOW.index(t["status"])
    if idx < len(SVC_FLOW)-1:
        conn.execute("UPDATE tickets SET status=? WHERE id=?",(SVC_FLOW[idx+1],tid))
        conn.commit()
    row = conn.execute("SELECT * FROM tickets WHERE id=?",(tid,)).fetchone()
    conn.close()
    return jsonify(dict(row))

@app.route("/api/tickets/<tid>/engineer", methods=["PUT"])
def assign_engineer(tid):
    conn = get_db()
    conn.execute("UPDATE tickets SET engineer=? WHERE id=?",(request.json.get("engineer","Unassigned"),tid))
    conn.commit()
    row = conn.execute("SELECT * FROM tickets WHERE id=?",(tid,)).fetchone()
    conn.close()
    return jsonify(dict(row))

@app.route("/api/products")
def get_products():
    return jsonify([{"name":k,"price":v} for k,v in PRODUCT_PRICES.items()])

# Init DB on startup
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False)
