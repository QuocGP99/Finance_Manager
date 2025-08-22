// static/js/savings.js
(function () {
  const cur = window.CURRENCY || '₫';
  const $  = (s, r=document)=>r.querySelector(s);
  const $$ = (s, r=document)=>Array.from(r.querySelectorAll(s));
  const N  = x => Number(x || 0);
  const fmt = n => `${cur}${Number(n||0).toLocaleString('vi-VN',{maximumFractionDigits:2})}`;

  // KPI refs
  const elSavedVal   = document.querySelector('.sv-kpi.k-green .sv-kpi-value');
  const elSavedSub   = document.querySelector('.sv-kpi.k-green .sv-kpi-sub');
  const elTargetVal  = document.querySelector('.sv-kpi.k-blue  .sv-kpi-value');
  const elTargetSub  = document.querySelector('.sv-kpi.k-blue  .sv-kpi-sub');
  const elMonthlyVal = document.querySelector('.sv-kpi.k-purple .sv-kpi-value');

  // Grid + modals
  const grid      = $('.sv-grid');
  const newBtn    = $('#newGoalBtn');
  const addModal  = $('#goalModal');
  const addForm   = $('#goalForm');
  const editModal = $('#editModal');
  const editForm  = $('#editForm');

  const openModal  = m => { m.classList.add('show'); m.setAttribute('aria-hidden','false'); };
  const closeModal = m => { m.classList.remove('show'); m.setAttribute('aria-hidden','true'); };

  const clampPct = (c,t)=> t>0 ? Math.min(100, Math.max(0, c/t*100)) : 0;
  const monthsToGoal = (c,t,m)=>{
    if (m<=0) return '–';
    const remain = Math.max(t - c, 0);
    const mo = Math.ceil(remain / m);
    return (isFinite(mo) && mo>=0) ? String(mo) : '–';
  };

  // ---- KPI ----
  function recalcMonthly(){
    let total = 0;
    $$('.sv-card', grid).forEach(c => total += N(c.dataset.monthly));
    if (elMonthlyVal) elMonthlyVal.textContent = fmt(total);
  }
  function recalcTotals(){
    let cur = 0, tar = 0;
    const cards = $$('.sv-card', grid);
    cards.forEach(c => { cur += N(c.dataset.current); tar += N(c.dataset.target); });
    if (elSavedVal)  elSavedVal.textContent  = fmt(cur);
    if (elTargetVal) elTargetVal.textContent = fmt(tar);
    const pct = tar>0 ? (cur/tar*100) : 0;
    if (elSavedSub)  elSavedSub.textContent  = `${pct.toFixed(1)}% of total goals`;
    if (elTargetSub) elTargetSub.textContent = `${cards.length} active goals`;
  }
  const recalcAll = ()=>{ recalcTotals(); recalcMonthly(); };

  // ---- Card UI ----
  function setCardUI(card, {current, target, monthly, due, priority}){
    if (current != null) card.dataset.current = current;
    if (target  != null) card.dataset.target  = target;
    if (monthly != null) card.dataset.monthly = monthly;
    if (due     != null) card.dataset.due     = due;
    if (priority)        card.dataset.priority= priority;

    const c = N(card.dataset.current), t = N(card.dataset.target), m = N(card.dataset.monthly||0);
    const pct = clampPct(c,t);

    const curEl = card.querySelector('.js-current');
    const pctEl = card.querySelector('.js-pct');
    const barEl = card.querySelector('.sv-bar span');
    const dueEl = card.querySelector('.js-due');
    const monEl = card.querySelector('.js-monthly');
    const monTx = card.querySelector('.sv-hint-sub .js-months');
    const badge = card.querySelector('.sv-badge');

    if (curEl) curEl.textContent = c.toLocaleString('vi-VN',{maximumFractionDigits:2});
    if (pctEl) pctEl.textContent = pct.toFixed(1);
    if (barEl) barEl.style.width = pct+'%';
    if (dueEl) dueEl.textContent = 'Due: ' + (card.dataset.due || '');
    if (monEl) monEl.textContent = m.toLocaleString('vi-VN',{maximumFractionDigits:2});
    if (monTx) monTx.textContent = monthsToGoal(c,t,m);
    if (badge && priority){ badge.textContent = priority; badge.className = 'sv-badge ' + priority; }
  }

  function bindCard(card){
    // Quick add +25/+50/+100
    card.querySelectorAll('.sv-chip').forEach(btn=>{
      btn.addEventListener('click', ()=>{
        const inc = N(btn.dataset.add);
        setCardUI(card, { current: N(card.dataset.current) + inc });
        recalcAll();
        toast('Added ' + fmt(inc));
      });
    });

    // Edit
    card.querySelector('[data-edit]')?.addEventListener('click', ()=>{
      editForm.current.value = card.dataset.current || 0;
      editForm.monthly.value = card.dataset.monthly || 0;
      openModal(editModal);

      const handler = (e)=>{
        e.preventDefault();
        setCardUI(card, {
          current: N(editForm.current.value),
          monthly: N(editForm.monthly.value)
        });
        recalcAll();
        closeModal(editModal);              // <-- tự đóng modal sau cập nhật
        toast('Goal updated');
        editForm.removeEventListener('submit', handler);
      };
      editForm.addEventListener('submit', handler, { once:true });
    });

    // Delete (ưu tiên nút data-delete; nếu không có, dùng nút cuối trong .sv-tools)
    const delBtn = card.querySelector('[data-delete]') || card.querySelector('.sv-tools .sv-icon:last-of-type');
    delBtn?.addEventListener('click', ()=>{
      const title = card.dataset.name || card.querySelector('.sv-card-txt strong')?.textContent || 'this goal';
      const c = N(card.dataset.current), t = N(card.dataset.target);
      const ok = confirm(`Delete "${title}"?\nCurrent/Target: ${fmt(c)} / ${fmt(t)}`);
      if (!ok) return;
      card.remove();
      recalcAll();
      toast('Deleted successfully');
    });
  }

  // ---- Build card (dùng khi tạo mới) ----
  function buildCard(data){
    const pct = clampPct(data.current, data.target);
    const art = document.createElement('article');
    art.className = 'sv-card';
    art.dataset.name     = data.title;
    art.dataset.current  = data.current;
    art.dataset.target   = data.target;
    art.dataset.due      = data.due || '';
    art.dataset.priority = data.priority || 'medium';
    art.dataset.monthly  = data.monthly || 0;

    art.innerHTML = `
      <header class="sv-card-hd">
        <div class="sv-card-title">
          <span class="material-icons sv-ic">savings</span>
          <div class="sv-card-txt">
            <strong>${esc(data.title)}</strong>
            <small class="muted">${esc('Saving for ' + (data.title||'').toLowerCase())}</small>
          </div>
        </div>
        <div class="sv-tools">
          <span class="sv-badge ${data.priority}">${esc(data.priority)}</span>
          <button class="sv-icon" title="Edit" data-edit><span class="material-icons">edit</span></button>
          <button class="sv-icon" title="Delete" data-delete><span class="material-icons">delete</span></button>
        </div>
      </header>

      <div class="sv-amt">
        <div class="sv-amt-left">${cur}<span class="js-current">${Number(data.current).toLocaleString('vi-VN',{maximumFractionDigits:2})}</span></div>
        <div class="sv-amt-right">/ ${cur}${Number(data.target).toLocaleString('vi-VN',{maximumFractionDigits:2})}</div>
      </div>

      <div class="sv-bar"><span style="width:${pct}%"></span></div>
      <div class="sv-row">
        <div class="muted"><span class="js-pct">${pct.toFixed(1)}</span>% complete</div>
        <div class="sv-due js-due">Due: ${esc(data.due || '')}</div>
      </div>

      <div class="sv-quick">
        <button class="sv-chip" data-add="25">+25</button>
        <button class="sv-chip" data-add="50">+50</button>
        <button class="sv-chip" data-add="100">+100</button>
      </div>

      <div class="sv-hint">
        <div class="sv-hint-title">
          <span class="material-icons">trending_up</span> Monthly contribution:
          <strong>${cur}<span class="js-monthly">${Number(data.monthly||0).toLocaleString('vi-VN',{maximumFractionDigits:2})}</span></strong>
        </div>
        <div class="sv-hint-sub muted">
          At this rate, you'll reach your goal in <span class="js-months">${monthsToGoal(data.current, data.target, data.monthly)}</span> months
        </div>
      </div>
    `;
    bindCard(art);
    return art;
  }

  // ---- Add Goal ----
  newBtn?.addEventListener('click', ()=>{
    const d = new Date(); d.setMonth(d.getMonth()+6);
    addForm.due.value = d.toISOString().slice(0,10);
    openModal(addModal);
  });

  addForm?.addEventListener('submit', (e)=>{
    e.preventDefault();
    const fd = new FormData(addForm);
    const title    = (fd.get('title')||'').toString().trim();
    const current  = N(fd.get('current'));
    const target   = N(fd.get('target'));
    const priority = (fd.get('priority')||'medium').toString();
    const due      = (fd.get('due')||'').toString();
    const monthly  = N(fd.get('monthly'));
    if (!title || !(target>0)) { alert('Please enter Goal Title and Target > 0'); return; }

    const card = buildCard({ title, current, target, priority, due, monthly });
    grid.prepend(card);
    recalcAll();

    closeModal(addModal);   // <-- tự đóng modal sau khi thêm
    addForm.reset();
    toast('Goal added');
  });

  // ---- Modal close wiring ----
  addModal?.querySelector('.modal-close')?.addEventListener('click', ()=> closeModal(addModal));
  addModal?.querySelector('[data-close]')?.addEventListener('click', ()=> closeModal(addModal));
  addModal?.addEventListener('click', e=>{ if(e.target===addModal) closeModal(addModal); });

  editModal?.querySelector('.modal-close')?.addEventListener('click', ()=> closeModal(editModal));
  editModal?.querySelector('[data-close]')?.addEventListener('click', ()=> closeModal(editModal));
  editModal?.addEventListener('click', e=>{ if(e.target===editModal) closeModal(editModal); });

  // ---- Init ----
  $$('.sv-card', grid).forEach(card=>{
    if (!('monthly' in card.dataset)) card.dataset.monthly = '0';
    bindCard(card);
    setCardUI(card, {}); // đồng bộ UI
  });
  recalcAll();

  // ---- Helpers ----
  function toast(msg){
    const d = document.createElement('div');
    d.textContent = msg;
    d.style.cssText='position:fixed;right:16px;bottom:16px;background:#111827;color:#fff;padding:10px 14px;border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.2);z-index:9999';
    document.body.appendChild(d);
    setTimeout(()=>d.remove(), 1600);
  }
  function esc(s){ return String(s||'').replace(/[&<>"']/g, m=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[m])); }
})();
