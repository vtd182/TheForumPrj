#!/usr/bin/env python3
import argparse
import csv
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VocabItem:
    term: str
    meaning_en: str
    meaning_vi: str


@dataclass(frozen=True)
class QA:
    question: str
    answer: str


@dataclass(frozen=True)
class Part1Topic:
    title: str
    qas: list[QA]
    vocab: list[VocabItem]


@dataclass(frozen=True)
class Part2Topic:
    prompt: str
    bullets: list[str]
    samples: list[str]
    vocab: list[VocabItem]


@dataclass(frozen=True)
class Part3Topic:
    title: str
    qas: list[QA]


@dataclass(frozen=True)
class VocabEnrichedItem:
    term: str
    pos: str
    ipa: str
    meaning_en: str
    meaning_vi: str


@dataclass(frozen=True)
class Part23Topic:
    title: str
    part2_prompt: str
    bullets: list[str]
    samples: list[str]
    vocab: list[VocabEnrichedItem]
    part3_qas: list[QA]


TOPIC_P1_RE = re.compile(r"^##\s+\d+\.\s+(?P<title>.+?)\s*$")
TOPIC_P2_RE = re.compile(r"^##\s+\d+\.\s+(?P<prompt>Describe.+?)\s*$", re.IGNORECASE)
TOPIC_P3_RE = re.compile(r"^##\s+\d+\.\s+Topic:\s+(?P<title>.+?)\s*$", re.IGNORECASE)
QUESTION_RE = re.compile(r"^\*\*(?P<q>.+?)\*\*\s*$")
VOCAB_HDR_RE = re.compile(r"^###\s+.*Vocabulary", re.IGNORECASE)
HR_RE = re.compile(r"^\s*---\s*$")
VOCAB_ITEM_RE = re.compile(
    r"^-\s+\*\*(?P<term>.+?)\*\*\s+[–-]\s+(?P<en>.+?)\s+[–-]\s+(?P<vi>.+?)\s*$"
)
VOCAB_ITEM_ENRICHED_RE = re.compile(
    r"^-\s+\*\*(?P<term>.+?)\*\*\s*(?:\((?P<pos>[^)]+)\))?\s*(?:/(?P<ipa>[^/]+)/)?\s*[–-]\s+(?P<en>.+?)\s+[–-]\s+(?P<vi>.+?)\s*$"
)
VERSION_RE = re.compile(r"^\s*(?:#+\s*)?Version\s+(?P<n>\d+)\s*$", re.IGNORECASE)

TOPIC_23_RE = re.compile(r"^##\s+Topic\s+\d+\s*:\s*(?P<title>.+?)\s*$", re.IGNORECASE)
PROMPT_23_RE = re.compile(r"^\*\*Prompt:\*\*\s*(?P<prompt>.+?)\s*$", re.IGNORECASE)
YOU_SHOULD_SAY_23_RE = re.compile(r"^\*\*You should say:\*\*\s*$", re.IGNORECASE)
VOCAB_TABLE_ROW_RE = re.compile(
    r"^\|\s*(?P<term>[^|]*?)\s*\|\s*(?P<pos>[^|]*?)\s*\|\s*(?P<ipa>[^|]*?)\s*\|\s*(?P<en>[^|]*?)\s*\|\s*(?P<vi>[^|]*?)\s*\|\s*$"
)
SAMPLE_LABEL_RE = re.compile(r"^\*\*(?P<label>(?:Sample|Version\s+\d+)):\*\*\s*$", re.IGNORECASE)


def latex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "#": r"\#",
        "$": r"\$",
        "%": r"\%",
        "&": r"\&",
        "_": r"\_",
        "^": r"\textasciicircum{}",
        "~": r"\textasciitilde{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def normalize_paragraphs(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    paragraphs = re.split(r"\n\s*\n+", raw)
    normalized: list[str] = []
    for p in paragraphs:
        p_lines = [ln.strip() for ln in p.splitlines() if ln.strip()]
        if not p_lines:
            continue
        normalized.append(" ".join(p_lines))
    return r"\par ".join(latex_escape(p) for p in normalized)


