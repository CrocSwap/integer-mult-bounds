# Exact representation change

The domain is the pinned PR626 independent owner checker on integer-valued
JSON owner/plan/native inputs that reach its footprint operations. It checks
`0 <= offset <= offset + w <= cap` before creating the interval. Thus the
interval endpoints and width used by the substitution are nonnegative.
Malformed noninteger inputs are outside this equivalence claim; neither
implementation is presented as a general JSON schema validator.

For a finite set S of nonnegative integers define

    encode(S) = sum(2**i for i in S).

Distinct indices occupy distinct binary digits. Consequently:

- `encode(S) & encode(T)` is zero exactly when S and T are disjoint.
- `encode(S) | encode(T) = encode(S union T)`.
- `encode(S).bit_count() = len(S)`.
- `encode(range(offset, offset + w)) = ((1 << w) - 1) << offset`,
  including w = 0.

A nonnegative integer m has `m & (m + 1) == 0` exactly when m has a suffix
of k one-bits and no higher one-bits, including k = 0. Indeed, adding one
clears the trailing ones and sets the first zero bit. Any higher one-bit
would survive the AND; if no such bit exists, the AND is zero. Therefore
this predicate is equivalent to

    S == set(range(len(S))).

Induct over the owner rows. The original dictionary defaults to an empty
set; the replacement defaults to zero. Assume both represent the same
occupied cells at a row's start. Every check before interval creation is
unchanged. The interval formula gives the same new cells; the overlap
predicate agrees and, on acceptance, union restores the invariant. Both
stop at the same failed `need` predicate for this row. After all rows, the
compact-prefix predicate and cardinality agree for every owner, including
unused owners. Every idle remainder `cap - len(S)` is identical. The paid
profile, rank-mass check, exact rational moments and outer comparison then
execute the original code on identical values. Dictionary iteration order
and all receipt fields are unchanged.

The adapter performs four exact, counted textual substitutions, only after
checking SHA-256 pins of the original checker and rational interval module.
It executes every original `need` statement. It neither caches acceptance
nor changes a moment engine, footprint capacity, window or owner row.
The same source-only admission is used for both adapter engines. The timed
reference is the original direct CLI, so the candidate pays its additional
pin/substitution overhead.

This is a written equivalence argument for the stated finite operations,
corroborated by bounded tests. It is not proof-assistant formalization,
a proof of the construction's inherited physical interfaces, or a proof of
the full multiplication theorem. Tests do not enlarge this mathematical
scope. The original checker itself is a supplemental audit; its recorded
success does not replace the native/controller/outer-assembly pipeline.
