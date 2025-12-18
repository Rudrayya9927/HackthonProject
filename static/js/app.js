
(function(){
  const userSelect = document.getElementById('userSelect');
  const displaySelect = document.getElementById('displaySelect');
  const zInput = document.getElementById('zInput');
  const winInput = document.getElementById('winInput');
  const refreshBtn = document.getElementById('refreshBtn');
  const kpiTotal = document.getElementById('kpiTotal');
  const kpiAnoms = document.getElementById('kpiAnoms');
  const kpiUser = document.getElementById('kpiUser');

  const ctx = document.getElementById('tsChart').getContext('2d');
  let chart = null;

  // Unique colors per user
  const COLORS = {
    'User A': '#2563eb', // blue
    'User B': '#ea580c', // orange
    'User C': '#16a34a'  // green
  };
  const BAND_COLOR = 'rgba(107,114,128,0.18)'; // light gray band

  async function loadData(){
    const user = userSelect.value;
    const z = zInput.value || '3.0';
    const win = winInput.value || '30';
    const includeBand = (displaySelect.value !== 'series') ? '1' : '0';
    const res = await fetch(`/api/data?user=${encodeURIComponent(user)}&z=${encodeURIComponent(z)}&win=${encodeURIComponent(win)}&band=${includeBand}`);
    if(!res.ok) throw new Error('Failed to fetch /api/data');
    return res.json();
  }

  function buildSingleChart(data){
    const { timestamps, values, anomaly_indices, mean, upper, lower, user } = data;
    const color = COLORS[user] || '#374151';

    const datasets = [
      {
        label: `${user} – series_0`,
        data: values,
        borderColor: color,
        backgroundColor: 'rgba(0,0,0,0)',
        tension: 0.25,
        pointRadius: 0
      }
    ];

    if(displaySelect.value === 'mean' || displaySelect.value === 'band'){
      datasets.push({
        label: 'rolling mean',
        data: mean,
        borderColor: '#111827',
        borderWidth: 1.2,
        pointRadius: 0
      });
    }
    if(displaySelect.value === 'band'){
      datasets.push({
        label: 'threshold band (upper)',
        data: upper,
        borderColor: 'rgba(0,0,0,0)',
        backgroundColor: BAND_COLOR,
        fill: '+1',
        pointRadius: 0
      });
      datasets.push({
        label: 'threshold band (lower)',
        data: lower,
        borderColor: 'rgba(0,0,0,0)',
        pointRadius: 0
      });
    }

    // Anomaly points
    const anomalyPoints = anomaly_indices.map(i => ({ x: timestamps[i], y: values[i] }));
    datasets.push({
      label: 'anomalies',
      type: 'scatter',
      data: anomalyPoints,
      pointBackgroundColor: '#b91c1c',
      pointBorderColor: '#b91c1c',
      pointRadius: 3.5,
      showLine: false
    });

    renderChart(timestamps, datasets);

    // KPIs
    kpiTotal.textContent = values.length;
    kpiAnoms.textContent = anomaly_indices.length;
    kpiUser.textContent = user;
    fillTable([{user, timestamps, values, anomaly_indices}]);
  }

  function buildAllChart(data){
    const { timestamps, series } = data;
    const datasets = [];
    const tableData = [];

    series.forEach(item => {
      const color = COLORS[item.user] || '#374151';
      datasets.push({
        label: `${item.user} – series_0`,
        data: item.values,
        borderColor: color,
        backgroundColor: 'rgba(0,0,0,0)',
        tension: 0.25,
        pointRadius: 0
      });
      if(displaySelect.value === 'mean' || displaySelect.value === 'band'){
        datasets.push({
          label: `${item.user} – mean`,
          data: item.mean,
          borderColor: '#111827',
          borderWidth: 1.0,
          pointRadius: 0
        });
      }
      if(displaySelect.value === 'band'){
        datasets.push({
          label: `${item.user} – upper`,
          data: item.upper,
          borderColor: 'rgba(0,0,0,0)',
          backgroundColor: BAND_COLOR,
          fill: '+1',
          pointRadius: 0
        });
        datasets.push({
          label: `${item.user} – lower`,
          data: item.lower,
          borderColor: 'rgba(0,0,0,0)',
          pointRadius: 0
        });
      }
      const points = item.anomaly_indices.map(i => ({ x: timestamps[i], y: item.values[i] }));
      datasets.push({
        label: `${item.user} – anomalies`,
        type: 'scatter',
        data: points,
        pointBackgroundColor: '#b91c1c',
        pointBorderColor: '#b91c1c',
        pointRadius: 3.5,
        showLine: false
      });
      tableData.push({user: item.user, timestamps, values: item.values, anomaly_indices: item.anomaly_indices});
    });

    renderChart(timestamps, datasets);
    const allLen = Math.max(...series.map(s => s.values.length));
    const allAnoms = series.reduce((acc, s) => acc + (s.anomaly_indices?.length || 0), 0);
    kpiTotal.textContent = allLen;
    kpiAnoms.textContent = allAnoms;
    kpiUser.textContent = 'ALL';
    fillTable(tableData);
  }

  function renderChart(labels, datasets){
    if(chart) chart.destroy();
    chart = new Chart(ctx, {
      type: 'line',
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 16/6,
        animation: false,
        scales: {
          x: {
            ticks: { color: '#374151', maxTicksLimit: 10 },
            grid: { color: 'rgba(0,0,0,0.05)' }
          },
          y: {
            ticks: { color: '#374151' },
            grid: { color: 'rgba(0,0,0,0.05)' }
          }
        },
        plugins: {
          legend: { labels: { color: '#111827' } },
          tooltip: {
            callbacks: { label: ctx => `${ctx.dataset.label}: ${Number(ctx.parsed.y).toFixed(3)}` }
          }
        }
      }
    });
  }

  function fillTable(items){
    const tbody = document.querySelector('#anomTable tbody');
    tbody.innerHTML = '';
    let counter = 1;
    items.forEach(item => {
      item.anomaly_indices.forEach(idx => {
        const tr = document.createElement('tr');
        const value = Number(item.values[idx]).toFixed(6);
        tr.innerHTML = `
          <td>${counter++}</td>
          <td>${item.user}</td>
          <td>${item.timestamps[idx]}</td>
          <td>${value}</td>
        `;
        tbody.appendChild(tr);
      });
    });
  }

  async function refresh(){
    try {
      const data = await loadData();
      if(data.user === 'ALL') buildAllChart(data); else buildSingleChart(data);
    } catch(err){ console.error(err); }
  }

  // Initial load and manual refresh only
  refresh();
  refreshBtn.addEventListener('click', refresh);
})();