def parse_vocab_block(lines: list[str], start: int) -> tuple[list[VocabItem], int]:
    vocab: list[VocabItem] = []
    i = start
    while i < len(lines):
        ln = lines[i].strip()
        if not ln:
            i += 1
            continue
        if HR_RE.match(ln) or ln.startswith("## "):
            break
        m = VOCAB_ITEM_ENRICHED_RE.match(ln) or VOCAB_ITEM_RE.match(ln)
        if m:
            vocab.append(
                VocabItem(
                    term=m.group("term").strip(),
                    meaning_en=m.group("en").strip(),
                    meaning_vi=m.group("vi").strip(),
                )
            )
        i += 1
    return vocab, i


def parse_part1(md: str) -> list[Part1Topic]:
    lines = md.strip("\ufeff").splitlines()
    topics: list[Part1Topic] = []
    i = 0
    current_title: str | None = None
    qas: list[QA] = []
    vocab: list[VocabItem] = []

    def flush() -> None:
        nonlocal current_title, qas, vocab
        if current_title:
            topics.append(Part1Topic(title=current_title, qas=qas, vocab=vocab))
        current_title = None
        qas = []
        vocab = []

    while i < len(lines):
        ln = lines[i].rstrip()
        i += 1
        if not ln.strip():
            continue
        if HR_RE.match(ln):
            continue

        m_topic = TOPIC_P1_RE.match(ln)
        if m_topic:
            flush()
            current_title = m_topic.group("title").strip()
            continue

        if VOCAB_HDR_RE.match(ln):
            vocab, i = parse_vocab_block(lines, i)
            continue

        m_q = QUESTION_RE.match(ln.strip())
        if m_q:
            question = m_q.group("q").strip()
            answer_lines: list[str] = []
            while i < len(lines):
                peek = lines[i].rstrip()
                if not peek.strip():
                    answer_lines.append("")
                    i += 1
                    continue
                if TOPIC_P1_RE.match(peek) or QUESTION_RE.match(peek.strip()) or VOCAB_HDR_RE.match(peek) or HR_RE.match(peek):
                    break
                answer_lines.append(peek)
                i += 1
            qas.append(QA(question=question, answer="\n".join(answer_lines).strip()))
            continue

    flush()
    return topics


def parse_part2(md: str) -> list[Part2Topic]:
    lines = md.strip("\ufeff").splitlines()
    topics: list[Part2Topic] = []
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        i += 1
        m_topic = TOPIC_P2_RE.match(ln)
        if not m_topic:
            continue

        prompt = m_topic.group("prompt").strip()

        while i < len(lines) and not lines[i].strip():
            i += 1

        bullets: list[str] = []
        if i < len(lines) and lines[i].strip().lower().startswith("**you should say"):
            i += 1
            while i < len(lines):
                bullet_ln = lines[i].strip()
                if HR_RE.match(bullet_ln):
                    i += 1
                    break
                if bullet_ln.startswith("- "):
                    bullets.append(bullet_ln[2:].strip())
                i += 1

        while i < len(lines) and HR_RE.match(lines[i].strip()):
            i += 1

        answer_lines: list[str] = []
        while i < len(lines):
            peek = lines[i].rstrip()
            if TOPIC_P2_RE.match(peek) or VOCAB_HDR_RE.match(peek) or TOPIC_P3_RE.match(peek):
                break
            if HR_RE.match(peek) and answer_lines:
                break
            if HR_RE.match(peek) and not answer_lines:
                i += 1
                continue
            answer_lines.append(peek)
            i += 1
        answer_text = "\n".join(answer_lines).strip()

        samples: list[str] = []
        versioned: list[tuple[int, list[str]]] = []
        current_version: int | None = None
        current_buf: list[str] = []
        for line in answer_text.splitlines():
            vm = VERSION_RE.match(line.strip())
            if vm:
                if current_version is not None:
                    versioned.append((current_version, current_buf))
                current_version = int(vm.group("n"))
                current_buf = []
                continue
            current_buf.append(line)
        if current_version is not None:
            versioned.append((current_version, current_buf))

        if versioned:
            for _, buf in sorted(versioned, key=lambda x: x[0]):
                samples.append("\n".join(buf).strip())
        else:
            samples.append(answer_text)

        vocab: list[VocabItem] = []
        while i < len(lines) and not VOCAB_HDR_RE.match(lines[i].strip()):
            if TOPIC_P2_RE.match(lines[i]) or TOPIC_P3_RE.match(lines[i]):
                break
            i += 1
        if i < len(lines) and VOCAB_HDR_RE.match(lines[i].strip()):
            i += 1
            vocab, i = parse_vocab_block(lines, i)

        topics.append(Part2Topic(prompt=prompt, bullets=bullets, samples=samples, vocab=vocab))
    return topics


