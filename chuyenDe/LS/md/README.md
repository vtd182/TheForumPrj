# LS Markdown (Listening/Speaking) — nguồn chung cho DOCX & PDF

Bạn chỉ cần chuẩn bị Markdown theo đúng quy ước, sau đó có thể xuất:
- **DOCX** (editable) qua Pandoc + Word reference template
- **PDF** qua Pandoc + LaTeX template

## Cấu trúc thư mục đề xuất

Đặt file vào:

`chuyenDe/LS/md/raw47/<Skill>/Level<level>/W<week>.md`

Ví dụ:
- `chuyenDe/LS/md/raw47/Listening/Level1/W2.md`
- `chuyenDe/LS/md/raw47/Speaking/Level3/W5.md`

## Frontmatter tối thiểu (khuyến nghị)

```yaml
---
title: "TÀI LIỆU CHUYÊN ĐỀ LISTENING"
skill: Listening
level: 1
week: 2
---
```

Ghi chú:
- `skill` dùng đúng một trong: `Listening` / `Speaking`
- `title` không bắt buộc cho PDF cover (cover title lấy từ `::: collectiontitle ... :::` nếu có)

## Component Markdown (dùng chung với RW)

- `::: collectiontitle ... :::` (dòng tiêu đề căn giữa dưới header)
- `::: prompt ... :::` (box prompt)
- `##` / `###` / `####` map sang các box section/step/green heading
- Các bảng trong fenced div: `::: cdoptiontable`, `::: cdvocabtable`, ...

## Regen nhanh

- DOCX: `bash chuyenDe/scripts/ls_md_to_word.sh`
- PDF: `bash chuyenDe/scripts/ls_md_to_pdf.sh`

