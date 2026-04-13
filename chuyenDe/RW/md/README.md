# Writing Markdown Files - Formatting Guidelines

---

## 🚨 RULE SỐ 1 — TUYỆT ĐỐI KHÔNG CẮT BỚT NỘI DUNG (ÁP DỤNG CHO CẢ 4 KỸ NĂNG)

> **Đây là rule ưu tiên cao nhất. Bất kỳ thao tác format nào cũng phải tuân thủ rule này trước.**

Khi chuyển đổi từ raw DOCX → Markdown, **100% nội dung phải được giữ nguyên**:

- ❌ KHÔNG tóm tắt, rút gọn, gộp, hay bỏ bớt bất kỳ phần nào
- ❌ KHÔNG bỏ qua phân tích câu hỏi nào — kể cả câu sai (wrong options)
- ❌ KHÔNG đổi thứ tự thông tin so với file gốc
- ✅ CHỈ được thêm formatting (heading, table, container) và từ vựng bổ sung

### Nội dung hay bị bỏ sót nhầm

| Kỹ năng | Thường bị cắt — CẦN GIỮ ĐỦ |
|---|---|
| **Reading** | "Từ khóa cần tìm", "Dẫn chứng trong bài", "Giải thích" trong MỖI câu; phân tích CÁC đáp án SAI |
| **Writing** | Chi tiết brainstorming từng phe; phân tích từng từ vựng với ví dụ; tất cả công thức và chiến thuật |
| **Listening** | Per-question keyword; option-by-option analysis kể cả options sai; map landmark; trap warnings |
| **Speaking** | Công thức mở rộng ý; phân tích tiêu chí từng band; toàn bộ bài mẫu; từ vựng kèm ví dụ |

### Format bắt buộc cho mỗi câu hỏi (Reading)

```markdown
### Câu N: [câu hỏi nguyên văn]

- **Từ khóa cần tìm:** keyword1, keyword2, ...
- **Dẫn chứng trong bài:** Đoạn X — *"quote nguyên văn từ bài đọc"*
- **Giải thích:** Lý do đáp án đúng; lý do tại sao các options kia sai
- **Đáp án: [đáp án]**
```

### Checklist trước khi gen DOCX

- [ ] Tất cả câu hỏi có mặt + đúng số thứ tự?
- [ ] Mỗi câu đủ: Từ khóa → Dẫn chứng → Giải thích → Đáp án?
- [ ] Phân tích các đáp án SAI cũng có mặt đầy đủ?
- [ ] Thứ tự các phần đúng như file gốc?

> Xem thêm chi tiết trong `chuyenDe/AGENT.md`

---



Khi cần format hoặc kiểm tra lại cấu trúc Writing MD, hãy tham chiếu các bộ file sau làm chuẩn:

| Bộ tài liệu | MD | DOCX |
|---|---|---|
| **W9/W11** (raww9) | `chuyenDe/RW/md/raww9/Writing/` | `chuyenDe/RW/docx/raww9/Writing/` |
| **W13** (raww13) | `chuyenDe/RW/md/raww13/Writing/` | `chuyenDe/RW/docx/raww13/Writing/` |

> **Quy tắc:** Mọi file Writing mới đều phải match cấu trúc của W9/W13 trước khi gen DOCX.

---

## Cấu trúc File MD (Writing)

Mỗi file Writing MD có 3 cấp độ với nội dung khác nhau:

| Level | Dạng bài | Band mục tiêu |
|---|---|---|
| **Level 1** | Task 2 — Opinion Essay (Agree/Disagree) | Band 4 → 5 |
| **Level 2** | Task 1 — Graph/Chart (Bar, Pie, Table) | Band 5 → 6 |
| **Level 3** | Task 1 — Dynamic Graph (Line, Mixed) | Band 6 → 7 |

---

## Format chuẩn từng file

### Top-level structure (áp dụng cho tất cả Level):

