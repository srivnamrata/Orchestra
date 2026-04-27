import { apiUrl } from './api.js';
import { activityFeed } from './feed.js';

export async function runGuruAudit() {
    const container  = document.getElementById('guru-audit-container');
    const refreshBtn = document.getElementById('guru-refresh-btn');
    if (!container) return;
    if (refreshBtn) refreshBtn.disabled = true;

    container.innerHTML = `<div style="text-align:center;padding:40px;color:var(--md-dim);font-size:13px">
        <span class="ms" style="font-size:32px;display:block;margin-bottom:10px;color:var(--g-amber)">self_improvement</span>
        Param Mitra is reading your week…
    </div>`;

    try {
        const res  = await fetch(apiUrl('/api/guru/audit'), { method: 'POST' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (data.status !== 'success') throw new Error(data.message || 'Audit failed');
        const a = data.audit;

        const icon  = v => ({ great: '✅', good: '👍', needs_improvement: '⚠️' }[v] || '📊');
        const color = v => ({ great: 'var(--g-green)', good: 'var(--g-blue)', needs_improvement: 'var(--g-amber)' }[v] || 'var(--md-dim)');

        const card = (ico, icoColor, label, section) => {
            const s = section || {};
            const hasTrain = s.training && typeof s.training === 'object';
            return `
            <div class="run-card" style="border-top:3px solid ${color(s.assessment)}">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
                <span class="ms" style="font-size:20px;color:${icoColor}">${ico}</span>
                <div style="flex:1"><div style="font-weight:700;font-size:13px">${label}</div><div style="font-size:11px;color:var(--md-dim)">${icon(s.assessment)} ${(s.assessment||'reviewing').replace('_',' ')}</div></div>
              </div>
              <p style="font-size:12px;color:var(--md-on-surface);line-height:1.6;margin:0 0 10px">${s.insight||'Analysing…'}</p>
              ${hasTrain?`<div style="background:var(--g-amber-light);border:1px solid rgba(176,96,0,0.2);border-radius:10px;padding:10px 12px;font-size:11px">
                <div style="font-weight:700;color:var(--g-amber);margin-bottom:3px">📚 Suggested: ${s.training.topic}</div>
                <div style="color:var(--md-dim)">${s.training.why||''}</div>
                ${s.training.link_hint?`<div style="margin-top:4px;color:var(--g-blue);font-weight:600">${s.training.link_hint}</div>`:''}
              </div>`:''}
            </div>`;
        };

        container.innerHTML = `
          ${a.summary?`<div class="run-card" style="background:var(--g-amber-light);border:1px solid rgba(176,96,0,0.15);margin-bottom:16px;padding:14px 16px"><div style="font-size:13px;font-weight:600;color:var(--md-on-surface)">${a.summary}</div></div>`:''}
          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin-bottom:16px">
            ${card('code','var(--g-blue)','Code Quality',a.code)}
            ${card('mail','#7c3aed','Communication',a.communication)}
            ${card('task_alt','var(--g-green)','Efficiency',a.efficiency)}
          </div>
          ${a.cheer?`<div style="text-align:center;padding:16px;font-size:14px;font-weight:600;color:var(--g-amber)">🙏 ${a.cheer}</div>`:''}`;

        activityFeed.log(`Param Mitra: ${a.summary||'Weekly insights ready.'}`, 'success', 'PARAM_MITRA');
    } catch (e) {
        container.innerHTML = `<div class="run-card" style="text-align:center;padding:32px">
            <p style="color:var(--g-red);margin-bottom:16px">Could not load insights: ${e.message}</p>
            <button class="intel-btn" onclick="window.runGuruAudit()"><span class="ms sm">refresh</span> Retry</button>
        </div>`;
    } finally {
        if (refreshBtn) refreshBtn.disabled = false;
    }
}

window.runGuruAudit = runGuruAudit;
