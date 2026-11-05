# TimeLoom — Full Productivity Tracker

A complete local productivity web app using Flask, SQLite, HTML, CSS and JavaScript.

## Features
- Activity tracking with category and task title; start/stop timer
- Productivity score and category breakdown
- Daily focus goal progress
- Weekly activity chart and 28-day weekday/hour heatmap
- Automatic productivity insights
- 25-minute focus / 5-minute break Pomodoro timer
- SQLite database created automatically

## Run on Windows
1. Extract this ZIP.
2. Open PowerShell in the `TimeLoom_Full` folder.
3. Optional virtual environment:
   `py -m venv .venv`
   `.\.venv\Scripts\Activate.ps1`
4. Install: `python -m pip install -r requirements.txt`
5. Run: `python app.py`
6. Open: http://127.0.0.1:5000

Keep the terminal open while using the app. Press Ctrl+C to stop it.
No Node.js or separate frontend server is needed.

## Structure
- app.py — Flask server and JSON API
- db.py — SQLite schema and initialization
- analytics.py — productivity calculations
- config.json — category weights, colors and goals
- static/index.html, style.css, script.js — complete frontend
