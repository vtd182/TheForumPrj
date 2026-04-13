# AGENT.md — Forum IELTS Content Pipeline

> Tài liệu trung tâm mô tả toàn bộ quy trình xử lý và sinh tài liệu giảng dạy IELTS cho dự án The Forum.
> **Đọc file này trước khi bắt đầu bất kỳ task nào.**
>
> Các tài liệu bổ sung (chi tiết hơn theo từng kỹ năng):
> - `chuyenDe/LS/md/README.md` — Listening & Speaking rules
> - `chuyenDe/RW/md/README.md` — Reading & Writing rules
> - `chuyenDe/word/README.md` — Pandoc, Lua filter, Word style mapping

---

## 📁 Cấu trúc thư mục thực tế

```
chuyenDe/
├── AGENT.md                         ← File này
├── LS/
│   ├── md/
│   │   ├── README.md                ← Rules chi tiết Listening & Speaking
│   │   ├── rawls7/
│   │   │   ├── Listening/Level{1,2,3}/W8.md   ← GOLD STANDARD Listening (W8)
│   │   │   └── Speaking/Level{1,2,3}/W7.md
│   │   ├── rawl10/Listening/Level{1,2,3}/W10.md
│   │   ├── rawl12/Listening/Level{1,2,3}/W12.md  ← GOLD STANDARD Listening (W12)
│   │   ├── rawl14/Listening/Level{1,2,3}/W14.md
│   │   ├── raws9/Speaking/Level{1,2,3}/W9.md
│   │   ├── raws11/Speaking/Level{1,2,3}/W11.md   ← GOLD STANDARD Speaking
│   │   └── raws13/Speaking/Level{1,2,3}/W13.md   ← GOLD STANDARD Speaking
│   └── docx/
│       ├── rawls7/Listening/Level{1,2,3}/W8.docx
│       └── ...
├── RW/
│   ├── md/
│   │   ├── README.md                ← Rules chi tiết Reading & Writing
│   │   ├── raww9/
│   │   │   ├── Reading/Level{1,2,3}/W10.md   ← GOLD STANDARD Reading
│   │   │   └── Writing/Level{1,2,3}/W9.md    ← GOLD STANDARD Writing
│   │   ├── raww13/Writing/Level{1,2,3}/W13.md ← GOLD STANDARD Writing
│   │   ├── rawr8/Reading/Level{1,2,3}/W8.md
│   │   └── rawr14/Reading/Level{1,2,3}/W14.md
│   └── docx/
│       └── ...
├── scripts/
│   ├── wr_md_to_word.sh             ← Gen DOCX hàng loạt (chỉ Writing)
│   ├── ls_md_to_word.sh             ← Gen DOCX hàng loạt (Listening/Speaking)
│   ├── postprocess_docx_tables.py  ← Fix table formatting DOCX
│   ├── rawls7_to_markdown.py       ← Parser raw → MD (ví dụ W8)
│   └── raww9_to_markdown.py        ← Parser raw → MD (ví dụ W9/W10-12)
└── word/
    ├── README.md                    ← Pandoc, Lua, Word style mapping
    ├── pandoc/
    │   ├── md_to_docx.sh           ← Script gen DOCX đơn lẻ
    │   └── cd-forum.lua            ← Lua filter map class → Word style
    ├── reference-writing.docx
    ├── reference-reading.docx
    ├── reference-listening.docx
    ├── reference-speaking.docx
    └── build_reference_docx.py     ← Tạo lại reference .docx
```

---

## 🚨 RULE SỐ 1 — TUYỆT ĐỐI KHÔNG CẮT BỚT NỘI DUNG

> **Đây là rule cao nhất. Bất kỳ thao tác format nào cũng phải tuân thủ rule này trước tiên.**

### Nguyên tắc

