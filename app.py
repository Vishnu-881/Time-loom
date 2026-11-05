import time
from datetime import datetime
from flask import Flask,jsonify,request
from db import get_db
import analytics
app=Flask(__name__,static_folder="static",static_url_path="")
db,cfg=get_db()
def win(days):
    end=time.time(); return end-days*86400,end
def data(): return request.get_json(silent=True) or {}
@app.get("/")
def home(): return app.send_static_file("index.html")
@app.get("/api/categories")
def categories(): return jsonify([dict(r) for r in db.execute("SELECT id,name,weight,color FROM categories ORDER BY id").fetchall()])
@app.get("/api/running")
def running():
    r=db.execute("SELECT e.id,e.title,e.start_ts,c.name AS category,c.color FROM entries e JOIN categories c ON c.id=e.category_id WHERE e.end_ts IS NULL LIMIT 1").fetchone()
    return jsonify(dict(r) if r else None)
@app.post("/api/timer/start")
def start():
    d=data(); c=db.execute("SELECT id FROM categories WHERE name=?",(d.get("category"),)).fetchone()
    if not c: return jsonify(error="Choose a valid category."),400
    if db.execute("SELECT id FROM entries WHERE end_ts IS NULL LIMIT 1").fetchone(): return jsonify(error="A timer is already running. Stop it first."),409
    cur=db.execute("INSERT INTO entries(category_id,title,start_ts) VALUES(?,?,?)",(c["id"],str(d.get("title",""))[:120],time.time())); db.commit()
    return jsonify(id=cur.lastrowid),201
@app.post("/api/timer/<int:eid>/stop")
def stop(eid):
    cur=db.execute("UPDATE entries SET end_ts=? WHERE id=? AND end_ts IS NULL",(time.time(),eid)); db.commit()
    if not cur.rowcount: return jsonify(error="That timer is not running."),404
    return jsonify(ok=True)
@app.post("/api/entries")
def add_entry():
    d=data()
    try: start,end=float(d["start"]),float(d["end"]); name=d["category"]
    except (KeyError,TypeError,ValueError): return jsonify(error="Provide category, start and end timestamps."),400
    c=db.execute("SELECT id FROM categories WHERE name=?",(name,)).fetchone()
    if not c or end<=start or end>time.time()+60: return jsonify(error="Invalid category or time range."),400
    db.execute("INSERT INTO entries(category_id,title,start_ts,end_ts,note) VALUES(?,?,?,?,?)",(c["id"],str(d.get("title",""))[:120],start,end,str(d.get("note",""))[:500])); db.commit()
    return jsonify(ok=True),201
@app.get("/api/summary")
def summary():
    try: days=max(1,min(365,int(request.args.get("days",7))))
    except ValueError: return jsonify(error="days must be an integer"),400
    rows=analytics.fetch(db,*win(days))
    return jsonify(breakdown=analytics.category_breakdown(rows),score=analytics.productivity_score(rows),daily=analytics.daily_totals(rows),total_minutes=round(sum(analytics.minutes(r) for r in rows),1),entries=len(rows))
@app.get("/api/heatmap")
def heat(): return jsonify(grid=analytics.heatmap(analytics.fetch(db,*win(28))))
@app.get("/api/insights")
def tips(): return jsonify(tips=analytics.insights(analytics.fetch(db,*win(7))))
@app.get("/api/goal")
def goal():
    now=datetime.now(); start=now.replace(hour=0,minute=0,second=0,microsecond=0).timestamp()
    rows=analytics.fetch(db,start,start+86400); done=sum(analytics.minutes(r) for r in rows if r["weight"]==1.0); target=int(cfg["goals"]["daily_focus_minutes"])
    return jsonify(day=now.strftime("%Y-%m-%d"),focus_minutes=round(done),target=target,progress=min(100,round(100*done/target)) if target else 0)
@app.post("/api/focus")
def focus():
    d=data()
    try: mins=int(d.get("minutes",cfg["focus"]["work_minutes"]))
    except (TypeError,ValueError): return jsonify(error="Invalid session length."),400
    if not 1<=mins<=180: return jsonify(error="Session must be 1–180 minutes."),400
    db.execute("INSERT INTO focus_sessions(entry_id,planned_min,completed,created_ts) VALUES(?,?,?,?)",(d.get("entry_id"),mins,int(bool(d.get("completed"))),time.time())); db.commit()
    return jsonify(ok=True),201
@app.get("/api/settings")
def settings(): return jsonify(focus=cfg["focus"],goals=cfg["goals"])
if __name__=="__main__": app.run(host="127.0.0.1",port=5000,debug=True)
