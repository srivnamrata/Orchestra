import { activityFeed } from './feed.js';

let _scanRunning = false;

export async function runScan(btn) {
    if (_scanRunning) return;
    _scanRunning = true;
    const scanBtn  = btn || document.getElementById('runScanBtn');
    if (scanBtn) { scanBtn.disabled = true; scanBtn.innerHTML = '<span class="ms sm fa-spin">radar</span> Scanning…'; }
    const traceBody = document.getElementById('live-trace-body');
    const traceIdle = document.getElementById('traceIdle');
    const scanDot   = document.getElementById('scanDot');
    const scanLabel = document.getElementById('scanLabel');
    if (traceIdle) traceIdle.style.display = 'none';
    if (scanDot)   scanDot.className = 'scan-dot running';
    if (scanLabel) scanLabel.textContent = 'Scanning…';

    const append = (agent, msg, color = '#1a73e8') => {
        if (!traceBody) return;
        const line = document.createElement('div');
        line.className = 'trace-line';
        line.innerHTML = `<span class="tl-agent" style="color:${color}">${agent}</span><span class="tl-text">${msg}</span>`;
        traceBody.appendChild(line);
        traceBody.scrollTop = traceBody.scrollHeight;
    };

    activityFeed.log('📡 Intelligence Scan initiated…', 'status', 'SYSTEM');
    [
        { delay: 300,  agent: 'ORCHESTRATOR', msg: 'Starting cross-agent environment scan…',              color: '#1a73e8' },
        { delay: 900,  agent: 'CRITIC',        msg: 'Analysing task backlog for planning risks…',          color: '#e37400' },
        { delay: 1500, agent: 'RESEARCHER',    msg: 'Checking external signals (GitHub, Slack, Email)…',  color: '#1e8e3e' },
        { delay: 2100, agent: 'AUDITOR',       msg: 'Auditing cross-agent intent alignment…',             color: '#007b83' },
        { delay: 2800, agent: 'ORCHESTRATOR',  msg: '✅ Scan complete — bottlenecks surfaced in Intelligence Panel.', color: '#1a73e8' },
    ].forEach(s => setTimeout(() => { append(s.agent, s.msg, s.color); activityFeed.log(s.msg, 'info', s.agent); }, s.delay));

    setTimeout(() => {
        if (scanDot)   scanDot.className = 'scan-dot idle';
        if (scanLabel) scanLabel.textContent = 'Idle';
        if (scanBtn)   { scanBtn.disabled = false; scanBtn.innerHTML = '<span class="ms sm">radar</span> Run Scan'; }
        _scanRunning = false;
    }, 3200);
}

export function clearScan() {
    const body  = document.getElementById('live-trace-body');
    const idle  = document.getElementById('traceIdle');
    const dot   = document.getElementById('scanDot');
    const label = document.getElementById('scanLabel');
    if (body)  body.innerHTML = '';
    if (idle)  idle.style.display = '';
    if (dot)   dot.className = 'scan-dot idle';
    if (label) label.textContent = 'Idle';
}

export function switchTraceAgent(agent, btn) {
    document.querySelectorAll('.trace-tab').forEach(t => t.classList.remove('active'));
    if (btn) btn.classList.add('active');
    activityFeed.log(`Switched trace view to ${agent}`, 'info', 'SYSTEM');
}

export function dismissBn(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
}

export function reviewBn(btn, type) {
    activityFeed.log(`Reviewing ${type} bottleneck…`, 'status', type.toUpperCase());
    btn.closest('.bn-item').style.opacity = '0.5';
}

window.runScan          = runScan;
window.clearScan        = clearScan;
window.switchTraceAgent = switchTraceAgent;
window.dismissBn        = dismissBn;
window.reviewBn         = reviewBn;
