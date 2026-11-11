# A D-exponent (0,-1) correction leaves the sharp x1 residual

**Scoped proof; no new κ.** On the published two-edge feed, start from the
sharp owner index of open PR #7033 and add arbitrary D-exponent-0
coefficients times `D3^{-1}` on the four final banks. The fresh x1 column
still contains

```text
Q^{-1} C1 Q^2 C1 C3 D1 D3
```

with coefficient 1. The four stored endpoint banks are not overwritten.
Keeping `x0 = D1 Q^{-1}` and y0 zero forces the coefficients

```text
u1 = -u0 C1,  u2 = -u0 x,  u3 = 0,
```

with `u0` an arbitrary D-exponent-0 element and `x = Q^2 (I + Q) C1 Q`.
The x1 column is then the residual monomial plus `u0` times a fixed
three-monomial defect. [PROOF.md](PROOF.md) gives the transports and the
products.

One bank is included: the gate column of that bank is a monomial unit, so
the coefficient must be zero, and the sharp residual remains. The same
gate blocks one homogeneous term of every other D exponent on one bank.
It does not block two banks at an exponent other than `(0,-1)`.

The selected frontier is unchanged. This does not rerun the D-exponent-0
obstruction, the y0 defect, or the one-edge `C1 Q` row.

## Result

The sharp image has `x0 = A = Q^{-1} D1`, y0 zero, y1 zero, and x1 equal
to the one monomial above. Left multiplication by `D3^{-1}` moves every
bank-x1 degree off `(1,1)`. A D-exponent-0 factor preserves degree, so no
choice of the four coefficients deletes that monomial.

The witness `u0 = I` uses four new multiplier monomials

```text
D3^{-1},  -C1 D3^{-1},  -Q^{-1} C1 Q D3^{-1},  -Q^2 C1 Q D3^{-1}
```

on banks 0, 1, and 2. Its x1 column is the residual plus

```text
-C1 D1 D3^{-1}
- Q^{-1} C1 Q C3 Q^{-1} D1
- Q^2 C1 Q C3 Q^{-1} D1.
```

Those monomials are the algebraic charge of this near-miss. They do not
clear the block. No scalar-field minimum and no tape cost are claimed.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/owner-indexed-d3-inverse-term --check-only
python3 -B scripts/research_package.py --package research/owner-indexed-d3-inverse-term
```

Direct replay:

```sh
python3 -I -W error -B research/owner-indexed-d3-inverse-term/verify.py
python3 -I -O -W error -B research/owner-indexed-d3-inverse-term/verify.py
```

The optimized command still executes the checks. They are `need` failures,
not assertions. No network, native build, or full multiplier replay is used.

## Scope

Original card: `joint-query-controller`. Scope status: **refined**. The
card asks for one source-bound caller identity, or an obstruction to that
change, together with its charges. This package does not change the query
demand. It takes the first open question of
[research/owner-indexed-x1-obstruction](https://github.com/CrocSwap/integer-mult-bounds/pull/7033):
add one term of D exponent `(0,-1)` to the sharp index and recompute the
four columns. The multi-bank family of that same exponent is the same
degree count, not a second exponent.

Base commit: `17469fff78c22941280f04d39dc5a1faee09c840`. Pins are in
[SOURCES.json](SOURCES.json). The catalogue is provenance. The selected
record, `search.py`, and `gauge.py` are live inputs. The verifier rejects
a moved κ. The selected conditional value is the selected record,
`781451/250000000`.

Overlap before this package was added, at base
`17469fff78c22941280f04d39dc5a1faee09c840`: `scripts/find_overlap.py
--refresh --all-terms` searched the complete local note inventory (10178
paths) and a snapshot of 339 open PR records fetched at 2026-11-10T10:15:04Z
plus 7013 discussion records fetched at 2026-11-10T10:16:06Z. Both phrases
`D exponent (0,-1)` and `owner-indexed` match only
[discussion reply 19513867](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19513867),
which asks this question and does not answer it. Open PR #7033 states the
same question with the exponent in backticks, so that literal pair misses
its body; the PR was read directly. That search is not a novelty
certificate. Closed PR bodies were outside the snapshot.

## Open next questions

Can a D-exponent `(0,1)` correction of the same sharp index, using two or
more banks, make the fresh x1 column zero while keeping `x0 = D1 Q^{-1}`
and y0 zero? Exponent `(0,-1)` never meets the residual degree. One
homogeneous term on one bank is already blocked for every degree by the
monomial gate. The coefficient shape `u1 = -u0 C1`, `u2 = -u0 x`,
`u3 = 0` still keeps the boundary at `D3`, and for `u0 = I` the
degree-`(1,1)` line properly contains the residual, so that positive
power is not the calculation above. The first step is to decide whether
any D-exponent-0 `u0` makes `R + u0 Δ_+` the zero element, where `Δ_+`
is the defect of that positive power, and to charge every monomial of a
solution. No such `u0` is solved here. The omitted-physical-relation
question of PR #7033 is a separate remainder and is not taken here.

## Credit

The trace, algebra, and published row are Cinna Davis's
`research/coded-active-feedback`, using Dugongue's PR4948 chronology,
Dillon's PR4933 code, and the passive ceiling packaged by Chris R /
Clear1nsight. The y0 defect is `research/owner-indexed-y0-clearance`.
The sharp index and the residual monomial are open PR #7033,
`research/owner-indexed-x1-obstruction`, head
`bc08ea6b28c345b0164ff1631642974719da087a`. The declared-family obstruction
is `research/active-feedback-coupling-lock`. The one-edge `C1 Q` row is
`research/active-feedback-outside-edge`. The gauge engine remains the
inherited `research/coded-native-caller/gauge.py`.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.
