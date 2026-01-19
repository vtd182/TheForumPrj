# IELTS Vocabulary LaTeX Template - Hướng Dẫn Sử Dụng

## 📁 Cấu Trúc Files

Template bao gồm 3 files chính:

1. **`style.tex`** - Định nghĩa tất cả styling, màu sắc, format (KHÔNG cần chỉnh sửa)
2. **`main.tex`** - File chính để compile (Chỉnh sửa thông tin header ở đây)
3. **`data.tex`** - File chứa dữ liệu vocabulary (Thay đổi nội dung từ vựng ở đây)

## 🚀 Cách Sử Dụng Nhanh

### Bước 1: Cập nhật thông tin trong `main.tex`

Mở file `main.tex` và tìm phần **DOCUMENT CONFIGURATION**:

```latex
% Header information for first page
\newcommand{\authorinfo}{THE FORUM CENTER - NGUYỄN HOÀNG HUY}
\newcommand{\documenttitle}{VOCABULARY ĐỘC QUYỀN (PHẦN 1)}
\newcommand{\topictitle}{TỪ VỰNG CHỦ ĐỀ: ACADEMIC VOCABULARY}
```

Thay đổi 3 dòng này theo nội dung của bạn:
- `\authorinfo` - Tên tác giả (góc trái header trang đầu)
- `\documenttitle` - Tiêu đề tài liệu (góc phải header trang đầu)
- `\topictitle` - Chủ đề vocabulary (dòng lớn bên dưới header đỏ)

### Bước 2: Thêm vocabulary vào `data.tex`

Mở file `data.tex` và sử dụng command `\vocabentry` để thêm từ vựng:

**Format đầy đủ (có ví dụ):**
```latex
\vocabentry{word}
{/pronunciation/ (part of speech)}
{Definition (Nghĩa tiếng Việt)}
{Example sentence in English.}
{Bản dịch ví dụ tiếng Việt.}
```

**Format ngắn (không có ví dụ):**
```latex
\vocabshort{word}
{/pronunciation/ (part of speech)}
{Definition (Nghĩa tiếng Việt)}
```

**Ví dụ thực tế:**
```latex
\vocabentry{conflate}
{/ˈkɑːnfleɪt/ (v)}
{To combine two or more things into one; to merge or blend (Kết hợp, hòa trộn)}
{Historians often conflate myth and reality when recounting ancient events.}
{Các nhà sử học thường kết hợp thần thoại và thực tế khi kể lại các sự kiện cổ đại.}
```

### Bước 3: Compile PDF

**⚠️ QUAN TRỌNG:** Template này SỬ DỤNG `xelatex` thay vì `pdflatex` để hỗ trợ font tùy chỉnh.

Chạy lệnh sau trong terminal (compile 2 lần để TikZ headers hiện đúng):

```bash
cd /Users/lap15116/Desktop/TheForumPrj/Vocab/template
xelatex main.tex
xelatex main.tex
```

Hoặc  sử dụng LaTeX editor có hỗ trợ XeLaTeX như Overleaf, TeXShop, hoặc VS Code với LaTeX Workshop extension (chọn XeLaTeX trong settings).

## 🎨 Tùy Chỉnh Nâng Cao

### Thay đổi màu sắc

Mở `style.tex` và tìm phần **COLOR DEFINITIONS**:

```latex
\definecolor{forumred}{HTML}{E52B20}      % Màu đỏ chính
\definecolor{textblack}{HTML}{000000}      % Màu chữ
\definecolor{watermarkgray}{HTML}{FFE5E5}  % Màu watermark
```

### Thay đổi watermark

**Cách 1:** Trong `main.tex`, thêm dòng này sau phần DOCUMENT CONFIGURATION:
```latex
\renewcommand{\watermarktext}{YOUR NEW TEXT}
```

**Cách 2:** Trong `style.tex`, tìm dòng:
```latex
\newcommand{\watermarktext}{THE FORUM}
```

### Thêm section headers (tùy chọn)

Trong `data.tex`, bạn có thể thêm headers để phân chia các nhóm từ:

```latex
\vocabsection{Academic Words - Group 1}

\vocabentry{word1}{...}{...}{...}{...}
\vocabentry{word2}{...}{...}{...}{...}

\vocabsection{Academic Words - Group 2}

\vocabentry{word3}{...}{...}{...}{...}
```

## 📝 Thiết Kế Template

### Trang đầu tiên:
- **Header đỏ lớn:** "IELTS VOCABULARY" (màu trắng, font lớn)
- **Sub-header đỏ:** Tên tác giả (trái) | Tiêu đề tài liệu (phải)
- **Topic title:** Chủ đề vocabulary (màu đen, bold)
- **Watermark:** "THE FORUM" ở giữa trang (màu hồng nhạt)
- **Footer:** Số trang màu đỏ

### Từ trang 2 trở đi:
- **Header:** Đường kẻ đỏ + badge "Self-study IELTS Material"
- **Watermark:** "THE FORUM"
- **Footer:** Số trang màu đỏ

### Format vocabulary:
- **Từ vựng:** Màu đỏ, bold, font lớn
- **Phiên âm:** In nghiêng, màu đen
- **Định nghĩa:** Font thường, màu đen
- **Ví dụ:** "Example:" (bold, nghiêng) + câu ví dụ (nghiêng)
- **Dịch ví dụ:** In nghiêng, trong ngoặc đơn

## ⚙️ Yêu Cầu Hệ Thống

Template cần các packages sau (đã được include trong `style.tex`):
- `fancyhdr` - Headers và footers
- `multicol` - Bố cục 2 cột
- `xcolor` - Màu sắc
- `tcolorbox` - Boxes cho header
- `tikz` - Vẽ header badge
- `eso-pic` - Watermark

## 🔄 Tạo Tài Liệu Mới

Khi muốn tạo một tài liệu vocabulary mới:

1. **Giữ nguyên:** `style.tex` (không cần thay đổi)
2. **Copy:** `main.tex` và `data.tex` sang folder mới (hoặc đổi tên)
3. **Chỉnh sửa:** 
   - Trong `main.tex`: Cập nhật 3 biến header
   - Trong `data.tex`: Xóa vocabulary cũ, thêm vocabulary mới
4. **Compile:** `pdflatex main.tex`

## 💡 Tips

- Giữ mỗi entry ngắn gọn để tránh tràn cột
- Sử dụng `\vocabshort` cho những từ không cần ví dụ
- Có thể thêm nhiều entries tùy ý, template sẽ tự động phân trang
- Font size và spacing đã được tối ưu để tối đa hóa nội dung

## ❓ Troubleshooting

**Lỗi compile:**
- Đảm bảo tất cả 3 files (`main.tex`, `style.tex`, `data.tex`) ở cùng folder
- Kiểm tra các ký tự đặc biệt trong tiếng Việt
- Chạy `pdflatex` 2 lần nếu header không hiển thị đúng

**Header trang 2+ không hiện:**
- Compile 2 lần để cập nhật headers
- Kiểm tra package `tikz` đã được cài đặt

**Watermark quá đậm/nhạt:**
- Chỉnh màu `watermarkgray` trong `style.tex`
- Hoặc thay đổi `fontsize{80}{96}` thành số khác
