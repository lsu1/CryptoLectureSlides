# Revision history

## Integration with Lecture 00 and the 3.5-hour session

- Keeps the decks separate and assigns Lecture 00 to 6:30–6:45 pm, followed by Lecture 01 through 10:00 pm.
- Removes the repeated motivation slide, formerly Lecture 01 page 2.
- Reframes the former definition slide as “Today: constructing and analysing ciphers,” preserving cryptanalysis and confidentiality as the technical focus.
- Keeps the formal encryption/decryption diagram with shorter prose and makes the shared-secret assumption explicit for the five classical ciphers.
- Replaces the cover subtitle with “Historical ciphers and cryptanalysis,” preserving its approved layout.
- Updates both teaching guides, page references, and break-slide return times for the agreed session. Breaks are 7:40–7:50 pm and 8:45–8:55 pm.
- Preserves all cipher constructions, worked examples, mathematical foundations, and optional appendix material. Lecture 00’s main presentation is unchanged.

The current Lecture 01 PDF contains **74 teaching pages plus 13 optional appendix pages**, for 87 pages total. The combined session lasts 210 minutes, including 20 minutes of breaks and 190 minutes of teaching. Fifteen teaching minutes are allocated to Lecture 00 and 175 to Lecture 01 and questions.

## Prior consolidated review

The page numbers below refer to the earlier 99-page PDF where stated. Those changes were applied together after the user's review; later removals renumber the deck.

- **Former page 1:** redesigned the cover using only the title, series name, and introductory subtitle. Removed the descriptive sentence, audience/lecture panel, and duration/revision strip identified by the red box.
- **Former page 12:** removed “Plan for the three hours.” Pacing remains in the instructor guide and README.
- **Former page 18:** the worked shift search now displays keys 1, 2, and 3, stopping when `HELLOWORLD` is recovered. Removed the key-4 trial.
- **Former page 21:** explicitly defines σ as the chosen secret alphabet permutation in S₂₆ and σ⁻¹ as its inverse for decryption.
- **Following former page 26:** condensed the eleven frequency-analysis stages into five representative stages. Kept the original 168-letter ciphertext, meaningful pair clues, partial plaintext updates, the complete recovered message, and the distinction between logical constraints and probabilistic guesses. Similar remaining trials are summarized.
- **Former pages 48–66:** replaced the mathematically dense sequence with ten example-led slides: highlighted repeated alignment; actual repetition distances; the meaning of index of coincidence (IC); a visual `AAB` match example; longer-text reference values; one essential IC formula; coloured aligned columns; individual column match rates; visual frequency comparisons; and key/message verification.
- **Optional mathematics:** moved the finite-sample IC derivation, larger worked count, sample/probability relationship, chi-squared formula, score contributions, candidate-score comparison, and full five-column score table into appendix pages A7–A13. Existing complete data remain in A1–A6.
- **Former pages 92 and 93:** removed “Reflection questions” and “Reading and sources.” Bibliographic references remain in the instructor guide and source documentation.
- **Scope and continuity:** retained the same five ciphers, the gentle cryptography introduction, appropriate formal definitions, worked Playfair/permutation examples, and selected exercises. No additional cipher algorithm was introduced.
- **Consistency:** updated the instructor guide, page references, source bundle, generated content/data, and validation checks to match the new structure.

That prior revision produced 75 teaching pages plus 13 appendix pages. The integration above supersedes its old three-hour pacing plan. Numerical and rendering verification for the current deck is reported in `validation.json`; manual review complements those checks.
