(function () {
  'use strict';
  document.documentElement.classList.add('js');
  var menuToggle = document.querySelector('[data-menu-toggle]');
  var nav = document.querySelector('[data-nav]');
  function closeMenu() {
    if (!menuToggle || !nav) return;
    menuToggle.setAttribute('aria-expanded', 'false');
    menuToggle.setAttribute('aria-label', 'Open navigation');
    nav.classList.remove('open');
  }
  if (menuToggle && nav) {
    menuToggle.addEventListener('click', function () {
      var open = menuToggle.getAttribute('aria-expanded') !== 'true';
      menuToggle.setAttribute('aria-expanded', String(open));
      menuToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      nav.classList.toggle('open', open);
    });
    nav.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeMenu();
    });
    document.addEventListener('click', function (event) {
      if (!nav.contains(event.target) && !menuToggle.contains(event.target)) closeMenu();
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
        closeMenu();
        menuToggle.focus();
      }
    });
    window.matchMedia('(min-width: 961px)').addEventListener('change', function (event) {
      if (event.matches) closeMenu();
    });
  }

  var filterBar = document.querySelector('[data-gallery-filters]');
  var cards = Array.from(document.querySelectorAll('[data-photo-card]'));
  var counter = document.querySelector('[data-gallery-count]');
  if (counter) { counter.setAttribute('role', 'status'); counter.setAttribute('aria-live', 'polite'); counter.setAttribute('aria-atomic', 'true'); }
  function visibleCards() { return cards.filter(function (card) { return !card.hidden; }); }
  function setCount(label) {
    if (!counter) return;
    var total = visibleCards().length;
    counter.textContent = total + ' photo' + (total === 1 ? '' : 's') + (label && label.toLowerCase() !== 'all' ? ' · ' + label : ' · all projects');
  }
  if (filterBar && cards.length) {
    filterBar.hidden = false;
    filterBar.addEventListener('click', function (event) {
      var button = event.target.closest('[data-filter]');
      if (!button || !filterBar.contains(button)) return;
      var filter = (button.getAttribute('data-filter') || 'all').toLowerCase();
      filterBar.querySelectorAll('[data-filter]').forEach(function (item) {
        item.setAttribute('aria-pressed', String(item === button));
      });
      cards.forEach(function (card) {
        var categories = (card.getAttribute('data-category') || '').toLowerCase().split(/[,|]/).map(function (s) { return s.trim(); });
        card.hidden = filter !== 'all' && categories.indexOf(filter) === -1;
      });
      setCount(button.textContent.trim());
    });
    setCount('all');
  }

  var dialog = document.querySelector('[data-lightbox]');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  var photo = dialog.querySelector('.lightbox-image');
  var title = dialog.querySelector('[data-lightbox-title]');
  var position = dialog.querySelector('[data-lightbox-position]');
  var previous = dialog.querySelector('[data-prev]');
  var next = dialog.querySelector('[data-next]');
  var close = dialog.querySelector('[data-close]');
  var activeLinks = [];
  var index = 0;
  var opener = null;
  if (!photo) return;

  function showPhoto(newIndex) {
    if (!activeLinks.length) return;
    index = (newIndex + activeLinks.length) % activeLinks.length;
    var link = activeLinks[index];
    var sourceImage = link.querySelector('img');
    photo.src = link.href;
    photo.alt = link.getAttribute('data-alt') || (sourceImage ? sourceImage.alt : 'Paving project photograph');
    if (title) title.textContent = link.getAttribute('data-caption') || photo.alt;
    if (position) position.textContent = (index + 1) + ' / ' + activeLinks.length;
    if (previous) previous.disabled = activeLinks.length < 2;
    if (next) next.disabled = activeLinks.length < 2;
  }
  document.addEventListener('click', function (event) {
    var link = event.target.closest('a[data-photo-link]');
    if (!link || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener = link;
    activeLinks = Array.from(document.querySelectorAll('a[data-photo-link]')).filter(function (item) {
      var card = item.closest('[data-photo-card]');
      return !card || !card.hidden;
    });
    showPhoto(Math.max(0, activeLinks.indexOf(link)));
    if (!dialog.open) dialog.showModal();
    document.body.style.overflow = 'hidden';
    if (close) close.focus();
  });
  if (close) close.addEventListener('click', function () { dialog.close(); });
  if (previous) previous.addEventListener('click', function () { showPhoto(index - 1); });
  if (next) next.addEventListener('click', function () { showPhoto(index + 1); });
  dialog.addEventListener('keydown', function (event) {
    if (event.key === 'ArrowLeft') { event.preventDefault(); showPhoto(index - 1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); showPhoto(index + 1); }
  });
  dialog.addEventListener('click', function (event) {
    if (event.target !== dialog) return;
    var rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
  dialog.addEventListener('close', function () {
    document.body.style.overflow = '';
    photo.removeAttribute('src');
    if (opener && document.contains(opener)) opener.focus({ preventScroll: true });
  });
})();

// Logo faces assemble once on entry; all content stays available without motion.
(function () {
  'use strict';
  var preference = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (preference.matches || !('IntersectionObserver' in window)) return;
  var targets = document.querySelectorAll('[data-reveal], [data-brand-mark]');
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -20px 0px' });
  document.documentElement.classList.add('motion-ready');
  targets.forEach(function (target) { observer.observe(target); });
  preference.addEventListener('change', function (event) {
    if (event.matches) {
      document.documentElement.classList.remove('motion-ready');
      targets.forEach(function (target) { target.classList.add('is-visible'); });
      observer.disconnect();
    }
  });
})();
