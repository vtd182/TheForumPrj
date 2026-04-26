# Forecast V2 Pipeline

Dự án **Forecast V2** dùng để tạo các bản forecast chất lượng dạng PDF cho kỹ năng Speaking (IELTS Speaking Intensive) với giao diện bìa và layout chuẩn từ The Forum Center.

## Cấu trúc thư mục

```text
Forecast-v2/
├── Raw/                     ← Chứa các file Raw dạng Markdown (VD: forecastQ2-26.md)
├── Rule/                    ← Thư mục chứa các rule riêng biệt để AI trả lời
├── Latex/                   ← Thư mục chứa template LaTeX & Build tools
│   ├── compile.sh           ← Script biên dịch LaTeX
│   ├── main.tex             ← File LaTeX gốc (chứa toàn bộ logic include)
│   ├── preamble.tex         ← Cấu hình thư viện và môi trường (tcolorbox ieltsprompt)
│   ├── build/               ← Chứa kết quả biên dịch (main.pdf)
│   ├── chapters/            ← (Được sinh tự động) Chứa các file .tex từng phần đã parse
│   ├── images/              ← Hình ảnh, logo tĩnh
│   ├── python/              
│   │   └── pipeline.py      ← Script cốt lõi để chuyển đổi từ Markdown sang LaTeX
│   ├── sections/            ← Chứa file fix tĩnh (coverpage.tex, frontmatter.tex)
│   ├── styles/              ← Các file style chuẩn xác định màu, font, môi trường
│   └── tikz/                ← Thư viện đồ hoạ TikZ
```

## Quy trình tự động

**Bước 1: Chuẩn bị file Raw**
Người dùng cung cấp một file `Raw/forecastQx-nn.md` (ví dụ: `forecastQ2-26.md`). File này chứa nội dung câu hỏi cho các Part 1, Part 2 & Part 3 với định dạng chuẩn đã quy định.

**Bước 2: Xử lý Python (Markdown to LaTeX)**
Chạy script `pipeline.py` bằng Python:
```bash
cd Latex/python
python3 pipeline.py
```
- Script sẽ tự động scan file markdow, bóc tách cấu trúc Header (`##`), bóc tách câu hỏi và prompts.
- Script xử lý escaping các kí tự đặc biệt của LaTeX (như `&` -> `\&`).
- Script sẽ trút dữ liệu và tạo ra file `Latex/chapters/part1.tex` và `Latex/chapters/part2_3.tex` được bọc sẵn trong các môi trường `ieltsprompt` đẹp mắt.

**Bước 3: Biên dịch PDF**
Chạy shell script compile:
```bash
cd Latex
./compile.sh
```
- Script sẽ kích hoạt `xelatex` hai lần (1 lần sinh metadata và 1 lần xử lý TOC, references).
- Kết quả `main.pdf` sẽ xuất hiện trong thư mục `Latex/build/`.

**Bước 4: (Tương lai) AI Generate Answer**
Hệ thống AI (tuân theo các prompt trong thư mục `Rule/`) sẽ tự động tìm các khoảng trống `Các câu trả lời mẫu...` giữa các `ieltsprompt` để điền theo rule đã ban hành như quy định 2-3 câu tự nhiên cho Part 1, 150-200 từ cho Part 2, và hướng nghị luận (argumentative) cho Part 3.
