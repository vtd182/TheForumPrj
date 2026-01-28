-- Pandoc Lua filter (LaTeX): map Markdown structure/classes to LaTeX macros/environments
--
-- Usage (via wrapper script):
--   pandoc input.md -t latex \
--     --from markdown+raw_attribute+fenced_divs+bracketed_spans+pipe_tables \
--     --lua-filter=chuyenDe/latex/pandoc/cd-forum-latex.lua

local utils = require("pandoc.utils")

local DOC_SKILL = ""

local function latex_escape(s)
  s = s:gsub("\\", "\\textbackslash{}")
  s = s:gsub("([{}$&#%%_])", "\\%1")
  s = s:gsub("%^", "\\^{}")
  s = s:gsub("~", "\\~{}")
  -- Help TeX break long tokens (IPA strings, slashes, dot-separated chunks).
  s = s:gsub("/", "/\\allowbreak{}")
  s = s:gsub("%.", ".\\allowbreak{}")
  return s
end

local function blocks_to_text(blocks)
  local parts = {}
  for _, b in ipairs(blocks or {}) do
    local t = utils.stringify(b)
    if t ~= "" then
      table.insert(parts, t)
    end
  end
  return table.concat(parts, " ")
end

local function inlines_to_text(inlines)
  return utils.stringify(pandoc.Plain(inlines))
end

local function is_ipa_string(s)
  if not s then
    return false
  end
  local t = s:gsub("^%s+", ""):gsub("%s+$", "")
  if not (t:match("^/.+/$")) then
    return false
  end
  -- Most IPA strings include non-ASCII codepoints (UTF-8 bytes >= 128).
  return t:match("[\128-\255]") ~= nil
end

