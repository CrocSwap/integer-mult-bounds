# Expanded count identity, including source complements

This is an independent check of the counting argument in §3 of zxv's
[PR4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436).
The construction and claimed bound belong to that predecessor.
[PR4476](https://github.com/CrocSwap/integer-mult-bounds/pull/4476) explicitly
excludes this expanded identity from its width and routing
audit. The result here concerns finite invocation counts under the declared
compiler interface, not native correctness or physical execution.

## Assumptions and quantities

Fix an integer base threshold `m >= 2` and one raw rule with rank surplus
`Delta`. At each rank `n >= m`, a finite local flow has:

- integer source counts `S_s >= 0`, with `1 <= s <= n`, and
  `S_n = sum_s S_s > 0`;
- integer exit counts `E_e >= 0`, with `1 <= e < n`;
- `u_n` raw invocations, each with a positive integer column multiplicity
  `c`, and `q_n = sum_invocations c`, so `0 <= u_n <= q_n`;
- the local conservation identity

  ```
  sum_s S_s*s - sum_e E_e*e = Delta*q_n.                 (1)
  ```

Source and exit counts include every actual boundary job. In particular,
unmatched paid jobs are exits. These assumptions are checked on the finite
fixtures; the general local-flow argument remains attributed to PR4436 and
its lockstep predecessors.

The new flow counter labels a unit by an ordered word of target slots, with
`W_k` distinct letters of rank `k`. Words with occurrence vector `a` number
`multinomial(|a|;a) product_k W_k^a_k`, exactly the predecessor's `u(a)`.
Deleting the final letter `k` bijects the corresponding parent words with
the child words at `a-e_k` and their labelled `k` target slots. The two jobs
have the same rank. They match when both units exist; otherwise the existing
parent job is an exit or the existing child slot is a source. This is the
Pascal matching identity without implementing a multinomial point matcher.

Unit existence depends only on depth and the products of target and paid
letters. Thus summing multiplicities of words with equal products preserves
these counts, even when different occurrence vectors have the same product.
Paid paths with equal products still count as separate paths. This quotient
is for counting; it does not identify their fields or construct a physical
chronological schedule. The literal ordered-word mode and compressed mode
use this same correspondence; their comparison is an internal control, not
a claim of two independent mathematical implementations.

Let `B_n` be productive width, `P_n` the number of rank-one leaves, `U_n`
the number of raw invocation instances after expansion, and `Q_n` the sum
of those instances' column multiplicities. Owned storage is excluded from
`B_n`. Below the threshold, including rank zero, set

```
B_n = 1,  P_n = n,  U_n = Q_n = 0       (0 <= n < m).
```

Rank-zero calls are empty programs. Recording or omitting such calls has
the same counts. For `n >= m`, use the declared nested widths

```
a_n = B_(n-1),             B_n = a_n*S_n.
```

The compiler replicates the complete local flow `a_n` times. Each of its
`a_n*S_s` source arrays also receives its complementary rank-`n-s` job.
Each of its `a_n*E_e` exits receives a rank-`e` job. A width-`B_r` uniform
program consumes `B_r` jobs of rank `r`, so the child invocation counts are

```
C_(n,n-s;source s) = a_n*S_s / B_(n-s),
C_(n,e;exit e)     = a_n*E_e / B_e.                    (2)
```

Counts at the same child rank add; source and exit jobs are not identified
merely because their ranks coincide.

## Integer batching and termination

Every width is a positive integer. For `r >= m`, `B_(r-1)` divides `B_r`
because their quotient is the positive integer `S_r`; smaller widths are
one. Hence every `B_r`, `r < n`, divides `a_n = B_(n-1)`. Both quotients
in (2) are nonnegative integers. Since `s > 0`, a complement satisfies
`0 <= n-s < n`; exits satisfy `1 <= e < n` by assumption. Thus recursive
expansion terminates by strict rank descent. The count argument does not
require a favorable moment exponent.

## Telescoping through every child

Write `sum_child C_r X_r` for the sum over both classes in (2), preserving
their multiplicities. Complete expansion gives the recurrences

```
P_n = sum_child C_r P_r,
U_n = a_n*u_n + sum_child C_r U_r,
Q_n = a_n*q_n + sum_child C_r Q_r.                    (3)
```

These count actual repeated invocations, not distinct nodes in a memoized
dependency graph. In particular, `Q_n` is measured by summing raw columns;
it is not defined by the rank deficit we are about to prove.

We prove simultaneously, by strong induction on `n`,

```
B_n*n - P_n = Delta*Q_n,             0 <= U_n <= Q_n. (4)
```

The base definitions make (4) immediate. At a nonbase rank the total
productive rank mass supplied to the smaller programs is exactly

```
sum_child C_r B_r*r
  = a_n * [sum_s S_s*(n-s) + sum_e E_e*e]
  = B_n*n - a_n*Delta*q_n,                            (5)
```

where the last step uses (1). Substitute the induction hypothesis
`P_r = B_r*r - Delta*Q_r` into the first recurrence in (3), then use
(5) and the third recurrence. This gives the first identity in (4).
For the second, each local column is a positive integer, so `u_n <= q_n`;
combine this with `U_r <= Q_r` in the last two recurrences in (3).

This also justifies a flattened interpreter. Replacing each child reference
by its finite list of raw instances and rank-one leaves preserves (3).
Induction on rank therefore proves that a literal expansion and a recursive
aggregate calculation have identical counts, provided the aggregate keeps
all invocation multiplicities. Sharing the stored description of a child
does not authorize sharing its executed instances or productive arrays.

If `Delta > 0`, nonnegative leaf counts now give

```
U_n <= Q_n = (B_n*n - P_n)/Delta <= B_n*n/Delta.       (6)
```

The identity in (4) itself does not require positive surplus. Positivity is
essential for (6): at zero surplus it would divide by zero; at negative
surplus division reverses inequalities and gives no stated upper bound.

## Why complements and ownership qualifications matter

For the valid rule with one target of rank two and one paid rank-one job,
`Delta=1`. At rank three its local flow has `S_2=E_1=u_3=q_3=1` and
`B_3=1`. The complete program has one rank-one complement and one rank-one
exit, hence `P_3=2`, `Q_3=1`, and `3-2=1`. Omitting the complement would
give `P_3=1`, `Q_3=1`, and the false identity `3-1=1`. A per-flow mass check
alone would not expose that compiler omission. Wrong batching factors and
deduplicated child invocations similarly invalidate the expanded inventory.

If every raw invocation uses at most `O_local` separately owned center
banks, allocating fresh banks to every expanded instance gives at most
`O_local*U_n` banks. The one-center case is `U_n`. This is a conditional
bank-count bound, not a bound on bank capacity, peak-optimal storage, router
scratch, physical movement or initialization/erasure cost. If an actual
implementation instead needs a bank per column, `Q_n` is the corresponding
count. Native ownership and tariffs require their own evidence.

No claim here checks the record grammar, encoded constants, direct exponent
gate, analytic transfer or a complete multiplication theorem. No kappa is
changed. Credit zxv for PR4436's construction and count claims, Jacob Alan
Sussman for the lockstep/Pascal construction, and Ryanson Jonathan for the
PR4456/PR4476 independent flow, width and routing checks that delimit this
remaining scope. Prepared for Dillon with substantial OpenAI Codex assistance;
no independent human or proof-assistant review is claimed. Apache-2.0.
