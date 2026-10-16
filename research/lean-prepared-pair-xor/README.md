# Paid binary input preparation and marked XOR

Four accepted Lean modules compose public PR488 preparation with a paid backward paired-input writer and the explicit-marker XOR scan of PR1840. The exact framing module is first-published here unchanged; no copy of the six already-public prerequisites is included.

For input bit lists xs and ys, the actual five-tape controller executes both mode switches, preserves the stated source/work tape contents and returns the marked XOR output head. Its genuine first halt is bounded by 18*max(length xs,length ys)+24. The output target value is the XOR of the two original unsigned values; its source track has the original second value. Work-input heads finish at their visited left blanks, rather than being claimed restored.

The actual entrance measure is V=max(1,length xs)+max(1,length ys)+2. Four-cell-per-step growth and actual halt stuttering derive time <=18V and every-prefix represented cells <=73V, including empty input and observations after halt. These deliberately conservative constants count finite-alphabet represented tape cells; fixed control and Boolean registers are additional constant storage. Initial encoding/workspace, physical layout, arbitrary dirty-state inversion and the complete selected multiplier remain separate.

The accepted framing result covers arbitrary supplied same-tape spectator contexts for the XOR stage. It does not install those contexts for free. All four source files are preserved exactly, including historical comments saying uncompiled; the source-bound manifest records subsequent kernel checking and independent review. There are 27 complete axiom probes and six full types for these four modules, with standard Lean axioms only and no new-source diagnostics.

Public dependencies are PR488 at 34eb901441affffaba76b00920f2f9cb05777117 and PR1840 at 3f1b0641d5866f9d0b6cdd8e46db416fed6c5645. Use their exact source paths/hashes in MANIFEST.json. This core needs Lean 4.21.0 only. The completed exponent-metadata refinement is outside this package until its separate dyadic dependency closure is public.

James Chang, Apache-2.0, with OpenAI assistance. Author-checked context: kappa=836330098538459/500000000000000000=0.001672660197076918. This contextual value is not a multiplier bound proved here. Preserve PR488's distinct historical source notices and authorship when obtaining its prerequisites.
