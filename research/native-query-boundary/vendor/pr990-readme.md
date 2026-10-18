# Batch restored native DATA shears through one dirty private row

**Research construction with a scoped finite optimum. No new kappa.**

This extends the private-only boundary of [PR #677](https://github.com/CrocSwap/integer-mult-bounds/pull/677), using Karl Appel's native ADDRESS query from [PR #521](https://github.com/CrocSwap/integer-mult-bounds/pull/521). Four DATA targets receive a rank-three combination of five immutable DATA sources. Sharing the correction for the arbitrary private input reduces twelve complete recursive queries to eight. The best schedule in the class below also reduces 36 aligned XOR scans to 30.

The elementary sharing idea is related to @CubeJerry's [PR #889](https://github.com/CrocSwap/integer-mult-bounds/pull/889), which batches common-factor product shears. This contribution supplies a different, fully specified native-query boundary, its complete child/affine/scan bill, and an exhaustive affine-state schedule census. It does not claim priority for compute/uncompute or general dirty correction sharing.

## Reproduce

From the repository root, with Python 3.10 or later and no external packages:

```sh
python3 -I -B research/native-shear-batch/verify.py
```

Expected:

```text
PASS_NATIVE_SHEAR_BATCH schedules=5376 queries=12->8 xor_scans=36->30 columns=7290 negative_controls=8 no_new_kappa
```

`CERTIFICATE.json` contains the complete 38-event program. Rows 0 through 3 are targets, rows 4 through 8 are sources, and row 9 is the dirty private row. `query` acts only on row 9. Its last field is the signed direction of the native query. `xor` gives destination and source row numbers. The checker emits the schedule afresh and compares the entire certificate, then executes it symbolically and on the complete order-three ADDRESS domain. Optimized Python is supported; checks do not depend on `assert`.

Exact base: `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`. Source commits and SHA-256 values are in `SOURCES.json`. The selected result at that base is PR942's conditional `1661960547713947/1000000000000000000`. Neither it nor `upstream/` is modified.

## Endpoint and schedule

All VALUE arithmetic is XOR over F2. Every row has the same complete ADDRESS domain and volume U. Let h be PR521's invertible ADDRESS permutation acting linearly on VALUE arrays. The endpoint is

```text
X' = X + (I+h) M Y,      Y' = Y,      q' = q.

M = [1 0 1 0 0]
    [0 1 1 1 1]
    [1 1 0 1 0]
    [0 1 1 1 0]
```

The private input q=d is arbitrary, including values unrelated to every DATA row. No row is copied, cleared or assumed zero. Source rows never change. Targets and private q are exclusively owned for the duration of the complete batch; intermediate states are not completed DATA interfaces.

A source mask b represents the XOR of selected Y rows, with source zero in its low bit. The program visits the following four private states. Each visit applies h to q, adds that row to the indicated targets, then applies h inverse to q. Between visits it toggles the individual source rows needed to change b. Finally it restores b to zero and adds M Y directly to the targets.

| b before query | Targets reading h q | Source scans from previous b |
|---:|---|---:|
| 0 | X0, X2 | 0 |
| 5 | X0, X1, X3 | 2 |
| 11 | X2, X3 | 3 |
| 27 | X1 | 1 |
| Return to 0 | None | 4 |

There are ten source-to-q scans, eight q-to-target scans and twelve direct source-to-target scans. Four forward/inverse query pairs give eight recursive children and 48 affine events.

For a general list of sample masks b_j and target-column masks a_j, the sampled target addition is

```text
sum_j a_j h(d + b_j Y)
  = (sum_j a_j) h(d) + h(sum_j a_j b_j Y).
```

Here the four target masks are `5, 11, 12, 2`. Their XOR is zero. Their outer products with the four source masks sum to M: the target rows are `5`, `5 XOR 27 = 30`, `0 XOR 11 = 11`, and `5 XOR 11 = 14`. Thus arbitrary dirt cancels, the sampled contribution is h M Y, and the direct scans finish the claimed endpoint. The final source toggles restore q=d. The inverse reverses every event and reverses each query direction. The endpoint itself is an involution.

This is a written identity for arbitrary arrays and any invertible linear h. The finite tests below check its implementation, not the full multiplication theorem.

## Exactly what was optimized

An **excursion** in this note is one h query on q, any set of direct q-to-target reads, and one h-inverse query returning q to the unpermuted source chart. Source toggles happen only outside excursions. The allowed remaining operations are individual source-to-q and source-to-target XOR scans. Target-to-target and source-to-source mixing, extra private rows, negative-height excursions, adjacent queries without return, and alternative ADDRESS primitives are outside this optimization class.

On arbitrary complete arrays, h and I are linearly independent over F2: PR521's h has a nontrivial odd-order ADDRESS orbit. With k sampled states, arbitrary-dirt restoration requires `sum a_j=0`, and matching the h coefficient requires `sum a_j b_j=M`. Consequently

```text
M = sum_(j=1..k-1) a_j (b_j + b_0),
rank(M) <= k-1.
```

The fixture has rank three, so at least four excursions, hence eight queries, are necessary **in this class**. Four suffice. This does not generalize PR677's one-shear private-only lower bound to every multi-shear query word.

At this minimum, the four b values must be affinely independent and their differences must span the three-dimensional row space
`{0,5,11,14,16,21,27,30}`. The checker considers all `choose(32,4)=35,960` four-element subsets of F2^5, retains exactly 224 valid sample sets, and evaluates all 24 orders of each. This includes offsets outside the row space. For each set, the even-parity coordinates of each M row uniquely determine all target reads. The minimum transitions between fixed source states cost their Hamming distance. Direct M Y costs twelve scans in this class.

All 5,376 schedules were completed, with no timeout or early stopping. Their XOR cost histogram is in the certificate. A second enumeration starts with the 168 ordered bases of the target column space and solves source coordinates for each of 32 offsets; it produces the same full histogram. The minimum is 30, attained by 232 schedules. The certificate chooses the lexicographically first minimizing tuple of source states, then target masks. Longer source paths, repeated cancelling reads and extra direct scans cannot lower the count for any fixed schedule.

The comparison is stronger than applying the four-query single-edge program twelve times. It considers all 28 unordered bases of the row space and uses the unique rank-three factorization `M=A B` for each. Each factor gets its own complete PR677 dirty restoration. Even allowing all final direct terms to cancel globally into M Y, this comparison needs twelve queries and at least

```text
2 sum_j weight(B_j) + 2 sum_j weight(A_j) + weight(M) = 36
```

XOR scans. The minimizing basis is `5,14,16`, with target masks `5,14,2`. This baseline optimum is also scoped to those separately completed rank factors. A DATA-query contract can instead use PR677's two-query shears; the present result is useful only when queries must stay private.

Assignment seed 52 was drawn with operating-system randomness. The fixture uses `random.Random(52).getrandbits(5)` for four rows, rejecting zero rows, missing source columns and ranks other than three. The stopping rule is the first accepted matrix within 1,000 attempts. It is accepted at attempt six. Randomness selects the object; the subsequent schedule census is exhaustive. No closed global search or fixed-menu exponent barrier is reopened.

## Complete local recurrence

For odd prime ell and b at least one, retain PR521's six ordered ADDRESS fields `(H0,H1,H2,D0,D1,D2)`, each of width b. Its map is

```text
h_address = I6 + s r^T / 4,
s = (1,0,1,-1,0,-1)^T,    r = (1,0,-1,-1,0,1)^T.
```

Its seven chronological events are `a2-=a0`, `a3+=a0`, `a5=(a5+5a0-a2-a3)/4`, a complete recursive ordinary interchange of fields 0 and 5, `a2+=a0`, `a3-=a0`, and `a5=-4a5+3a0+a2+a3`. The reverse inverts every event. Every affine control precedes its target. Denominators and diagonal coefficients are units for every odd ell. Complete spectator ranges remain present in each child.

Let C(U,b) bound a complete ordinary interchange child on the queried row, including its restored recursive workspace. Let A(U,b) bound one retained ordered-affine event, including coefficient preparation, source access, temporary streams, arithmetic and head returns. Let X(U) bound an aligned native XOR scan, including both source/target access and head returns. Let R(V,b) pay row routing, split/merge if needed, descriptors, parking/recovery and any fixed evaluator setup not already in C, A or X. These are the inherited streaming contracts, not unit-cost arithmetic assumptions.

There are nine genuine DATA rows, so V=9U; the dirty private row adds U persistent storage. The paid local recurrence is

```text
B_batch(V,3b) <= 8 C(V/9,b) + 48 A(V/9,b)
                 + 30 X(V/9) + R(V,b).
```

Every one of the eight children acts on the entire private row of actual volume V/9 and width b, including all spectators. The parent ADDRESS width is 3b in each H/D group. V/9 follows from this nine-row input contract; it is not borrowed from PR677's three-row V/3 normalization. For independent batches, sum this entire bill at every invocation. No child is omitted as a recovery step, and no cached h(d) row is retained between batches.

For this fixed row count and fixed literal schedule, the non-child terms are O(V) under the inherited stream contracts. Therefore, if `C(U,b) <= U c(b)`, the conditional local normalization is `B_batch(V,3b)/V <= (8/9)c(b)+O(1)`. This is a typed reduction from B_batch to C, **not** a self-recursion for ordinary multiplication or a new exponent. The separately completed comparison has `12 C + 72 A + 36 X + R_sep`, with the same persistent rows. No measured runtime comparison is asserted, and the routing constants may differ.

Persistent row storage is `10U = 10V/9`. A safe total peak bound is `10U + W_local(V,b) + W_C(U,b)`, where W_local includes affine evaluator, routing and parking scratch. Calls run sequentially and reuse restored child workspace. There are no new full helper rows, source copies, zeroing or erasure operations. Internal scratch, precision for address counters and tape work remain in A, C and W_local. VALUE arithmetic itself is exact XOR.

## Verification and remaining obligations

The checker compares the complete emitted word and both census formulations to the certificate. It checks the endpoint and literal inverse as Laurent polynomials over F2 with one arbitrary input symbol per row. Independently, a bitset matrix interpreter checks all 7,290 input columns over all 729 addresses in `(Z/3)^6`, including every private and source column, and then reverses the whole program. The direct ADDRESS map and chronological affine/child lowering agree on all six rational columns, every order-three address and every one of the 15,625 order-five addresses. The literal reversed affine/child lowering is also checked on every rational basis column.

Eight negative controls reject omitted dirt compensation, omitted private restoration, an omitted direct term, a wrong query direction, a query on a DATA row, a wrong source, removal of the recursive child from its affine wrappers, and an underpriced certificate. A positive control adds two cancelling XORs and requires both to remain charged.

Validation on 2026-10-13, macOS 26.5.2 arm64 with Python 3.14.8: normal and isolated optimized runs passed, including a two-file copy executed from outside the repository. Four additional actual-certificate mutations were rejected by the command-line verifier at their intended guards: query underpricing, a missing event, a histogram change preserving the schedule total, and a changed target matrix. All nine Git source hashes matched. `make selected-record-check` and all 17 `test_selected*.py` tests passed. No repository-wide `make verify`, cold supplier reconstruction, hosted CI or Lean build was run; this package changes no existing generator or selected supplier artifact.

The rank argument is a written scoped proof. The 30-scan optimality is a complete finite census in its stated class, not a formal proof of an unrestricted circuit lower bound. The exact identities and finite replays do not instantiate a supplier or prove the complete multiplication theorem.

Still required before any exponent claim: identify actual supplier calls with this common h and source/target incidence, authorize their private-only batch lifetime, admit their complete row stock and routes, compose the full bit and complex profiles, and check the assembly inequalities. All-size compilation, common-label realization, whole-call hosting and the inherited tape/analytic interfaces remain obligations. This packet does not change either supplier, so it makes no claim about which assembly constraint would bind after integration. It is not an inference from PR974's optimistic budget relaxations.

The final overlap review also found [PR #982](https://github.com/CrocSwap/integer-mult-bounds/pull/982), which removes a dedicated connector by borrowing an output in a product-shear batch. That changes the scratch and permitted-query contract. This package retains one dedicated private row and never queries DATA; it does not compete with or supersede that result.

Attribution, licensing and substantial AI assistance are disclosed in `NOTICE.md`. Session selection and overlap checks are recorded in `CLAIM.md`.
