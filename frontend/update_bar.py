import re

with open('/Users/Shared/Orchestra_refined/frontend/index.html', 'r') as f:
    content = f.read()

# 1. Update unified-stats-bar
bar_target = re.search(r'(<div class="unified-stats-bar anim a2">.*?</div>\n    </div>)', content, re.DOTALL)
if bar_target:
    bar_replacement = """<div class="unified-stats-bar anim a2">
      <!-- Left: Intelligence -->
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
      </div>
      
      <div class="usb-divider"></div>

      <!-- Middle: Analytics -->
      <div class="usb-analytics">
        <div class="usb-stat" onclick="window.location.href='/analytics'">
          <div class="usb-num">247</div>
          <div class="usb-lbl">Tasks Completed</div>
        </div>
        <div class="usb-stat" onclick="window.location.href='/analytics'">
          <div class="usb-num">83h</div>
          <div class="usb-lbl">Time Saved</div>
        </div>
      </div>
      
      <div class="usb-divider"></div>

      <!-- Right: Active Workflow & Agent Reasoning -->
      <div class="usb-reasoning" onclick="window.location.href='/trace'" style="border-radius: 0 var(--radius-xl) var(--radius-xl) 0;">
        <div style="display:flex; align-items:center;">
          <div class="usb-r-icon">
            <span class="ms" style="color:white; font-size:22px;">psychology</span>
          </div>
          <div class="usb-r-text">
            <div class="usb-r-title"><span id="active-count">3</span> Agent Thought Trace</div>
            <div class="usb-r-sub">Click to view real-time Agent Reasoning</div>
          </div>
        </div>
        <span class="ms" style="color:rgba(255,255,255,0.6); font-size:24px;">chevron_right</span>
      </div>
    </div>"""
    content = content.replace(bar_target.group(1), bar_replacement)
else:
    print("Could not find unified-stats-bar")

# 2. Update toggleIntelOverlay function
js_target = """function toggleIntelOverlay(e) {
  if (e) e.stopPropagation();
  const intelPanel = document.getElementById('intel-panel');
  const feedCard = document.getElementById('feed-card');
  if (intelPanel.classList.contains('overlay-active')) {
    intelPanel.classList.remove('overlay-active');
    intelPanel.style.display = 'none';
    feedCard.style.opacity = '1';
    feedCard.style.pointerEvents = 'auto';
  } else {
    intelPanel.classList.add('overlay-active');
    intelPanel.style.display = 'block';
    feedCard.style.opacity = '0';
    feedCard.style.pointerEvents = 'none';
  }
}"""

js_replacement = """function toggleIntelOverlay(e) {
  if (e) e.stopPropagation();
  const intelPanel = document.getElementById('intel-panel');
  const feedCard = document.getElementById('feed-card');
  if (intelPanel.classList.contains('overlay-active')) {
    intelPanel.classList.remove('overlay-active');
    intelPanel.style.display = 'none';
    intelPanel.style.position = 'absolute';
    feedCard.style.display = 'block';
  } else {
    intelPanel.classList.add('overlay-active');
    intelPanel.style.display = 'block';
    intelPanel.style.position = 'relative'; // Push content down instead of absolute overlay
    feedCard.style.display = 'none';
  }
}"""

content = content.replace(js_target, js_replacement)

# Also remove transition opacity on feed-card since we are using display none/block
content = content.replace('<div class="feed-card" id="feed-card" style="transition: opacity 0.3s;">', '<div class="feed-card" id="feed-card">')

with open('/Users/Shared/Orchestra_refined/frontend/index.html', 'w') as f:
    f.write(content)
print("Updated successfully")
