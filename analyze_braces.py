#!/usr/bin/env python3
"""Analyze JavaScript file for unbalanced braces."""

with open('d:\\multiagent-productivity-assist\\frontend\\app.js', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find lines that have only closing braces or end a function
suspicious = []
for i, line in enumerate(lines):
    stripped = line.strip()
    # Check for lines that are just closing braces (possibly with semicolon)
    if stripped in ['}', '});', '};', '},', '} }', '} );']:
        suspicious.append((i+1, stripped, line.rstrip()))

print(f"Found {len(suspicious)} lines with closing-brace-only patterns\n")
print("Lines with only closing braces:")
for line_num, pattern, content in suspicious[:50]:
    print(f"Line {line_num:4d}: {pattern:15s}")

# Now analyze function structure
print("\n\nAnalyzing function structure...")
opens = 0
closes = 0
balance = 0
detailed_issues = []

for i, line in enumerate(lines):
    lineOpens = line.count('{')
    lineCloses = line.count('}')
    opens += lineOpens
    closes += lineCloses
    prev_balance = balance
    balance = opens - closes
    
    # Look for places where balance becomes very negative or jumps unexpectedly
    if balance < prev_balance - 5 or (lineCloses > 2 and balance < -1):
        detailed_issues.append({
            'line': i + 1,
            'content': line.strip()[:100],
            'closes': lineCloses,
            'balance': balance
        })

print(f"\nTotal opens: {opens}, closes: {closes}, final balance: {balance}")
print(f"\nShowing lines where balance drops significantly:")
for issue in detailed_issues[:20]:
    print(f"Line {issue['line']}: balance={issue['balance']}, closes={issue['closes']} | {issue['content']}")
