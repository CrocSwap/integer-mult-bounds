# The p=19 word without the code: trace-certified word, exact price, kappa 0.0034

**The p=19 controller word is emitted as the controller's own gate trace and
re-priced. The invoice never sees the code — `invoice(p, pattern, thick, profile)`
takes no coding argument — so the coded reverse was an overlay the endpoint does not
need, and dropping it removes the terminal-gauge decoder that the coded words cannot
pay for. Complex side 0.007578535, BIT supplier 0.0034, outer
`kappa = 951999/280000000 = 0.0033999964`: **+12.58 %** over the selected repository
record `60403/20000000 = 0.00302015` and **+12.31 %** over the maintainer-reported
`0.00302728823` (reported in review; no certificate for it in this tree), with zero
recodings and zero decoder.

The endpoint is **conditional**: the 7,752 helper units are inherited rather than
replayed, the compiler result is a numerical instantiation of the majorant under an
applicability premise, and the word is certified as the controller's operator rather
than by a physical bank replay.**

## Why there is no code

The retained native reverse call is atomic, `X ← D(X − QCY)`, `Y ← DY`
(`coded-native-caller/PHYSICAL.md`), so its letter is `D` while `[C,D] ≠ 0` and
`[C,Q] ≠ 0`. A role that carries the code through a stage therefore leaves the
terminal gauge `Q⁻¹BᵢQ`, one `Q` decoder per owner per thick stage: **2,128 rank-1
units at p=19**, against a root budget of **1,103 units** (this receipt computes both;
1,104 extra rank-1 units drop the root to 0.0034). The alternative — code fewer
stages — does not exist: every proper subset of coded pairs fails the
diagonalisation at p=3, 4 and 5, so the code is all-or-nothing and always costs
`112·p`.

Nothing forces that overlay. `invoice()` prices a word by its rank census (the T
targets and the D paid reads), and the census is independent of the coding, so the
word without the code keeps the identical root 0.007578535 while its field bill
collapses to zero recodings.

## The word, without hand transcription

A prior audit showed that a hand-written `standard()` reference can drift from the
controller it is meant to mirror. This package therefore does not transcribe: the
controller's own loop is re-executed with a gate log, and the log is replayed in the
controller's monomial algebra. The replay must reproduce `controller()`'s matrix
**exactly**, and the word must diagonalise.

`p19_plain.py` checks, for p = 2, 3 and 19:

- the trace identity: replayed trace == `controller(p, keep_of(p, pat), all-ones)`;
- the diagonalisation: `diagonalize(p, pat, all-ones)` returns the standard outputs
  with denominators `[1]`;
