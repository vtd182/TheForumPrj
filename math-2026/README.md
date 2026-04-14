# 📘 math-2026 — Tuyển tập các câu hay và khó (Thi thử THPT QG 2026)

> **Mục tiêu**: Tổng hợp & biên soạn lại các câu hay, khó từ đề thi thử của các **trường** và **sở GD&ĐT** trên cả nước, trình bày dưới dạng tài liệu LaTeX chuyên nghiệp.

---

## 📂 Cấu trúc thư mục

```
math-2026/
│
├── README.md                  # 📖 File hướng dẫn này (source of truth)
├── .gitignore                 # Git ignore cho build artifacts
├── toanTHPTQG.pdf             # PDF mẫu gốc (template tham khảo)
│
├── main.tex                   # Entry point LaTeX
├── preamble.tex               # Packages + import modules (KHÔNG chứa logic)
│
├── styles/                    # 🎨 Thiết kế — tách riêng từng mối quan tâm
│   ├── colors.tex             #   Bảng màu (ForumDarkBlue, TikzCurve1, ...)
│   ├── environments.tex       #   tcolorbox environments (baitoan, loigiai, ...)
│   └── commands.tex           #   Custom commands (dapan, tagNguon, macros)
│
├── tikz/                      # ✏️ TikZ drawing library
│   ├── lib/
│   │   └── tikz-math.tex      #   Core: BBT, đồ thị, HHKG, số phức, XS
│   └── examples.tex           #   Cheatsheet 9 ví dụ (chỉ tham khảo)
│
├── sections/                  # 📄 Các phần cố định (không phải chapters)
│   ├── coverpage.tex          #   Trang bìa (TikZ overlay)
│   ├── frontmatter.tex        #   Mục lục, lời nói đầu, hướng dẫn sử dụng
│   └── backmatter.tex         #   Bảng đáp số, lộ trình ôn tập
│
├── chapters/                  # 📚 Nội dung chính — mỗi chủ đề 1 file
│   ├── chuong01.tex           #   Ch.1: Hàm số và ứng dụng (có bài mẫu)
│   ├── chuong02.tex           #   Ch.2: Mũ — Logarit
│   ├── chuong03.tex           #   Ch.3: Tích phân
│   ├── chuong04.tex           #   Ch.4: Số phức
│   ├── chuong05.tex           #   Ch.5: Hình học không gian
│   └── chuong06.tex           #   Ch.6: Xác suất — Thống kê
│
├── raw/                       # 📥 Đề thi gốc dạng Markdown
│   └── (đề thi .md sẽ đặt ở đây)
│
├── images/                    # 🖼️ Hình ảnh (graphicspath đã set)
│
└── build/                     # 📦 Output (git ignored)
    └── main.pdf
```

### Nguyên tắc tổ chức

| Nguyên tắc | Giải thích |
|-------------|------------|
| **Separation of Concerns** | `styles/` tách colors, environments, commands riêng |
| **Modular preamble** | `preamble.tex` chỉ `\input` modules, không định nghĩa inline |
| **Sections vs Chapters** | `sections/` = phần cố định (cover, front/back); `chapters/` = nội dung bài |
| **TikZ tách riêng** | `tikz/lib/` cho macros, `tikz/examples.tex` cho cheatsheet |
| **Raw input riêng** | `raw/` chứa Markdown gốc, không trộn với LaTeX output |

---

## 🔧 Workflow (Quy trình làm việc)

### Bước 1: Nhận raw (đề thi + lời giải) dạng Markdown
- Đề thi và lời giải được cung cấp dưới dạng file `.md` trong thư mục `raw/`.
- Mỗi file `.md` chứa các câu hỏi + đáp án + lời giải chi tiết.
- Có thể kèm mô tả đồ thị / bảng biến thiên cần vẽ.

### Bước 2: Agent format & render vào template LaTeX
- Agent đọc file `.md`, trích xuất các câu hỏi, phân loại theo chủ đề.
- Chuyển đổi sang LaTeX sử dụng các environment đã định nghĩa trong `styles/`.
- **Vẽ TikZ** cho đồ thị, BBT, hình học theo `tikz/lib/tikz-math.tex`.
- Thêm vào file chương tương ứng trong `chapters/`.

### Bước 3: Compile & Review
```bash
# Compile với XeLaTeX (cần chạy 2 lần để TOC đúng)
export PATH="/Library/TeX/texbin:$PATH"
cd math-2026
xelatex -interaction=nonstopmode -output-directory=build main.tex
xelatex -interaction=nonstopmode -output-directory=build main.tex
```

---

## 🎨 Template Conventions (Quy ước template)

### Màu sắc chủ đạo
| Tên | Mã màu | Sử dụng |
|-----|---------|---------|
| `ForumDarkBlue` | `#1B3A5C` | Thanh tiêu đề bài, header |
| `ForumMidBlue` | `#2E6DA4` | Section titles, box borders |
| `ForumLightBlue` | `#D6EAF8` | Nền box lời giải, prompt |
| `ForumOrange` | `#E67E22` | Tag nguồn, accent |
| `ForumGold` | `#F39C12` | Highlight, tag mức độ |
| `ForumGreen` | `#27AE60` | Đáp án đúng, tips |
| `ForumRed` | `#E74C3C` | Chú ý, warning |
| `TikzCurve1/2/3` | Blue/Red/Green | Đường cong trên đồ thị |
| `TikzGrid` | `#E8E8E8` | Lưới đồ thị |

