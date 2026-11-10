# Optimal unbiased rounding by five reversible lattice maps

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

**Claim type: scoped all-lattice construction and proof with a finite exact
certificate.** For A=[[3,-4],[4,3]]/5, five explicit bijections of Z^2 have
uniform average Ax at every integer input. Retaining the seed gives an exact
two-sided inverse. Their expected squared error is zero when Ax is integral
and 2/5 otherwise. This is the pointwise minimum among all unbiased
integer-valued random outputs, including irreversible ones. Each seed also
has squared error at most 4/5. Grid spacing h scales these bounds by h^2.
No new kappa or selected-frontier change is claimed.

The construction attains the ordinary stochastic-rounding error optimum
while preserving exact reversibility for each seed. It uses dependent
coordinate rounding and a finite matching, rather than treating independently
rounded coordinates as a permutation. No physical sampler or execution-cost
claim follows from this mathematical interface.

[PROOF.md](PROOF.md) gives the universal argument.
[TABLE.json](TABLE.json) gives the five 25-row transversals, and
[construct.py](construct.py) regenerates them by bounded integer matching.
For x=5q+r, the map is Bq+table_s[r], where B=5A. Its inverse locates the
unique table output in y's coset modulo BZ^2, subtracts it and applies B^-1.
Every certificate condition has only 25 rows per seed; translation covariance
then supplies all integer inputs, including negative and arbitrarily large
ones. The exact verifier needs only the Python standard library.

## Reproduce

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/unbiased-periodic-rotation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/unbiased-periodic-rotation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unbiased-periodic-rotation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unbiased-periodic-rotation --check-source-history
```

Any CPython 3.12 path may replace that absolute path. Expected scientific
marker: `PASS_UNBIASED_PERIODIC_ROTATION`. Every direct run emits its computed
counts and a receipt bound to all eight package-file hashes. No receipt is
handwritten. Registered commands have a 120-second timeout and write no
replay outputs into the checkout. To regenerate the certificate, run
`python3.12 -I -B research/unbiased-periodic-rotation/construct.py` and compare
its stdout with TABLE.json.

The finite replay checks all 125 seed/residue entries, 16,810 signed two-sided
roundtrips, 3,750 images on four larger quotients and 1,250 signed translation
cases through 1,024-bit coordinates. Five controls distinguish a transversal
from an unbiased nearest-cell ensemble, require retention of the seed, reject
a fixed-seed unbiasedness claim, and reject independent coordinate rounding's
wrong output capacities. Finite tests corroborate the written argument; the
proof's covariance and inverse formulas supply the universal quantifiers.

## Scope and related work

The original `uniform-transfer-audit` card is explicitly changed to a new
precision-interface side result. It does not discharge an assumption at its
actual selected caller. Canonical base is
7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision eight; the selected
record remains PR6030, conditional kappa 0.003125804.

The question and matching construction are original to this contribution.
Classical scalar rounding variance, lattice quotient and regular bipartite
matching arguments retain their classical status. No general literature
priority is claimed for those methods. The rational phase also occurs in
ywz65's [PR2589](https://github.com/CrocSwap/integer-mult-bounds/pull/2589)
and Nick Petalas's [PR6304](https://github.com/CrocSwap/integer-mult-bounds/pull/6304).
Their deterministic lifting and norm/error results are context, not premises
or audit targets. The present question changes the contract to an unbiased
random ensemble with the pointwise stochastic error optimum. It does not
improve or generalize the four-tie deterministic optimum of PR6304, and its
individual-map 4/5 bound is not claimed as a new deterministic threshold.

[PR6418](https://github.com/CrocSwap/integer-mult-bounds/pull/6418) studies
adaptive bias from reusing a rounding seed. This construction requires an
independent seed for the stated expectation and supplies no reuse guarantee.
The same selected precision/native/compiler, ownership and analytic lineage
keeps its existing credit. No predecessor scientific replay was run.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362318).
Live open/account PRs, handoffs, active Discussions, local reservations, main
README terms and distinctive merged searches were checked. Sparse local
notes, arbitrary historical code and unpublished work remain coverage limits.

## Limitations

The seed is an externally supplied uniform five-state variable. Exact return
retains it. Sampling it, storing it, reclaiming its entropy and implementing
the quotient lookup with reversible scratch remain unpriced. The construction
allows outward norm movement and covers one rational planar rotation. There
is no inverse-unbiasedness, adaptive seed, repeated-word error, selected-root
or caller-binding theorem. Native/physical cost, precision/storage/tape costs,
supplier admission and a complete signed recursive invoice remain open.
All five framework assumptions remain. Selected cold replay, native builds,
Lean, Docker, independent human review and formal proof-kernel review are
unrun or unclaimed.

## Open next questions

- Bind a phase actually used by a supplier, its lattice, seed ownership and
  outward headroom. Start with an exact producer/consumer contract and price
  quotient lookup, seed sampling/retention and restoration before judging the
  complete invoice. The missing physical caller is the blocker.
- Can a finite matching with unbiased nearest-cell outputs be constructed for
  another rational orthogonal operator? Start with its integral period matrix
  and exact output-coset capacities. A favorable scalar error bound alone
  does not provide such an ensemble. No extension is reserved here.

Structured first steps and blockers are in [TASK.json](TASK.json).

## Code constraints

The constructor uses no recursion or optimizer. At most five matchings each
have 25 augmentations, each scanning at most 25 rows and 25 columns; each
alternating path has at most 25 links. The verifier's finite domains are
explicit in the counts above. Functions fit within sixty physical lines.
Explicit exception checks remain active under optimized Python. The only
package import is the adjacent constructor. File reads are bounded to eight
regular files of at most one MiB each; the table is limited to 64 KiB and
its coordinate shapes/ranges are checked before computation.

Power of Ten rule 3 deviation: CPython allocates integers and collections
during this bounded offline computation. The graph has 625 capacity entries
and 625 optional output entries, the certificate 125 points, and the largest
oracle image set 400 points. Large-coordinate tests use at most 1,030-bit
integers. Runtime allocation internals are not instrumented. Warning-strict
normal/optimized execution and in-memory syntax checks provide diagnostics;
no external type checker or linter was run. This is not an allocation-free or
bounded-word runtime implementation.
