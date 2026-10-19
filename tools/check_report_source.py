"""Check local references and structural consistency before TeX compilation."""
import hashlib
import json
import re
from pathlib import Path
from collections import Counter

root = Path(__file__).resolve().parents[1]
report = root/'docs'/'report'
files = sorted(report.rglob('*.tex'))
texts = {p:p.read_text(encoding='utf-8') for p in files}
all_text = '\n'.join(texts.values())
errors=[]
for path,text in texts.items():
    stack=[]
    for match in re.finditer(r'\\(begin|end)\{([^}]+)\}',text):
        op,env=match.groups()
        if op=='begin': stack.append(env)
        elif not stack or stack.pop()!=env: errors.append(f'{path.name}: unbalanced environment {env}')
    if stack: errors.append(f'{path.name}: unclosed environments {stack}')
    for name in re.findall(r'\\input\{([^}]+)\}',text):
        if not (report/(name+'.tex')).exists(): errors.append('Missing input '+name)
    for name in re.findall(r'\\reportfigure\{([^}]+)\}',text):
        if not (report/'images'/name).exists(): errors.append('Missing image '+name)
    if '\ufffd' in text: errors.append(f'{path.name}: replacement character')
labels = re.findall(r'\\label\{([^}]+)\}',all_text)
labels += re.findall(r'\\reportfigure\{[^}]+\}\{[^}]+\}\{[^}]+\}\{([^}]+)\}',all_text)
for label,count in Counter(labels).items():
    if count>1: errors.append('Duplicate label '+label)
for ref in re.findall(r'\\ref\{([^}]+)\}',all_text):
    if ref not in labels: errors.append('Missing label '+ref)
bib = re.findall(r'\\bibitem\{([^}]+)\}',all_text)
for group in re.findall(r'\\cite\{([^}]+)\}',all_text):
    for cite in group.split(','):
        if cite not in bib: errors.append('Missing citation '+cite)
src=report/'source'/'original-report.docx'
original=Path('C:/Users/userc/Downloads/NEXOS Report.docx')
same=hashlib.sha256(src.read_bytes()).digest()==hashlib.sha256(original.read_bytes()).digest()
if not same: errors.append('Retained original differs from supplied file')
result={
    'tex_files':len(files),
    'main_chapters':sum(len(re.findall(r'\\chapter\{',t)) for p,t in texts.items() if re.match(r'\d\d-',p.name)),
    'appendix_chapters':texts[report/'chapters'/'appendices.tex'].count('\\chapter{'),
    'references':len(bib),
    'figures':all_text.count('\\begin{tikzpicture}')+sum(t.count('\\reportfigure{') for p,t in texts.items() if p.name!='main.tex'),
    'retained_docx_byte_identical':same,
    'first_three_pages_exported':(report/'source'/'first-three-pages.pdf').exists(),
    'compiled_pdf_exists':(report/'main.pdf').exists(),
    'approximate_source_word_count':len(re.findall(r'\b[A-Za-z][A-Za-z-]*\b',all_text)),
    'errors':errors,
    'note':'Structural checks are not a TeX compile or rendered page review.'
}
(report/'source-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
raise SystemExit(bool(errors))
