# Claim, construction and scope

## Claim

Under the retained interfaces, T(n) = O(n (log n)^(1−κ)) with

    κ = 6830611/10^10 = 0.0006830611.

The bit supplier is PR200's physical bit word with PR186's completed entrance banks. The complex supplier is the v4 source-assisted word of PR194, unchanged, as composed in PR202. The bit side binds:

- packed bit coarse saving 683528191056257/10^18 (PR186's 10^-18 grid);
- PR184's 10^-10 bit saving 6835281/10^10;
- complex saving 219037/312500000.

Without the finite leaf, κ = 6826211/10^10. The gains are 0.913% over PR202 (6768823/10^10) and 0.848% over PR199's leafed PR200 composition (1693287/2500000000). The verifier reproduces both of those numbers from the same tools.

## Inventory on the literal PR200 word

`verify.py` loads PR200's frozen physical word through PR200's own `bit/word.py`. It then runs PR200's `bit/terminal.py` prover with PR200's 34 face0 sinks. That prover checks every source, target and dirty column of the sink-modified word over F2 and against the integer defining decoder, in both directions, with its three mutation controls. Its profile must equal PR200's certified `bit.profile` field by field.

- **Virtual roles:** 18,908.
- **Splices:** the 1,760 compensated aliases are internal splices. Each recipient is a rank-21 gauge read at the deadline of its dead donor. A recipient is charged inside its donor's chain, not as a separate entrance.
- **Deleted sinks:** `terminal.py` deletes the 34 sink registers. Their writes become target shears at the pivot. Each sink role is checked to lie outside the gauges, the splice endpoints and the sources. A deleted sink has no register and therefore no residual to bank.
- **Live chains:** 18,908 − 1,760 − 34 = 17,114. They are exactly the registers in `terminal.py`'s live inventory. Of these, 2,200 are surviving rank-20 entrance gauges, on 220 distinct frames, and 14,914 are completed chains.

## Completed banks (PR186)

For nested commuting split projectors with P_S P_A = P_S, the partial swap D_P(x, y) = (x − Px + Py, y − Py + Px) satisfies D_A D_S^−1 = D_(P_A − P_S). Its rank is h − dim S:

- 4 for a rank-20 entrance;
- 24 for a completed chain.

Following PR186, each rank-20 entrance contributes a rank-4 residual, and each completed chain a rank-24 residual. These are packed into stage-private width-72 banks: 18 × 4 for entrances and 3 × 24 for completed chains. There are three stages and nine physical replicas; the factor three is only the moment normalization. Per stage there are 1,100 entrance banks and 44,742 completed banks. The literal stock is

    3(1,100 + 44,742) + 2 · 9 · 1,760 = 169,206 = 9W,   W = 56402/3.

This removes exactly the 2,200 rank-60 entrance exteriors. The rank mass falls from 1,483,712 to 1,351,712. The deficit stays at 1,936 (72W − mass), and the largest child is 22.

`bank_projectors()` is PR186's function, checked AST-identical to the upstream source. It verifies the partition, idempotence and disjointness of both bank families. On all 144 columns over F2 and over the integers, it checks the full dirty swap and the restoration after the reverse pass. It rejects the omitted-block and repeated-block controls in both rings. A weighted variant of PR197's endpoint check repeats the swap over Z/9, Z/25 and Z/125, using PR186's two patterns, forward and reversed, with the same two controls.

## Schedule and exact charts

The round-8 supplement (`references/round8/BANK-SCHEDULE.md`) schedules the banks:

- route role s of invocation g to bank g·H_s^−1, using fixed rational charts H_s with H_s E_s H_s^−1 = P_s that are pairwise distinct within each bank group;
- choose the prime q after the charts;
- process one low residue class at a time.

The verifier also runs the supplement's GL_2(Z/9) diagnostic.

The charts are explicit here. For each distinct entrance frame with annihilator rows a, the residual rows are 15a − (Σa)·1. Each is checked G-orthogonal to the frame's 20-dimensional source basis, with G = 9I − J. The 24 × 24 matrix B made of the residual rows and that source basis is inverted fraction-free with PR197's `inverse_integer`. The inverse is checked on both sides, and its elementary factors are replayed to the identity.

Over the 220 frames, every chart has at most 186 factors, and every inverse entry and denominator is at most 18. The verifier asserts the bound 2^79. Two slots of one bank place the residual in disjoint coordinate blocks of an invertible chart. Their difference is therefore a nonzero integer matrix, over the common denominator, with entries below 2^80. So no prime q > 2^80 identifies two charts of one group. This discharges, for these fixed charts, the extra prime exclusion that the round-8 review attached to PR186's routing matrices.

## Routing toll

The chart calls are fixed and finite: K = 18((3W − 1) + 17,114 · 72 · (186 + 71)) = 5,701,209,426 < 2^40 selector calls per invocation. As in PR197, they run with the inherited ordinary selector. Their exponent is at most PR184's atom exponent, which `certify()` places strictly between the ordinary saving and 1 minus that saving. They enter the ordered-adapter toll, not the rank children.

## Pricing

`certify()`, `paid_moment()` and `independent_bank_moment()` are PR186's functions, AST-identical to the upstream source. They give the packed coarse saving 683528191056257/10^18, with:

- the next grid point excluded;
- the full worst-case rare-class fallback on bad fraction 10^-16;
- the least atom on the 10^-24 grid;
- an independent base-two moment that agrees.

PR184's `select()` reprices the packed profile on its 10^-10 grid (6835281/10^10, which does not exceed the 10^-18 certificate). Its `assemble()` runs the unchanged 47 strict constraints and seven margins against the v4 complex profile.

The finite leaf follows PR185, which the round-8 review accepted as transferable. Starting from `select()`'s effective saving a_0, three acyclic levels a_(j+1) = (1 − C)C + C·a_j with C = 6835281/10^10 are applied. The verifier checks a_j < C < 1 − a_j at each level and the closed form a_3 = C − C^3(C − a_0). As in PR199, a_3 replaces the effective saving in PR184's assembly. The verifier also reproduces PR202 (6768823/10^10) and PR199 (1693287/2500000000) from PR200's unpacked profile with the same code.

## Mutation controls

Five mutations are rejected:

- a deleted sink counted as a live bank chain;
- a live chain added to the deleted sinks;
- a corrupted packed rank mass;
- a missing rank-60 exterior;
- a wrong entrance chart residual.

## Scope

This is a conditional finite witness. The finite checks cover:

- the literal PR200 word with its terminal sinks;
- the completed bank endpoints;
- the exact entrance charts;
- the paid moments;
- the 47-constraint arithmetic.

The bank routing, stage cover and low-residue streaming remain the conditional contracts of PR186 and the round-8 supplement. That supplement applies to the bit-side GL cover and does not justify concurrent live-core overlap. The weighted compiler, precision and recovery, restored rows, fixed-tape routing and analytic transfer remain inherited assumptions. The complex supplier keeps PR184's scope: no globally renumbered scalar transcript and no full Clifford/router replay.

PR200, PR202, PR197 and PR199 have no maintainer review. The scheduling supplement is not a Lean-checked theorem. No optimality claim is made.
