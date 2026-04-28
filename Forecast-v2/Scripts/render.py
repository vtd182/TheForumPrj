import re
import os
import sys
import shutil
import subprocess


def escape_latex(text):
    """Escape special LaTeX characters in user-facing text."""
    text = text.replace('&', r'\&')
    text = text.replace('%', r'\%')
    text = text.replace('#', r'\#')
    
    # User requested to replace -- with -
    text = text.replace('--', '-')
    
    # Translate Sample headers to English
    text = text.replace('Học sinh / Sinh viên', 'Student Persona (Band 7-8)')
    text = text.replace('Học sinh/Sinh viên', 'Student Persona (Band 7-8)')
    text = text.replace('Người đi làm', 'Working Professional Persona (Band 7-8)')
    
    return text


def build_vocab_table(raw_vocab_lines):
    """Convert raw markdown vocab lines into a 5-column LaTeX tabularx table.

    Supported formats (flexible):
      - **word** (pos) (/IPA/): English meaning | Vietnamese meaning
      - **word** (/IPA/): English meaning | Vietnamese meaning
      - **word** (pos): English meaning | Vietnamese meaning
      - **word** (pos) (IPA): English meaning | Vietnamese meaning  [no / delimiters]
    The function distinguishes IPA from pos by checking if the group starts with /
    or contains only letters/spaces (pos) vs IPA characters.
    """
    def is_ipa(s):
        """Return True if this parenthetical group looks like an IPA transcription."""
        s = s.strip()
        return s.startswith('/') or s.startswith('ˌ') or s.startswith('ˈ')

    rows = []
    for v in raw_vocab_lines:
        v = v.strip()
        if not v.startswith('- '):
            continue
        v = v[2:].strip()

        # Extract bold word
        m_word = re.match(r'\*\*(.*?)\*\*\s*(.*)', v)
        if not m_word:
            continue
        word = escape_latex(m_word.group(1))
        rest = m_word.group(2).strip()

        # Extract all parenthetical groups before the colon
        # e.g. "(adj)" "(/fʊd/)" "(n phr)" "(/ˌep.ɪˈstiː.mɪk/)"
        paren_pattern = re.compile(r'^\(([^)]*)\)\s*')
        groups = []
        while rest.startswith('('):
            pm = paren_pattern.match(rest)
            if pm:
                groups.append(pm.group(1))
                rest = rest[pm.end():]
            else:
                break

        # rest should now start with ": meaning | meaning"
        if not rest.startswith(':'):
            continue
        meaning_part = rest[1:].strip()

        # Split meaning into English | Vietnamese
        if '|' in meaning_part:
            eng_raw, vie_raw = meaning_part.split('|', 1)
            eng = escape_latex(eng_raw.strip())
            vie = escape_latex(vie_raw.strip())
        else:
            # No pipe — treat whole thing as Vietnamese meaning
            eng = ''
            vie = escape_latex(meaning_part.strip())

        # Classify groups into pos vs ipa
        pos = ''
        ipa = ''
        for g in groups:
            if is_ipa(g):
                ipa = g
            else:
                pos = escape_latex(g)

        rows.append(
            f"\\textbf{{{word}}} & {pos} & {ipa} & {eng} & {vie} \\\\ \\hline"
        )

    if not rows:
        return ""

    header = (
        "\n\\vspace{0.8em}\n"
        "\\begin{center}\n"
        "\\renewcommand{\\arraystretch}{1.65}\n"
        "\\rowcolors{2}{ForumFreshLight}{white}\n"
        "\\begin{tabularx}{\\textwidth}{|V{0.22\\textwidth}|C{0.07\\textwidth}|I{0.20\\textwidth}|Y|V{0.18\\textwidth}|}\n"
        "\\hline\n"
        "\\rowcolor{ForumFreshBlue!20}\n"
        "\\textbf{Từ} & \\textbf{Loại} & \\textbf{IPA} & "
        "\\textbf{English Meaning} & \\textbf{Dịch nghĩa} \\\\\n"
        "\\hline\n"
    )
    footer = "\\end{tabularx}\n\\end{center}\n"
    return header + "\n".join(rows) + "\n" + footer



