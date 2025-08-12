// static/js/dashboard.js
(function () {
  // days, dayValues, catLabels, catValues, window.CURRENCY được inject từ dashboard.html
  const cur = window.CURRENCY || '';
  const $ = (id) => document.getElementById(id);

  // Bar: Spending theo ngày/tháng
  if (window.ChartHelpers && $('barChart')) {
    const labels = Array.isArray(days) ? days : [];
    const values = Array.isArray(dayValues) ? dayValues : [];
    ChartHelpers.renderBarChart($('barChart'), labels, values, {
      label: 'Spending',
      currency: cur
    });
  }

  // Pie: Category Breakdown
  if (window.ChartHelpers && $('pieChart')) {
    const labels = Array.isArray(catLabels) ? catLabels : [];
    const values = Array.isArray(catValues) ? catValues : [];
    ChartHelpers.renderDoughnutWithPercents($('pieChart'), labels, values, {
      legendPos: 'right',
      currency: cur
    });
  }
})();
