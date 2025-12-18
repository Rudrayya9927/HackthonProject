
# Retain • Anomaly Detection (Mock)

This bundle uses **randomly generated data** (no CSV/Azure) to simulate:
- Skill mismatch (assigned required skill ≠ user skill)
- Over/Under utilization vs a 6h/day baseline

## How to run
```bash
pip install flask numpy pandas
python app.py
```
Then open: http://127.0.0.1:5000/

If the page loads but the chart is blank:
1) Hard refresh the browser (Ctrl+F5 or Cmd+Shift+R)
2) Open DevTools → Network → `/api/data` must return 200 JSON
3) If your network blocks CDNs, download Chart.js and serve locally:
   - Download `chart.umd.min.js` and place it at `static/js/chart.umd.min.js`
   - Replace the CDN tag in `templates/index.html` with:
     ```html
     <script src="{{ url_for('static', filename='js/chart.umd.min.js') }}"></script>
     ```

## Notes
- Projects: IBSS, Retain, WFM
- Users & skills: User A (Python), User B (SQL), User C (UI/UX)
- Baseline: 6h/day; anomalies when |actual-6| > 1.5h
- Use the top dropdowns (Project, User, Display) then **Refresh**.
