# Adaptive complete row bills

At type i, let R_i be a finite nonempty set of nonnegative rational rows of
length n. A row must include all child, adapter and restoration charges of its
declared contract. Each node can choose its row independently. The local toll
is one. Define T(x)_i = max_{r in R_i} r x. A policy selects one row per type;
its matrix is A. These are mathematical costs, not physical native operations.

The certificate has exactly two possible conclusions:

1. A rational u >= 1 satisfies u = 1 + T(u). A policy A attains every row:
   u = 1 + Au. The value u is the exact worst total over all finite depths and
   adaptive choices. All allowed rows have the common strict contraction
   bound r u <= q u_i, where q = max_i (u_i-1)/u_i < 1.
2. A legal policy A has a nonzero rational v >= 0 with Av >= v. Its unit-toll
   work diverges in at least one type. Thus no finite worst total exists for
   all types, and no common positive strict contraction weights exist.

## Fixed policy alternative

For M = I-A, eliminate columns without row swaps while each pivot is positive.
The off-diagonal Schur entries stay nonpositive. If pivot k is nonpositive,
set v_k=1 and v_j=0 for j>k. Solve the earlier triangular equations for v_i.
The signs give v>=0. The first k original equations are zero. The k-th original
equation is the nonpositive pivot, since earlier equations are zero. Every later
original row is nonpositive, since it sees only off-diagonal entries on the
support of v. Thus Mv<=0. This proves the second alternative.

If all pivots are positive, substitution preserves nonnegativity. In particular
u=M^{-1}1 is positive, and Au=u-1>=0 gives u>=1. The weighted maximum norm
contracts by max_i (Au)_i/u_i<1. It follows that M^{-1}=sum_{j>=0} A^j>=0.
The vector u is the unit-toll total. This is the classical M-matrix alternative.

## Finite policy improvement

Start with any policy. Apply the fixed policy alternative. A noncontraction
witness ends the algorithm. Otherwise obtain its total u. For each type, select
a row that maximizes r u. Keep the old choice at a tie. Change only rows with
r u > u_i-1. If no row changes, u=1+T(u), as required.

Suppose the next policy B also contracts, with total z. Then

    z-u = (I-B)^{-1}(1+Bu-u) >= 0.

The last vector is nonzero, since some row changed strictly. The inverse contains
the identity, so at least one coordinate increases strictly. A policy cannot
recur: its total is unique, while all later totals are at least the preceding
total and each improvement is strict somewhere. There are only product_i |R_i|
policies. The uncapped exact algorithm therefore terminates. The implementation
has a declared 4096-policy default budget; exhaustion emits no certificate.
No polynomial runtime or small rational-growth bound is claimed.

## Adaptive choices and exact attainment

Let x_0=0 and x_{d+1}=1+T(x_d). Induction on depth proves that x_d is the maximum
work with d toll levels. Independent row choices are essential: every type may
use its own maximizing row at every node. More history cannot improve this
finite-horizon recursion. The positive vector u bounds every x_d from above.

For x,y, nonnegative rows give

    |T(x)_i-T(y)_i| <= max_{r in R_i} r |x-y|.

Thus T is q-Lipschitz in the u-weighted maximum norm. Iteration converges to u.
The fixed attaining policy has total (I-A)^{-1}1=u, so adaptivity cannot exceed
this one policy. More precisely, 0<=u-x_d<=q^d u. This also gives an explicit
finite-depth tail bound for every allowed schedule.

For an unsafe witness, choose c>0 with 1>=cv. Then A^j1>=cv for every j. The
sum through d toll levels is at least dc v, which diverges on the nonzero
support of v. A positive weight w with Aw<w is impossible: at an index that
maximizes v_i/w_i, monotonicity would give v_i< v_i.

## Why the row contract matters

The whole matrices [[0,2],[0,0]] and [[0,0],[2,0]] each have zero square. Their
independent row menu also permits [[0,2],[2,0]], which has witness (1,1).
Checking only the displayed whole matrices misses this legal bad combination.
Conversely, independent row closure can add choices that a correlated physical
contract forbids. A bad row policy then rejects the relaxation, not that physical
contract. The same distinction applies to upper-bound rows versus exact costs.

The safe menu in example.json has exact total (5,3), even though one allowed
row has sum 6/5. The attaining rows are (1/5,1) and (2/5,0). All rows obey
the common ratio 4/5. The example is a synthetic contract, not a selected
supplier invoice. It shows the additional decision supported by this tool.

## Credit and limits

This is an exact certificate interface and proof of its implementation, not a
new general matrix or policy-iteration theorem. Credit classical Bellman policy
iteration and M-matrix theory. Kozyakin's
[independent-row-uncertainty theory](https://arxiv.org/abs/1507.00492) gives the
related spectral finiteness setting. PR5785 supplies the repository's fixed
matrix interface; PR5892 treats observed forcing; PR6271 treats synchronized
paid switching. Their results are not re-audited here. No physical row coverage,
selected compiler applicability, native realization, new kappa or discharge of
the five selected assumptions follows from this certificate.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
