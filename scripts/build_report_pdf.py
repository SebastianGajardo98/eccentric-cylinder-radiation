"""Render the written report, docs/REPORT.md, as a typeset PDF.

Equations are typeset with KaTeX and figures are embedded; headless Chrome or
Edge prints the page to docs/REPORT.pdf. Needs Chrome or Edge (or the CHROME
environment variable) and an internet connection for the KaTeX files.

Usage: python scripts/build_report_pdf.py
"""

import html
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import markdown
from pypdf import PdfReader, PdfWriter

from assignment_content import TITLE
from study_data import ROOT, text_hash

SOURCE = ROOT / "docs" / "REPORT.md"
OUTPUT = ROOT / "docs" / "REPORT.pdf"
KATEX = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist"
DISPLAY_MATH = re.compile(r"^\$\$\n(.+?)\n\$\$$", re.S | re.M)
INLINE_MATH = re.compile(r"(?<!\$)\$(?!\$)([^$\n]+?)\$")

STYLE = """
@page { size: A4; margin: 20mm 19mm 22mm;
  @bottom-center { content: counter(page) " / " counter(pages); font: 9pt Cambria, Georgia, serif; color: #57534e; } }
body { font-family: Cambria, Georgia, "Times New Roman", serif; font-size: 10.5pt; line-height: 1.45; color: #1c1917; }
h1 { font-size: 19pt; line-height: 1.2; margin: 0 0 .4em; }
h2 { font-size: 14.5pt; margin: 1.6em 0 .5em; padding-bottom: .15em; border-bottom: 1px solid #d6d3d1; break-after: avoid; }
h3 { font-size: 12pt; margin: 1.3em 0 .4em; break-after: avoid; }
h4 { font-size: 10.5pt; margin: 1.1em 0 .3em; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: .7em 0; font-size: 8.8pt; line-height: 1.3; break-inside: avoid; }
th, td { border: 1px solid #d6d3d1; padding: 3px 6px; vertical-align: top; }
th { background: #f5f5f4; }
img { display: block; max-width: 100%; margin: .7em auto; break-inside: avoid; }
pre { background: #f5f5f4; padding: 6px 9px; font-size: 8.5pt; white-space: pre-wrap; break-inside: avoid; }
code { font-family: Consolas, "Courier New", monospace; font-size: 88%; }
blockquote { margin: .6em 0; padding: .2em .9em; border-left: 3px solid #b45309; background: #fafaf9; }
a { color: #1d4ed8; text-decoration: none; }
.math-display { margin: .6em 0; break-inside: avoid; }
.katex { font-size: 1.05em; }
"""

SCRIPT = """
document.querySelectorAll(".math").forEach(element => {
  katex.render(element.textContent, element, {displayMode: element.classList.contains("math-display"), throwOnError: false});
});
"""


def report_html():
    """Convert the Markdown report to HTML, keeping the TeX away from Markdown."""
    text = SOURCE.read_text(encoding="utf-8")
    formulas = []

    def keep(match, display):
        formulas.append((match.group(1), display))
        return f"MATHPLACEHOLDER{len(formulas)-1}END"

    text = DISPLAY_MATH.sub(lambda m: keep(m, True), text)
    text = INLINE_MATH.sub(lambda m: keep(m, False), text)
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    for index, (tex, display) in enumerate(formulas):
        token = f"MATHPLACEHOLDER{index}END"
        if display:
            body = body.replace(f"<p>{token}</p>", f'<div class="math math-display">{html.escape(tex)}</div>')
        else:
            body = body.replace(token, f'<span class="math">{html.escape(tex)}</span>')
    assert "MATHPLACEHOLDER" not in body, "A formula was not restored after the Markdown conversion."
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(TITLE)}</title>
<base href="{(ROOT / 'docs').as_uri()}/">
<link rel="stylesheet" href="{KATEX}/katex.min.css">
<script src="{KATEX}/katex.min.js"></script>
<style>{STYLE}</style></head>
<body>{body}<script>{SCRIPT}</script></body></html>"""
    return page, len(formulas)


def find_browser():
    candidates = [os.environ.get("CHROME"),
                  r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                  r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  *(shutil.which(name) for name in ("google-chrome", "chromium", "chromium-browser", "msedge"))]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise FileNotFoundError("Install Chrome or Edge, or set CHROME to a Chromium-based browser, to build the PDF report.")


def run_browser(browser, profile, *arguments):
    # A separate profile keeps the headless run away from any open browser window.
    command = [browser, "--headless", "--disable-gpu", "--no-first-run", f"--user-data-dir={profile}",
               "--virtual-time-budget=30000", *arguments]
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=180, check=True).stdout


def main():
    # Chrome's PDF trailer prompts a harmless pypdf repair notice.
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    page, formula_count = report_html()
    browser = find_browser()
    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / "report.html"
        source.write_text(page, encoding="utf-8")
        printed = Path(work) / "report.pdf"
        dom = run_browser(browser, Path(work) / "profile", "--dump-dom", source.as_uri())
        rendered = dom.count('class="katex"')
        if rendered != formula_count or "katex-error" in dom:
            raise RuntimeError(f"Typeset {rendered} of {formula_count} formulas; check the KaTeX download and the TeX in REPORT.md.")
        run_browser(browser, Path(work) / "profile", "--no-pdf-header-footer", f"--print-to-pdf={printed}", source.as_uri())
        writer = PdfWriter(clone_from=PdfReader(printed))
    # Replacing the metadata drops the print timestamps, so an unchanged report rebuilds byte for byte.
    writer.metadata = {"/Title": TITLE, "/Author": "Sebastian Alberto Gajardo Lobos",
                       "/Subject": "Heat and Mass Transfer (Radiative Heat Transfer)",
                       "/ReportSourceSHA256": text_hash(SOURCE)}
    with OUTPUT.open("wb") as stream:
        writer.write(stream)
    print(f"Written report PDF: {OUTPUT} ({len(writer.pages)} pages, {formula_count} formulas)", flush=True)


if __name__ == "__main__":
    main()
