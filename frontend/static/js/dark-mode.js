/* ============================================================
   ORCHESTRA DARK MODE — inject this JS anywhere in your HTML
   ============================================================ */

(function() {
  // Inject theme toggle button into topbar
  function injectThemeToggle() {
    // Find topbar right section — adjust selector to match your topbar
    const topbarRight = document.querySelector(
      '.topbar-right, .nav-right, .header-actions, [class*="topbar"] [class*="right"]'
    );
    if (!topbarRight || document.getElementById('orch-theme-toggle')) return;

    const btn = document.createElement('button');
    btn.id = 'orch-theme-toggle';
    btn.title = 'Toggle dark mode';
    btn.innerHTML = '<span class="icon-sun">light_mode</span><span class="icon-moon">dark_mode</span>';
    btn.onclick = toggleTheme;

    // Insert before last child (usually the user avatar)
    topbarRight.insertBefore(btn, topbarRight.lastElementChild);
  }

  function applyTheme(dark) {
    document.documentElement.classList.toggle('orch-dark', dark);
    try { localStorage.setItem('orch-theme', dark ? 'dark' : 'light'); } catch(e) {}
  }

  window.toggleTheme = function() {
    applyTheme(!document.documentElement.classList.contains('orch-dark'));
  };

  // On load — respect saved pref or system preference
  (function() {
    let saved;
    try { saved = localStorage.getItem('orch-theme'); } catch(e) {}
    if (saved === 'dark') applyTheme(true);
    else if (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches) applyTheme(true);
  })();

  // Listen for system preference changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    try { if (!localStorage.getItem('orch-theme')) applyTheme(e.matches); } catch(err) {}
  });

  // Inject toggle when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectThemeToggle);
  } else {
    injectThemeToggle();
  }
})();