- ❌ KHÔNG tóm tắt, rút gọn, gộp, hay bỏ bớt bất kỳ phần nào
- ❌ KHÔNG bỏ qua phân tích câu hỏi nào — kể cả wrong options (A, B, C, D, E)
- ❌ KHÔNG đổi thứ tự thông tin so với file raw gốc
- ✅ CHỈ được thêm: heading, table, container, từ vựng bổ sung

### Nội dung thường bị cắt nhầm — chú ý đặc biệt

| Kỹ năng | Hay bị cắt |
|---|---|
| **Reading** | "Từ khóa cần tìm", "Dẫn chứng trong bài", "Phân tích" trong MỖI câu; phân tích CÁC đáp án SAI |
| **Writing** | Chi tiết brainstorming từng phe; phân tích từng từ với ví dụ; kỹ thuật mở rộng ý Contrast/Hypothetical |
| **Listening** | Per-question keyword; option-by-option analysis (A/B/C kể cả sai); map landmark; trap warnings |
| **Speaking** | Toàn bộ bài mẫu; công thức mở rộng ý; phân tích tiêu chí từng band; từ vựng kèm ví dụ |

### Checklist bắt buộc trước khi gen DOCX

- [ ] Đếm số câu hỏi trong raw → số câu trong .md phải bằng nhau?
- [ ] Mỗi câu có đủ 4 trường: **Từ khóa → Dẫn chứng → Phân tích → Đáp án**?
- [ ] Các wrong options (B, D, E...) được giải thích tại sao sai?
- [ ] Transcript / Bài mẫu đầy đủ, không cắt giữa chừng?
- [ ] Thứ tự phần không đổi so với file raw?

---

## 🔄 Pipeline tổng thể

```
Raw DOCX (do người dùng cung cấp)
      │
      ▼  bước 1: extract bằng pandoc hoặc docx2txt
Raw Markdown (scratch/)
      │
      ▼  bước 2: parse + format theo rules + thêm từ vựng
Structured .md  (LS/md/raw<N>/ hoặc RW/md/raw<N>/)
      │
      ▼  bước 3: md_to_docx.sh hoặc wr_md_to_word.sh
Output .docx
      │
      ▼  bước 4: postprocess_docx_tables.py
Final DOCX
```

**Extract raw bằng pandoc:**
```bash
export PATH="/opt/homebrew/bin:$PATH"
pandoc input.docx -t markdown --wrap=none -o scratch/raw_output.md
```

---

## 🟦 SKILL: LISTENING

### Tài liệu tham chiếu

| Mục đích | File |
|---|---|
| Rules đầy đủ | `chuyenDe/LS/md/README.md` |
| **GOLD STANDARD** (Section 1 form + Section 2 MCQ + Section 3 dialogue + Section 4 monologue) | `chuyenDe/LS/md/rawls7/Listening/Level1/W8.md` |
| Gold Standard thêm (map + matching) | `chuyenDe/LS/md/rawl12/Listening/Level2/W12.md` |
| Ví dụ đã hoàn chỉnh gần nhất | `chuyenDe/LS/md/rawl14/Listening/Level3/W14.md` |

### Cấu trúc file Listening .md (thứ tự bắt buộc)

```
─ frontmatter (---)
─ ::: collectiontitle ::: 
─ ::: cdlisteningsection :::        ← SECTION 1 exam questions ONLY
─ ::: cdlisteningsection :::        ← SECTION 2 exam questions ONLY
─ ::: cdlisteningsection :::        ← SECTION 3 exam questions ONLY
─ ::: cdlisteningsection :::        ← SECTION 4 exam questions ONLY
─ ## Phần 1: Hướng dẫn Section 1    ← NGOÀI container
─ ## Phần 2: Hướng dẫn Section 2
─ ## Phần 3: Lời giải — Answer Key
─ ## Phần 4: Lời băng — Transcript  ← ::: cdtranscriptsection :::
─ ## Từ vựng                         ← ::: cdreadingvocabtable :::
```

