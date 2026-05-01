export function applyTheme(isDark) {
    document.documentElement.classList.toggle('dark', isDark);
    const sun  = document.querySelector('.icon-sun');
    const moon = document.querySelector('.icon-moon');
    if (sun)  sun.style.display  = isDark ? 'none'  : 'block';
    if (moon) moon.style.display = isDark ? 'block' : 'none';
    localStorage.setItem('orchestra-theme', isDark ? 'dark' : 'light');
}

export function toggleTheme() {
    applyTheme(!document.documentElement.classList.contains('dark'));
}

window.applyTheme  = applyTheme;
window.toggleTheme = toggleTheme;
