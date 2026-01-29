#!/usr/bin/env python3
"""
Convert listening transcript to 2-column table format
Speaker | Dialogue
With alternating row colors
"""
import re
from pathlib import Path

def convert_transcript_to_table(filepath):
    """Convert transcript section to table format"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find transcript section
    lines = content.split('\n')
    output_lines = []
    in_transcript = False
    current_section = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if entering transcript section
        if re.match(r'^## Phần \d+: Lời băng', line):
            output_lines.append(line)
            in_transcript = True
            i += 1
            continue
        
        # Check if this is a SECTION header within transcript
        if in_transcript and re.match(r'^### SECTION \d+', line):
            current_section = line
            output_lines.append('')
            output_lines.append(line)
            output_lines.append('')
            # Start table
            output_lines.append('::: cdtranscripttable')
            output_lines.append('')
            output_lines.append('| Speaker | Dialogue |')
            output_lines.append('|---------|----------|')
            i += 1
            continue
        
        # Check if leaving transcript (next major section)
        if in_transcript and (re.match(r'^## (?!SECTION)', line) or i == len(lines) - 1):
            # Close table if open
            if current_section:
                output_lines.append('')
                output_lines.append(':::')
                output_lines.append('')
                current_section = None
            in_transcript = False
            output_lines.append(line)
            i += 1
            continue
        
        # Process transcript dialogue lines
        if in_transcript and current_section:
            # Match pattern: SPEAKER:  dialogue
            match = re.match(r'^([A-Z\s]+):\s+(.+)$', line)
            if match:
                speaker = match.group(1).strip()
                dialogue = match.group(2).strip()
                output_lines.append(f'| {speaker} | {dialogue} |')
            elif line.strip() == '':
                # Empty line - skip
                pass
            else:
                # Continuation line - add to previous dialogue
                if output_lines and output_lines[-1].startswith('|'):
                    # Remove trailing |, add text, add back |
                    output_lines[-1] = output_lines[-1].rstrip('| ').rstrip() + ' ' + line.strip() + ' |'
        else:
            output_lines.append(line)
        
        i += 1
    
    # Write back
    new_content = '\n'.join(output_lines)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Converted transcript in {filepath}")

if __name__ == '__main__':
    files = [
        Path("/Users/lap15116/Desktop/TheForumPrj/chuyenDe/LS/md/rawls7/Listening/Level1/W8.md"),
        Path("/Users/lap15116/Desktop/TheForumPrj/chuyenDe/LS/md/rawls7/Listening/Level2/W8.md"),
        Path("/Users/lap15116/Desktop/TheForumPrj/chuyenDe/LS/md/rawls7/Listening/Level3/W8.md"),
    ]
    
    for f in files:
        if f.exists():
            convert_transcript_to_table(f)
        else:
            print(f"File not found: {f}")
    
    print("\n✅ All transcripts converted to table!")
