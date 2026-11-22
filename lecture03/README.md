# MH6003 Cryptography · Lecture 03

[Download the AES lecture](Lecture03_AES.pdf) · [Download the instructor guide](Lecture03_Instructor_Guide.pdf)

The lecture follows the substitution–permutation network in Lecture 2 into the Advanced Encryption Standard. A single AES-128 plaintext and key connect state layout, the first round, the key schedule and decryption. In the arithmetic section, students calculate the reference lecture’s byte product 57 × 83 = C1 and use the inverse of 05 to construct the S-box entry 6B. All byte values in these examples are hexadecimal.

| Time | Slides | Classroom activity |
| --- | --- | --- |
| 18:30–19:30 | 1–23 | Load a block into the state. Interpret bytes as polynomials, multiply in the AES field and find a multiplicative inverse. |
| 19:30–19:45 | 24 | Break |
| 19:45–20:45 | 25–41 | Trace all four operations in round 1. Calculate one MixColumns output together, then try a second column. |
| 20:45–21:00 | 42 | Break |
| 21:00–22:00 | 43–60 | Derive the first round key, compare key sizes, reach the ciphertext and reverse the operations. Check the result against a published test vector. |

Slides 61–69 are optional references. They include the forward and inverse S-boxes, every AES-128 round key and round-end state for this example, and worked algebra. The PDF bookmarks and links on the teaching slides open the corresponding references.

## Sources

The scope follows Wu Hongjun’s supplied *MH4311 Cryptography, Lecture 6, Block Cipher AES*. The standard defines the arithmetic, transformations and key schedule. The ascending-byte key and the plaintext starting with 00 11 22 33 come from the 2001 edition, Appendix C.1. [Current AES standard](https://doi.org/10.6028/NIST.FIPS.197-upd1) · [Original edition with the worked example](https://doi.org/10.6028/NIST.FIPS.197)

## Editing and rebuilding

The opening, schedule and reference tables are in [content.py](content.py). The three teaching sections are in [field.py](field.py), [rounds.py](rounds.py) and [keys.py](keys.py). Both PDFs use the same slide records. [aes_trace.py](aes_trace.py) derives the lookup tables and state grids and checks all three key sizes against published known answers.

With the [Lecture 2 Python dependencies](../lecture02/requirements.txt), DejaVu fonts and pdfLaTeX installed, run these commands from the repository root. The slide builder uses the existing Lecture 2 layout and vector maths code.

```sh
python lecture03/build_aes.py
python lecture03/build_guide.py
```
