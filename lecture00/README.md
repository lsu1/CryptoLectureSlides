# Lecture 00: Introduction to Cryptography

An **11-slide, nontechnical introduction** for master's students encountering cryptography for the first time. Its suggested slide delivery is **11 minutes 45 seconds**, allocated within the **6:30–6:45 pm opening** of the 6:30–10:00 pm joint session. The remaining 3 minutes 15 seconds allows responses and the handoff to Lecture 01. The two decks remain separate.

- [Lecture slides (PDF)](Lecture00_Introduction.pdf)
- [Teaching notes (PDF)](Lecture00_Teaching_Notes.pdf): three pages of timing, delivery guidance, accuracy notes, and sources.
- [Editable source bundle](Lecture00_Source.zip)

The deck follows the gist of the supplied `Lecture01_Introduction.pdf`: cryptography's protection goals, changing technology and communication, practical applications, and its place within a secure system. It keeps the opening visual and approachable, without formulas or protocol tutorials.

Examples include private messaging, HTTPS, payments, passkeys, electronic passports, and signed software updates. It omits the old Swift-volume and regional ATM timelines and uses an illustrative scam rather than a dated news case. Sources and nuanced technical qualifications are kept in the companion notes, rather than adding a reading or warning slide after every application.

## Shared session plan

Both teaching guides use the following 3.5-hour plan, with 190 teaching minutes and two ten-minute breaks:

| Time (pm) | Focus |
|---|---|
| 6:30–6:45 | Lecture 00: introduction |
| 6:45–7:40 | Lecture 01: foundations, shift, substitution, frequency analysis |
| 7:40–7:50 | Break |
| 7:50–8:45 | Lecture 01: Vigenère, Kasiski, IC, key recovery |
| 8:45–8:55 | Break |
| 8:55–9:30 | Lecture 01: Playfair |
| 9:30–9:50 | Lecture 01: transposition |
| 9:50–10:00 | Lecture 01: comparison and questions |

Lecture 01 now avoids repeating this deck’s general motivation. It retains the formal vocabulary, mathematical model, attacker assumptions, and worked cipher examples. Lecture 00’s presentation remains unchanged; its guide now situates it within the full evening session.

## Edit and rebuild

`content.py` holds the slide titles, delivery times, speaker notes, and source records. `build_deck.py` produces the slides; `build_notes.py` produces the teaching companion. The original supplied PDF is cited but is not redistributed.

From this directory, with Python 3, ReportLab, PyMuPDF, and the DejaVu Sans font files available:

```sh
python build_deck.py
python build_notes.py
python validate.py
```

The main presentation does not require Internet access. Text and diagrams are generated as PDF content with embedded fonts. After editing, inspect the rendered pages as well as running the checks. The source bundle is intended for future revision; Git history preserves published versions.
