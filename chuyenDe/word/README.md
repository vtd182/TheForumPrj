# Word template (editable) + mapping từ Markdown (RW: Reading/Writing)

Mục tiêu: bạn soạn/chỉnh sửa nhiều bằng Word, nhưng vẫn giữ “ngôn ngữ hình ảnh” gần giống template LaTeX (màu/box/header/footer/watermark).

Repo này làm 2 việc:
- Tạo **Word reference template** (`reference-*.docx`) bằng code (để đồng bộ style/margin/header/footer/watermark).
- Convert **Markdown → DOCX** qua Pandoc + Lua filter (để “map” đúng component/style).

Ngoài ra có pipeline “raw Word → Markdown → DOCX” cho bộ `raw47`.

---

## 0) Pipeline tổng thể (raw Word → MD → DOCX)

### Input/Output
- Input “raw Word”: `chuyenDe/raw47/*.docx`
- Output Markdown: `chuyenDe/RW/md/raw47/<Skill>/Level<level>/W<week>.md`
- Output DOCX: `chuyenDe/RW/docx/raw47/<Skill>/Level<level>/W<week>.docx`

### Luồng xử lý
1) **Parse raw DOCX** → list paragraph + level của bullet/numbering  
   - `chuyenDe/scripts/generate_from_raw47.py` (`extract_paragraphs()`)
2) **Split theo section** (Wk/Level/Skill)  
   - `split_sections()` dựa trên dòng header dạng: `W7 (Feb 9-15): Reading` / `Writing`
3) **Render Markdown** (normalize whitespace, detect headings/questions/tables)  
   - `chuyenDe/scripts/raw47_to_markdown.py`
4) **MD → DOCX** bằng Pandoc reference docx + Lua filter (map style)  
   - `chuyenDe/word/pandoc/md_to_docx.sh`
   - Filter: `chuyenDe/word/pandoc/cd-forum.lua`
5) **Postprocess DOCX** (fix width/indent/grid cho các bảng)  
   - `chuyenDe/scripts/postprocess_docx_tables.py`

Chạy 1 phát full pipeline:
- `bash chuyenDe/scripts/raw47_to_word.sh`

Chỉ regen DOCX từ Markdown (không tách raw Word, không rebuild reference):
- `bash chuyenDe/scripts/raw47_md_to_word.sh`

## 1) Tạo Word template (`reference-*.docx`)

File generator:
- `chuyenDe/word/build_reference_docx.py`

Chạy:
- `python3 chuyenDe/word/build_reference_docx.py`

Output:
- `chuyenDe/word/reference-writing.docx`
- `chuyenDe/word/reference-reading.docx`
- `chuyenDe/word/reference.docx` (legacy, mặc định Writing)

`reference.docx` có:
- watermark logo (logoTF.png) đặt trong header (VML)
- header trang 1 (khối đỏ + title + author/doctype)
- header các trang khác (đường đỏ + badge đơn giản)
- footer (số trang + thanh đỏ)
- các styles cho component (Prompt/Section/Step/Note + màu inline)

Ghi chú thiết kế quan trọng:
- Body font mặc định: **Georgia** (docDefaults + Normal).
- Heading/Title dùng **Latin Modern Sans** (để “giống LaTeX”).
- Header trang 1 “IELTS WORKSHOP”: **Impact**, size **72**.
- Header/footer “full giấy” (bằng table + negative indent), trong khi content giữ lề 2cm.
- Watermark đã được làm nhạt (opacity/gain/blacklevel trong VML) để giảm “đậm” khi export PDF.

## 1.1) Cài font để không bị fallback

Template Word đang dùng các font “giống LaTeX” cho header/title/component (ví dụ `Latin Modern Sans`, `UTM Impact`). Nếu máy bạn chưa cài `Latin Modern Sans` thì Word sẽ tự fallback sang font khác (thường là UTM/Arial), nhìn sẽ lệch.

- Font trong repo:
  - `font/Latin-Modern-Sans/*.otf`
  - `font/latin-modern-roman/*.otf`
  - `font/UTM-Impact.ttf`
- macOS: mở từng file font → **Install** (Font Book), rồi **Quit Word (Cmd+Q)** và mở lại.
- Windows: chọn các file font → **Install for all users**, rồi mở lại Word.

## 2) Convert Markdown → DOCX (giữ styles)

Yêu cầu: cài Pandoc trên máy của bạn.
- macOS: `brew install pandoc`

Script:
- `chuyenDe/word/pandoc/md_to_docx.sh`

Ví dụ:
- Writing: `bash chuyenDe/word/pandoc/md_to_docx.sh chuyenDe/word/example.md /tmp/out.docx chuyenDe/word/reference-writing.docx`
- Reading: `bash chuyenDe/word/pandoc/md_to_docx.sh chuyenDe/word/example.md /tmp/out.docx chuyenDe/word/reference-reading.docx`

Pandoc options đang dùng:
- Input: `markdown+raw_attribute+fenced_divs+bracketed_spans`
- Filter Lua để map `class`/`custom-style` sang Word style.

## 3) Quy ước viết Markdown để map đúng component

Nguyên tắc:
- Dùng **fenced Div** (`::: <class> ... :::`) để gắn “component”.
- Dùng **Span class** (`[text]{.cdblue}`) để gắn màu inline.
- Với **Markdown table kiểu pipe**, luôn để **một dòng trống** trước `::: ...` để Pandoc parse table ổn định.

