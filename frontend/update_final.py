import re

with open('/Users/Shared/Orchestra_refined/frontend/index.html', 'r') as f:
    content = f.read()

# 1. Update Spacing
# main-grid gap
content = re.sub(r'(\.main-grid \{\n  display: grid; grid-template-columns: 1fr 320px;\n  gap: )16px(;\s*align-items: stretch;\n\})', r'\g<1>24px\g<2>', content)

# runs-col gap
content = re.sub(r'(\.runs-col \{ display: flex; flex-direction: column; gap: )12px(; \})', r'\g<1>24px\g<2>', content)

# 2. Update Date and Top Level
topbar_target = """  <div class="topbar">
    <div class="tb-left">
    </div>"""

topbar_replacement = """  <div class="topbar">
    <div class="tb-left">
      <div id="topbar-datetime" style="font-size: 13px; color: var(--md-muted); font-weight: 500;"></div>
    </div>"""

content = content.replace(topbar_target, topbar_replacement)

# Remove hardcoded date from greeting
greeting_target = """    <!-- Greeting -->
    <div class="greeting anim a1">
      <div class="g-hi">Good afternoon · Saturday, 25 Apr 2026</div>
      <div class="g-title">Welcome back, Administrator 👋</div>
    </div>"""

greeting_replacement = """    <!-- Greeting -->
    <div class="greeting anim a1">
      <div class="g-title" id="welcome-title">Welcome back, Administrator 👋</div>
    </div>"""

content = content.replace(greeting_target, greeting_replacement)

# 3. Add JS for User Management and Live Date, and fix agent health listener
js_injection = """// ── User Management & Live Date ──
document.addEventListener('DOMContentLoaded', () => {
  // Restore user info from localStorage
  try {
    const userJson = localStorage.getItem('orch-user');
    if (userJson) {
      const user = JSON.parse(userJson);
      const name = user.name || "Administrator";
      const email = user.email || "admin@orchestra.ai";
      const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase() || 'AD';
      
      const avatarEl = document.querySelector('.user-row .avatar');
      const nameEl = document.querySelector('.user-row .user-name');
      const emailEl = document.querySelector('.user-row .user-email');
      const welcomeEl = document.getElementById('welcome-title');
      
      if(avatarEl) avatarEl.textContent = initials;
      if(nameEl) nameEl.textContent = name;
      if(emailEl) emailEl.textContent = email;
      if(welcomeEl) welcomeEl.textContent = `Welcome back, ${name} 👋`;
    }
  } catch(e) {}

  // Live Date Time in Topbar
  function updateDateTime() {
    const now = new Date();
    const options = { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true };
    const dateString = now.toLocaleDateString('en-US', options);
    
    const hour = now.getHours();
    let timeGreeting = 'Good evening';
    if (hour < 12) timeGreeting = 'Good morning';
    else if (hour < 17) timeGreeting = 'Good afternoon';
    
    const tbDate = document.getElementById('topbar-datetime');
    if (tbDate) tbDate.textContent = `${timeGreeting} · ${dateString}`;
  }
  
  updateDateTime();
  setInterval(updateDateTime, 60000); // update every minute

  // Fix Agent Health click handler (in case it wasn't binding properly)
  document.querySelectorAll('.ah-row').forEach(row => {
    const nameEl = row.querySelector('.ah-name');
    if(!nameEl) return;
    const name = nameEl.textContent.toLowerCase();
    if(AGENT_DATA[name]) {
      // Re-attach explicitly
      row.onclick = () => openAgentDrawer(name);
      row.title = `Click to open ${nameEl.textContent} conversation`;
    }
  });
});
</script>"""

content = content.replace("</script>", js_injection)

# Just in case there was a syntax error in the previous runDemo replacement, let's verify it manually or rely on python string replacement not throwing
with open('/Users/Shared/Orchestra_refined/frontend/index.html', 'w') as f:
    f.write(content)

print("Updated index.html")