def parse_part3(md: str) -> tuple[list[Part3Topic], list[VocabItem]]:
    lines = md.strip("\ufeff").splitlines()
    topics: list[Part3Topic] = []
    vocab_all: list[VocabItem] = []
    i = 0
    current_title: str | None = None
    qas: list[QA] = []

    def flush() -> None:
        nonlocal current_title, qas
        if current_title:
            topics.append(Part3Topic(title=current_title, qas=qas))
        current_title = None
        qas = []

    while i < len(lines):
        ln = lines[i].rstrip()
        i += 1
        if not ln.strip():
            continue
        if VOCAB_HDR_RE.match(ln):
            vocab_all, i = parse_vocab_block(lines, i)
            break
        if HR_RE.match(ln):
            continue
        m_topic = TOPIC_P3_RE.match(ln)
        if m_topic:
            flush()
            current_title = m_topic.group("title").strip()
            continue
        m_q = QUESTION_RE.match(ln.strip())
        if m_q:
            question = m_q.group("q").strip()
            answer_lines: list[str] = []
            while i < len(lines):
                peek = lines[i].rstrip()
                if not peek.strip():
                    answer_lines.append("")
                    i += 1
                    continue
                if TOPIC_P3_RE.match(peek) or QUESTION_RE.match(peek.strip()) or VOCAB_HDR_RE.match(peek) or HR_RE.match(peek):
                    break
                answer_lines.append(peek)
                i += 1
            qas.append(QA(question=question, answer="\n".join(answer_lines).strip()))
            continue

    flush()
    return topics, vocab_all


