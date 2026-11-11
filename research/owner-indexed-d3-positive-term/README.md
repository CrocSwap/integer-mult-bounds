# No D-exponent (0, 1) correction clears the sharp x1 column

**Scoped proof; no new κ.** Question from open PR #7052: can a
D-exponent (0, 1) correction of the same sharp index, using two or more
banks, make the fresh x1 column zero while keeping x0 = D1 Q^{-1} and y0
zero? No. On the published two-edge feed, no such correction exists in
the formal algebra. In particular, no D-exponent `(0, 1)` correction of
the sharp owner index keeps `x0 = D1 Q^{-1}` and y0 zero while making the
fresh x1 column the zero element. The corrections that keep the boundary are exactly

```text
u1 = -u0 C1,  u2 = -u0 x,  u3 = 0,
```

for a D-exponent-0 element `u0`, and `R + u0 Δ_+` never vanishes.
[PROOF.md](PROOF.md) gives the degree split and the two witnesses.

The selected frontier is unchanged. This does not redo the D-exponent-0
obstruction, the D-exponent `(0, -1)` obstruction, or the y0 defect.

## Result

Evidence class: a proof in the predecessor's rational group algebra.
The coefficient `u0` is an arbitrary finite-support element. The
syllable-length-4 replay is a control for the free right `Q` action, not
a census. A failed search is not the argument.

The sharp image has `x1 = R = Q^{-1} C1 Q^2 C1 C3 D1 D3`. Left
multiplication by `D3` meets that degree. The boundary forces the closed
form above, and then

```text
Δ_+ = -C1
      - (Q^{-1} + Q^2) C1 (Q^{-1} C3 Q),
```

at degrees `(1, 1)` and `(1, 2)`. Degree `(1, 1)` vanishes for exactly
one element, `u_* = Q^{-1} C1 Q^2 C1 C3 C1`. That monomial does not kill
degree `(1, 2)`. Every other `u0` leaves `R` with a nonzero coefficient
on that line.

The right kernel of `x` is the right kernel of `I + Q`. Every nonzero
anti-invariant therefore gives a genuine two-bank correction, on banks 0
and 1 only. The witness `σ = I - Q + Q^2 - Q^3` charges eight multiplier
monomials and leaves five image monomials at degree `(1, 1)`, including
`R` with coefficient 1. The three-bank near-miss `u_*` charges four
multiplier monomials and leaves two image monomials at degree `(1, 2)`.
No scalar-field minimum and no tape cost are claimed. The four stored
banks are only read.

The same raw-column supports show that every integer power other than
`0` and `1` misses degree `(1, 1)` for every coefficient tuple. The case
`-1` is the support gap already proved in open PR #7052; its boundary
analysis is not repeated. No sum of two boundary-preserving single-power
corrections clears x1 either. A second power meets the near-miss leftover
only at exponent 2, and that defect's degree-`(1, 3)` kernel consists of
anti-invariants, whose support size is divisible by 4, while the leftover
has support size 2.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/owner-indexed-d3-positive-term --check-only
python3 -B scripts/research_package.py --package research/owner-indexed-d3-positive-term
```

Direct replay:

```sh
python3 -I -W error -B research/owner-indexed-d3-positive-term/verify.py
python3 -I -O -W error -B research/owner-indexed-d3-positive-term/verify.py
```

The optimized command still executes the checks. They are `need` failures,
not assertions. No network, native build, or full multiplier replay is used.

## Scope

Original card: `joint-query-controller`. Scope status: **refined**. The
card asks for one source-bound caller identity. This package answers the
D-exponent `(0, 1)` question in open PR #7052, including every
finite-support coefficient and the two-bank kernel. It does not change
the query demand.

Base commit: `e54523517d0f03e58352e647c403a5af3e525a57`. Pins are in
[SOURCES.json](SOURCES.json). The catalogue and selected record are
provenance. `search.py` and `gauge.py` are live inputs. The selected
conditional value is the selected record,
`363005817/100000000000`. The revision-8 priority note still quotes an
older checkpoint. This package does not change the frontier.

Open PR #7052, head `00b08c5ae3a0f8a3645773978c5a557684e29e91`, is not
imported. The replay below recomputes the sharp image and the published
`(0, -1)` defect from the merged feed. Overlap on 2026-11-11: a GitHub
search for `D-exponent (0, 1)` returned #7052, #7033, and unrelated
#3449; #7052 asks this question and does not solve `u0`. Open titles
containing `D-exponent` are #7033, #7052, #7056, and the unrelated
cyclotomic note #7195. No discussion hit the same phrase. The search is
not a novelty certificate. Closed PR bodies were outside the title scan
except where the phrase search included them.

## Open next questions

Can coefficients at two distinct nonzero powers of `D3`, not required to
preserve the boundary separately, keep `x0 = D1 Q^{-1}` and y0 zero and
make the fresh x1 column zero? Every single nonzero power is settled, and
so is every sum of two boundary-preserving single-power corrections. Power
1 puts bank 3 at degree `(1, 2)`, where power 2 puts banks 0 and 2, so a
coupled pair can still cancel. The first step is the pair of powers
`(1, 2)`: write the x0 and y0 equations at degrees `(1, 1)`, `(1, 2)`, and
`(1, 3)`. The degree-`(1, 1)` part of x1 still comes only from the power-1
coefficients on banks 0 and 2. This package forces bank 3 to vanish only
when a single power is present.

## Credit

The trace, algebra, and published row are Cinna Davis's
`research/coded-active-feedback`, using Dugongue's PR4948 chronology,
Dillon's PR4933 code, and the passive ceiling packaged by Chris R /
Clear1nsight. The y0 defect is `research/owner-indexed-y0-clearance`.
The sharp index and the residual monomial are open PR #7033. The
D-exponent `(0, -1)` obstruction, the monomial gate, and the question
answered here are open PR #7052. The gauge engine remains
`research/coded-native-caller/gauge.py`.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.

## Workflow feedback (optional)

The registered package checker accepted the scoped proof without a
separate session report. One link is enough:
https://github.com/CrocSwap/integer-mult-bounds/discussions/1200
