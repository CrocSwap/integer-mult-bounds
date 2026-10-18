# Exact moving-origin representation of the corrected census

This is a written representation-equivalence proof for Nicholas Stone's pinned
PR2973 C census, with `1 <= N <= 7` and positive even `L <= 20`. It does not
introduce a pruning rule. Its collision-budget soundness, canonical word domain
and relation to `f(7)` remain those of the pinned predecessor `MATH.md`.
The proof is not checked by a formal proof assistant.

## Compression keeps the parity classes separate

Write `p(x)` for Hamming-weight parity and `pi(x)=x>>1`. The map `pi` is linear
over F2. Restricted to either coset `p(x)=b`, it is bijective onto F2^(N-1):
the omitted bit is uniquely `b XOR p(pi(x))`. Consequently pair differences
within E, within O, and between E and O can each be stored in one 64-bit mask.

The within-class differences have parity zero, and the cross differences have
parity one. They must remain distinct even when their compressed indices
coincide. Thus the exact full coverage test is

```
popcount(ee | oo | 1) + popcount(eo) == 2^N.
```

The bit `1` includes zero in the even coset. Combining all three compressed
masks with OR would be wrong: that mutant loses the known four-source universal
word `01021323` and is rejected by the verifier. A coordinate projection here
is only an encoding *within already separated weight-parity classes*. It does
not replace weight parity by coordinate bit 0, the unsound operation corrected
in PR2973.

## Keep the coordinate origin at the current walk position

At the entry to `rec(i)`, let q be the current prefix, E the distinct global
even-weight prefixes and O the distinct global odd-weight prefixes. Maintain

```
epoints = { pi(x XOR q) : x in E }
opoints = { pi(x XOR q) : x in O }.
```

The labels E and O keep their *global* parity meaning; their relative images
need not be even and odd respectively. The pair-support masks ee, oo and eo
encode global XOR differences and do not move with q. The existing 128-bit
`seen`, original state arrays, sizes, visit/letter counts and collision counts
are retained.

A label j takes q to `nq=q XOR 2^j`. For every old point x,

```
pi(x XOR nq) = pi(x XOR q) XOR pi(2^j).
```

For j=0 this compressed-coordinate translation is the identity. For j>0 it
flips exactly the index bit j-1. With `shift=2^(j-1)` and a mask `low[j]`
selecting index positions whose j-1 bit is zero, the permutation is exactly

```
((mask & low[j]) << shift) | ((mask >> shift) & low[j]).
```

It swaps the two halves of each index block of length `2*shift`. For the allowed
labels the shift is at most 32; no shift by the word width is used. It preserves
unions and cardinalities and is its own inverse. For N<7, valid masks remain
inside the first `2^(N-1)` positions. N=1 uses only the identity case.

Let next_e and next_o be the translated masks. If nq is fresh and has global
parity p, its differences with the old same-parity prefixes are exactly
`p ? next_o : next_e`; its differences with the opposite class are the other
mask. This replaces the old loops over E and O with two constant-size
permutations. Injectivity within each parity coset means the new mask has the
same pair support and the same intersection count with existing supports.
Therefore both collision increments are unchanged.

Before recursion, install next_e/next_o. If nq is fresh, add bit zero to the
appropriate point mask, since `pi(nq XOR nq)=0`. Freshness is still decided by
the unchanged full `seen` mask, so compression cannot create a false revisit.
If nq is an old point, there is no pair or collision increment, but moving the
origin still permutes the point masks. After recursion restore both old point
masks, together with the unchanged predecessor rollback. Reset both masks
before each shard. The closing q_L=0 remains outside the prefix set exactly
as in the original implementation.

## Induction gives the same traversal, not only the same final answer

Initially E={0}, O is empty, q=0; the invariant holds with epoints=1,
opoints=0 and empty difference supports. Assume it at a recursive entry.
The allowed next labels, shard tests, count and reachability tests are unchanged.
The preceding identities give identical pair-support/collision increments for
each proposed extension. Thus both budget tests accept or reject the same
extension, in the same order, incrementing the same prune counter. Installing
the translated masks preserves the invariant at the child; restoring the old
masks preserves it at the next sibling. At a leaf the separated-coset formula
gives exactly the old coverage test. The word emission and output-I/O paths are
unchanged.

Induction therefore gives the same ordered recursive entries, every node,
leaf and prune counter, ordered witnesses, and cap/abort behavior. This assumes
the predecessor's stated machine/input domain and no external I/O failure;
the existing I/O failure detection is retained. A capped run is incomplete,
even if its emitted witness file is empty.

## Executable checks and scope

The new scalar state oracle reconstructs both relative point masks and all
three difference supports from the original E/O arrays, recomputing excesses
from pair cardinalities. It runs at every recursive entry in small full-domain
checks, 36 capped seven-source checks and the complete L20 (10,7) traversal.
The bit permutation is checked on all 448 basis/label pairs plus composite
masks. Sanitizer-trap builds cover the kernel and all dimensions 1 through 7.

The predecessor's raw-product oracle is reused, with attribution: 164 complete
small comparisons, including positive universal words and all four budget modes.
Its Python seven-source oracle recomputes full pair supports from scratch.
These are independent of this mask representation; the complete billion-node
comparison still shares the predecessor's traversal and pruning logic and is
not a second independent proof of that logic. Exact full JSON and witness-byte
comparisons cover all six original completed large cases. Only the per-shard
and total `seconds` fields are excluded, after validating they are finite and
nonnegative.

No length22 census, new lower bound, supplier construction, native compiler
admission or new kappa follows from a faster replay. The finite result retained
from PR2973 is `22 <= f(7) <= 24` in the PR943 singleton prefix-walk model.
