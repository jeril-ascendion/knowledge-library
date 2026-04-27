/* Ascendion Engineering — Wordmark animator
   Wraps each character of .nav-wordmark text in a span with staggered delay.
   Call once on DOMContentLoaded. */
(function () {
  function animateWordmark() {
    const el = document.querySelector('.nav-wordmark');
    if (!el) return;
    const text = el.textContent;
    el.textContent = '';
    text.split('').forEach((ch, i) => {
      const span = document.createElement('span');
      span.className = 'wordmark-char';
      span.style.animationDelay = (i * 28) + 'ms';
      span.textContent = ch;
      el.appendChild(span);
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', animateWordmark);
  } else {
    animateWordmark();
  }
})();
