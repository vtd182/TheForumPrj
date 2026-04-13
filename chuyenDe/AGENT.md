# AGENT.md — Forum IELTS Educational Content Pipeline

> Tài liệu này mô tả toàn bộ quy trình (pipeline) xử lý và sinh tài liệu giảng dạy IELTS cho dự án The Forum.
> Đọc kỹ trước khi bắt đầu bất kỳ task nào liên quan đến 4 kỹ năng: **Reading, Writing, Listening, Speaking**.

---

## 📌 Cấu trúc thư mục

```
chuyenDe/
├── RW/
│   ├── md/rawr<N>/Reading/Level{1,2,3}/W<N>.md   ← Markdown nguồn (Reading)
│   ├── md/raww<N>/Writing/Level{1,2,3}/W<N>.md   ← Markdown nguồn (Writing)
│   ├── docx/rawr<N>/Reading/...                  ← Output DOCX (Reading)
│   └── docx/raww<N>/Writing/...                  ← Output DOCX (Writing)
├── LS/
│   ├── md/rawl<N>/Listening/Level{1,2,3}/W<N>.md ← Markdown nguồn (Listening)
│   ├── md/raws<N>/Speaking/Level{1,2,3}/W<N>.md  ← Markdown nguồn (Speaking)
│   ├── docx/rawl<N>/Listening/...                ← Output DOCX (Listening)
│   └── docx/raws<N>/Speaking/...                 ← Output DOCX (Speaking)
├── scripts/
│   ├── wr_md_to_word.sh      ← Gen DOCX hàng loạt cho Writing/Reading
│   └── postprocess_docx_tables.py
├── word/
│   ├── pandoc/md_to_docx.sh  ← Gen DOCX đơn lẻ (Listening/Speaking)
│   ├── reference-writing.docx
│   └── reference-speaking.docx
├── RW/md/README.md           ← Rules cho Reading & Writing
├── LS/md/README.md           ← Rules cho Listening & Speaking
└── AGENT.md                  ← File này
```

---

## 🔄 Pipeline tổng quan

```
Raw DOCX (raw input)
      │
      ▼
[Bước 1] pandoc extract → raw .md (scratch/)
      │
      ▼
[Bước 2] Format & parse → structured .md (md/raw<N>/)
      │         (áp dụng rules từ README + AGENT.md)
      ▼
[Bước 3] Gen DOCX → md_to_docx.sh / wr_md_to_word.sh
      │
      ▼
[Bước 4] Postprocess → postprocess_docx_tables.py
      │
      ▼
Output DOCX (docx/raw<N>/)
```

---

## 🚨 RULE SỐ 1 — NỘI DUNG TUYỆT ĐỐI KHÔNG ĐƯỢC CẮT BỚT

> **ĐÂY LÀ RULE QUAN TRỌNG NHẤT. VI PHẠM RULE NÀY LÀ LỖI NGHIÊM TRỌNG.**

### Nguyên tắc cốt lõi

Khi chuyển đổi từ raw DOCX → Markdown, **100% nội dung gốc phải được giữ nguyên**:

- ❌ KHÔNG tóm tắt, rút gọn, gộp, hay diễn giải lại bất kỳ phần nào
- ❌ KHÔNG bỏ qua bất kỳ câu hỏi, đáp án, hay phần phân tích nào
- ❌ KHÔNG đổi thứ tự thông tin so với file gốc
- ✅ CHỈ được thêm formatting (heading, bold, table, container) và từ vựng

### Nội dung hay bị bỏ sót nhầm — cần đặc biệt chú ý

| Kỹ năng | Thường bị cắt |
|---|---|
| **Reading** | Phần "Từ khóa cần tìm", "Dẫn chứng trong bài", "Giải thích" từng câu; phân tích CÁC ĐÁP ÁN SAI (không chỉ đáp án đúng) |
| **Listening** | Per-question keyword analysis; option-by-option explanation (A/B/C/D); note-taking examples; trap warnings; map landmark descriptions |
| **Writing** | Chi tiết brainstorming từng phe; phân tích từng từ vựng với ví dụ cụ thể; công thức và chiến thuật |
| **Speaking** | Công thức mở rộng ý (Contrast/Hypothetical); phân tích tiêu chí từng band; toàn bộ bài mẫu; từ vựng gợi ý với ví dụ |

### Checklist trước khi hoàn thành bất kỳ file .md nào

