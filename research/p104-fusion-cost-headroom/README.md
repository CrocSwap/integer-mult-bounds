# P104 fusion savings afford less than one extra rank-one child

At the selected complex primitive saving, the local transport savings in
[PR2662](https://github.com/CrocSwap/integer-mult-bounds/pull/2662) and its newer
[PR2712](https://github.com/CrocSwap/integer-mult-bounds/pull/2712) successor are
respectively **0.5273081047...** and **0.5409352129...** rank-one child units,
relative to PR2586. With fixed caller normalization and all other costs fixed,
one additional uncompensated rank-one child outweighs either improvement.
This independently implemented cost certificate checks a changed-profile budget;
it does not claim that either predecessor omitted a charge or that P104 is impossible.

The milestone is a scoped audit. No supplier, selected frontier or kappa changes.
Native correctness and the partial inverse-transpose boundary remain inherited
from the pending predecessors.

## Source-bound profile census

The verifier imports no predecessor Python. It independently recomputes binary
frame dimensions, checks nested transport frames and declared ranks, and recounts
every transport in three exact literal words. Decompressed bytes are authenticated
by SHA256 and original Git blob ID; compression headers are irrelevant. The
selected record binds the benchmark exponent to its actual assembly, including
the certificate digest and kappa identity.

| Word | H1 | H2 | H3 | H4 | H5 | H6 | H7 | H8 | Transports |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PR2586 | 1632 | 74 | 86 | 104 | 48 | 42 | 76 | 8 | 2070 |
| PR2662 | 1504 | 58 | 74 | 93 | 57 | 57 | 91 | 8 | 1942 |
| PR2712 | 1498 | 60 | 74 | 92 | 58 | 56 | 92 | 8 | 1938 |

Every row has rank mass 3542. Each word also has 3104 ADDs, 208 signs, eight
private allocations and eight erasures. These counts do not independently prove
the scalar maps or the correctness of private erasure.

## Exact cost implication

The benchmark is the primitive saving, rather than kappa:

```text
a = 67018507072324140917 / 40000000000000000000000
  = 0.001675462676808103522925
p = 1-a
G(a) = sum_r (old_count_r - new_count_r) * r^p
```

For fixed caller width `m` and role normalization `W`, the local normalized
improvement is `G/(W*m^p)`. A new rank-one child contributes `1/(W*m^p)`.
If `q` is the net extra child numerator after all compensating credits, the
changed construction improves this comparison exactly when `q<G`.

| Change from PR2586 | Certified G at selected a | Unique G=1 crossing in a |
|---|---|---|
| PR2662 endpoint fusion | [0.527308104723768345, 0.527308104723768346] | [0.003182398581, 0.003182398582] |
| PR2712 including shared-chart retiming | [0.540935212882540449, 0.540935212882540450] | [0.003101949576, 0.003101949577] |

PR2712 adds only about 0.01362710816 rank-one units of local savings over PR2662
at this benchmark. [RESULT.json](RESULT.json) records exact rational enclosures
and endpoint signs. Displayed decimal intervals are outward rounded.

This budget depends on the saving being tested. At the planning benchmark
`a=1/99`, the gains lie respectively in
`[3.151173092486566266, 3.151173092486566267]` and
`[3.232718769789614414, 3.232718769789614415]`.
Both then afford three extra rank-one children in this isolated comparison;
neither affords four. This does not establish a favorable complete bill there.

## Proof and arithmetic enclosure

The source-bound profile differences are positive sums of unit merges
`H1+Hr -> H(r+1)`. For PR2662, the multiplicities at `r=2,3,4,5,6` are
`16,28,39,30,15`. PR2712 adds two merges at `r=1`, one at `r=4`, and one at
`r=6`. The checker verifies these identities against the recounted profiles.

For one merge put `g_r(a)=1+r^(1-a)-(r+1)^(1-a)`. Then

```text
g'_r(a) = (r+1)^(1-a)*ln(r+1) - r^(1-a)*ln(r) > 0,   0 <= a <= 1.
```

Indeed `x^(1-a)*ln(x)` strictly increases on `x>=1` in that range. Both total
gains are continuous and strictly increasing, start at zero, and have unique
crossings of one. Certified opposite signs at adjacent `10^-12` grid points
prove the displayed brackets. The verifier uses at most 35 bisections in
`[0,1/50]` and fails on an unresolved interval sign.

All acceptance arithmetic uses `Fraction`. For each `1<=r<=8`, set
`z=(r-1)/(r+1)`. With `N=128`,

```text
L = 2 * sum_{k=0}^{N-1} z^(2k+1)/(2k+1)
L <= ln(r) <= L + 2*z^(2N+1)/((2N+1)*(1-z^2)).
```

The upper remainder replaces every remaining denominator by `2N+1` and sums
the geometric tail. Endpoints are rounded outward to the dyadic grid `2^-160`.
For `0<=a<=1/50`, use `r^(1-a)=r*exp(-a*ln(r))`. On `0<=x<=1`, alternating
Taylor partial sums through degrees 25 and 24 bound `exp(-x)` below and above.
The code checks that domain, reverses the logarithm endpoints because
`exp(-x)` decreases, and rounds outward again. Signed profile differences use
the appropriate endpoint order. No floating-point value enters acceptance.

## Reproduce and controls

Python 3.12, standard library only, no network. From the repository root:

```sh
python3.12 scripts/research_package.py --package research/p104-fusion-cost-headroom
```

Registered commands run normal and optimized verification plus six test groups.
Direct replay also works in a Git-free export containing the package and its
two declared selected inputs:

```sh
python3.12 -I -O -B -W error research/p104-fusion-cost-headroom/verify.py
```

Expected stdout:
`PASS_P104_FUSION_COST_HEADROOM profiles=3 comparisons=2 controls=6 no_new_kappa`.
Replay is read-only and compares the entire recomputed receipt to RESULT.json.
`--out PATH` writes an additional receipt with exclusive creation.

Six mathematical controls cover an incorrect intrinsic rank, equal-mass
different profiles, reversed improvement, an extra uncompensated H1, a negative
saving and the zero-saving boundary. Tests independently use 100-digit Decimal
arithmetic on 32 power cases, four budget values and four root signs. That oracle
is corroboration, not acceptance evidence. Tests distinguish primitive saving
from kappa, accept recompression in a Git-free read-only replay, reject altered
source bytes and receipts, preserve existing output, and exercise resource bounds.

## Limits and next decision

The caller width and role count are fixed. An owner change might remove idle
work, share one added child across calls, change endpoints or change the profile.
Those changes must be priced; their credits are not ruled out here. One rank-one
child shared across two identical calls already costs less than their combined
quoted savings. This is not a complete moment or a bound on every implementation.

Native phases, dirty-state maps, scalar/address movement, rounded private erasure,
ownership, idle/residual charges, output consumers, precision, all-size lifting
and correction of the other 102 forward rows are not checked. The selected
supplier cold replay is not run for this local audit.

Revision 5 decision: finish this audit and narrow the next step to a complete
owner-window delta. These small local gains alone do not justify another
dependent optimization campaign. This is not a family-wide obstruction.

A concurrent [conditional consumer-budget finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/2619#discussioncomment-18955566)
by Jose Manuel examines a specific five-forward/four-dual consumer using PR2458
and PR2712. It reports an unfavorable optimistic full bill even after forgiving
416 rank units per dual. That provisional Discussion calculation is distinct
from this source-bound local comparison and is not recertified by this package.
Check its exact coverage premise before attempting the same consumer; a changed
consumer or changed credit needs its own complete bill.
The final overlap check also found [PR2725](https://github.com/CrocSwap/integer-mult-bounds/pull/2725),
a different X90/N90 retiming from PR2662. Its changed profile is outside this
three-word certificate; no budget conclusion is transferred to it.

## Open next questions

1. For a consumer outside that concurrent scoped screen, can one actual owner
   window realize the changed word with net added numerator below this allowance?
   Pin an explicit caller, assign both old and new rank-3
   through rank-7 transports and decreasing endpoints, and count every idle/return
   credit. The missing physical caller and full invoice block a feasibility
   conclusion. This continues PR2662's handoff.
2. Can an explicit shared endpoint or compensated ADD contract amortize an added
   child across calls? Start with a two-call dirty-state identity, then charge
   retention, restoration and changed children. A sharing declaration alone is
   insufficient. No such construction is supplied here.

Structured questions appear in [TASK.json](TASK.json).

## Sources and credit

Base main `78ceed4139bc61be797f6d38f21a03d972bb3290`, priority revision 5.
PR2662 is pinned at `b67542b2896c21106f3945673bbf5b6e131408cc` and PR2712 at
`afa5d6649460dcdb93489babd74f0ee9d01a4911`. PR2586's original word is retained
through PR2662's exact input. Selected inputs and historical catalogue provenance
are in [SOURCES.json](SOURCES.json); retained words and original notices are
pinned in [PREDECESSORS.json](PREDECESSORS.json).

Credit commdata2338 for PR2662's fusions and cost boundary; ywz65 for PR2712's
retiming, PR2586's physical dual, PR2497 and PR2551; and Nick Petalas for PR2550's
complementary frames. Retained notices preserve Ross Richardson, Hiroki Kumazaki,
Chafik Boukhalfa, Rohan Arun, Adam Gall, Josie Elliston, Ali Romman, icekylinx and
the earlier native/geometry lineage. PR2713's endpoint-rank formalization is
complementary; no rank theorem is claimed new here. Standard logarithm, Taylor
and monotonicity facts are used.

New work by Nick Petalas, Apache-2.0. Substantial AI assistance was used in
derivation, implementation, prose and internal review. A separate internal review
corroborated the arithmetic and source counts; this is not independent human,
proof-assistant, hosted-CI or maintainer review.

## Engineering verification limits

Build the Lever produced the rerunnable source census and exact cost certificate.
Prove It Works required direct literal-word recounts, receipt comparison and an
export replay. Power of Ten bounds each word at 6000 events, each binary frame
at nine dimensions, each input payload at 2 MB, each root search at 35 iterations,
and each test subprocess at 30 seconds. Every new function is under 60 lines.
Explicit `require` checks remain active with `-O`; resources use scoped cleanup.

Rule 3 deviation: CPython, JSON, gzip and rational arithmetic allocate dynamically;
fixed allocation would require replacing the standard-library runtime. This is
limited to one finite CLI run with six pinned predecessor inputs, three words,
eight ranks, 128 log terms, 25 Taylor terms and the bounds above. Limit/exhaustion
controls and read-only export replay check the compensating limits. A service or
untrusted general-purpose extension must reassess allocation before reuse.

Rule 10 scope: the registered checks use warnings-as-errors and both optimization
modes; syntax/static diagnostics apply to the two new Python files. No unrelated
historical build configuration or predecessor executable is changed.

## Maintainer integration: historical selected input

This calculation uses the selected record at `SOURCES.json`'s `base_commit`,
retained byte-for-byte in `inputs/SELECTED-AT-BASE.json` and authenticated against
the original source hash. The live selection is not a runtime dependency.
The original assembly input and all numerical receipts remain unchanged.
This preserves a historical local budget; it does not select a new frontier.
