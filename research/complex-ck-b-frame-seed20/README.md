# A fixed-boundary frame barrier for the selected CK supplier

**Scoped negative result. No new kappa.** The selected CK complex supplier's
1,930 B-phase scalar gates already minimize their paid recursive moment among
all simultaneous frame reassignments that preserve their order, operands and
exact end-of-B register frames. This holds for every power `0 < p < 1`, with
cost `sum H[r] * r**p`. The allowed frames are all subspaces of `F_2^9`, including
ones absent from the retained frame catalogue.

This closes a specific optimization class. It does not claim unique frames,
optimality after reordering or resynthesis, optimality with changed B boundaries,
or optimality of the JP8 provider. The scalar word and every existing repository
file remain unchanged.

## Reproduce

From the repository root, using Python 3.11 or later and its standard library:

```sh
python3 -B research/complex-ck-b-frame-seed20/check.py
```

The command checks the source pins, reconstructs the complete frame domains,
recomputes [CERTIFICATE.json](CERTIFICATE.json), and runs the independent
enumeration checks and negative controls. The core receipt prints:

```text
PASS_CK_FIXED_END_B_FRAME_BOUND gates=1930 flexible=474 profiles=119 exponent=0<p<1
```

The core checker can also be run alone as `python3 -B
research/complex-ck-b-frame-seed20/verify.py`. Neither command writes files,
needs a solver, or fetches data. They fail if pinned inputs or the receipt differ.

## Object, accounting and boundary

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected record at this base is conditional
`kappa = 51110230636731/31250000000000000 = 0.001635527380375392`.
Its [maintainer review](../../docs/research/community-k492-review.md) explains
that #626 retains #622's provider definitions and changes the owner allocation.
The input here is the freshly replayed #622 CK
[canonical word](../community-k492-audit/pr622/replay/ck-local/CANONICAL-WORD.json.gz).
Its decompressed hash matches the CK identity in #626's retained SPEC.
[SOURCES.json](SOURCES.json) pins both heads and eight source files.

Only B frames vary. A, the center cut, precondition, compensation, cleanup tail,
FULL cleanup, initial/final adapters, helpers, coefficients and owners are fixed.
The center phase acts on private copies, so A's ending live frames are B's
starting frames. Each scalar gate uses one common frame for its operands.
Each operand climbs monotonically to it, paying one child whose rank is the
dimension increase. See the retained
[emitter](../complex-k492-owner-repair/code/hpe_emit_local.py) and
[native auditor](../complex-k492-owner-repair/code/hpe_audit_and_transport.py).

For each register touched in B, its last gate is pinned to the original frame.
There are 492 distinct pinned gates. This preserves every end-of-B frame exactly,
including the boundary used by the cold-helper row/column cone check. All later
climbs and all endpoint wrappers therefore stay fixed. The scalar circuit itself
is unchanged on arbitrary input and helper columns, in either orientation.

The baseline B histogram is

```text
H_B = {1:1236, 2:496, 3:200, 4:96}, rank mass = 3212.
```

The checker separately recounts the fixed A, center, tail and final climbs:

```text
H_fixed = {1:1360, 2:56, 3:104, 4:64, 5:70, 6:8, 8:8}.
H_total = {1:2596, 2:552, 3:304, 4:160, 5:70, 6:8, 8:8}.
```

Their sum matches the canonical word's complete local profile. The native
[moment engine](../complex-multicold/engines/moment.py) multiplies
`sum H[r]*r**(1-a)` by the positive factor `m**(a-1)/W`. Thus the result covers
its recursive moment for every `0 < a < 1`. No global assembly or new exponent
is inferred from this local certificate.

## Complete finite domain

Forward propagation takes the join of the current operand frames. Reverse
propagation takes their intersection. Both passes inject the exact last-gate
pins. Induction along each register proves that every feasible frame at gate
`i` lies between the resulting subspaces `L_i` and `U_i`.

The quotient dimensions `dim(U_i/L_i)` are 0, 1 or 2. Their complete subspace
intervals contain 1, 2 or 5 frames respectively. The checker enumerates an
interval by repeatedly adjoining each missing vector. Every intermediate
subspace has a basis extending the lower subspace, so this reaches all of them.

| Gate domains | Number of gates |
| --- | ---: |
| One frame | 1,456 |
| Two frames | 418 |
| Five frames | 56 |

The unrestricted product is `2**418 * 5**56` assignments before shared-register
constraints. This is not a sampled search. A factor for every operand transition
checks subspace inclusion and charges its exact rank difference. These factors
and the pinned boundaries are equivalent to the entire monotone common-frame
constraint in the stated class.

Min-fill variable elimination exhausts that factor graph. A table entry retains
all paid histograms not excluded by the exact dominance rule below. Eliminating
a gate combines all incident factors and enumerates every gate-domain value for
each separator assignment. Discarded histories have no future constraints except
that separator, which is the usual variable-elimination invariant.

The largest separator has five gates. The replay evaluates 4,724 local domain
assignments, retains at most five histograms per conditional table entry, and
ends with 119 profiles. This count is work after exact elimination, not the
number of feasible full schedules. The stopping rule is elimination of every
one of the 474 flexible gates; there is no timeout or incomplete branch.

## Why the pruning and final comparison are exact