- [ ] Tất cả câu hỏi (Q1..Qlast) đều có mặt và đúng số thứ tự?
- [ ] Mỗi câu hỏi có đủ: Từ khóa → Dẫn chứng → Giải thích → Đáp án?
- [ ] Các đáp án SAI cũng được giải thích (không chỉ đáp án đúng)?
- [ ] Transcript/Bài mẫu đầy đủ, không cắt đoạn nào?
- [ ] Bảng từ vựng có đủ tất cả các từ như raw?
- [ ] Thứ tự các phần đúng như file gốc?

---

## 📚 Quy trình theo từng kỹ năng

### 🔵 READING (rawr<N>)

**Reference files:** `RW/md/rawr9/`, `RW/md/rawr12/`

**Cấu trúc file MD:**
```
frontmatter → collectiontitle → ::: prompt (bài đọc) :::
→ Phần I: Câu hỏi (trong ::: cdlisteningsection :::)
→ Phần II: Hướng dẫn làm bài (NGOÀI container)
→ Phần III: Lời giải — Answer Key
→ Từ vựng (::: cdreadingvocabtable :::)
```

**Format hướng dẫn từng câu (BẮT BUỘC):**
```markdown
### Câu N: [câu hỏi]

- **Từ khóa cần tìm:** keyword1, keyword2, ...
- **Dẫn chứng trong bài:** Đoạn X — *"quote nguyên văn"*
- **Giải thích:** Lý do tại sao đáp án đúng/sai là...
- **Đáp án: [đáp án]**
```

**Dạng bài theo Level:**
- L1: TRUE/FALSE/NOT GIVEN + Note Completion
- L2: Paragraph Headings + Multiple Choice (có giải thích TẤT CẢ options A-E) + Sentence Completion
- L3: Matching Statements + YES/NO/NOT GIVEN + Date Matching

**Gen DOCX:**
```bash
export PATH="/opt/homebrew/bin:$PATH"
bash chuyenDe/scripts/wr_md_to_word.sh \
  "$(pwd)/chuyenDe/RW/md/rawr<N>" \
  "$(pwd)/chuyenDe/RW/docx/rawr<N>"
```

---

### 📝 WRITING (raww<N>)

**Reference files:** `RW/md/raww9/`, `RW/md/raww13/`

**Cấu trúc file MD:**
```
frontmatter → collectiontitle → ::: prompt (đề bài) :::
→ [yêu cầu đề bài]
→ Phần I: Xây dựng nền tảng / Phân tích dữ liệu
→ Phần II: Hướng dẫn viết bài / Bài mẫu
→ Phần III: Công cụ ngôn ngữ
→ [Phần IV: Từ vựng tổng hợp — nếu có]
```

**Nội dung theo Level:**
- L1: Task 2 Opinion Essay (Band 4→5)
- L2: Task 1 Static Chart (Band 5→6)
- L3: Task 1 Dynamic Graph (Band 6→7)

**Gen DOCX:**
```bash
export PATH="/opt/homebrew/bin:$PATH"
bash chuyenDe/scripts/wr_md_to_word.sh \
  "$(pwd)/chuyenDe/RW/md/raww<N>" \
  "$(pwd)/chuyenDe/RW/docx/raww<N>"
```

---

### 🎧 LISTENING (rawl<N>)

**Reference files:** `LS/md/rawls7/` (W8), `LS/md/rawl12/` (W12)

**Cấu trúc file MD:**
```
frontmatter → collectiontitle
→ ::: cdlisteningsection ::: (SECTION exam questions — mỗi section một block)
→ Phần 1: Section X (hướng dẫn NGOÀI container)
→ Phần 2: Section Y (hướng dẫn NGOÀI container)
→ Phần 3: Lời giải — Answer Key
→ Phần 4: Lời băng — Transcript (::: cdtranscriptsection :::)
→ Từ vựng (::: cdreadingvocabtable :::)
```

**Format hướng dẫn Section (BẮT BUỘC đầy đủ):**
```
### I. HƯỚNG DẪN CHUNG
   [general strategy theo dạng bài]

### II. HƯỚNG DẪN CHI TIẾT
   Bước 1: Phân tích hướng dẫn và giới hạn từ
   Bước 2-3: Per-question keyword + prediction
      - Câu N: keyword... → dự đoán ngữ pháp → paraphrase dự kiến
   Bước 4-5: Phân tích đáp án
      - Câu N: Audio quote → option A/B/C analysis với ✔/✘ + lý do
```

**Transcript:**
- Dialogue (2+ speakers) → `::: cdtranscripttable :::` (2-column table)
- Monologue (1 speaker) → plain text

