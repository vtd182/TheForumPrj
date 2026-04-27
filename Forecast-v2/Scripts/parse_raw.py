import re
import os
import sys

def parse_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = re.split(r'# PART 2 & PART 3: CUE CARDS', content)
    part1_raw = parts[0]
    part2_3_raw = parts[1] if len(parts) > 1 else ""

    part1_sections = []
    current_topic = None
    current_questions = []

    def flush_part1_topic():
        nonlocal current_topic, current_questions
        if current_topic and current_questions:
            part1_sections.append({
                'topic': current_topic,
                'questions': current_questions
            })
        current_topic = None
        current_questions = []

    for raw_line in part1_raw.splitlines():
        line = raw_line.strip()

        category_match = re.match(r'^#\s+(PART 1:\s+.+)$', line, re.IGNORECASE)
        if category_match:
            flush_part1_topic()
            part1_sections.append({
                'type': 'category',
                'title': category_match.group(1).strip()
            })
            continue

        topic_match = re.match(r'^##\s+(.+)$', line)
        if topic_match:
            flush_part1_topic()
            current_topic = topic_match.group(1).strip()
            continue

        if current_topic and (line.startswith('> -') or line.startswith('>-')):
            q = re.sub(r'^>\s*-\s*', '', line).strip()
            current_questions.append(q)

    flush_part1_topic()

    part2_3_sections = []
    p2_3_chunks = re.split(r'\n##\s+', '\n' + part2_3_raw)
    for chunk in p2_3_chunks:
        if not chunk.strip() or chunk.strip().startswith('# PART 2'):
            continue
            
        lines = chunk.strip().split('\n')
        topic_name = lines[0].strip()
        
        cue_card_lines = []
        discussion_qs = []
        
        mode = "none"
        for line in lines[1:]:
            clean_line = line.strip()
            if "[!prompt]" in clean_line or "Cue Card" in clean_line:
                mode = "cuecard"
                continue
            elif "[!question]" in clean_line or "Discussion" in clean_line:
                mode = "discussion"
                continue
                
            if mode == "cuecard":
                if clean_line.startswith('>'):
                    cue_card_lines.append(clean_line.lstrip('>').strip())
            elif mode == "discussion":
                if clean_line.startswith('>'):
                    d_line = clean_line.lstrip('>').strip()
                    if d_line:
                        discussion_qs.append(d_line)
        
        questions = []
        if cue_card_lines:
            questions.append({
                "type": "cuecard",
                "title": "Part 2: Cue Card",
                "body": "\n".join(cue_card_lines)
            })
            
        for dq in discussion_qs:
            questions.append({
                "type": "discussion",
                "title": dq,
                "body": ""
            })
                
        if questions:
            part2_3_sections.append({
                'topic': topic_name,
                'questions': questions
            })
            
    return part1_sections, part2_3_sections

def generate_template(data, outpath, version="forum", is_part23=False):
    with open(outpath, 'w', encoding='utf-8') as f:
        for sec in data:
            if sec.get('type') == 'category':
                f.write(f"# {sec['title']}\n\n")
                continue

            f.write(f"## {sec['topic']}\n\n")
            for q in sec['questions']:
                if isinstance(q, dict):
                    # It's Part 2/3
                    f.write(f"### {q['title']}\n")
                    if q['body']:
                        f.write(f"{q['body']}\n\n")
                    else:
                        f.write("\n")
                else:
                    # It's Part 1 string
                    f.write(f"### {q}\n\n")
                    
                if version == "forum":
                    f.write("**Sample 1: Học sinh / Sinh viên**\n\n[Nhập câu trả lời vào đây]\n\n")
                    f.write("**Vocabulary:**\n- **word** (/pron/): Nghĩa\n\n")
                    f.write("**Sample 2: Người đi làm**\n\n[Nhập câu trả lời vào đây]\n\n")
                    f.write("**Vocabulary:**\n- **word** (/pron/): Nghĩa\n\n")
                elif version == "public":
                    f.write("**Sample 1: Học sinh / Sinh viên**\n\n[Nhập câu trả lời vào đây]\n\n")
                    f.write("**Vocabulary:**\n- **word** (/pron/): Nghĩa\n\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_raw.py <path_to_raw_markdown>")
        sys.exit(1)

    raw_md_path = os.path.abspath(sys.argv[1])
    if not os.path.exists(raw_md_path):
        print(f"Error: {raw_md_path} does not exist.")
        sys.exit(1)
        
    filename = os.path.basename(raw_md_path)
    forecast_name = os.path.splitext(filename)[0]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Run parsing
    p1, p23 = parse_markdown(raw_md_path)
    
    versions = ["forum", "public"]
    for v in versions:
        outdir = os.path.join(project_root, "Data", forecast_name, v)
        os.makedirs(outdir, exist_ok=True)
        
        part1_out = os.path.join(outdir, "answered_part1.md")
        part2_3_out = os.path.join(outdir, "answered_part2_3.md")
        
        # Note: If file exists, we don't want to overwrite and destroy answered data!
        if not os.path.exists(part1_out):
            generate_template(p1, part1_out, version=v)
            print(f"Created {part1_out}")
        else:
            print(f"Skipped {part1_out} (already exists)")
            
        if not os.path.exists(part2_3_out):
            generate_template(p23, part2_3_out, version=v)
            print(f"Created {part2_3_out}")
        else:
            print(f"Skipped {part2_3_out} (already exists)")
