import { activityFeed } from './feed.js';

export function showCompletionToast(goalText) {
    const toast = document.getElementById('completionToast');
    const el    = document.getElementById('ct-goal-text');
    if (el)    el.textContent = goalText;
    if (toast) toast.classList.add('show');
}

export function switchView(viewId) {
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
        const text = item.textContent.trim().toLowerCase();
        const active =
            (viewId === 'dashboard'   && (text.includes('dashboard') || text.includes('home'))) ||
            (viewId === 'workflows'   && text.includes('active workflow')) ||
            (viewId === 'tasks'       && text.includes('all task')) ||
            (viewId === 'outputs'     && text.includes('output')) ||
            (viewId === 'trace'       && text.includes('agent reasoning')) ||
            (viewId === 'vibe-checks' && text.includes('vibe')) ||
            (viewId === 'debates'     && text.includes('debate')) ||
            (viewId === 'settings'    && (text.includes('setting') || text.includes('safety')));
        item.classList.toggle('active', active);
    });

    document.querySelectorAll('.view-section').forEach(v => {
        v.style.display = v.id === `view-${viewId}` ? '' : 'none';
    });

    const bar = document.getElementById('back-dash-bar');
    if (bar) bar.style.display = viewId === 'dashboard' ? 'none' : 'flex';
}

export function openPalette() {
    const p   = document.getElementById('palette');
    const b   = document.getElementById('paletteBackdrop');
    const inp = document.getElementById('paletteInput');
    if (p && b) {
        p.classList.add('open');
        b.classList.add('open');
        if (inp) { inp.value = ''; setTimeout(() => inp.focus(), 50); }
    }
}

export function closePalette() {
    const p = document.getElementById('palette');
    const b = document.getElementById('paletteBackdrop');
    if (p && b) { p.classList.remove('open'); b.classList.remove('open'); }
}

document.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); openPalette(); }
    if (e.key === 'Escape') closePalette();
});

window.switchView        = switchView;
window.openPalette       = openPalette;
window.closePalette      = closePalette;
window.showCompletionToast = showCompletionToast;
