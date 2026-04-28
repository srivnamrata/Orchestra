// Pure DOM-rendering functions — no external module imports.

export function renderVibeCheck(data) {
    const list = document.getElementById('vibe-check-results');
    if (!list) return;
    list.innerHTML = (data.scenarios_tested || []).map(s => `
        <div class="run-card" style="margin-bottom:16px;border-left:4px solid ${s.approval_status==='APPROVED'?'var(--g-green)':'var(--g-red)'}">
            <div style="display:flex;justify-content:space-between;align-items:start">
                <div>
                    <div class="run-title">${s.name}</div>
                    <div style="display:flex;gap:8px;margin:8px 0">
                        <span class="chip" style="background:${s.approval_status==='APPROVED'?'var(--g-green-light)':'var(--g-red-light)'};color:${s.approval_status==='APPROVED'?'var(--g-green)':'var(--g-red)'}">${s.approval_status}</span>
                        <span class="chip" style="background:var(--md-surface-2)">Risk: ${s.risk_level}</span>
                    </div>
                    <p style="color:var(--md-on-surface);font-size:13px;line-height:1.4">${s.explanation}</p>
                </div>
                <div style="text-align:right">
                    <div style="font-size:24px;font-weight:700;color:${s.approval_status==='APPROVED'?'var(--g-green)':'var(--g-red)'}">${s.approval_status==='APPROVED'?'95%':'22%'}</div>
                    <div style="font-size:10px;color:var(--md-dim)">SAFETY SCORE</div>
                </div>
            </div>
        </div>`).join('');
}

export function renderDebate(data) {
    const list = document.getElementById('debate-list');
    if (!list) return;
    const summary = data.summary || {};
    list.innerHTML = `
        <div class="run-card" style="margin-bottom:16px">
            <div class="run-title" style="color:var(--g-violet)">Debate ID: ${data.debate_id}</div>
            <div style="margin:12px 0;font-size:18px;font-weight:600">${data.final_decision}</div>
            <div style="background:var(--md-surface-2);padding:16px;border-radius:12px;margin-bottom:16px">
                <div style="font-size:12px;color:var(--md-dim);margin-bottom:8px">ARGUMENT BREAKDOWN</div>
                <pre style="font-family:var(--font-mono);font-size:12px;color:var(--md-on-surface);white-space:pre-wrap">${JSON.stringify(summary.arguments||summary,null,2)}</pre>
            </div>
            <div style="display:flex;gap:12px">
                <div class="chip" style="background:var(--g-blue-light);color:var(--g-blue)">Consensus: ${summary.consensus_reached?'YES':'NO'}</div>
                <div class="chip" style="background:var(--g-green-light);color:var(--g-green)">Score: ${summary.confidence_score?(summary.confidence_score*100).toFixed(0)+'%':'N/A'}</div>
            </div>
        </div>`;
}

export function renderCriticAnalysis(data) {
    const wfList = document.getElementById('workflows-list');
    if (!wfList) return;
    wfList.innerHTML = `
        <div class="run-card" style="margin-bottom:16px;border-top:4px solid var(--g-amber)">
            <div class="run-title">Workflow Analysis Report</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:16px 0">
                <div style="background:var(--md-surface-2);padding:12px;border-radius:8px;text-align:center"><div style="font-size:20px;font-weight:700">1</div><div style="font-size:10px;color:var(--md-dim)">TOTAL TASKS</div></div>
                <div style="background:var(--md-surface-2);padding:12px;border-radius:8px;text-align:center"><div style="font-size:20px;font-weight:700">2/5</div><div style="font-size:10px;color:var(--md-dim)">PRIORITY SCORE</div></div>
                <div style="background:var(--md-surface-2);padding:12px;border-radius:8px;text-align:center"><div style="font-size:20px;font-weight:700">72%</div><div style="font-size:10px;color:var(--md-dim)">EFFICIENCY</div></div>
            </div>
            <div style="margin-bottom:12px"><div style="font-size:12px;color:var(--g-red);font-weight:600;margin-bottom:4px">⚠️ Issues Detected:</div><div style="font-size:13px;padding:8px;background:rgba(234,67,53,0.1);border-radius:6px;color:var(--md-on-surface)">Task "demo for client A" has no due date - planning risk</div></div>
            <div><div style="font-size:12px;color:var(--g-green);font-weight:600;margin-bottom:4px">✅ Recommendations:</div><div style="font-size:13px;padding:8px;background:rgba(52,168,83,0.1);border-radius:6px;color:var(--md-on-surface)">Prioritize "demo for client A" - highest priority value</div></div>
        </div>`;
}

