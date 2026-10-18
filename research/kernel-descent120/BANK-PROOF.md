# Historical bank proof and projector construction

The chart, residual-projector and completion arguments below are inherited. Numerical examples and40-replica inventory are historical; REPLICATION-PROOF.md and the fresh bank receipt specify this package's120-replica construction.

## Sufficient construction

Suppose a literal scalar word has been independently checked to restore all arbitrary helper values and has no final data/helper block. Suppose it uses the inherited nested-frame address compiler, and each newly changed helper has initial nondegenerate frame E of dimension d and final frame I24. The changed helper then has actual residual partial swap D_P with P=I-sigma_E; this is an inherited compiler conclusion, not a conclusion of rank counting. Assume the old frame admissions remain unchanged.

For the present pinned PR249 family, all newly changed helpers previously belonged to the zero-entrance rank24 residual family. There are 14,287 such helpers before new changes. The unchanged nonfull families are 2,200 rank4,22 rank6,5 rank7,48 rank11,23 rank12,2 rank15 helpers. All occur in40 replicas and5 stages.

Let S be the sum of dimensions of the new entrances, m the number of changed helpers. If S is divisible by3, and the required rank4 filler does not exceed84,930 blocks per stage, there is an explicit complete stage-private bank allocation with

  banks_per_stage =117563-S/3,
  literal_stock =869415-5S/3,
  normalized_stock =173883-S/3.

For each new helper of residual rank r=24-d, make ten banks containing four of its rank-r replica blocks and30-r existing rank4 blocks. Each bank has width4r+4(30-r)=120; all40 replicas are assigned. The filler consumption per changed helper is10(6+d). Keep the inherited rank11/rank4, rank7/rank4, rank6,rank12,andrank15 patterns; distribute the remaining rank4 blocks into pure30-block banks and unchanged rank24 blocks into pure5-block banks. All helper identities and intervals are explicitly enumerated. This is sufficient for arbitrary selected changed roles subject to the stated numerical conditions; it is not restricted to pair kernels.

## Exact charts establish the actual projectors

The checker constructs every new chart from the supplied basis U, not from its dimension. Put G=I-J/9, H=U G U^T. Compute a rational row basis V of ker(U G), and set B=[V^T | U^T]. Then B is invertible exactly when E is nondegenerate. Its first24-d columns span the actual G-orthogonal complement. The checker constructs the actual projector

  sigma=U^T H^-1 U G

and checks B^-1(I-sigma)B=diag(I_(24-d),0_d), both inverse products, and U G V^T=0. It emits B and B^-1, exact determinants, and elementary row-operation counts. Every elimination pivot and intermediate coefficient is checked to have numerator and denominator of magnitude below2^80. Thus every relevant nonzero divisor is a unit at each admitted prime q>2^80, including over all inherited Z/q^w. The proof does not infer an orthogonal chart from dimension alone.

For each assigned block b in stage i, use the inherited literal normalizer

  N_b=(b+1) Pi_b embed_i(B^-1),

where Pi_b sends the first residual coordinates in the stage window to the assigned interval and matches ordered complements bijectively. The resulting conjugate of the actual projector is precisely the assigned coordinate projector. The unchanged old-chart factor ceiling548 remains valid if each checked new chart has at most548 factors; permutation/scaling retain the total787 bound.

Distinct blocks in one bank have distinct route keys on a coordinate outside the current24-coordinate stage window. The embedded chart inverse fixes that coordinate. If the two permutations send it to different coordinates, the keys are distinct; if they send it to the same coordinate, the unequal scalars b+1 distinguish them. The scalars and their differences are units because their magnitudes are at most30 and q>2^80. Use the inherited full GL-cover route d*tau_i*N_b^-1; this argument does not justify replacing it by a projective quotient or removing its gates.

## Completion and finite cost

Complete each stage/replica cover sweep before proceeding. All assigned coordinate projectors in a bank annihilate each other and sum to I120. Their dirty partial swaps therefore compose to the full bank swap; arbitrary initial correlations are allowed. The checker independently executes all240 address basis columns in both orders for each distinct layout, and checks that each single-block omission or repetition fails on exactly twice that block's rank.

The full explicit assignment has3,317,400 helper/replica/stage entries. For literal stock W the inherited conservative selector charge is

  2*5*40*((W-1)+16587*120*787).

The literal scalar word, its integer coefficient bill, global formal columns, and the47 strict pricing inequalities require their separate verifiers. This bank result does not delete actual scalar gates or certify an exponent by itself.

## Current results

Regression on the checked132 pair entrances reproduces W=869195,173839 normalized stock,and selector626938189600. The generic checker constructs all132 charts with at most30 factors and exact intermediate numerator/denominator bound4.

Preflight for132 pairs and seven selected triples (dimensions4,3,9,9,9,12,14) gives S=192,139 charts,W=869095,173819 normalized stock,selector626938149600. Maximum chart cost144; every intermediate numerator and denominator has magnitude at most15. All assignments and6,240 endpoint columns plus6,240 nonzero control columns pass. This preflight installs the proposed initial frames synthetically. Re-run against the root worker's literal transformed word outputs before treating it as source-bound composition.

No standalone kappa improvement or Lean certification is claimed here.

## Source-bound collective result

The actual collective156 outputs now pass the generic bank checker:156 actual charts, total entrance rank327, literal stock868870, normalized stock173774, selector626938059600. All3,317,400 helper/replica/stage assignments pass, as do6,720 endpoint and6,720 nonzero control columns. Every new chart uses at most156 factors and every exact intermediate numerator/denominator is at most135, preserving the inherited548/787 ceilings and2^80 prime guard. See `collective156/BANK-REVIEW.json` and `collective156/BANK-CHARTS.json`; `collective156/SOURCE-BINDING.json` binds the actual parent word and verifier inputs.

## Source-bound pooled result

The actual pooled word passes with252 charts and entrance rank1047. Literal stock867670; normalized stock173534; selector626937579600. Its largest chart costs200 factors; all rational intermediate numerators/denominators are at most704. All3,317,400 assignments and10,560 forward/backward endpoint columns plus10,560 nonzero controls pass. The inherited548/787 factor ceilings and2^80 prime guard are unchanged. `pooled/SOURCE-BINDING.json` pins the concrete input word and bank receipts. The original pre-admission fundamental word is superseded because it included singular frames.

## Source-bound multiple-checkpoint result

The actual multicut word passes with518 charts and entrance rank1344. Literal stock867175; normalized stock173435; selector626937381600. Largest chart200 factors; all exact intermediate numerators/denominators<=704. All3,317,400 assignments and10,560 endpoint columns plus10,560 nonzero controls pass. Banks depend on actual initial/final frames, so using different verified scalar checkpoint positions introduces no additional bank geometry obligation. The scalar word and global columns remain separate checks. See `multicut/SOURCE-BINDING.json`.
