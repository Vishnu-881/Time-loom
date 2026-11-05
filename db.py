import json, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SCHEMA = """
CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT UNIQUE NOT NULL,weight REAL DEFAULT 0.5,color TEXT DEFAULT '#888888');
CREATE TABLE IF NOT EXISTS entries(id INTEGER PRIMARY KEY AUTOINCREMENT,category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,title TEXT DEFAULT '',start_ts REAL NOT NULL,end_ts REAL,note TEXT DEFAULT '');
CREATE TABLE IF NOT EXISTS focus_sessions(id INTEGER PRIMARY KEY AUTOINCREMENT,entry_id INTEGER REFERENCES entries(id) ON DELETE SET NULL,planned_min INTEGER NOT NULL,completed INTEGER DEFAULT 0,created_ts REAL NOT NULL);
"""
def get_db():
    db=sqlite3.connect(ROOT/'timeloom.db',check_same_thread=False); db.row_factory=sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON"); db.executescript(SCHEMA)
    cfg=json.loads((ROOT/'config.json').read_text(encoding='utf-8'))
    for name,c in cfg["categories"].items():
        db.execute("INSERT OR IGNORE INTO categories(name,weight,color) VALUES(?,?,?)",(name,c["weight"],c["color"]))
    db.commit(); return db,cfg
