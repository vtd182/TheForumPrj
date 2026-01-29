#!/usr/bin/env python3
"""
Close transcript table divs
"""
import re
from pathlib import Path

def close_transcript_divs(filepath):
    """Add closing ::: for transcript tables"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple approach: find lines starting with ::: cdtranscripttable that don't have closing :::
    lines = content.split('\n')
    output = []
    in_transcript_table = False
    
    for i, line in enumerate(lines):
        if line.strip() == '::: cdtranscripttable':
            in_transcript_table = True
            output.append(line)
        elif in_transcript_table and line.strip().startswith(':::') and 'cdtranscripttable' not in line:
            # Already has closing
            in_transcript_table = False
            output.append(line)
        elif in_transcript_table:
            # Check if we hit a new section (## level heading not inside table)
            if re.match(r'^## ', line) and not line.startswith('|'):
                # Close the div before this heading
                output.append('')
                output.append(':::')
                output.append('')
                in_transcript_table = False
                output.append(line)
            else:
                output.append(line)
        else:
            output.append(line)
    
    # Close if still open at end
    if in_transcript_table:
        output.append('')
        output.append(':::')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output))
    
    print(f"Closed divs in {filepath}")

if __name__ == '__main__':
    files = [
        Path("/Users/lap15116/Desktop/TheForumPrj/chuyenDe/LS/md/rawls7/Listening/Level1/W8.md"),
        Path("/Users/lap15116/Desktop/TheForumPrj/chuyenDe/LS/md/rawls7/Listening/Level2/W8.md"),
        Path("/Users/lap15116/Desktop/TheForumPrj/chuyenDe/LS/md/rawls7/Listening/Level3/W8.md"),
    ]
    
    for f in files:
        if f.exists():
            close_transcript_divs(f)
    
    print("\n✅ All divs closed!")
