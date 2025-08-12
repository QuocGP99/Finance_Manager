// static/js/base.js
(function () {
  window.CURRENCY = window.CURRENCY || '';

  window.renderDoughnutWithPercents = function (canvasEl, labels, values, opts = {}) {
    const { legendPos = 'right', currency = (window.CURRENCY || '') } = opts;
    if (!canvasEl) return null;
    const safeLabels = Array.isArray(labels) ? labels : [];
    const safeValues = Array.isArray(values) ? values : [];

    try {
      if (window.ChartDataLabels) { Chart.register(ChartDataLabels); }
      return new Chart(canvasEl, {
        type: 'doughnut',
        data: { labels: safeLabels, datasets: [{ data: safeValues }] },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: legendPos },
            datalabels: window.ChartDataLabels ? {
              formatter: (value, ctx) => {
                const data = ctx.chart.data.datasets[0].data || [];
                const total = data.reduce((a, b) => a + b, 0);
                const pct = total ? (value / total) * 100 : 0;
                return pct.toFixed(1) + '%';
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
                  const sum = (ctx.dataset.data || []).reduce((a, b) => a + b, 0);
                  const pct = sum ? (val / sum * 100) : 0;
                  return `${ctx.label}: ${currency}${Number(val).toLocaleString()} (${pct.toFixed(1)}%)`;
                }
              }
            }
          }
        }
      });
    } catch (e) {
      console.error('renderDoughnutWithPercents error:', e);
      return null;
    }
  };
})();
