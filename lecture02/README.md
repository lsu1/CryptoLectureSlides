# Lecture 02: One-time Pads and Block Ciphers

A technical lecture for master's students, continuing from Lecture 01's classical ciphers. It combines the supplied one-time-pad, block-cipher introduction, and DES references into one evening session, with worked examples and a complete proof of OTP perfect secrecy.

- [Lecture slides (PDF)](Lecture02_OTP_and_Block_Ciphers.pdf)
- [Instructor guide (PDF)](Lecture02_Instructor_Guide.pdf): pacing, worked answers, slide-by-slide teaching notes, corrections, and sources.
- [Editable source bundle](Lecture02_Source.zip)
- [Changes from the references](CHANGES.md)

The main deck covers one-time pads and reuse, elementary probability and Bayes' rule, perfect secrecy, entropy and unicity distance, computational security, block-cipher design, a specified toy SPN, Feistel networks, DES, Double DES, and Triple DES. Optional appendix pages contain the conditional-entropy key bound, full DES reference tables, the two-round Feistel calculation in both directions, and all eight first-round DES S-box calculations in A14. AES internals, modes of operation, and new advanced ciphers are left for later lectures.

## Session plan

The 6:30–10:00 pm session has **190 teaching minutes and two ten-minute breaks**. The allocations include calculations, board explanations, and questions.

| Time (pm) | Focus |
|---|---|
| 6:30–7:40 | One-time pads, probability, perfect secrecy, entropy, redundancy, and unicity |
| 7:40–7:50 | Break |
| 7:50–8:50 | Practical security, block-cipher design, toy SPN, and Feistel networks |
| 8:50–9:00 | Break |
| 9:00–10:00 | DES internals and key schedule, Double DES, and Triple DES |

`slide_content.py` defines the schedule and derives page counts and per-slide allocations from the assembled content. The instructor guide generates its ranges and teaching notes from those same records. Optional appendix pages have no scheduled teaching allocation.

## Examples and scope

The new deck retains and completes the original `NANYANG` / `XRTRPLK` letter example, ten-bit XOR exercise, two-dice probability example, and fair/biased coin entropy examples. It adds a fully specified numerical trace for the reference's toy SPN and uses one DES known-answer vector throughout the data path and key schedule. The toy lookup values and keys are explicit teaching choices; the reference drawing did not supply them.

The DES walkthrough follows one complete round in order: input halves after IP, expansion, key mixing, the actual S-box groups, permutation P, and the Feistel output. It then derives the round key and returns to the remaining rounds, final swap, and final ciphertext. The first-round S₁ lookup uses `011000`, row `00` (0), column `1100` (12), and output `0101` (5). Appendix A14 works every six-bit XOR and S-box selection, supporting a complete check of the same round.

Contemporary security statements distinguish historical DES/TDEA from current deployment choices. NIST's withdrawal of the TDEA recommendation, effective 1 January 2024, is cited in the guide. The old processor-price lists and supercomputer rankings are replaced by clearly hypothetical key-search rates. A block cipher's key size, block size, and attack resistance are treated as separate quantities.

The scope references are Wu Hongjun's `Lecture03_OneTimePad.pdf` (35 pages), `Lecture04_Block_Cipher_Introduction.pdf` (26 pages), and `Lecture05_Block_Cipher_DES.pdf` (26 pages). The originals are cited but are not redistributed. Official NIST references are bibliographic: retrieval attempts were blocked by the network proxy, as recorded in the guide.

## Edit and rebuild

The editable files separate content from rendering:

- `otp_content.py`, `block_content.py`, and `des_content.py`: explanations, examples, teaching notes, and initial pacing weights.
- `slide_content.py`: assembly, cover, breaks, closing slide, and wall-clock allocations.
- `crypto_examples.py`: toy SPN and DES tables, calculations, and traces.
- `build_lecture.py`, `diagrams.py`, and `math_typesetting.py`: slide layout, vector illustrations, and equations.
- `build_guide.py`: the dynamically generated instructor companion.
- `validate.py`: numerical, content, font, rendering, and layout checks.
- `package_source.py`: the editable source bundle.

Requirements are Python 3, ReportLab, PyMuPDF, the DejaVu Sans and Sans Mono font files, and `pdflatex` with `amsmath`, `amssymb`, Latin Modern, `xcolor`, and `geometry`. Equations are placed as vector PDF content; LaTeX shell escape is disabled. The build and presentation do not require Internet access.

From this directory:

```sh
python build_lecture.py
python build_guide.py
python validate.py
python package_source.py
```

Generated JSON records document the slide content, session plan, worked examples, layout checks, and validation results. After changing content or layout, inspect the rendered slides and guide as well as running the checks. The PDFs are reviewable outputs; the source bundle supports future revision.
