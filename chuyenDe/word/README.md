# Word template (editable) + mapping từ Markdown

Mục tiêu: bạn soạn/chỉnh sửa nhiều bằng Word, nhưng vẫn giữ “ngôn ngữ hình ảnh” gần giống template LaTeX (màu/box/header/footer/watermark).

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

## 2) Convert Markdown → DOCX (giữ styles)

Yêu cầu: cài Pandoc trên máy của bạn.
- macOS: `brew install pandoc`

Script:
- `chuyenDe/word/pandoc/md_to_docx.sh`

Ví dụ:
- Writing: `bash chuyenDe/word/pandoc/md_to_docx.sh chuyenDe/word/example.md /tmp/out.docx chuyenDe/word/reference-writing.docx`
- Reading: `bash chuyenDe/word/pandoc/md_to_docx.sh chuyenDe/word/example.md /tmp/out.docx chuyenDe/word/reference-reading.docx`

## 3) Quy ước viết Markdown để map đúng component

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

## 4) Export raw47 (Writing + Reading, theo Level/Week)

- Tách raw47 → Markdown: `python3 chuyenDe/scripts/raw47_to_markdown.py`
  - Output: `chuyenDe/RW/md/raw47/<Skill>/Level<level>/W<week>.md`
- Export Markdown → DOCX (dùng đúng reference template):
  - `bash chuyenDe/scripts/raw47_to_word.sh`
  - Output: `chuyenDe/RW/docx/raw47/<Skill>/Level<level>/W<week>.docx`
