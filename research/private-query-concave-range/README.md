# Private-query cost on the full concave range

For the fixed retained 112-port E8 Gram correction and private source
frames, the saved optimum extends to the whole range `0 <= b <= 1`:
the bill `sum_j r_j^(1-b)` has minimum `8*8^(1-b)`. The new scalar step
is the uniform inequality `7*9^a + 2 - 8*8^a > 2/27` for `0 <= a <= 1`.
It uses five exact integer comparisons and a written derivative argument.
This is a scoped negative result. It supplies no new circuit or kappa.

Read [PROOF.md](PROOF.md) for the exact model and argument. The result
uses six historical premises: Gram rank eight, minimum support 53,
private frame ranks one through nine, capacity at most 36 below rank
eight, total private rank at least 64 with no rank-nine frame at equality,
and attainment by eight rank-eight coordinate gathers. The proof lists
the rank range as part of its model. Its five numbered facts give the
other premises. The fixed Gram matrix is `G = R R^T/4`, over Q, R or C.
Here `R` is the 112 by 8 matrix `root_lines[8:]` in the retained prototype;
the full prototype has 120 rows. Each private frame is a linear subspace
`F_j` of `F_2^9`, and `r_j = dim_F2(F_j)`. It contains every binary source
label in its query's support and may strictly contain their minimal span.
Scalar queries may be redundant.

The [historical independent proof](historical/work/autonomous-kappa-run/framework/PRIVATE64-INDEPENDENT-REVIEW.md)
and the [sharp-rank proof](historical/work/p518-next/complex/paired-five/E8-PRIVATE-QUERY-OPTIMUM64.md)
are included with their finite data and independent checkers. The
[old weighted proof](historical/work/autonomous-kappa-run/framework/private64-weighted/PROOF.md)
only covers `0 < b <= 1/32`. The new extension preserves that model.
The original historical files remain byte-identical. Their statements
about old publication status and old replay scope are historical.

The later [one-sided decoder theorem](https://github.com/CrocSwap/integer-mult-bounds/blob/4c32ac3b88d63ad06d2b30e526aa07a12929db36/research/one-sided-decoders-all-m/README.md)
proves a characteristic-zero unweighted floor and a unique cost-64
decoder in its stated dense-pairing Gram model. It is related work.
The present package retains its own fixed-Gram premise proof and does
not claim a new unweighted floor. A reduction to that later theorem
must check the source-label and cost conventions before it can replace
the historical dependencies. The new scalar inequality and weighted
range are the proposed contribution.

The eight coordinate gathers attain equality for the full range.
At `b > 1`, enlarging all eight frames to rank nine gives a smaller
bill, so the upper endpoint is exact for this cost law. Shared carriers,
native blocks, productive ownership, changed Gram codes and physical
execution costs are outside the claim. The optional fitting-matrix
extensions in historical notes are not part of this package's new claim.

From this package directory, with Python 3.10 or later:

```sh
python3 -B verify.py --build /tmp/private-query-concave-replay
```

The build path must not exist. Only the standard library is required.
The final line must be:

```text
PASS_PRIVATE_QUERY_CONCAVE_RANGE_INPUTS 2/27 1735600
```

The replay checks the scalar inputs in normal and optimized Python,
repeats the independent scalar calculation, and regenerates the geometric
inputs from the pinned root and label data. It checks all 43,435 rank-seven
frames, all 1,735,600 profiles of total rank at most 63, and all 195,666
rank partitions of total 64. The last check excludes each of the 79,403
partitions with a rank-nine frame. The runner rejects optimized Python
because the historical checkers use assertions. The standalone scalar
checker works with optimized Python.

These finite checks do not prove the written capacity arguments, the
two final query-profile contradictions, or the derivative argument.
Those proofs and the historical independent reviews are included.
The run does not repeat fitting-rigidity certificates or any physical
supplier verification. `replayed-receipt.json` and `replay.log` record
the independent cleanup review replay of the current source manifest.
`SOURCE-MANIFEST.json` records exact local
source paths and SHA256 hashes. No current exponent is inferred from
the old cost records.

The fixed E8 root construction is Jacob Sussman's work, at
[the recorded source commit](https://github.com/jacobalansussman/wht-power-saving-lean/tree/9c94857bbaee886f8649edee0bc2d3c738f9555e).
The data came through @icekylinx's
[PR #531](https://github.com/CrocSwap/integer-mult-bounds/pull/531).
The copied [root and label data](https://github.com/CrocSwap/integer-mult-bounds/blob/e07a8a3f9f79c22113398a0c5dbbc7601f489b3e/research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json)
are byte-identical to that Git object. Its
[source notice](https://github.com/CrocSwap/integer-mult-bounds/blob/e07a8a3f9f79c22113398a0c5dbbc7601f489b3e/research/direct-delivery504-global/NOTICE.md)
and [credit record](https://github.com/CrocSwap/integer-mult-bounds/blob/e07a8a3f9f79c22113398a0c5dbbc7601f489b3e/research/direct-delivery504-global/SOURCES.json)
are retained with the copied data. `SOURCE-MANIFEST.json` binds the bytes.
OpenAI Codex and research agents prepared the local
proof and independent checks under the user's direction. No independent
human review is claimed.

## Open next questions

Can the weighted range be derived directly from the later one-sided
decoder theorem with the same source-label convention? The first step
is to bind the two root and label coordinate systems and compare the
uncorrected cost definitions. That proof is not supplied here. A physical
shared-carrier method has a different payment rule and needs a separate
analysis before this private-query bound applies.
