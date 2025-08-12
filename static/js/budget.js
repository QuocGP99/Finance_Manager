// static/js/budget.js
(function () {
  const cur = window.CURRENCY || '';
  const $  = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const fmt = n => `${cur}${Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

  // ===== KPI helpers =====
  function readTotals() {
    let totalLimit = 0, totalSpent = 0;
    $$('#budgetList .budget-item').forEach(card => {
      totalLimit += +card.dataset.limit || 0;
      totalSpent += +card.dataset.spent || 0;
    });
    return {
      totalLimit,
      totalSpent,
      remaining: Math.max(totalLimit - totalSpent, 0),
      pct: totalLimit ? (totalSpent / totalLimit * 100) : 0
    };
  }
  function renderKPI() {
    const t = readTotals();
    $('#kpiTotalLimit') && ($('#kpiTotalLimit').textContent = fmt(t.totalLimit));
    $('#kpiTotalSpent') && ($('#kpiTotalSpent').textContent = fmt(t.totalSpent));
    $('#kpiRemaining')  && ($('#kpiRemaining').textContent  = fmt(t.remaining));
    $('#kpiPctUsed')    && ($('#kpiPctUsed').textContent    = t.pct.toFixed(1));
  }

  // ===== Card helpers =====
  function updateCard(card) {
    const spent = +card.dataset.spent || 0;
    const limit = +card.dataset.limit || 0;
    const pct   = limit ? (spent / limit * 100) : 0;

    const titleEl = card.querySelector('.bi-title');
    const amountEl = card.querySelector('.bi-amount');
    const pctEl    = card.querySelector('.bi-pct');
    const barSpan  = card.querySelector('.bar span');
    const leftEl   = card.querySelector('.bi-remaining');

    amountEl && (amountEl.textContent = `${fmt(spent)} / ${fmt(limit)}`);
    pctEl    && (pctEl.textContent    = pct.toFixed(1));
    barSpan  && (barSpan.style.width  = `${Math.min(100, pct)}%`);
    leftEl   && (leftEl.textContent   = `${fmt(Math.max(limit - spent, 0))} remaining`);

    // chip cảnh báo nếu >80%
    const chip = titleEl?.querySelector('.chip');
    if (chip) {
      chip.classList.remove('low', 'medium');
      if (pct >= 80) {
        chip.textContent = 'Warning';
        chip.classList.add('medium');
      } else {
        chip.textContent = 'On Track';
        chip.classList.add('low');
      }
    }
  }

  function bindCardActions(card) {
    // Edit
    card.querySelector('[data-edit]')?.addEventListener('click', () => {
      openModal('edit', {
        category: card.dataset.name,
        amount: card.dataset.limit
      }, (data) => {
        card.dataset.name  = data.category;
        card.dataset.limit = data.amount;
        // đổi tiêu đề nếu đổi tên
        const titleTxt = card.querySelector('.bi-title');
        if (titleTxt) {
          // bi-title: "Tên <span class='chip ...'>...</span>"
          const chip = titleTxt.querySelector('.chip');
          titleTxt.textContent = data.category + ' ';
          chip && titleTxt.appendChild(chip);
        }
        updateCard(card);
        renderKPI();
      });
    });

    // Delete
    card.querySelector('[data-delete]')?.addEventListener('click', () => {
      if (confirm('Delete this budget category?')) {
        card.remove();
        renderKPI();
      }
    });
  }

  // ===== Modal logic (phù hợp modal mới) =====
  const modal = $('#budgetModal');
  const form  = $('#budgetForm');

  function openModal(mode = 'add', initial = {}, onSubmit) {
    if (!modal || !form) return;

    // Set title + nút submit (dựa theo markup modal mới)
    const titleEl = modal.querySelector('.modal-head h3');
    if (titleEl) titleEl.textContent = (mode === 'add') ? 'Add New Budget Category' : 'Edit Budget Category';

    // reset form
    form.reset();

    // preset cho edit
    const selCategory = form.category;
    const inputCustom = form.custom;         // optional (nếu bạn có field custom)
    const customWrap  = $('#customWrap') || form.closest('.modal')?.querySelector('#customWrap');
    const amountInput = form.amount;

    if (mode === 'edit') {
      // nếu danh mục có trong options => chọn; không có => bật custom
      if (selCategory) {
        let matched = false;
        for (const opt of selCategory.options || []) {
          if (opt.value === initial.category) { selCategory.value = opt.value; matched = true; break; }
        }
        if (!matched) {
          // fallback cho custom (nếu tồn tại)
          if (selCategory.querySelector('option[value="__custom__"]')) {
            selCategory.value = '__custom__';
            customWrap && customWrap.classList.remove('hide');
          }
          if (inputCustom) inputCustom.value = initial.category || '';
        }
      }
      if (amountInput) amountInput.value = initial.amount || '';
    } else {
      // add: ẩn custom
      customWrap && customWrap.classList.add('hide');
    }

    // binding change cho select (nếu có __custom__)
    selCategory?.addEventListener('change', () => {
      if (selCategory.value === '__custom__') customWrap && customWrap.classList.remove('hide');
      else customWrap && customWrap.classList.add('hide');
    }, { once: true });

    // mở modal
    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');

    // one-off submit
    const handler = (e) => {
      e.preventDefault();
      let category = selCategory ? selCategory.value : '';
      if (category === '__custom__') category = (inputCustom?.value || '').trim();
      const amount = +(amountInput?.value || 0);

      if (!category || amount <= 0) { alert('Please select a category and enter amount > 0'); return; }

      onSubmit && onSubmit({ category, amount });
      closeModal();
      form.removeEventListener('submit', handler);
    };
    form.addEventListener('submit', handler, { once: true });
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
  }

  // open/close triggers
  $('#addBudgetBtn')?.addEventListener('click', () => openModal('add', {}, (data) => {
    // tạo card mới
    const card = document.createElement('article');
    card.className = 'panel budget-item';
    card.dataset.name  = data.category;
    card.dataset.spent = '0';
    card.dataset.limit = String(data.amount);
    card.innerHTML = `
      <div class="row">
        <div class="bi-title">${data.category} <span class="chip low">On Track</span></div>
        <div class="bi-tools" style="display:flex;align-items:center;gap:10px;">
          <span class="bi-amount">${fmt(0)} / ${fmt(data.amount)}</span>
          <button class="icon-btn" data-edit title="Edit"><span class="material-icons">edit</span></button>
          <button class="icon-btn" data-delete title="Delete"><span class="material-icons">delete</span></button>
        </div>
      </div>
      <div class="bar green" style="margin-top:10px"><span style="width:0%"></span></div>
      <div class="row" style="margin-top:6px">
        <div class="muted"><span class="bi-pct">0.0</span>% used</div>
        <div class="bi-remaining">${fmt(data.amount)} remaining</div>
      </div>
      <div class="row bi-apply" style="margin-top:8px; background:#faf5ff; border:1px solid #efe6ff; padding:10px 12px; border-radius:10px">
        <div class="muted">AI suggests: ${fmt(data.amount * 0.96)}</div>
        <button class="btn btn-outline" style="padding:6px 12px"><span class="material-icons" style="font-size:18px">check_circle</span>Apply</button>
      </div>
    `;
    $('#budgetList')?.appendChild(card);
    bindCardActions(card);
    updateCard(card);
    renderKPI();
  }));
  modal?.querySelector('.modal-close')?.addEventListener('click', closeModal);
  modal?.querySelector('[data-close]')?.addEventListener('click', closeModal);
  modal?.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });

  // ===== First bind for existing cards =====
  $$('#budgetList .budget-item').forEach(card => bindCardActions(card));
  renderKPI();
})();
