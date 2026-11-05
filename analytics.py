from collections import defaultdict
from datetime import datetime,timedelta
def fetch(db,start,end):
    return db.execute("""SELECT e.id,e.title,e.start_ts,e.end_ts,c.name,c.weight,c.color FROM entries e JOIN categories c ON c.id=e.category_id WHERE e.end_ts IS NOT NULL AND e.end_ts>? AND e.start_ts<? ORDER BY e.start_ts DESC""",(start,end)).fetchall()
def minutes(r): return max(0,(r["end_ts"]-r["start_ts"])/60)
def category_breakdown(rows):
    out=defaultdict(float)
    for r in rows: out[r["name"]]+=minutes(r)
    return {k:round(v,1) for k,v in sorted(out.items(),key=lambda x:-x[1])}
def productivity_score(rows):
    total=sum(minutes(r) for r in rows)
    return round(100*sum(minutes(r)*r["weight"] for r in rows)/total,1) if total else 0.0
def daily_totals(rows):
    out=defaultdict(float)
    for r in rows:
        t=datetime.fromtimestamp(r["start_ts"]); end=datetime.fromtimestamp(r["end_ts"])
        while t<end:
            nxt=min(end,t.replace(hour=0,minute=0,second=0,microsecond=0)+timedelta(days=1))
            out[t.strftime("%Y-%m-%d")]+=(nxt-t).total_seconds()/60; t=nxt
    return {k:round(v,1) for k,v in sorted(out.items())}
def heatmap(rows):
    grid=[[0.0]*24 for _ in range(7)]
    for r in rows:
        t=datetime.fromtimestamp(r["start_ts"]); end=datetime.fromtimestamp(r["end_ts"])
        while t<end:
            nxt=min(end,t.replace(minute=0,second=0,microsecond=0)+timedelta(hours=1))
            grid[t.weekday()][t.hour]+=(nxt-t).total_seconds()/60; t=nxt
    return [[round(v,1) for v in row] for row in grid]
def insights(rows):
    if not rows: return ["Start tracking activities to see your productivity insights."]
    cats=category_breakdown(rows); total=sum(cats.values()); hours=[sum(day[h] for day in heatmap(rows)) for h in range(24)]
    peak=max(range(24),key=lambda h:hours[h]); top,mins=next(iter(cats.items()))
    distracting=sum(minutes(r) for r in rows if r["weight"]==0)
    tips=[f"Your busiest hour is {peak:02d}:00–{(peak+1)%24:02d}:00.",f"{top} is your biggest activity, accounting for {100*mins/total:.0f}% of tracked time."]
    tips.append(f"{100*distracting/total:.0f}% of your tracked time went to distracting categories. Consider setting a limit." if distracting/total>.25 else "Nice balance. Keep protecting time for high-focus activities.")
    return tips
