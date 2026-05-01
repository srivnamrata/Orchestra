// Activity feed — generative UI support. No external imports; other modules depend on this.
export const activityFeed = {
    log(message, type = 'info', agent = 'SYSTEM', widget = null) {
        const feed = document.getElementById('feed');
        if (!feed) return;

        const entryWrapper = document.createElement('div');
        entryWrapper.className = 'feed-entry-wrapper';

        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const colors = {
            info:    { main: 'var(--g-blue)',  bg: 'var(--g-blue-light)' },
            success: { main: 'var(--g-green)', bg: 'var(--g-green-light)' },
            warning: { main: 'var(--g-amber)', bg: 'var(--g-amber-light)' },
            error:   { main: 'var(--g-red)',   bg: 'var(--g-red-light)' },
            status:  { main: 'var(--g-teal)',  bg: 'var(--g-teal-light)' },
            user:    { main: 'var(--md-on-surface)', bg: 'var(--md-surface-2)' },
        };
        const c = colors[type] || colors.info;

        let contentHtml = `<div class="f-text">${message}</div>`;
        if (widget?.sources) contentHtml += this.renderProvenance(widget.sources);
        if (widget)          contentHtml += `<div class="f-widget">${this.renderWidget(widget)}</div>`;

        entryWrapper.innerHTML = `
            <div class="feed-entry stream-new">
                <div class="f-time">${timestamp}</div>
                <div class="f-body">
                    <div class="f-agent" style="color:${c.main};background:${c.bg};border:1px solid ${c.main}33">
                        ${agent.toUpperCase()}
                    </div>
                    ${contentHtml}
                    <div class="f-feedback-row">
                        <span class="fb-label">Helpful?</span>
                        <button class="fb-btn up" onclick="submitFeedback(this,'up')">
                            <span class="ms">thumb_up</span>
                            <span class="fb-count">0</span>
                        </button>
                        <button class="fb-btn down" onclick="submitFeedback(this,'down')">
                            <span class="ms">thumb_down</span>
                            <span class="fb-count">0</span>
                        </button>
                    </div>
                </div>
                <div class="f-explain-icon">🧠</div>
            </div>`;
        feed.prepend(entryWrapper);
        while (feed.children.length > 50) feed.removeChild(feed.lastElementChild);
    },

    renderWidget(w) {
        if (w.type === 'progress-table') {
            return `
                <div class="gen-widget table-widget">
                    <table>
                        <thead><tr><th>Project</th><th>Status</th><th>Health</th></tr></thead>
                        <tbody>${(w.data || []).map(r => `
                            <tr>
                                <td>${r.name}</td>
                                <td><span class="chip" style="background:${r.color}22;color:${r.color}">${r.status}</span></td>
                                <td><div style="width:100%;height:4px;background:var(--md-surface-3);border-radius:4px"><div style="width:${r.pct}%;height:100%;background:${r.color};border-radius:4px"></div></div></td>
                            </tr>`).join('')}
                        </tbody>
                    </table>
                    <div class="export-group" style="margin-top:10px;display:flex;gap:8px">
                        <button class="export-btn" onclick="activityFeed.log('Pushing to Jira...','status','SYSTEM')">Push to Jira</button>
                        <button class="export-btn" onclick="exportTasks('csv',${JSON.stringify(w.data).replace(/"/g,'&quot;')})">CSV</button>
                        <button class="export-btn" onclick="exportTasks('json',${JSON.stringify(w.data).replace(/"/g,'&quot;')})">JSON</button>
                    </div>
                </div>`;
        }
        if (w.type === 'action-card') {
            return `
                <div class="gen-widget card-widget" style="border-left:4px solid var(--g-blue)">
                    <div style="font-weight:700;margin-bottom:8px">${w.title}</div>
                    <div style="font-size:12px;color:var(--md-dim);margin-bottom:12px">${w.description}</div>
                    <div style="display:flex;gap:8px">
                        ${(w.actions||[]).map(a=>`<button class="na-btn primary" onclick="activityFeed.log('Triggered: ${a}','success','WIDGET')">${a}</button>`).join('')}
                    </div>
                </div>`;
        }
        if (w.type === 'debate-card') {
            return `
                <div class="debate-card">
                    <div class="debate-header">
                        <div class="debate-title">${w.title}</div>
                        <div class="consensus-badge" style="background:var(--g-blue-light);color:var(--g-blue);padding:4px 10px;border-radius:20px;font-size:10px;font-weight:800">
                            ${w.consensus}% Consensus
                        </div>
                    </div>
                    <div class="debate-body" style="padding:16px">
                        ${w.rounds.map(r=>`
                            <div class="debate-row" style="display:flex;gap:12px;margin-bottom:12px">
                                <div class="dr-avatar" style="width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;color:white;font-weight:800;background:${r.color}">${r.agent.charAt(0)}</div>
                                <div class="dr-content">
                                    <div class="dr-agent" style="font-weight:700;font-size:12px">${r.agent} <span class="vote-chip v-${r.vote.toLowerCase()}">${r.vote}</span></div>
                                    <div class="dr-pos" style="font-size:11px;color:var(--md-on-surface)">${r.message}</div>
                                </div>
                            </div>`).join('')}
                    </div>
                </div>`;
        }
        if (w.type === 'task-draft') {
            const draftId = `draft-${Math.random().toString(36).substr(2,5)}`;
            window[draftId] = w.tasks;
            return `
                <div class="draft-worksheet" id="${draftId}-container">
                    <div class="dw-head">
                        <div class="dw-title">${w.title}</div>
                        <span class="sc-tag">${w.tasks.length} Drafts</span>
                    </div>
                    <div class="dw-body">
                        ${w.tasks.map((t,idx)=>`
                            <div class="dw-row">
                                <div class="dw-check active" onclick="this.classList.toggle('active')"><span class="ms">check</span></div>
                                <div class="dw-info">
                                    <div class="dw-name">${t.title}</div>
                                    <div class="dw-meta">${t.priority.toUpperCase()} • ${t.due_date||'No Date'}</div>
                                </div>
                            </div>`).join('')}
                    </div>
                    <div class="dw-foot">
                        <button class="goal-run" style="width:100%" onclick="commitDraftTasks('${draftId}')">
                            <span class="ms sm">save</span> Commit to Task Workspace
                        </button>
                    </div>
                </div>`;
        }
        if (w.type === 'guru-audit') {
            return `
                <div class="guru-card anim a1">
                    <div class="guru-msg">"${w.message}"</div>
                    <div class="audit-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px">
                        ${['code','comm','eff'].map(k=>`
                            <div class="audit-item" style="text-align:center">
                                <div class="p-meter" style="height:80px;width:8px;background:var(--md-surface-3);border-radius:10px;margin:0 auto 12px;position:relative;overflow:hidden">
                                    <div class="p-fill" style="position:absolute;bottom:0;width:100%;background:var(--g-amber);border-radius:10px;height:${w.scores[k]}%"></div>
                                </div>
                                <div class="p-val" style="font-weight:800;font-size:14px">${w.scores[k]}%</div>
                                <div class="p-label" style="font-size:10px;font-weight:800;color:var(--md-dim)">${k.toUpperCase()}</div>
                            </div>`).join('')}
                    </div>
                    <div style="font-weight:700;font-size:12px;margin-bottom:12px;text-transform:uppercase;color:var(--md-dim);margin-top:24px">The Path to Mastery</div>
                    <div class="academy-grid" style="display:grid;grid-template-columns:1fr;gap:10px">
                        ${(w.trainings||[]).map(t=>`
                            <div class="academy-item" style="background:rgba(255,255,255,0.05);padding:12px;border-radius:12px;border:1px solid var(--md-surface-3)">
                                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                                    <div style="font-size:10px;font-weight:800;color:var(--g-amber);text-transform:uppercase">${t.category}</div>
                                    <span class="ms" style="font-size:14px;color:var(--md-dim)">school</span>
                                </div>
                                <div style="font-size:13px;font-weight:700;color:var(--md-on-surface);margin-bottom:2px">${t.topic}</div>
                                <div style="font-size:11px;color:var(--md-dim)">${t.benefit}</div>
                            </div>`).join('')}
                    </div>
                    <div style="margin-top:24px;padding:16px;background:var(--g-amber-light);border-radius:12px;border:1px solid var(--g-amber)">
                        <div style="font-weight:800;font-size:10px;color:var(--g-amber);text-transform:uppercase;margin-bottom:4px">Potential Unlock</div>
                        <div style="font-size:13px;font-weight:700;color:var(--md-on-surface)">${w.unlock}</div>
                    </div>
                </div>`;
        }
        return '';
    },

    renderProvenance(sources) {
        if (!sources?.length) return '';
        const typeMap = {
            slack:  { color: '#611f69', label: 'Slack' },
            github: { color: '#24292e', label: 'GitHub' },
            doc:    { color: 'var(--g-blue)', label: 'Doc' },
            metric: { color: 'var(--g-green)', label: 'Metric' },
        };
        const items = sources.map(s => {
            const t = typeMap[s.type] || typeMap.doc;
            return `<div class="prov-source">
                <div class="prov-source-icon" style="background:${t.color}">${t.label.charAt(0)}</div>
                <div class="ps-text"><strong>${t.label}</strong>: ${s.detail}</div>
            </div>`;
        }).join('');
        return `<div class="prov-container">
            <div class="prov-chip"><span class="ms">verified_user</span></div>
            <div class="prov-tooltip">
                <div class="prov-tooltip-title">Data Provenance</div>${items}
            </div>
        </div>`;
    },
};

// Expose for HTML onclick attributes (e.g. activityFeed.log(...))
window.activityFeed = activityFeed;
