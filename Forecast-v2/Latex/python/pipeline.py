import re
import os

def escape_latex(text):
    # Escape special LaTeX characters
    # Only escape & for now, as that's the main culprit. Can add % $ # _ { } ~ ^ \ later if needed.
    return text.replace('&', r'\&')

def parse_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into Part 1 and Part 2 & 3
    parts = re.split(r'# PART 2 & PART 3: CUE CARDS', content)
    part1_raw = parts[0]
    part2_3_raw = parts[1] if len(parts) > 1 else ""

    part1_sections = []
    
    # Split by topic heading "## "
    p1_chunks = re.split(r'\n##\s+', '\n' + part1_raw)
    for chunk in p1_chunks:
        if not chunk.strip() or chunk.strip().startswith('# PART 1'): 
            continue
            
        lines = chunk.strip().split('\n')
        topic_name = lines[0].strip()
        
        prompt_title = f"IELTS Part 1 — {topic_name}"
        questions = []
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('> [!prompt]'):
                prompt_title = re.sub(r'> \[\!prompt\]\s*', '', line).strip()
            elif line.startswith('> -') or line.startswith('>-'):
                q = re.sub(r'^>\s*-\s*', '', line).strip()
                questions.append(escape_latex(q))
                
        if questions:
            part1_sections.append({
                'topic': escape_latex(topic_name),
                'title': escape_latex(prompt_title),
                'questions': questions
            })

    part2_3_sections = []
    p2_3_chunks = re.split(r'\n##\s+', '\n' + part2_3_raw)
    
    for chunk in p2_3_chunks:
        if not chunk.strip():
            continue
            
        lines = chunk.strip().split('\n')
        topic_name = lines[0].strip()
        
        # We need to distinguish P2 (prompt block) and P3 (question block)
        in_p2 = False
        in_p3 = False
        
        p2_title = "Cue Card"
        p2_content = []
        p3_title = "Discussion Questions"
        p3_questions = []
        
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('> [!prompt]'):
                in_p2 = True
                in_p3 = False
                p2_title = re.sub(r'> \[\!prompt\]\s*', '', line).strip()
                continue
            elif line.startswith('> [!question]'):
                in_p3 = True
                in_p2 = False
                p3_title = re.sub(r'> \[\!question\]\s*', '', line).strip()
                continue
                
            if in_p2:
                # Clean prompt
                clean_line = re.sub(r'^>\s*', '', line)
                if clean_line:
                     p2_content.append(escape_latex(clean_line))
                     
            elif in_p3:
                # Clean question
                m = re.match(r'^>\s*\d+\.\s*(.+)', line)
                if m:
                    p3_questions.append(escape_latex(m.group(1).strip()))
                    
        part2_3_sections.append({
            'topic': escape_latex(topic_name),
            'p2_title': escape_latex(p2_title),
            'p2_content': p2_content, # list of lines
            'p3_title': escape_latex(p3_title),
            'p3_questions': p3_questions
        })
        
    return part1_sections, part2_3_sections

def generate_part1_tex(part1_data, outpath):
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write("% PART 1\n")
        f.write("\\chapter{Part 1: Personal \\& General Topics}\n\n")
        
        for idx, sec in enumerate(part1_data, 1):
            f.write(f"\\section{{{sec['topic']}}}\n")
            f.write(f"\\begin{{ieltsprompt}}[{sec['title']}]\n")
            f.write("\\begin{itemize}[itemsep=4pt]\n")
            # Fallback if questions is empty, though we skipped empty chunks
            if not sec['questions']:
                f.write("    \\item \\textit{No questions found}\n")
            for q in sec['questions']:
                f.write(f"    \\item {q}\n")
            f.write("\\end{itemize}\n")
            f.write("\\end{ieltsprompt}\n\n")
            
            f.write("\\vspace{1em}\n")
            f.write("\\textit{Các câu trả lời mẫu sẽ được cập nhật tại đây...}\n")
            f.write("\\vspace{2em}\n\n")

def generate_part2_3_tex(part2_3_data, outpath):
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write("% PART 2 & 3\n")
        f.write("\\chapter{Part 2 \\& 3: Cue Cards \\& Discussion Topics}\n\n")
        
        for idx, sec in enumerate(part2_3_data, 1):
            f.write(f"\\section{{{sec['topic']}}}\n")
            
            # Part 2
            f.write(f"\\begin{{ieltsprompt}}[{sec['p2_title']}]\n")
            for line in sec['p2_content']:
                if line.startswith('- '):
                    f.write(f"\\textbullet\\ {line[2:]} \\\\\n")
                else:
                    f.write(f"{line} \\\\\n")
            f.write("\\end{ieltsprompt}\n\n")
            
            f.write("\\vspace{1em}\n")
            f.write("\\textit{Bài trả lời mẫu Part 2 sẽ được cập nhật tại đây (150-200 từ)...}\n")
            f.write("\\vspace{2em}\n\n")
            
            # Part 3
            f.write(f"\\begin{{ieltsprompt}}[{sec['p3_title']}]\n")
            f.write("\\begin{enumerate}[itemsep=4pt]\n")
            for q in sec['p3_questions']:
                f.write(f"    \\item {q}\n")
            f.write("\\end{enumerate}\n")
            f.write("\\end{ieltsprompt}\n\n")
            
            f.write("\\vspace{1em}\n")
            f.write("\\textit{Các câu trả lời mẫu Part 3 (4-5 câu) sẽ được cập nhật tại đây...}\n")
            f.write("\\vspace{2em}\n\n")

if __name__ == "__main__":
    raw_md_path = "../../Raw/forecastQ2-26.md"
    part1_out = "../chapters/part1.tex"
    part2_3_out = "../chapters/part2_3.tex"
    
    os.makedirs(os.path.dirname(part1_out), exist_ok=True)
    
    print("Parsing Markdown file...")
    p1, p23 = parse_markdown(raw_md_path)
    print(f"Found {len(p1)} Part 1 topics.")
    print(f"Found {len(p23)} Part 2 & 3 topics.")
    
    print("Generating LaTeX files...")
    generate_part1_tex(p1, part1_out)
    generate_part2_3_tex(p23, part2_3_out)
    
    print("Generation complete!")
