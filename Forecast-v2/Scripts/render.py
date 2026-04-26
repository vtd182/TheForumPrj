import re
import os
import sys
import shutil
import subprocess

def escape_latex(text):
    return text.replace('&', r'\&')

def parse_answered_part1(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by topic: ## Topic Name
    topics = re.split(r'\n##\s+', '\n' + content)
    parsed_topics = []

    for chunk in topics:
        if not chunk.strip() or chunk.strip().startswith('# PART'):
            continue
        
        lines = chunk.strip().split('\n')
        topic_name = lines[0].strip()
        # Remove any "IELTS Part 1 — " prefix if present or keep it? 
        # The script will just output it as the section title.
        
        body_text = "\n".join(lines[1:]).strip()
        
        # Split questions: ### Question text
        questions = re.split(r'\n###\s+', '\n' + body_text)
        parsed_questions = []

        for q_chunk in questions:
            if not q_chunk.strip():
                continue
            q_lines = q_chunk.strip().split('\n')
            q_title = q_lines[0].strip()
            q_body = "\n".join(q_lines[1:]).strip()
            
            # Now we find samples and vocabulary
            # We can just iterate lines to identify them or use regex
            # But the simplest LaTeX mapping is to just replace Markdown formatting 
            # with LaTeX formatting!
            
            # Bold "**text**" -> "\textbf{text}"
            q_body = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', q_body)
            # Vocab items: "- \textbf{word} (pron): meaning"
            # We need to extract the Vocabulary block to wrap in multicols
            
            parts = re.split(r'\\textbf{Vocabulary:?}', q_body, flags=re.IGNORECASE)
            
            latex_blocks = []
            
            for i, part in enumerate(parts):
                if i > 0:
                    # This part contains vocabulary list
                    vocab_lines = part.strip().split('\n')
                    clean_v_lines = []
                    for v in vocab_lines:
                        if v.startswith('- '):
                            # wrap the first \textbf{} into \vocab{}
                            # e.g. "- \textbf{word}: meaning" -> "\item \vocab{word}: meaning"
                            v = re.sub(r'\\textbf{(.*?)}', r'\\vocab{\1}', v, count=1)
                            # Remove the "- " and add \item
                            v = re.sub(r'^-\s*', r'\\item ', v)
                            clean_v_lines.append(v)
                        else:
                            clean_v_lines.append(v)
                    
                    latex_blocks.append("\\vspace{0.5em}\n\\textbf{\\textit{Vocabulary:}}\n\\begin{multicols}{2}\n\\begin{itemize}[itemsep=2pt, leftmargin=1.5em]")
                    latex_blocks.append("\n".join(clean_v_lines))
                    latex_blocks.append("\\end{itemize}\n\\end{multicols}")
                else:
                    # Regular text (Samples)
                    # Convert double newlines to \\ or \vspace
                    part = part.strip().replace('\n\n', '\n\n\\vspace{0.5em}\n\n')
                    latex_blocks.append(part)
                    
            latex_content = "\n\n".join(latex_blocks)
            
            parsed_questions.append({
                'q_title': escape_latex(q_title),
                'latex_content': escape_latex(latex_content)
            })
            
        parsed_topics.append({
            'topic': escape_latex(topic_name),
            'questions': parsed_questions
        })
    return parsed_topics

# Simplistic approach to Part 2 & 3
def parse_answered_part2_3(filepath):
    if not os.path.exists(filepath):
        return []
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    topics = re.split(r'\n##\s+', '\n' + content)
    parsed_topics = []

    for chunk in topics:
        if not chunk.strip() or chunk.strip().startswith('# PART'):
            continue
            
        lines = chunk.strip().split('\n')
        topic_name = lines[0].strip()
        body_text = "\n".join(lines[1:]).strip()
        
        # We will just treat the whole block similarly, maybe detecting P2 and P3 blocks
        body_text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', body_text)
        
        parts = re.split(r'\\textbf{Vocabulary:?}', body_text, flags=re.IGNORECASE)
        latex_blocks = []
        for i, part in enumerate(parts):
            if i > 0:
                vocab_lines = part.strip().split('\n')
                clean_v_lines = []
                for v in vocab_lines:
                    if v.startswith('- '):
                        v = re.sub(r'\\textbf{(.*?)}', r'\\vocab{\1}', v, count=1)
                        v = re.sub(r'^-\s*', r'\\item ', v)
                        clean_v_lines.append(v)
                    else:
                        clean_v_lines.append(v)
                
                latex_blocks.append("\\vspace{0.5em}\n\\textbf{\\textit{Vocabulary:}}\n\\begin{multicols}{2}\n\\begin{itemize}[itemsep=2pt, leftmargin=1.5em]")
                latex_blocks.append("\n".join(clean_v_lines))
                latex_blocks.append("\\end{itemize}\n\\end{multicols}")
            else:
                part = part.strip().replace('\n\n', '\n\n\\vspace{0.5em}\n\n')
                latex_blocks.append(part)
                
        latex_content = "\n\n".join(latex_blocks)
        
        parsed_topics.append({
            'topic': escape_latex(topic_name),
            'latex_content': escape_latex(latex_content)
        })
    return parsed_topics

def generate_part1_tex(parsed_data, outpath):
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write("% PART 1\n")
        f.write("\\chapter{Part 1: Personal \\& General Topics}\n\n")
        
        for sec in parsed_data:
            f.write(f"\\section{{{sec['topic']}}}\n")
            
            for q in sec['questions']:
                f.write(f"\\begin{{ieltsprompt}}[{q['q_title']}]\n")
                f.write(q['latex_content'])
                f.write("\n\\end{ieltsprompt}\n\n")

def generate_part2_3_tex(parsed_data, outpath):
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write("% PART 2 & 3\n")
        f.write("\\chapter{Part 2 \\& 3: Cue Cards \\& Discussion Topics}\n\n")
        
        for sec in parsed_data:
            f.write(f"\\section{{{sec['topic']}}}\n")
            # In P23, the chunks might just be one big prompt, we can wrap it fully
            f.write("\\begin{ieltsprompt}[Cue Card \\& Discussion]\n")
            f.write(sec['latex_content'])
            f.write("\n\\end{ieltsprompt}\n\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 render.py <path_to_data_folder>")
        print("Example: python3 render.py Data/forecastQ2-26/forum")
        sys.exit(1)

    data_dir = os.path.abspath(sys.argv[1])
    if not os.path.exists(data_dir):
        print(f"Error: {data_dir} does not exist.")
        sys.exit(1)
        
    # Extract forecast name and version from data_dir path
    # e.g., Data/forecastQ2-26/forum
    parts = data_dir.rstrip('/').split('/')
    if len(parts) >= 2:
        version = parts[-1]
        forecast_name = parts[-2]
    else:
        forecast_name = "output"
        version = "default"
        
    output_folder_name = f"{forecast_name}_{version}"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    template_dir = os.path.join(project_root, "Template")
    output_dir = os.path.join(project_root, "Output", output_folder_name)
    
    print(f"Rendering: {output_folder_name}")
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    shutil.copytree(template_dir, output_dir)
    os.makedirs(os.path.join(output_dir, "chapters"), exist_ok=True)
    
    part1_md = os.path.join(data_dir, "answered_part1.md")
    part2_3_md = os.path.join(data_dir, "answered_part2_3.md")
    
    part1_out = os.path.join(output_dir, "chapters", "part1.tex")
    part2_3_out = os.path.join(output_dir, "chapters", "part2_3.tex")
    
    p1_data = parse_answered_part1(part1_md)
    p2_3_data = parse_answered_part2_3(part2_3_md)
    
    print(f"Parsed {len(p1_data)} P1 topics and {len(p2_3_data)} P2/3 topics.")
    
    generate_part1_tex(p1_data, part1_out)
    generate_part2_3_tex(p2_3_data, part2_3_out)
    
    compile_script = os.path.join(output_dir, "compile.sh")
    os.chmod(compile_script, 0o755)
    
    print("Compiling LaTeX document...")
    try:
        subprocess.run(["./compile.sh"], cwd=output_dir, check=True)
        print(f"Success! PDF generated at: Output/{output_folder_name}/build/main.pdf")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling LaTeX! Check the logs in Output/{output_folder_name}/build/")
        sys.exit(1)
