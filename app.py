
# app.py
import io
import time
import hashlib
from dataclasses import dataclass
from typing import Dict, List

from flask import Flask, request, jsonify, make_response, render_template_string
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless backend for server-side rendering
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # dev: avoid caching static responses

# -------------------- Domain --------------------
USERS = [
    {"name": "User A", "skill": "Python"},
    {"name": "User B", "skill": "SQL"},
    {"name": "User C", "skill": "UI/UX"},
]
PROJECTS = ["IBSS", "Retain", "WFM"]

# Per your requirement, everything is local and random;
# No data is fetched from the network or files.
@dataclass
class DayPoint:
    date: str
    hours: float
    expected: float
    mismatch: bool
    anomaly: str  # 'over' | 'under' | 'none'

EXPECTED_HOURS = 6.0         # baseline hours/day
ANOMALY_MARGIN = 1.5         # +/- margin to flag anomalies
DAYS = 14                    # number of days to simulate

# Stable colors per user
COLORS = {
    "User A": "#2563eb",  # blue
    "User B": "#ea580c",  # orange
    "User C": "#16a34a",  # green
}

# Per-project required skill bias (just a simple illustrative mapping)
PROJECT_SKILL_BIAS = {
    "IBSS":   ["Java", "SQL", "Python"],
    "Retain": ["Python", "UI/UX", "SQL"],
    "WFM":    ["SQL", "Python", "DataEng"],
}

def stable_seed(project: str, user_name: str, base: int = 2025) -> int:
    """
    Derive a repeatable seed from project+user so the same selection
    produces the same random series across runs (useful for demo/testing).
    """
    h = hashlib.sha256(f"{project}:{user_name}".encode()).hexdigest()
    return base + int(h[:8], 16)

def generate_series(project: str, user: Dict, days: int = DAYS,
                    expected_hours: float = EXPECTED_HOURS,
                    anomaly_margin: float = ANOMALY_MARGIN) -> Dict:
    """
    Generate time-series for a user's daily hours using local randomness only.
    Flags:
      - skill mismatch if required_skill != user.skill
      - 'over' if hours > expected + margin
      - 'under' if hours < expected - margin
    """
    rng = np.random.default_rng(stable_seed(project, user["name"]))
    required_pool = PROJECT_SKILL_BIAS.get(project, [user["skill"]])

    start = pd.Timestamp("2021-01-01")
    points: List[DayPoint] = []

    for d in range(days):
        date = (start + pd.Timedelta(days=d)).strftime("%Y-%m-%d")
        required_skill = rng.choice(required_pool)
        mismatch = (required_skill != user["skill"])

        # Base hours around expected ± random noise
        hours = expected_hours + float(rng.normal(0.0, 0.8))

        # Occasionally underutilized (bench/low load)
        if rng.random() < 0.15:
            hours = max(0.5, expected_hours - float(rng.uniform(2.0, 4.0)))

        # If mismatch, user takes longer → overutilization risk
        if mismatch:
            hours += float(rng.uniform(1.5, 3.5))

        hours = float(np.clip(hours, 0.0, 12.0))

        # Anomaly classification
        if hours > expected_hours + anomaly_margin:
            anomaly = "over"
        elif hours < expected_hours - anomaly_margin:
            anomaly = "under"
        else:
            anomaly = "none"

        points.append(DayPoint(date, hours, expected_hours, mismatch, anomaly))

    return {
        "user": user["name"],
        "skill": user["skill"],
        "project": project,
        "points": points,
    }

