
// static/js/app.js
(async function () {
  const refreshBtn = document.getElementById("refreshBtn");
  const kpiTotal = document.getElementById("kpiTotal");
  const kpiAnoms = document.getElementById("kpiAnoms");
  const kpiThresh = document.getElementById("kpiThresh");

  const ctx = document.getElementById("tsChart").getContext("2d");
  let chart;

  async function loadData() {
    const res = await fetch("/api/data");
    if (!res.ok) throw new Error("Failed to fetch /api/data");
    return res.json();
  }

  function buildChart(data) {
    const { timestamps, values, anomaly_indices, mean, upper, lower } = data;

    // Build anomalies dataset (sparse points)
    const anomalyPoints = anomaly_indices.map(i => ({ x: timestamps[i], y: values[i] }));

    // Destroy previous chart if any
    if (chart) chart.destroy();

    chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: timestamps,
        datasets: [
          {
            label: "series_0",
            data: values,
            borderColor: "#3b82f6",
            backgroundColor: "rgba(59,130,246,0.15)",
            tension: 0.2,
            pointRadius: 0
          },
          {
            label: "rolling mean",
            data: mean,
            borderColor: "#22c55e",
            borderWidth: 1.2,
            pointRadius: 0
          },
          {
            label: "upper band",
            data: upper,
            borderColor: "rgba(34,197,94,0.0)",
            backgroundColor: "rgba(34,197,94,0.12)",
            fill: "+1",
            pointRadius: 0
          },
          {
            label: "lower band",
            data: lower,
            borderColor: "rgba(34,197,94,0.0)",
            pointRadius: 0
          },
          {
            label: "anomalies",
            type: "scatter",
            data: anomalyPoints,
            pointBackgroundColor: "#ef4444",
            pointBorderColor: "#ef4444",
            pointRadius: 3.5,
            showLine: false
          }
        ]
      },
      options: {
        interaction: { mode: "nearest", intersect: false },
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: "#cbd5e1", maxTicksLimit: 12 } },
          y: { ticks: { color: "#cbd5e1" }, grid: { color: "rgba(255,255,255,0.06)" } }
        },
        plugins: {
          legend: { labels: { color: "#e5e7eb" } },
          tooltip: {
            callbacks: {
              label: ctx => `${ctx.dataset.label}: ${Number(ctx.parsed.y).toFixed(3)}`
            }
          }
        }
      }
    });
  }

  function fillTable(data) {
    const { timestamps, values, anomaly_indices } = data;
    const tbody = document.querySelector("#anomTable tbody");
    tbody.innerHTML = "";

    anomaly_indices.forEach((idx, i) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${i + 1}</td>
        <td>${timestamps[idx]}</td>
        <td>${Number(values[idx]).toFixed(6)}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  async function refresh() {
    const data = await loadData();
    kpiTotal.textContent = data.values.length;
    kpiAnoms.textContent = data.anomaly_indices.length;
    buildChart(data);
    fillTable(data);
  }

  refreshBtn.addEventListener("click", refresh);

  // Initial load
  refresh();
})();
