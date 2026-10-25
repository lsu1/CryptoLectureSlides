# Lecture 01: Classical Ciphers — consolidated revision

A three-hour lecture for mathematics master's students with little prior cryptography background. The current PDF has **75 teaching slides and 13 optional appendix pages**, with two ten-minute breaks included in the instructor's pacing plan.

## Files

- [Lecture slides (PDF)](Lecture01_Classical_Ciphers.pdf)
- [Instructor guide (PDF)](Lecture01_Instructor_Guide.pdf): pacing, worked answers, teaching notes, reading, and revision details.
- [Editable source bundle](Lecture01_Source.zip)
- [Worked-example data](worked_examples.json)
- [Validation report](validation.json)
- [Revision notes](CHANGES.md)

The scope remains shift, monoalphabetic substitution, Vigenère, Playfair, and block transposition. The reference's 168-letter frequency-analysis example is explained through five grouped recovery stages. The Vigenère attack uses one consistent 1,045-letter dataset, with its complete ciphertext and recovered prose in the appendix.

## Teaching sequence

The timetable is kept here and in the instructor guide, rather than on a lecture slide. The longer allocations allow calculation pauses, board annotations, and questions; they are not intended as equal time per page.

| Elapsed time | Slides | Material |
|---|---|---|
| 00–16 min | 1–11 | Communication problem, terminology, symmetric keys, mathematical model |
| 16–25 min | 12–18 | Shift definition, inverse, worked calculation, and search stopping at key 3 |
| 25–30 min | 19–22 | Substitution and the chosen permutation σ |
| 30–60 min | 23–32 | Five representative frequency-analysis recovery stages and guided practice |
| 60–70 min | 33 | Break |
| 70–120 min | 34–50 | Vigenère, visual Kasiski repetitions, IC intuition, coloured columns, and key recovery |
| 120–130 min | 51 | Break |
| 130–158 min | 52–66 | Playfair square, preparation, geometric rules, and exercise |
| 158–172 min | 67–73 | Permutation definition, example, and inverse |
| 172–180 min | 74–75 | Compare constructions and connect to digital messages |
| Optional support | 76–88 | Complete data, IC derivations, and detailed frequency scoring |

The main presentation defines the **index of coincidence (IC)** as a letter-match probability, illustrates it with `AAB`, then introduces the essential count formula. The appendix retains the longer derivations and chi-squared calculations for optional mathematical depth.

## Edit and rebuild

- `slide_content.py`: editable slide content, diagram inputs, and typeset equations.
- `cipher_examples.py`: cipher operations, datasets, and numerical calculations.
- `build_lecture.py`: layout, visual diagrams, and PDF assembly.
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

The PDFs, `slide_manifest.json`, `worked_examples.json`, and `validation.json` are generated outputs. Inspect rendered pages after content or layout changes; numerical checks alone do not establish presentation quality. Equations and diagrams are vector content, and text and mathematics fonts are embedded.

## Reference and provenance

Based on the supplied `Lecture02_Classical_Ciphers.pdf`, Wu Hongjun, 79 pages. The reference's ciphertext/plaintext example and the standard Playfair illustration are retained and credited. The original PDF is not redistributed here. Reading and bibliographic information are in the instructor guide; the lecture's former final reading slide has been removed. Previous published versions remain available through Git history.