### Prompt box

```md
::: prompt
Nội dung prompt...
:::
```

### Section / Step / Green heading

- `## ...` → `CD Section`
- `### ...` → `CD Step`
- `#### ...` → `CD Green Heading`

### Collection title (dòng tiêu đề giữa header và nội dung)

```md
::: collectiontitle
Level 1 — W4 (01/01–07/01)
:::
```

### Note

- Blockquote `> ...` → `CD Note`
- Hoặc:

```md
::: cdnote
Nội dung note...
:::
```

### Màu inline

```md
[đỏ]{.cdred} [xanh dương]{.cdblue} [xanh lá]{.cdgreen} [tím]{.cdpurple}
```

---

## 3.1) Component dành cho Reading (câu hỏi + bảng)

### Cụm câu hỏi (1 dòng/1 câu, không bullet)

```md
::: cdquestions
**1.** Question text...  
**2.** Question text...
:::
```

Trong DOCX: `cdquestions` được map sang paragraph style `CDQuestion` (giảm spacing).

### Bảng TRUE/FALSE/NOT GIVEN (căn giữa, dùng cho instructions)

```md
::: cdoptiontable
| Option | Meaning |
| --- | --- |
| **TRUE** | the statement is true |
| **FALSE** | the statement is false |
| **NOT GIVEN** | the information is not given in the passage |
:::
```

Trong DOCX: style `CDOptionTable`, được postprocess để `w:jc=center`.

### Bảng A–F “Option / Person-Choice” (thụt trái, full width trong content)

```md
::: cdchoicetable
| **Option** | **Person/Choice** |
| --- | --- |
| **A** | Jim Bowler |
| **B** | Alan Thorne |
:::
```

### Bảng “Đối chiếu và Kết luận Đáp án” (Câu / Phân tích / Đáp án)

```md
::: cdanswertable
| Câu | Phân tích và Dẫn chứng | Đáp án |
| --- | --- | --- |
| **21** | ... | **5 million** |
:::
```

### Bảng đáp án tổng hợp (tự thêm ở cuối mỗi Reading)

```md
::: cdanswerkeytable
| Câu | Đáp án |
| --- | --- |
| **14** | **x** |
:::
```

### Tổng hợp từ vựng cuối bài (tự thêm ở cuối mỗi Reading)

```md
::: cdreadingvocabtable
| Từ vựng (Từ loại) | Phiên âm | Nghĩa tiếng Anh (Giải thích chi tiết nghĩa tiếng Việt) | Ví dụ minh họa |
| --- | --- | --- | --- |
| **exemplary** | /ɪɡˈzempləri/ | serving as a perfect example (Giải thích...) | ... |
:::
```

Hiện tại pipeline sẽ lấy từ mục `Glossary` trong Reading (dạng `term: definition`) và đổ vào bảng này (chưa tự có “từ loại/phiên âm/ví dụ” nếu raw không có).

## 4) Export raw47 (Writing + Reading, theo Level/Week)

- Tách raw47 → Markdown: `python3 chuyenDe/scripts/raw47_to_markdown.py`
  - Output: `chuyenDe/RW/md/raw47/<Skill>/Level<level>/W<week>.md`
- Export Markdown → DOCX (dùng đúng reference template):
  - `bash chuyenDe/scripts/raw47_to_word.sh`
  - Output: `chuyenDe/RW/docx/raw47/<Skill>/Level<level>/W<week>.docx`

---

## 5) Hướng dẫn mở rộng cho “raw Word cấu trúc khác”

### 5.1) Split section (W/Level/Skill)
Nếu raw Word khác format header, hãy sửa regex trong:
- `chuyenDe/scripts/generate_from_raw47.py` (`HEADER_RE`)

Yêu cầu tối thiểu để split đúng:
- Có một dòng đánh dấu “bắt đầu section” chứa: tuần + ngày + skill (Reading/Writing).

### 5.2) Heuristic nhận diện heading / questions / bảng
Các “luật” chính nằm ở:
- `chuyenDe/scripts/raw47_to_markdown.py`
  - `_writing_heading_level()` / `_reading_heading_level()`
  - detect instruction stems → blockquote
  - detect TFNG options → `cdoptiontable`
  - detect A–F choices → `cdchoicetable`
  - detect numbered questions → `cdquestions`
  - detect “Đối chiếu…” → `cdanswertable`

Khi raw Word thay đổi cách trình bày, thường chỉ cần điều chỉnh regex/heurstic ở file này.

### 5.3) Thêm component mới (chuẩn cho AI khác làm theo)
Muốn thêm `::: mycomponent` map sang style Word:
1) **Thêm style** vào template generator: `chuyenDe/word/build_reference_docx.py` (styles.xml)
2) **Map class → style** trong filter: `chuyenDe/word/pandoc/cd-forum.lua` (`TABLE_STYLE`/`BLOCK_STYLE`/`SPAN_STYLE`)
3) Nếu là **table** và cần fix width/indent/grid, thêm rule vào: `chuyenDe/scripts/postprocess_docx_tables.py`
4) Emit markdown đúng chuẩn trong generator (nếu auto): `chuyenDe/scripts/raw47_to_markdown.py`
