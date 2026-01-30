#!/usr/bin/env python3
"""
Convert listening transcript to 2-column table format
ONLY if dialogue (2+ speakers detected)
Use bold text for section headers instead of ### headings
"""
import re
from pathlib import Path

def detect_speakers(lines, start_idx, end_idx):
    """Detect unique speakers in a section"""
    speakers = set()
    for i in range(start_idx, end_idx):
        match = re.match(r'^([A-Z\s]+):\s+', lines[i])
        if match:
            speaker = match.group(1).strip()
            speakers.add(speaker)
    return speakers

def convert_transcript_to_table(filepath):
    """Convert transcript section to table format ONLY if dialogue"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    output_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if entering transcript section
        if re.match(r'^## Phần \d+: Lời băng', line):
            output_lines.append(line)
            i += 1
            # Process subsections
            while i < len(lines):
                # Check for ### SECTION X heading
                if re.match(r'^### SECTION \d+', lines[i]):
                    section_match = re.match(r'^### (SECTION \d+)', lines[i])
                    section_title = section_match.group(1)
                    section_start = i + 1
                    
                    # Find end of this section
                    section_end = section_start
                    while section_end < len(lines):
                        if re.match(r'^(###|##)', lines[section_end]):
                            break
                        section_end += 1
                    
                    # Detect speakers
                    speakers = detect_speakers(lines, section_start, section_end)
                    
                    # Only convert to table if 2+ speakers (dialogue)
                    if len(speakers) >= 2:
                        # DIALOGUE - convert to table with BOLD header
                        output_lines.append('')
                        output_lines.append(section_title)  # Plain text, no formatting
                        output_lines.append('')
                        output_lines.append('::: cdtranscripttable')
                        output_lines.append('')
                        output_lines.append('| Speaker | Dialogue |')
                        output_lines.append('|---------|----------|')
                        
                        # Convert dialogue lines
                        for j in range(section_start, section_end):
                            match = re.match(r'^([A-Z\s]+):\s+(.+)$', lines[j])
                            if match:
                                speaker = match.group(1).strip()
                                dialogue = match.group(2).strip()
                                output_lines.append(f'| {speaker} | {dialogue} |')
                            elif lines[j].strip() == '':
                                # Skip empty lines
                                pass
                            else:
                                # Continuation line - add to previous dialogue
                                if output_lines and output_lines[-1].startswith('|'):
                                    output_lines[-1] = output_lines[-1].rstrip('| ').rstrip() + ' ' + lines[j].strip() + ' |'
                        
                        output_lines.append('')
                        output_lines.append(':::')
                    else:
                        # MONOLOGUE - keep plain text with plain header
                        output_lines.append('')
                        output_lines.append(section_title)  # Plain text, no formatting
                        output_lines.extend(lines[section_start:section_end])
                    
                    i = section_end
                    continue
                
                # Check if leaving transcript
                if re.match(r'^## (?!SECTION)', lines[i]):
                    output_lines.append(lines[i])
                    i += 1
                    break
                
                output_lines.append(lines[i])
                i += 1
            continue
        
        output_lines.append(line)
        i += 1
    
    # Write back
    new_content = '\n'.join(output_lines)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Processed transcript in {filepath}")

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
    
    print("\n✅ All transcripts processed!")
