import re

with open('/Users/Shared/Orchestra_refined/frontend/index.html', 'r') as f:
    content = f.read()

# 1. Remove "3" from Agent Thought Trace
content = content.replace('<div class="usb-r-title"><span id="active-count">3</span> Agent Thought Trace</div>', '<div class="usb-r-title">Agent Thought Trace</div>')

# 2. Add Integrations next to Intelligence in the blue bar
intel_target = """      <!-- Left: Intelligence -->
      <div class="usb-reasoning intel-toggle-btn" onclick="toggleIntelOverlay(event)" style="border-radius: var(--radius-xl) 0 0 var(--radius-xl);">
        <div style="display:flex; align-items:center;">
          <div class="usb-r-icon">
            <span class="ms" style="color:white; font-size:22px;">hub</span>
          </div>
          <div class="usb-r-text">
            <div class="usb-r-title">Intelligence</div>
            <div class="usb-r-sub">News, Research & Tasks</div>
          </div>
        </div>
      </div>"""
intel_replacement = """      <!-- Left: Intelligence & Integrations -->
      <div class="usb-reasoning intel-toggle-btn" onclick="toggleIntelOverlay(event)" style="border-radius: var(--radius-xl) 0 0 var(--radius-xl); border-right: 1px solid rgba(255,255,255,0.15);">
        <div style="display:flex; align-items:center;">
          <div class="usb-r-icon">
            <span class="ms" style="color:white; font-size:22px;">hub</span>
          </div>
          <div class="usb-r-text">
            <div class="usb-r-title">Intelligence</div>
            <div class="usb-r-sub">News & Tasks</div>
          </div>
        </div>
      </div>
      <div class="usb-reasoning" onclick="window.location.href='/integrations'" style="border-radius: 0;">
        <div style="display:flex; align-items:center;">
          <div class="usb-r-icon">
            <span class="ms" style="color:white; font-size:22px;">extension</span>
          </div>
          <div class="usb-r-text">
            <div class="usb-r-title">Integrations</div>
            <div class="usb-r-sub">Active plugins</div>
          </div>
        </div>
      </div>"""
content = content.replace(intel_target, intel_replacement)

# 3. Quick Actions updates
sa_target = """  <!-- Quick Actions -->
  <div class="sidebar-actions">
    <div class="sa-label">Quick Actions</div>
    <button class="sa-btn" onclick="runDemo('critic')"><span class="ms">manage_search</span> Critic Replan</button>
    <button class="sa-btn" onclick="runDemo('scan')"><span class="ms">radar</span> Run Scan</button>
    <button class="sa-btn" onclick="runDemo('vibe')"><span class="ms">check_circle</span> Vibe Check</button>
    <button class="sa-btn" onclick="runDemo('debate')"><span class="ms">gavel</span> Agent Debate</button>
  </div>"""
sa_replacement = """  <!-- Quick Actions -->
  <div class="sidebar-actions">
    <div class="sa-label">Quick Actions</div>
    <button class="sa-btn" onclick="runDemo('critic')"><span class="ms">manage_search</span> Critic Replan</button>
    <button class="sa-btn" onclick="runDemo('scan')"><span class="ms">radar</span> Run Scan</button>
    <button class="sa-btn" onclick="runDemo('vibe')"><span class="ms">check_circle</span> Vibe Check</button>
    <button class="sa-btn" onclick="runDemo('debate')"><span class="ms">gavel</span> Agent Debate</button>
    <button class="sa-btn" onclick="runDemo('safety')"><span class="ms">shield</span> Safety Audit</button>
  </div>"""
content = content.replace(sa_target, sa_replacement)

