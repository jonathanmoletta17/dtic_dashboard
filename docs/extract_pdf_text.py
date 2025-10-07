import sys
from PyPDF2 import PdfReader
from pathlib import Path
p = Path(r"docs/Reescrever texto para prompt.pdf")
reader = PdfReader(str(p))
text_parts = []
for i, page in enumerate(reader.pages):
    try:
        t = page.extract_text() or ""
    except Exception:
        t = ""
    text_parts.append(f"\n--- Page {i+1} ---\n{t}")
out = Path(r"docs/Reescrever_texto_para_prompt.txt")
out.write_text("".join(text_parts), encoding="utf-8")
print(f"Wrote {out} with {len(text_parts)} pages.")