### Frontmatter bắt buộc

```yaml
---
title: "TÀI LIỆU CHUYÊN ĐỀ LISTENING"
skill: Listening
level: 1        # 1 | 2 | 3
week: 8
---
```

### Exam question block (trong cdlisteningsection)

Xem thực tế tại `rawls7/Listening/Level1/W8.md` dòng 11–54:

```markdown
::: cdlisteningsection

## SECTION 1 Question 1 -- 10

Complete the notes below.

Write **ONE WORD AND/OR A NUMBER** for each answer.

**Flanders Conference Hotel**

**Conference facilities**

- the **1** ............................... room for talks
- area for coffee and an **3** ..............................
- free **4** ................................. throughout

:::
```

### Hướng dẫn chi tiết từng Section (NGOÀI container)

Format bắt buộc cho mỗi câu hỏi — phải đủ 5 trường:

```markdown
## Phần 1: Hướng dẫn Section 1

### I. HƯỚNG DẪN CHUNG
[chiến lược tổng quát theo dạng bài: form filling / MCQ / matching / map]

### II. HƯỚNG DẪN CHI TIẾT

***Bước 1: Phân tích hướng dẫn và giới hạn từ***
[ONE WORD / TWO WORDS / A NUMBER...]

***Bước 2-3: Đọc câu hỏi, gạch chân keyword, dự đoán***

- **Câu N:** [từ khóa] → [dự đoán ngữ pháp: danh từ/tính từ/số] → [paraphrase dự kiến]

***Bước 4-5: Phân tích đáp án***

- **Câu N:**
    - Audio: *"quote nguyên văn từ transcript"*
    - Option A: [phân tích] → ✔ (vì ...) hoặc ✘ (vì ...)
    - Option B: [phân tích] → ✘ (vì ...)
    - Option C: [phân tích] → ✘ (vì ...)
```

### Transcript format

- **Dialogue (2+ speakers)** → bảng `cdtranscripttable`:

```markdown
::: cdtranscriptsection

SECTION 1

::: cdtranscripttable
| Speaker | Dialogue |
|---------|----------|
| ANGELA | Hello, Flanders conference hotel. |
| MAN | Oh, hi. I wanted to ask about your conference facilities. |
:::

SECTION 4

Good morning. My name's Mark Bergin...
(plain text — monologue)

:::
```

- **Monologue (1 speaker)** → plain text, KHÔNG dùng table

### Gen DOCX — Listening

```bash
export PATH="/opt/homebrew/bin:$PATH"
REF=~/Desktop/TheForumPrj/chuyenDe/word/reference-speaking.docx
CONV=~/Desktop/TheForumPrj/chuyenDe/word/pandoc/md_to_docx.sh
POST=~/Desktop/TheForumPrj/chuyenDe/scripts/postprocess_docx_tables.py

for LEVEL in 1 2 3; do
  MD=~/Desktop/TheForumPrj/chuyenDe/LS/md/rawl14/Listening/Level${LEVEL}/W14.md
  OUT=~/Desktop/TheForumPrj/chuyenDe/LS/docx/rawl14/Listening/Level${LEVEL}
  mkdir -p "$OUT"
  bash "$CONV" "$MD" "$OUT/W14.docx" "$REF"
  python3 "$POST" "$OUT/W14.docx"
  echo "Listening L${LEVEL} done"
done
```

> **Lưu ý:** Listening dùng `reference-speaking.docx` (không phải reference-listening).

---

## 🟩 SKILL: SPEAKING

### Tài liệu tham chiếu

| Mục đích | File |
|---|---|
| Rules đầy đủ | `chuyenDe/LS/md/README.md` (phần Speaking) |
| **GOLD STANDARD** | `chuyenDe/LS/md/raws11/Speaking/Level1/W11.md` |
| Gold Standard thêm | `chuyenDe/LS/md/raws13/Speaking/Level1/W13.md` |

