% ============================================
% FORECAST SPEAKING - PART 1 CLASS
% ============================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{forecastp1}[2026/01/19 v1.0 Forecast Speaking Part 1]

\LoadClass[12pt,a4paper]{article}

% ============================================
% PACKAGES
% ============================================
\RequirePackage[english,vietnamese]{babel}
\RequirePackage[a4paper,left=2cm,right=2cm,top=0cm,bottom=0cm,includehead,includefoot,headheight=50pt,footskip=1.5cm]{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{xcolor}
\RequirePackage{graphicx}
\RequirePackage{tikz}
\RequirePackage{eso-pic}
\RequirePackage{fontspec}
\usetikzlibrary{calc}

% ============================================
% FONTS
% ============================================
\newcommand{\forecast@fontroot}{}%
\IfFileExists{./@font/latin-modern-roman/lmroman10-regular.otf}{\renewcommand{\forecast@fontroot}{./@font}}{%
  \IfFileExists{../../@font/latin-modern-roman/lmroman10-regular.otf}{\renewcommand{\forecast@fontroot}{../../@font}}{%
    \IfFileExists{../../font/latin-modern-roman/lmroman10-regular.otf}{\renewcommand{\forecast@fontroot}{../../font}}{%
      \IfFileExists{./font/latin-modern-roman/lmroman10-regular.otf}{\renewcommand{\forecast@fontroot}{./font}}{}%
    }%
  }%
}%

\ifx\forecast@fontroot\empty
  \setmainfont{Latin Modern Roman}
  \setsansfont{Latin Modern Sans}
\else
  \setmainfont[
    Path=\forecast@fontroot/latin-modern-roman/,
    Extension=.otf,
    UprightFont=lmroman10-regular,
    BoldFont=lmroman10-bold,
    ItalicFont=lmroman10-italic,
    BoldItalicFont=lmroman10-bolditalic
  ]{Latin Modern Roman}
  \setsansfont[
    Path=\forecast@fontroot/Latin-Modern-Sans/,
    Extension=.otf,
    UprightFont=lmsans10-regular,
    BoldFont=lmsans10-bold,
    ItalicFont=lmsans10-oblique,
    BoldItalicFont=lmsans10-boldoblique
  ]{Latin Modern Sans}
\fi

\IfFileExists{\forecast@fontroot/UTM-Impact.ttf}{%
  \newfontfamily\impactfont{UTM-Impact.ttf}[Path=\forecast@fontroot/,Extension=.ttf,UprightFont=UTM-Impact]
}{%
  \IfFileExists{../../font/UTM-Impact.ttf}{%
    \newfontfamily\impactfont{UTM-Impact.ttf}[Path=../../font/,Extension=.ttf,UprightFont=UTM-Impact]
  }{%
    \newfontfamily\impactfont{UTM-Impact.ttf}[Path=./,Extension=.ttf,UprightFont=UTM-Impact]
  }%
}

% ============================================
% COLORS
% ============================================
\definecolor{forumred}{HTML}{E52B20}
\definecolor{topicblue}{HTML}{1F4E79}

% ============================================
% LAYOUT
% ============================================
\setlength{\parindent}{0pt}
\setlength{\headheight}{40pt}

% Page number styling
\newcommand{\forecast@pagenumfont}{\sffamily\bfseries\fontsize{14}{16}\selectfont}

% ============================================
% WATERMARK
% ============================================
\AtBeginDocument{%
  \pgfsetfillopacity{0.15}%
  \pgfsetstrokeopacity{0.15}%
  \pgfsetfillopacity{1}%
  \pgfsetstrokeopacity{1}%
}
\newcommand{\forecast@watermarkfile}{../../Vocab/wm/logoTF.png}
\IfFileExists{./templates/logoTF.png}{\renewcommand{\forecast@watermarkfile}{./templates/logoTF.png}}{}
\IfFileExists{./logoTF.png}{\renewcommand{\forecast@watermarkfile}{./logoTF.png}}{}
\IfFileExists{../wm/logoTF.png}{\renewcommand{\forecast@watermarkfile}{../wm/logoTF.png}}{}
\AddToShipoutPictureBG{%
  \begin{tikzpicture}[remember picture, overlay]
    \fill[white] (current page.south west) rectangle (current page.north east);
    \node[opacity=0.15] at (current page.center) {%
      \includegraphics[width=15cm]{\forecast@watermarkfile}%
    };
  \end{tikzpicture}%
}

% ============================================
% HEADER / FOOTER STYLES
% ============================================
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\raisebox{0.15cm}{\textcolor{forumred}{{\forecast@pagenumfont\thepage}}}}