def parse_part23_merged(md: str) -> list[Part23Topic]:
    lines = md.strip("\ufeff").splitlines()
    topics: list[Part23Topic] = []
    i = 0

    while i < len(lines):
        ln = lines[i].rstrip()
        i += 1
        m_topic = TOPIC_23_RE.match(ln)
        if not m_topic:
            continue

        title = m_topic.group("title").strip()
        part2_prompt = ""
        bullets: list[str] = []
        samples: list[str] = []
        vocab: list[VocabEnrichedItem] = []
        part3_qas: list[QA] = []

        in_vocab = False
        while i < len(lines):
            cur = lines[i].rstrip()
            if TOPIC_23_RE.match(cur):
                break
            i += 1

            if not cur.strip() or HR_RE.match(cur):
                continue

            pm = PROMPT_23_RE.match(cur.strip())
            if pm:
                part2_prompt = pm.group("prompt").strip()
                continue

            if YOU_SHOULD_SAY_23_RE.match(cur.strip()):
                while i < len(lines):
                    b = lines[i].strip()
                    if not b:
                        i += 1
                        break
                    if b.startswith("- "):
                        bullets.append(b[2:].strip())
                        i += 1
                        continue
                    break
                continue

            if cur.strip().startswith("### Vocabulary"):
                in_vocab = True
                while i < len(lines):
                    vln = lines[i].strip()
                    if not vln:
                        i += 1
                        continue
                    if (
                        vln.startswith("### ")
                        or vln.startswith("## ")
                        or HR_RE.match(vln)
                        or QUESTION_RE.match(vln.strip())
                        or SAMPLE_LABEL_RE.match(vln.strip())
                    ):
                        break
                    if vln.startswith("|"):
                        if set(vln.strip()) <= {"|", "-", " "}:
                            i += 1
                            continue
                        mrow = VOCAB_TABLE_ROW_RE.match(vln)
                        if mrow:
                            term = mrow.group("term").strip()
                            if term.lower() in {"term", "từ"}:
                                i += 1
                                continue
                            vocab.append(
                                VocabEnrichedItem(
                                    term=term,
                                    pos=mrow.group("pos").strip(),
                                    ipa=mrow.group("ipa").strip(),
                                    meaning_en=mrow.group("en").strip(),
                                    meaning_vi=mrow.group("vi").strip(),
                                )
                            )
                        i += 1
                        continue
                    m2 = VOCAB_ITEM_ENRICHED_RE.match(vln) or VOCAB_ITEM_RE.match(vln)
                    if m2:
                        gd = m2.groupdict()
                        vocab.append(
                            VocabEnrichedItem(
                                term=m2.group("term").strip(),
                                pos=(gd.get("pos") or "").strip(),
                                ipa=(gd.get("ipa") or "").strip(),
                                meaning_en=m2.group("en").strip(),
                                meaning_vi=m2.group("vi").strip(),
                            )
                        )
                    i += 1
                continue

            sm = SAMPLE_LABEL_RE.match(cur.strip())
            if sm:
                sample_lines: list[str] = []
                while i < len(lines):
                    nxt = lines[i].rstrip()
                    if SAMPLE_LABEL_RE.match(nxt.strip()) or nxt.startswith("### ") or nxt.startswith("## ") or HR_RE.match(nxt):
                        break
                    sample_lines.append(nxt)
                    i += 1
                samples.append("\n".join(sample_lines).strip())
                continue

            # After vocab section, treat bold lines as Part 3 questions.
            if in_vocab:
                mq = QUESTION_RE.match(cur.strip())
                if mq:
                    question = mq.group("q").strip()
                    ans_lines: list[str] = []
                    while i < len(lines):
                        aln = lines[i].rstrip()
                        if not aln.strip():
                            ans_lines.append("")
                            i += 1
                            continue
                        if aln.startswith("## ") or aln.startswith("### ") or HR_RE.match(aln) or QUESTION_RE.match(aln.strip()):
                            break
                        ans_lines.append(aln)
                        i += 1
                    part3_qas.append(QA(question=question, answer="\n".join(ans_lines).strip()))
                    continue

        topics.append(
            Part23Topic(
                title=title,
                part2_prompt=part2_prompt,
                bullets=bullets,
                samples=[s for s in samples if s.strip()],
                vocab=vocab,
                part3_qas=part3_qas,
            )
        )

    return topics


def render_vocab_itemize(vocab: list[VocabItem]) -> str:
    if not vocab:
        return ""
    lines: list[str] = []
    lines.append("\\textbf{Vocabulary}\\par\n")
    lines.append("\\begin{itemize}\n")
    for v in vocab:
        term = latex_escape(v.term)
        en = latex_escape(v.meaning_en)
        vi = latex_escape(v.meaning_vi)
        lines.append(f"  \\item \\textbf{{{term}}} -- {en} -- {vi}\n")
    lines.append("\\end{itemize}\n")
    return "".join(lines)


