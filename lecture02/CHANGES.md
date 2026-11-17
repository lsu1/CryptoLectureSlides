# Changes from the supplied Lecture 03–05 references

The three old decks are consolidated into **Lecture 02: One-time Pads and Block Ciphers**, for a 6:30–10:00 pm master's class with 190 teaching minutes and two ten-minute breaks. The academic tone, mathematical definitions, proofs, and step-by-step examples are retained. The new presentation follows the established navy, teal, and light-paper design, with consistent embedded fonts and vector equations and diagrams.

## Structure and teaching

- Repeated course outlines, reading pages, section covers, and separate summaries are consolidated. Sources and detailed delivery guidance are in the instructor companion.
- The sequence now moves from the previous lecture's repeating-key weakness to OTP construction, probability, perfect secrecy, information theory, practical security, round structures, and DES.
- Original worked examples are completed, including all letters of `NANYANG + XRTRPLK`, the ten-bit XOR answer and reversal, dice conditioning, and coin entropy.
- The OTP proof is expanded into explicit likelihood, marginal-probability, and Bayes steps. A nonuniform plaintext prior demonstrates that perfect secrecy preserves prior beliefs rather than making every message equally likely.
- The reference toy SPN receives explicit S-box values, a bit permutation, round keys, and a numerical trace. These are identified as new teaching choices because the old diagram did not specify them.
- Feistel inversion is shown algebraically and through a small calculation. One DES plaintext/key/ciphertext vector connects the initial permutation, first round, S-boxes, key schedule, final swap, and output.
- Conditional-entropy depth and complete DES lookup tables are optional appendix material. The main deck includes the complete OTP proof and essential DES calculations.

## Corrections and updates

- OTP requirements explicitly include a uniform key independent of the message, enough fresh pad material, secrecy, and no reuse. Reuse cancellation is worked numerically; VENONA illustrates the operational failure without claiming that a correctly used OTP was broken.
- Perfect secrecy is stated for positive-probability ciphertext observations. Message length and integrity are distinguished from the confidentiality theorem.
- Shannon's information-theory paper is dated **1948**; his secrecy-systems paper is dated **1949**. The entropy definition includes the zero-probability convention.
- Single-letter entropy, normalized block entropy, and entropy rate are distinguished. The unicity calculation consistently assumes a language rate of 1.25 bits per letter, producing about **25.6 letters**, with an explicit explanation that this is a statistical heuristic. It is neither a guaranteed break nor a computational attack cost.
- Information-theoretic and computational security are compared without equating every information-theoretic notion with exact perfect secrecy. Known-plaintext attacks are defined using matching pairs and a clear attack objective.
- Kerckhoffs' principle supports public specifications and independent review. The reference's suggestion that publishing a cipher relies on cooperative attackers is removed.
- Dated CPU-price lists, supercomputer rankings, and fixed future speed forecasts are replaced by hypothetical complete-key-test rates. FLOPS and clock frequency are not treated as cipher benchmarks.
- Block size, key size, and security strength are separated. Round keys are derived values, rather than independent OTP pads. Diffusion is attributed to the interaction of layers and rounds; a bit permutation alone only reorders bits.
- DES's 56 effective key bits are distinguished from its 64-bit parity-bearing encoding. Table indexing, the non-invertible Feistel inner function, S-box selection, round-key rotations, and the final swap use one consistent convention.
- Double DES includes meet-in-the-middle work and storage requirements, false candidates, and verification with additional known pairs. Triple DES uses EDE notation, distinguishes two-key and three-key forms, and avoids claiming 168-bit security.
- DES and TDEA are described as historical algorithms. The guide cites NIST's withdrawal of SP 800-67 Rev. 2, effective **1 January 2024**, and distinguishes new protection from legacy processing. The 64-bit block-size limitation remains separate from key length.

## Provenance and review

The scope references are Wu Hongjun's `Lecture03_OneTimePad.pdf`, `Lecture04_Block_Cipher_Introduction.pdf`, and `Lecture05_Block_Cipher_DES.pdf`. Their core topics remain; AES internals, modes, and additional advanced ciphers are not introduced. Original uploaded PDFs are cited but not redistributed.

The instructor guide records source-page coverage, worked answers, per-slide notes, the session schedule, and bibliographic sources. Official NIST pages could not be fetched through the network proxy; the citations are not presented as freshly retrieved documents. The DES trace is recomputed from the tables and independently checked, including its final ciphertext with OpenSSL. The validation report records the actual numerical, PDF, font, geometry, and rendering checks performed for the generated edition.
