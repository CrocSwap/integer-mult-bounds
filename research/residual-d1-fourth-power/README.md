# D1^4 = I leaves the residual x1 monomial nonzero

**Scoped proof; no new κ.** The formal algebra of the published two-edge
feed imposes `Q^4 = C1^2 = C3^2 = I` and the inherited rule that `D_i`
conjugates only `C_i` by `Q^{-1}`. One physical relation omitted by that
algebra is the fresh-Gaussian equation `D1^4 = I`. In the quotient by
that single central equation, the residual word

```text
Q^{-1} C1 Q^2 C1 C3 D1 D3
```

keeps the representative with word `(-1, 2, 1, 1, 2, 3)` and degree
`(1, 1)`, coefficient 1. The comparison element `Q^{-1} C1` keeps the
distinct representative with word `(-1, 2)` and degree `(0, 0)`, and the
Q-letter parity character still sends that representative to `-1`.

[PROOF.md](PROOF.md) gives the coset reduction and an 8-dimensional
separating representation. The representation also satisfies `D3^4 = I`
and `(C1 C3)^3 = I`. Those two equations are extra relations of the
matrices. They are not part of the formal quotient.

The selected frontier is unchanged. This quotient is not an autonomous
caller. No multiplier is exhibited.

## Result

`research/coded-active-feedback` records that `D^4 = I` is a physical
source relation not imposed on its formal algebra. The stage-1 instance
of that law is `D1^4 = I`. In the predecessor algebra this element is
the empty word at degree `(4, 0)`, so the equation is not already true.

Multiplying the residual by `D1^4` only adds 4 to the D1 exponent. The
quotient therefore leaves the exponent-1 representative in place, with
coefficient 1. `D1^4 - I` itself reduces to zero, and `D1` does not.

The one-axis factor `A = [[a, b], [b, a]]` with `a = (1+i)/2` and
`b = (1-i)/2` satisfies `A^2 = X` and `A^4 = I` by exact arithmetic in
`Z[i]`. That is the matrix law named in the moving-stage tariff. The
native eight-axis word is not replayed.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/residual-d1-fourth-power --check-only
python3 -B scripts/research_package.py --package research/residual-d1-fourth-power
```

Direct replay:

```sh
python3 -I -W error -B research/residual-d1-fourth-power/verify.py
python3 -I -O -W error -B research/residual-d1-fourth-power/verify.py
```

The optimized command still executes the checks. They are `need`
failures, not assertions. No network, native build, or full multiplier
replay is used. The run prints `PASS_RESIDUAL_D1_FOURTH_POWER` and
`new_kappa null`.

## Scope

Original card: `joint-query-controller`. Scope status: **refined**. The
card asks for one source-bound caller identity, or an obstruction to
that change, together with its charges. This package does not change
the query demand. It takes open question 2 of the D-exponent-0 x1
obstruction, the question posed by
[PR #7033](https://github.com/CrocSwap/integer-mult-bounds/pull/7033)
and recorded in
[discussion comment 19513870](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19513870).
The first step named there is one source relation outside
`Q^4 = C1^2 = C3^2 = I` and the inherited D conjugation rule. The
relation used here is `D1^4 = I`.

Base commit: `17469fff78c22941280f04d39dc5a1faee09c840`. Pins are in
[SOURCES.json](SOURCES.json). The catalogue is provenance. The selected
record, `search.py`, `gauge.py`, and the three cited proofs are live
inputs. The selected conditional value is the selected record,
`781451/250000000`.

Overlap at this base used `scripts/find_overlap.py`. Local notes at
`17469fff78c22941280f04d39dc5a1faee09c840` (10178 paths, complete
inventory), 339 open-PR records fetched at 2026-11-10T10:19:05Z, and
7013 discussion records fetched at 2026-11-10T10:20:14Z. The phrase
`Q^{-1} C1 Q^2 C1 C3` matches PR #7033 and
[discussion comment 19513867](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19513867),
which ask this question. Requiring both `physical relation` and `D^4`,
and both `omitted` and `D^4=I`, matched nothing in that snapshot. The
search is not a novelty certificate. Closed PR bodies were outside the
open-PR snapshot.

## Open next questions

Does one linear source relation, compatible with
`Q^4 = C1^2 = C3^2 = I` and the inherited D conjugation rule, send the
coefficient word `Q^{-1} C1 Q^2 C1 C3` to zero while leaving
`Q^{-1} C1` nonzero? `D1^4 = I` meets this word only by adding multiples
of 4 to a D exponent that is already zero on the coefficient, so the
coset sum stays 1. A linear dependence among distinct degree-zero words
could behave differently. The first step is to evaluate
`C = diag(K_i)^{-1} F diag(K_i)` from
`research/native-involutive-dual/PROOF.md` on one shared central axis
and reduce this coefficient there. This package does not evaluate `F`.

If a later quotient does send the residual to zero and keeps
`Q^{-1} C1` nonzero, which owner-indexed multiplier on the four
published banks becomes the autonomous row `[A, 0, 0, 0]`? Killing the
monomial in a quotient is not yet a caller. The first step is to name
that quotient and recompute the four columns. No such quotient is
constructed here.

## Credit

The trace, algebra, and omitted-relation sentence are Cinna Davis's
`research/coded-active-feedback`, using Dugongue's PR4948 chronology,
Dillon's PR4933 code, and the gauge engine in
`research/coded-native-caller/gauge.py`. The normalized one-axis law
`D^2 = X`, `D^4 = I` is Nick Petalas's
`research/moving-stage-restoration-tariff`. The residual monomial and
the question are the open remainder of the D-exponent-0 x1 obstruction.
The nonzero D-exponent multiplier question from that obstruction is a
separate question and is not answered here.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.