def render_vocab_table_simple(vocab: list[VocabItem]) -> str:
    if not vocab:
        return ""
    lines: list[str] = []
    lines.append("\\begin{forecastvocabsimpletable}\n")
    for v in vocab:
        lines.append(
            "\\forecastvocabsimplerow{"
            + latex_escape(v.term)
            + "}{"
            + latex_escape(v.meaning_en)
            + "}{"
            + latex_escape(v.meaning_vi)
            + "}\n"
        )
    lines.append("\\end{forecastvocabsimpletable}\n")
    return "".join(lines)

def render_vocab_table_full(vocab: list[VocabEnrichedItem]) -> str:
    if not vocab:
        return ""
    lines: list[str] = []
    lines.append("\\begin{forecastvocabtable}\n")
    for v in vocab:
        lines.append(
            "\\forecastvocabrow{"
            + latex_escape(v.term)
            + "}{"
            + latex_escape(v.pos)
            + "}{"
            + latex_escape(v.ipa)
            + "}{"
            + latex_escape(v.meaning_en)
            + "}{"
            + latex_escape(v.meaning_vi)
            + "}\n"
        )
    lines.append("\\end{forecastvocabtable}\n")
    return "".join(lines)


def write_part1_tex(topics: list[Part1Topic], out_path: Path) -> None:
    parts: list[str] = []
    parts.append("\\documentclass{templates/forecastp1}\n\n")
    parts.append("\\newcommand{\\authorinfo}{THE FORUM CENTER - NGUYỄN HOÀNG HUY}\n")
    parts.append("\\newcommand{\\documenttitle}{SPEAKING FORECAST QUÝ III}\n")
    parts.append("\\newcommand{\\collectiontitle}{TUYỂN TẬP SAMPLE SPEAKING IELTS FORECAST QUÝ III (P1)}\n\n")
    parts.append("\\begin{document}\n\n")
    parts.append("\\thispagestyle{firstpage}\n")
    parts.append("\\makeforecastheader{\\authorinfo}{\\documenttitle}{\\collectiontitle}\n")
    parts.append("\\pagestyle{otherpages}\n\n")
    for idx, t in enumerate(topics, start=1):
        parts.append(f"\\forecasttopic{{Topic {idx}: {latex_escape(t.title)}}}\n")
        for qa in t.qas:
            parts.append(
                "\\forecastqa{"
                + latex_escape(qa.question)
                + "}{"
                + normalize_paragraphs(qa.answer)
                + "}\n"
            )
        if t.vocab:
            parts.append(render_vocab_itemize(t.vocab))
        parts.append("\n")
    parts.append("\\end{document}\n")
    out_path.write_text("".join(parts), encoding="utf-8")

def write_part23_merged_raw(part2_topics: list[Part2Topic], part3_topics: list[Part3Topic], out_path: Path) -> None:
    lines: list[str] = []
    lines.append("# PART 2+3 (MERGED BY TOPIC)\n\n")
    if len(part2_topics) != len(part3_topics):
        lines.append(
            f"> Warning: Part 2 topics ({len(part2_topics)}) != Part 3 topics ({len(part3_topics)}). "
            "Merged by index up to the shortest length.\n\n"
        )
    n = min(len(part2_topics), len(part3_topics))
    for i in range(n):
        p2 = part2_topics[i]
        p3 = part3_topics[i]
        lines.append(f"## Topic {i+1}: {p3.title}\n\n")
        lines.append(f"**Prompt:** {p2.prompt}\n\n")
        if p2.bullets:
            lines.append("**You should say:**\n")
            for b in p2.bullets:
                lines.append(f"- {b}\n")
            lines.append("\n")
        if p2.samples:
            for si, s in enumerate(p2.samples, start=1):
                if len(p2.samples) == 1:
                    lines.append("**Version 1:**\n\n")
                else:
                    lines.append(f"**Version {si}:**\n\n")
                lines.append(s.strip() + "\n\n")
        if p2.vocab:
            lines.append("### Vocabulary\n\n")
            lines.append("| Term | POS | IPA | Meaning (EN) | Meaning (VI) |\n")
            lines.append("|---|---|---|---|---|\n")
            for v in p2.vocab:
                lines.append(f"| {v.term} |  |  | {v.meaning_en} | {v.meaning_vi} |\n")
            lines.append("\n")

        for qa in p3.qas:
            lines.append(f"**{qa.question}**\n\n{qa.answer.strip()}\n\n")
        lines.append("---\n\n")

    out_path.write_text("".join(lines), encoding="utf-8")


