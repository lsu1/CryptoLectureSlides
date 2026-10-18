# Lecture 01: Classical Ciphers — revised edition

A three-hour lecture for mathematics master's students with little prior cryptography background. The revised PDF has **93 teaching slides and six supporting appendix pages**, with two ten-minute breaks included in the schedule.

## Files

- [Lecture slides (PDF)](Lecture01_Classical_Ciphers.pdf)
- [Instructor guide (PDF)](Lecture01_Instructor_Guide.pdf): seven pages of pacing, worked answers, teaching notes, and revision details.
- [Editable source bundle](Lecture01_Source.zip)
- [Worked-example data](worked_examples.json)
- [Validation report](validation.json)
- [Revision notes](CHANGES.md)

Only the five original constructions are taught: shift, monoalphabetic substitution, Vigenère, Playfair, and block transposition. The reference's 168-letter frequency-analysis example is restored with eleven recovery stages. The Vigenère attack uses one consistent 1,045-letter dataset, printed in full within the appendix.

## Teaching sequence

| Elapsed time | Slides | Material |
|---|---|---|
| 00–16 min | 1–12 | Communication problem, terminology, symmetric keys, mathematical model |
| 16–25 min | 13–19 | Shift definition, inverse, and worked calculation |
| 25–30 min | 20–23 | Substitution as a bijection |
| 30–60 min | 24–39 | Guided frequency-analysis recovery |
| 60–70 min | 40 | Break |
| 70–120 min | 41–66 | Vigenère, Kasiski, IC derivation, and key recovery |
| 120–130 min | 67 | Break |
| 130–158 min | 68–82 | Playfair square, preparation, separate rules, and exercise |
| 158–172 min | 83–89 | Permutation definition, example, and inverse |
| 172–180 min | 90–93 | Comparison, reflection, and reading |
| Supporting data | 94–99 | Ciphertext, column counts, model probabilities, recovered prose |

## Edit and rebuild

- `slide_content.py`: editable slide content and typeset equations.
- `cipher_examples.py`: cipher operations, datasets, and numerical calculations.
- `build_lecture.py`: layout and PDF assembly.
- `math_typesetting.py`: LaTeX vector-equation rendering, with shell escape disabled.
- `build_guide.py`: instructor-guide content and layout.
- `validate.py`: numerical, content, rendering, geometry, and font checks.

Requires Python 3 with ReportLab and PyMuPDF; DejaVu Sans / Sans Mono files in `/usr/share/fonts/truetype/dejavu/`; and `pdflatex` with amsmath, amssymb, Latin Modern, xcolor, and geometry. See `requirements.txt` for the Python versions used in this environment. No Internet access is needed to build once these prerequisites are present.

Run from this directory:

```sh
python build_lecture.py
python build_guide.py
python validate.py
```

The PDFs, `slide_manifest.json`, `worked_examples.json`, and `validation.json` are generated outputs. Inspect rendered pages after content or layout changes; passing numerical checks alone does not establish presentation quality. Equations are vector content, and all text and mathematics fonts are embedded.

## Reference and provenance

Based on the supplied `Lecture02_Classical_Ciphers.pdf`, Wu Hongjun, 79 pages. The reference's ciphertext and plaintext example are retained and credited, together with the standard Playfair illustration. The original PDF is not redistributed here. Bibliographic reading is listed on slide 93. Previous published versions remain available through Git history.
