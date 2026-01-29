#!/usr/bin/env python3
"""
Auto-wrap listening sections with ::: cdlisteningsection divs
"""
import re
from pathlib import Path

def wrap_listening_sections(filepath):
    """Wrap each section (## SECTION X ... ## Phần X) in cdlisteningsection div"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all SECTION patterns
    # Pattern: ## SECTION X ... (everything until next ## SECTION or end of analysis sections)
    sections = []
    lines = content.split('\n')
    
    i = 0
    output_lines = []
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a SECTION header
        if re.match(r'^## SECTION \d+', line):
            # Start of a section - find the end
            section_start = i
            i += 1
            
            # Find the end: either next SECTION, or after the corresponding "Phần" analysis
            # Look for "## Phần X: Section Y" that matches this section number
            section_num_match = re.search(r'SECTION (\d+)', lines[section_start])
            if section_num_match:
                section_num = section_num_match.group(1)
                
                # Find corresponding analysis section
                analysis_pattern = rf'^## Phần {section_num}:'
                found_analysis = False
                analysis_end = i
                
                while i < len(lines):
                    if re.match(analysis_pattern, lines[i]):
                        found_analysis = True
                        i += 1
                        # Continue until next "## Phần" or "## SECTION" or special sections
                        while i < len(lines):
                            if (re.match(r'^## (SECTION|Phần \d+:|Lời giải|Lời băng)', lines[i])):
                                analysis_end = i
                                break
                            i += 1
                        break
                    elif re.match(r'^## (SECTION|Phần \d+:|Lời giải|Lời băng)', lines[i]):
                        # Hit another section without finding analysis
                        analysis_end = i
                        break
                    i += 1
                
                # Wrap this section
                output_lines.append('::: cdlisteningsection')
                output_lines.append('')
                output_lines.extend(lines[section_start:analysis_end])
                output_lines.append('')
                output_lines.append(':::')
                output_lines.append('')
                
                # Don't increment i, we're already at the right position
                continue
        
        # Not a section header, just add the line
        output_lines.append(line)
        i += 1
    
    # Write back
    new_content = '\n'.join(output_lines)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Wrapped sections in {filepath}")

if __name__ == '__main__':
    files = [
        Path("/Users/lap15116/Desktop/TheForumPrj/chuyenDe/LS/md/rawls7/Listening/Level1/W8.md"),
        Path("/Users/lap15116/Desktop/TheForumPrj/chuyenDe/LS/md/rawls7/Listening/Level2/W8.md"),
        Path("/Users/lap15116/Desktop/TheForumPrj/chuyenDe/LS/md/rawls7/Listening/Level3/W8.md"),
    ]
    
    for f in files:
        if f.exists():
            wrap_listening_sections(f)
        else:
            print(f"File not found: {f}")
    
    print("\n✅ All files wrapped!")
