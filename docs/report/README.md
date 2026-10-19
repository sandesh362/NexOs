# NEXOS professional project report

This project contains the expanded LaTeX report and its figures. The original Word
document is retained without modification in `source/original-report.docx`.

**Build status:** the full report source is authored. The final PDF has not yet
been compiled or visually qualified. Export of the original Word pages was
blocked because the automatic approval review service reported model capacity
failure. The built-in LaTeX compiler also failed to start because of a Windows
sandbox configuration error. These are environment failures, not report results.

## Contents

- Declaration, acknowledgements, abstract and abbreviations.
- Automatically generated contents, figure list and table list.
- Twelve chapters covering introduction, literature, requirements, architecture,
  execution, security, data, interface, implementation, ISO delivery, evaluation
  and roadmap.
- Eighteen numbered primary research and official documentation references.
- Four appendices covering interface contracts, sandbox requirements, evaluation
  fixtures, release criteria and traceability.
- Ten figures: four retained project diagrams, four native TikZ diagrams and two
  original UI concepts. UI concepts are explicitly labelled as proposed screens.

## Typography and page system

The rewritten body uses A4 paper, a 32 mm binding margin, 25 mm remaining margins,
12 pt Times-style text and mathematics through `newtx`, 1.5 body spacing, numbered
chapters, linked references and automatic page labels. It is an academic project
report with IEEE-style numbered references, rather than a two-column IEEE
conference submission.

The first three pages are inserted from the original Word PDF export with no
headers, footers or text overlays added. Their original page dimensions are
preserved even if different from the new A4 body. They must not be retyped or
reformatted. The final rendering must be compared with the exported originals.

The original cover/certificate contain institutional wording that may need team
review, including inconsistent degree wording. The report generation workflow
does not correct those protected pages.

## Finish the build

1. Export the original DOCX using Word without saving changes to it. On Windows,
   `export_original_pages.ps1` creates `source/original-report.pdf` read-only.
   Alternatively, save a PDF from Word to that exact path without editing the DOCX.
2. Run `python prepare_front_pages.py` with `pypdf` available. This copies pages
   1–3 into `source/first-three-pages.pdf` and writes a preservation manifest.
3. Use a working TeX Live, MiKTeX or Tectonic environment. From this directory,
   run `pdflatex -interaction=nonstopmode -halt-on-error main.tex` three times,
   or use `build.ps1`. Tectonic is supported through `build.ps1 -Engine tectonic`.
4. Inspect the compiler log for missing references, missing assets and overfull
   boxes. Render every final page and inspect text, tables, captions and margins.
5. Compare the first three rendered pages against the original PDF export. Only
   after these checks should the final PDF be described as submission ready.

The main document deliberately fails when `first-three-pages.pdf` is missing;
it never replaces the protected pages with a generated approximation.

## Content and evidence rules

The architecture follows the current project README and decision record: Ubuntu
24.04 LTS, native Qt interface, Python user daemon, Ollama, controlled adapters,
SQLite and required ISO delivery. The first implementation is a deterministic
static diagnosis CLI. Model planning, Linux worker isolation, native desktop and
the release ISO remain planned. Unit tests are not represented as end-to-end agent
accuracy or proof of complete security. No publication or award is fabricated.

No PDF from another generator is substituted for the requested LaTeX output.
