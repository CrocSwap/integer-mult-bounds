# One center-basis shear lowers the historical dyadic scalar bill

**Finite complex-supplier circuit improvement; no new kappa.** A single
unimodular reparameterization of the historical rank-h dyadic central factor
lowers its complete scalar-operation bound at h=26. The center count, side
circuit, all-incidence frame groups, recursive children and dirty restoration
contract are retained.

| Count | Original | Replacement | Saved |
|---|---:|---:|---:|
| Gather G | 14,100 | 12,352 | 1,748 |
| Scatter H | 31,281 | 31,557 | −276 |
| G + H | 45,381 | 43,909 | 1,472 |
| Complete signed invocation | 786,938 | 783,994 | 2,944 |
| Complete three-stage scalar bound | 15,959,102,640,000 | 15,899,398,320,000 | 59,704,320,000 |

These are the historical circuit's addition/subtraction/halving charges,
not runtime measurements, selected JP8/CK primitive counts or new recursive
rank savings. The unchanged rank ledger means this improvement supplies no
larger multiplication exponent. It is useful as a fully priced local circuit
rewrite and an exact example of center-basis optimization.

## Reproduce

From the repository root with Python 3.11+ and its standard library:

```sh
python3 -I -B research/dyadic-center-basis-shear/verify.py
```

Expected final line:

```text
PASS_DYADIC_CENTER_BASIS_SHEAR h=26 moves=1300 admissible=650 G+H=45381->43909 full_scalar_saved=59704320000 no_new_kappa
```

The command recomputes every field of [CERTIFICATE.json](CERTIFICATE.json).
`--out /fresh/path.json` emits the recomputed certificate and refuses an
existing output. It verifies [SOURCES.json](SOURCES.json) before inherited
imports. An assertion-enabled isolated subprocess runs the original
constructors even when the outer verifier is invoked with `-O`.

The actual adapter is `circuit.shear(original_factor, 1, 2, -1)`, consumed
by `source_worker.py` through the unchanged original `invoke` executor.
No source patch or selected-record change is required to replay it.

## Base, selection and dependency boundary

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The OS-random assignment
seed was **20**, complex-supplier track. [SELECTION.json](SELECTION.json)
records the three candidates, scope, initial optimistic budget and bounded
search. Current CK/JP8 coefficient reuse overlaps #769/#787/#793; fixed-order
A/B frame freedom is covered by #776. Seed `20 % 3 = 2` selected the historical
center factor. Seed 20 also chooses the first of its two tied one-shear
minimizers. No pinned sprint issue existed, so the claim is local.

