# LaTeX (PDF) pipeline từ Markdown (cùng MD dùng cho DOCX)

Mục tiêu: dùng **chung 1 nguồn Markdown** (`chuyenDe/RW/md/raw47/...`) để xuất ra **PDF theo template LaTeX** (header/footer/watermark giống hệ `chuyên đề`), trong khi DOCX vẫn dùng Word reference template.

## 1) Thành phần chính

- Base template (header/footer/watermark + box macros): `chuyenDe/common/workshop-base.tex`
- Class:
  - Reading: `chuyenDe/RW/templateReading/cdreading.cls`
  - Writing: `chuyenDe/RW/templateWriting/cdwriting.cls`
- Pandoc LaTeX filter (map component Markdown → LaTeX macros/table): `chuyenDe/latex/pandoc/cd-forum-latex.lua`
- Script build PDF từ Markdown: `chuyenDe/latex/md_to_pdf.sh`

## 2) Cách build PDF từ Markdown

Yêu cầu:
- `pandoc`
- `xelatex` (TeX Live/MacTeX)

Ví dụ:

```bash
bash chuyenDe/latex/md_to_pdf.sh chuyenDe/RW/md/raw47/Reading/Level1/W5.md /tmp/Reading-L1-W5.pdf Reading
```

Nếu frontmatter có `skill: Reading|Writing` thì có thể bỏ arg thứ 3:

```bash
bash chuyenDe/latex/md_to_pdf.sh chuyenDe/RW/md/raw47/Writing/Level1/W4.md /tmp/Writing-L1-W4.pdf
```

## 3) Mapping component Markdown → LaTeX

Filter `cd-forum-latex.lua` hỗ trợ các cấu trúc đang dùng trong Markdown (docx pipeline):

- Heading:
  - `## ...` → `\cdsection{...}`
  - `### ...` → `\cdstep{...}`
  - `#### ...` → `\cdgreenheading{...}`
- Note:
  - blockquote `> ...` → `\begin{cdnote}...\end{cdnote}`
- Inline color:
  - `[text]{.cdred}` → `\cdred{...}` (tương tự `cdblue/cdgreen/cdpurple`)
- Cụm câu hỏi:
  - `::: cdquestions ... :::` → `\begin{cdquestions}...\end{cdquestions}` (giảm spacing)
- Bảng trong fenced div:
  - `::: cdoptiontable` → bảng 2 cột (Option/Meaning), có line + header nền xanh
  - `::: cdchoicetable` → bảng A–F (Option/Person)
  - `::: cdanswertable` → bảng 3 cột (Câu/Phân tích/Đáp án)
  - `::: cdanswerkeytable` → bảng đáp án tổng hợp
  - `::: cdreadingvocabtable` → bảng tổng hợp vocab 4 cột
  - `::: cdvocabtable` → bảng 2 cột chung (Heading/Title,…)

Ghi chú:
- Các bảng thường dùng `tabularx` để tự co giãn theo `\linewidth`; các bảng dài (cần ngắt trang) dùng `longtable` để không tràn xuống footer và có thể chia qua nhiều trang.
- Nên có **một dòng trống trước bảng** trong Markdown để Pandoc parse “pipe table” ổn định.

## 4) Nếu raw Word thay đổi cấu trúc

Bạn vẫn có thể tách ra Markdown như pipeline hiện tại, rồi build PDF từ Markdown.
Khi cần thêm component mới:
1) Tạo fenced div/span mới trong Markdown.
2) Map nó trong `chuyenDe/latex/pandoc/cd-forum-latex.lua` (Div/Span/Header).
3) Nếu cần macro/table style mới, thêm vào `chuyenDe/common/workshop-base.tex`.
