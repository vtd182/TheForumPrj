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
\RequirePackage[utf8]{inputenc}
\RequirePackage[T5]{fontenc}
\RequirePackage[english,vietnamese]{babel}
\RequirePackage[a4paper, left=2cm, right=2cm, top=0cm, bottom=0cm, includehead, includefoot, headheight=50pt, footskip=1.5cm]{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{multicol}
\RequirePackage{xcolor}
\RequirePackage{tcolorbox}
\RequirePackage{graphicx}
\RequirePackage{tikz}
\RequirePackage{eso-pic}
\RequirePackage{palatino}   % Similar to the PDF's serif font
\RequirePackage{helvet}     % Sans-serif font for headers
\RequirePackage{newunicodechar}
\RequirePackage{fontspec}
\usetikzlibrary{calc}

% ============================================
% 3. CUSTOM FONT DEFINITIONS
% ============================================
\newfontfamily\impactfont{UTM-Impact.ttf}[
  Path = ./,
  Extension = .ttf,
  UprightFont = UTM-Impact
]

% ============================================
% 4. COLOR DEFINITIONS
% ============================================
\definecolor{forumred}{HTML}{E52B20}      % Main red color
\definecolor{textblack}{HTML}{000000}      % Main text color
\definecolor{watermarkgray}{HTML}{FFE5E5}  % Watermark color (lighter red)

% ============================================
% 5. IPA UNICODE CHARACTER SUPPORT
% ============================================
\newunicodechar{ɑ}{a}
\newunicodechar{ː}{:}
\newunicodechar{ˈ}{'}
\newunicodechar{ˌ}{,}
\newunicodechar{ə}{@}
\newunicodechar{æ}{ae}
\newunicodechar{ɪ}{I}
\newunicodechar{ʊ}{U}
\newunicodechar{ɔ}{O}
\newunicodechar{ʌ}{A}
\newunicodechar{ɛ}{E}
\newunicodechar{ŋ}{ng}
\newunicodechar{θ}{th}
\newunicodechar{ð}{dh}
\newunicodechar{ʃ}{sh}
\newunicodechar{ʒ}{zh}
\newunicodechar{ʧ}{ch}
\newunicodechar{ʤ}{j}
\newunicodechar{ɡ}{g}
\newunicodechar{ɹ}{r}
\newunicodechar{ɜ}{e}
\newunicodechar{ɒ}{o}

% ============================================
% 6. PAGE LAYOUT
% ============================================
\setlength{\parindent}{0pt}
\setlength{\columnsep}{1.5cm}
\setlength{\headheight}{40pt}

% ============================================
% 7. WATERMARK (WITH GUARD)
% ============================================
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
  \raisebox{0.15cm}{\textcolor{forumred}{\Large\bfseries\thepage}}%
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
      \node[text=forumred, font=\Large\bfseries] 
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
      \node[text=forumred, font=\Large\bfseries] 
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
\vspace{3.6cm}

\noindent
{\fontsize{14}{17}\sffamily\bfseries #3}

\vspace{12pt}
}

% ============================================
% 10. VOCABULARY ENTRY COMMANDS
% ============================================
% Full version with example
% Usage: \vocabentry{word}{pronunciation}{definition}{example}{translation}
\newcommand{\vocabentry}[5]{%
  \noindent
  {\sffamily\bfseries\color{forumred}\large #1}\\
  {\itshape #2}\\
  #3\\
  {\itshape\textbf{Example:} #4}\\
  {\itshape (#5)}
  
  \vspace{8pt}
}

% Short version without example
% Usage: \vocabshort{word}{pronunciation}{definition}
\newcommand{\vocabshort}[3]{%
  \noindent
  {\sffamily\bfseries\color{forumred}\large #1}\\
  {\itshape #2}\\
  #3
  
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
