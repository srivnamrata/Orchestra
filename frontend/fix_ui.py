import re

with open('/Users/Shared/Orchestra_refined/frontend/index.html', 'r') as f:
    content = f.read()

# 1. Enable Mic for goal input
mic_btn = '<button class="goal-mic" title="Voice input"><span class="ms sm">mic</span></button>'
mic_btn_new = '<button class="goal-mic" id="goalMicBtn" title="Voice input" onclick="toggleMic(this)"><span class="ms sm">mic</span></button>'
content = content.replace(mic_btn, mic_btn_new)

# 2. Club Tasks Completed and Time Saved vertically
analytics_old = """      <!-- Middle: Analytics -->
      <div class="usb-analytics">
        <div class="usb-stat" onclick="window.location.href='/analytics'">
          <div class="usb-num">247</div>
          <div class="usb-lbl">Tasks Completed</div>
        </div>
        <div class="usb-stat" onclick="window.location.href='/analytics'">
          <div class="usb-num">83h</div>
          <div class="usb-lbl">Time Saved</div>
        </div>
      </div>"""
analytics_new = """      <!-- Middle: Analytics -->
      <div class="usb-analytics" style="display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; padding:12px 0;">
        <div class="usb-stat" onclick="window.location.href='/analytics'" style="display:flex; flex-direction:row; align-items:baseline; gap:8px;">
          <div class="usb-num" style="font-size:20px;">247</div>
          <div class="usb-lbl" style="font-size:11px;">Tasks Completed</div>
        </div>
        <div class="usb-stat" onclick="window.location.href='/analytics'" style="display:flex; flex-direction:row; align-items:baseline; gap:8px;">
          <div class="usb-num" style="font-size:20px;">83h</div>
          <div class="usb-lbl" style="font-size:11px;">Time Saved</div>
        </div>
      </div>"""
content = content.replace(analytics_old, analytics_new)

# 3. All Tasks and Outputs
tasks_old = '<div class="nav-item"><span class="ms">task_alt</span> All Tasks <span class="nav-badge nb-gray">24</span></div>'
tasks_new = '<div class="nav-item" onclick="if(typeof triggerTaskDemo===\\\'function\\\') triggerTaskDemo(); else alert(\\\'Opening Tasks\\\');" style="cursor:pointer;"><span class="ms">task_alt</span> All Tasks <span class="nav-badge nb-gray">24</span></div>'
# wait, backslash escaping in python string literal
tasks_new = '<div class="nav-item" onclick="if(typeof triggerTaskDemo===\'function\') triggerTaskDemo(); else alert(\'Opening Tasks\');" style="cursor:pointer;"><span class="ms">task_alt</span> All Tasks <span class="nav-badge nb-gray">24</span></div>'
content = content.replace(tasks_old, tasks_new)

outputs_old = '<div class="nav-item"><span class="ms">folder_open</span> Outputs</div>'
outputs_new = '<div class="nav-item" onclick="if(typeof triggerResearchDemo===\'function\') triggerResearchDemo(); else alert(\'Opening Outputs\');" style="cursor:pointer;"><span class="ms">folder_open</span> Outputs</div>'
content = content.replace(outputs_old, outputs_new)

# 4. Agent Health Bottom Match
# I'll just set flex: 1 on agent-health-card to stretch it. Wait, I can do it via regex.
# Also the recent completions is feed-container, I'll ensure flex: 1
health_old = '        <!-- Agent Health -->\n        <div class="agent-health-card">'
health_new = '        <!-- Agent Health -->\n        <div class="agent-health-card" style="flex: 1; display: flex; flex-direction: column;">'
content = content.replace(health_old, health_new)

# Make ah-row container take flex 1
health_row_old = '          <div class="ah-row">'
# I'll let CSS handle it.

# 5. Modals JS Injection
# Replace playAudio() and runDemo() in the script tag
# Need to replace the whole runDemo function. Let's find it.

