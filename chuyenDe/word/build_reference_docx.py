#!/usr/bin/env python3
from __future__ import annotations

import datetime as _dt
import zipfile
from pathlib import Path


def _utc_now_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).replace(microsecond=0).isoformat()


def _content_types_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/word/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
  <Override PartName="/word/header2.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""


def _rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def _app_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex CLI</Application>
  <DocSecurity>0</DocSecurity>
  <ScaleCrop>false</ScaleCrop>
  <Company></Company>
  <LinksUpToDate>false</LinksUpToDate>
  <SharedDoc>false</SharedDoc>
  <HyperlinksChanged>false</HyperlinksChanged>
  <AppVersion>1.0</AppVersion>
</Properties>
"""


def _core_xml() -> str:
    created = _utc_now_iso()
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:dcmitype="http://purl.org/dc/dcmitype/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>IELTS Workshop - reference</dc:title>
  <dc:creator>The Forum Center</dc:creator>
  <cp:lastModifiedBy>Codex CLI</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{created}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{created}</dcterms:modified>
</cp:coreProperties>
"""


def _theme_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
  <a:themeElements>
    <a:clrScheme name="Office">
      <a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>
      <a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1F4E79"/></a:dk2>
      <a:lt2><a:srgbClr val="E52B20"/></a:lt2>
      <a:accent1><a:srgbClr val="E52B20"/></a:accent1>
      <a:accent2><a:srgbClr val="1F4E79"/></a:accent2>
      <a:accent3><a:srgbClr val="5AA244"/></a:accent3>
      <a:accent4><a:srgbClr val="7A1FA2"/></a:accent4>
      <a:accent5><a:srgbClr val="666666"/></a:accent5>
      <a:accent6><a:srgbClr val="999999"/></a:accent6>
      <a:hlink><a:srgbClr val="1F4E79"/></a:hlink>
      <a:folHlink><a:srgbClr val="7A1FA2"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Office">
      <a:majorFont>
        <a:latin typeface="Latin Modern Sans"/>
      </a:majorFont>
      <a:minorFont>
        <a:latin typeface="Georgia"/>
      </a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Office"/>
  </a:themeElements>
