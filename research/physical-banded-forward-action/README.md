# Physical banded forward action

This package executes a supplied real band-matrix action on packed RHS columns
using fixed physical tape roles. It writes fresh zero target rows, interleaves
the borrowed sources, calls the unchanged seven-product inverse-page service
once, projects the targets, checks source preservation bit for bit, and erases
all owned work. It returns a protected output in the original padded layout.

The construction lifts F to a square-zero matrix N with
`N[2i,2j+1]=-F[i,j]`. Solving `(I+N)y=(0,x)` returns `(Fx,x)`, even when F is
singular. Preparing the factors from F rounded once to the P grid yields
exactly the same final page bytes as preparing exact F then rounding the pages.
The verifier actually runs the unchanged physical `prepare_pages`; it does not
feed expected page values to the consumer.

**No new κ.** This is one literal forward primitive with a finite actual broad
Reference binding. It does not implement the whole broad Gaussian word, global
union routing, FFT/CRT recovery or any discharge of the selected five assumptions.

## Exact scope and complete cost

`BandedAction.run(source,pages,n,r,b,w,P)` accepts batch-major real RHS columns,
with row and final-column padding zero. The dyadic block b covers the doubled
interleaved band. All external ports and heads are restored. Metadata may alias
other metadata; data ports are distinct and outside the complete owned closure.
Call `consume()` after using the protected output.

With `K=ceil(2n/b)` and `J=ceil(r/b)`, the transaction makes exactly
`2(2K-1)J` b-by-b products, each with `7^log2(b)` actual scalar children.
[PROOF.md](PROOF.md) retains the full scalar-word price, parked-frame movement,
all ceiling terms, encoded counters, inserted zeros, projection, erasure,
complete-r backing and separately paid setup. For row sparsity s and current
complex-l1 input radius R, the error relative to original F is at most
`(sR+6)2^-P`. Stored sources/targets stay within `max(1,||F||∞)R`; exact kernel
scratch uses its larger inherited guards.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/physical-banded-forward-action
```

Expected: all four registered normal and optimized commands pass. The physical
commands match the exact `RESULT.json` receipt and marker
`PASS_PHYSICAL_BANDED_FORWARD_ACTION`; the independent controls report
`PASS_INDEPENDENT_FORWARD_CONTROLS`.
For a direct replay:

```sh
python3 -I -B research/physical-banded-forward-action/verify.py
```

The checks execute an actual **broad** `Reference(61,3,2,1,3,32)` Schur matrix
from window `[16,20)` with explicit interior `{1,2}`; a signed nongrid singular
tridiagonal matrix; and a shorter one-row zero matrix on the same owner. They
check partial rows/RHS, original source/page bindings, exact pre-round page
equivalence, protected output, all 2,788 owned roles, aliases, corrupt padding,
tiny out-of-band source coefficients and failure after a completed matrix child.

The independent source oracle derives the Schur matrix through the full
original broad matrix inverse and explicitly rejects narrow substitution.
The independent output oracle forms three disjoint integer dot sums instead
of replaying the author's block recurrence. It compares every actual returned
bit, source preservation, original-matrix error and the complete product count.

## Provenance and limits

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The unchanged actual `seven_product.py` and `fast_boundary.py` come from public
fork commit `f821cba68f44048e70e78afb75603ed4dde99f11`; their source paths and
hashes are in [SOURCES.json](SOURCES.json). Canonical page preparation and the
physical scalar-word cohort are retained from
CrocSwap/integer-mult-bounds#5059. The same-reference broad finite-core program
and numerical prerequisites are inherited from merged
CrocSwap/integer-mult-bounds#4205. Closed/unmerged
CrocSwap/integer-mult-bounds#481 already proposes batched Gaussian arithmetic;
the generic identity and arithmetic exponent are not claimed anew here.

The unchanged `reference_source.py` adapter is retained from
[`research/shrinking-reference-halo/source.py`](https://github.com/CubeJerry/integer-mult-bounds/blob/a99c4dce9f6bf1972b13f0f239e082ac70a9e5e8/research/shrinking-reference-halo/source.py)
at published fork commit `a99c4dce9f6bf1972b13f0f239e082ac70a9e5e8`.
Its SHA-256 is
`20c0fb2e4aa95de976ef6ce74ded4bf1cb9073732eca7eda8f61e45d239afa2c`.
The source authentication and isolated Reference-loading adapter are credited
to that predecessor package; they are not new implementation in this result.

The explicit finite interior is not asserted to be the production carve's
choice. The source target is its exact rational broad Schur, without an ideal
Gaussian approximation claim. Input and coefficient preparation, and any
earlier grid conversion, are separate charged work. No finite-size speedup over
a direct matvec or competing physical implementation is claimed.

## Open next questions

Can one complete broad union-window caller bind its original coupling shear,
source page key, current-grid conversion and header routing around this
primitive? The first step is one frozen source and a full chronological physical
transaction, with setup and partial-batch ceilings retained. The current
already-packed ABI does not supply that caller.

Prepared for `@CubeJerry` with substantial OpenAI Codex assistance. A separate
source-aware AI reviewer supplied the independent original-matrix, page and
three-sum oracle. Credit the original construction authors, Jose Manuel's common
Reference/core integration, Mason Hale's interval arithmetic, the retained
physical scalar-word and exact seven-product contributors, and the named
predecessors above. Apache-2.0; source notices are retained. Finite checks are
not human approval or a formal proof-assistant certification.
