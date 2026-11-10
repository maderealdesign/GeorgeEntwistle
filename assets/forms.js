(function () {
  'use strict';
  document.querySelectorAll('[data-quote-form]').forEach(function (form) {
    var button = form.querySelector('button[type="submit"]');
    var label = form.querySelector('[data-submit-label]');
    var status = form.querySelector('[data-form-status]');
    var sending = false;
    form.addEventListener('submit', async function (event) {
      event.preventDefault();
      if (sending) return;
      if (!form.reportValidity()) return;
      sending = true;
      form.dataset.state = 'sending';
      form.setAttribute('aria-busy', 'true');
      button.disabled = true;
      label.textContent = 'Sending…';
      status.hidden = true;
      status.textContent = '';
      var controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
      var timer = controller ? window.setTimeout(function () { controller.abort(); }, 30000) : null;
      try {
        var options = {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams(new FormData(form)).toString()
        };
        if (controller) options.signal = controller.signal;
        var response = await fetch('/', options);
        if (!response.ok) throw new Error('Submission was not accepted');
        form.dataset.state = 'success';
        label.textContent = 'Enquiry sent';
        window.location.assign(form.getAttribute('action'));
      } catch (error) {
        form.dataset.state = 'error';
        status.textContent = error.name === 'AbortError'
          ? 'We couldn’t confirm your enquiry was received. Your details are still here. Please try again, or call George on 07581 223870.'
          : 'Your enquiry could not be sent. Your details are still here. Please try again, or call George on 07581 223870.';
        status.hidden = false;
        status.focus();
        sending = false;
        button.disabled = false;
        label.textContent = 'Try sending again';
      } finally {
        if (timer !== null) window.clearTimeout(timer);
        form.removeAttribute('aria-busy');
      }
    });
  });
})();
