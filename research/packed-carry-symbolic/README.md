# Symbolic all-radix certificate for the packed-bit carry table

**Independent verification of a scoped identity; no new kappa.** This package
certifies the complete matching-prefix transition table used in Hanson Sun
(@bbMisk)'s [PR1245](https://github.com/CrocSwap/integer-mult-bounds/pull/1245),
head `44bf3b1d6031e4069f5abe26211f15e52293e1f4`, for **every even integer
radix B >= 4**. Its mathematical result agrees with that predecessor. The new
contribution is a source-bound, finite **symbolic certificate** whose exact
linear inequalities imply the unbounded-radix claim. It neither imports the
predecessor checker nor relies on interpolation or a large-radix cutoff.

PR1245 already provides a written quantified proof, normalized parity tests,
a finite radix sweep and full-word tests. This is an independent mechanization
of the intermediate carry-boundary argument, not discovery of its table or
source-pattern law. It also applies to even non-powers of two as a local digit
identity; the packed binary caller still uses B=2^K, K>=6.

## Result

Carry-state bit i means the signed carry of gate i+1 is present. Starting from
state zero, every matching prefix has state in `{0,5,10,80,160}`. For any one
nonzero state E, the number of dirty digit pairs `(u,w)` out of B^2 is:

| Source bit | Incoming | Outgoing matching state | Count |
|---|---|---|---:|
| 0 | 0 | 0 | B^2 |
| 0 | E | 0 | B(B-1) |
| 0 | E | E | B |
| 1 | 0 | 0 | B(B-2) |
| 1 | 0 | each E | B/2 |
| 1 | E | any | 0 |

All omitted matching counts vanish. The checker proves closure, disagreement
on every excluded cell, exact polynomial counts, and signed suffix-carry
cancellation. See [PROOF.md](PROOF.md) for the finite-certificate soundness
argument and the inherited source-pattern corollary.

## Reproduce and inspect

From the repository root, standard library and Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/packed-carry-symbolic
```

Expected: `PASS_SYMBOLIC_PACKED_CARRY cells=360 all_even_B>=4 no_new_kappa`,
six passing package tests, and `PASS_REGISTERED_RESEARCH_PACKAGE`.
A standalone offline replay is also available:

```sh
python3 -I -O -B research/packed-carry-symbolic/verify.py
```

The 360 rows in [CERTIFICATE.json](CERTIFICATE.json) cover five incoming
states, two source bits, four parity pairs and nine guard-region pairs.
Every row supplies only quotient witnesses. The checker independently
reconstructs its unwrapped trajectory from the **literal manuscript equation**,
then checks 12,960 affine inequalities and 2,880 signed carry transitions.
It totals the cell sizes as polynomials in N=B/2 and compares all ten rows
with the claimed table. It checks strict mismatch rather than accepting an
unclassified outcome. Empty middle cells at N=2 have zero polynomial weight.

[EXPECTED.json](EXPECTED.json) also records 25,088 complete small word states
against the unchanged whole-word simulator. That finite source-binding check
is separate from the universal local proof. Seven certificate/gate mutations
must fail; an odd-radix counterexample and a target-only false agreement show
why even radix and restoration of the dirty coordinate are necessary.
`test_package.py` checks source/receipt corruption, missing inputs, optimized
read-only relocation and the exact rejection of a finite-sample-only inequality.

To regenerate, run `verify.py --write NEW_RECEIPT.json`; it refuses to replace
an existing file. `--generate` regenerates the symbolic witness only when
`CERTIFICATE.json` is absent. The generator samples N=4 **only to propose
quotients**; every proposed quotient must then pass the universal inequalities.
Changing this sample cannot weaken the verifier.

## Scope, assumptions and accounting

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. [SOURCES.json](SOURCES.json)
pins every live input by SHA256 and Git blob, records the predecessor head and
README digest, and preserves the selected record as historical provenance.
The selected certificate routes to `community-batch1099-review.md` and the
actual `complex-t16-rare-pattern-exchanges` construction, with conditional
kappa `836330098538459/500000000000000000`. Those files are unchanged.

The symbolic proof trusts ordinary Python integer arithmetic, the small
checker, the partition lemma proved in PROOF.md and the source transcription
parser. It is not Lean or a full theorem-prover result. No predecessor
implementation is imported; the retained whole-word simulator is deliberately
used only as a separately identified source-binding oracle. Both the new
checker and written proof were AI-assisted; no independent human review is
claimed.

This certificate discharges one local digit implication. Complete dirty fields,
low-to-high carry interpretation, unchanged source bits and the original
eight-gate chronology are required for the global fiber corollary. Arbitrary
restricted y/z fibers and source/dirty correlations are excluded. No new
physical layout, rounding rule, correction implementation, native supplier,
recursive invoice or exponent follows. All rotations, source reads, swaps,
scans, record motion, sorting, correction and restoration retain their
predecessor prices. Full selected cold replay, native compilation, hosted CI
and all-size physical admission are unrun and unclaimed.

## Open next questions

An independently admissible source-restricted caller remains needed before a
fiber-dependent density can alter an actual paid bill. A useful first step is
to name one concrete caller and prove that its splitting preserves complete
y/z fibers and the source law while charging every movement and correction.
No such caller is provided here. Separately, this small affine-certificate
kernel could be translated into a proof assistant; the first step is a formal
lemma that endpoint affine inequalities certify all cells for N>=2. This is
blocked by implementation/review time, not by a missing mathematical premise.
Structured questions are in [TASK.json](TASK.json).

## Credit and overlap

Prepared for **Philipp (@mightyOil)** with substantial **OpenAI Codex GPT-6
Astra** assistance in derivation, implementation, verification and writing.
New work is Apache-2.0. Credit Hanson Sun / bbMisk PR1245 for the fixed-source
law and transition statement; Precious / Kyu PR773
`dbd9da3eed9a0045b77de861099e869259f1ad13` for the matching-prefix states and
complete-rectangle method; Aryan Sudhir PR735
`8d36139e49add1e55795e283b3bfa45e1cfe1bf0` for the guard-envelope distinction;
and OpenAI's retained manuscript / finite-identity source for the eight gates.
Upstream license and source notices remain untouched. No priority over these
predecessors is claimed.

OS assignment seed **79**, independent-verification track. Candidate reviews
also considered PR1220's dyadic-forest census and PR1235's endpoint tours; both
already have broad independent replay evidence. The narrower carry-boundary
certificate was chosen to add a distinct proof method. Live PR bodies and
all Discussion claim pages were checked before the claim, and again before
submission; search absence does not certify novelty. The seed determines the
track and this choice of proof obligation, not mathematical randomness.
