# Listening Markdown Files - Formatting Guidelines

## Transcript Formatting Rules

### Auto-Detection: Dialogue vs Monologue

The transcript conversion script automatically detects whether a section contains:
- **Dialogue** (2+ speakers) → Convert to 2-column table
- **Monologue** (1 speaker) → Keep plain text format

**Examples:**

#### Dialogue (2+ speakers) → Table Format
```markdown
### SECTION 1

::: cdtranscripttable
| Speaker | Dialogue |
|---------|----------|
| ANGELA | Hello, Flanders conference hotel. |
| MAN | Oh, hi. I wanted to ask about... |
:::
```

#### Monologue (1 speaker) → Plain Text
```markdown
### SECTION 2

GUIDE: Welcome everyone to the National Museum...
(continues in plain text)
```

### Important Rules

1. **Never manually format transcripts** - Use `convert_transcript.py` script
2. **Plain text for monologues** - Do NOT convert single-speaker sections to tables
3. **Table for dialogues only** - Only use `::: cdtranscripttable` when 2+ speakers detected
4. **Preserve speaker names** - Keep original UPPERCASE speaker labels
5. **No empty cells** - Each dialogue must have both speaker and content
6. **Section headers are plain text** - No bold or heading formatting for "SECTION X" titles in transcripts

### Running the Conversion

```bash
cd LS
python3 convert_transcript.py
```

The script will:
- Detect number of unique speakers per section
- Convert to table if 2+ speakers
- Keep plain text if 1 speaker
- Preserve all existing formatting and div wrappers

## Section Container Guidelines

### Wrapping Sections

Each SECTION (questions + analysis) should be wrapped in:

```markdown
::: cdlisteningsection

## SECTION 1 Question 1 -- 10
[content]

## Phần 1: Section 1
[analysis]

:::
```

### What NOT to Wrap

- Answer Key sections
- Transcript sections
- Vocabulary tables
- Frontmatter and collection title

## Visual Styling

- **Section containers**: Red borders with 3D shadow
- **SECTION headers**: Centered, 14pt, blue
- **CDStep spacing**: Increased to prevent sticking
- **Transcript tables**: Alternating row colors (#F5F5F5)