export function renderNews(articles) {
    const pane = document.getElementById('pane-news');
    if (!pane) return;
    const srcColors = { 'hacker news':'#ff6600', hackernews:'#ff6600', 'dev.to':'#08090a', reddit:'#ff4500', arxiv:'var(--g-blue)' };
    const label = document.getElementById('news-source-label');
    if (label && articles.length) {
        const s = typeof articles[0].source==='object' ? articles[0].source.name : (articles[0].source||'News');
        label.textContent = `${s} · ${new Date().toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'})}`;
    }
    const grid = document.getElementById('hn-news-grid') || pane.querySelector('.news-grid');
    if (!grid) return;
    if (!articles.length) { grid.innerHTML = '<div class="empty-state">No news available.</div>'; return; }
    grid.innerHTML = articles.map(a => {
        const src      = typeof a.source==='object' ? (a.source.name||'News') : (a.source||'News');
        const color    = srcColors[src.toLowerCase()] || 'var(--g-amber)';
        const url      = (a.url||a.link||'#').replace(/'/g,'%27');
        const title    = (a.title||'').replace(/\\/g,'\\\\').replace(/'/g,"\\'").replace(/"/g,'&quot;');
        const score    = a.score ? `<span class="news-score">▲ ${a.score}</span>` : a.descendants!=null ? `<span class="news-score">💬 ${a.descendants}</span>` : '';
        return `
            <div class="news-card nc-hn">
                <div class="news-source-row"><div class="news-favicon" style="background:${color};color:white">${src.charAt(0).toUpperCase()}</div><span class="news-source-name">${src}</span><span class="news-date">${a.publishedAt?new Date(a.publishedAt).toLocaleDateString('en-GB',{day:'numeric',month:'short'}):''}</span></div>
                <div class="news-title">${a.title}</div>
                ${score?`<div class="news-meta">${score}</div>`:''}
                <div class="news-actions">
                    <button class="na-btn" onclick="playAudio('${title}')">🎧 Listen</button>
                    <button class="na-btn" onclick="window.open('${url}','_blank')">📖 Read</button>
                    <button class="na-btn" onclick="activityFeed.log('Article saved to Knowledge Graph','success','KNOWLEDGE')">🔖 Save</button>
                </div>
            </div>`;
    }).join('');
}

export function renderResearch(papers) {
    const pane = document.getElementById('pane-research');
    if (!pane) return;
    const label = document.getElementById('research-source-label');
    if (label) label.textContent = `arXiv · ${new Date().toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'})}`;
    const grid = document.getElementById('arxiv-research-grid') || pane.querySelector('.news-grid');
    if (!grid) return;
    if (!papers.length) { grid.innerHTML = '<div class="empty-state">No research papers found.</div>'; return; }
    grid.innerHTML = papers.map(p => {
        const title = (p.title||'').replace(/\\/g,'\\\\').replace(/'/g,"\\'");
        const url   = (p.url||'#').replace(/'/g,'%27');
        const cat   = p.primary_category||p.source||'arXiv';
        return `
            <div class="news-card nc-arxiv">
                <div class="news-source-row"><div class="news-favicon" style="background:var(--g-blue);color:white;font-size:8px;font-weight:800">aX</div><span class="news-source-name">${cat}</span></div>
                <div class="news-title">${p.title}</div>
                ${p.citation_count?`<div class="news-meta"><span class="news-score" style="color:var(--g-blue)">★ ${p.citation_count} citations</span></div>`:''}
                <div class="news-actions">
                    <button class="na-btn" onclick="playAudio('${title}')">🎧 Listen</button>
                    <button class="na-btn" onclick="window.open('${url}','_blank')">📖 View</button>
                    <button class="na-btn" onclick="activityFeed.log('Paper indexed in Knowledge Graph','success','KNOWLEDGE')">🔖 Save</button>
                </div>
            </div>`;
    }).join('');
}


export function renderTasks(tasks) {
    const html = (tasks||[]).map(t => {
        const done = t.status === 'done';
        return `<div class="task-intel-item">
            <div class="ti-check ${done?'done':''}">${done?'✓':''}</div>
            <div><div class="ti-title ${done?'done-text':''}">${t.title}</div><div style="display:flex;gap:6px;margin-top:4px"><span class="ti-priority">${t.priority||'med'}</span></div></div>
        </div>`;
    }).join('');
    const pane = document.getElementById('pane-tasks');
    const all  = document.getElementById('all-tasks-list');
    if (pane) pane.querySelector('.task-intel-grid').innerHTML = html;
    if (all)  all.innerHTML = html;
}

export function renderSchedule(events) {
    const pane = document.getElementById('pane-schedule');
    if (!pane) return;
    const grid = pane.querySelector('.schedule-grid');
    if (!grid) return;
    grid.innerHTML = (events||[]).map(ev => `
        <div class="sched-item">
            <div class="sched-time">${ev.start_time?ev.start_time.split('T')[1].slice(0,5):'--:--'}</div>
            <div><div class="sched-name">${ev.summary}</div><div class="sched-detail">${ev.location||'Remote'}</div></div>
        </div>`).join('');
}