def read_lexicon_csv(path: Path) -> dict[str, tuple[str, str]]:
    mapping: dict[str, tuple[str, str]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            term = (row.get("term") or row.get("Term") or "").strip()
            if not term:
                continue
            pos = (row.get("pos") or row.get("POS") or "").strip()
            ipa = (row.get("ipa") or row.get("IPA") or "").strip()
            mapping[term.casefold()] = (pos, ipa)
    return mapping


def write_lexicon_template(topics: list[Part23Topic], out_path: Path) -> None:
    if out_path.exists() and out_path.read_text(encoding="utf-8").strip():
        return
    seen: set[str] = set()
    terms: list[str] = []
    for t in topics:
        for v in t.vocab:
            key = v.term.casefold()
            if key in seen:
                continue
            seen.add(key)
            terms.append(v.term)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "pos", "ipa"])
        for term in sorted(terms, key=lambda x: x.casefold()):
            writer.writerow([term, "", ""])


def apply_lexicon(topics: list[Part23Topic], lexicon: dict[str, tuple[str, str]]) -> list[Part23Topic]:
    updated: list[Part23Topic] = []
    for t in topics:
        new_vocab: list[VocabEnrichedItem] = []
        for v in t.vocab:
            pos, ipa = v.pos, v.ipa
            m = lexicon.get(v.term.casefold())
            if m:
                if not pos and m[0]:
                    pos = m[0]
                if not ipa and m[1]:
                    ipa = m[1]
            new_vocab.append(
                VocabEnrichedItem(
                    term=v.term,
                    pos=pos,
                    ipa=ipa,
                    meaning_en=v.meaning_en,
                    meaning_vi=v.meaning_vi,
                )
            )
        updated.append(
            Part23Topic(
                title=t.title,
                part2_prompt=t.part2_prompt,
                bullets=t.bullets,
                samples=t.samples,
                vocab=new_vocab,
                part3_qas=t.part3_qas,
            )
        )
    return updated

def write_part23_interleaved_tex(
    topics: list[Part23Topic],
    out_path: Path,
) -> None:
    parts: list[str] = []
    parts.append("\\documentclass{templates/forecastp23}\n\n")
    parts.append("\\newcommand{\\authorinfo}{THE FORUM CENTER - NGUYỄN HOÀNG HUY}\n")
    parts.append("\\newcommand{\\documenttitle}{TÀI LIỆU IELTS SPEAKING QUÝ 3}\n")
    parts.append("\\newcommand{\\subtitle}{IELTS SPEAKING PART 2 + 3}\n\n")
    parts.append("\\begin{document}\n\n")
    parts.append("\\thispagestyle{firstpage}\n")
    parts.append("\\makeforecastheader{\\authorinfo}{\\documenttitle}{\\subtitle}\n")
    parts.append("\\pagestyle{otherpages}\n\n")

    for idx, t in enumerate(topics, start=1):
        if idx > 1:
            parts.append("\\clearpage\n")

        parts.append("\\begin{center}{\\color{topicblue}\\sffamily\\bfseries ")
        parts.append("Topic " + str(idx) + ": " + latex_escape(t.title))
        parts.append("}\\end{center}\n")
        parts.append("\\vspace{10pt}\n")

        bullets = t.bullets or []
        parts.append("\\forecastcuecard{" + latex_escape(t.part2_prompt or t.title) + "}{%\n")
        for b in bullets:
            if b.lower().startswith("and "):
                parts.append("  \\item " + latex_escape(b) + "\n")
            else:
                parts.append("  \\item \\textbf{" + latex_escape(b) + "}\n")
        parts.append("}\n\n")

        samples = t.samples or [""]
        if len(samples) == 1:
            parts.append("\\forecastsample[1]{" + normalize_paragraphs(samples[0]) + "}\n")
        else:
            parts.append("\\forecastsample[1]{" + normalize_paragraphs(samples[0]) + "}\n")
            parts.append("\\clearpage\n")
            parts.append("\\forecastsample[2]{" + normalize_paragraphs(samples[1]) + "}\n")

        if t.vocab:
            parts.append("\\clearpage\n")
            parts.append(render_vocab_table_full(t.vocab))
            parts.append("\n")

        if t.part3_qas:
            parts.append("\\clearpage\n")
            parts.append("\\begin{center}{\\color{topicblue}\\sffamily\\bfseries ")
            parts.append("Topic " + str(idx) + ": " + latex_escape(t.title))
            parts.append("}\\end{center}\n")
            parts.append("\\vspace{10pt}\n")
            for qa in t.part3_qas:
                parts.append(
                    "\\forecastqa{"
                    + latex_escape(qa.question)
                    + "}{"
                    + normalize_paragraphs(qa.answer)
                    + "}\n"
                )

    parts.append("\\end{document}\n")
    out_path.write_text("".join(parts), encoding="utf-8")