- the census at p=19: 20 forward stages, 19 reverse stages, **39 stage letters** (the controller applies the stage gate at every stage 0..2p), 36 retained idle calls, 108 bridges and 19 closing swaps = **241 gates**, with zero recodings (the idles are the
  controller's own, 198 rank across 396 role-rank).

## The price and the paid accounting

| item | value |
|---|---|
| invoice root | 0.007578535 (reproduced from the p16 published root) |
| ambient target rank | 153 |
| recodings / field maps / adds / clears | **0 / 0 / 0 / 0** |
| terminal-gauge decoder | **0** |
| guards at the endpoint | alpha 0.99579414, gamma 0.963763, delta 0.951561 |
| compiler | shape-correct majorant: H0 = 5,170,423,668,736, H1 = 49,224,448,837,637,726,209 |
| compiler premises | `20⁶⁴ < 21⁶³` ✓, `max target rank 153 < 256` ✓ |
| BIT | atom 0.004 > ordinary 0.0034363538 > admitted 0.0034 |
| ledger | 54 strict + 4 functional predicates positive at kappa; at exactly 0.0034 only `actual_bit_above_effective` fails |

The compiler constants matter and were wrong in an earlier draft: the p7 pair
(`h = 1/7`, `B = (4+7h)v`, `H0 ≥ 7v`) needs `10 < 2⁴` and `121 < 2⁷`, which fail here
(`20 < 2⁴`, `153 < 2⁷` and `20⁷ < 21⁶` are all false). The constants used here are
the ones `research/query-thinned-controllers/verify.py::tail` derives for exactly this
complex shape (`h = 1/64`, `B = (5+8h)v`, `debt = 1 + 8v(1−z₀)`, `H0 ≥ 8v`).

## What this package corrected

- the code is unnecessary: the invoice is code-blind, so the coded overlay only adds
  the decoder;
- the compiler constants of the p7 unit do not apply to a unit that splits at 20,
  completes at 21 and has ambient rank 153;
- an idle call is `term(0, sel)`, a product of stage letters, so its physical form is a
  Gaussian power and it needs no recoding;
- the closing swap carries the −1 sign and must sit after any gauge unload.

## Physical binding: the lifting lemma

The p=19 word needs 2^153 addresses, so it cannot be replayed literally. The binding is
therefore proved rather than sampled. The controller's word is a polynomial in the
retained stage variables plus one central variable; give stage `s` its own eight-axis
block and give the word one shared centre axis, and every monomial becomes an operator
on 2^(8k+1) addresses. That map `Φ` is a **ring homomorphism**: distinct-axis Gaussians
commute, powers on one axis add, and `Φ` fixes the identity. Hence any polynomial
identity between the gate list and the controller matrix lifts to address operators for
every block count `k`, and the p=19 word realises the p=19 controller matrix by
construction (`p19_lift.py`, receipt `P19_LIFT.json`).

The p=2 address replay (`p19_bank.py`) is then a **control on the implementation**, not
the proof: two blocks plus the shared centre, 2^17 addresses per role, four roles, twenty
gates, one dense seed. It is randomised, not exhaustive, and is labelled as such.

The lemma also caught a real bug: the selection bits of a monomial are **exponents**,
and an implementation that applies one gate per selected stage is not multiplicative once
an exponent reaches 2 — which the p=19 word does constantly.

## The tail limit is settled

δ = 0.9515606085 and γ = 0.963763. The source tail argument uses its limits only through
"each bound to the power 128 is below 1/16", and it closes at `L = 97/100`:
`0.97¹²⁸ = 0.0202666 < 1/16`, `0.97¹⁰²⁴ < 2⁻³²`, then `1/(1+1024·10⁻⁹) + 4·2⁻³² < 1`.
γ additionally meets the source's own tighter `31/32 = 0.96875`. So the `19/20` guard
written into the source certificates is a stronger choice this word does not need, and
the independent review on the earlier draft reached the same conclusion.

## Inherited interfaces, and what is discharged here

The word is new; the producer and the compiler are not. Every obligation is either
discharged against this word or consumed from an inherited interface unchanged.

| obligation | status |
|---|---|
| word realises the controller matrix | **discharged** — lifting lemma, plus the p=2 address control |
| rank completion below `b^v` | **discharged** — this census has `max target rank 153 < 256` |
| splitting at `c^v` | **discharged** — `20⁶⁴ < 21⁶³` |
| whole-job normalizers | inherited; the word adds no job and consumes the same T/D interface |
| distinct-owner child allocation | inherited; the word introduces no new owner |
| rank-one surplus retention | inherited; the census is unchanged by the word |
| helper fields disjoint from the word | **discharged mechanically** — the trace's roles are exactly `0…2p−1`, so no gate reads or writes helper-owned state |
| 7,752 helper units materialised | **not built here**; inherited from PR4929 with its ownership and ABI |
| field-bill admission under the caller ABI | inherited; the word's only paid operations are the inherited ones |
| precision, tape, hosting, hosted CI, kernel review | inherited external obligations |

## Open next questions

- Can the block-decomposed replay be made exhaustive rather than randomised, e.g. by
  comparing the two operators on a spanning set of the 2^17 address space?
- Does one materialised helper stage-unit agree with the inherited profile, closing the
  last helper obligation?
- Is the endpoint's `0.97` tail limit worth pushing into the source package so later
  words can cite it instead of re-deriving it?

## Reproduce

```sh
python3 -B research/coded-reverse-word-p19/p19_plain.py     # trace identity, diagonalisation, price
python3 -B research/coded-reverse-word-p19/p19_claim.py     # invoice, guards, compiler, BIT, budgets, ledger
python3 -B research/coded-reverse-word-p19/verify.py        # fast receipt
python3 -B research/coded-reverse-word-p19/p19_word.py      # the coded overlay, kept as a record
```

## Credit

PR4940 coded reverse controller: Cayden Burkart / SethBurkart123. PR4933 signed
physical code: Dillon. PR4929 center-free producer: Dugongue / mdumitrean. PR4433 and
PR4359 compiler and outer ledger: retained with attribution. PR4470 controller and
query thinning: Cinna Davis / 1337isnot1337. Retained lineage as credited in those
packages.
