# MH6003: Cryptography — course information

A **seven-slide draft for instructor review**, based on the supplied OBTL course document, grading-discussion screenshot, and subsequent user clarifications.

- [Course-information slides (PDF)](MH6003_Course_Information.pdf)
- [Instructor review notes (PDF)](MH6003_Review_Notes.pdf)
- [Editable source bundle](MH6003_Source.zip)

The deck lists both instructors, the topics for all 13 weeks, the **20% mid-term / 30% group project / 50% final** grading split, the closed-book examination arrangements, and the group-project timeline. Week 12 remains regular teaching. Week 13 contains about one hour of revision followed by the two-hour final exam.

The review notes record source precedence and details still to be specified, such as calendar dates, exact examination times, and the project submission format. The original document and screenshot are not redistributed, and unrelated email correspondence is not included.

## Edit and rebuild

`content.py` contains the course facts and source records. `build_deck.py` generates the slides; `build_review.py` generates the review companion. The draft uses the course series' DejaVu Sans fonts, consistent colours, and embedded text.

Requires Python 3, ReportLab, PyMuPDF, and the DejaVu Sans font files at `/usr/share/fonts/truetype/dejavu/`. See `requirements.txt` for the Python versions used in this environment.

Run from this directory:

```sh
python build_deck.py
python build_review.py
python validate.py
```

Inspect the rendered pages after edits as well as running the checks. The slide PDF and review PDF are generated outputs; the source bundle supports later revisions, and Git history preserves published versions.
