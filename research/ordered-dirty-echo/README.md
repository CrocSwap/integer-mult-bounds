# Fewer dirty-echo calls at a fixed scratch budget

**Recursive-interface research / finite construction refinement; no new κ.**

An exact ordered-tree optimizer reduces the complete dirty-echo call count
from **512 to 464** for 27 factors with six borrowed arrays, and from
**2,112 to 1,600** for 56 factors with eight borrowed arrays. Both comparisons
use Dillon Amburgey's improved balanced ternary schedule in
[PR #689](https://github.com/CrocSwap/integer-mult-bounds/pull/689).
Every inverse and restoration call is included. The factor order is unchanged.
These are operation counts, not measured runtime improvements.
The factor counts are generic interface fixtures, not asserted prime-power
cyclic-inversion parameters for the inherited PR628 implementation.

The mechanism is androolloyd's
[PR #673](https://github.com/CrocSwap/integer-mult-bounds/pull/673) dirty echo.
Its first and last children execute twice, while the middle child executes
four times. Allowing unbalanced contiguous splits and mixed binary/ternary
nodes reduces repeated work. At 27 factors the chosen root split is
`9,7,11`, outside #689's recursively balanced class. The 15-factor result
of 160 calls already belongs to #689 and is retained as a comparison control.

## Reproduce

From the repository root, with Python 3.10+ and its standard library:

```sh
python3 -I -O -B research/ordered-dirty-echo/verify.py
```

Expected: `PASS_ORDERED_DIRTY_ECHO`, with the exact coverage counts described
below. The command authenticates the vendored predecessor, recomputes all
fields of [CERTIFICATE.json](CERTIFICATE.json), and compares the complete
result. No network, optional library, pending-PR checkout, or generated cache
is needed. The checks remain active under optimized Python.

[VALIDATION.json](VALIDATION.json) records the local environment, isolated
package replay, selected-record check, and two additional certificate/source
corruption checks. It distinguishes these runs from checks not performed.

The certificate contains each selected tree, ordered prices, scratch budget,
actual reserved scratch, weighted cost, leaf count, per-factor multiplicity,
and a hash of the complete emitted instruction word. `--emit` prints the
recomputed certificate for inspection; it does not overwrite the frozen file.

## What is optimized

For fixed positive integer leaf prices and a cap on borrowed arrays,
[optimize.py](optimize.py) finds the minimum charged leaf cost over every
ordered binary/ternary tree. Each node reserves all its connectors throughout
its child calls. Children share a deeper scratch pool because they restore it.
This is the predecessor's allocation discipline. Ancestor-storage reuse,
factor permutations, fanout above three, and different echo words are outside
the optimization class.

The [written proof](PROOF.md) gives the complete recurrence, exact linear
product, nonlinear restoration contract, execution/preparation/precision
charges, and proof of the dynamic program's optimum within this class.
Source and target add two further array roles: the two uniform witnesses
have eight and ten total roles respectively.

Unequal prices are supported at a **fixed common precision and layout**. The
seed-derived abstract prices `(3,2,1,9,8,7,6)` have minimum weighted cost
180 with four borrowed arrays and 168 with five. Their call counts are 36
and 40 respectively, so a weighted reduction need not reduce calls or the
precision needed by a concrete implementation. These prices are a scheduling
fixture, not measured supplier costs.

## Verification and completed coverage

- Exhaustive comparison against a separate postfix-tree enumerator covers
  every cost vector in `{1,3}^n`, for `1 <= n <= 6` and every scratch budget
  `0 <= b <= n-1`: **642 cost/budget cases and 207 ordered tree shapes**.
  A separate path-based calculation checks cost and scratch use.
- Exact free noncommutative expressions check the ordered linear product and
  cancellation of every dirty input for all 207 trees and all four larger
  witnesses, in both signs. This does not assume the factors commute.
- Exact nonlinear integer maps test source/scratch restoration and inverse
  execution for two dirty inputs per tree and witness. A concrete nonlinear
  example confirms that restored dirt can still affect the output increment.
- Omitted restoration, reversed factor order, an undercharged middle child,
  and insufficient scratch must each fail for the intended reason.
- The emitted words for the predecessor's balanced trees are compared with
  its unchanged, source-pinned generator. The certificate also retains #689's
  corrected balanced counts.

The proof establishes the recurrence for the stated finite-tree class. The
executable coverage is bounded; it is not a formal verification of the
multiplication theorem. No random candidate search or early search cutoff is
used. The assignment seed is 56; it selects the 56-factor probe and the
unequal-price fixture `c_i = 1 + ((56 + 17*i) mod 9)`, `0 <= i < 7`.

## Scope and handoff

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
[SOURCES.json](SOURCES.json) pins the actual #673 and #689 sources, and
[NOTICE.md](NOTICE.md) preserves attribution and substantial AI-assistance
disclosure. The [local sprint claim](CLAIM.md) records the three candidate
tasks, overlap review, stopping rule, and result.

At that base, the selected result is the reviewed #626 composition with
κ = `51110230636731/31250000000000000`. Its certificate, actual K492 owner
construction, and maintainer review were followed before selecting this task.
This package changes only its own research directory.

The local echo still needs an admitted all-role supplier, physical layout,
source/phase access, routing, coefficient preparation, rounding and exact
recovery before it can contribute to a multiplication bound. The pinned
three-shear direct adapter has optimistic moment at least `6-6/n >= 3` for
`n >= 2`, even after these optimizations; it fails the required contraction.
The proof explains why. The selected construction's compiler, common-label,
mutable-basis, hosting, residual, precision, tape and analytic assumptions
remain inherited. No selected cold replay, full repository suite, Lean proof,
remote CI, or practical performance benchmark is claimed for this package.
