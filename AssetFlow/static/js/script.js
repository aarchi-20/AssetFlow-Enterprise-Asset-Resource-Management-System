/* =========================================================================
   AssetFlow — shared front-end behaviour
   Presentation-layer only: sidebar/menu, tabs, modals, drag/drop visuals,
   counters, animated bars, booking-slot selection, auth panel switch,
   password visibility, toasts. No data is persisted — Django owns state.
   ========================================================================= */

document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initTabs();
  initModals();
  initPasswordToggles();
  initAuthTabs();
  initCounters();
  initRevealOnScroll();
  initBarAnimations();
  initKanbanDragDrop();
  initBookingSlots();
  initAuditVerify();
  initNotifFilters();
  initToastDemo();
  initSearchFocusHotkey();
});

/* ---------------------------------------------------------------------
   Sidebar (mobile slide-in)
   --------------------------------------------------------------------- */
function initSidebar(){
  const toggle = document.querySelector('[data-menu-toggle]');
  const sidebar = document.querySelector('.sidebar');
  const scrim = document.querySelector('.sidebar-scrim');
  if (!toggle || !sidebar) return;

  const open = () => { sidebar.classList.add('open'); scrim && scrim.classList.add('show'); };
  const close = () => { sidebar.classList.remove('open'); scrim && scrim.classList.remove('show'); };

  toggle.addEventListener('click', () => {
    sidebar.classList.contains('open') ? close() : open();
  });
  scrim && scrim.addEventListener('click', close);
  sidebar.querySelectorAll('.nav-link').forEach(l => l.addEventListener('click', close));
}

/* ---------------------------------------------------------------------
   Generic tabs — works for Organization Setup, Notifications filters, etc.
   Markup contract: [data-tabs] wraps [data-tab-btn="key"] buttons and
   sibling [data-tab-panel="key"] panels.
   --------------------------------------------------------------------- */
function initTabs(){
  document.querySelectorAll('[data-tabs]').forEach(group => {
    const btns = group.querySelectorAll('[data-tab-btn]');
    const panelsWrap = document.querySelector(group.dataset.tabs) || document;
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        const key = btn.getAttribute('data-tab-btn');
        btns.forEach(b => b.classList.toggle('active', b === btn));
        panelsWrap.querySelectorAll('[data-tab-panel]').forEach(p => {
          p.classList.toggle('active', p.getAttribute('data-tab-panel') === key);
        });
      });
    });
  });
}

/* ---------------------------------------------------------------------
   Modals — [data-open-modal="id"] opens #id, [data-close-modal] closes
   nearest .modal-overlay, overlay click and Escape close it too.
   --------------------------------------------------------------------- */
function initModals(){
  document.querySelectorAll('[data-open-modal]').forEach(btn => {
    btn.addEventListener('click', () => {
      const el = document.getElementById(btn.getAttribute('data-open-modal'));
      if (el) { el.classList.add('open'); document.body.style.overflow = 'hidden'; }
    });
  });
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeOverlay(overlay);
    });
    overlay.querySelectorAll('[data-close-modal]').forEach(btn => {
      btn.addEventListener('click', () => closeOverlay(overlay));
    });
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.open').forEach(closeOverlay);
    }
  });
  function closeOverlay(overlay){
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }
}

/* ---------------------------------------------------------------------
   Password show/hide
   --------------------------------------------------------------------- */
