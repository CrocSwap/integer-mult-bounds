# Complete bank allocation with 120 replicas

This generalizes the preceding 40-replica construction. Let h be the number of changed helpers and S the sum of their entrance dimensions. Every changed helper originally belonged to the rank-24 residual family; its new residual rank is r=24-d. The actual projector and nondegenerate chart checks are unchanged. Require 4 <= r <= 24 and enough rank-4 filler, as checked explicitly.

For each changed helper, allocate 30 width-120 banks, each holding four of its residual blocks of rank r and 30-r rank-4 blocks. This places all 120 replicas. The width identity is 4r+4(30-r)=120. The old five base patterns are tripled. Their remaining rank-4 inventory is 254790 blocks. New helpers consume 30*sum(30-r) of them, so the remaining inventory is always divisible by 30; the program checks nonnegativity. Unchanged rank-24 helpers occupy 24 full banks each. Hence no congruence restriction on S remains.

The complete counts are:

    banks per stage = 352689 - S
    literal stock = 844800 + 5*(352689-S) = 2608245 - 5*S
    normalized stock = 521649 - S

Every helper/replica/stage triple is enumerated: 16587*120*5 = 9952200 assignments. Within a stage each allocated interval is checked disjoint from earlier intervals and each bank fills exactly 120 coordinates. Exact chart conjugation and the existing coordinate-projector completion proof establish the actual dirty swaps. Every distinct layout is checked on all 240 address basis columns in both directions, with nonvacuous omission/repetition controls.

## Namespace extension

The five-stage scalar checker proves the one-replica map on all 23627 independent physical coordinates. For replica t in 0..119 give each data/helper coordinate r the name (t,r), or integer 23627*t+r. This map is injective: division and remainder by23627 recover t and r. The direct sum of120 copies therefore preserves every proved source/target/dirty identity. Each COPY temporary also receives its replica name and retains the checked local lifetime. Stage-private bank names are (stage,bank); assignments include replica explicitly and are exhaustively checked across all120 replicas before a stage's bank sweep completes. This is the same namespace construction for600 stage/replica pairs instead of200; it does not assume free copying, shared clean helpers or a new scalar identity.

## Fully charged cost

The helper profile is multiplied by120 rather than40; four boundary bins receive48*1760 normalized children each. The literal profile is five times the normalized profile and has deficit528000. The finite checker reconstructs every count from the final word and actual bank receipt.

For literal stock W the conservative selector charge is

    2*5*120*((W-1)+16587*120*787).

All route families, operation costs, child costs, selectors, normalizers and stage charges are recomputed. The selector's earlier2^40 comparison was only an incidental bound for the smaller construction. The new checker requires it below2^48 and charges the full integer value inside the total primitive coefficient, independently required below2^80 and below the fixed prime2^127-1. The actual payload guard remains checked at104 bits. Increasing constant replication does not alter the asymptotic exponent; the actual complete moment determines whether retaining extra cancellations is beneficial.

These arguments use the same inherited nested-frame compiler, weighted-chart, routing and all-size interfaces. They do not prove those interfaces or an unconditional integer-multiplication theorem.