### Cấu trúc file Speaking .md

```
─ frontmatter (---)
─ ::: collectiontitle :::
─ ## Part 1: [topic]          ← câu hỏi + phân tích + bài mẫu
─ ## Part 2: [cue card topic] ← cue card + full sample + vocab
─ ## Part 3: [topic]          ← câu hỏi thảo luận + chiến lược + bài mẫu
─ ## Tiêu chí đánh giá        ← band descriptors
─ ## Từ vựng gợi ý            ← ::: cdvocabtable :::
```

### Gen DOCX — Speaking

Giống Listening — thay đường dẫn `rawl` → `raws`.

---

## 🟥 SKILL: READING

### Tài liệu tham chiếu

| Mục đích | File |
|---|---|
| Rules đầy đủ | `chuyenDe/RW/md/README.md` |
| **GOLD STANDARD** (TRUE/FALSE/NG + Summary) | `chuyenDe/RW/md/raww9/Reading/Level1/W10.md` |
| Gold Standard (Matching + YES/NO/NG) | `chuyenDe/RW/md/raww9/Reading/Level2/W10.md` |
| Ví dụ gần nhất | `chuyenDe/RW/md/rawr14/Reading/Level2/W14.md` |

### Cấu trúc file Reading .md

```
─ frontmatter (---)
─ ::: collectiontitle :::
─ ::: prompt :::                  ← Bài đọc nguyên văn (đoạn A, B, C...)
─ ## Phần I: Câu hỏi
  ─ ::: cdlisteningsection :::   ← Questions block 1
  ─ ::: cdlisteningsection :::   ← Questions block 2
─ ## Phần II: Hướng dẫn làm bài  ← NGOÀI container
─ ## Phần III: Lời giải — Answer Key
─ ## Từ vựng                      ← ::: cdreadingvocabtable :::
```

### Frontmatter bắt buộc

```yaml
---
title: "TÀI LIỆU CHUYÊN ĐỀ READING"
skill: Reading
level: 1        # 1 | 2 | 3
week: 14
---
```

### Dạng câu hỏi theo Level

| Level | Dạng bài thường gặp |
|---|---|
| L1 | TRUE/FALSE/NOT GIVEN + Note/Summary Completion |
| L2 | Paragraph Headings + Multiple Choice + Sentence Completion |
| L3 | Matching Statements + YES/NO/NOT GIVEN + Date/Name Matching |

### Instruction box — TRUE/FALSE/NOT GIVEN (thực tế từ W10.md)

```markdown
> Do the following statements agree with the information given in Reading Passage 2?

> In boxes 14-20 on your answer sheet, write

::: cdoptiontable
| Option | Meaning |
| --- | --- |
| **TRUE** | the statement is true |
| **FALSE** | the statement is false |
| **NOT GIVEN** | the information is not given in the passage |
:::

::: cdquestions
**14.** The term "biodiversity" consists of living creatures and the environment that they live in.  
**15.** There are species that have not been researched because it's unnecessary to study all creatures.  
:::
```

### Format hướng dẫn từng câu — BẮT BUỘC đủ 4 trường

Ví dụ thực tế từ `raww9/Reading/Level1/W10.md` dòng 101–106:

```markdown
- **Câu 14:** The term "biodiversity" consists of living creatures...
    - **Từ khóa:** "term 'biodiversity'", "consists of", "living creatures", "environment".
    - **Định vị:** Đoạn A. Tìm định nghĩa của "biodiversity".
    - **Dẫn chứng:** Bài đọc viết: "...biodiversity comprises every form of life [= living creatures]...
      and the ecosystems of which they are apart [= environment]."
    - **Phân tích:** "Comprises" đồng nghĩa với "consists of". Định nghĩa bao gồm cả sinh vật và hệ sinh thái.
    - **Đáp án:** TRUE
```

