// static/js/analytics.js
(function () {
  // months, income, spending, catLabels, catValues, window.CURRENCY được inject từ analytics.html
  const cur = window.CURRENCY || '';
  const $ = (id) => document.getElementById(id);
  const fmt = (v) => `${cur}${(+v).toLocaleString()}`;

  const M = Array.isArray(months) ? months : [];
  const I = Array.isArray(income) ? income : [];
  const S = Array.isArray(spending) ? spending : [];
  const CL = Array.isArray(catLabels) ? catLabels : [];
  const CV = Array.isArray(catValues) ? catValues : [];
  const CC = Array.isArray(catColors) ? catColors : [];

  // Dropdown (UI only, null-safe)
  (function initPeriodDropdown() {
    const btn = $('periodToggle'), menu = $('periodMenu'), label = $('periodLabel');
    if (!(btn && menu && label)) return;
    btn.addEventListener('click', () => menu.style.display = menu.style.display === 'block' ? 'none' : 'block');
    document.addEventListener('click', (e) => { if (!btn.contains(e.target) && !menu.contains(e.target)) menu.style.display = 'none'; });
    menu.querySelectorAll('li').forEach(li => li.addEventListener('click', () => {
      menu.querySelectorAll('li').forEach(x => x.classList.remove('active'));
      li.classList.add('active'); label.textContent = li.textContent; menu.style.display = 'none';
      // TODO: fetch dữ liệu theo range
    }));
  })();

  if (!window.ChartHelpers) return;

  // 1) Spending vs Budget (bar)
  (function drawSpendingVsBudget() {
    const el = $('chartSpendingVsBudget'); if (!el) return;
    const maxSpend = S.length ? Math.max(...S) : 0;
    const budget = M.map(() => Math.round(maxSpend * 1.15));
    ChartHelpers.renderBarChart(el, M, S, {
      label: 'Spending',
      currency: cur
    });
    // Gợi ý: nếu muốn hiển thị thêm dataset Budget, dùng Chart.js trực tiếp:
    // const chart = ChartHelpers.renderBarChart(...); rồi chart.data.datasets.push({label:'Budget', data:budget, ...}); chart.update();
  })();

  // 2) Pie breakdown (doughnut)
  (function drawPieBreakdown() {
    const el = $('pieChart'); if (!el) return;
    ChartHelpers.renderDoughnutWithPercents(el, CL, CV, { legendPos: 'right', currency: cur, backgroundColor: CC });
  })();

  // 3) Category Trends (line) – tạo dataset giả lập từ tổng từng category
  (function drawCategoryTrends() {
    const el = $('chartCategoryTrends'); if (!el) return;
    const baseMultipliers = [0.9, 1.0, 0.85, 1.2, 1.05];
    const datasets = CL.map((name, idx) => {
      const total = CV[idx] || 0;
      const avg = total / Math.max(baseMultipliers.length, 1);
      const data = baseMultipliers.map((x, i) => Math.round(avg * x * (0.95 + 0.05 * ((i + idx) % 2))));
      return {
        label: name,
        data,
        tension: 0.35,
        fill: false,
        borderColor: CC[idx] || '#bab0ab',
        backgroundColor: CC[idx] || '#bab0ab'
      };
    });
    ChartHelpers.renderLineChart(el, M, datasets);
  })();

  // 4) Savings (area)
  (function drawSavingsArea() {
    const el = $('chartSavingsArea'); if (!el) return;
    const savings = M.map((_, i) => Math.max((I[i] || 0) - (S[i] || 0), 0));
    // Dùng Chart.js trực tiếp để fill area
    new Chart(el, {
      type: 'line',
      data: { labels: M, datasets: [{ label: 'Savings', data: savings, fill: true, tension: 0.35 }] },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: {
          x: { grid: { color: '#e5e7eb' }, ticks: { color: '#6b7280', font: { size: 11 } } },
          y: { grid: { color: '#e5e7eb' }, ticks: { color: '#6b7280', font: { size: 11 } }, beginAtZero: true }
        },
        plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => fmt(c.parsed.y) } } }
      }
    });
  })();

  // 5) Weekly (bar) – phân bổ từ tháng gần nhất
  (function drawWeeklyBars() {
    const el = $('chartWeeklyBars'); if (!el) return;
    const last = S[S.length - 1] || 0;
    const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
    const values = [0.26, 0.28, 0.22, 0.24].map(p => Math.round(last * p));
    ChartHelpers.renderBarChart(el, labels, values, { label: 'Spending', currency: cur });
  })();
})();
