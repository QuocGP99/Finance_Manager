// static/js/expenses.js
(function () {
  const cur = window.CURRENCY || "₫";
  const $  = (s, r=document)=>r.querySelector(s);
  const $$ = (s, r=document)=>Array.from(r.querySelectorAll(s));
  const fmt0 = n => `${cur}${Number(n).toLocaleString('vi-VN', { maximumFractionDigits: 0 })}`;

  // ========== JSON toast ==========
  function toastJSON(obj){
    let el = $('.exp-toast');
    if (!el){
      el = document.createElement('div');
      el.className = 'exp-toast';
      document.body.appendChild(el);
    }
    el.textContent = JSON.stringify(obj, null, 2);
    el.classList.add('show');
    setTimeout(()=> el.classList.remove('show'), 2200);
  }

  // ========== KPI ==========
  const kpiSpentEl = $('#kpiTotalSpent') || document.querySelector('.exp-kpi.blue .value');
  const kpiCntEl   = $('#kpiTxCount')    || document.querySelector('.exp-kpi.purple .value');
  const kpiAvgEl   = $('#kpiAvgTx')      || document.querySelector('.exp-kpi.orange .value');

  function readVisible(){
    const rows = $$('.exp-row').filter(r => getComputedStyle(r).display !== 'none');
    let total = 0, count = 0;
    rows.forEach(r=>{
      const v = Number(r.dataset.amount || r.querySelector('[data-amount]')?.dataset.amount || 0);
      total += v; count += 1;
    });
    return { total, count, avg: count ? total / count : 0 };
  }
  function renderKPIs(){
    const { total, count, avg } = readVisible();
    if (kpiSpentEl) kpiSpentEl.textContent = fmt0(total);
    if (kpiCntEl)   kpiCntEl.textContent   = String(count);
    if (kpiAvgEl)   kpiAvgEl.textContent   = fmt0(avg);
  }

  // ========== Helpers ==========
  const colorOf = (cat='')=>{
    const c = cat.toLowerCase();
    if (c.includes('ăn uống') || c.includes('food')) return 'orange';
    if (c.includes('di chuyển') || c.includes('transport')) return 'blue';
    if (c.includes('giải trí') || c.includes('entertain')) return 'purple';
    if (c.includes('mua sắm') || c.includes('shop')) return 'green';
    if (c.includes('hóa đơn') || c.includes('bills') || c.includes('util')) return 'red';
    return 'yellow';
  };
  const escapeHtml = s => String(s||'').replace(/[&<>"']/g, m=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[m]));

  // ========== Build/bind row ==========
  let uid = Date.now();
  function buildRow(data){
    const item = document.createElement('div');
    item.className = 'titem exp-row';
    Object.assign(item.dataset, {
      id: data.id || `c${uid++}`,
      desc: data.desc,
      category: data.category,
      date: data.date,
      method: data.method,
      amount: String(data.amount)
    });

    const badgeColor = colorOf(data.category);
    item.innerHTML = `
      <div class="ico"><span class="material-icons">shopping_bag</span></div>
      <div style="flex:1">
        <div class="name">${escapeHtml(data.desc)}</div>
        <div class="sub">
          ${escapeHtml(data.date)} &nbsp;|&nbsp; ${escapeHtml(data.method)}
          <span class="badge ${badgeColor}">${escapeHtml(data.category)}</span>
        </div>
      </div>
      <div class="amt neg" data-amount="${data.amount}">${fmt0(data.amount)}</div>
      <div style="display:flex; gap:6px; margin-left:8px;">
        <button class="btn icon" title="Edit" data-edit><span class="material-icons">edit</span></button>
        <button class="btn icon" title="Delete" data-delete><span class="material-icons">delete</span></button>
      </div>
    `;
    bindRow(item);
    return item;
  }

  function bindRow(row){
    // EDIT
    row.querySelector('[data-edit]')?.addEventListener('click', ()=>{
      openEdit(row);
    });
    // DELETE
    row.querySelector('[data-delete]')?.addEventListener('click', ()=>{
      if (!confirm('Delete this expense?')) return;
      const payload = {
        action: 'delete',
        id: row.dataset.id,
        desc: row.dataset.desc,
        amount: Number(row.dataset.amount || 0),
        category: row.dataset.category
      };
      row.remove();
      renderKPIs();
      toastJSON(payload);
    });
  }

  // Bind các rows render từ server
  $$('.exp-row').forEach(bindRow);

  // ========== Modal ADD ==========
  const addModal = $('#expModal');
  const addForm  = $('#expForm');

  function openAdd(){
    if (addForm?.date && !addForm.date.value){
      addForm.date.value = new Date().toISOString().slice(0,10);
    }
    addModal.classList.add('show');
    addModal.setAttribute('aria-hidden','false');
  }
  function closeAdd(){
    addModal.classList.remove('show');
    addModal.setAttribute('aria-hidden','true');
    addForm?.reset();
  }
  $('#addExpenseBtn')?.addEventListener('click', openAdd);
  addModal?.querySelector('.modal-close')?.addEventListener('click', closeAdd);
  addModal?.querySelector('[data-close]')?.addEventListener('click', closeAdd);
  addModal?.addEventListener('click', (e)=>{ if(e.target===addModal) closeAdd(); });

   // Mở modal Add Expense nếu có ?action=add
  const params = new URLSearchParams(window.location.search);
  if (params.get('action') === 'add') {
    document.getElementById('addExpenseBtn')?.click();
  }

  addForm?.addEventListener('submit', (e)=>{
    e.preventDefault();
    const fd = new FormData(addForm);
    const data = {
      id: `c${uid++}`,
      desc: (fd.get('desc')||'').toString().trim(),
      amount: Number(fd.get('amount')||0),
      category: (fd.get('category')||'').toString(),
      date: (fd.get('date')||new Date().toISOString().slice(0,10)).toString(),
      method: (fd.get('method')||'Cash').toString()
    };
    if (!data.desc || !(data.amount>0) || !data.category){
      alert('Please fill Description, positive Amount and Category'); return;
    }
    const list = $('#expList') || document.querySelector('.tlist');
    const row = buildRow(data);
    list?.prepend(row);
    renderKPIs();
    toastJSON({ action: 'add', ...data });
    closeAdd();
  });

  // ========== Modal EDIT ==========
  const editModal = $('#expEditModal');
  const editForm  = $('#expEditForm');
  let editingRow  = null;

  function openEdit(row){
    editingRow = row;
    $('#expEditTitle').textContent = `Edit Expense – ${row.dataset.desc || ''}`;
    editForm.desc.value     = row.dataset.desc || row.querySelector('.name')?.textContent?.trim() || '';
    editForm.amount.value   = Number(row.dataset.amount || 0);
    editForm.category.value = row.dataset.category || '';
    editForm.date.value     = row.dataset.date || '';
    // chuẩn hóa label method trong Edit form (khác value Add form)
    const m = row.dataset.method || 'Cash';
    editForm.method.value   = m.replace('-', ' ');
    editModal.classList.add('show');
    editModal.setAttribute('aria-hidden','false');
  }
  function closeEdit(){
    editModal.classList.remove('show');
    editModal.setAttribute('aria-hidden','true');
    editingRow = null;
  }
  editModal?.querySelector('.modal-close')?.addEventListener('click', closeEdit);
  editModal?.querySelector('[data-close]')?.addEventListener('click', closeEdit);
  editModal?.addEventListener('click', (e)=>{ if(e.target===editModal) closeEdit(); });

  editForm?.addEventListener('submit', (e)=>{
    e.preventDefault();
    if (!editingRow) return;

    const fd = new FormData(editForm);
    const updated = {
      id: editingRow.dataset.id,
      desc: (fd.get('desc')||'').toString().trim(),
      amount: Number(fd.get('amount')||0),
      category: (fd.get('category')||'').toString(),
      date: (fd.get('date')||'').toString(),
      method: (fd.get('method')||'Cash').toString()
    };
    if (!updated.desc || !(updated.amount>0) || !updated.category){
      alert('Please fill Description, positive Amount and Category'); return;
    }

    // Update dataset
    Object.assign(editingRow.dataset, {
      desc: updated.desc,
      amount: String(updated.amount),
      category: updated.category,
      date: updated.date,
      method: updated.method
    });

    // Update UI
    editingRow.querySelector('.name').textContent = updated.desc;
    const badgeColor = colorOf(updated.category);
    editingRow.querySelector('.sub').innerHTML = `
      ${escapeHtml(updated.date)} &nbsp;|&nbsp; ${escapeHtml(updated.method)}
      <span class="badge ${badgeColor}">${escapeHtml(updated.category)}</span>
    `;
    const amtEl = editingRow.querySelector('.amt');
    amtEl.dataset.amount = String(updated.amount);
    amtEl.textContent = fmt0(updated.amount);

    renderKPIs();
    toastJSON({ action: 'edit', ...updated });
    closeEdit();
  });

  // ========== Filter theo category ==========
  $('#catFilter')?.addEventListener('change', (e)=>{
    const val = e.target.value;
    $$('.exp-row').forEach(r=>{
      const cat = r.dataset.category || '';
      r.style.display = (val==='All' || !val || cat===val) ? '' : 'none';
    });
    renderKPIs();
  });

  // init
  renderKPIs();
})();
