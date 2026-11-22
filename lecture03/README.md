# MH6003 Cryptography · Lecture 03

[Download the AES lecture](Lecture03_AES.pdf) · [Download the instructor guide](Lecture03_Instructor_Guide.pdf)

This instructor-review edition follows one AES-128 block from the plaintext to the ciphertext and back. It includes the mathematical development from the reference lecture alongside the worked encryption. Slides 5 and 6 map the four stages of encryption and the operations within a round. Select a stage or operation to open a worked example. Select the strip above a calculation to return to its overview.

| Scheduled time | Slides | Material | Estimated time to teach in full |
| --- | --- | --- | --- |
| 18:30–19:30 | 1–41 | Meet AES, load the state, calculate integer GCDs and modular inverses, and build the byte field with polynomial examples. | 104 min |
| 19:30–19:45 | 42 | Break | 15 min |
| 19:45–20:45 | 43–74 | Trace the first round. Construct an S-box entry, rotate rows, derive and invert the MixColumns matrix, and XOR the round key. | 106 min |
| 20:45–21:00 | 75 | Break | 15 min |
| 21:00–22:00 | 76–94 | Expand the key, reach the final ciphertext, decrypt the example and check an implementation. | 60 min |

The class has 180 teaching minutes. Working through every main slide and exercise is estimated at 270 teaching minutes. The break slides mark the scheduled classroom breaks. The full sequence is available for the instructor to review before choosing what to teach live.

Appendix slides 95–105 contain the forward and inverse S-boxes, all eleven round keys and round-end states for the AES-128 example, additional worked algebra, the decryption loop and an implementation comparison. The PDF bookmarks list each appendix entry. Links beside slide footers open the corresponding reference.

## Sources

The scope follows Wu Hongjun’s supplied *MH4311 Cryptography, Lecture 6, Block Cipher AES*. The standard defines the arithmetic, transformations and key schedule. The ascending-byte key and the plaintext starting with 00 11 22 33 come from the 2001 edition, Appendix C.1. [Current AES standard](https://doi.org/10.6028/NIST.FIPS.197-upd1) · [Original edition with the worked example](https://doi.org/10.6028/NIST.FIPS.197)

## Editing and rebuilding

The opening, schedule and reference tables are in [content.py](content.py). The overview slides and step labels are in [algorithm.py](algorithm.py). The three teaching sections are in [field.py](field.py), [rounds.py](rounds.py) and [keys.py](keys.py). Both PDFs use the same slide records. [aes_trace.py](aes_trace.py) derives the lookup tables and state grids and checks all three key sizes against published known answers.

With the [Lecture 2 Python dependencies](../lecture02/requirements.txt), DejaVu fonts and pdfLaTeX installed, run these commands from the repository root. The slide builder uses the existing Lecture 2 layout and vector maths code.

```sh
python lecture03/build_aes.py
python lecture03/build_guide.py
```
