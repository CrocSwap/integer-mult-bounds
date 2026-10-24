# Exact parity constants and q-series for the projection recurrence

This package answers **Open next questions, item 2** in Krzysztof Wojt's
[#5193](https://github.com/CrocSwap/integer-mult-bounds/pull/5193): an explicit
q-series for every eigenmode and exact parity-sensitive leading error constants.
For the unstrengthened projection recurrence with seed
`a_4=(0,27456,48576,68320,86592)` and `T_m=a_m(m)/a_m(1)`, it proves

\[
T_m=\frac{439277}{149175}
+2^{-m}\left(\frac{815083}{596700}
+(-1)^m\frac{323}{28}\mathcal K\right)+O(4^{-m}),
\qquad
\mathcal K=\prod_{i=1}^{\infty}
\left(\frac{1-2^{-i}}{1+2^{-i}}\right)^2>0.
\]

The even and odd limits of `2^m(T_m-439277/149175)` are, respectively,
`1.535225897075989125...` and `1.196743266657880490...`. The complete scaled
sequence therefore has no limit. The rational limit itself is Nick Petalas's
[#5151](https://github.com/CrocSwap/integer-mult-bounds/pull/5151) result.

## Proof and evidence

[PROOF.md](PROOF.md) gives the recurrence and a self-contained derivation.
Starting with #5193's credited four-mode reduction, a change of variables gives
a dilation equation for each mode's generating function. Its explicit q-series,
classical q-Gauss summation ([NIST DLMF 17.6.1](https://dlmf.nist.gov/17.6.E1)),
and simple poles at 1 and +/-2 give the constants. Subtracting the pole parts
at +/-4 as well justifies the `O(4^-m)` remainder by Cauchy's estimate.

[verify.py](verify.py) uses only the Python standard library and exact rational
arithmetic for the mathematical checks. [RESULT.json](RESULT.json) records:

- 2,691 whole-profile equalities against a separately implemented raw recurrence;
- 276 finite-product identities and 520 eigenmode transformations;
- 32 rigorous generating-series enclosure comparisons and 16 residue checks;
- six rejected perturbations of the seed, subdiagonal, raw recurrence seed,
  eigenvalue, parity sign, or residue factor.

These finite checks corroborate the proof; series-interval overlap and finite
asymptotic samples do not themselves prove the universal analytic identities.
The q-Gauss identity is a cited classical mathematical input, not a network or
runtime dependency. The script reads its own source and `PROOF.md` only to
produce receipt hashes; it writes no files and imports no predecessor code.

[REVIEW.md](REVIEW.md) records a separate Codex agent's mathematical and code
review and binds it to exact hashes. It also records an independently written
raw recurrence check through block 100. This is AI review, not human review or
proof-kernel verification.

## Reproduce

From the repository root, with Python 3.12 and its standard library:

```sh
python3 -B scripts/research_package.py --package research/projection-parity-constants
python3 -I -X dev -W error -B research/projection-parity-constants/verify.py
python3 -I -O -X dev -W error -B research/projection-parity-constants/verify.py
python3 -B scripts/check_research_commit.py --package research/projection-parity-constants --check-source-history
```

Expected markers are `PASS_PROJECTION_PARITY_CONSTANTS`,
`PASS_REGISTERED_RESEARCH_PACKAGE`, and `PASS_RESEARCH_COMMIT_BYTES`.
The retained receipt was produced by CPython 3.12.14; its Python-version field
will reflect the interpreter used. Normal and optimized runs have identical
output on that interpreter. The direct verifier also works in a Git-free
package export. The registered metadata runner needs Git history to check the
provenance pins.

## Sources, scope and overlap

Publication base: `1ec1119972c9aefe42525172d07b332fcff81cb4`, priority revision 7.
The proof and independent review were prepared at the earlier source snapshot
`ff3cc58e370d0f678e529246f8c73e8094e18fcf` and are preserved byte-for-byte.
The #5193 README and proof are unchanged at the publication base.
[SOURCES.json](SOURCES.json) pins the predecessor question, proof, exact-limit
proof, task catalogue and selected record as historical provenance. There are
no external executable inputs. [TASK.json](TASK.json) explicitly records the
changed scope from `independent-moment`: this is a user-selected arithmetic
side result, not completion of that paid-ledger card.

The investigation inspected the source question, nearby PRs and Discussion
handoffs; a final live `projection in:title` PR search again returned #5193 as
the newest relevant projection result. This is bounded overlap coverage, not
a global priority claim. Unpublished work and every historical reply were not
exhaustively checked.

No new kappa, selected-frontier improvement, supplier admission, hook-rank
certificate, physical caller, dirty-state restoration or full multiplication
theorem follows from this package. The optional triangle/max strengthening and
classification of all seeds are outside its scope.

## Open next questions

The structured questions and blockers are also in [TASK.json](TASK.json).

1. **Which seeds have monotone top ratios?** The parity constants give necessary
   tail inequalities. Start with the linear seed-to-mode map and adjacent
   differences; equality cases still need higher terms and finite-prefix control.
2. **Can finite mode coefficients simplify further?** Start by extracting
   coefficients of PROOF.md equation (7) for modes 1 through 4. A shorter
   elementary expression could ease exact evaluation; none is established here.
3. **Can the inherited hook-rank and physical-engine premises be verified?**
   Start with one source-bound #4628/#4643 hook-rank obligation. Those missing
   certificates and complete physical costs are independent blockers to any
   multiplication-bound interpretation.

## Credit

Prepared for NicholasStone with substantial OpenAI Codex assistance, including
a separate AI review agent. New text and code are Apache-2.0.

Jacob Alan Sussman [#4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628)
supplied the recurrence, seed and proposed engine interpretation; Maximilian
Lutz [#4643](https://github.com/CrocSwap/integer-mult-bounds/pull/4643) supplied
independent projection counts and recurrence audit; Nick Petalas #5151 proved
the exact limit; JoyboyBrian
[#5184](https://github.com/CrocSwap/integer-mult-bounds/pull/5184) proved strict
finite-block descent; Krzysztof Wojt #5193 supplied the four modes and sharp
geometric order. Eumemic #288, Swapnil Jain, and the retained certificate/engine
lineage retain their credit. Q-Gauss summation is classical.
