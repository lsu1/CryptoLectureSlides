# Lecture 00: Introduction to Cryptography

An **11-slide, nontechnical introduction** for master's students encountering cryptography for the first time. The suggested pacing is **11 minutes 45 seconds**, with room to adapt within a 10–15-minute opening before Lecture 01.

- [Lecture slides (PDF)](Lecture00_Introduction.pdf)
- [Teaching notes (PDF)](Lecture00_Teaching_Notes.pdf): three pages of timing, delivery guidance, accuracy notes, and sources.
- [Editable source bundle](Lecture00_Source.zip)

The deck follows the gist of the supplied `Lecture01_Introduction.pdf`: cryptography's protection goals, changing technology and communication, practical applications, and its place within a secure system. It keeps the opening visual and approachable, without formulas or protocol tutorials.

Examples include private messaging, HTTPS, payments, passkeys, electronic passports, and signed software updates. It omits the old Swift-volume and regional ATM timelines and uses an illustrative scam rather than a dated news case. Sources and nuanced technical qualifications are kept in the companion notes, rather than adding a reading or warning slide after every application.

## Edit and rebuild

`content.py` holds the slide titles, delivery times, speaker notes, and source records. `build_deck.py` produces the slides; `build_notes.py` produces the teaching companion. The original supplied PDF is cited but is not redistributed.

From this directory, with Python 3, ReportLab, PyMuPDF, and the DejaVu Sans font files available:

```sh
python build_deck.py
python build_notes.py
python validate.py
```

The main presentation does not require Internet access. Text and diagrams are generated as PDF content with embedded fonts. After editing, inspect the rendered pages as well as running the checks. The source bundle is intended for future revision; Git history preserves published versions.