```
frontmatter (---)
::: collectiontitle ... :::
::: prompt
  [Đề bài - nguyên văn]
:::
[Yêu cầu đề bài -- Do you agree? / Summarise...]
## Phần I: ...  (Phân tích / Chiến lược)
## Phần II: ... (Hướng dẫn viết bài / Bài mẫu)
## Phần III: ... (Công cụ ngôn ngữ)
[## IV. ... (Từ vựng tổng hợp -- nếu cần)]
```

### Frontmatter bắt buộc:

```yaml
---
title: "TÀI LIỆU CHUYÊN ĐỀ WRITING"
skill: Writing
level: 1        # 1 | 2 | 3
week: 13
---
```

---

## Nội dung theo từng Level

### Level 1 — Task 2 Opinion Essay

**Phần I: Xây dựng nền tảng tư duy và chiến lược**
- Tiêu chí Band 4 → 5 (Task Response, C&C, Lexical, Grammar)
- Giải mã đề bài (chủ đề cốt lõi, yêu cầu nhiệm vụ)
- Brainstorming (phát triển ý 2 phe)
- Kỹ thuật mở rộng ý (Contrast, Hypothetical, Real-world)
- Dàn ý đề xuất

**Phần II: Kiến tạo bài luận hoàn chỉnh**
- Mở bài (Introduction) — paraphrase + stance
- Thân bài 1 (Body 1) — topic sentence + giải thích + ví dụ
- Thân bài 2 (Body 2) — topic sentence + giải thích + ví dụ
- Kết bài (Conclusion) — tóm tắt + khẳng định lại

**Phần III: Công cụ ngôn ngữ**
- Từ vựng: bảng `cdvocabtable` 3 cột (Từ | Nghĩa | Ví dụ đơn giản)
- Mẫu câu ngữ pháp: bảng `cdvocabtable` + giải thích

### Level 2 — Task 1 Static/Dynamic Chart (Band 5→6)

**Phần I: Phân tích dữ liệu**
- Tiêu chí Band 5 → 6
- Giải mã biểu đồ (loại biểu đồ, đối tượng, thời gian, đơn vị)
- Phân tích số liệu & xu hướng (bảng/bullet so sánh)
- Xác định đặc điểm chính cho Overview
- Nhóm thông tin (Body grouping strategy)

**Phần II: Hướng dẫn viết bài**
- Mở bài, Overview, Thân bài 1, Thân bài 2 — có câu mẫu hoàn chỉnh

**Phần III/IV: Cấu trúc ngữ pháp & Từ vựng**
- Grammar patterns nâng cao (In stark contrast, Experienced a rise, By far...)
- Bảng `cdvocabtable` 4 cột (Từ | Từ loại | Nghĩa | Ứng dụng)

### Level 3 — Task 1 Dynamic Graph (Band 6→7)

Cấu trúc như Level 2 nhưng nhấn mạnh:
- **Overtaking / Change in rank** (đổi ngôi)
- **Perfect Participle** (Having hosted...)
- **Reference pronouns** (this figure, such events)
- **Collocations** (upward momentum, plunged to a low of...)
- Bảng từ vựng 4 cột với từ nâng cao

---

## Containers & Special Blocks

| Block | Dùng khi nào |
|---|---|
| `::: collectiontitle ... :::` | Header tiêu đề tài liệu (đầu file) |
| `::: prompt ... :::` | Đề bài nguyên văn |
| `::: cdvocabtable ... :::` | Bảng từ vựng và ngữ pháp |
| `[text]{.cdblue}` | Nhãn màu xanh (tiêu đề sub-section) |
| `[text]{.cdgreen}` | Highlight quan điểm (ĐỒNG Ý / KHÔNG ĐỒNG Ý) |

---

## Gen DOCX

```bash
bash chuyenDe/scripts/wr_md_to_word.sh \
  "$(pwd)/chuyenDe/RW/md/raww13" \
  "$(pwd)/chuyenDe/RW/docx/raww13"
```

Script `wr_md_to_word.sh` dùng `reference-writing.docx` và tự động:
- Tìm tất cả `.md` trong thư mục input
- Xác định `skill/Level/Week` từ đường dẫn
- Xuất DOCX tương ứng ra thư mục output
- Chạy `postprocess_docx_tables.py` để fix table formatting
