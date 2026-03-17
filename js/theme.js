(function() {
  var html = document.documentElement;
  var stored = localStorage.getItem('sf-theme');
  if (stored) html.setAttribute('data-theme', stored);

  var toggle = document.getElementById('themeToggle');
  if (toggle) {
    toggle.addEventListener('click', function() {
      var next = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      html.setAttribute('data-theme', next);
      localStorage.setItem('sf-theme', next);
    });
  }
})();
