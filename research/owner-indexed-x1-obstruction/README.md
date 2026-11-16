# No owner index clears the three-term x1 block

**Scoped proof; no new κ.** On the published two-edge feed, every
owner-indexed D-exponent-0 left map of the four final banks that keeps
`x0 = D1 Q^{-1}` has x1 coefficient

```text
(const - m0 C1) D1 + (1 - m0 x) Q^{-1} C3 D1 D3.
```

The second summand is never zero, so the x1 column is never the zero
element. Keeping y0 zero fixes `m1` and does not cancel that summand. The
four stored endpoint banks are not overwritten. The autonomous row would
be `[A, 0, 0, 0]`. Removing the three published keys still leaves one
monomial, so that row is not reached.

Exactly one index also clears the `D1` line. It keeps y0 zero and leaves
the single monomial `Q^{-1} C1 Q^2 C1 C3 D1 D3`. That image is not a
clearance of the three-term block. [PROOF.md](PROOF.md) gives the products
and the parity character.

The selected frontier is unchanged. This does not rerun the y0 defect,
the declared alternating-family lock, or a feedback-edge test.

## Result

The predecessor replay stores `A = D1 Q^{-1}` on final bank 2 together
with the published three-term x1 block, and stores a pure y0 monomial on
final bank 1. For each D-exponent-0 element `m0`, the other coefficients
that keep `x0 = A` and clear y0 are uniquely

```text
m3 = 0,  m2 = 1 - m0 x,  m1 = const - m0 C1.
```

Here

```text
x = Q^2 (I + Q) C1 Q,  const = Q^{-1}(C1 Q C1 - I).
```

The element `I + Q` is sent to zero by the Q-letter parity character,
while `Q^{-1} C1` is sent to `-1`. That forbids `m0 x = 1`, so the
`D1 D3` summand cannot vanish.

The sharp index `m0 = const C1` uses the two monomials
`-Q^{-1} C1 + Q^{-1} C1 Q` and the one monomial
`m2 = Q^{-1} C1 Q^2 C1 Q`. Its fresh image has x0 block `A`, y0 block 0,
y1 block 0, and x1 block the single monomial above. This is an identity
in the predecessor's algebra, not a search over a bounded ansatz.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/owner-indexed-x1-obstruction --check-only
python3 -B scripts/research_package.py --package research/owner-indexed-x1-obstruction
```

Direct replay:

```sh
python3 -I -W error -B research/owner-indexed-x1-obstruction/verify.py
python3 -I -O -W error -B research/owner-indexed-x1-obstruction/verify.py
```

The optimized command still executes the checks. They are `need` failures,
not assertions. No network, native build, or full multiplier replay is used.

## Scope

Original card: `joint-query-controller`. Scope status: **refined**. The
card asks for one source-bound caller identity, or an obstruction to that
change, together with its charges. This package does not change the query
demand. It takes the x1-column question in
[research/owner-indexed-y0-clearance](../owner-indexed-y0-clearance/README.md),
which is the remainder of handoff
[discussion comment 19138525](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19138525)
after that package cleared y0 and left the published x1 coefficient in
place.

Base commit: `17469fff78c22941280f04d39dc5a1faee09c840`. Pins are in
[SOURCES.json](SOURCES.json). The catalogue and selected record are
provenance. `search.py` and `gauge.py` are live inputs. The selected
conditional value is the selected record, `781451/250000000`.

Overlap at this base used `scripts/find_overlap.py` against a snapshot
fetched on 2026-11-10: local notes at
`17469fff78c22941280f04d39dc5a1faee09c840` (10178 paths, complete
inventory), 317 open-PR records at 08:49:48Z, and 6971 discussion records
at 08:50:49Z. Requiring both phrases `three-term x1` and `owner-indexed`
matches the predecessor package and
[discussion reply 19507118](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19507118),
which ask this question, and no open PR. That search is not a novelty
certificate. Closed PR bodies were not part of that snapshot.

## Open next questions

Can one owner-indexed multiplier whose D exponent is not zero cancel
`Q^{-1} C1 Q^2 C1 C3 D1 D3` while keeping `x0 = D1 Q^{-1}`, keeping y0
zero, and leaving the four final banks stored? The argument here separates
the `D1` and `D1 D3` lines only for a D-exponent-0 factor. The first step
is to add one term of D exponent `(0,-1)` to the sharp index above and
recompute the four columns. This package does not solve that term.

Does one physical relation omitted by this formal algebra send the
residual word `Q^{-1} C1 Q^2 C1 C3` to zero without collapsing
`Q^{-1} C1`? Nonvanishing is an identity in the predecessor's sufficient
algebra, not a faithful physical impossibility. The first step is to name
one source relation outside `Q^4 = C1^2 = C3^2 = I` and the inherited D
conjugation rule, then reduce only that word. No such relation is imposed
here.

## Credit

The trace, algebra, and published row are Cinna Davis's
`research/coded-active-feedback`, using Dugongue's PR4948 chronology,
Dillon's PR4933 code, and the passive ceiling packaged by Chris R /
Clear1nsight. The y0 defect and the constant-index charge are
`research/owner-indexed-y0-clearance`. The declared-family obstruction is
`research/active-feedback-coupling-lock`. The one-edge `C1 Q` row is
`research/active-feedback-outside-edge`. The gauge engine remains the
inherited `research/coded-native-caller/gauge.py`.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.
