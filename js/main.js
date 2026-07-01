// Mobile nav toggle
const toggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');

if (toggle && navLinks) {
  toggle.addEventListener('click', () => {
    const open = navLinks.classList.toggle('open');
    toggle.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', open);
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.site-nav')) {
      navLinks.classList.remove('open');
      toggle.classList.remove('open');
      toggle.setAttribute('aria-expanded', false);
    }
  });
}

// Highlight active nav link based on current page
const currentPage = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav-links a').forEach(link => {
  const href = link.getAttribute('href');
  if (href === currentPage || (currentPage === '' && href === 'index.html')) {
    link.classList.add('active');
  } else {
    link.classList.remove('active');
  }
});

// FAQ accordion
document.querySelectorAll('.faq-question').forEach(btn => {
  btn.addEventListener('click', () => {
    const item = btn.closest('.faq-item');
    const isOpen = item.classList.contains('open');
    // Close all
    document.querySelectorAll('.faq-item.open').forEach(el => el.classList.remove('open'));
    // Open clicked (unless it was already open)
    if (!isOpen) item.classList.add('open');
  });
});

// Lightbox
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightbox-img');
const lightboxClose = document.getElementById('lightbox-close');

if (lightbox) {
  document.querySelectorAll('.gallery-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      lightboxImg.src = link.href;
      lightboxImg.alt = link.querySelector('img')?.alt || '';
      lightbox.classList.add('open');
      document.body.style.overflow = 'hidden';
    });
  });

  const closeLightbox = () => {
    lightbox.classList.remove('open');
    lightboxImg.src = '';
    document.body.style.overflow = '';
  };

  lightboxClose?.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', (e) => { if (e.target === lightbox) closeLightbox(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeLightbox(); });
}

// Event details modal (upcoming events list)
const eventModal = document.getElementById('event-modal');
const eventModalBody = document.getElementById('event-modal-body');
const eventModalClose = document.getElementById('event-modal-close');

if (eventModal) {
  const openEventModal = (item) => {
    const tpl = item.querySelector('.event-detail-tpl');
    if (!tpl) return;
    eventModalBody.replaceChildren(tpl.content.cloneNode(true));
    eventModal.classList.add('open');
    document.body.style.overflow = 'hidden';
    eventModalClose?.focus();
  };

  const closeEventModal = () => {
    eventModal.classList.remove('open');
    eventModalBody.replaceChildren();
    document.body.style.overflow = '';
  };

  document.querySelectorAll('.upcoming-item, .event-card').forEach(item => {
    item.addEventListener('click', () => openEventModal(item));
    item.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openEventModal(item);
      }
    });
  });

  eventModalClose?.addEventListener('click', closeEventModal);
  eventModal.addEventListener('click', (e) => { if (e.target === eventModal) closeEventModal(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeEventModal(); });
}

// Calendar tabs
document.querySelectorAll('.cal-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    const target = tab.dataset.target;
    document.querySelectorAll('.cal-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.cal-panel').forEach(p => p.hidden = true);
    tab.classList.add('active');
    const panel = document.getElementById(target);
    if (panel) panel.hidden = false;
  });
});