</a:theme>
"""


def _styles_xml() -> str:
    # Colors are taken from `chuyenDe/common/workshop-base.tex`.
    forumred = "E52B20"
    topicblue = "1F4E79"
    cuegreen = "5AA244"
    accentpurple = "7A1FA2"
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Georgia" w:hAnsi="Georgia" w:cs="Georgia"/>
        <w:sz w:val="24"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:after="120"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>

  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:rPr>
      <w:rFonts w:ascii="Georgia" w:hAnsi="Georgia" w:cs="Georgia"/>
      <w:sz w:val="24"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:uiPriority w:val="9"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
      <w:b/>
      <w:sz w:val="32"/>
      <w:color w:val="{forumred}"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:uiPriority w:val="9"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:before="200" w:after="100"/></w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
      <w:b/>
      <w:sz w:val="28"/>
      <w:color w:val="{topicblue}"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="CDCollectionTitle">
    <w:name w:val="CD Collection Title"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:jc w:val="center"/>
      <w:spacing w:before="120" w:after="160"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
      <w:b/>
      <w:sz w:val="24"/>
      <w:color w:val="{forumred}"/>
    </w:rPr>
  </w:style>

  <w:style w:type="character" w:styleId="CDRed">
    <w:name w:val="CD Red"/>
    <w:rPr><w:color w:val="{forumred}"/></w:rPr>
  </w:style>
  <w:style w:type="character" w:styleId="CDBlue">
    <w:name w:val="CD Blue"/>
    <w:rPr><w:color w:val="{topicblue}"/></w:rPr>
  </w:style>
  <w:style w:type="character" w:styleId="CDGreen">
    <w:name w:val="CD Green"/>
    <w:rPr><w:color w:val="{cuegreen}"/></w:rPr>
  </w:style>
  <w:style w:type="character" w:styleId="CDPurple">
    <w:name w:val="CD Purple"/>
    <w:rPr><w:color w:val="{accentpurple}"/></w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="CDPrompt">
    <w:name w:val="CD Prompt"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:before="120" w:after="160"/>
      <w:pBdr>
        <w:top w:val="single" w:sz="8" w:space="2" w:color="{forumred}"/>
        <w:left w:val="single" w:sz="8" w:space="2" w:color="{forumred}"/>
        <w:bottom w:val="single" w:sz="8" w:space="2" w:color="{forumred}"/>
        <w:right w:val="single" w:sz="8" w:space="2" w:color="{forumred}"/>
      </w:pBdr>
      <w:shd w:val="clear" w:color="auto" w:fill="FDECEC"/>
      <w:ind w:left="200" w:right="200"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
      <w:i/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="CDSection">
    <w:name w:val="CD Section"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:before="160" w:after="120"/>
      <w:pBdr>
        <w:left w:val="single" w:sz="24" w:space="2" w:color="{forumred}"/>
      </w:pBdr>
      <w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>
      <w:ind w:left="240"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
      <w:b/>
      <w:color w:val="{forumred}"/>
      <w:sz w:val="26"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="CDStep">
    <w:name w:val="CD Step"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:before="140" w:after="100"/>
      <w:pBdr>
        <w:left w:val="single" w:sz="24" w:space="2" w:color="{topicblue}"/>
      </w:pBdr>
      <w:shd w:val="clear" w:color="auto" w:fill="EAF2FB"/>
      <w:ind w:left="240"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
      <w:b/>
      <w:color w:val="{topicblue}"/>
      <w:sz w:val="24"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="CDGreenHeading">
    <w:name w:val="CD Green Heading"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:before="120" w:after="80"/>
      <w:pBdr>
        <w:left w:val="single" w:sz="24" w:space="2" w:color="{cuegreen}"/>
      </w:pBdr>
      <w:shd w:val="clear" w:color="auto" w:fill="F1F8EE"/>
      <w:ind w:left="240"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
      <w:b/>
      <w:color w:val="{cuegreen}"/>
      <w:sz w:val="24"/>
    </w:rPr>
  </w:style>

  <w:style w:type="paragraph" w:styleId="CDNote">
    <w:name w:val="CD Note"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:before="120" w:after="120"/>
      <w:pBdr>
        <w:left w:val="single" w:sz="24" w:space="2" w:color="{accentpurple}"/>
      </w:pBdr>
      <w:shd w:val="clear" w:color="auto" w:fill="F6F0FA"/>
      <w:ind w:left="240"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
      <w:b/>
      <w:color w:val="{accentpurple}"/>
      <w:sz w:val="24"/>
    </w:rPr>
  </w:style>

  <w:style w:type="table" w:styleId="CDVocabTable">
    <w:name w:val="CDVocabTable"/>
    <w:basedOn w:val="TableNormal"/>
    <w:tblPr>
      <w:tblW w:w="5000" w:type="pct"/>
      <w:tblBorders>
        <w:top w:val="single" w:sz="10" w:space="0" w:color="BFBFBF"/>
        <w:left w:val="single" w:sz="10" w:space="0" w:color="BFBFBF"/>
        <w:bottom w:val="single" w:sz="10" w:space="0" w:color="BFBFBF"/>
        <w:right w:val="single" w:sz="10" w:space="0" w:color="BFBFBF"/>
        <w:insideH w:val="single" w:sz="8" w:space="0" w:color="D0D0D0"/>
        <w:insideV w:val="single" w:sz="8" w:space="0" w:color="D0D0D0"/>
      </w:tblBorders>
      <w:tblCellMar>
        <w:top w:w="80" w:type="dxa"/>
        <w:left w:w="120" w:type="dxa"/>
        <w:bottom w:w="80" w:type="dxa"/>
        <w:right w:w="120" w:type="dxa"/>
      </w:tblCellMar>
    </w:tblPr>
    <w:tblStylePr w:type="firstRow">
      <w:tcPr>
        <w:shd w:val="clear" w:color="auto" w:fill="{topicblue}"/>
      </w:tcPr>
      <w:rPr>
        <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
        <w:b/>
        <w:color w:val="FFFFFF"/>
      </w:rPr>
    </w:tblStylePr>
  </w:style>
</w:styles>
"""


def _settings_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:zoom w:percent="100"/>
  <w:defaultTabStop w:val="720"/>
  <w:displayBackgroundShape/>
  <w:compat/>
</w:settings>
"""


def _document_xml() -> str:
    # Letter size, margins aligned with LaTeX geometry:
    # left/right ≈ 2cm = 1134 twips, top/bottom 0.
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="CDPrompt"/></w:pPr>
      <w:r><w:t>[Your Writing Prompt Here]</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="CDSection"/></w:pPr>
      <w:r><w:t>Phần I. Xác định tư duy</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="CDStep"/></w:pPr>
      <w:r><w:t>1. Bước 1: Xác định quan điểm</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>Viết nội dung ở đây…</w:t></w:r>
    </w:p>
    <w:sectPr>
      <w:headerReference w:type="default" r:id="rId1"/>
      <w:headerReference w:type="first" r:id="rId2"/>
      <w:footerReference w:type="first" r:id="rId3"/>
      <w:footerReference w:type="default" r:id="rId3"/>
      <w:titlePg/>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="0" w:right="1134" w:bottom="0" w:left="1134" w:header="0" w:footer="0" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>
"""


