import re

with open('/Users/Shared/Orchestra_refined/frontend/index.html', 'r') as f:
    content = f.read()

# 1. Add Intelligence stat in usb-analytics
analytics_target = """        <div class="usb-stat" onclick="window.location.href='/analytics'">
          <div class="usb-num">247</div>
          <div class="usb-lbl">Tasks Completed</div>
        </div>"""
analytics_replacement = """        <div class="usb-stat" onclick="window.location.href='/analytics'">
          <div class="usb-num">247</div>
          <div class="usb-lbl">Tasks Completed</div>
        </div>
        <div class="usb-stat intel-toggle-btn" onclick="toggleIntelOverlay(event)">
          <div class="usb-num"><span class="ms" style="font-size:26px">hub</span></div>
          <div class="usb-lbl">Intelligence</div>
        </div>"""
content = content.replace(analytics_target, analytics_replacement)

# 2. Extract intel-panel and remove it from bottom
intel_panel_match = re.search(r'(    <!-- Intelligence Panel -->\n    <div class="intel-panel anim a6">.*?\n    </div>\n)', content, re.DOTALL)
if intel_panel_match:
    intel_panel_html = intel_panel_match.group(1)
    # modify intel_panel_html to hide it and make it absolute
    intel_panel_html = intel_panel_html.replace('<div class="intel-panel anim a6">', '<div class="intel-panel" id="intel-panel" style="position: absolute; top: 0; left: 0; right: 0; display: none; z-index: 20; box-shadow: var(--shadow-3);">')
    
    # remove it from its original location
    content = content.replace(intel_panel_match.group(1), "")
    
    # 3. Wrap feed-card and insert intel-panel
    feed_card_target = """        <!-- Smart Activity Feed -->
        <div class="feed-card">"""
    
    feed_card_replacement = """        <!-- Smart Activity Feed Container -->
        <div class="feed-container" style="position: relative;">
          <!-- Smart Activity Feed -->
          <div class="feed-card" id="feed-card" style="transition: opacity 0.3s;">"""
          
    content = content.replace(feed_card_target, feed_card_replacement)
    
    feed_end_target = """          <div class="feed-body" id="feed"></div>
        </div>"""
        
    feed_end_replacement = """          <div class="feed-body" id="feed"></div>
        </div>
""" + intel_panel_html + """
        </div>"""
    
    content = content.replace(feed_end_target, feed_end_replacement)

# 4. Add JS functions at the end
js_to_add = """
// ── Intelligence Overlay Logic ──
function toggleIntelOverlay(e) {
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
}

document.addEventListener('click', (e) => {
  const intelPanel = document.getElementById('intel-panel');
  const toggleBtns = document.querySelectorAll('.intel-toggle-btn');
  
  if (intelPanel && intelPanel.classList.contains('overlay-active')) {
    let isToggleClick = false;
    toggleBtns.forEach(btn => {
      if (btn.contains(e.target)) isToggleClick = true;
    });
    
    if (!intelPanel.contains(e.target) && !isToggleClick) {
      toggleIntelOverlay();
    }
  }
});
</script>"""

content = content.replace("</script>", js_to_add)

with open('/Users/Shared/Orchestra_refined/frontend/index.html', 'w') as f:
    f.write(content)
print("Updated successfully")