The selected certificate was followed to the actual
[#626 construction](../complex-k492-owner-repair/README.md),
[review](../../docs/research/community-k492-review.md) and
[assembly](../community-k492-audit/pr626/replay/ASSEMBLY.json).
The current accepted conditional value at this base remains
`51110230636731/31250000000000000 = 0.001635527380375392`.
Its source head is `660de893d27bb7abd1d5b01b1640207528a5c851`, with reviewed
#622 `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6` and retained #543
`2065fe4f72a914d907f1046603f5a36f17018535`. This package changes none of them.

The object improved here is Douglas R. Colkitt's
[historical dyadic center](../../docs/research/dyadic-central-factor.md),
[written factor/phase argument](../../notes/dyadic-central-factor.tex), and
[implementation](../../scripts/experiments/complex_centers.py), retained in
commit `d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`. The old note's h=26 saving
and `2^-31` language describe its historical checkpoint. They are not the
current frontier. There is no pending-PR code dependency, and no claim to
supersede contemporary E8 suppliers or their coefficient optimizations.

## Exact construction

Let `v=binom(h,3)` and `T0={0,1,2}`. For triple indicators `s,t`, the source
has scatter numerators U and gather coefficients V:

    U[S,0] = s0+s1+s2−1,     U[S,i] = si−s0  (i≥1),
    V[0,T] = 1,              V[i,T] = ti−1(i∈T0) (i≥1).

Its central map is `UV/2`, with `(UV)[S,T]=|S∩T|−1`.
Use center-coordinate matrix `A=I−E12`, whose inverse is `I+E12`:

    V' = A V,       U' = U A^−1.

Only one gather row and one scatter column change:

    V'[1,T] = t1−t2,
    U'[S,2] = s1+s2−2s0.

All other entries are unchanged. Since `E12²=0`, the product `U'V'=UV`
is exact in every dimension. The new gather still uses only 0,±1, while
scatter numerators lie in 0,±1,±2. Numerator −2 means a single subtraction
with scalar coefficient −1. This extends the old `verify_factor` alphabet
check (which excluded −2) but introduces no primitive operation: the old
negative scatter phase already applies −1 when an original numerator is +2.
The optional checker explicitly admits and prices both signs of 2; the
original checker remains untouched and is tested to reject the extended
alphabet for its original reason.

## Dirty restoration and why no adapter is paid

Let c be the arbitrary initial contents of the existing h center roles.
The central subsequence acts as

    y ← y − U'c/2,
    c ← c + V'x,
    y ← y + U'c/2,
    c ← c − V'x.

It leaves x and c unchanged and adds `U'V'x/2 = UVx/2` to y. The inverse
sequence subtracts this map and also restores c. No actual register is
converted from c to Ac: the new scatter cancels the same arbitrary dirty c
on its two visits. Consequently there is no initial/final center-basis
conversion and no additional helper or restoration work.

The unchanged side subsequence supplies the complementary side map, so the
complete twelve-operation invocation is still `y ← y+x`, or `y ← y−x`
in reverse. Full exact formal-variable replay checks all 998 independent
source/target/side/center columns at h=8 and all 2,767 at h=10, in both
directions. Separately, the independent central implementation checks 356
basis executions at h=4,6,8 in coordinates `(x,2y,c)`; h<8 is algebra-only
coverage, not a claim of a complete historical supplier at those sizes.

## Complete cost and frame accounting

Each nonzero gather entry costs one signed addition. A scatter numerator
±2 costs one signed addition; ±1 costs one halving and one signed addition.
Every source access represented by those updates is counted. The side
mixer M, copy C and weighted-injection J terms are freshly recounted from the
unchanged h=26 side topology:

    M=158444, C=10400, J=10400,
    fixed side bill = 4M + 2C + 4J = 696176.

The factors 4,2,4 include the inverse mixers, both copies and both weighted
injections. The full invocation costs `4M+2C+4J+2G+2H`, including both
central scatters and inverse gather. There are `3v²=20,280,000` invocations.
Thus the full scalar-bound decrease is `6v²·1472 = 59,704,320,000`.

For the chosen shear, the old gather row has `binom(h−1,3)` nonzeros; the new
one has `2 binom(h−2,2)`. The old affected scatter column costs
`4 binom(h−2,2)`. Counting whether s0 is present and how many of s1,s2 are
present gives new cost `5 binom(h−2,2)`. Therefore

    saving in G+H = binom(h−1,3) − 3 binom(h−2,2)
                  = (h−10)(h−2)(h−3)/6.

This improves the scalar bill exactly when h>10, is neutral at h=10, and
loses 10 operations at h=8. The replay checks the chosen formula against
actual factors for every even h from 8 through 40. This is a proof for the
chosen shear, not an unrestricted optimality theorem.

Crucially, retain **all** original data and center incidences in each common
gather/scatter frame group, including incidences with zero scalar coefficient.
The inherited phase argument explicitly permits scalar factor changes under
this rule. No gate is split into new frames and no incidence is silently
removed. Every center retains its downward residual of dimension h; the
first/third-stage reuse still preserves center indices. Thus all helpers,
source corrections, endpoint repairs and recursive children keep their old
accounting:

| Ledger item | Unchanged value at h=26 |
|---|---:|
| Center roles per invocation | 26 |
| Side roles per invocation | 89,622 |
| m | 17,576 |
| W | 1,247,192,960,000 |
| L | 13,709,280,000 |
| s | 21,920,655,731,520,000 |
| Wm−s | 7,733,440,000 |

The source's scalar node allowance `E=64(W+m+1)³` is unchanged. The replay
checks `E > 4 steps_new + 8s + 8W + 8m`, and reproduces its conditional
stopped recurrence guard `A(e)≤s A(e/m)+E` with the same leaf rule. All
coefficients are still realized using the inherited signed-addition/halving
alphabet; its operation-count-based guard remains applicable. This does
not supply a new tight numerical-growth, tape or all-size realization proof.
The paid rank profile and its saving are unchanged. Another historical
supplier/assembly constraint cannot be improved by this scalar reduction
alone, and no assembly rerun or new exponent is claimed.

## Bounded search and independent evidence

The primary census exhausts exactly `2h(h−1)=1300` single elementary shears
`V_i←V_i+εV_j`, `U_j←U_j−εU_i`, with `i≠j`, `ε∈{−1,+1}`, at h=26.
It accepts only gather magnitudes ≤1 and scatter numerator magnitudes ≤2.
Exactly 650 moves meet both restrictions. The minimum change in G+H is
−1472, attained by `(i,j,ε)=(1,2,−1)` and `(2,1,−1)`. The source-bound
census records all coverage counts, the complete cost histogram and a
canonical transcript hash. The stopping rule is exhaustive completion of
this one-shear neighborhood; no multi-step search is being claimed.

The independent implementation imports no producer or repository code.
It also checks the one-shear census by 16 coordinate-type/sign orbits. The
source factors are invariant, up to triple relabeling, under exchanging
coordinates 1 and 2 and permuting coordinates 3 through h−1. Thus the
classes {0}, {1,2}, {3,...,h−1} give eight ordered distinct-coordinate types
and two signs, with exact orbit multiplicities. Their admissibility, full
cost histogram and minimum must match the 1,300-move implementation.
This is a different finite counting method, not a larger search.

The independent implementation contracts the three distinguished coordinates and the remaining intersection
cardinality separately, checks all 6,760,000 coefficients, and hashes the
same complete row-major coefficient stream as the sparse-multiplication
checker. Both costs and coefficient hashes must agree. Its separately
executed integer central circuits preserve all dirty inputs and detect
omitted restoration, omitted dirty cancellation, a gather-only rewrite and
the wrong sign on a −2 numerator.

Additional checks, exact failure controls, overlap refresh and environment
are recorded in [VALIDATION.md](VALIDATION.md). No failed search is promoted
to an impossibility theorem. Optimality is limited to the declared finite
one-shear alphabet; general unimodular bases, multiple shears, new helpers,
new frame schedules and current supplier constructions remain open here.

## Attribution and remaining obligations

Prepared by **Curtis Dransfield with substantial OpenAI Codex assistance** in
construction, proof, code, verification and writing, including a separate
Codex worker's independent implementation and review. This is methodological
independence, not independent human peer review. New files use the repository's
Apache-2.0 license.

Credit Douglas R. Colkitt for the historical dyadic factor, disjoint-tensor
side circuit, dirty transparent schedule, frame proof and recurrence ledger,
with their existing AI disclosures. The selected construction's Jeremy Kothe,
Chafik Boukhalfa, eumemic, DreamingOfClouds, Rohan Arun and retained predecessor
credits remain in its unchanged sources. Contemporary coefficient-circuit
work is credited as related scope, not imported or combined savings.

This package freshly rebuilds h=26 scalar topology/counts and central
coefficients. Its unchanged h=26 side coefficient/phase proofs are inherited;
full dirty-input invocation replay is finite at h=8,10. The full tensorized
network, upstream analytic transfer, fixed-tape/precision and all-size
compiler assumptions are not newly proved. Neither the historical certificate
nor the selected frontier is edited, and no Lean or full multiplication-theorem
verification is asserted.