def process_topic_block(topic_chunk):
    """Process a full ## Topic block. Extract questions and vocab separately."""
    lines = topic_chunk.strip().split('\n')
    topic_name = lines[0].strip()
    body = "\n".join(lines[1:]).strip()

    # Split out vocabulary blocks first
    # Find all **Vocabulary:** markers and their content
    parts = re.split(r'(?m)^\*\*Vocabulary:\*\*\s*$', body)

    # parts[0] = all Q&A text before first vocab
    # parts[1..n] = vocab items + possibly more Q&A after
    qa_text = parts[0]
    vocab_blocks_raw = []

    for i in range(1, len(parts)):
        part_lines = parts[i].strip().split('\n')
        vocab_lines = []
        remaining_qa = []
        hit_non_vocab = False
        for line in part_lines:
            if not hit_non_vocab and (line.strip().startswith('- **') or line.strip() == ''):
                vocab_lines.append(line)
            else:
                hit_non_vocab = True
                remaining_qa.append(line)
        vocab_blocks_raw.append(vocab_lines)
        if remaining_qa:
            qa_text += "\n" + "\n".join(remaining_qa)

    # Now split qa_text into individual questions by ### headers
    q_chunks = re.split(r'\n###\s+', '\n' + qa_text)
    questions = []
    for qc in q_chunks:
        if not qc.strip():
            continue
        q_lines = qc.strip().split('\n')
        q_title = q_lines[0].strip()
        q_body = "\n".join(q_lines[1:]).strip()

        # Convert bold
        q_body = re.sub(
            r'\*\*(.*?)\*\*',
            lambda m: '\\textbf{' + escape_latex(m.group(1)) + '}',
            q_body
        )
        
        # Finally escape the remaining body
        q_body = escape_latex(q_body)

        # Convert bullets for cue card prompt
        prompt_text = ""
        answer_text = q_body

        # Check if this is a cue card (has text before Sample)
        sample_match = re.search(r'\\textbf\{Sample\s', q_body)
        if sample_match:
            prompt_text = q_body[:sample_match.start()].strip()
            answer_text = q_body[sample_match.start():].strip()
        else:
            # No sample - might be a question-only line
            prompt_text = q_body
            answer_text = ""

        # Convert bullet points in prompt to itemize
        if prompt_text and '- ' in prompt_text:
            p_lines = prompt_text.split('\n')
            p_clean = []
            in_list = False
            for p in p_lines:
                if p.strip().startswith('- '):
                    if not in_list:
                        p_clean.append("\\begin{itemize}[leftmargin=2em, itemsep=2pt]")
                        in_list = True
                    p_clean.append("\\item " + p.strip()[2:])
                else:
                    if in_list:
                        p_clean.append("\\end{itemize}")
                        in_list = False
                    p_clean.append(p)
            if in_list:
                p_clean.append("\\end{itemize}")
            prompt_text = "\n".join(p_clean)

        questions.append({
            'q_title': escape_latex(q_title),
            'prompt_text': prompt_text,
            'answer_text': answer_text,
        })

    # Build vocab tables from raw blocks
    vocab_tables = []
    for vb in vocab_blocks_raw:
        table = build_vocab_table(vb)
        if table:
            vocab_tables.append(table)

    return {
        'topic': escape_latex(topic_name),
        'questions': questions,
        'vocab_tables': vocab_tables,
    }


