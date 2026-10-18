from __future__ import annotations

import html
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Preformatted, Flowable, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "NEXOS_Architecture_and_Build_Plan.md"
OUTPUT = ROOT / "output" / "pdf" / "NEXOS_Architecture_and_Build_Plan.pdf"
QA = ROOT / "tmp" / "pdfs"

FONTDIR = Path("C:/Windows/Fonts")
for name, filename in [("Calibri", "calibri.ttf"), ("Calibri-Bold", "calibrib.ttf"), ("Calibri-Italic", "calibrii.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONTDIR / filename)))
pdfmetrics.registerFontFamily("Calibri", normal="Calibri", bold="Calibri-Bold", italic="Calibri-Italic", boldItalic="Calibri-Bold")

INK = colors.HexColor("#172434")
BLUE = colors.HexColor("#214F70")
MUTED = colors.HexColor("#566677")
LIGHT = colors.HexColor("#F0F4F7")
LINE = colors.HexColor("#D5DDE4")
WHITE = colors.white
WIDTH = 174 * mm

STYLES = {
    "title": ParagraphStyle("Title", fontName="Calibri-Bold", fontSize=27, leading=32, textColor=INK, spaceAfter=18),
    "subtitle": ParagraphStyle("Subtitle", fontName="Calibri", fontSize=15, leading=20, textColor=BLUE, spaceAfter=16),
    "h1": ParagraphStyle("Heading1", fontName="Calibri-Bold", fontSize=19, leading=24, textColor=INK, spaceAfter=14, keepWithNext=True),
    "h2": ParagraphStyle("Heading2", fontName="Calibri-Bold", fontSize=11.8, leading=15, textColor=BLUE, spaceBefore=8, spaceAfter=6, keepWithNext=True),
    "body": ParagraphStyle("Body", fontName="Calibri", fontSize=10.5, leading=14.3, textColor=INK, spaceAfter=8),
    "list": ParagraphStyle("List", fontName="Calibri", fontSize=10.3, leading=13.8, textColor=INK, leftIndent=12, firstLineIndent=-10, spaceAfter=5),
    "cell": ParagraphStyle("Cell", fontName="Calibri", fontSize=9.3, leading=12.2, textColor=INK, spaceAfter=0),
    "th": ParagraphStyle("TableHeader", fontName="Calibri-Bold", fontSize=9.4, leading=12, textColor=WHITE),
    "code": ParagraphStyle("Code", fontName="Courier", fontSize=8.2, leading=10.6, textColor=INK, backColor=LIGHT, borderPadding=9, spaceBefore=4, spaceAfter=10),
    "caption": ParagraphStyle("Caption", fontName="Calibri-Italic", fontSize=9, leading=12, textColor=MUTED, spaceAfter=10),
    "refs": ParagraphStyle("References", fontName="Calibri", fontSize=9.1, leading=12.2, textColor=INK, spaceAfter=5),
}


def inline(text):
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" size="9">\1</font>', text)
    text = text.replace("→", " &gt; ").replace("·", " | ")
    text = re.sub(r"(https://[^\s<]+)", r'<link href="\1" color="#214F70">\1</link>', text)
    return text


class Architecture(Flowable):
    def __init__(self, deployment=False):
        Flowable.__init__(self)
        self.width = WIDTH
        self.height = 266 if deployment else 286
        self.deployment = deployment

    def draw(self):
        c = self.canv
        w = self.width

        def box(x, y, width, height, title, detail="", fill=LIGHT):
            c.setFillColor(fill)
            c.setStrokeColor(LINE)
            c.roundRect(x, y, width, height, 4, fill=1, stroke=1)
            c.setFillColor(INK)
            c.setFont("Calibri-Bold", 10.5)
            c.drawCentredString(x + width/2, y + height - 17, title)
            if detail:
                c.setFont("Calibri", 8.6)
                for i, t in enumerate(detail.split("\n")):
                    c.drawCentredString(x + width/2, y + height - 30 - i * 10, t)

        def arrow(x1, y1, x2, y2):
            c.setStrokeColor(BLUE)
            c.setLineWidth(1)
            c.line(x1, y1, x2, y2)
            if y2 < y1:
                c.line(x2, y2, x2 - 3, y2 + 5)
                c.line(x2, y2, x2 + 3, y2 + 5)
            elif x2 > x1:
                c.line(x2, y2, x2 - 5, y2 - 3)
                c.line(x2, y2, x2 - 5, y2 + 3)

        if not self.deployment:
            mainw = w * .69
            rightx = mainw + 14
            rw = w - rightx
            box(0, 238, mainw, 42, "Desktop panel and CLI", "Request, previews, progress and evidence")
            box(0, 183, mainw, 42, "Intent parser and planner", "Schema checked dependency graph")
            box(0, 128, mainw, 42, "Durable scheduler and agent roles", "Bounded concurrency, locks and checkpoints")
            box(0, 73, mainw, 42, "Permission broker", "Capabilities, action digest and sandbox selection", colors.HexColor("#E2EDF4"))
            box(0, 18, mainw, 42, "Registered tools and adapters", "Linux files and services | External connectors")
            for y in [238, 183, 128, 73]:
                arrow(mainw/2, y, mainw/2, y-13)
            box(rightx, 210, rw, 65, "Model gateway", "One local model\nor consented cloud\nNo tool authority")
            box(rightx, 120, rw, 65, "Task state and memory", "SQLite and retrieval\nProvenance and expiry\nNo permission grants")
            box(rightx, 22, rw, 75, "Verifier and audit", "Observed postconditions\nEvidence and history\nSuccess only after checks")
            arrow(mainw, 215, rightx, 215)
            arrow(mainw, 149, rightx, 149)
            arrow(mainw, 39, rightx, 39)
            c.setFont("Calibri-Italic", 8.5)
            c.setFillColor(MUTED)
            c.drawString(0, 2, "Solid arrows show principal calls; verification feeds durable task state and the UI.")
        else:
            box(0, 204, w, 50, "User session on Ubuntu 24.04 LTS", "Desktop launcher, notifications and local authenticated panel")
            box(0, 125, w*.55, 60, "NEXOS control service", "systemd user unit | Local API\nScheduler, broker and SQLite")
            box(w*.59, 125, w*.41, 60, "Inference gateway", "Local runtime or cloud\nMinimal permitted context")
            arrow(w*.27, 204, w*.27, 185)
            arrow(w*.55, 155, w*.59, 155)
            box(0, 37, w*.55, 66, "Sandboxed local workers", "Scoped files, no secrets\nNetwork denied and resource capped\nNo unrestricted host shell")
            box(w*.59, 37, w*.41, 66, "Deterministic connectors", "Credential handle from keyring\nApproved remote operations\nReconcile before retry")
            arrow(w*.27, 125, w*.27, 103)
            arrow(w*.55, 135, w*.79, 103)
            c.setFillColor(MUTED)
            c.setFont("Calibri-Italic", 8.5)
            c.drawString(0, 17, "Separate worker and connector capabilities; normal assistant runtime has no root authority.")


def make_table(lines):
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    rows = [rows[0]] + rows[2:]
    n = len(rows[0])
    widths = [WIDTH*.32, WIDTH*.68] if n == 2 else [WIDTH/n]*n
    cells = [[Paragraph(inline(cell), STYLES["th"] if i == 0 else STYLES["cell"]) for cell in row] for i, row in enumerate(rows)]
    t = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
        ("GRID", (0, 0), (-1, -1), .4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return [t, Spacer(1, 10)]


def parse_page(text, first=False):
    lines = text.strip().splitlines()
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("```"):
            is_mermaid = line.startswith("```mermaid")
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            if is_mermaid:
                result.append(Architecture(deployment=any("subgraph HOST" in item for item in buf)))
                result.append(Spacer(1, 8))
            else:
                result.append(Preformatted("\n".join(buf), STYLES["code"]))
            i += 1
            continue
        if line.startswith("|"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                buf.append(lines[i]); i += 1
            result.extend(make_table(buf))
            continue
        if line.startswith("# "):
            if first:
                result.append(Spacer(1, 26))
            result.append(Paragraph(inline(line[2:]), STYLES["title"] if first else STYLES["h1"]))
        elif line.startswith("## "):
            result.append(Paragraph(inline(line[3:]), STYLES["subtitle"] if first and i < 5 else STYLES["h2"]))
        elif re.match(r"^\d+\. ", line) or line.startswith("- "):
            result.append(Paragraph(inline(line), STYLES["refs"] if re.match(r"^- \*\*[RS]\d+", line) else STYLES["list"]))
        else:
            paragraph = [line]
            while i+1 < len(lines) and lines[i+1].strip() and not re.match(r"^(#|\||```|\[\[|\d+\. |- )", lines[i+1].strip()):
                i += 1; paragraph.append(lines[i].strip())
            result.append(Paragraph(inline(" ".join(paragraph)), STYLES["body"]))
        i += 1
    return result


class Doc(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in ["Heading1", "Title"]:
            key = f"section-{len(self.section_pages)}"
            title = flowable.getPlainText()
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key, level=0)
            self.section_pages.append({"title": title, "page": self.page})


def page_chrome(c, d):
    w, h = d.pagesize
    c.saveState()
    c.setFillColor(MUTED)
    c.setFont("Calibri", 8.3)
    if d.page > 1:
        c.drawString(18*mm, h-13*mm, "NEXOS   Architecture and Build Plan")
    c.drawString(18*mm, 12*mm, "Version 1.0  |  18 October 2026")
    c.drawRightString(w-18*mm, 12*mm, str(d.page))
    c.restoreState()


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    pages = SOURCE.read_text(encoding="utf-8").split("\n---\n")
    story = []
    for i, page in enumerate(pages):
        if i:
            story.append(PageBreak())
        story.extend(parse_page(page, first=i == 0))
    doc = Doc(str(OUTPUT), pagesize=(210*mm, 297*mm), rightMargin=18*mm, leftMargin=18*mm,
              topMargin=23*mm, bottomMargin=22*mm, title="NEXOS Architecture and Build Plan",
              author="NEXOS Project", subject="Linux agentic workstation architecture and implementation plan")
    doc.section_pages = []
    doc.build(story, onFirstPage=page_chrome, onLaterPages=page_chrome)
    (QA / "section_pages.json").write_text(json.dumps(doc.section_pages, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "sections": len(pages), "headings": doc.section_pages}, indent=2))


if __name__ == "__main__":
    main()
