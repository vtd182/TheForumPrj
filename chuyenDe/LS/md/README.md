# Listening Markdown Files - Formatting Guidelines

## 📌 Tham chiếu Format chuẩn (Reference Files)

Khi cần format hoặc kiểm tra lại cấu trúc Listening MD, hãy tham chiếu **2 bộ file sau** làm chuẩn:

| Bộ tài liệu | Đường dẫn MD | Đường dẫn DOCX |
|---|---|---|
| **W8** (rawls7) | `chuyenDe/LS/md/rawls7/Listening/` | `chuyenDe/LS/docx/rawls7/Listening/` |
| **W12** (rawl12) | `chuyenDe/LS/md/rawl12/Listening/` | `chuyenDe/LS/docx/rawl12/Listening/` |

Cả hai bộ đều có đủ Level 1, 2, 3 và bao gồm đầy đủ các dạng:
- **Section 1:** Form completion (dialogue 2 người → `cdtranscripttable`)
- **Section 2:** Monologue + Multiple Choice/Matching (plain text)
- **Section 3:** Dialogue học thuật 2-3 người → `cdtranscripttable`
- **Section 4:** Monologue học thuật (plain text)

> **Quy tắc:** Mọi file Listening mới đều phải match cấu trúc của W8/W12 trước khi gen DOCX.

---

## Transcript Formatting Rules

### Auto-Detection: Dialogue vs Monologue

The transcript conversion script automatically detects whether a section contains:
- **Dialogue** (2+ speakers) → Convert to 2-column table
- **Monologue** (1 speaker) → Keep plain text format

**Examples:**

#### Dialogue (2+ speakers) → Table Format
```markdown
SECTION 1

::: cdtranscripttable
| Speaker | Dialogue |
|---------|----------|
| ANGELA | Hello, Flanders conference hotel. |
| MAN | Oh, hi. I wanted to ask about... |
:::
```

#### Monologue (1 speaker) → Plain Text
```markdown
SECTION 2

Good morning. My name's Mark Bergin...
(continues in plain text)
```

### Important Rules

1. **Plain text for monologues** - Do NOT convert single-speaker sections to tables
2. **Table for dialogues only** - Only use `::: cdtranscripttable` when 2+ speakers detected
3. **Preserve speaker names** - Keep original UPPERCASE speaker labels (MAN, WOMAN, LIZ, etc.)
4. **No empty cells** - Each dialogue row must have both speaker and content
5. **Section headers are plain text** - Write "SECTION 1", "SECTION 2" as plain text (no `##` heading) inside the transcript block

## Section Container Guidelines

### Structure Overview

Each MD file follows this **exact** top-level structure:

```
frontmatter (---)
::: collectiontitle ... :::
::: cdlisteningsection          ← SECTION X exam questions ONLY
  ## SECTION X Question N -- M
  [questions]
:::
::: cdlisteningsection          ← next SECTION exam questions ONLY
  ## SECTION X
  [questions]
:::
## Phần 1: Section X            ← Analysis OUTSIDE cdlisteningsection
  [hướng dẫn + phân tích]
## Phần 2: Section X            ← Analysis OUTSIDE cdlisteningsection
  [hướng dẫn + phân tích]
## Phần 3: Lời giải -- Answer Key   ← OUTSIDE (plain text)
## Phần 4: Lời băng -- Transcript   ← OUTSIDE (cdtranscriptsection wrapper)
## Từ vựng                           ← OUTSIDE (cdreadingvocabtable)
```

### What Goes INSIDE `cdlisteningsection`

**Only** the exam question blocks:

```markdown
::: cdlisteningsection

## SECTION 1 Question 1 -- 10

Complete the form below.

Write **ONE WORD AND/OR A NUMBER** for each answer.

[questions, options, tables...]

:::
```

### What Goes OUTSIDE `cdlisteningsection`

Everything else is placed **outside** the containers:

| Block | Container used |
|---|---|
| `## Phần X: Section X` (analysis) | None — plain markdown |
| `## Phần X: Lời giải -- Answer Key` | None — plain text list |
| `## Phần X: Lời băng -- Transcript` | `cdtranscriptsection` wraps the whole transcript part |
| `## Từ vựng` | `cdreadingvocabtable` |

## Transcript Section Wrapper

The **entire** transcript part (all sections combined) is wrapped in a single `cdtranscriptsection`:

```markdown
## Phần 4: Lời băng -- Transcript

::: cdtranscriptsection

SECTION 1

::: cdtranscripttable
| Speaker | Dialogue |
|---------|----------|
| MAN | Hello. |
| WOMAN | ... |
:::

SECTION 2

Good morning. My name's Mark Bergin. I'm a Human Resources Manager...
(plain text monologue)

:::
```

## Answer Key Format

Answer keys use **plain numbered list** — no tables, no bold wrappers:

```markdown
## Phần 3: Lời giải -- Answer Key

### Section 1

1\. instructor

2\. 65

3\. certificate

### Section 2

11\. B

12\. A
```

## Visual Styling

- **Section containers** (`cdlisteningsection`): Red borders with 3D shadow
- **SECTION headers**: Centered, 14pt, blue
- **CDStep spacing**: Increased to prevent sticking
- **Transcript tables** (`cdtranscripttable`): Alternating row colors (#F5F5F5)
- **Vocab tables** (`cdreadingvocabtable`): 4 columns — Word, IPA, English meaning + Vietnamese, Example