def _document_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header2.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
  <Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
</Relationships>
"""


def _watermark_shape_xml() -> str:
    # VML watermark technique (in header), using logoTF.png.
    return """<w:p>
  <w:r>
    <w:pict>
      <v:shapetype id="_x0000_t75" coordsize="21600,21600" o:spt="75" o:preferrelative="t"
                   path="m@4@5l@4@11@9@11@9@5xe" filled="t" stroked="f">
        <v:stroke joinstyle="miter"/>
        <v:formulas>
          <v:f eqn="if lineDrawn pixelLineWidth 0"/>
          <v:f eqn="sum @0 1 0"/>
          <v:f eqn="sum 0 0 @1"/>
          <v:f eqn="prod @2 1 2"/>
          <v:f eqn="prod @3 21600 pixelWidth"/>
          <v:f eqn="prod @3 21600 pixelHeight"/>
          <v:f eqn="sum @0 0 1"/>
          <v:f eqn="prod @6 1 2"/>
          <v:f eqn="prod @7 21600 pixelWidth"/>
          <v:f eqn="sum @8 21600 0"/>
          <v:f eqn="prod @7 21600 pixelHeight"/>
          <v:f eqn="sum @10 21600 0"/>
        </v:formulas>
        <v:path o:extrusionok="f" gradientshapeok="t" o:connecttype="rect"/>
        <o:lock v:ext="edit" aspectratio="t"/>
      </v:shapetype>
      <v:shape id="WatermarkLogo" o:spid="_x0000_s2049" type="#_x0000_t75"
               style="position:absolute;margin-left:0;margin-top:0;width:450pt;height:450pt;z-index:-251654144;
                      mso-position-horizontal:center;mso-position-horizontal-relative:page;
                      mso-position-vertical:center;mso-position-vertical-relative:page;
                      opacity:.03"
               o:allowincell="f" stroked="f">
        <v:fill opacity=".03" o:opacity2=".03"/>
        <v:imagedata r:id="rId1" o:title="logoTF" gain="19661f" blacklevel="22938f"/>
      </v:shape>
    </w:pict>
  </w:r>
</w:p>
"""


def _header_first_xml() -> str:
    # First page header: approximates LaTeX overlay header via table blocks.
    # HeaderHeight 2.55cm ≈ 1446 twips; WhiteGap 0.16cm ≈ 91; SubHeight 0.75cm ≈ 425.
    forumred = "E52B20"
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:v="urn:schemas-microsoft-com:vml"
       xmlns:o="urn:schemas-microsoft-com:office:office">
  <w:tbl>
    <w:tblPr>
      <w:tblW w:w="12240" w:type="dxa"/>
      <w:tblInd w:w="-1134" w:type="dxa"/>
      <w:tblLayout w:type="fixed"/>
      <w:tblBorders>
        <w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/>
        <w:insideH w:val="nil"/><w:insideV w:val="nil"/>
      </w:tblBorders>
    </w:tblPr>
    <w:tblGrid><w:gridCol w:w="12240"/></w:tblGrid>
    <w:tr>
      <w:trPr><w:trHeight w:val="1446" w:hRule="exact"/></w:trPr>
      <w:tc>
        <w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{forumred}"/></w:tcPr>
        <w:p>
          <w:pPr>
            <w:jc w:val="center"/>
            <w:spacing w:before="0" w:after="0"/>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Impact" w:hAnsi="Impact" w:cs="Impact"/>
              <w:color w:val="FFFFFF"/>
              <w:sz w:val="144"/>
              <w:b/>
            </w:rPr>
            <w:t>IELTS WORKSHOP</w:t>
          </w:r>
        </w:p>
      </w:tc>
    </w:tr>
    <w:tr>
      <w:trPr><w:trHeight w:val="91" w:hRule="exact"/></w:trPr>
      <w:tc><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="FFFFFF"/></w:tcPr><w:p/></w:tc>
    </w:tr>
    <w:tr>
      <w:trPr><w:trHeight w:val="425" w:hRule="exact"/></w:trPr>
      <w:tc>
        <w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{forumred}"/></w:tcPr>
        <w:tbl>
          <w:tblPr>
            <w:tblW w:w="12240" w:type="dxa"/>
            <w:tblLayout w:type="fixed"/>
            <w:tblBorders>
              <w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/>
              <w:insideH w:val="nil"/><w:insideV w:val="nil"/>
            </w:tblBorders>
          </w:tblPr>
          <w:tblGrid>
            <w:gridCol w:w="6120"/><w:gridCol w:w="6120"/>
          </w:tblGrid>
          <w:tr>
            <w:tc>
              <w:tcPr>
                <w:shd w:val="clear" w:color="auto" w:fill="{forumred}"/>
                <w:tcMar>
                  <w:left w:w="1134" w:type="dxa"/>
                  <w:right w:w="240" w:type="dxa"/>
                </w:tcMar>
              </w:tcPr>
              <w:p>
                <w:pPr><w:jc w:val="left"/></w:pPr>
                <w:r>
                  <w:rPr>
                    <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
                    <w:color w:val="FFFFFF"/><w:b/><w:sz w:val="20"/>
                  </w:rPr>
                  <w:t>THE FORUM CENTER - NGUYỄN HOÀNG HUY</w:t>
                </w:r>
              </w:p>
            </w:tc>
            <w:tc>
              <w:tcPr>
                <w:shd w:val="clear" w:color="auto" w:fill="{forumred}"/>
                <w:tcMar>
                  <w:left w:w="240" w:type="dxa"/>
                  <w:right w:w="1134" w:type="dxa"/>
                </w:tcMar>
              </w:tcPr>
              <w:p>
                <w:pPr><w:jc w:val="right"/></w:pPr>
                <w:r>
                  <w:rPr>
                    <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
                    <w:color w:val="FFFFFF"/><w:b/><w:sz w:val="20"/>
                  </w:rPr>
                  <w:t>{{DOCTYPE}}</w:t>
                </w:r>
              </w:p>
            </w:tc>
          </w:tr>
        </w:tbl>
      </w:tc>
    </w:tr>
  </w:tbl>
  {_watermark_shape_xml().rstrip()}
</w:hdr>
"""