run_demo_regex = re.compile(r'// Demo buttons / Quick actions\nfunction runDemo\(type\)\{.*?\n\}', re.DOTALL)

run_demo_new = """// Demo buttons / Quick actions
function runDemo(type){
  const dialog = document.getElementById('quickActionModal');
  const title = document.getElementById('qaTitle');
  const content = document.getElementById('qaContent');
  
  if (type === 'debate') {
    dialog.style.width = '600px';
    title.innerHTML = '<span class="ms" style="vertical-align:middle;margin-right:8px;">forum</span> Live Agent Debates';
    content.innerHTML = `
      <div style="background:var(--md-surface-1); padding:16px; border-radius:8px; margin-top:12px; font-family:var(--font-mono); font-size:12px; color:#e0e0e0;">
        <div style="color:#ff5252; font-weight:bold; font-size:14px; margin-bottom:8px;">Debate ID: debate-ce717bb2</div>
        <div style="margin-bottom:4px;"><b>Subject:</b> Delete production database indices</div>
        <div style="margin-bottom:16px;"><b>Final Decision:</b> <span style="color:#4caf50;">✅ CONSENSUS REACHED (Team Confidence: 88%)</span></div>
        <div style="color:#888; margin-bottom:8px;">Full Summary:</div>
        <pre style="color:#82aaff; margin:0; overflow-x:auto;">{
  "debate_id": "debate-ce717bb2",
  "action": "Unknown",
  "issue": "High-stakes decision requiring team consensus",
  "consensus": true,
  "overall_confidence": "88%",
  "votes": {
    "support": 3,
    "conditional_support": 2,
    "concern": 0,
    "oppose": 0
  }
}</pre>
      </div>`;
  } else if (type === 'critic') {
    dialog.style.width = '700px';
    title.innerHTML = '<span class="ms" style="vertical-align:middle;margin-right:8px;">psychology</span> Workflow Analysis';
    content.innerHTML = `
      <div style="background:var(--md-surface-1); padding:16px; border-radius:8px; margin-top:12px;">
        <div style="color:#4fc3f7; font-weight:bold; margin-bottom:12px;">📊 Workflow Analysis Report</div>
        <div style="display:flex; gap:12px; margin-bottom:16px;">
          <div style="flex:1; background:var(--md-surface-2); padding:12px; border-radius:6px; border:1px solid #1e3a5f;">Total Tasks: 1</div>
          <div style="flex:1; background:var(--md-surface-2); padding:12px; border-radius:6px; border:1px solid #1e3a5f;">Priority Score: 2/5</div>
          <div style="flex:1; background:var(--md-surface-2); padding:12px; border-radius:6px; border:1px solid #1e3a5f;">Efficiency Score: 72%</div>
        </div>
        <div style="color:#ffb74d; font-weight:bold; margin-bottom:8px;">⚠️ Issues Detected (1):</div>
        <div style="background:rgba(255,82,82,0.1); padding:8px; border-radius:4px; margin-bottom:16px; border-left:3px solid #ff5252;">1. Task "dfds" has no due date - planning risk</div>
        <div style="color:#4caf50; font-weight:bold; margin-bottom:8px;">✅ Recommendations (1):</div>
        <div style="background:rgba(76,175,80,0.1); padding:8px; border-radius:4px; margin-bottom:16px; border-left:3px solid #4caf50;">1. Prioritize "dfds" - highest priority value</div>
        <div style="font-weight:bold; margin-bottom:8px;">📋 Task Breakdown:</div>
        <div style="background:var(--md-surface-2); padding:8px; border-radius:4px;">dfds <span style="color:#888; font-size:12px;">[medium] open</span></div>
        <div style="margin-top:16px; font-size:12px; color:#888;">✨ Critic Agent recommends optimizing task dependencies and prioritization for 20% efficiency gain.</div>
      </div>`;
  } else if (type === 'vibe') {
    dialog.style.width = '700px';
    title.innerHTML = '<span class="ms" style="vertical-align:middle;margin-right:8px;">shield</span> Vibe-Check Results';
    content.innerHTML = `
      <div style="background:var(--md-surface-1); padding:16px; border-radius:8px; margin-top:12px;">
        <div style="color:#4fc3f7; font-weight:bold; margin-bottom:12px;">🛡️ Safety & Alignment Report</div>
        <div style="display:flex; gap:12px; margin-bottom:16px;">
          <div style="flex:1; background:var(--md-surface-2); padding:16px; border-radius:6px; border:1px solid #1e5f3a;">
            <div style="color:#888; font-size:12px; margin-bottom:4px;">Safety Score:</div>
            <div style="color:#4caf50; font-size:24px; font-weight:bold;">95%</div>
          </div>
          <div style="flex:1; background:var(--md-surface-2); padding:16px; border-radius:6px; border:1px solid #1e3a5f;">
            <div style="color:#888; font-size:12px; margin-bottom:4px;">Goal Alignment:</div>
            <div style="color:#4fc3f7; font-size:24px; font-weight:bold;">88%</div>
          </div>
        </div>
        <div style="color:#4caf50; font-weight:bold; margin-bottom:16px;">✅ No Concerns Detected</div>
        <div style="color:#4caf50; font-weight:bold; margin-bottom:8px;">✅ Approved Items (0):</div>
        <div style="color:#888; font-size:13px; margin-bottom:16px;">All tasks evaluated for intent alignment and safety protocols.</div>
        <div style="font-size:12px; color:#aaa;">✨ Vibe-check complete. All agents are aligned with user goals and safety protocols are satisfied.</div>
      </div>`;
  } else {
    dialog.style.width = '400px';
    title.textContent = type.toUpperCase() + ' Action';
    content.textContent = "Action executed.";
  }
  dialog.showModal();
}

function toggleMic(btn) {
  if (btn.classList.contains('recording')) {
    btn.classList.remove('recording');
    btn.style.color = '';
    btn.style.animation = '';
    document.getElementById('goalInput').placeholder = "What would you like the Orchestra to orchestrate today?";
  } else {
    btn.classList.add('recording');
    btn.style.color = '#ff5252';
    btn.style.animation = 'pulse 1.5s infinite';
    document.getElementById('goalInput').placeholder = "Listening... Speak your goal.";
  }
}

function playAudio(){
  const btn = event.target.closest('button');
  if (btn.textContent.includes('Playing')) {
    window.speechSynthesis.cancel();
    btn.innerHTML = '<span class="ms sm">headphones</span> Audio Summary';
    return;
  }
  btn.innerHTML = '<span class="ms sm">equalizer</span> Playing…';
  
  const msg = new SpeechSynthesisUtterance("Welcome to your intelligence brief. You have 6 tasks completed, and 83 hours of time saved. System health is optimal, and all agents are active and aligned.");
  msg.rate = 1.05;
  msg.pitch = 1.0;
  msg.onend = () => {
    btn.innerHTML = '<span class="ms sm">headphones</span> Audio Summary';
  };
  window.speechSynthesis.speak(msg);
}"""

content = run_demo_regex.sub(run_demo_new, content)

# I should also replace the old playAudio if it existed outside the runDemo scope (it did)
old_play_audio_regex = re.compile(r'function playAudio\(\)\{const btn=event.target.closest\(\\\'button\\\'\);.*?\}', re.DOTALL)
# wait, playAudio was actually defined as:
# function playAudio(){const btn=event.target.closest('button');btn.textContent='⏸ Playing…';setTimeout(()=>btn.innerHTML='<span class="ms sm">headphones</span> Audio Summary',3000);}
content = re.sub(r"function playAudio\(\)\{const btn=event\.target\.closest\('button'\);.*?3000\);\}", "", content, flags=re.DOTALL)


with open('/Users/Shared/Orchestra_refined/frontend/index.html', 'w') as f:
    f.write(content)

print("UI Fixed.")