\fancypagestyle{firstpage}{%
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  \fancyfoot[C]{%
    \begin{tikzpicture}[remember picture, overlay]
      \draw[forumred, line width=5pt] (current page.south west) -- (current page.south east);
      \node[text=forumred, font=\forecast@pagenumfont] at ([yshift=20pt]current page.south) {\thepage};
    \end{tikzpicture}%
  }%
}

\fancypagestyle{otherpages}{%
  \fancyhf{}
  \renewcommand{\headrulewidth}{0pt}
  \fancyhead[C]{%
    \begin{tikzpicture}[remember picture, overlay]
      \draw[forumred, line width=8pt] (current page.north west) -- (current page.north east);
      \def\w{5.4cm}
      \def\h{0.7cm}
      \def\r{9pt}
      \coordinate (badgeTopCenter) at ([yshift=-4pt]current page.north);
      \coordinate (A) at ($(badgeTopCenter)+(-\w/2,0)$);
      \path[fill=forumred]
        (A) -- ++(\w,0) -- ++(0,-\h+\r)
        arc[start angle=0,end angle=-90,radius=\r]
        -- ++(-\w+2*\r,0)
        arc[start angle=-90,end angle=-180,radius=\r]
        -- ++(0,\h-\r) -- cycle;
      \node[text=white, font=\sffamily\bfseries\fontsize{10}{12}\selectfont]
        at ($(badgeTopCenter)+(0,-\h/2)$) {Self-study IELTS Material};
    \end{tikzpicture}%
  }%
  \fancyfoot[C]{%
    \begin{tikzpicture}[remember picture, overlay]
      \draw[forumred, line width=5pt] (current page.south west) -- (current page.south east);
      \node[text=forumred, font=\forecast@pagenumfont] at ([yshift=20pt]current page.south) {\thepage};
    \end{tikzpicture}%
  }%
}

% ============================================
% FIRST PAGE HEADER
% ============================================
\newcommand{\forecast@centerheading}[1]{%
  {\centering\sffamily\bfseries\spaceskip=0.18em\relax #1\par}%
}
\newcommand{\makeforecastheader}[3]{%
  \begin{tikzpicture}[remember picture, overlay]
    \def\HeaderHeight{2.55cm}
    \def\WhiteGap{0.16cm}
    \def\SubHeight{0.75cm}

    \fill[forumred]
      (current page.north west) rectangle ([yshift=-\HeaderHeight]current page.north east);

    \node[
      text=white,
      font=\impactfont\fontsize{72}{78}\selectfont,
      anchor=south,
      inner sep=0pt
    ] at ([yshift=-\HeaderHeight-1pt]current page.north) {FORECAST SPEAKING};

    \fill[white]
      ([yshift=-\HeaderHeight]current page.north west) rectangle ([yshift=-\HeaderHeight-\WhiteGap]current page.north east);

    \fill[forumred]
      ([yshift=-\HeaderHeight-\WhiteGap]current page.north west)
      rectangle ([yshift=-\HeaderHeight-\WhiteGap-\SubHeight]current page.north east);

    \node[text=white, font=\sffamily\bfseries\small, anchor=west, text height=1.6ex, text depth=0.4ex]
      at ([xshift=2cm,yshift=-\HeaderHeight-\WhiteGap-\SubHeight/2] current page.north west) {#1};
    \node[text=white, font=\sffamily\bfseries\small, anchor=east, text height=1.6ex, text depth=0.4ex]
      at ([xshift=-2cm,yshift=-\HeaderHeight-\WhiteGap-\SubHeight/2] current page.north east) {#2};
  \end{tikzpicture}%

  \vspace{0.75cm}
  \forecast@centerheading{#3}
  \vspace{6pt}
}

% ============================================
% TOPIC / QA COMMANDS
% ============================================
\newif\ifforecast@firsttopic
\forecast@firsttopictrue

\newcommand{\forecasttopic}[1]{%
  \ifforecast@firsttopic
    \global\forecast@firsttopicfalse
  \else
    \clearpage
  \fi
  \begin{center}
    {\color{topicblue}\sffamily\bfseries #1}
  \end{center}
  \vspace{10pt}
}

\newcommand{\forecastqa}[2]{%
  \textbf{Question:} \textbf{#1}\par
  \vspace{4pt}
  \textbf{Sample Answer:} #2\par
  \vspace{12pt}
}

\endinput
