import re

with open('/Users/Shared/Orchestra_refined/frontend/trace.html', 'r') as f:
    content = f.read()

# 1. Remove Replay button and add Active Workflows Only
tb_right_target = """  <div class="tb-right">
    <button class="tb-btn" onclick="exportTrace()"><span class="ms sm">download</span> Export</button>
    <button class="tb-btn" onclick="replayTrace()"><span class="ms sm">replay</span> Replay</button>
    <button class="theme-toggle" onclick="toggleTheme()">"""
    
tb_right_replacement = """  <div class="tb-right">
    <button class="tb-btn" onclick="exportTrace()"><span class="ms sm">download</span> Export</button>
    <button class="tb-btn" onclick="filterTl('active')"><span class="ms sm">filter_list</span> Active Workflows Only</button>
    <button class="theme-toggle" onclick="toggleTheme()">"""

if tb_right_target in content:
    content = content.replace(tb_right_target, tb_right_replacement)

# 2. Add some seed data to EVENTS so it's not completely blank
events_target = "const EVENTS = [];"
events_replacement = """const EVENTS = [
  { id:'lv1', time:'09:00', agent:'orchestrator', type:'decision', title:'Initialize workflow', detail:'Received user prompt: API Documentation', tags:['trigger'], reasoning:['Parsed prompt', 'Identified requirements'], input:'API Documentation', output:'Workflow plan', handoffTo:'planner', decision:'Route to Planner' },
  { id:'lv2', time:'09:01', agent:'planner', type:'task', title:'Decompose task', detail:'Broke down API documentation into 3 subtasks', tags:['planning'], reasoning:['Analyzed endpoints', 'Created draft structure'], input:'Workflow plan', output:'3 Subtasks', handoffTo:'researcher', decision:'Hand off to Researcher' },
  { id:'lv3', time:'09:03', agent:'researcher', type:'task', title:'Gather specs', detail:'Searched codebase for endpoint definitions', tags:['search'], reasoning:['Found 12 endpoints', 'Extracted parameters'], input:'3 Subtasks', output:'Raw specs', handoffTo:'writer', decision:'Hand off to Writer' },
  { id:'lv4', time:'09:05', agent:'writer', type:'task', title:'Draft documentation', detail:'Writing OpenAPI swagger docs', tags:['drafting', 'live'], reasoning:['Formatting paths', 'Adding descriptions'], input:'Raw specs', output:'Draft docs', handoffTo:null, decision:'Working...' }
];"""
content = content.replace(events_target, events_replacement)

with open('/Users/Shared/Orchestra_refined/frontend/trace.html', 'w') as f:
    f.write(content)

print("Updated trace.html")