> **Quy tắc chặt:** Mỗi câu hỏi = đủ 4 trường (Từ khóa / Định vị+Dẫn chứng / Phân tích / Đáp án).
> Với dạng Multiple Choice: phân tích **tất cả** options A, B, C, D — kể cả options sai.

### Answer key table (cuối file)

```markdown
::: cdanswerkeytable
| Câu | Đáp án |
| --- | --- |
| **14** | **TRUE** |
| **15** | **FALSE** |
:::
```

### Vocabulary table (cuối file)

Ví dụ thực tế từ `raww9/Reading/Level1/W10.md` dòng 220–237:

```markdown
::: cdreadingvocabtable
| Từ vựng (Từ loại) | Phiên âm | Nghĩa tiếng Anh (Giải thích tiếng Việt) | Ví dụ minh họa |
| --- | --- | --- | --- |
| **biodiversity** (n) | /ˌbaɪ.əʊ.daɪˈvɜː.sɪ.ti/ | the variety of plant and animal life (sự đa dạng sinh học) | The Amazon has exceptional biodiversity. |
| **keystone species** (n) | /ˈkiː.stəʊn ˌspiː.ʃiːz/ | a species with large ecosystem impact (loài then chốt) | Sea otters are a keystone species in kelp forests. |
:::
```

### Gen DOCX — Reading

Reading **không** dùng `wr_md_to_word.sh` (script đó chỉ xử lý `Writing/`). Dùng trực tiếp:

```bash
export PATH="/opt/homebrew/bin:$PATH"
REF=~/Desktop/TheForumPrj/chuyenDe/word/reference-writing.docx
CONV=~/Desktop/TheForumPrj/chuyenDe/word/pandoc/md_to_docx.sh
POST=~/Desktop/TheForumPrj/chuyenDe/scripts/postprocess_docx_tables.py

for LEVEL in 1 2 3; do
  MD=~/Desktop/TheForumPrj/chuyenDe/RW/md/rawr14/Reading/Level${LEVEL}/W14.md
  OUT=~/Desktop/TheForumPrj/chuyenDe/RW/docx/rawr14/Reading/Level${LEVEL}
  mkdir -p "$OUT"
  bash "$CONV" "$MD" "$OUT/W14.docx" "$REF"
  python3 "$POST" "$OUT/W14.docx"
  echo "Reading L${LEVEL} done"
done
```

---

## 🟨 SKILL: WRITING

### Tài liệu tham chiếu

| Mục đích | File |
|---|---|
| Rules đầy đủ | `chuyenDe/RW/md/README.md` |
| **GOLD STANDARD** L1 (Task 2 Opinion) | `chuyenDe/RW/md/raww9/Writing/Level1/W9.md` |
| Gold Standard L2 (Task 1 Chart) | `chuyenDe/RW/md/raww9/Writing/Level2/W9.md` |
| Gold Standard thêm | `chuyenDe/RW/md/raww13/Writing/Level1/W13.md` |

### Cấu trúc file Writing .md

```
─ frontmatter (---)
─ ::: collectiontitle :::
─ ::: prompt :::           ← Đề bài nguyên văn
─ [yêu cầu đề — Do you agree? / Summarise...]
─ ## Phần I: Xây dựng nền tảng / Phân tích dữ liệu
─ ## Phần II: Hướng dẫn viết bài / Bài mẫu
─ ## Phần III: Công cụ ngôn ngữ (Grammar + Vocabulary)
─ [## Phần IV: Từ vựng tổng hợp — nếu cần]
```

### Frontmatter bắt buộc

```yaml
---
title: "TÀI LIỆU CHUYÊN ĐỀ WRITING"
skill: Writing
level: 1
week: 9
dates: "Mar 9-15"
---
```

### Kỹ thuật mở rộng ý trong Phần I — BẮT BUỘC giữ đủ

Ví dụ thực tế từ `raww9/Writing/Level1/W9.md` dòng 38–50:

