# Forecast V2 Pipeline

Dự án **Forecast V2** dùng để tạo các bản forecast chất lượng dạng PDF cho kỹ năng Speaking (IELTS Speaking Intensive) với giao diện bìa và layout chuẩn từ The Forum Center.

## Cấu trúc thư mục

```text
Forecast-v2/
├── Raw/                     ← Chứa các file Raw dạng Markdown (VD: forecastQ2-26.md)
├── Rule/                    ← Thư mục chứa các rule riêng biệt để AI trả lời (vd: speaking-rule.md)
├── Template/                ← Khuôn đúc chuẩn LaTeX (không sửa đổi nội dung tại đây)
│   ├── compile.sh           
│   ├── main.tex             
│   ├── preamble.tex         
│   ├── images/              
│   ├── sections/            
│   └── styles/              
├── Output/                  ← Chứa thư mục project của mỗi đợt forecast 
│   └── forecastQ2-26/       ← Mỗi Quý sẽ có 1 folder riêng chứa cả PDF và src latex
└── Scripts/              
    └── pipeline.py          ← Script cốt lõi điều phối mọi quá trình
```

## Quy trình tự động

**Bước 1: Chuẩn bị file Raw**
Người dùng cung cấp một file `Raw/forecastQx-nn.md` (ví dụ: `forecastQ2-26.md`). File này chứa nội dung câu hỏi cho các Part 1, Part 2 & Part 3 với định dạng chuẩn đã quy định.

**Bước 2: Xử lý Python (Tự động hóa hoàn toàn)**
Từ thư mục `Forecast-v2/`, gọi script truyền kèm file markdown:
```bash
python3 Scripts/pipeline.py Raw/forecastQ2-26.md
```

**What happens inside?**
- Script nhận diện tên Quý (`forecastQ2-26`) và tạo folder làm việc riêng `Output/forecastQ2-26/`.
- Copy toàn bộ nội dung từ `Template/` qua Output.
- Script tự động scan file markdow, bóc tách cấu trúc Header (`##`), escaping `\&`, và trút dữ liệu thành `chapters/part1.tex` và `chapters/part2_3.tex` bên trong Output.
- Script tự động kích hoạt `compile.sh` biên dịch PDF qua `xelatex`.

**Kết quả:** File gốc LaTeX biên dịch xong kèm theo file **`Output/forecastQ2-26/build/main.pdf`**.

**Bước 3: (Tương lai) AI Generate Answer**
Hệ thống AI (tuân theo các prompt trong thư mục `Rule/speaking-rule.md`) sẽ tự động tìm đoạn `.md` hoặc sửa thẳng `.tex` để sinh các bài trả lời mẫu đúng 100% chuẩn cấu trúc và phát âm.