def _header_default_xml() -> str:
    # Other pages header: approximate top red line + centered badge.
    forumred = "E52B20"
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
       xmlns:v="urn:schemas-microsoft-com:vml"
       xmlns:o="urn:schemas-microsoft-com:office:office">
  <w:tbl>
    <w:tblPr>
      <w:tblW w:w="12240" w:type="dxa"/>
      <w:tblInd w:w="-1134" w:type="dxa"/>
      <w:tblLayout w:type="fixed"/>
      <w:tblBorders>
        <w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/>
        <w:insideH w:val="nil"/><w:insideV w:val="nil"/>
      </w:tblBorders>
    </w:tblPr>
    <w:tblGrid><w:gridCol w:w="12240"/></w:tblGrid>
    <w:tr>
      <w:trPr><w:trHeight w:val="120" w:hRule="exact"/></w:trPr>
      <w:tc><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{forumred}"/></w:tcPr><w:p/></w:tc>
    </w:tr>
    <w:tr>
      <w:trPr><w:trHeight w:val="360" w:hRule="exact"/></w:trPr>
      <w:tc>
        <w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="FFFFFF"/></w:tcPr>
        <w:tbl>
          <w:tblPr>
            <w:tblW w:w="3000" w:type="dxa"/>
            <w:jc w:val="center"/>
            <w:tblBorders>
              <w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/>
              <w:insideH w:val="nil"/><w:insideV w:val="nil"/>
            </w:tblBorders>
          </w:tblPr>
          <w:tblGrid><w:gridCol w:w="3000"/></w:tblGrid>
          <w:tr>
            <w:tc>
              <w:tcPr>
                <w:shd w:val="clear" w:color="auto" w:fill="{forumred}"/>
                <w:tcMar>
                  <w:top w:w="80" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/>
                  <w:left w:w="120" w:type="dxa"/><w:right w:w="120" w:type="dxa"/>
                </w:tcMar>
              </w:tcPr>
              <w:p>
                <w:pPr><w:jc w:val="center"/></w:pPr>
                <w:r>
                  <w:rPr>
                    <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
                    <w:color w:val="FFFFFF"/><w:b/><w:sz w:val="20"/>
                  </w:rPr>
                  <w:t>Self-study IELTS Material</w:t>
                </w:r>
              </w:p>
            </w:tc>
          </w:tr>
        </w:tbl>
      </w:tc>
    </w:tr>
  </w:tbl>
  {_watermark_shape_xml().rstrip()}
