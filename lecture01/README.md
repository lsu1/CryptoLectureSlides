# Lecture 01: Classical Ciphers

74-slide widescreen PDF for a three-hour introductory lecture, including two ten-minute breaks. Intended for master's students with a computer science or engineering background and little prior cryptography.

## Deliverables

- `Lecture01_Classical_Ciphers.pdf`: lecture slides, worked examples, exercises, and answers.
- `Lecture01_Instructor_Guide.pdf`: five-page pacing and delivery guide.
- `worked_examples.json`: complete substitution and Vigenère datasets, IC calculations, and key definitions.
- `slide_manifest.json`: structured slide content.

The scope retains shift, monoalphabetic substitution, Vigenère, Playfair, and block transposition. No additional cipher algorithm is developed. All graphics are generated as vector shapes and text. DejaVu fonts are embedded. The modern security scenario is illustrative, not a news claim.

## Rebuild

Requires Python 3, ReportLab, and the DejaVu Sans font files at `/usr/share/fonts/truetype/dejavu/`. The build scripts are authoritative; `slide_manifest.json` is generated rather than read as an input.

Run in the directory containing these files:

```sh
python build_lecture.py
python build_guide.py
```

The lecture build asserts example results, round trips, key recovery, selected statistical values, and layout constraints. After edits, inspect the rendered pages as well. PDF rendering and quality inspection in this delivery used PyMuPDF and Pillow; they are not required to build the PDFs.

## Reference

Based on the supplied `Lecture02_Classical_Ciphers.pdf`, Wu Hongjun, 79 pages. The original is not redistributed in this bundle. Bibliographic references are on the final slide. The instructor guide explains the changes and teaching conventions.
