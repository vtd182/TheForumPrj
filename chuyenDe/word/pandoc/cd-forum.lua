-- Pandoc Lua filter: map Markdown structure/classes to Word styles in reference.docx
--
-- Usage:
--   pandoc input.md -o output.docx \
--     --reference-doc=chuyenDe/word/reference.docx \
--     --lua-filter=chuyenDe/word/pandoc/cd-forum.lua

local utils = require("pandoc.utils")

local SPAN_STYLE = {
  cdred = "CD Red",
  cdblue = "CD Blue",
  cdgreen = "CD Green",
  cdpurple = "CD Purple",
}

local BLOCK_STYLE = {
  collectiontitle = "CD Collection Title",
  prompt = "CD Prompt",
  cdsection = "CD Section",
  cdstep = "CD Step",
  cdgreenheading = "CD Green Heading",
  cdnote = "CD Note",
}

local TABLE_STYLE = {
  cdvocabtable = "CDVocabTable",
  cdoptiontable = "CDOptionTable",
  cdanswertable = "CDAnswerTable",
  cdchoicetable = "CDChoiceTable",
}

local function set_custom_style(attr, style_name)
  -- Pandoc >= 3 treats elements as immutable; build a new Attr.
  local id = ""
  local classes = {}
  local attributes = {}

  if attr ~= nil then
    id = attr.identifier or ""
    classes = attr.classes or {}
    if attr.attributes ~= nil then
      for k, v in pairs(attr.attributes) do
        attributes[k] = v
      end
    end
  end

  attributes["custom-style"] = style_name
  return pandoc.Attr(id, classes, attributes)
end

local function has_class(attr, class_name)
  for _, c in ipairs(attr.classes or {}) do
    if c == class_name then
      return true
    end
  end
  return false
end

local function div_to_single_para(div, style_name)
  local inlines = {}
  for _, blk in ipairs(div.content) do
    if blk.t == "Para" or blk.t == "Plain" then
      if #inlines > 0 then
        table.insert(inlines, pandoc.LineBreak())
      end
      for _, il in ipairs(blk.content) do
        table.insert(inlines, il)
      end
    else
      local text = utils.stringify(blk)
      if text ~= "" then
        if #inlines > 0 then
          table.insert(inlines, pandoc.LineBreak())
        end
        table.insert(inlines, pandoc.Str(text))
      end
    end
  end

  local attr = set_custom_style(pandoc.Attr("", {}, {}), style_name)
  return pandoc.Para(inlines, attr)
end

function Header(el)
  if el.level == 2 then
    return pandoc.Header(el.level, el.content, set_custom_style(el.attr, "CD Section"))
  end
  if el.level == 3 then
    return pandoc.Header(el.level, el.content, set_custom_style(el.attr, "CD Step"))
  end
  if el.level == 4 then
    return pandoc.Header(el.level, el.content, set_custom_style(el.attr, "CD Green Heading"))
  end
  return el
end

function BlockQuote(el)
  -- Treat blockquotes as notes by wrapping in a styled Div.
  return pandoc.Div(el.content, set_custom_style(pandoc.Attr("", {}, {}), "CD Note"))
end

function Div(el)
  local classes = {}
  if el.attr and el.attr.classes then
    classes = el.attr.classes
  end

  for _, class_name in ipairs(classes) do
    local table_style_name = TABLE_STYLE[class_name]
    if table_style_name then
      local out = {}
      for _, blk in ipairs(el.content) do
        if blk.t == "Table" then
          local attr = set_custom_style(blk.attr, table_style_name)
          local ncols = #blk.colspecs
          local colspecs = blk.colspecs
          if ncols > 0 then
            colspecs = {}
            if class_name == "cdanswertable" and ncols == 3 then
              -- Make analysis column wider for readability.
              local weights = { 0.14, 0.72, 0.14 }
              for i = 1, ncols do
                local align = blk.colspecs[i][1]
                colspecs[i] = { align, weights[i] }
              end
            elseif class_name == "cdchoicetable" and ncols == 2 then
              local weights = { 0.18, 0.82 }
              for i = 1, ncols do
                local align = blk.colspecs[i][1]
                colspecs[i] = { align, weights[i] }
              end
            else
              local w = 1.0 / ncols
              for i = 1, ncols do
                local align = blk.colspecs[i][1]
                colspecs[i] = { align, w }
              end
            end
          end
          table.insert(out, pandoc.Table(blk.caption, colspecs, blk.head, blk.bodies, blk.foot, attr))
        else
          table.insert(out, blk)
        end
      end
      return out
    end
  end

  for _, class_name in ipairs(classes) do
    if class_name == "cdquestions" then
      -- Apply paragraph style to all paragraphs inside this Div.
      return pandoc.Div(el.content, set_custom_style(el.attr, "CDQuestion"))
    end
  end

  for _, class_name in ipairs(classes) do
    local style_name = BLOCK_STYLE[class_name]
    if style_name then
      return pandoc.Div(el.content, set_custom_style(el.attr, style_name))
    end
  end
  return el
end

function Span(el)
  local classes = {}
  if el.attr and el.attr.classes then
    classes = el.attr.classes
  end
  for _, class_name in ipairs(classes) do
    local style_name = SPAN_STYLE[class_name]
    if style_name then
      return pandoc.Span(el.content, set_custom_style(el.attr, style_name))
    end
  end
  return el
end