</w:hdr>
"""


def _footer_default_xml() -> str:
    forumred = "E52B20"
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:tbl>
    <w:tblPr>
      <w:tblW w:w="12240" w:type="dxa"/>
      <w:tblInd w:w="-1134" w:type="dxa"/>
      <w:tblLayout w:type="fixed"/>
      <w:tblBorders>
        <w:top w:val="nil"/><w:left w:val="nil"/><w:bottom w:val="nil"/><w:right w:val="nil"/>
        <w:insideH w:val="nil"/><w:insideV w:val="nil"/>
      </w:tblBorders>
    </w:tblPr>
    <w:tblGrid><w:gridCol w:w="12240"/></w:tblGrid>
    <w:tr>
      <w:trPr><w:trHeight w:val="560" w:hRule="exact"/></w:trPr>
      <w:tc>
        <w:tcPr>
          <w:vAlign w:val="bottom"/>
          <w:shd w:val="clear" w:color="auto" w:fill="FFFFFF"/>
          <w:tcMar>
            <w:bottom w:w="240" w:type="dxa"/>
          </w:tcMar>
        </w:tcPr>
        <w:p>
          <w:pPr>
            <w:jc w:val="center"/>
            <w:spacing w:before="0" w:after="0"/>
          </w:pPr>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
              <w:color w:val="{forumred}"/><w:b/><w:sz w:val="28"/>
            </w:rPr>
            <w:fldChar w:fldCharType="begin"/>
          </w:r>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
              <w:color w:val="{forumred}"/><w:b/><w:sz w:val="28"/>
            </w:rPr>
            <w:instrText xml:space="preserve"> PAGE </w:instrText>
          </w:r>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
              <w:color w:val="{forumred}"/><w:b/><w:sz w:val="28"/>
            </w:rPr>
            <w:fldChar w:fldCharType="separate"/>
          </w:r>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
              <w:color w:val="{forumred}"/><w:b/><w:sz w:val="28"/>
            </w:rPr>
            <w:t>1</w:t>
          </w:r>
          <w:r>
            <w:rPr>
              <w:rFonts w:ascii="Latin Modern Sans" w:hAnsi="Latin Modern Sans" w:cs="Latin Modern Sans"/>
              <w:color w:val="{forumred}"/><w:b/><w:sz w:val="28"/>
            </w:rPr>
            <w:fldChar w:fldCharType="end"/>
          </w:r>
        </w:p>
      </w:tc>
    </w:tr>
    <w:tr>
      <w:trPr><w:trHeight w:val="100" w:hRule="exact"/></w:trPr>
      <w:tc><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{forumred}"/></w:tcPr><w:p/></w:tc>
    </w:tr>
  </w:tbl>
</w:ftr>
"""


def _header_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/logoTF.png"/>
</Relationships>
"""


def build_reference_docx(repo_root: Path, out_path: Path, *, doctype: str) -> None:
    logo_path = repo_root / "Vocab" / "wm" / "logoTF.png"
    if not logo_path.exists():
        raise SystemExit(f"Missing watermark image: {logo_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _content_types_xml())
        zf.writestr("_rels/.rels", _rels_xml())
        zf.writestr("docProps/app.xml", _app_xml())
        zf.writestr("docProps/core.xml", _core_xml())

        zf.writestr("word/document.xml", _document_xml())
        zf.writestr("word/_rels/document.xml.rels", _document_rels_xml())
        zf.writestr("word/styles.xml", _styles_xml())
        zf.writestr("word/settings.xml", _settings_xml())
        zf.writestr("word/theme/theme1.xml", _theme_xml())

        zf.writestr("word/header1.xml", _header_default_xml())
        zf.writestr("word/_rels/header1.xml.rels", _header_rels_xml())
        zf.writestr("word/header2.xml", _header_first_xml().replace("{DOCTYPE}", doctype))
        zf.writestr("word/_rels/header2.xml.rels", _header_rels_xml())
        zf.writestr("word/footer1.xml", _footer_default_xml())

        zf.writestr("word/media/logoTF.png", logo_path.read_bytes())


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    out_dir = repo_root / "chuyenDe" / "word"
    out_dir.mkdir(parents=True, exist_ok=True)

    writing = out_dir / "reference-writing.docx"
    reading = out_dir / "reference-reading.docx"
    legacy = out_dir / "reference.docx"

    build_reference_docx(
        repo_root=repo_root,
        out_path=writing,
        doctype="TÀI LIỆU CHUYÊN ĐỀ WRITING",
    )
    build_reference_docx(
        repo_root=repo_root,
        out_path=reading,
        doctype="TÀI LIỆU CHUYÊN ĐỀ READING",
    )
    build_reference_docx(
        repo_root=repo_root,
        out_path=legacy,
        doctype="TÀI LIỆU CHUYÊN ĐỀ WRITING",
    )
    print(f"Wrote {writing}")
    print(f"Wrote {reading}")
    print(f"Wrote {legacy}")


if __name__ == "__main__":
    main()
