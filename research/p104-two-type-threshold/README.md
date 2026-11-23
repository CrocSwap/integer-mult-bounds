# Two-type raw price threshold with paid half-splits

This is an aggregate price/stock result for the literal Gaussian 48-call word in [PR #8072](https://github.com/CrocSwap/integer-mult-bounds/pull/8072), head `75f7e1c44f48c43983016bcf8878c4d9e5e87c62`. It is **not a native signed multiplier, a new qualified κ, an ownership proof, or a complete economic invoice**. Source reconstruction, conclusions, and the remaining open boundary are distinct.

## Model and result

Rebuilding the staged canonical word gives 52,608 productive target ports, 281,568 paid ports, and 183,312 rank-one paid ports in the unscaled type. Type 0 has those ranks; type 1 scales every target and paid rank by 2. A type-0 rank-one paid port may be replaced by two rank-1/2 paid ports, and a type-1 rank-two paid port by two rank-one ports. A type has a fixed **integer** split count in `0..183312`. Its occurrence frequency is any nonnegative real number; frequencies are not both zero.

At rate `c`, a rank `r` paid port demands `r^(1-c)` and a rank `k` target supplies `k^(1-c)`, multiplied by its type frequency. Fractional flow is permitted exactly where `5r <= 4k`. Let `c_int` be the supremum of rates `0 <= c <= 1` for which that aggregate flow exists. The following are certified strict bounds:

```text
0.003898466610885757242 < c_int < 0.003898466610885757243
```

The feasible lower witness has 1,006 type-0 splits, no type-1 splits, and `frequency_1/frequency_0` approximately `90.24604144478511564111`. The exact rational frequency and 51-edge rational flow are in `CERTIFICATE.json`. The flow uses lower target-price and upper paid-price bounds, hence funds the true prices strictly.

If split counts are instead permitted to be arbitrary reals, the corresponding relaxation has a **different** limit:

```text
0.003898466621505769638 < c_relaxed < 0.003898466621505769639
```

Its lower witness uses approximately 1,005.279848031309 splits of type 0. That is not a fixed whole-count type installation; it is included to separate the linear-program relaxation from the integer claim. Both upper proofs allow arbitrary nonnegative real frequencies and type-1 split counts, so they do not depend on a numerical optimizer or a restricted search grid.

The original source's installed raw trial `17145637307/2^42`, type frequencies `5:451`, and 1,008 type-0 splits provide a strict positive comparison control. The new bracket is a **raw** ceiling for this fixed two-scale and split model only; it does not price ordinary work, finite losses, timing, activation, storage, owner returns, or the complete signed caller.

## A broader raw obstruction at 0.0039

For the same unsplit base word at `c = 0.0039`, directed arithmetic gives total productive capacity minus paid demand strictly below `-1.53934254762`. Scaling every rank by a positive factor `s` multiplies both totals by `s^(1-c)`. Thus any finite mixture of such copies with nonnegative frequencies, at least one of which is positive, has a negative total margin.

The conclusion remains true if any paid rank `r` is subdivided into finitely many positive ranks whose sum is `r`: since `0 < 1-c < 1`, their powered costs sum to at least `r^(1-c)`, strictly more for a subdivision into two or more positive parts. This gives a raw total-price obstruction for **arbitrary finite positive scales and paid subdivisions**, with the productive word and its scaled ranks fixed. It already holds when all rank-compatibility requirements are relaxed. Changing productive ranks, changing the source word, or allowing other financial credits is outside this corollary. The narrower two-type integer bracket above gives the sharper bound near the crossing.

## Exact proof

For each paid-rank cutoff `h`, the necessary Hall inequality is

```text
sum(k^(1-c) for targets with 4k >= 5h)
  - sum(r^(1-c) for paid ports with r >= h) >= 0.
```

The verifier reconstructs each complete histogram from a curated scientific-source snapshot materialized from the authenticated stage, then rounds the prices outward with integer square roots and products. It brackets the exponent on a `2^-128` grid and values on a `2^-224` grid. A separately written rational atanh/log and exponential-series routine checks overlapping enclosures at representative ranks. All claimed signs and multipliers are exact rational arithmetic; SciPy, floating-point fitting, and the exploratory root digits are not used in the proof.

For upper certificates let `w0,w1` be the nonnegative frequencies, `u=w0*n0/183312`, and `v=w1*n1/183312`. Each stored row is an optimistic directed upper bound of a necessary Hall margin in the coefficient order `(w0,w1,u,v)`, multiplied by `2^224`. A feasible actual margin must make every row nonnegative. The positive combinations in `CERTIFICATE.json` cancel the last three coefficients exactly and leave a negative coefficient on `w0`:

* At the integer upper endpoint, the `n0 <= 1005` proof combines cutoff 1, cutoff 2, `1005*w0 - 183312*u >= 0`, and `v >= 0`. The other proof combines the total, cutoff 2, `183312*u - 1006*w0 >= 0`, and `v >= 0`. The two cases exhaust integer `n0`. Their resulting constants, after division by `2^224`, are approximately `-0.2778994044` and `-9.01258718e-14` respectively.
* At the fractional upper endpoint, one combination of the total, cutoff 1, cutoff 2, and `v >= 0` has constant approximately `-1.33690257e-13` in the same units. The exact positive multipliers and coefficients, including the zero cancellations, are saved rather than rounded.

If `w0 > 0`, a positive combination of nonnegative rows cannot be negative. If `w0 = 0`, the same strict-positive multipliers force `v = 0`; cutoff 2 then has a strictly negative coefficient on `w1`, forcing `w1 = 0`, contrary to the nonzero-frequency requirement. Thus the proofs also cover the pure type-1 endpoint.

The upper is global in the stated rate domain: if a feasible flow exists at `c2` and `c1 < c2`, let `delta=c2-c1` and multiply every old flow out of rank `r` by `r^delta`. This exactly funds each new paid demand. Since every allowed edge satisfies `r < k`, the load arriving at a target of rank `k` grows by at most `k^delta`, the same factor as that target's new capacity. Therefore feasibility is downward closed, so the certified separator at either upper endpoint also excludes every higher rate in the model.

## Replay and controls

From this directory run:

```sh
python3.12 -I -B verify.py
```

Python 3.12 is required; no network, Git, SciPy, or third-party Python package is used by the standalone checker. It checks the minimal #8072 source receipt and the public-file allowlist, reconstructs the canonical graph, labelled word and census from the curated source files, recomputes every exact row and flow, verifies the saved certificate, then runs the controls. It rejects changed dual multipliers, a mutated source census, one extra unavailable split, the neighboring split counts at the lower witness ratio, and a forbidden transfer. It also checks the old source trial and the independent enclosure method. `VERIFY.json` registers the command for the repository's generic research replay; standalone operation does not require the research runner or the original checkout.

`source/SOURCE-RECEIPT.json` records the public #8072 repository, head, scientific file blob IDs, predecessor archive digest, and the exact curated source-file hashes. The private evidence run authenticated and restored the complete original archive before making this snapshot. The public replay checks the snapshot and reconstructs the graph and word, but does **not** itself restore that omitted complete archive or check the current hosted head and CI. `PUBLIC-FILES.json` gives the exact SHA-256 allowlist of every public file other than the allowlist itself.

## Open next questions

* Can the integer-count lower witness be realized with actual native labels, chronology, source windows, return ownership and finite precision? The aggregate flow leaves all of these obligations open.
* After a valid implementation exists, can its ordinary and numerical complete invoices support an improvement in signed κ? The raw bracket alone does not answer that question.
* Do additional scale types, different paid subdivisions, productive changes, or a changed word improve the limit? These possibilities are outside this fixed two-type result.
