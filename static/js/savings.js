// static/js/savings.js
(function () {
  const cur = window.CURRENCY || '';
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // Format tiền
  const fmt = (v) => `${cur}${Number(v).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  // Tính số tháng còn lại (>=1)
  const monthsLeft = (dueStr) => {
    const today = new Date();
    const due = new Date(dueStr);
    const y = due.getFullYear() - today.getFullYear();
    const m = due.getMonth() - today.getMonth();
    const d = due.getDate() - today.getDate();
    let total = y * 12 + m + (d > 0 ? 1 : 0);
    return Math.max(1, total);
  };

  // Cập nhật 1 thẻ goal
function updateCard(card) {
  const currentEl = card.querySelector('.js-current');
  const pctEl = card.querySelector('.js-pct');
  const bar = card.querySelector('.sv-bar > span');
  const monthlyEl = card.querySelector('.js-monthly');
  const monthsEl = card.querySelector('.js-months');
  const dueEl = card.querySelector('.js-due');

  const target = Number(card.dataset.target || 0);
  let current = Number(String(currentEl.textContent).replace(/[, ]/g, '') || card.dataset.current || 0);

  const pct = target > 0 ? Math.min(100, (current / target) * 100) : 0;
  pctEl.textContent = (Math.round(pct * 10) / 10).toString();
  bar.style.width = `${pct}%`;

  const overdue = new Date(card.dataset.due) < new Date();
  dueEl.classList.toggle('overdue', overdue);

  const left = Math.max(target - current, 0);
  const mLeft = monthsLeft(card.dataset.due);

    // Nếu có override → dùng override; nếu không → công thức mặc định
  const override = Number(card.dataset.monthlyOverride || 0);
  let monthly = override > 0 ? override : (left / mLeft);

  // Nếu override > 0 và monthly > left → clamp bằng left (đạt trong 1 tháng)
  monthly = Math.min(monthly, left);

  // months hiển thị: nếu override > 0 → ceil(left / override), else = mLeft
  const monthsCalc = override > 0 && monthly > 0 ? Math.max(1, Math.ceil(left / override)) : Math.max(1, mLeft);

  monthlyEl.textContent = Number(monthly).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  monthsEl.textContent = monthsCalc;
  currentEl.textContent = Number(current).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return { current, target, monthly };
}

// SỬA: KPI tổng tính theo override nếu có
function recomputeMonthly() {
  let sum = 0;
  $$('.sv-card').forEach((card) => {
    const cur = Number(String(card.querySelector('.js-current').textContent).replace(/[, ]/g, ''));
    const target = Number(card.dataset.target || 0);
    const left = Math.max(target - cur, 0);
    const mLeft = monthsLeft(card.dataset.due);
    const override = Number(card.dataset.monthlyOverride || 0);
    const monthly = override > 0 ? Math.min(override, left) : (left / mLeft);
    sum += monthly;
  });
  setMonthlyKPI(sum);
}

  // Khởi tạo tất cả card + tính KPI “Monthly Commitment”
  function init() {
    let totalMonthly = 0;
    $$('.sv-card').forEach((card) => {
      const r = updateCard(card);

      // Quick add buttons
      $$('.sv-chip', card).forEach((btn) => {
        btn.addEventListener('click', () => {
          const add = Number(btn.dataset.add || 0);
          const curEl = card.querySelector('.js-current');
          const curNum = Number(String(curEl.textContent).replace(/[, ]/g, '')) + add;
          curEl.textContent = curNum.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
          const res = updateCard(card);
          recomputeMonthly(); // cập nhật KPI tổng
        });
      });

      totalMonthly += r.monthly;
    });
    setMonthlyKPI(totalMonthly);
  }

  function setMonthlyKPI(v) {
    const el = document.getElementById('kpiMonthly');
    if (el) el.textContent = fmt(v);
  }


  init();
})();
// === Modal create goal ===
(function setupCreateGoal() {
  const $ = (s, r=document) => r.querySelector(s);
  const modal = $('#goalModal');
  const openBtn = $('#newGoalBtn');
  const closeBtns = [$('.modal-close', modal), $('[data-close]', modal)];
  const form = $('#goalForm');

  // set default date = +6 months
  const dueInput = form.querySelector('input[name="due"]');
  if (dueInput && !dueInput.value) {
    const d = new Date(); d.setMonth(d.getMonth()+6);
    dueInput.value = d.toISOString().slice(0,10);
  }

  function open() { modal.classList.add('show'); modal.setAttribute('aria-hidden','false'); }
  function close(){ modal.classList.remove('show'); modal.setAttribute('aria-hidden','true'); }
  openBtn?.addEventListener('click', open);
  closeBtns.forEach(b=>b?.addEventListener('click', close));
  modal.addEventListener('click', (e)=>{ if(e.target===modal) close(); });

  form.addEventListener('submit', (e)=>{
    e.preventDefault();
    const fd = new FormData(form);
    const data = {
      name: (fd.get('title') || '').toString().trim(),
      desc: (fd.get('desc') || '').toString().trim(),
      target: Number(fd.get('target') || 0),
      current: Number(fd.get('current') || 0),
      priority: (fd.get('priority') || 'medium').toString(),
      category: (fd.get('category') || 'General').toString(),
      due: (fd.get('due') || '').toString(),
      monthly: Number(fd.get('monthly') || 0)
    };
    if (!data.name || !data.target || data.target <= 0) {
      alert('Please enter Goal Title and Target Amount > 0'); return;
    }

    // Tạo card theo cùng markup đang dùng
    const card = document.createElement('article');
    card.className = 'sv-card';
    card.dataset.name = data.name;
    card.dataset.current = String(data.current);
    card.dataset.target = String(data.target);
    card.dataset.due = data.due;
    card.dataset.priority = data.priority;
    card.innerHTML = `
      <header class="sv-card-hd">
        <div class="sv-card-title">
          <span class="material-icons sv-ic">savings</span>
          <div class="sv-card-txt">
            <strong>${data.name}</strong>
            <small class="muted">${data.desc ? data.desc : 'Saving for ' + data.name.toLowerCase()}</small>
          </div>
        </div>
        <div class="sv-tools">
          <span class="sv-badge ${data.priority}">${data.priority}</span>
          <button class="sv-icon" title="Edit"><span class="material-icons">edit</span></button>
          <button class="sv-icon" title="Duplicate"><span class="material-icons">content_copy</span></button>
          <button class="sv-icon" title="More"><span class="material-icons">more_vert</span></button>
        </div>
      </header>

      <div class="sv-amt">
        <div class="sv-amt-left">${cur}<span class="js-current">${Number(data.current).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}</span></div>
        <div class="sv-amt-right">/ ${cur}${Number(data.target).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}</div>
      </div>

      <div class="sv-bar"><span></span></div>
      <div class="sv-row">
        <div class="muted"><span class="js-pct">0</span>% complete</div>
        <div class="sv-due js-due">Due: ${data.due || '-'}</div>
      </div>

      <div class="sv-quick">
        <button class="sv-chip" data-add="25">+25</button>
        <button class="sv-chip" data-add="50">+50</button>
        <button class="sv-chip" data-add="100">+100</button>
      </div>

      <div class="sv-hint">
        <div class="sv-hint-title">
          <span class="material-icons">trending_up</span> Monthly contribution:
          <strong>${cur}<span class="js-monthly">${(data.monthly||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}</span></strong>
        </div>
        <div class="sv-hint-sub muted">
          At this rate, you'll reach your goal in <span class="js-months">–</span> months
        </div>
      </div>
    `;

    document.querySelector('.sv-grid')?.appendChild(card);

    // gắn handler + tính toán lại giống các card cũ
    // reuse các hàm đã có trong file (updateCard & recomputeMonthly)
    if (typeof updateCard === 'function') {
      updateCard(card);
    }
    // gán click cho quick add
    card.querySelectorAll('.sv-chip').forEach(btn=>{
      btn.addEventListener('click', ()=>{
        const add = Number(btn.dataset.add||0);
        const curEl = card.querySelector('.js-current');
        const curNum = Number(String(curEl.textContent).replace(/[, ]/g,'')) + add;
        curEl.textContent = curNum.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});
        if (typeof updateCard === 'function') updateCard(card);
        if (typeof recomputeMonthly === 'function') recomputeMonthly();
      });
    });

    if (typeof recomputeMonthly === 'function') recomputeMonthly();
    form.reset(); close();
  });
})();
// === Modal Edit Goal ===
(function setupEditGoal() {
  const $  = (s, r = document) => r.querySelector(s);
  const modal = $('#editModal');
  const title = $('#editTitle');
  const form  = $('#editForm');
  let editingCard = null;

  function open(card) {
    editingCard = card;
    const name = card.dataset.name || 'Goal';
    title.textContent = `Edit Goal - ${name}`;

    const cur = Number(String(card.querySelector('.js-current').textContent).replace(/[, ]/g, '')) || 0;
    const override = Number(card.dataset.monthlyOverride || 0);

    form.current.value = cur;
    form.monthly.value = override > 0 ? override : 0;

    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');
  }
  function close() {
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
    editingCard = null;
  }

  // Delegation: mọi click vào [data-edit] đều mở modal
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-edit]');
    if (!btn) return;
    const card = btn.closest('.sv-card');
    if (card) open(card);
  });

  modal.querySelector('.modal-close')?.addEventListener('click', close);
  modal.querySelector('[data-close]')?.addEventListener('click', close);
  modal.addEventListener('click', (e) => { if (e.target === modal) close(); });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!editingCard) return;

    const newCur     = Number(form.current.value || 0);
    const newMonthly = Number(form.monthly.value || 0);

    // cập nhật current
    const curEl = editingCard.querySelector('.js-current');
    curEl.textContent = newCur.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    // set/unset override
    if (newMonthly > 0) editingCard.dataset.monthlyOverride = String(newMonthly);
    else delete editingCard.dataset.monthlyOverride;

    updateCard(editingCard);
    recomputeMonthly();
    close();
  });
})();