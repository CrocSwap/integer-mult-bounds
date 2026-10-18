# Why the one-basis closure is equivalent

Let the immutable live-line table be integer vectors `L_i` of dimension `d`,
and let `p = 2147483647`. For a nonempty mask `M`, the frozen PR886 checker
forms `S = {L_i : i in M}` and returns

```
({i : rank_p(S union {L_i}) = rank_p(S)}, rank_p(S)).
```

It includes selected lines without a second rank call. The new implementation
returns the same pair by constructing one echelon basis of `span_p(S)` and
testing each remaining line for membership in that basis. This is an exact
linear-algebra identity over the fixed prime field, not a probabilistic test.

## Basis construction and membership

Process selected rows in their original order. Reduce a row against the
existing unit-pivot rows, in increasing pivot order. Each subtraction is a row
operation, so the residual differs from the original row by an element of the
existing span. A zero residual adds no dimension. Otherwise normalize its
first nonzero coordinate using its inverse in the field and insert the row at
that pivot. The new pivot is absent from the existing basis, so the new row is
independent. Earlier coordinates of a row with a later pivot are zero; sorting
the pivots therefore preserves echelon form even when a new pivot precedes a
previously inserted one. Induction gives exactly `span_p(S)` and its dimension.

For any candidate line, subtract the basis rows in increasing pivot order.
Later rows cannot reintroduce an earlier pivot. A zero residual means the line
was a combination of the basis rows. Conversely, a combination reduces to zero
by that elimination. The membership predicate is therefore equivalent to the
frozen `rank_p(S union {L_i}) == rank_p(S)` predicate. If the basis has `d`
pivots, it spans the entire coordinate space and every live line is admitted.

The empty-mask result remains `(0, 0)`, exactly the reference's explicit
convention. Actual E8 live lines are nonzero. Synthetic zero-line tests retain
that empty convention and check ordinary span membership for nonempty masks.

## Why the modular rank is the rational rank here

Both the integrated reference and the new factory enforce the sufficient
Hadamard guard

```
B^d < p^2, where B = max_i sum_j L_ij^2.
```

For any nonzero `k` by `k` minor of original live rows, `k <= d`, Hadamard gives
`det^2 <= B^k <= B^d < p^2` when `B >= 1`. Thus its nonzero integer determinant
has absolute value below `p` and remains nonzero modulo `p`. Vanishing integer
minors also vanish modulo `p`, so every subset of live rows has the same rank
over the rationals and the prime field. The `B = 0` case has rank zero over
both. This covers augmented sets used in membership tests as well. No guard
about large coefficients in an intermediate modular basis is necessary: the
minor argument applies to the original integer rows.

The test table containing `p*e_1` shows why the guard matters: rational rank is
one while its modular rank is zero. The factory rejects that table. This is
a concrete failure control, not a claim that this sufficient guard is necessary.

## Coverage preserved by the adapter

Five consumed files are admitted by their pinned SHA256 bytes before execution.
The adapter replaces only the top-level `close` function in the parsed frozen
checker. The resulting code is compiled with `optimize=0`; optimized CLI
invocations are additionally refused. All original frame catalogue checks,
least/greatest bounds, options, component enumeration, nesting rejection,
paid profiles, rational moment intervals and selected-minimum comparisons run.
All other AST statements, including the original `rank` function and assertion
sites, remain present. Existing sources and defaults are not edited.

The cache uses precisely the old input-mask boundary. It starts empty for each
word execution, and the factory copies its line coordinates into immutable
tuples. There is no persistent cache, cross-word reuse, changed pricing, or
enumeration pruning. Complete differential replay compares every mask, closed
mask and rank, not just the final optimum. Receipt equality includes the
reference's full printed JSON through an exact stdout digest.

This argument establishes the closure algorithm's equivalence under the stated
domain. The accompanying finite replay corroborates its implementation. Neither
is a formal proof of the full multiplication theorem, a new frame optimum, or
an extension of the predecessor's fixed-word search domain.
