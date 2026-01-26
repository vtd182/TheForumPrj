on run argv
  if (count of argv) < 2 then
    error "Usage: docx_to_pdf_word.applescript <docx1> <pdf1> [<docx2> <pdf2> ...]"
  end if
  if ((count of argv) mod 2) is not 0 then
    error "Arguments must be pairs: <docx> <pdf>"
  end if

  tell application "Microsoft Word"
    set visible to false
    try
      set display alerts to none
    end try
  end tell

  tell application "Microsoft Word"
    repeat with i from 1 to (count of argv) by 2
      set docxPath to item i of argv
      set pdfPath to item (i + 1) of argv

      set docxFile to POSIX file docxPath
      set pdfFile to POSIX file pdfPath

      open docxFile
      set docRef to active document

      -- Word uses fixed-format export via "save as" with PDF file format.
      save as docRef file name pdfFile file format format PDF
      close docRef saving no
    end repeat
    quit
  end tell
end run

