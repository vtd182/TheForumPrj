# Chuyên đề (LS/RW) templates

Mục tiêu: mỗi template trong `chuyenDe/` dùng chung 1 “base” để dễ reuse, nhưng vẫn giữ layout giống các file PDF template mẫu.

## Cấu trúc

- `chuyenDe/common/workshop-base.tex`: phần base (fonts + watermark + header/footer) dùng chung.
- `chuyenDe/LS/templateListening`: template Listening
- `chuyenDe/LS/templateSpeaking`: template Speaking
- `chuyenDe/RW/templateReading`: template Reading
- `chuyenDe/RW/templateWriting`: template Writing

## Cách dùng nhanh

Vào đúng thư mục template và build:

- Listening: `cd chuyenDe/LS/templateListening && xelatex main.tex`
- Speaking: `cd chuyenDe/LS/templateSpeaking && xelatex main.tex`
- Reading: `cd chuyenDe/RW/templateReading && xelatex main.tex`
- Writing: `cd chuyenDe/RW/templateWriting && xelatex main.tex`

Mỗi template có:

- file class riêng: `cdlistening.cls`, `cdspeaking.cls`, `cdreading.cls`, `cdwriting.cls`
- file `main.tex` mẫu để copy/reuse

## Tuỳ biến

Trong `main.tex` bạn có thể override:

- `\workshopsetauthor{...}`
- `\workshopsetmaintitle{...}` (mặc định: `IELTS WORKSHOP`)
- `\workshopsetdoctype{...}` (mặc định theo template: `TÀI LIỆU CHUYÊN ĐỀ ...`)
- `\workshopsetsubtitle{...}` (dòng tiêu đề giữa, dưới title lớn)