For a histogram `H`, let `M(H)=sum r*H[r]` and
`S_k(H)=sum min(r,k)*H[r]`. At a fixed separator, transition ranks telescope, so
all alternatives have the same mass. The implementation asserts this invariant.
It discards `G` only when another profile `H` has equal mass and
`S_k(H) <= S_k(G)` for all integer `1 <= k <= 9`.

To justify that rule, set `f(r)=r**p`, `f(0)=0`, and
`d_k=f(k)-f(k-1)`. For `0<p<1`, the `d_k` decrease and

```text
f(r) = d_9*r + sum_{k=1}^8 (d_k-d_{k+1})*min(r,k).
```

All coefficients on the right are nonnegative. Dominance therefore holds for
every power in the claimed interval and remains valid when adding other factors.
Incomparable profiles are retained rather than resolved by floating arithmetic.

Concave dominance alone leaves 119 profiles. One is the baseline. Every other
profile differs only at ranks 1 through 4. Write its cost minus the baseline as

```text
D(p) = a + b*2**p + c*3**p + d*4**p.
```

The checker establishes `b<=0`, `d>=0` and `a+2*b+3*c+4*d=0` for all 118
alternatives. Thus `D(1)=0`. It also certifies `D'(1)<0` exactly:

```text
D'(1) = (2*b+8*d)*log(2) + 3*c*log(3).
```

Eight terms of the rational atanh series, with its geometric remainder, prove
`69/100 < log(2) < 7/10` and `109/100 < log(3) < 11/10`. Substituting the
appropriate endpoint for each coefficient gives a strictly negative upper
bound in every case. The largest is `-21/25`.

If `c>=0`, then `D'(p)/2**p` is nondecreasing in `p`, because its nonconstant
terms have nonnegative coefficients and bases greater than one. If `c<0`, use
`D'(p)/3**p`: the term with coefficient `b*log(2)` has base `2/3`, so it is
nondecreasing because `b<=0`; the `d*log(4)` term has base `4/3` and is also
nondecreasing. The remaining term is constant. In either case `D'(1)<0` implies
`D'(p)<0` for `p<1`. Integrating to `D(1)=0` gives `D(p)>0` for `0<p<1`.

Every feasible profile is therefore no better than a retained profile, and
every distinct retained profile is worse than the baseline. This proves weak
optimality of the baseline paid moment in the stated finite class. It does not
prove uniqueness of the frame assignment.

## Sprint choice, provenance and limits

The operating-system assignment seed was **20**, selecting the complex-supplier
track and CK via `20 modulo 2`. The algorithm itself is deterministic. Three
candidates and the local claim are recorded in [CLAIM.json](CLAIM.json). No
pinned coordination issue existed. The initial overlap review covered 501 open
PRs through #681, plus the maintainer ledger and relevant prior negative results.

Related #661, by @yuj1r0, proves an all-frame barrier for the R420 **bit** B phase.
This complex instance has coupled frame choices that its per-register argument
does not settle. The contribution here is complete finite-domain elimination
for CK with its cold-helper boundary, plus the four-rank derivative certificate.
No code was imported from #661. #651 studies target hosting and raw-face sharing,
#646 changes the K-triangle skeleton, and #681/#645 change factory circuits or
dirty-input propagation. Those mechanisms are outside this fixed-circuit class.
The final refresh covered 513 open PRs through #693. New #683 concerns mixed
K/M bypass carriers and #687 enumerates one-read relocations under minimal join
frames. Neither changes this result's fixed-order, all-frame scope or supplies
a dependency. The pinned-issue query remained empty.
Immediately before submission, #694 through #697 were also reviewed. #696
lowers complex scalar primitives while preserving frames; #697 changes source
access and helper count. Both lie outside the fixed-circuit class here.

Credit goes to Jeremy Kothe's #622 K-triangle construction and schedule;
Chafik Boukhalfa's #626 owner package; DreamingOfClouds' cold-helper, emitter and
native-verification work; icekylinx's coordinate-total/direct-delivery lineage;
Dominik Scholz's prefix work; the frame-coalescing, recurrence and remaining
contributors retained in the selected review. The unchanged bit supplier is
eumemic's #543. Their results are inputs, not new contributions of this note.

Prepared for **@thakrarsagar**, with substantial **OpenAI Codex** assistance in
research, implementation, proof development, independent checks and writing.
New files use the repository's Apache-2.0 license. No predecessor file is copied
or relicensed.

The finite certificate does not reprove the inherited scalar construction,
uniform compiler, common-label or mutable-basis realization, whole-call hosting,
normalized residuals, precision/tape/exact recovery or analytic transfer.
It is not a Lean proof or a full multiplication-theorem audit. Reordering,
different helper/source interfaces, changed boundary frames, and JP8 remain
outside this result. The expensive full supplier/global replay is not needed to
establish this isolated barrier and was not rerun; the selected-record check was.
The complete package command passed on macOS arm64 with Python 3.11.17 and
3.14.8. [VALIDATION.json](VALIDATION.json) records the checks and their limits.
The same command passed from a clean archive containing only this package and
the eight pinned inputs. [PR #698](https://github.com/CrocSwap/integer-mult-bounds/pull/698)
is the completed sprint handoff.
