#!/usr/bin/env python3
"""Count total actual braces (not lines) in the file."""

with open('d:\\multiagent-productivity-assist\\frontend\\app.js', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Count individual brace characters
open_count = content.count('{')    
close_count = content.count('}')

print(f"Total brace characters in file:")
print(f"  Opening braces '{{': {open_count}")
print(f"  Closing braces '}}': {close_count}")
print(f"  Difference: {close_count - open_count} (extra closes)")

# Also count... lines with braces (what PowerShell counted)
lines = content.split('\n')
lines_with_open = sum(1 for line in lines if '{' in line)
lines_with_close = sum(1 for line in lines if '}' in line)

print(f"\nLines containing braces (what PowerShell's Select-String counted):")
print(f"  Lines with '{{': {lines_with_open}")
print(f"  Lines with '}}': {lines_with_close}")

# Count lines with MULTIPLE braces
multi_open_lines = [(i+1, line.count('{'), line) for i, line in enumerate(lines) if line.count('{') > 1]
multi_close_lines = [(i+1, line.count('}'), line) for i, line in enumerate(lines) if line.count('}') > 1]

print(f"\nLines with MULTIPLE opening braces ({len(multi_open_lines)} lines):")
for line_num, count, line in multi_open_lines[:10]:
    print(f"  Line {line_num}: {count} braces | {line[:60]}")

print(f"\nLines with MULTIPLE closing braces ({len(multi_close_lines)} lines):")
for line_num, count, line in multi_close_lines[:10]:
    print(f"  Line{line_num}: {count} braces | {line[:60]}")
