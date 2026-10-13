# Exact occupied-cell representation

The pinned T37 wrapper loads the PR890 independent checker with its existing
four textual adaptations, then sets T = 37 and the nominated idle profile.
It recounts the native local paid profile, binds the U8 word and its replay,
checks source-event projections, builds literal windows and orthogonal port
bases, and calls `check_roles`. This package runs that wrapper unchanged.
After its ordinary module loader executes, an opt-in hook replaces only
`check_roles` with the same function after three exact source-block edits.
The loader hook is restored in a `finally` block. It is used in isolated,
single-threaded processes, not as a concurrent global library patch.

Those edits change the `used` dictionary's empty value, its disjoint interval
update and its final prefix/cardinality test. The helper/family sets, event
windows, chart cache, permutation checks, owner identities, inventories,
profile arithmetic, prefix/row reserves and complete returned receipt are
unchanged. Source hashes and exact patch-site matches fail closed on drift.

## Set/bitmap bijection

For a finite set S of nonnegative occupied coordinates, define

```
B(S) = sum(2^i for i in S).
```

Uniqueness of binary expansion gives a bijection to nonnegative integers.
Its basic identities are

```
S intersect T is empty  iff  B(S) & B(T) == 0
B(S union T) = B(S) | B(T)
|S| = B(S).bit_count().
```

For an interval with nonnegative offset o and width w,

```
B({o, ..., o+w-1}) = ((1 << w) - 1) << o.
```

The empty set corresponds to zero. Finally S is exactly the pending prefix
`{0,...,|S|-1}` if and only if

```
B(S) == (1 << B(S).bit_count()) - 1.
```

The cardinality alone is insufficient. For example `{0,2}` and `{0,1}` each
contain two cells, but only the latter is a prefix. This last equivalence
preserves the original gap predicate as well as the residual-capacity count.

Both engines start each dictionary entry empty. After every role, the
disjointness predicate has the same truth value and the union update preserves
the bijection. By induction over the unchanged role order, each entry encodes
the same occupied set at every boundary. The final prefix and leftover counts
therefore agree for every window/port entry. All later calculations receive
identical inputs, and every earlier or intervening predicate is retained.

The original `range(offset, offset+width)` is still constructed before bounds
admission. This preserves its integer-index checks and exceptions, including
integral floats and malformed values, and its conversion of an accepted
Boolean zero offset. Before shifting, the original nonnegative-offset and
capacity inequalities are checked explicitly. Thus a huge invalid offset
does not cause a huge allocation; it receives the same capacity rejection.
The disjointness part of the original conjunction then runs separately with
the same error message. The prior whole-helper width check is unchanged.

The pinned context validates the helper-width inventory and consumes exact
source-bound child ranks. Actual widths are 4, 5, 7, 8 or 9, and every observed
occupied bitmap fits 48 bits. Python integers are exact; the proof does not
depend on a fixed machine-word width, a modular fingerprint or sampling.

## Executed evidence

The ordinary set and bitmap engines run the complete unchanged T37 wrapper,
including its six original corruption controls and eight omitted-edit
controls. Every original receipt field agrees with the retained maintainer
replay. Only the eight machine-specific input-path keys are normalized to
logical names, after the complete exact input-hash inventory is checked.
No numerical or proof-relevant field is dropped. The raw original receipt
and the separately pinned adapter identity are both retained in saved runs.

A separate occupancy replay compares the set/bitmap representations after
all **167,832** role updates, covering **1,258,074** cell insertions and all
**74,592** final slice-prefix checks. It records a deterministic stream hash.
This is a separate mathematical representation check, not instrumentation of
the original function. The full original wrapper and receipt comparisons
provide the binding to its actual execution.

Additional differential runs reject 16 changed owner inputs with identical
exception type and message: negative/huge/non-integer offsets, invalid widths,
capacity violations at early/middle/last roles, early/late overlaps, and an
equal-cardinality shifted prefix. Four equivalent inputs are accepted with
identical receipts: the original, reversed and seed-94 shuffled role orders,
and a reference-accepted Boolean zero offset. A deliberately weakened
cardinality-only prefix predicate accepts the shifted invalid prefix; the
proper checker rejects it. Thus equality on the frozen valid word alone is
not the only test of the optimization.

Finite primitive coverage comprises **51,190** interval-admission/union cases
over capacities 0 through 8, every occupied subset, offsets -1 through
capacity+1 and widths 0 through 9; plus all **65,536** masks on 16 positions
for prefix equivalence. These tests corroborate the general bijection proof;
they do not replace it or prove the full multiplication theorem.

The optimization changes verification cost only. Native circuit execution,
controller construction, whole-hosted invoice, exact moments and outer
assembly are outside this audit stage and are not rerun or accelerated here.
All original compiler, realization, hosting, precision/tape, analytic and
bit-interface assumptions remain.