local function render_cd_table(class_name, tbl)
  -- Extract header + body rows as plain text.
  local header_rows = {}
  for _, row in ipairs((tbl.head and tbl.head.rows) or {}) do
    local cells = {}
    for _, cell in ipairs(row.cells or {}) do
      local raw = blocks_to_text(cell.content)
      local escaped = latex_escape(raw)
      if is_ipa_string(raw) then
        escaped = "\\cdipa{" .. escaped .. "}"
      end
      table.insert(cells, escaped)
    end
    table.insert(header_rows, cells)
  end

  local body_rows = {}
  for _, body in ipairs(tbl.bodies or {}) do
    for _, row in ipairs(body.body or {}) do
      local cells = {}
      for _, cell in ipairs(row.cells or {}) do
        local raw = blocks_to_text(cell.content)
        local escaped = latex_escape(raw)
        if is_ipa_string(raw) then
          escaped = "\\cdipa{" .. escaped .. "}"
        end
        table.insert(cells, escaped)
      end
      table.insert(body_rows, cells)
    end
  end

  local ncols = #tbl.colspecs
  if ncols == 0 then
    -- Fallback: infer from first row.
    if #header_rows > 0 then
      ncols = #header_rows[1]
    elseif #body_rows > 0 then
      ncols = #body_rows[1]
    end
  end

  local function widths_for()
    if class_name == "cdanswertable" and ncols == 3 then
      return { 0.14, 0.72, 0.14 }
    elseif (class_name == "cdchoicetable" or class_name == "cdanswerkeytable") and ncols == 2 then
      return { 0.18, 0.82 }
    elseif class_name == "cdreadingvocabtable" and ncols == 4 then
      return { 0.24, 0.14, 0.40, 0.22 }
    elseif class_name == "cdoptiontable" and ncols == 2 then
      return { 0.22, 0.78 }
    elseif class_name == "cdvocabtable" and ncols == 2 then
      return { 0.18, 0.82 }
    end

    if ncols <= 0 then
      return {}
    end
    local w = 1.0 / ncols
    local widths = {}
    for i = 1, ncols do widths[i] = w end
    return widths
  end

  local function colspec_for_tabularx()
    -- Use tabularx for width correctness; use m{..} for fixed columns.
    if class_name == "cdanswertable" and ncols == 3 then
      return "|M{0.14\\linewidth}|Y|M{0.14\\linewidth}|"
    elseif (class_name == "cdchoicetable" or class_name == "cdanswerkeytable" or class_name == "cdvocabtable") and ncols == 2 then
      return "|M{0.18\\linewidth}|Y|"
    elseif class_name == "cdoptiontable" and ncols == 2 then
      return "|M{0.22\\linewidth}|Y|"
    end

    -- Fallback
    if ncols == 1 then
      return "|Y|"
    end
    local parts = { "|" }
    local w = 1.0 / ncols
    for i = 1, ncols do
      if i == ncols then
        table.insert(parts, "Y|")
      else
        table.insert(parts, string.format("M{%.2f\\linewidth}|", w))
      end
    end
    return table.concat(parts, "")
  end

  local function looks_like_before_after_upgrade_table(normalized_header)
    if not normalized_header or #normalized_header ~= 2 then
      return false
    end
    local a = normalized_header[1] or ""
    local b = normalized_header[2] or ""

    -- Heuristic: these tables usually encode band levels in both headers,
    -- e.g. "Band 4.0" vs "Band 5.5+". Matching on ASCII is robust against
    -- Vietnamese normalization differences (NFC/NFD).
    local band_a = a:match("band%s*([0-9]+%.?[0-9]*)")
    local band_b = b:match("band%s*([0-9]+%.?[0-9]*)")
    if band_a and band_b and band_a ~= band_b then
      return true
    end

    local left_ok = (a:find("original") ~= nil) or (a:find("before") ~= nil)
    local right_ok = (b:find("upgrade") ~= nil) or (b:find("improv") ~= nil) or (b:find("after") ~= nil)
    return left_ok and right_ok
  end

  local function colspec_for_longtable()
    -- Leave room for rules + tabcolsep; keep sum < 1.0 to avoid overfull boxes.
    if class_name == "cdanswertable" and ncols == 3 then
      return "|M{0.10\\linewidth}|M{0.66\\linewidth}|M{0.14\\linewidth}|"
    elseif (class_name == "cdanswerkeytable" or class_name == "cdchoicetable" or class_name == "cdvocabtable") and ncols == 2 then
      return "|M{0.17\\linewidth}|M{0.73\\linewidth}|"
    elseif class_name == "cdoptiontable" and ncols == 2 then
      return "|M{0.20\\linewidth}|M{0.70\\linewidth}|"
    end
    if class_name == "cdreadingvocabtable" and ncols == 4 then
      return "|M{0.22\\linewidth}|M{0.13\\linewidth}|M{0.38\\linewidth}|M{0.20\\linewidth}|"
    end
    -- default longtable: fall back to tabularx spec without Y
    if ncols == 1 then
      return "|M{0.93\\linewidth}|"
    end
    local parts = { "|" }
    local w = 0.93 / ncols
    for _ = 1, ncols do
      table.insert(parts, string.format("M{%.2f\\linewidth}|", w))
    end
    return table.concat(parts, "")
  end

  -- Header analysis (used for styling + some layout overrides).
  local header = header_rows[1]
  local skip_header = false
  local normalized_header = nil
  local force_equal_two_col = false
  if header ~= nil and #header > 0 then
    local normalized = {}
    for _, h in ipairs(header) do
      table.insert(normalized, (h:gsub("\\allowbreak%{%}", "")):lower())
    end
    normalized_header = normalized
    force_equal_two_col = (ncols == 2 and looks_like_before_after_upgrade_table(normalized))

    local is_generic_two_col =
      #normalized == 2
      and ((normalized[1] == "heading" and normalized[2] == "title")
        or (normalized[1] == "option" and (normalized[2] == "meaning" or normalized[2] == "person/choice")))
    if class_name == "cdvocabtable" and is_generic_two_col then
      skip_header = true
    end
    if class_name == "cdchoicetable" and is_generic_two_col then
      skip_header = true
    end
    if class_name == "cdoptiontable" and is_generic_two_col then
      -- Keep centered option table clean (avoid showing "Option / Meaning" header).
      skip_header = true
    end
  end

  local use_longtable = (
    class_name == "cdreadingvocabtable"
    or class_name == "cdanswertable"
    or class_name == "cdanswerkeytable"
    or (#body_rows >= 18 and class_name ~= "cdoptiontable")
  )
  local colspec = use_longtable and colspec_for_longtable() or colspec_for_tabularx()
  if (not use_longtable) and force_equal_two_col then
    -- For "Câu gốc / Câu nâng cấp" (Before & After) tables, use a 50/50 split.
    colspec = "|Y|Y|"
  end

  local out = {}
  table.insert(out, "\\begingroup")
  table.insert(out, "\\sloppy")
  table.insert(out, "\\renewcommand{\\tabularxcolumn}[1]{>{\\RaggedRight\\arraybackslash}m{#1}}")
  table.insert(out, "\\setlength{\\tabcolsep}{6pt}")
  table.insert(out, "\\renewcommand{\\arraystretch}{1.15}")
  table.insert(out, "\\arrayrulecolor{black!25}")

  if not use_longtable then
    table.insert(out, "\\begin{cdtablebox}")
  end

  if class_name == "cdreadingvocabtable" then
    table.insert(out, "\\footnotesize")
    table.insert(out, "\\setlength{\\tabcolsep}{4pt}")
    table.insert(out, "\\renewcommand{\\arraystretch}{1.10}")
    table.insert(out, "\\setlength{\\LTpre}{0pt}")
    table.insert(out, "\\setlength{\\LTpost}{0pt}")
  end
  if use_longtable then
    table.insert(out, "\\setlength{\\tabcolsep}{4pt}")
    table.insert(out, "\\setlength{\\LTleft}{0pt}")
    table.insert(out, "\\setlength{\\LTright}{0pt}")
    table.insert(out, "\\setlength{\\LTpre}{0pt}")
    table.insert(out, "\\setlength{\\LTpost}{0pt}")
  end

  if class_name == "cdoptiontable" then
    table.insert(out, "\\begin{center}")
  end

  if use_longtable then
    table.insert(out, "\\begin{longtable}{" .. colspec .. "}")
  else
    table.insert(out, "\\begin{tabularx}{\\linewidth}{" .. colspec .. "}")
  end
  table.insert(out, "\\hline")

  local function header_row()
    local cells = {}
    for _, h in ipairs(header or {}) do
      table.insert(cells, "\\cdtableheader{" .. h .. "}")
    end
    return "\\rowcolor{topicblue} " .. table.concat(cells, " & ") .. " \\\\ \\hline"
  end

  if header ~= nil and #header > 0 and not skip_header then
    table.insert(out, header_row())
    if use_longtable then
      table.insert(out, "\\endfirsthead")
      table.insert(out, "\\hline")
      table.insert(out, header_row())
      table.insert(out, "\\endhead")
      table.insert(out, "\\hline")
      table.insert(out, "\\endfoot")
      table.insert(out, "\\hline")
      table.insert(out, "\\endlastfoot")
    end
  end

  for _, row in ipairs(body_rows) do
    if #row > 0 then
      table.insert(out, table.concat(row, " & ") .. " \\\\ \\hline")
    end
  end

  if use_longtable then
    table.insert(out, "\\end{longtable}")
  else
    table.insert(out, "\\end{tabularx}")
  end
  if class_name == "cdoptiontable" then
    table.insert(out, "\\end{center}")
  end
  if not use_longtable then
    table.insert(out, "\\end{cdtablebox}")
  end
  table.insert(out, "\\endgroup")

  return pandoc.RawBlock("latex", table.concat(out, "\n"))
end

local function handle_Header(el)
  local text = latex_escape(inlines_to_text(el.content))
  if el.level == 2 then
    return pandoc.RawBlock("latex", "\\cdsection{" .. text .. "}")
  elseif el.level == 3 then
    return pandoc.RawBlock("latex", "\\cdstep{" .. text .. "}")
  elseif el.level == 4 then
    return pandoc.RawBlock("latex", "\\cdgreenheading{" .. text .. "}")
  end
  return el
end

local function handle_BlockQuote(el)
  local out = { pandoc.RawBlock("latex", "\\begin{cdnote}") }
  for _, b in ipairs(el.content or {}) do
    table.insert(out, b)
  end
  table.insert(out, pandoc.RawBlock("latex", "\\end{cdnote}"))
  return out
end

local function handle_Div(el)
  local classes = (el.attr and el.attr.classes) or {}

  for _, c in ipairs(classes) do
    if c == "collectiontitle" then
      local title_text = latex_escape(blocks_to_text(el.content))
      local after = "\\vspace{6pt}"
      if (DOC_SKILL or ""):lower() == "writing" then
        -- Writing typically starts with a prompt box; keep it well below the centered title.
        after = "\\vspace{18pt}"
      end
      return pandoc.RawBlock("latex", "\\workshopcenterheading{" .. title_text .. "}" .. after)
    end
  end

  for _, c in ipairs(classes) do
    if c == "prompt" then
      local prompt_text = latex_escape(blocks_to_text(el.content))
      return pandoc.RawBlock("latex", "\\workshopprompt{" .. prompt_text .. "}")
    end
    if c == "cdquestions" then
      local out = { pandoc.RawBlock("latex", "\\begin{cdquestions}") }
      for _, b in ipairs(el.content or {}) do
        table.insert(out, b)
      end
      table.insert(out, pandoc.RawBlock("latex", "\\end{cdquestions}"))
      return out
    end
    if c == "cdvocabtable" or c == "cdoptiontable" or c == "cdchoicetable" or c == "cdanswertable" or c == "cdanswerkeytable" or c == "cdreadingvocabtable" then
      -- Custom render first table inside this div (most of our MD tables are single-table divs).
      for _, b in ipairs(el.content or {}) do
        if b.t == "Table" then
          return render_cd_table(c, b)
        end
      end
      -- If no table found, fall back to content.
      return el.content
    end
  end

  return el
end

local function handle_Span(el)
  local classes = (el.attr and el.attr.classes) or {}
  for _, c in ipairs(classes) do
    if c == "cdred" then
      local out = { pandoc.RawInline("latex", "\\cdred{") }
      for _, il in ipairs(el.content) do table.insert(out, il) end
      table.insert(out, pandoc.RawInline("latex", "}"))
      return out
    elseif c == "cdblue" then
      local out = { pandoc.RawInline("latex", "\\cdblue{") }
      for _, il in ipairs(el.content) do table.insert(out, il) end
      table.insert(out, pandoc.RawInline("latex", "}"))
      return out
    elseif c == "cdgreen" then
      local out = { pandoc.RawInline("latex", "\\cdgreen{") }
      for _, il in ipairs(el.content) do table.insert(out, il) end
      table.insert(out, pandoc.RawInline("latex", "}"))
      return out
    elseif c == "cdpurple" then
      local out = { pandoc.RawInline("latex", "\\cdpurple{") }
      for _, il in ipairs(el.content) do table.insert(out, il) end
      table.insert(out, pandoc.RawInline("latex", "}"))
      return out
    end
  end
  return el
end

function Pandoc(doc)
  DOC_SKILL = utils.stringify((doc.meta and doc.meta.skill) or "") or ""
  return doc:walk({
    Header = handle_Header,
    BlockQuote = handle_BlockQuote,
    Div = handle_Div,
    Span = handle_Span,
  })
end
