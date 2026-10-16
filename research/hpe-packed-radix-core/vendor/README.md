# A kernel-checked integer energy core for the HPE radix question

For a finite list of Gaussian integers, a circuit in the explicit stage grammar
of `Energy.lean` with k unnormalized C stages satisfies

`energy(output) = 4^k * energy(input)`.

For a basis input, each real and imaginary output coefficient has square at
most `4^k`. Eight named theorem roots compile on **Lean 4.34.1 core**, with only
`propext`, `Classical.choice` and `Quot.sound`. Four deliberately false theorem
variants fail. This supplies a formal energy lemma requested by
[PR1859](https://github.com/CrocSwap/integer-mult-bounds/pull/1859), whose smaller
packed radix previously had a written unitary argument and finite tests.

This is a standalone formal lemma plus an external finite source binding.
It does **not** connect inside Lean to the retained Lean 4.21/Mathlib `gz`,
`runZ` or `vec_digits`, prove a new packed-comparison theorem, replace the
existing checker, or establish a supplier, runtime improvement or new kappa.

## Exact grammar and hypotheses

Energy is the sum of `a*a+b*b` over coordinates `(a,b)`. The formal relation has:

- arbitrary genuine list permutations;
- coordinatewise powers of i, including varying diagonal phases;
- a C stage after permutation into fixed points and disjoint pairs, followed
  by another genuine permutation. Every input coordinate is covered once.

At a fixed point, the unnormalized C formula doubles its coordinate. On a
two-cycle, both outputs use the same Boolean sign and the literal integer
formula from `HyperplaneEnd.Clifford.cgz`. The pair energy is four times the
input pair energy. Structural induction proves the full-stage result;
chronological circuit induction proves the exponent law. Nonnegative squares
then give the member-coordinate bound. These theorems hold for arbitrary
Gaussian integer inputs and arbitrary finite lengths, including empty lists,
fixed points and either C sign. The grammar permits more permutations than the
XOR source gate requires; its theorem is deliberately stated at that level.

`Run` counts a complete C stage once. It does not count individual two-cycles
as separate full-vector C stages. The proof does not assume that helpers are
zero, that coordinates can be dropped, or that different output signs are free.

## External correspondence and finite evidence

`verify.py` reads the six retained literal circuits `lhsLit1..3/rhsLit1..3`.
It reuses PR1859's compiler/executor and the earlier closed literal parser as
comparison subjects, then independently decomposes each involution into its
fixed points/two-cycles and implements the stage grammar. All 512 real basis
columns at every stage agree exactly, with exact energy checks. A dense signed
Gaussian vector additionally exercises each stage. Complex linearity of both
specified integer formulas extends real-basis agreement to Gaussian inputs;
this explanation is not an internal Lean source-equivalence theorem.

The exact counts and six C-stage counts are in `RESULT.json`. Eight controls
reject a noninvolution, duplicate/omitted/out-of-range coordinates,
nonbijective pullback, missing phase entry, inconsistent pair signs and
undoubled fixed points. The last two are actual energy counterexamples.

This is not advertised as a new independent implementation of the whole
Clifford algebra. Reusing the retained parser/compiler is explicit; source
hashes and Git blobs bind every imported input in `SOURCES.json`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -I -B scripts/research_package.py --package research/hpe-clifford-energy-core
python3.12 -I -O -B research/hpe-clifford-energy-core/verify.py
python3.12 -I -B research/hpe-clifford-energy-core/check_lean.py --lean /path/to/lean-4.34.1/bin/lean
```

The generic registered replay checks the finite binding and pins. The separate
Lean command checks all eight named axiom reports and four rejected false
statements in a fresh temporary directory. It needs only the official Lean
4.34.1 core installation, commit `5045d0056413266e57c625dcd7c365b10e377c52`;
there is no Mathlib download or retained HPE build. Windows may need TEMP/TMP
pointed at a writable workspace. Local kernel and finite checks passed;
hosted CI, the selected cold replay and human peer review are not claimed.

## Open next questions

Connect this integer stage relation to the retained `gz/runZ` definitions
inside Lean: first prove the finite involution cycle partition covers `Fin512`
exactly once, then transport the energy identity. After bridging toolchain and
source semantics, derive the absolute entry bound and feed it into
`vec_digits` with the smaller radix. Until that is done, the existing broader
checker remains the proven admission route. See `TASK.json` for the structured
question and stopping boundary.

## Provenance and credit

Base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision4, picker
nonce `e50020977d372da774664ddea9ba43d9`, refined `formal-interface-lemma`.
The initial snapshot covered683 open PRs with Discussion API rate limiting.
The final refresh recovered complete pagination:695 open PRs at12:45:17UTC
and1202 Discussion records at12:48:30UTC on2026-10-15. Visible #1163/#1166
pages were also read through Curiosity Bot. The targeted search found no
matching competing scope; metadata coverage is not a novelty certificate.

Jeremy Kothe/jeremykothe2's PR593 supplies the original Clifford formulas and
packed proof; woklerx's PR1859 supplies the stronger-premise radix question;
commdata2338 supplies the retained semantic-binding parser. The Lemma A/G and
construction lineage retain their notices. Prepared for **ywz65** with
substantial **OpenAI Codex assistance** in proof, implementation, checks and
writing. Apache-2.0. Automated review is not human peer review.