# Update runDemo in JS to show modal
rundemo_target = """// Demo buttons
function runDemo(type){
  const msgs={vibe:{agent:'CRITIC',color:'var(--g-amber)',cbg:'var(--g-amber-light)',text:'Vibe Check started. Evaluating goal alignment across all active workflows…'},debate:{agent:'ORCHESTRATOR',color:'var(--g-green)',cbg:'var(--g-green-light)',text:'Debate initiated. Orchestrator vs Critic — arguing best strategy for UI Redesign…'},critic:{agent:'CRITIC',color:'var(--g-amber)',cbg:'var(--g-amber-light)',text:'Critic Replan running. Scanning for inefficiencies across workflow graph…'},scan:{agent:'AUDITOR',color:'var(--g-teal)',cbg:'var(--g-teal-light)',text:'Proactive scan started. Cross-referencing tasks, calendar, GitHub and email…'}};
  const m=msgs[type];if(!m)return;
  const n=new Date(),t=`${String(n.getHours()).padStart(2,'0')}:${String(n.getMinutes()).padStart(2,'0')}`;
  feedData.unshift({time:t,agent:m.agent,color:m.color,cbg:m.cbg,text:m.text,tag:'status'});feedFilter='all';document.querySelectorAll('.feed-tab').forEach((b,i)=>b.classList.toggle('active',i===0));renderFeed();
}"""

rundemo_replacement = """// Demo buttons / Quick actions
function runDemo(type){
  const titles = {
    vibe: "Vibe Check", debate: "Agent Debate", critic: "Critic Replan", scan: "Run Scan", safety: "Safety Audit"
  };
  const contents = {
    vibe: "This view would display the active vibe check across all orchestrator nodes. Evaluates goal alignment.",
    debate: "This view would stream live agent debate reasoning. Orchestrator vs Critic arguing best strategy.",
    critic: "This view would present the Critic Replan graph optimization.",
    scan: "This view would show proactive scans across integrations.",
    safety: "This view would list flagged PII and ethics audits."
  };
  const dialog = document.getElementById('quickActionModal');
  document.getElementById('qaTitle').textContent = titles[type];
  document.getElementById('qaContent').textContent = contents[type];
  dialog.showModal();
}"""
content = content.replace(rundemo_target, rundemo_replacement)

# Add <dialog> before closing </main>
dialog_html = """  <dialog id="quickActionModal" style="padding: 24px; border: 1px solid var(--md-surface-2); border-radius: var(--radius-xl); background: var(--md-surface); box-shadow: var(--shadow-3); width: 400px; max-width: 90vw; color: var(--md-on-surface);">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 16px;">
      <div id="qaTitle" style="font-family: var(--font-display); font-size: 18px; font-weight: 700;">Action</div>
      <button onclick="document.getElementById('quickActionModal').close()" style="background: none; border: none; cursor: pointer; color: var(--md-muted);"><span class="ms">close</span></button>
    </div>
    <div id="qaContent" style="color: var(--md-muted); font-size: 14px; line-height: 1.5;">
      Loading interactive view...
    </div>
    <div style="margin-top: 24px; display: flex; justify-content: flex-end;">
      <button class="tb-btn primary" onclick="document.getElementById('quickActionModal').close()">Close</button>
    </div>
  </dialog>
"""
content = content.replace("</main>", dialog_html + "</main>")

# 4. Remove Intelligence and Integrations from left, move Bottlenecks
nav_target = re.search(r'(    <div class="nav-label">Intelligence</div>\n    <div class="nav-item".*?    <div class="nav-item"><span class="ms">mail</span> Email <span class="nav-badge nb-gray">stub</span></div>)', content, re.DOTALL)

bottlenecks_target = re.search(r'(        <!-- Silent Bottlenecks -->\n        <div class="trace-card">\n          <div class="bottlenecks-section".*?\n            </div>\n          </div>\n        </div>)', content, re.DOTALL)

if nav_target and bottlenecks_target:
    # First remove bottlenecks from its original place
    content = content.replace(bottlenecks_target.group(1), "")
    
    # We will strip the "trace-card" container from bottlenecks to fit better in sidebar
    bottlenecks_inner = bottlenecks_target.group(1).replace('<div class="trace-card">\n          ', '').replace('        </div>\n', '')
    # Wrap it nicely for sidebar
    bottlenecks_styled = bottlenecks_inner.replace('<div class="bottlenecks-section" id="bottlenecks">', '<div class="bottlenecks-section" id="bottlenecks" style="margin: 12px 10px; padding: 12px; background: var(--md-surface-1); border-radius: var(--radius-md); border: 1px solid var(--md-surface-2);">')
    
    # Replace nav_target with the bottlenecks block
    content = content.replace(nav_target.group(1), bottlenecks_styled)

with open('/Users/Shared/Orchestra_refined/frontend/index.html', 'w') as f:
    f.write(content)

print("Updated index.html")
