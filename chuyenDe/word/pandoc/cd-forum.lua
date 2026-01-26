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

local function set_custom_style(attr, style_name)
  if attr == nil then
    attr = pandoc.Attr("", {}, {})
  end
  if attr.attributes == nil then
    attr.attributes = {}
  end
  attr.attributes["custom-style"] = style_name
  return attr
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

  local para = pandoc.Para(inlines)
  para.attr = set_custom_style(para.attr, style_name)
  return para
end

function Header(el)
  if el.level == 2 then
    el.attr = set_custom_style(el.attr, "CD Section")
    return el
  end
  if el.level == 3 then
    el.attr = set_custom_style(el.attr, "CD Step")
    return el
  end
  if el.level == 4 then
    el.attr = set_custom_style(el.attr, "CD Green Heading")
    return el
  end
  return el
end

function BlockQuote(el)
  -- Treat blockquotes as notes by wrapping in a styled Div.
  local attr = set_custom_style(pandoc.Attr("", {}, {}), "CD Note")
  return pandoc.Div(el.content, attr)
end

function Div(el)
  local classes = {}
  if el.attr and el.attr.classes then
    classes = el.attr.classes
  end
  for _, class_name in ipairs(classes) do
    local style_name = BLOCK_STYLE[class_name]
    if style_name then
      el.attr = set_custom_style(el.attr, style_name)
      return el
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
      el.attr = set_custom_style(el.attr, style_name)
      return el
    end
  end
  return el
end
