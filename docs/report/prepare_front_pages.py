"""Copy the first three rendered source pages without editing their content."""
from pathlib import Path
import hashlib
import json
from pypdf import PdfReader, PdfWriter

root = Path(__file__).resolve().parent
source = root / 'source' / 'original-report.pdf'
target = root / 'source' / 'first-three-pages.pdf'
reader = PdfReader(source)
if len(reader.pages) < 3:
    raise SystemExit('The exported source must contain at least three pages.')
writer = PdfWriter()
for page in reader.pages[:3]:
    writer.add_page(page)
with target.open('wb') as stream:
    writer.write(stream)
record = {
    'source_pdf_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'original_docx_sha256': hashlib.sha256((root/'source'/'original-report.docx').read_bytes()).hexdigest(),
    'preserved_pages': [1, 2, 3],
    'page_sizes_points': [[float(p.mediabox.width), float(p.mediabox.height)] for p in reader.pages[:3]],
    'preservation_method': 'Copy source PDF page objects, then include with pdfpages and no overlays',
    'final_render_comparison_required': True,
}
(root/'source'/'preservation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(target)
