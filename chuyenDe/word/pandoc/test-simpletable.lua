-- Test creating simple table programmatically
-- For Pandoc 3.x

function Div(el)
  if el.attr.classes[1] == "testtable" then
    -- Build table manually using SimpleTable (older API, more reliable)
    local content_blocks = el.content
    
    -- For SimpleTable: (caption, alignments, widths, headers, rows)
    local caption = {}
    local aligns = {pandoc.AlignDefault}
    local widths = {0}  -- 0 means auto
    local headers = {{}}  -- empty header row
    local rows = {
      {{content_blocks}}  -- one row with one cell containing all blocks
    }
    
    local tbl = pandoc.SimpleTable(caption, aligns, widths, headers, rows)
    return tbl
  end
  return el
end
