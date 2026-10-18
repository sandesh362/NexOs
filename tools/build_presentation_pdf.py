"""Build printable presentation notes from the repository Markdown script."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/presentation/NEXOS_Presentation_Script.md"
OUTPUT = ROOT / "output/pdf/NEXOS_Presentation_Script.pdf"


def main():
    # Use installed platform fonts without bundling their source files.
    font_root = Path("C:/Windows/Fonts")
    if not font_root.exists():
        raise SystemExit("This authoring helper currently expects the Windows Calibri font set")
    for family, filename in [("NexosText", "calibri.ttf"), ("NexosBold", "calibrib.ttf")]:
        pdfmetrics.registerFont(TTFont(family, str(font_root / filename)))
    pdfmetrics.registerFontFamily("NexosText", normal="NexosText", bold="NexosBold", italic="NexosText", boldItalic="NexosBold")
    ink = colors.HexColor("#172D40")
    blue = colors.HexColor("#245979")
    muted = colors.HexColor("#536A7B")
    styles = {
        "title": ParagraphStyle("Title", fontName="NexosBold", fontSize=27, leading=32, textColor=ink, spaceAfter=17),
        "h1": ParagraphStyle("Heading1", fontName="NexosBold", fontSize=21, leading=26, textColor=ink, spaceAfter=13, keepWithNext=True),
        "h2": ParagraphStyle("Heading2", fontName="NexosBold", fontSize=13.5, leading=18, textColor=blue, spaceBefore=10, spaceAfter=7, keepWithNext=True),
        "body": ParagraphStyle("Body", fontName="NexosText", fontSize=11.1, leading=15.4, textColor=ink, spaceAfter=9, allowWidows=0, allowOrphans=0),
        "list": ParagraphStyle("List", fontName="NexosText", fontSize=10.7, leading=14.6, textColor=ink, spaceAfter=7, leftIndent=12, firstLineIndent=-10),
        "cell": ParagraphStyle("Cell", fontName="NexosText", fontSize=9.3, leading=12.4, textColor=ink),
        "th": ParagraphStyle("TableHeader", fontName="NexosBold", fontSize=9.5, leading=12.6, textColor=colors.white),
    }

    def inline(value):
        value = html.escape(value)
        value = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<link href="\2" color="#245979">\1</link>', value)
        value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
        return value

    class Document(SimpleDocTemplate):
        def afterFlowable(self, item):
            if isinstance(item, Paragraph) and item.style.name in {"Title", "Heading1"}:
                key = f"section-{len(self.sections)}"
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(item.getPlainText(), key, 0)
                self.sections.append({"title": item.getPlainText(), "page": self.page})

    def chrome(canvas, doc):
        canvas.saveState()
        canvas.setFont("NexosText", 8.4)
        canvas.setFillColor(muted)
        if doc.page > 1:
            canvas.drawString(19*mm, 284*mm, "NEXOS   Presentation script and discussion notes")
        canvas.drawString(19*mm, 12*mm, "Presentation 20 October 2026")
        canvas.drawRightString(191*mm, 12*mm, str(doc.page))
        canvas.restoreState()

    story = []
    chunks = SOURCE.read_text(encoding="utf-8").split("\n---\n")
    width = 172 * mm
    for chunk_number, chunk in enumerate(chunks):
        if chunk_number:
            story.append(PageBreak())
        else:
            story.append(Spacer(1, 25))
        lines = chunk.strip().splitlines()
        index = 0
        while index < len(lines):
            current = lines[index].strip()
            if not current:
                index += 1
                continue
            if current.startswith("|"):
                rows = []
                while index < len(lines) and lines[index].strip().startswith("|"):
                    rows.append([item.strip() for item in lines[index].strip().strip("|").split("|")])
                    index += 1
                rows = [rows[0]] + rows[2:]
                cells = [[Paragraph(inline(item), styles["th"] if r == 0 else styles["cell"]) for item in row] for r, row in enumerate(rows)]
                table = Table(cells, colWidths=[width*.32, width*.34, width*.34], repeatRows=1)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), blue),
                    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F0F4F7")]),
                    ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#D2DCE5")),
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("LEFTPADDING", (0,0), (-1,-1), 7),
                    ("RIGHTPADDING", (0,0), (-1,-1), 7),
                    ("TOPPADDING", (0,0), (-1,-1), 8),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ]))
                story.extend([table, Spacer(1, 11)])
                continue
            if current.startswith("# "):
                style = "title" if chunk_number == 0 else "h1"
                story.append(Paragraph(inline(current[2:]), styles[style]))
            elif current.startswith("## "):
                story.append(Paragraph(inline(current[3:]), styles["h2"]))
            elif current.startswith("- "):
                story.append(Paragraph(inline(current), styles["list"]))
            else:
                paragraph = [current]
                while index+1 < len(lines) and lines[index+1].strip() and not lines[index+1].startswith(("#", "- ", "|")):
                    index += 1
                    paragraph.append(lines[index].strip())
                story.append(Paragraph(inline(" ".join(paragraph)), styles["body"]))
            index += 1
        if chunk_number == 0:
            story.append(Spacer(1, 15))
            story.append(Image(str(ROOT / "docs/assets/nexos-overview.png"), width=width, height=width*740/1600))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = Document(str(OUTPUT), pagesize=(210*mm,297*mm), leftMargin=19*mm, rightMargin=19*mm,
                        topMargin=23*mm, bottomMargin=22*mm, title="NEXOS Presentation Script",
                        author="NEXOS Project", subject="Proposal speech and literature review for 20 October 2026")
    document.sections = []
    document.build(story, onFirstPage=chrome, onLaterPages=chrome)
    print(json.dumps({"output": str(OUTPUT), "sections": document.sections}, indent=2))


if __name__ == "__main__":
    main()