def write_part2_like_tex(topics: list[Part2Topic], out_path: Path) -> None:
    parts: list[str] = []
    parts.append("\\documentclass{templates/forecastp23}\n\n")
    parts.append("\\newcommand{\\authorinfo}{THE FORUM CENTER - NGUYỄN HOÀNG HUY}\n")
    parts.append("\\newcommand{\\documenttitle}{TÀI LIỆU IELTS SPEAKING QUÝ 3}\n")
    parts.append("\\newcommand{\\subtitle}{IELTS SPEAKING PART 2}\n\n")
    parts.append("\\begin{document}\n\n")
    parts.append("\\thispagestyle{firstpage}\n")
    parts.append("\\makeforecastheader{\\authorinfo}{\\documenttitle}{\\subtitle}\n")
    parts.append("\\pagestyle{otherpages}\n\n")
    for idx, t in enumerate(topics, start=1):
        if idx > 1:
            parts.append("\\clearpage\n")
        bullets = t.bullets or []
        if bullets:
            parts.append("\\forecastcuecard{" + latex_escape(t.prompt) + "}{%\n")
            for b in bullets:
                if b.lower().startswith("and "):
                    parts.append("  \\item " + latex_escape(b) + "\n")
                else:
                    parts.append("  \\item \\textbf{" + latex_escape(b) + "}\n")
            parts.append("}\n\n")
        for s_idx, sample in enumerate(t.samples, start=1):
            if len(t.samples) == 1:
                parts.append("\\forecastsample{" + normalize_paragraphs(sample) + "}\n")
            else:
                parts.append("\\forecastsample[" + str(s_idx) + "]{" + normalize_paragraphs(sample) + "}\n")
            if s_idx < len(t.samples):
                parts.append("\\clearpage\n")
        if t.vocab:
            parts.append("\\clearpage\n")
            parts.append(render_vocab_table_full(t.vocab))
            parts.append("\n")

    parts.append("\\end{document}\n")
    out_path.write_text("".join(parts), encoding="utf-8")

