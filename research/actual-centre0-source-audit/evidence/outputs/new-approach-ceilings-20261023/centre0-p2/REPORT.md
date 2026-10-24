# Exact remaining recursive budget of the corrected-centre p2 relaxation

**Conditional result: at most 12 additional positive-rank recursive calls fit
the declared optimistic invoice over the full interval
[.0030217758,.00339999].** Twelve H1 calls pass; thirteen fail at the included
right endpoint. A single extra rank-12 child also fits throughout the interval;
a rank-13 child fails there. These are exact rank-model bounds for an explicitly
unrealized independent-main target grant. They are not completed caller,
physical-supplier, compiler-reserve or κ admission.

## Source-profile match and retained failure

The source-derived corrected local offer is frozen from
`outputs/seven-mode-producer-feasibility-20261023/CORRECTED-DERIVATION.json`,
SHA256 `d40187525bd50b77f277de46575097c6d34a18af96802e7aec7b4f49213465d4`,
with its report. Original source is Dugongue's #4948 at
`86e474038e05f99a76d41f71d81946ad2327e4a4`. It restores one actual H8 centre,
retunes four repair rows, and retains all eight H1 repairs. Forward/backward
local paid profiles are equal:

```
N={1:2209,2:412,3:510,4:127,5:40,8:1}.
```

This profile is a source-derived edit specification; no changed native word was
emitted or run. We match the optimistic p2 incidence exactly as

```
P=2N+336 H1+224 H8
 ={1:4754,2:824,3:1020,4:254,5:80,8:226}.
```

The rank-one coefficient is `2*(2201+8)+3*112`: all 16 repair calls across two
FULLs remain. The H8 coefficient is `224+2`: the one paid IDLE plus one restored
centre per FULL. There is no H8-minus-H1 cancellation. The corrected local
finite bill also adds 714 scalar ADDs per FULL, 1428 for two; these are separate
from recursive rank moments and have not been converted into an H1 budget.

The target grant is

```
T={4:56,7:14,8:94,9:876,17:224}
 =2{4:28,7:7,8:47,9:326}+224 H9+224 H17.
```

It credits 816 original helpers once and **grants** 448 autonomous main jobs.
Those main endpoints are unproved. The numerical target/old-p2 premise was
originally displayed in the frozen active-feed PROPOSAL.md whose actual h
endpoint failed; that failure is preserved and checked. Astra's new design
receipt explicitly retains status
`AUTHOR_DESIGN_OPTIMISM_ONLY_UNREALIZED_TARGET_GRANT`. The corrected local G
does not repair that failed caller merely by changing its numerical profile.
No whole-caller engine is imported with altered target data.

## Uniform proof and sharp integer limits

Set `H_r(C)=r^(1-C)`, `H_0=0`, and
`M(C)=sum T[r] H_r(C)-sum P[r] H_r(C)`. On the exact closed interval
`a=15108879/5000000000`, `b=339999/100000000`, the derivative is

```
M'(C)=sum P[r] H_r(C) log r - sum T[r] H_r(C) log r.
```

Every positive H_r is nonincreasing in C. Using outward rational bounds,

```
M'(C) <= sum P[r] upper(H_r(a)) upper(log r)
        -sum T[r] lower(H_r(b)) lower(log r)
       < -19660.823331812427897464928484 < 0.
```

This proves strict decrease over the whole interval; it is not extrapolation
from two point tests. The minimum is therefore at the included right endpoint,
where independent rational intervals enclose

```
M(b) in [12.804117221917453035517808,
         12.804117221917453035517809].
```

Consequently the exact largest integer k for `M(C)-k*H1(C)>0` throughout the
domain is **k=12**. The residual margin after 12 H1 is at least
`.804117221917453035517808`; after 13 H1 the right-endpoint margin is at most
`-.195882778082546964482191`. Every positive-rank call has H_r>=1 here, so any
13 such added calls also fail there in this declared additive invoice model.
This is not a lower bound on shared implementations or alternative suppliers.

For the one-child rank limit, `upper(H12(a))<lower(M(b))` proves rank 12 fits
everywhere; `lower(H13(b))>upper(M(b))` rejects rank 13 at b. Larger ranks cost
still more because 1-C>0. Thus 12 is also the exact largest integer rank of one
additional child that fits uniformly. A mixed extra bill K(C) must be tested
as `K(C)<M(C)`; the two integer limits do not make all smaller mixed bills fit.

No compiler epsilon is invented for this design. Positive raw margin remains
subject to both paid completion/splitting tails, actual ambient/compiler binding,
a funded strict reserve, finite tape/routing/owned-storage/precision constants,
the actual ordinary interface and complete outer transfer. The retained #4610
route is described in the parent baseline ledger, not proved for this p2 grant.

## Verification and smallest next gate

`check_burden.py` authenticates six frozen inputs and reuses the previously
independently written p19 rational engine (logarithm atanh series plus alternating
exponential enclosures). It imports neither Astra's author-design engine nor
any native/caller/compiler implementation. Engine range conditions are checked
explicitly outside assertions, including `log r<3` for r<=17 and `C log r<1/50`.
Normal/optimized warning-strict outputs are byte-identical. Mutations omitting
2H8, deleting 16H1, or promoting the unrealized target status are rejected.
The author's endpoint enclosures are contained in the independent enclosures.

```
python3 -I -W error -B outputs/new-approach-ceilings-20261023/centre0-p2/check_burden.py
python3 -I -O -W error -B outputs/new-approach-ceilings-20261023/centre0-p2/check_burden.py
```

This bounded check takes below one second per mode here. No precision of an
unchanged raw crossing was extracted. The #5083 packet remains frozen separately.

The smallest useful next task is source/embedding admission: supply a literal
whole caller returning all 448 granted main jobs and every helper, then price
every extra recursive correction. If that bill contains 13 new positive-rank
calls, or one rank>=13 call, the present target grant already fails at b. A
smaller correction still needs its full pointwise bill and the compiler tail/
reserve gates. Unknown finite work is payable and is not funded by these raw
rank-model units. Root retains the native/caller expansion gate.

Credit Astra's changed-producer design and optimistic receipt; the production
worker's actual-centre source derivation; Dugongue #4948/#4929, Cao Yifan, Cinna
Davis, zxv, Jacob Alan Sussman and the retained native/helper/compiler lineage;
the prior p19 independent interval engine and the failed active-feed proposal
whose exact scope remains visible. Substantial OpenAI Codex assistance.
Local-only result, Apache-2.0; no public write, new κ or selected-frontier change.