function initPasswordToggles(){
  document.querySelectorAll('.toggle-visibility').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.closest('.input-icon-wrap').querySelector('input');
      const isPw = input.type === 'password';
      input.type = isPw ? 'text' : 'password';
      btn.innerHTML = isPw ? eyeOffIcon() : eyeIcon();
    });
  });
}
function eyeIcon(){ return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="12" r="3"/></svg>'; }
function eyeOffIcon(){ return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 3l18 18M10.6 10.6a2 2 0 002.8 2.8M9.4 5.5A10.7 10.7 0 0112 5c7 0 11 7 11 7a13.2 13.2 0 01-3.4 3.9M6.2 6.6C3.6 8.3 2 11 2 11s4 7 11 7c1.4 0 2.7-.3 3.8-.7"/></svg>'; }

/* ---------------------------------------------------------------------
   Auth screen: login / signup pill toggle
   --------------------------------------------------------------------- */
function initAuthTabs(){
  const tabs = document.querySelectorAll('.auth-tab');
  if (!tabs.length) return;
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const key = tab.getAttribute('data-auth-tab');
      tabs.forEach(t => t.classList.toggle('active', t === tab));
      document.querySelectorAll('.auth-panel').forEach(p => {
        p.classList.toggle('active', p.getAttribute('data-auth-panel') === key);
      });
    });
  });
}

/* ---------------------------------------------------------------------
   KPI counters — animate number up when card enters viewport
   Markup: <span data-counter="128">0</span>
   --------------------------------------------------------------------- */
function initCounters(){
  const counters = document.querySelectorAll('[data-counter]');
  if (!counters.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      animateCount(entry.target);
      io.unobserve(entry.target);
    });
  }, { threshold: 0.4 });
  counters.forEach(c => io.observe(c));
}
function animateCount(el){
  const target = parseInt(el.getAttribute('data-counter'), 10) || 0;
  const duration = 900;
  const start = performance.now();
  function tick(now){
    const p = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(eased * target);
    if (p < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

/* ---------------------------------------------------------------------
   Generic scroll reveal for .reveal elements, with stagger via --d
   --------------------------------------------------------------------- */
function initRevealOnScroll(){
  const items = document.querySelectorAll('.reveal');
  if (!items.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting){
        entry.target.classList.add('in');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  items.forEach((el, i) => {
    el.style.setProperty('--d', `${(i % 8) * 60}ms`);
    io.observe(el);
  });
}

/* ---------------------------------------------------------------------
   Bar / hbar chart animate-in (Reports screen)
   --------------------------------------------------------------------- */
function initBarAnimations(){
  const charts = document.querySelectorAll('.bar-chart');
  const hbars = document.querySelectorAll('.hbar-fill');
  if (charts.length){
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting){
          entry.target.classList.add('animate');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.3 });
    charts.forEach(c => io.observe(c));
  }
  if (hbars.length){
    const io2 = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting){
          const target = entry.target.getAttribute('data-width') || '0%';
          entry.target.style.width = target;
          io2.unobserve(entry.target);
        }
      });
    }, { threshold: 0.3 });
    hbars.forEach(h => io2.observe(h));
  }
}

/* ---------------------------------------------------------------------
   Kanban board drag & drop (visual reordering only — Maintenance screen)
   --------------------------------------------------------------------- */
function initKanbanDragDrop(){
  const cards = document.querySelectorAll('.kanban-card');
  const cols = document.querySelectorAll('.kanban-cards');
  if (!cards.length) return;

  cards.forEach(card => {
    card.setAttribute('draggable', 'true');
    card.addEventListener('dragstart', () => card.classList.add('dragging'));
    card.addEventListener('dragend', () => {
      card.classList.remove('dragging');
      updateKanbanCounts();
    });
  });

  cols.forEach(col => {
    col.addEventListener('dragover', (e) => {
      e.preventDefault();
      col.closest('.kanban-col').classList.add('drag-over');
      const dragging = document.querySelector('.dragging');
      const after = getDragAfterElement(col, e.clientY);
      if (!dragging) return;
      if (after == null) col.appendChild(dragging);
      else col.insertBefore(dragging, after);
    });
    col.addEventListener('dragleave', (e) => {
      if (!col.contains(e.relatedTarget)) col.closest('.kanban-col').classList.remove('drag-over');
    });
    col.addEventListener('drop', () => col.closest('.kanban-col').classList.remove('drag-over'));
  });

  function getDragAfterElement(container, y){
    const els = [...container.querySelectorAll('.kanban-card:not(.dragging)')];
    return els.reduce((closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;
      if (offset < 0 && offset > closest.offset) return { offset, element: child };
      return closest;
    }, { offset: -Infinity }).element;
  }

  function updateKanbanCounts(){
    document.querySelectorAll('.kanban-col').forEach(col => {
      const count = col.querySelectorAll('.kanban-card').length;
      const badge = col.querySelector('.kanban-count');
      if (badge) badge.textContent = count;
    });
  }
}

