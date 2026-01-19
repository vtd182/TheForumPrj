# IELTS Vocabulary Template (XeLaTeX) — Hướng dẫn sử dụng

Template này tạo PDF vocabulary 2 cột, có header/footer theo đúng layout, kèm watermark logo ở nền.

## Cấu trúc thư mục

Trong `Vocab/template/`:

- `forumvocab.cls` — file class chứa toàn bộ style/layout (thường chỉ chỉnh ở đây khi muốn đổi design)
- `main.tex` — file chính để compile (chỉnh title/author/topic)
- `data.tex` — dữ liệu từ vựng (thêm/sửa nội dung)
- `UTM-Impact.ttf` — font cho tiêu đề “IELTS VOCABULARY”
- `scripts/check_watermark_consistency.py` — script kiểm tra watermark page 1 vs page 2 (tuỳ chọn)

Watermark logo nằm ở `Vocab/wm/logoTF.png` (được load từ `Vocab/template/forumvocab.cls` qua đường dẫn `../wm/logoTF.png`).

Font chính của tài liệu được lấy từ thư mục `font/` ở root repo:

- `font/latin-modern-roman/` (cho nội dung trong `data.tex`)
- `font/Latin-Modern-Sans/` (cho các phần dùng `\sffamily`: header, nhãn, số trang,…)

Nếu bạn muốn đóng gói font ngay trong template, bạn có thể tạo `@font/` và đặt cấu trúc tương tự; class sẽ tự dò (fallback theo thứ tự) `./@font`, `../../@font`, `../../font`, `./font`.

## Cách dùng nhanh

### 1) Cập nhật thông tin trong `main.tex`

Mở `Vocab/template/main.tex` và chỉnh 3 biến:

```latex
\newcommand{\authorinfo}{...}
\newcommand{\documenttitle}{...}
\newcommand{\topictitle}{TỪ VỰNG CHỦ ĐỀ: ...}
```

- `\authorinfo`: góc trái header trang đầu
- `\documenttitle`: góc phải header trang đầu
- `\topictitle`: dòng chủ đề (đã được căn giữa)

### 2) Nhập dữ liệu từ vựng trong `data.tex`

Template hỗ trợ 2 dạng:

**Đầy đủ (có ví dụ):**
```latex
\vocabentry{word}
{/pronunciation/ (pos)}
{Definition (nghĩa tiếng Việt)}
{Example sentence in English.}
{Dịch ví dụ tiếng Việt.}
```

**Ngắn (không có ví dụ):**
```latex
\vocabshort{word}
{/pronunciation/ (pos)}
{Definition (nghĩa tiếng Việt)}
```

Format hiển thị: `từ + IPA + nghĩa` trên cùng 1 dòng (nếu dài sẽ tự xuống dòng tự nhiên).

### 3) Compile PDF (bắt buộc XeLaTeX)

```bash
cd Vocab/template
xelatex main.tex
```

Nếu bạn chỉnh TikZ/header và thấy chưa cập nhật đúng, chạy thêm lần 2:

```bash
xelatex main.tex
```

## Tuỳ chỉnh nâng cao

### Đổi logo watermark

- Thay ảnh `Vocab/wm/logoTF.png` (giữ đúng tên file), hoặc
- Sửa đường dẫn/scale trong `Vocab/template/forumvocab.cls` (tìm `logoTF.png`).

Opacity watermark nằm ở `node[opacity=0.15]`.

### Fix IPA bị “trắng”/không hiển thị

Template dùng font fallback riêng cho IPA để tránh thiếu glyph. Ưu tiên:

1. `Charis SIL`
2. `Doulos SIL`
3. `Gentium Plus`
4. `Noto Serif` / `Noto Sans`
5. `Times New Roman`

Nếu máy bạn chưa có các font SIL/Noto, nên cài `Charis SIL` để IPA đẹp và đầy đủ nhất.

### Đổi màu chủ đạo / size số trang

Màu chính nằm trong `Vocab/template/forumvocab.cls`:

```latex
\definecolor{forumred}{HTML}{E52B20}
```

Số trang dùng macro:

```latex
\newcommand{\forumvocab@pagenumfont}{...}
```

Bạn có thể chỉnh `\fontsize{...}{...}` hoặc bỏ `\bfseries` tuỳ ý.

### Thêm tiêu đề nhóm (tuỳ chọn)

Trong `data.tex`:

```latex
\vocabsection{Academic Words — Group 1}
```

## Kiểm tra nhanh (tuỳ chọn)

Nếu có `gs` (Ghostscript) và Python 3:

```bash
python3 Vocab/template/scripts/check_watermark_consistency.py Vocab/template/main.pdf
```

Script sẽ báo tỷ lệ “độ đậm” watermark giữa trang 1 và 2 (để tránh lỗi page 1 bị đậm hơn).

## Troubleshooting

- **Compile lỗi font**: kiểm tra thư mục `font/latin-modern-roman` và `font/Latin-Modern-Sans` có tồn tại (hoặc dùng `@font/`), và bạn đang compile bằng `xelatex`.
- **IPA bị thiếu ký tự**: cài `Charis SIL` (khuyến nghị), sau đó build lại.
- **Watermark trang 1 đậm hơn**: chạy script kiểm tra ở trên; nếu bạn có chỉnh phần watermark/shipout, hãy báo mình vị trí chỉnh để mình kiểm lại.