### Các environment chính
| Environment | Cú pháp | Mô tả |
|-------------|---------|--------|
| `baitoan` | `\begin{baitoan}{SỐ \hfill \tagNguon{...}}` | Khung bài toán |
| `loigiai` | `\begin{loigiai}` | Khung lời giải |
| `chotdang` | `\begin{chotdang}{Tiêu đề}` | Chốt dạng / Key takeaway |
| `nguon` | `\begin{nguon}{Tên nguồn}` | Tag nguồn (standalone) |
| `prompt` | `\begin{prompt}[title={...}]` | Gợi ý / Tóm tắt |
| `chuy` | `\begin{chuy}` | Chú ý / Warning |
| `dapso` | `\begin{dapso}` | Đáp số inline |

### Commands
| Command | Ví dụ |
|---------|-------|
| `\dapan{A}{B}{C}{D}` | 4 đáp án 1 cột |
| `\dapanhai{...}` / `\dapanbon{...}` | 2 cột / 4 cột |
| `\dung{text}` | Đánh dấu đáp án đúng (xanh) |
| `\tagNguon{text}` | Tag nguồn inline |
| `\separator` | Đường kẻ phân cách |

### TikZ Drawing Kit

| Macro / Style | Chức năng |
|---------------|-----------|
| `\bbtBacBa{x1}{x2}{f1}{f2}{lim-}{lim+}` | BBT hàm bậc 3 |
| `\bbtBacBon{x1}{x2}{x3}{f1}{f2}{f3}{lim-}{lim+}` | BBT hàm bậc 4 |
| `\begin{bangBT}{w}{h}...\end{bangBT}` | BBT tự do |
| `forum graph` / `forum graph small` | pgfplots style cho đồ thị |
| `\tiemcanDung{x}{ymin}{ymax}` | Tiệm cận đứng |
| `\tiemcanNgang{y}{xmin}{xmax}` | Tiệm cận ngang |
| `\diemDB{x}{y}{label}{pos}` | Điểm đặc biệt (fill) |
| `\diemHo{x}{y}{label}{pos}` | Điểm rỗng (không fill) |
| `solid edge` / `hidden edge` | Cạnh HHKG thấy/khuất |
| `\dinh{name}{coord}{label-pos}` | Đỉnh HHKG |
| `\gocVuong{vertex}{p1}{p2}{size}` | Ký hiệu góc vuông |
| `prob node` / `prob edge` / `prob label` | Cây xác suất |

> 📝 Xem thêm: [`tikz/examples.tex`](tikz/examples.tex) — Cheatsheet 9 ví dụ đầy đủ

### Header / Footer
- **Header trái**: Tên phần/chương hiện tại
- **Header phải**: "The Forum Center"
- **Số trang**: Trung tâm dưới; La Mã cho frontmatter, Ả Rập cho mainmatter

### Font
- **Body**: Serif (mặc định XeLaTeX)
- **Tiêu đề / Tag**: Sans-serif (bold)
- **Toán**: Default math font

---

## 📋 Ghi chú chỉnh sửa template

> ⚠️ **Quy tắc**: Mọi thay đổi template so với bản gốc `toanTHPTQG.pdf` đều phải ghi lại ở đây.

### Changelog

| Ngày | Thay đổi | Lý do |
|------|----------|-------|
| 2026-04-12 | Khởi tạo template LaTeX từ PDF mẫu | Lần đầu |
| 2026-04-13 | Tái cấu trúc folder: tách `styles/`, `tikz/`, `sections/` | Modular, dễ bảo trì |
| 2026-04-13 | Thêm TikZ drawing library (BBT, đồ thị, HHKG, số phức, XS) | Hỗ trợ vẽ hình trong đề |
| 2026-04-13 | Thêm pgfplots, mở rộng TikZ libraries | Vẽ đồ thị hàm số |
| 2026-04-13 | Đổi 6 chương cũ → 5 chương mới theo chủ đề đề thi | Phù hợp nguồn đề thực tế |
| 2026-04-13 | `chotdang` → `meobotui` ("Mẹo nhỏ bỏ túi") | Tên gần gũi, văn phong hơn |
| 2026-04-13 | Bỏ tất cả icon (`$\star$`, `$\blacktriangleright$`...) khỏi title box | Gọn, sạch hơn |
| 2026-04-15 | Xóa tag mức độ (`mucDoTB`, `mucDoKho`, `mucDoRatKho`) | Không cần phân loại |

---

## 🛠 Yêu cầu hệ thống

- **TeX Live 2025** (MacTeX) — đã cài tại `/Library/TeX/texbin/`
- **XeLaTeX** — compiler chính (hỗ trợ Unicode tiếng Việt)
- Packages cần thiết (đã có sẵn trong TeX Live):
  - `tcolorbox`, `fontspec`, `tikz`, `pgfplots`, `geometry`, `fancyhdr`
  - `enumitem`, `amsmath`, `amssymb`, `hyperref`, `graphicx`
  - `xcolor`, `tabularx`, `booktabs`, `colortbl`
  - TikZ libraries: `calc`, `positioning`, `arrows.meta`, `patterns`, `3d`, `perspective`

---

## 📝 Ghi chú cho Agent

1. **Đọc raw `.md`** → Parse câu hỏi, đáp án, lời giải
2. **Phân loại** theo chủ đề (hàm số, mũ-log, tích phân, số phức, HHKG, XS)
3. **Render** vào đúng environment LaTeX (`baitoan`, `loigiai`, `nguon`, v.v.)
4. **Vẽ TikZ** theo `tikz/examples.tex` — chọn macro phù hợp (BBT, đồ thị, hình)
5. **Giữ nguyên** mọi ký hiệu toán học, không truncate
6. **Mọi chỉnh sửa template** → hỏi user có ghi vào README Changelog không
7. **Compile test** sau mỗi batch để đảm bảo không lỗi
8. **Styles** chỉ sửa trong `styles/` và `tikz/lib/`, KHÔNG sửa inline trong chapters
