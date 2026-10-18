import json
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageOps, ImageDraw, ImageFont
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output/pdf/NEXOS_Architecture_and_Build_Plan.pdf"
OUT = ROOT / "tmp/pdfs/rendered"
OUT.mkdir(parents=True, exist_ok=True)

reader = PdfReader(PDF)
doc = pdfium.PdfDocument(PDF)
texts = []
for i in range(len(doc)):
    page = doc[i]
    image = page.render(scale=1.5).to_pil().convert("RGB")
    image.save(OUT / f"page-{i+1:02}.png")
    texts.append(reader.pages[i].extract_text())
    page.close()
doc.close()

font = ImageFont.truetype("C:/Windows/Fonts/calibrib.ttf", 19)
for start in range(0, len(texts), 6):
    thumbnails = []
    for i in range(start, min(start+6, len(texts))):
        im = Image.open(OUT / f"page-{i+1:02}.png")
        im.thumbnail((420, 594))
        tile = Image.new("RGB", (440, 634), "#e5e9ed")
        tile.paste(im, ((440-im.width)//2, 30))
        ImageDraw.Draw(tile).text((12, 6), f"Page {i+1}", font=font, fill="black")
        thumbnails.append(tile)
    sheet = Image.new("RGB", (1320, 1268), "#e5e9ed")
    for i, tile in enumerate(thumbnails):
        sheet.paste(tile, ((i%3)*440, (i//3)*634))
    sheet.save(OUT / f"contact-{start//6+1}.png")

reference = pdfium.PdfDocument("C:/Users/userc/Downloads/NEXOS_Major_Project_Professional_Revised.pdf")
for number in [4, 11]:
    page = reference[number-1]
    page.render(scale=1.3).to_pil().save(OUT / f"source-page-{number}.png")
    page.close()
reference.close()

all_text = "\n".join(texts)
required = ["60 GB", "16 GB", "RTX 3050", "Permission broker", "Google Meet", "90%", "References and source traceability"]
results = {
    "page_count": len(texts),
    "all_pages_nonempty": all(len(t.strip()) > 200 for t in texts),
    "required_phrases": {term: term in all_text for term in required},
    "replacement_characters": all_text.count("\ufffd"),
    "pdf_bytes": PDF.stat().st_size,
    "source_words": len((ROOT / "docs/NEXOS_Architecture_and_Build_Plan.md").read_text(encoding="utf-8").split()),
    "section_pages": json.loads((ROOT / "tmp/pdfs/section_pages.json").read_text()),
}
(ROOT / "tmp/pdfs/verification.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps({k:v for k,v in results.items() if k != "section_pages"}, indent=2))
