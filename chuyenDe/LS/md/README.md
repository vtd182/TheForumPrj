# Listening & Speaking Markdown Files - Formatting Guidelines

---

## 🚨 RULE SỐ 1 — TUYỆT ĐỐI KHÔNG CẮT BỚT NỘI DUNG (ÁP DỤNG CHO CẢ 4 KỸ NĂNG)

> **Đây là rule ưu tiên cao nhất. Bất kỳ thao tác format nào cũng phải tuân thủ rule này trước.**

Khi chuyển đổi từ raw DOCX → Markdown, **100% nội dung phải được giữ nguyên**:

- ❌ KHÔNG tóm tắt, rút gọn, gộp, hay bỏ bớt bất kỳ phần nào
- ❌ KHÔNG bỏ qua phân tích câu hỏi nào — kể cả phân tích options sai (A/B/C/D/E)
- ❌ KHÔNG đổi thứ tự thông tin so với file gốc
- ✅ CHỈ được thêm formatting (heading, table, container) và từ vựng bổ sung

### Nội dung hay bị bỏ sót nhầm

| Kỹ năng | Thường bị cắt — CẦN GIỮ ĐỦ |
|---|---|
| **Listening** | Per-question keyword; option-by-option analysis (A/B/C kể cả sai); map landmark; trap warnings; note-taking examples với ví dụ tờ nháp mô phỏng |
| **Speaking** | Công thức mở rộng ý (Contrast/Hypothetical); phân tích tiêu chí từng band; toàn bộ bài mẫu; từ vựng kèm ví dụ cụ thể |
| **Reading** | "Từ khóa cần tìm", "Dẫn chứng trong bài", "Giải thích" trong MỖI câu; phân tích CÁC options sai |
| **Writing** | Chi tiết brainstorming từng phe; phân tích từng từ vựng với ví dụ; tất cả công thức và chiến thuật |

### Format bắt buộc khi phân tích từng câu hỏi (Listening)

```markdown
- **Câu N:**

    - **Từ khóa cần tìm:** keyword1, keyword2, ...
    - Audio: [quote nguyên văn từ transcript]
    - Option A: ... → phân tích → ✔/✘
    - Option B: ... → phân tích → ✔/✘
    - Option C: ... → phân tích → ✔/✘
```

### Checklist trước khi gen DOCX

- [ ] Tất cả câu hỏi (Q1..Qlast) có mặt + đúng số thứ tự?
- [ ] Transcript đầy đủ, không cắt đoạn nào?
- [ ] Mỗi option (kể cả sai) được giải thích riêng?
- [ ] Map landmark (nếu có) được mô tả đầy đủ?
- [ ] Thứ tự các phần đúng như file gốc?

> Xem thêm chi tiết trong `chuyenDe/AGENT.md`

---



Khi cần format hoặc kiểm tra lại cấu trúc Listening MD, hãy tham chiếu **2 bộ file sau** làm chuẩn:

| Bộ tài liệu | Đường dẫn MD | Đường dẫn DOCX |
|---|---|---|
| **W8** (rawls7) | `chuyenDe/LS/md/rawls7/Listening/` | `chuyenDe/LS/docx/rawls7/Listening/` |
| **W12** (rawl12) | `chuyenDe/LS/md/rawl12/Listening/` | `chuyenDe/LS/docx/rawl12/Listening/` |

## 📌 Tham chiếu Format chuẩn — Speaking

Khi cần format hoặc kiểm tra lại cấu trúc Speaking MD, hãy tham chiếu **bộ file sau** làm chuẩn:

| Bộ tài liệu | Đường dẫn MD | Đường dẫn DOCX |
|---|---|---|
| **W11** (raws11) | `chuyenDe/LS/md/raws11/Speaking/` | `chuyenDe/LS/docx/raws11/Speaking/` |
| **W13** (raws13) | `chuyenDe/LS/md/raws13/Speaking/` | `chuyenDe/LS/docx/raws13/Speaking/` |

> **Quy tắc:** Mọi file Speaking mới đều phải match cấu trúc của W11/W13 trước khi gen DOCX.

---

## ⚠️ Quy tắc bắt buộc khi format Speaking MD

### 1. KHÔNG ĐƯỢC cắt bớt thông tin từ DOCX gốc

Khi pandoc extract từ DOCX raw, **toàn bộ nội dung phải được giữ nguyên** — không được tóm tắt, bỏ bớt, hay gộp các phần lại. Thứ tự thông tin phải giữ **đúng trật tự gốc** trong file DOCX.

Các thông tin quan trọng hay bị bỏ sót:
- Phần **chi tiết Brainstorming** và **kỹ thuật mở rộng ý**
- Phần phân tích từng từ vựng (bullet có *Ví dụ:* cụ thể) trong mục "Từ vựng gợi ý"
- **Công thức** và **Phân tích** trong mỗi câu hỏi Part 1/Part 3
- Các **chiến thuật** tổng hợp cuối phần tiêu chí

### 2. KHÔNG dùng `>` blockquote cho ghi chú thông thường

Trong file Word được gen từ pandoc, `>` blockquote → Style **CD Note** (màu **tím** — `#7A1FA2`, nền `#F6F0FA`).

Tuy nhiên, tránh dùng `>` quá nhiều vì nó tạo màu nổi bật không phù hợp với các ghi chú thông thường. Chỉ dùng `>` cho:
- Lưu ý quan trọng thực sự cần nhấn mạnh
- Quy tắc hoặc cảnh báo critical

Với các nội dung ghi chú bình thường (chiến thuật, tip), dùng bullet list thông thường hoặc heading.

### 3. Heading level map → màu sắc trong Word

| Markdown | Word Style | Màu |
|---|---|---|
| `##` | CD Section | Đỏ (`#E52B20`), nền xám nhạt |
| `###` | CD Step | Xanh dương (`#1F4E79`), nền xanh nhạt |
| `####` | CD Green Heading | **Xanh lá** (`#5AA244`) ← tránh dùng quá nhiều |
| `>` blockquote | CD Note | **Tím** (`#7A1FA2`), nền tím nhạt |

**Nguyên tắc:** Dùng `##` cho các phần chính (I, II, III, IV), dùng `###` cho câu hỏi và sub-section, dùng `####` chỉ khi thực sự cần nhấn mạnh một sub-sub-section.



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