def write_part3_tex(topics: list[Part3Topic], out_path: Path) -> None:
    parts: list[str] = []
    parts.append("\\documentclass{templates/forecastp23}\n\n")
    parts.append("\\newcommand{\\authorinfo}{THE FORUM CENTER - NGUYỄN HOÀNG HUY}\n")
    parts.append("\\newcommand{\\documenttitle}{TÀI LIỆU IELTS SPEAKING QUÝ 3}\n")
    parts.append("\\newcommand{\\subtitle}{IELTS SPEAKING PART 3}\n\n")
    parts.append("\\begin{document}\n\n")
    parts.append("\\thispagestyle{firstpage}\n")
    parts.append("\\makeforecastheader{\\authorinfo}{\\documenttitle}{\\subtitle}\n")
    parts.append("\\pagestyle{otherpages}\n\n")
    for idx, t in enumerate(topics, start=1):
        parts.append(f"\\forecasttopic{{Topic {idx}: {latex_escape(t.title)}}}\n")
        for qa in t.qas:
            parts.append(
                "\\forecastqa{"
                + latex_escape(qa.question)
                + "}{"
                + normalize_paragraphs(qa.answer)
                + "}\n"
            )
        parts.append("\n")
    parts.append("\\end{document}\n")
    out_path.write_text("".join(parts), encoding="utf-8")


def compile_pdf(project_dir: Path, tex_path: Path, out_pdf: Path) -> None:
    cmd = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", tex_path.name]
    subprocess.check_call(cmd, cwd=project_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(cmd, cwd=project_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    produced = project_dir / (tex_path.stem + ".pdf")
    if not produced.exists():
        raise RuntimeError(f"PDF not produced: {produced}")
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(produced, out_pdf)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Forecast LaTeX + PDFs from raw_XX markdown.")
    parser.add_argument("--raw-dir", type=Path, required=True, help="Directory containing ANS_PART_*.md")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output project directory (e.g. Forecast/forecast01)")
    parser.add_argument("--compile", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--lexicon", type=Path, default=None, help="Optional CSV: term,pos,ipa to fill vocab fields")
    args = parser.parse_args()

    out_dir: Path = args.out_dir
    raw_dir: Path = args.raw_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_p1 = (raw_dir / "ANS_PART_1.md").read_text(encoding="utf-8")
    raw_p2 = (raw_dir / "ANS_PART_2.md").read_text(encoding="utf-8")
    raw_p3 = (raw_dir / "ANS_PART_3.md").read_text(encoding="utf-8")
    out_p23_path = out_dir / "raw" / "ANS_PART_23.md"
    raw_p23_path = raw_dir / "ANS_PART_23.md"
    raw_p23 = out_p23_path.read_text(encoding="utf-8") if out_p23_path.exists() else ""
    if not raw_p23.strip() and raw_p23_path.exists():
        raw_p23 = raw_p23_path.read_text(encoding="utf-8")

    p1_topics = parse_part1(raw_p1)
    p2_topics = parse_part2(raw_p2)
    p3_topics, _p3_vocab = parse_part3(raw_p3)

    tex1 = out_dir / "forecast01_part1.tex"
    tex23 = out_dir / "forecast01_part23.tex"
    merged_raw_out = out_dir / "raw" / "ANS_PART_23.md"
    merged_raw_out_repo = raw_dir / "ANS_PART_23.md"

    write_part1_tex(p1_topics, tex1)
    if not raw_p23.strip():
        write_part23_merged_raw(p2_topics, p3_topics, merged_raw_out_repo)
        raw_p23 = merged_raw_out_repo.read_text(encoding="utf-8")

    if not merged_raw_out.exists() or not merged_raw_out.read_text(encoding="utf-8").strip():
        write_part23_merged_raw(p2_topics, p3_topics, merged_raw_out)

    topics23 = parse_part23_merged(raw_p23)
    write_lexicon_template(topics23, out_dir / "raw" / "lexicon_template.csv")
    if args.lexicon:
        topics23 = apply_lexicon(topics23, read_lexicon_csv(args.lexicon))
    write_part23_interleaved_tex(topics23, tex23)

    if args.compile:
        compile_pdf(out_dir, tex1, out_dir / "output" / "forecast01_part1.pdf")
        compile_pdf(out_dir, tex23, out_dir / "output" / "forecast01_part23.pdf")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
