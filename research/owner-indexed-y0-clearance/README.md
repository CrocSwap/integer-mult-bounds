# Owner-indexed reading clears y0 and keeps x0

**Scoped identity and field ledger; no new κ.** On the published two-edge
feed, every owner-indexed D-exponent-0 left map of the four final banks
that keeps `x0 = D1 Q^{-1}` and clears y0 has the same defect

```text
m1 + m0 C1 = -Q^{-1} + Q^{-1} C1 Q C1.
```

The constant index `m0 = 0`, `m1 = const`, `m2 = 1` writes that defect
into a fresh image. The four stored endpoint banks are not overwritten.
The image's x1 block is the published three-term coefficient and stays
unpaid. [PROOF.md](PROOF.md) gives the products and the circuit.

The selected frontier is unchanged. This does not rerun the declared
alternating-family lock, and it does not test a new feedback edge.

## Result

The predecessor replay stores `A = D1 Q^{-1}` on final bank 2 together
with the y0 coupling, and stores a pure y0 monomial on final bank 1.
Right division by the unit `A` produces three D-exponent-0 elements
`x`, `g`, and `b`. Finite multiplication gives `x b = 1 - Q^2` and
`C1 g = Q^2`, so every D-exponent-0 coefficient `m0` determines

```text
m3 = 0,  m2 = 1 - m0 x,  m1 = const - m0 C1,
const = Q^{-1}(C1 Q C1 - I).
```

Both coefficients in `const` are forced. Moving `Q^{-1}` into `m0` does
not delete it from the combination. The constant-index fresh image

```text
S = bank 2 + const · bank 1
```

has x0 block `A`, y0 block 0, and the original x1 block. Banks 0, 1, 2,
and 3 stay equal to the replayed left endpoint.

One factored circuit, using the predecessor's published field units and
charging each of `Q` and `Q^{-1}` as one 112-field monomial pass, costs
2016 scalar ADDs, 672 monomial passes, 32 mode CLEARs, 224 COPYs, and
336 extra fields, with 8 mode fields reused and no new Gaussian child.
That count is an upper bound for this circuit. It is not a minimum and
not a tape proof. A three-factor reading of `Q^{-1}` is not settled.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B scripts/research_package.py --package research/owner-indexed-y0-clearance --check-only
python3 -B scripts/research_package.py --package research/owner-indexed-y0-clearance
```

Direct replay:

```sh
python3 -I -W error -B research/owner-indexed-y0-clearance/verify.py
python3 -I -O -W error -B research/owner-indexed-y0-clearance/verify.py
```

The optimized command still executes the checks. They are `need` failures,
not assertions. No network, native build, or full multiplier replay is used.

## Scope

Original card: `joint-query-controller`. Scope status: **refined**. The
card asks for one source-bound caller identity and its extra charges.
This package does not change the query demand. It takes the owner-indexed
remainder of handoff
[discussion comment 19138525](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19138525)
after [research/coded-active-feedback](../coded-active-feedback/README.md)
restored the missing coefficient. The declared-family obstruction is the
fork package behind draft PR 152; its census is not repeated.

Base commit: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Pins are in
[SOURCES.json](SOURCES.json). The catalogue and selected record are
provenance. `search.py` is a live input. The selected conditional value
used for orientation is the selected record,
`781451/250000000`, not the older decimal printed in the revision-8
priority note.

Local overlap at that commit searched the complete note inventory and
found no note containing both "owner-indexed" and "y0 coupling". The
remote overlap cache was absent. A live open-PR search for `y0` on
CrocSwap/integer-mult-bounds returned no pull requests. That search is
not a novelty certificate.

## Open next questions

Can a fresh image clear the three-term x1 block while keeping x0 equal
to `D1 Q^{-1}`, keeping y0 zero, and leaving the four final banks stored
unchanged? The y0 term is no longer the obstruction on this image. The
first step is the same four-bank equation on the x1 column, with every
new monomial charged. This package leaves the published x1 coefficient
in place.

Does one inherited monomial pass implement `Q` and `Q^{-1}`, or must
`Q^{-1}` be expanded before the field ledger is a tape cost? The ledger
uses the predecessor's `Q^2` unit for each uniform power. The first step
is to bind the source monomial primitive for a single power of `Q`. No
native word is replayed here.

## Credit

The trace, algebra, and published row are Cinna Davis's
`research/coded-active-feedback`, using Dugongue's PR4948 chronology,
Dillon's PR4933 code, and the passive ceiling packaged by Chris R /
Clear1nsight. The one-point odd-Q correction from final bank 1, without
this owner-index identity or this charge, is the fork package
`research/active-feedback-coupling-lock`. The gauge engine remains the
inherited `research/coded-native-caller/gauge.py`.

Prepared by unpaidmoon with substantial Cursor Grok assistance.
Apache-2.0.
