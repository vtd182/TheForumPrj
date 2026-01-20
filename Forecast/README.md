# Forecast Speaking Templates (XeLaTeX)

Repo có 2 template LaTeX theo đúng layout của:
- `Forecast/forecastP1.pdf` (Part 1)
- `Forecast/forecasrP2.pdf` (Part 2 + Part 3)

## Yêu cầu
- Compile bằng `xelatex`
- Font Latin Modern nằm trong `font/latin-modern-roman` và `font/Latin-Modern-Sans`
- Font Impact: `font/UTM-Impact.ttf` (dùng cho header + watermark)

## Template Part 1 (P1)
- Thư mục: `Forecast/templateP1`
- File chính: `Forecast/templateP1/main.tex`
- Class: `Forecast/templateP1/forecastp1.cls`

### API chính
- `\makeforecastheader{author}{documentTitle}{collectionSubtitle}`
- `\forecasttopic{Topic 1: ...}` (tự `\clearpage` giữa các topic)
- `\forecastqa{Question?}{Sample answer...}`

Compile:
```bash
cd Forecast/templateP1
xelatex main.tex
```

## Template Part 2 + 3 (P2)
- Thư mục: `Forecast/templateP23`
- File chính: `Forecast/templateP23/main.tex`
- Class: `Forecast/templateP23/forecastp23.cls`

### API chính
- `\makeforecastheader{author}{documentTitle}{subtitle}`
- `\forecasttopic{Topic 1: ...}` (mỗi topic bắt đầu ở trang mới)
- `\forecastparttitle{IELTS SPEAKING PART 2}` (tuỳ chọn)
- `\forecastcuecard{prompt}{\item ...}` (box xanh)
- Version support:
  - 1 version: `\forecastsample{...}`
  - nhiều version: `\forecastsample[1]{...}`, `\forecastsample[2]{...}`, ...
- Vocab table (tuỳ chọn):
  - `\begin{forecastvocabtable} ... \forecastvocabrow{...} ... \end{forecastvocabtable}`

Compile:
```bash
cd Forecast/templateP23
xelatex main.tex
```