**Gen DOCX (đơn lẻ):**
```bash
export PATH="/opt/homebrew/bin:$PATH"
REF=~/Desktop/TheForumPrj/chuyenDe/word/reference-speaking.docx
CONV=~/Desktop/TheForumPrj/chuyenDe/word/pandoc/md_to_docx.sh
POST=~/Desktop/TheForumPrj/chuyenDe/scripts/postprocess_docx_tables.py

for LEVEL in 1 2 3; do
  OUT=~/Desktop/TheForumPrj/chuyenDe/LS/docx/rawl<N>/Listening/Level${LEVEL}
  mkdir -p "$OUT"
  bash "$CONV" ~/Desktop/TheForumPrj/chuyenDe/LS/md/rawl<N>/Listening/Level${LEVEL}/W<N>.md "$OUT/W<N>.docx" "$REF"
  python3 "$POST" "$OUT/W<N>.docx"
done
```

---

### 🎤 SPEAKING (raws<N>)

**Reference files:** `LS/md/raws11/` (W11), `LS/md/raws13/` (W13)

**Cấu trúc file MD:**
```
frontmatter → collectiontitle
→ Part 1: [questions + formula + expansion technique]
→ Part 2: [cue card + full sample answer + vocab]
→ Part 3: [questions + strategy + full discussion]
→ Tiêu chí đánh giá (band descriptors)
→ Từ vựng gợi ý (::: cdvocabtable :::)
```

**Gen DOCX:** Giống Listening — dùng `md_to_docx.sh` với `reference-speaking.docx`.

---

## 🛠️ Công cụ và scripts

| Script | Dùng khi nào | PATH cần thiết |
|---|---|---|
| `wr_md_to_word.sh` | Gen Reading/Writing hàng loạt | `/opt/homebrew/bin` (pandoc) |
| `md_to_docx.sh` | Gen Listening/Speaking từng file | `/opt/homebrew/bin` (pandoc) |
| `postprocess_docx_tables.py` | Fix table formatting trong DOCX output | Python 3 |

> ⚠️ **QUAN TRỌNG:** Luôn set `export PATH="/opt/homebrew/bin:$PATH"` trước khi chạy bất kỳ script nào, vì pandoc được cài tại `/opt/homebrew/bin`.

---

## 🎨 Heading → Style mapping (Word)

| Markdown | Word Style | Màu |
|---|---|---|
| `##` | CD Section | Đỏ (`#E52B20`), nền xám nhạt |
| `###` | CD Step | Xanh dương (`#1F4E79`) |
| `####` | CD Green Heading | Xanh lá (`#5AA244`) — dùng hạn chế |
| `> blockquote` | CD Note | Tím (`#7A1FA2`) — chỉ cho lưu ý quan trọng |

---

## 📋 Containers đặc biệt

| Container | Dùng ở đâu |
|---|---|
| `::: collectiontitle :::` | Đầu mỗi file (tiêu đề tài liệu) |
| `::: prompt :::` | Writing (đề bài) / Reading (bài đọc) |
| `::: cdlisteningsection :::` | Listening (chỉ chứa exam questions) |
| `::: cdtranscriptsection :::` | Listening transcript (bao cả 4 sections) |
| `::: cdtranscripttable :::` | Dialogue transcript (2-column) |
| `::: cdreadingvocabtable :::` | Bảng từ vựng 4 cột |
| `::: cdvocabtable :::` | Bảng từ vựng Writing/Speaking |

---

## 🗂️ Tuần reference chuẩn

| Kỹ năng | Reference tuần |
|---|---|
| Reading | W9 (rawr9), W12 (rawr12) |
| Writing | W9/W11 (raww9), W13 (raww13) |
| Listening | W8 (rawls7), W12 (rawl12) |
| Speaking | W11 (raws11), W13 (raws13) |

---

## ✅ Workflow khi nhận raw mới

```
1. Đọc README.md (LS/md/ hoặc RW/md/) để nhớ rules
2. Đọc AGENT.md (file này) — đặc biệt Rule Số 1
3. Xem reference files của kỹ năng tương ứng
4. Parse raw DOCX → extract toàn bộ nội dung (dùng pandoc hoặc docx2txt)
5. Tạo .md với 100% nội dung giữ nguyên, chỉ thêm formatting
6. Tự kiểm tra checklist "No-Truncation" ở trên
7. Gen DOCX bằng script phù hợp
8. Chạy postprocess_docx_tables.py
```