# -------------------- UI (single-file: inline HTML/CSS/JS) --------------------
PAGE_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Retain • Anomaly Detection (Local Random)</title>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <style>
    :root{
      --bg:#fff;--text:#111827;--muted:#6b7280;--accent:#2563eb;--warn:#b91c1c;
      --card:#fff;--border:#e5e7eb;
    }
    *{box-sizing:border-box}
    body{margin:0;background:var(--bg);color:var(--text);font-family:Segoe UI,Roboto,Arial,sans-serif}
    .app-header{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--border);background:#fff;position:sticky;top:0;z-index:10}
    .controls{display:flex;gap:12px;align-items:flex-end;flex-wrap:wrap}
    .control-group{display:flex;flex-direction:column;gap:4px}
    .control-group label{font-size:12px;color:var(--muted)}
    select,button{padding:6px 8px;border:1px solid var(--border);border-radius:6px;background:#fff}
    button{background:var(--accent);color:#fff;border:none;cursor:pointer}
    button:hover{opacity:.9}
    .container{max-width:1100px;margin:16px auto;padding:0 16px}
    .kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}
    .kpi{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:12px}
    .kpi-label{font-size:12px;color:var(--muted)}
    .kpi-value{font-size:20px;margin-top:4px}
    .kpi .warn{color:var(--warn)}
    .card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px;margin-bottom:16px}
    .card h2{margin:0 0 8px 0;font-size:16px}
    .chart-wrap{width:100%;height:420px;display:flex;align-items:center;justify-content:center;background:#fff;border:1px solid var(--border);border-radius:8px}
    .chart-wrap img{max-width:100%;max-height:100%;object-fit:contain;background:#fff}
    .table{width:100%;border-collapse:collapse;font-size:14px}
    .table th,.table td{border-bottom:1px solid var(--border);padding:8px 6px}
    .table thead th{background:#f8fafc;text-align:left}
    .table tbody tr:nth-child(even){background:#f9fafb}
    .table tbody tr:hover td{background:#eef2ff}
    footer{padding:12px 16px;border-top:1px solid var(--border);background:#fff}
  </style>
</head>
<body>
<header class="app-header">
  <h1>Retain • Anomaly Detection (Local Random)</h1>
  <div class="controls">
    <div class="control-group">
      <label for="project">Project</label>
      <select id="project">
        {% for p in projects %}<option>{{p}}</option>{% endfor %}
      </select>
    </div>
    <div class="control-group">
      <label for="user">User</label>
      <select id="user">
        {% for u in users %}<option>{{u.name}}</option>{% endfor %}
        <option>ALL</option>
      </select>
    </div>
    <div class="control-group">
      <label for="display">Display</label>
      <select id="display">
        <option value="actual" selected>Actual only</option>
        <option value="baseline">Actual + Baseline</option>
      </select>
    </div>
    <button id="refresh">Refresh</button>
  </div>
</header>

<main class="container">
  <section class="kpis">
    <div class="kpi"><div class="kpi-label">Project</div><div class="kpi-value" id="kpiProject">—</div></div>
    <div class="kpi"><div class="kpi-label">User</div><div class="kpi-value" id="kpiUser">—</div></div>
    <div class="kpi"><div class="kpi-label">Anomalies</div><div class="kpi-value warn" id="kpiAnoms">—</div></div>
  </section>

  <section class="card">
    <h2>Daily Hours – Under/Over Utilization & Skill Mismatch</h2>
    <div class="chart-wrap">
      <img id="chart" alt="Anomaly chart (PNG)">
    </div>
  </section>

  <section class="card">
    <h2>Skill Mismatch & Utilization Alerts</h2>
    <table class="table" id="anomTable">
      <thead>
        <tr>
          <th>#</th><th>Date</th><th>User</th><th>Hours</th><th>Expected</th><th>Type</th><th>Skill Mismatch</th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </section>
</main>

<footer>
  <small>All data & plots generated locally in Python. No external browsing or CDNs.</small>
</footer>

<script>
  const $ = (id) => document.getElementById(id);

  async function loadData() {
    const project = $("project").value;
    const user = $("user").value;
    const res = await fetch(`/api/data?project=${encodeURIComponent(project)}&user=${encodeURIComponent(user)}`);
    if (!res.ok) throw new Error("Failed to fetch /api/data");
    return res.json();
  }

  function fillTable(items){
    const tbody = document.querySelector("#anomTable tbody");
    tbody.innerHTML = "";
    let i = 1;
    items.forEach(row => {
      row.anomalies.forEach((a, idx) => {
        if (a === "none" && !row.mismatch[idx]) return; // only alerts
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${i++}</td>
          <td>${row.timestamps[idx]}</td>
          <td>${row.user}</td>
          <td>${Number(row.values[idx]).toFixed(2)}</td>
          <td>${Number(row.expected[idx]).toFixed(2)}</td>
          <td>${a === "none" ? "-" : a}</td>
          <td>${row.mismatch[idx] ? "Yes" : "No"}</td>
        `;
        tbody.appendChild(tr);
      });
    });
  }

  async function refresh() {
    try{
      const data = await loadData();
      const project = $("project").value;
      const user = $("user").value;
      const showBaseline = $("display").value === "baseline";

      // KPIs
      $("kpiProject").textContent = project;
      $("kpiUser").textContent = user;
      const totalAnoms = (data.user === "ALL")
        ? data.series.reduce((acc, s) => acc + s.anomalies.filter(a => a !== "none").length, 0)
        : data.anomalies.filter(a => a !== "none").length;
      $("kpiAnoms").textContent = totalAnoms;

      // Chart: use server-side PNG with a cache-buster
      const ts = Date.now();
      const imgUrl = `/plot.png?project=${encodeURIComponent(project)}&user=${encodeURIComponent(user)}&baseline=${showBaseline ? "1" : "0"}&t=${ts}`;
      $("chart").src = imgUrl;

      // Table rows
      if (data.user === "ALL") {
        const rows = data.series.map(s => ({
          user: s.user,
          timestamps: data.timestamps,
          values: s.values,
          expected: s.expected,
          anomalies: s.anomalies,
          mismatch: s.mismatch
        }));
        fillTable(rows);
      } else {
        fillTable([{
          user: data.user,
          timestamps: data.timestamps,
          values: data.values,
          expected: data.expected,
          anomalies: data.anomalies,
          mismatch: data.mismatch
        }]);
      }
    }catch(e){
      console.error(e);
      alert("Failed to refresh. Check console.");
    }
  }

  $("refresh").addEventListener("click", refresh);
  // Initial load
  refresh();
</script>
</body>
</html>
"""

# -------------------- Flask routes --------------------
@app.route("/")
def index():
    return render_template_string(PAGE_HTML, projects=PROJECTS, users=USERS)

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/data")
def api_data():
    project = request.args.get("project", "IBSS")
    user_name = request.args.get("user", "User A")

    def build_payload(data: Dict):
        pts = data["points"]
        ts = [p.date for p in pts]
        vals = [p.hours for p in pts]
        exp = [p.expected for p in pts]
        anom = [p.anomaly for p in pts]
        mis = [p.mismatch for p in pts]
        # Compat keys for older front-ends (not strictly needed here)
        upper = [e + ANOMALY_MARGIN for e in exp]
        lower = [e - ANOMALY_MARGIN for e in exp]
        return ts, vals, exp, anom, mis, upper, lower

    if user_name == "ALL":
        series = []
        base_ts = None
        for u in USERS:
            data = generate_series(project, u)
            ts, vals, exp, anom, mis, up, lo = build_payload(data)
            if base_ts is None:
                base_ts = ts
            series.append({
                "user": data["user"],
                "skill": data["skill"],
                "values": vals,
                "expected": exp,
                "anomalies": anom,
                "mismatch": mis
            })
        return jsonify({"project": project, "user": "ALL", "timestamps": base_ts, "series": series})

    # Single user
    u = next((x for x in USERS if x["name"] == user_name), USERS[0])
    data = generate_series(project, u)
    ts, vals, exp, anom, mis, up, lo = build_payload(data)
    return jsonify({
        "project": project, "user": data["user"], "skill": data["skill"],
        "timestamps": ts, "values": vals, "expected": exp,
        "anomalies": anom, "mismatch": mis
    })

@app.route("/plot.png")
def plot_png():
    """
    Render a PNG chart on the server (no JS libs, no CDN).
    Query:
      - project=IBSS|Retain|WFM
      - user=User A|User B|User C|ALL
      - baseline=0|1  (show expected baseline)
    """
    project = request.args.get("project", "IBSS")
    user_name = request.args.get("user", "User A")
    show_baseline = request.args.get("baseline", "0") == "1"

    # Prepare data
    items = []
    timestamps = None
    if user_name == "ALL":
        for u in USERS:
            data = generate_series(project, u)
            pts = data["points"]
            ts = [p.date for p in pts]
            vals = [p.hours for p in pts]
            mis = [p.mismatch for p in pts]
            anom = [p.anomaly for p in pts]
            if timestamps is None:
                timestamps = ts
            items.append({"user": u["name"], "values": vals, "mismatch": mis, "anomalies": anom})
    else:
        u = next((x for x in USERS if x["name"] == user_name), USERS[0])
        data = generate_series(project, u)
        pts = data["points"]
        timestamps = [p.date for p in pts]
        items.append({
            "user": u["name"],
            "values": [p.hours for p in pts],
            "mismatch": [p.mismatch for p in pts],
            "anomalies": [p.anomaly for p in pts]
        })

    # Plot
    fig, ax = plt.subplots(figsize=(12, 4), dpi=120)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    # Baseline (same for all users)
    if show_baseline:
        ax.plot(timestamps, [EXPECTED_HOURS]*len(timestamps),
                color="#6b7280", linewidth=1.2, linestyle=(0, (6, 4)), label="baseline (6h)")

    # Lines & anomaly markers
    for item in items:
        user = item["user"]
        color = COLORS.get(user, "#374151")
        ax.plot(timestamps, item["values"], color=color, linewidth=1.6, label=f"{user} – hours")

        # Overlay anomalies
        xs_over, ys_over = [], []
        xs_under, ys_under = [], []
        xs_mis, ys_mis = [], []
        for i, a in enumerate(item["anomalies"]):
            x = timestamps[i]; y = item["values"][i]
            if a == "over": xs_over.append(x); ys_over.append(y)
            if a == "under": xs_under.append(x); ys_under.append(y)
            if item["mismatch"][i]: xs_mis.append(x); ys_mis.append(y)

        if xs_over:
            ax.scatter(xs_over, ys_over, s=28, c="#dc2626", zorder=5, label=f"{user} – over")
        if xs_under:
            ax.scatter(xs_under, ys_under, s=28, c="#7c3aed", zorder=5, label=f"{user} – under")
        if xs_mis:
            ax.scatter(xs_mis, ys_mis, s=45, c="#f59e0b", marker="^", zorder=6, label=f"{user} – mismatch")

    ax.set_title(f"{project} – Daily Hours", color="#111827", fontsize=12)
    ax.set_xlabel("Date", color="#374151")
    ax.set_ylabel("Hours", color="#374151")
    ax.grid(True, color="0.9", linestyle="-", linewidth=0.8, alpha=0.7)
    ax.set_ylim(0, 12)
    # Keep the legend minimal (no external toggles in chart)
    ax.legend(ncol=3, fontsize=8, frameon=False, loc="upper left")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)

    resp = make_response(buf.read())
    resp.headers["Content-Type"] = "image/png"
    # No cache so refresh button always updates
    resp.headers["Cache-Control"] = "no-store, max-age=0"
    return resp

@app.after_request
def add_no_cache(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

if __name__ == "__main__":
    print("Starting at http://127.0.0.1:5000  (Press Ctrl+C to stop)")
    app.run(host="127.0.0.1", port=5000, debug=True)