/* ---------------------------------------------------------------------
   Resource booking — slot selection + resource switch (visual only)
   --------------------------------------------------------------------- */
function initBookingSlots(){
  document.querySelectorAll('.slot-block.open').forEach(slot => {
    slot.addEventListener('click', () => {
      document.querySelectorAll('.slot-block.selected').forEach(s => {
        if (s !== slot) s.classList.remove('selected');
      });
      slot.classList.toggle('selected');
      const label = document.querySelector('[data-selected-slot]');
      if (label) {
        const active = document.querySelector('.slot-block.selected');
        label.textContent = active ? active.getAttribute('data-time') : 'No slot selected';
      }
    });
  });

  document.querySelectorAll('.resource-item').forEach(item => {
    item.addEventListener('click', () => {
      document.querySelectorAll('.resource-item').forEach(r => r.classList.remove('active'));
      item.classList.add('active');
      const title = document.querySelector('[data-resource-title]');
      if (title) title.textContent = item.querySelector('.r-name').textContent;
    });
  });
}

/* ---------------------------------------------------------------------
   Audit checklist — Verified / Missing / Damaged toggle per row
   --------------------------------------------------------------------- */
function initAuditVerify(){
  document.querySelectorAll('.verify-group').forEach(group => {
    const buttons = group.querySelectorAll('.verify-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        buttons.forEach(b => b.classList.remove('is-active'));
        btn.classList.add('is-active');
        updateAuditSummary();
      });
    });
  });
  function updateAuditSummary(){
    const flagged = document.querySelectorAll('.verify-btn[data-state="missing"].is-active, .verify-btn[data-state="damaged"].is-active').length;
    const summary = document.querySelector('[data-audit-flagged]');
    if (summary) summary.textContent = flagged;
  }
}

/* ---------------------------------------------------------------------
   Notifications filter pills
   --------------------------------------------------------------------- */
function initNotifFilters(){
  const pills = document.querySelectorAll('[data-notif-filter]');
  const items = document.querySelectorAll('[data-notif-type]');
  if (!pills.length) return;
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const filter = pill.getAttribute('data-notif-filter');
      items.forEach(item => {
        const show = filter === 'all' || item.getAttribute('data-notif-type') === filter;
        item.style.display = show ? '' : 'none';
      });
    });
  });
}

/* ---------------------------------------------------------------------
   Toast demo — trigger via [data-toast-demo]
   --------------------------------------------------------------------- */
function initToastDemo(){
  const stack = document.querySelector('.toast-stack');
  document.querySelectorAll('[data-toast-demo]').forEach(btn => {
    btn.addEventListener('click', () => {
      const msg = btn.getAttribute('data-toast-demo') || 'Saved successfully';
      showToast(msg);
    });
  });
  function showToast(msg){
    if (!stack) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg><span>${msg}</span>`;
    stack.appendChild(toast);
    setTimeout(() => {
      toast.style.transition = 'opacity .3s ease, transform .3s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(16px)';
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }
}

/* ---------------------------------------------------------------------
   "/" focuses the topbar search field, like most SaaS dashboards
   --------------------------------------------------------------------- */
function initSearchFocusHotkey(){
  const search = document.querySelector('.search-field input');
  if (!search) return;
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      search.focus();
    }
  });
}