def parse_answered_file(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    parsed = []
    current_topic_lines = []

    def flush_topic():
        nonlocal current_topic_lines
        if current_topic_lines:
            parsed.append(process_topic_block("\n".join(current_topic_lines)))
            current_topic_lines = []

    for raw_line in content.splitlines():
        line = raw_line.rstrip()

        category_match = re.match(r'^#\s+(PART 1:\s+.+)$', line.strip(), re.IGNORECASE)
        if category_match:
            flush_topic()
            parsed.append({
                'type': 'category',
                'title': escape_latex(category_match.group(1).strip()),
            })
            continue

        if re.match(r'^##\s+', line):
            flush_topic()
            current_topic_lines = [re.sub(r'^##\s+', '', line).strip()]
            continue

        if current_topic_lines:
            current_topic_lines.append(line)

    flush_topic()
    return parsed


def generate_part1_tex(parsed_data, outpath):
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write("% Part 1\n")
        f.write("\\chapter{Part 1: Personal \\& General Topics}\n\n")

        for sec in parsed_data:
            if sec.get('type') == 'category':
                f.write(f"\\section*{{{sec['title']}}}\n")
                f.write(f"\\addcontentsline{{toc}}{{section}}{{{sec['title']}}}\n\n")
                continue

            f.write(f"\\section{{{sec['topic']}}}\n")
            for q in sec['questions']:
                f.write("\\begin{ieltsquestion}\n")
                f.write(f"\\textbf{{{q['q_title']}}}\n")
                f.write("\\end{ieltsquestion}\n")
                if q['answer_text']:
                    f.write(q['answer_text'])
                    f.write("\n\n")
                f.write("\\separator\n\n")

            # Vocab table(s) at end of topic
            for vt in sec['vocab_tables']:
                f.write(vt)
                f.write("\n")
            f.write("\\newpage\n\n")


def generate_part2_3_tex(parsed_data, outpath):
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write("% Part 2 & 3\n")
        f.write("\\chapter{Part 2 \\& 3: Cue Cards \\& Discussion Topics}\n\n")

        for sec in parsed_data:
            if sec.get('type') == 'category':
                continue

            f.write(f"\\section{{{sec['topic']}}}\n")
            part3_header_written = False
            vocab_idx = 0

            for q in sec['questions']:
                is_cuecard = q['q_title'].upper().startswith("PART 2")
                if is_cuecard:
                    f.write("\\begin{ieltsprompt}\n")
                    if q['prompt_text']:
                        f.write(f"{q['prompt_text']}\n")
                    f.write("\\end{ieltsprompt}\n")
                    if q['answer_text']:
                        f.write("\\begin{ieltsanswer}\n")
                        f.write(q['answer_text'])
                        f.write("\n\\end{ieltsanswer}\n\n")
                    # Vocab table after cue card answer
                    if vocab_idx < len(sec['vocab_tables']):
                        f.write(sec['vocab_tables'][vocab_idx])
                        f.write("\n")
                        vocab_idx += 1
                else:
                    if not part3_header_written:
                        f.write("\\partthreeheader\n\n")
                        part3_header_written = True
                    f.write("\\begin{ieltsquestion}\n")
                    f.write(f"\\textbf{{{q['q_title']}}}\n")
                    f.write("\\end{ieltsquestion}\n")
                    if q['answer_text']:
                        f.write(q['answer_text'])
                        f.write("\n\n")
                    f.write("\\separator\n\n")

            # Remaining vocab tables (e.g. Part 3 summary vocab)
            while vocab_idx < len(sec['vocab_tables']):
                f.write(sec['vocab_tables'][vocab_idx])
                f.write("\n")
                vocab_idx += 1

            f.write("\\newpage\n\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 render.py <path_to_data_folder>")
        sys.exit(1)

    data_dir = os.path.abspath(sys.argv[1])
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

    p1_data = parse_answered_file(part1_md)
    p2_3_data = parse_answered_file(part2_3_md)

    print(f"Parsed {len(p1_data)} P1 topics and {len(p2_3_data)} P2/3 topics.")

    generate_part1_tex(p1_data, os.path.join(output_dir, "chapters", "part1.tex"))
    generate_part2_3_tex(p2_3_data, os.path.join(output_dir, "chapters", "part2_3.tex"))

    compile_script = os.path.join(output_dir, "compile.sh")
    os.chmod(compile_script, 0o755)

    print("Compiling LaTeX document...")
    try:
        subprocess.run(["./compile.sh"], cwd=output_dir, check=True)
        print(f"Success! PDF generated at: Output/{output_folder_name}/build/main.pdf")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling LaTeX! Check the logs in Output/{output_folder_name}/build/")
        sys.exit(1)
