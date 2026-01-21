% ============================================
% FORUMVOCAB DOCUMENT CLASS
% ============================================
% A custom LaTeX class for IELTS Vocabulary documents
% Created by: The Forum Center
% Version: 1.0
% ============================================

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{forumvocab}[2026/01/19 v1.0 IELTS Vocabulary Document Class]

% ============================================
% 1. BASE CLASS
% ============================================
\LoadClass[12pt,a4paper]{article}

% ============================================
% 2. REQUIRED PACKAGES
% ============================================
% Note: inputenc/fontenc not needed for XeTeX - it handles UTF-8 natively
\RequirePackage[english,vietnamese]{babel}
% Disable babel shorthands for double quotes. Some babel language shorthands
% make `"` active and break literal quotes in examples/notes (e.g. "Tube.").
\addto\extrasenglish{\shorthandoff{"}}
\addto\extrasvietnamese{\shorthandoff{"}}
\AtBeginDocument{%
  \shorthandoff{"}%
  \catcode`\"=12\relax
}
\RequirePackage[a4paper, left=2cm, right=2cm, top=0cm, bottom=0cm, includehead, includefoot, headheight=50pt, footskip=1.5cm]{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{multicol}
\RequirePackage{xcolor}
\RequirePackage{tcolorbox}
\RequirePackage{graphicx}
\RequirePackage{tikz}
\RequirePackage{eso-pic}
\RequirePackage{fontspec}
\usetikzlibrary{calc}

% ============================================
% 3. FONT DEFINITIONS
% ============================================
% Prefer project-bundled fonts (if present), otherwise fall back to system fonts.
% Expected structure (as added in this repo):
%   ../../font/latin-modern-roman/*.otf
%   ../../font/Latin-Modern-Sans/*.otf
\newcommand{\forumvocab@fontroot}{}%
\IfFileExists{./@font/latin-modern-roman/lmroman10-regular.otf}{\renewcommand{\forumvocab@fontroot}{./@font}}{%
  \IfFileExists{../../@font/latin-modern-roman/lmroman10-regular.otf}{\renewcommand{\forumvocab@fontroot}{../../@font}}{%
    \IfFileExists{../../font/latin-modern-roman/lmroman10-regular.otf}{\renewcommand{\forumvocab@fontroot}{../../font}}{%
      \IfFileExists{./font/latin-modern-roman/lmroman10-regular.otf}{\renewcommand{\forumvocab@fontroot}{./font}}{}%
    }%
  }%
}%

\ifx\forumvocab@fontroot\empty
  \setmainfont{Latin Modern Roman}
  \setsansfont{Latin Modern Sans}
\else
  \setmainfont[
    Path=\forumvocab@fontroot/latin-modern-roman/,
    Extension=.otf,
    UprightFont=lmroman10-regular,
    BoldFont=lmroman10-bold,
    ItalicFont=lmroman10-italic,
    BoldItalicFont=lmroman10-bolditalic
  ]{Latin Modern Roman}
  \setsansfont[
    Path=\forumvocab@fontroot/Latin-Modern-Sans/,
    Extension=.otf,
    UprightFont=lmsans10-regular,
    BoldFont=lmsans10-bold,
    ItalicFont=lmsans10-oblique,
    BoldItalicFont=lmsans10-boldoblique
  ]{Latin Modern Sans}
\fi

% Custom Impact font for headers
\newfontfamily\impactfont{UTM-Impact.ttf}[
  Path = ./,
  Extension = .ttf,
  UprightFont = UTM-Impact
]

% IPA font: prefer a font with good IPA coverage to avoid missing glyphs.
\IfFontExistsTF{Charis SIL}{%
  \newfontfamily\forumvocab@ipafont{Charis SIL}[Scale=MatchLowercase]%
}{%
  \IfFontExistsTF{Doulos SIL}{%
    \newfontfamily\forumvocab@ipafont{Doulos SIL}[Scale=MatchLowercase]%
  }{%
    \IfFontExistsTF{Gentium Plus}{%
      \newfontfamily\forumvocab@ipafont{Gentium Plus}[Scale=MatchLowercase]%
    }{%
      \IfFontExistsTF{Noto Serif}{%
        \newfontfamily\forumvocab@ipafont{Noto Serif}[Scale=MatchLowercase]%
      }{%
        \IfFontExistsTF{Noto Sans}{%
          \newfontfamily\forumvocab@ipafont{Noto Sans}[Scale=MatchLowercase]%
        }{%
          \IfFontExistsTF{Times New Roman}{%
            \newfontfamily\forumvocab@ipafont{Times New Roman}[Scale=MatchLowercase]%
          }{%
            \newfontfamily\forumvocab@ipafont[
              Path=\forumvocab@fontroot/latin-modern-roman/,
              Extension=.otf,
              UprightFont=lmroman10-regular,
              BoldFont=lmroman10-bold,
              ItalicFont=lmroman10-italic,
              BoldItalicFont=lmroman10-bolditalic,
              Scale=MatchLowercase
            ]{Latin Modern Roman}%
          }%
        }%
      }%
    }%
  }%
}
\newcommand{\forumvocab@ipa}[1]{{\forumvocab@ipafont\itshape #1}}

% ============================================
% 4. COLOR DEFINITIONS
% ============================================
\definecolor{forumred}{HTML}{E52B20}      % Main red color
\definecolor{textblack}{HTML}{000000}      % Main text color
\definecolor{watermarkgray}{HTML}{FFE5E5}  % Watermark color (lighter red)

% ============================================
% 6. PAGE LAYOUT
% ============================================
\setlength{\parindent}{0pt}
\setlength{\columnsep}{1.5cm}
\setlength{\headheight}{40pt}

% Page number styling (uses the new sans font)
\newcommand{\forumvocab@pagenumfont}{\sffamily\bfseries\fontsize{14}{16}\selectfont}

% ============================================
% 7. WATERMARK (WITH GUARD)
% ============================================
% Work around xdvipdfmx/shipout ordering where the first page can miss the
% transparency resource and render the watermark fully opaque.
\AtBeginDocument{%
  \pgfsetfillopacity{0.15}%
  \pgfsetstrokeopacity{0.15}%
  \pgfsetfillopacity{1}%
  \pgfsetstrokeopacity{1}%
}

% Guard to ensure watermark is only registered once
\ifdefined\forumvocab@watermark@registered\else
  \newcommand{\forumvocab@watermark@registered}{}
  \AddToShipoutPictureBG{%
    \begin{tikzpicture}[remember picture, overlay]
      \node[opacity=0.15] at (current page.center) {%
        \includegraphics[width=15cm]{../wm/logoTF.png}%
      };
    \end{tikzpicture}%
  }
\fi

% ============================================
% 8. HEADER & FOOTER STYLES
% ============================================
\pagestyle{fancy}
\fancyhf{} % Clear all headers and footers

% Footer - Red page number
\fancyfoot[C]{%
  \raisebox{0.15cm}{\textcolor{forumred}{{\forumvocab@pagenumfont\thepage}}}%
}

% ----- First Page Style -----
\fancypagestyle{firstpage}{%
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  % Top border line
  \fancyhead[C]{%
    \begin{tikzpicture}[remember picture, overlay]
      \draw[forumred, line width=5pt] 
        (current page.north west) -- 
        (current page.north east);
    \end{tikzpicture}%
  }
  % Bottom border line and page number
  \fancyfoot[C]{%
    \begin{tikzpicture}[remember picture, overlay]
      \draw[forumred, line width=5pt] 
        (current page.south west) -- 
        (current page.south east);
      \node[text=forumred, font=\forumvocab@pagenumfont] 
        at ([yshift=20pt]current page.south) 
        {\thepage};
    \end{tikzpicture}%
  }
}

% ----- Other Pages Style -----
\fancypagestyle{otherpages}{%
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  \fancyhead[C]{%
    \begin{tikzpicture}[remember picture, overlay]
      % Thick top line
      \draw[forumred, line width=8pt] 
        (current page.north west) -- 
        (current page.north east);

      % Badge dimensions
      \def\w{5.4cm}
      \def\h{0.7cm}
      \def\r{9pt}

      % Badge position
      \coordinate (badgeTopCenter) at ([yshift=-4pt]current page.north);
      \coordinate (A) at ($(badgeTopCenter)+(-\w/2,0)$);

      % Badge shape
      \path[fill=forumred]
        (A)
        -- ++(\w,0)
        -- ++(0,-\h+\r)
        arc[start angle=0,end angle=-90,radius=\r]
        -- ++(-\w+2*\r,0)
        arc[start angle=-90,end angle=-180,radius=\r]
        -- ++(0,\h-\r)
        -- cycle;

      % Badge text
      \node[
        text=white,
        font=\sffamily\bfseries\fontsize{10}{12}\selectfont
      ]
      at ($(badgeTopCenter)+(0,-\h/2)$)
      {Self-study IELTS Material};
    \end{tikzpicture}
  }
  % Bottom border line and page number
  \fancyfoot[C]{%
    \begin{tikzpicture}[remember picture, overlay]
      \draw[forumred, line width=5pt] 
        (current page.south west) -- 
        (current page.south east);
      \node[text=forumred, font=\forumvocab@pagenumfont] 
        at ([yshift=20pt]current page.south) 
        {\thepage};
    \end{tikzpicture}%
  }
}

% ============================================
% 9. FIRST PAGE HEADER COMMAND
% ============================================
% Usage: \makefirstpageheader{Author}{Document Title}{Topic Title}
\newcommand{\makefirstpageheader}[3]{%
\begin{tikzpicture}[remember picture, overlay]

  % ===== PARAMETERS =====
  \def\HeaderHeight{2.4cm}
  \def\WhiteGap{0.18cm}
  \def\SubHeight{0.8cm}

  % ===== MAIN RED HEADER =====
  \fill[forumred]
    (current page.north west)
    rectangle
    ([yshift=-\HeaderHeight]current page.north east);

  % ===== MAIN TITLE =====
  \node[
    text=white,
    font=\impactfont\fontsize{72}{80}\selectfont,
    anchor=south,
    inner sep=0pt,
    outer sep=0pt
  ]
  at ([yshift=-\HeaderHeight-1.2pt]current page.north)
  {IELTS VOCABULARY};

  % ===== WHITE SEPARATOR =====
  \fill[white]
    ([yshift=-\HeaderHeight]current page.north west)
    rectangle
    ([yshift=-\HeaderHeight-\WhiteGap]current page.north east);

  % ===== SUB HEADER =====
  \fill[forumred]
    ([yshift=-\HeaderHeight-\WhiteGap]current page.north west)
    rectangle
    ([yshift=-\HeaderHeight-\WhiteGap-\SubHeight]current page.north east);

  % Left text
  \node[
    text=white,
    font=\sffamily\bfseries\small,
    anchor=west
  ]
  at ([xshift=2cm,
       yshift=-\HeaderHeight-\WhiteGap-\SubHeight/2]
      current page.north west)
  {#1};

  % Right text
  \node[
    text=white,
    font=\sffamily\bfseries\small,
    anchor=east
  ]
  at ([xshift=-2cm,
       yshift=-\HeaderHeight-\WhiteGap-\SubHeight/2]
      current page.north east)
  {#2};

\end{tikzpicture}

% ===== PUSH CONTENT DOWN =====
\vspace{1cm}

\noindent
{\centering\fontsize{14}{17}\sffamily\bfseries #3\par}

\vspace{12pt}
}

% ============================================
% 10. VOCABULARY ENTRY COMMANDS
% ============================================
\newcommand{\forumvocab@vocabhead}[2]{%
  {\sffamily\bfseries\color{forumred}\large #1}%
  \hspace{0.4em}%
  {\forumvocab@ipa{#2}}%
}
\newcommand{\forumvocab@vocabline}[3]{%
  \forumvocab@vocabhead{#1}{#2}%
  \hspace{0.6em}---\hspace{0.6em}%
  #3\par
}

% Full version with example
% Usage: \vocabentry{word}{pronunciation}{definition}{example}{translation}
\newcommand{\vocabentry}[5]{%
  \noindent\forumvocab@vocabline{#1}{#2}{#3}%
  {\itshape\textbf{Example:} #4}\par
  {\itshape (#5)}
  
  \vspace{8pt}
}

% Short version without example
% Usage: \vocabshort{word}{pronunciation}{definition}
\newcommand{\vocabshort}[3]{%
  \noindent\forumvocab@vocabline{#1}{#2}{#3}%
  
  \vspace{8pt}
}

% ============================================
% 11. SECTION COMMANDS
% ============================================
\newcommand{\vocabsection}[1]{%
  \vspace{10pt}
  \noindent
  {\sffamily\bfseries\large\color{forumred} #1}
  \vspace{6pt}
}

\endinput
