(function () {
  // Menu no celular
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('menu');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? 'Fechar' : 'Menu';
    });
  }

  // Carrossel de passagens
  var box = document.querySelector('[data-slides]');
  if (box) {
    var slides = Array.prototype.slice.call(box.querySelectorAll('.slide'));
    var dotsWrap = box.querySelector('.dots');
    var live = box.querySelector('[aria-live]');
    var i = 0, timer = null;
    var dots = slides.map(function (s, n) {
      var d = document.createElement('button');
      d.type = 'button';
      d.setAttribute('aria-label', 'Passagem ' + (n + 1) + ' de ' + slides.length);
      d.addEventListener('click', function () { go(n); restart(); });
      dotsWrap.appendChild(d);
      return d;
    });
    function go(n) {
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle('on', k === i); s.setAttribute('aria-hidden', k === i ? 'false' : 'true'); });
      dots.forEach(function (d, k) { d.setAttribute('aria-current', k === i ? 'true' : 'false'); });
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    function restart() { stop(); timer = setInterval(function () { go(i + 1); }, 30000); }
    box.querySelector('[data-prev]').addEventListener('click', function () { go(i - 1); restart(); if (live) live.textContent = slides[i].textContent; });
    box.querySelector('[data-next]').addEventListener('click', function () { go(i + 1); restart(); if (live) live.textContent = slides[i].textContent; });
    // pausa só com o mouse em cima (no celular o toque não pausa)
    box.addEventListener('pointerenter', function (ev) { if (ev.pointerType === 'mouse') stop(); });
    box.addEventListener('pointerleave', function (ev) { if (ev.pointerType === 'mouse') restart(); });
    // pausa enquanto alguém navega pelo teclado dentro do carrossel
    box.addEventListener('focusin', function (ev) { try { if (ev.target.matches(':focus-visible')) stop(); } catch (err) {} });
    box.addEventListener('focusout', restart);
    // começa em uma passagem diferente a cada dia
    var day = Math.floor(Date.now() / 86400000);
    go(day % slides.length);
    restart();
  }

  // Copiar mensagem
  Array.prototype.forEach.call(document.querySelectorAll('[data-copy]'), function (b) {
    b.addEventListener('click', function () {
      var text = b.getAttribute('data-copy');
      var done = function () { var o = b.textContent; b.textContent = 'Copiada'; setTimeout(function () { b.textContent = o; }, 2000); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () {});
    });
  });
})();
