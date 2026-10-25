# Lecture 01: Classical Ciphers — historical ciphers and cryptanalysis

The technical deck for a **6:30–10:00 pm joint session**, following the separate Lecture 00 introduction. The current PDF has **74 teaching slides and 13 optional appendix pages**. The 3.5-hour plan includes two ten-minute breaks, 15 minutes for Lecture 00, and 175 teaching minutes for Lecture 01 and questions.

## Files

- [Lecture slides (PDF)](Lecture01_Classical_Ciphers.pdf)
- [Instructor guide (PDF)](Lecture01_Instructor_Guide.pdf): pacing, worked answers, teaching notes, reading, and revision details.
- [Editable source bundle](Lecture01_Source.zip)
- [Worked-example data](worked_examples.json)
- [Validation report](validation.json)
- [Revision notes](CHANGES.md)

The opening assumes the Lecture 00 application survey is complete. It removes the duplicate motivation, preserves the definition of cryptanalysis, shortens the encryption diagram’s prose, and clarifies that these classical examples assume a shared secret. The scope remains shift, monoalphabetic substitution, Vigenère, Playfair, and block transposition. The reference's 168-letter frequency-analysis example is explained through five grouped recovery stages. The Vigenère attack uses one consistent 1,045-letter dataset, with its complete ciphertext and recovered prose in the appendix.

## Teaching sequence

The decks remain separate. The timetable is kept here and in both teaching guides; the break slides show the corresponding return times. Lecture 00’s suggested delivery is 11 minutes 45 seconds within its 15-minute opening slot. The technical allocations allow calculation pauses, board annotations, and questions rather than equal time per slide.

| Time (pm) | Deck / slides | Material |
|---|---|---|
| 6:30–6:45 | Lecture 00: 1–11 | Nontechnical orientation and handoff |
| 6:45–7:40 | Lecture 01: 1–31 | Formal foundations, shift, substitution, frequency analysis |
| 7:40–7:50 | Lecture 01: 32 | Break |
| 7:50–8:45 | Lecture 01: 33–49 | Vigenère, visual Kasiski/IC, key recovery |
| 8:45–8:55 | Lecture 01: 50 | Break |
| 8:55–9:30 | Lecture 01: 51–65 | Playfair |
| 9:30–9:50 | Lecture 01: 66–72 | Transposition |
| 9:50–10:00 | Lecture 01: 73–74 | Comparison and questions |
| Optional support | Lecture 01: 75–87 | Complete data, IC derivations, detailed scoring |

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
