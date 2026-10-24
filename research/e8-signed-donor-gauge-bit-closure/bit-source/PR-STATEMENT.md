# E8 bit word: κ = 8.75481145306751e-4 (complex-bound)

**Claim.** We claim a conditional κ = 875481145306751/10¹⁸ ≈ 8.75481145306751·10⁻⁴. That is +9.29 % over #352 and
+8.54 % over the best p = 10 bit package.

**What is new.** This is the first bit supplier that is not a paired-cube word. Its labels are the 120 root lines of E8
in Q⁸, with the E8 form, which is positive definite, so every frame is nondegenerate:
- h = 8, m = 40, v = 120, R = 865;
- 9 retained totals at the full frame, so copy loss 72 and deficit 120;
- the junk of each target is the E7 in its cap;
- a side network built on D4 blocks and π-coset pairings, after a local search.

**Bit coarse saving.** c = 9.04072820242522·10⁻⁴. That is +12.0 % over the previous bit root and 3.2 % above
Sussman's E8 complex unit (b = 8.76248285600677·10⁻⁴), which therefore binds. With #363's seven-stage b₃ the same bit
word would bind at κ = 9.0326e-4; this package reports that number but does not claim it.

**How it is checked** (`bash verify.sh DIR`, about 2.5 min):
1. The word is regenerated from its producer parameters.
2. An independent checker verifies:
   - exact rational frame legality;
   - the exact F₂ identity on all 1105 columns, with dirty helpers;
   - the Gram determinants and the price.
   It rejects 6 word-level mutants.
3. The **PR #266 official legality and five-stage formal-columns checkers** run with h = 8 and NCOPY = 9. 6 record-level
   mutants are rejected.
4. Exact nondegeneracy under the E8 Gram and PR #315's prime-witness rule. The only prime is 2.
5. PR234's five-stage route and idle geometry is checked on all 120 ports, with W(E8) reflection words as port
   isometries. The idle ranks are (14, 7, 18, 4).
6. Banks: 173 exact width-40 banks.
7. PR #352's complex checks, unchanged.
8. PR #315's moment engines and the outer assembly with all 47 constraints. The adjacent grid point is rejected.
9. The finite bill at m = 40: coefficient 41 bits < 2⁸⁰.

**Regressions.** Every bit-side generalization has a parameter whose default is the original. On the PR #325 p10b word,
and on agent G's p = 10 loans receipts, each one reproduces the original checker's output:
- legality: byte-identical receipt;
- five-stage columns: identical receipt;
- prime witnesses: identical counts;
- banks: byte-identical output;
- certify_bit: identical fields;
- finite bill: the same coefficient, gaps, chain and route hash;
- geometry: the same routes.

**Admitted explicitly.** 9 retained totals at h = 8: a layout pin of the paired-cube words. It is charged as NCOPY = 9
copies, temporaries and episodes. All inherited bit-supplier interfaces, and #352's complex obligations, are retained.
PR234's bank construction for a non-paired-cube family is checked on the exact matrices; it is not re-proved.

Author: Dylan Crow, with Anthropic Claude assistance. Credits:
- Jacob Sussman: the E8 family and unit;
- DaysSky: #352, and #363 for the secondary step;
- #346/#315/#266/source527/PR234 lineage: see `README.md` and `NOTICE.md`.