```markdown
Kĩ thuật mở rộng ý tưởng

- **[Phương pháp So sánh (Contrast)]{.cdblue}:**
    - **Ý tưởng:** Thư viện yên tĩnh.
    - **Viết:** Ở nhà thường ồn ào, NHƯNG thư viện thì rất yên tĩnh để tập trung.
- **[Liên hệ Thực tế (Real-world Connection)]{.cdblue}:**
    - **Ý tưởng:** Người nghèo cần thư viện.
    - **Viết:** Nhiều học sinh nghèo không có tiền mua laptop, vì vậy họ cần thư viện.
- **[Giả định "Nếu - Thì" (Hypothetical Scenarios)]{.cdblue}:**
    - **Ý tưởng:** Nếu đóng cửa thư viện.
    - **Viết:** Nếu thư viện đóng cửa, người già sẽ không có nơi đọc sách.
```

### Nội dung theo Level

| Level | Phần I | Phần II | Band |
|---|---|---|---|
| L1 | Brainstorming + Dàn ý | Bài mẫu full (Intro+Body1+Body2+Conclusion) | 4→5 |
| L2 | Phân tích chart + xu hướng | Mở bài + Overview + Body | 5→6 |
| L3 | Chart nâng cao (overtaking) | Tương tự L2 + collocations | 6→7 |

### Gen DOCX — Writing

```bash
export PATH="/opt/homebrew/bin:$PATH"
bash ~/Desktop/TheForumPrj/chuyenDe/scripts/wr_md_to_word.sh \
  ~/Desktop/TheForumPrj/chuyenDe/RW/md/raww13 \
  ~/Desktop/TheForumPrj/chuyenDe/RW/docx/raww13
```

> Script `wr_md_to_word.sh` chỉ xử lý thư mục con tên `Writing/`. Không dùng cho Reading.

---

## 🎨 Markdown → Word Style Mapping

Chi tiết đầy đủ tại `chuyenDe/word/README.md` (section 3).

| Markdown | Word Style | Màu |
|---|---|---|
| `## ...` | CD Section | Đỏ `#E52B20`, nền xám nhạt |
| `### ...` | CD Step | Xanh dương `#1F4E79`, nền xanh nhạt |
| `#### ...` | CD Green Heading | Xanh lá `#5AA244` — hạn chế dùng |
| `> blockquote` | CD Note | Tím `#7A1FA2` — chỉ dùng cho lưu ý quan trọng |
| `::: prompt :::` | Prompt Box | Viền nổi bật |
| `::: collectiontitle :::` | Collection Title | Tiêu đề trang |

## 📦 Containers đặc biệt

| Container | Dùng ở đâu | Ví dụ file |
|---|---|---|
| `::: collectiontitle :::` | Đầu mọi file | Tất cả |
| `::: prompt :::` | Đề bài Writing / Bài đọc Reading | `raww9/Writing/Level1/W9.md` |
| `::: cdlisteningsection :::` | Listening exam questions | `rawls7/Listening/Level1/W8.md` |
| `::: cdtranscriptsection :::` | Toàn bộ transcript | `rawls7/Listening/Level1/W8.md` |
| `::: cdtranscripttable :::` | Dialogue 2-column table | `rawls7/Listening/Level1/W8.md` |
| `::: cdreadingvocabtable :::` | Bảng từ vựng 4 cột | `raww9/Reading/Level1/W10.md` |
| `::: cdvocabtable :::` | Bảng từ vựng Writing/Speaking (3 cột) | `raww9/Writing/Level1/W9.md` |
| `::: cdoptiontable :::` | Bảng TRUE/FALSE/NG instructions | `raww9/Reading/Level1/W10.md` |
| `::: cdquestions :::` | Cụm câu hỏi Reading (1 dòng/câu) | `raww9/Reading/Level1/W10.md` |
| `::: cdanswerkeytable :::` | Bảng đáp án tổng hợp | `raww9/Reading/Level1/W10.md` |

