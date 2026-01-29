-- Test pandoc table creation
local el = {content = {pandoc.Para{pandoc.Str("Test")}}}

-- Try to create simplest table
local cell = pandoc.Cell(el.content)
local row = pandoc.Row({cell})

-- Try with SimpleTable first
return pandoc.SimpleTable(
  {},  -- caption
  {{pandoc.AlignDefault, 1.0}},  -- colspecs
  {},  -- headers
  {{cell}}  -- rows (list of list of cells)
)
