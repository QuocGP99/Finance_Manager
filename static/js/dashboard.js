// static/js/dashboard.js
(function () {
  const cur = window.CURRENCY || '';
  const $ = (id) => document.getElementById(id);

  if (window.ChartHelpers && $('barChart')) {
    const labels = Array.isArray(days) ? days : [];
    const values = Array.isArray(dayValues) ? dayValues : [];
    ChartHelpers.renderBarChart($('barChart'), labels, values, { label: 'Spending', currency: cur });
  }

  if (window.ChartHelpers && $('pieChart')) {
    const labels = Array.isArray(catLabels) ? catLabels : [];
    const values = Array.isArray(catValues) ? catValues : [];
    ChartHelpers.renderDoughnutWithPercents($('pieChart'), labels, values, { legendPos: 'right', currency: cur });
  }
})();

/* ==== Sort for "Recent Transactions" (toggle low/high) ==== */
(function () {
  const btn  = document.getElementById('sortRecentBtn');
  const list = document.getElementById('recentList');
  if (!btn || !list) return;

  let asc = true; // click đầu: Low → High

  const parseMoney = (txt) => {
    // bỏ ký tự tiền tệ, khoảng trắng, dấu chấm ngăn nghìn; giữ dấu âm/dương
    const s = (txt || '').replace(/[^\d+\-.,]/g, '').replace(/\./g, '').replace(',', '.');
    const n = parseFloat(s);
    return isNaN(n) ? 0 : n;
  };

  const getAmt = (row) => parseMoney(row.querySelector('.amt')?.textContent || '0');

  btn.addEventListener('click', () => {
    const items = Array.from(list.querySelectorAll('.titem'));
    items.sort((a, b) => asc ? getAmt(a) - getAmt(b) : getAmt(b) - getAmt(a));
    items.forEach(el => list.appendChild(el));
    btn.querySelector('.material-icons').textContent = asc ? 'south' : 'north';
    asc = !asc;
  });
})();
