# Shared phase-repair rank bound for independent groups

## Statement

Take `G >= 1` independent direct-sum copies of the exact port-zero idle-transfer defect retained from PR #3220. Each copy has a rank-two eight-stream matrix defect at character 16. Keep the original residual mass fixed. Repairs are additional caller-level phase children of integer ranks `q_j` between 1 and the outer cap 51; a rank-`q` phase child can alter at most `q` independent stream directions. Assume `0 <= a <= 1/400` and charge each child `q^(1-a)` raw moment units.

Then any exact repair has total child rank at least `2G` and total raw repair cost strictly greater than `G`. The PR #3220 residual-repacking allowance is less than `153/160` per group. Therefore no such repair can pay for the repacking, even if routing, restoration and all other repair overhead are free.

This statement is conditional on independent direct-sum group inputs and additive repair rank. It does not cover overlapping group inputs or corrections absorbed into the original calls.

## Rank of the retained defect

PR #3220's pinned proof gives the only nonzero entries of `Delta` at character 16 (zero-based indices):

```text
Delta[1,1] = -1-i
Delta[3,1] = -1-i
Delta[7,7] =  1-i
```

Thus only columns 1 and 7 are nonzero, so `rank_Q(i)(Delta) <= 2`. The principal minor on rows and columns `{1,7}` equals

```text
(-1-i)(1-i) = -2 != 0,
```

so its rank is exactly two. The exact source proof bytes and Git blob are pinned in `SOURCES.json` and retained under `vendor/`.

For `G` independent groups, their joint defect is `Delta_G = Delta ⊕ ... ⊕ Delta`; hence `rank(Delta_G) = 2G`.

## Required repair rank

Insert repair phase children one at a time at arbitrary caller-level cuts. At character 16, inserting one rank-`q_j` phase child changes the full operator by

```text
S_j (U_j - I) P_j,
```

where `P_j` and `S_j` include every earlier and later operation at that cut. Since the phase child changes at most `q_j` independent stream directions, `rank(U_j-I) <= q_j`, and multiplication by surrounding matrices cannot increase rank. The difference between the unrepaired and repaired operators is the sum of these insertion differences, so rank subadditivity gives

```text
2G = rank(Delta_G) <= sum_j q_j.
```

This argument does not assume the repairs are assigned separately to each group. It permits one repair child to span several groups and grants arbitrary source access and routing. It does assume the group errors are independent direct summands and that the repair is a phase-child insertion rather than a changed original factorization.

## Moment cost

Let `Q = sum_j q_j`. Every repair child has rank `1 <= q_j <= 51`. For any `0 <= a <= 1/400`,

```text
q_j^(1-a) = q_j * q_j^(-a)
          >= q_j * 51^(-a)
          >= q_j * 51^(-1/400)
          >  q_j / 2,
```

because `51 < 2^400`. Therefore total repair cost satisfies

```text
C = sum_j q_j^(1-a) > Q/2 >= G.
```

PR #3220 bounds the per-group repacking savings by

```text
B(a) <= 20*a*51/e <= 51/(20e) < 153/160,
```

using `e > 1 + 1 + 1/2 + 1/6 = 8/3`. Thus total available allowance is

```text
G*B(a) < 153G/160 < G < C.
```

The repair remains unaffordable even in this optimistic direct-sum shared model. For `G=2`, rank at least four is required; one rank-four child is a feasible rank-packing relaxation, but exact correctability is not asserted. The OR-Tools receipt gives a lower-rounded objective for this finite relaxed rank partition; the inequalities above prove the general result independently of the solver.

## Scope limits

- The retained witness is one source-bound owner-zero/port-zero defect. This proof takes two or more independent copies abstractly; it does not identify two actual T740 groups with disjoint source spaces.
- It covers additional phase-child repairs at caller-level cuts, not changes inside opaque recursive children or new multi-stream interactions.
- It fixes the original residual rank mass. Absorbed repairs, changed stock, changed coverage or reductions in original paid work require another complete invoice.
- It is not a new provider moment, κ, supplier admission or selected-frontier update.