---

## 🛠️ Scripts & Tools

| Script | Dùng khi | Lưu ý |
|---|---|---|
| `word/pandoc/md_to_docx.sh` | Gen 1 file DOCX đơn lẻ | Truyền thêm `reference-*.docx` |
| `scripts/wr_md_to_word.sh` | Gen hàng loạt **Writing only** | Không dùng cho Reading |
| `scripts/ls_md_to_word.sh` | Gen hàng loạt Listening/Speaking | Xem script để biết reference nào |
| `scripts/postprocess_docx_tables.py` | Fix table width/indent/grid | Chạy sau mọi lần gen DOCX |
| `word/build_reference_docx.py` | Tạo lại reference-*.docx | Chỉ khi đổi style/font |

> ⚠️ **PATH FIX:** Luôn thêm dòng này trước khi chạy bất kỳ script nào:
> ```bash
> export PATH="/opt/homebrew/bin:$PATH"
> ```
> Pandoc được cài tại `/opt/homebrew/bin` — không nằm trong PATH mặc định.

### Reference .docx dùng cho từng kỹ năng

| Kỹ năng | Reference file |
|---|---|
| Writing | `word/reference-writing.docx` |
| Reading | `word/reference-writing.docx` (dùng chung) |
| Listening | `word/reference-speaking.docx` (dùng chung) |
| Speaking | `word/reference-speaking.docx` |

---

## 📋 Workflow chuẩn khi nhận raw mới

```
1. Đọc file này (AGENT.md) — đặc biệt Rule Số 1
2. Đọc README tương ứng:
   - LS skill  → LS/md/README.md
   - RW skill  → RW/md/README.md
   - Word/style → word/README.md
3. Mở GOLD STANDARD file tương ứng để tham chiếu cấu trúc:
   - Listening → rawls7/Listening/Level1/W8.md
   - Speaking  → raws11/Speaking/Level1/W11.md
   - Reading   → raww9/Reading/Level1/W10.md
   - Writing   → raww9/Writing/Level1/W9.md
4. Extract raw DOCX → pandoc → scratch/*.md
5. Parse + format → structured .md (giữ 100% nội dung, chỉ format)
6. Self-check checklist no-truncation (xem mục RULE SỐ 1)
7. Gen DOCX (dùng đúng command theo kỹ năng)
8. Chạy postprocess_docx_tables.py
```

---

## 🗂️ Bảng tra nhanh Gold Standard

| Kỹ năng | Level | Gold Standard file | Dạng bài nổi bật |
|---|---|---|---|
| **Listening** | L1 | `rawls7/Listening/Level1/W8.md` | Section 1 Form, Section 2 MCQ |
| **Listening** | L2 | `rawl12/Listening/Level2/W12.md` | Section 3 Map, Section 4 Gap-fill |
| **Listening** | L3 | `rawl12/Listening/Level3/W12.md` | Section 3 Matching, Section 4 Notes |
| **Speaking** | L1 | `raws11/Speaking/Level1/W11.md` | Part 1, Part 2, Part 3 full |
| **Speaking** | L2/L3 | `raws13/Speaking/Level2/W13.md` | Band 5-7 targets |
| **Reading** | L1 | `raww9/Reading/Level1/W10.md` | TRUE/FALSE/NG + Summary |
| **Reading** | L2 | `raww9/Reading/Level2/W10.md` | Paragraph Headings + MCQ |
| **Reading** | L3 | `raww9/Reading/Level3/W10.md` | Matching + YES/NO/NG |
| **Writing** | L1 | `raww9/Writing/Level1/W9.md` | Task 2 Opinion Essay |
| **Writing** | L2 | `raww9/Writing/Level2/W9.md` | Task 1 Bar/Pie/Table |
| **Writing** | L3 | `raww13/Writing/Level3/W13.md` | Task 1 Line/Mixed Graph |
