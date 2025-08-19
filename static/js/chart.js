// static/js/chart.js
(function () {
  const defaultCurrency = window.CURRENCY || '';

  // Hàm vẽ Doughnut với % + tooltip currency
  function renderDoughnutWithPercents(canvasEl, labels, values, opts = {}) {
    const { legendPos = 'right', currency = defaultCurrency, backgroundColor } = opts;
    if (!(canvasEl && window.Chart)) return null;
    if (window.ChartDataLabels) Chart.register(ChartDataLabels);

    return new Chart(canvasEl, {
      type: 'doughnut',
      data: { labels, datasets: [{ data: values, backgroundColor: backgroundColor }] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: legendPos },
          datalabels: window.ChartDataLabels ? {
            formatter: (value, ctx) => {
              const total = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
              return total ? ((value / total) * 100).toFixed(1) + '%' : '0%';
            },
            color: '#fff',
            font: { weight: '700' },
            backgroundColor: 'rgba(0,0,0,0.5)',
            borderRadius: 4,
            padding: 4
          } : undefined,
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const val = ctx.parsed;
                const sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
                const pct = sum ? (val / sum) * 100 : 0;
                return `${ctx.label}: ${currency}${Number(val).toLocaleString()} (${pct.toFixed(1)}%)`;
              }
            }
          }
        }
      }
    });
  }

  // Hàm vẽ Bar chart
  function renderBarChart(canvasEl, labels, values, opts = {}) {
    const { label = 'Value', color = 'rgba(59,130,246,0.9)', currency = defaultCurrency } = opts;
    if (!(canvasEl && window.Chart)) return null;
    return new Chart(canvasEl, {
      type: 'bar',
      data: { labels, datasets: [{ label, data: values, backgroundColor: color, borderRadius: 6, maxBarThickness: 40 }] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { 
          x: { grid: { color: '#e5e7eb' }, ticks: { color: '#6b7280', font: { size: 11 } } },
          y: { grid: { color: '#e5e7eb' }, ticks: { color: '#6b7280', font: { size: 11 } }, beginAtZero: true }
        },
        plugins: { 
          legend: { display: false }, 
          tooltip: { callbacks: { label: (c) => `${label}: ${currency}${Number(c.parsed.y).toLocaleString()}` } } 
        }
      }
    });
  }

  // Hàm vẽ Line chart
  function renderLineChart(canvasEl, labels, datasets, opts = {}) {
    if (!(canvasEl && window.Chart)) return null;
    return new Chart(canvasEl, {
      type: 'line',
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { 
          x: { grid: { color: '#e5e7eb' }, ticks: { color: '#6b7280', font: { size: 11 } } },
          y: { grid: { color: '#e5e7eb' }, ticks: { color: '#6b7280', font: { size: 11 } }, beginAtZero: true }
        },
        plugins: { legend: { position: 'bottom' } }
      }
    });
  }

  // Expose ra global
  window.ChartHelpers = {
    renderDoughnutWithPercents,
    renderBarChart,
    renderLineChart
  };
})();
