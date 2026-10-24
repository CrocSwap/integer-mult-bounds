# Exact two-call cost at tied tensor width two

## Source contract and statement

Use the widened monomial game in Jacob Alan Sussman's PR4628 (head
`ee4fd87f064017c23e5a86fc1dcfe0a5237caed3`, PROOF §§1–4). Put d=2^m,
V=C^d, a=(1+i)/2, b=(1-i)/2, C_v=aI+bX_v. At the fixed width f=2,
a paid call is C_v⊗C_v on one register. Free letters are B⊗B for monomial
B on V; arbitrary finite complex scalar register mixing, copies and resets
are free. There is one arbitrary input and finitely many zero helpers, all
returned to zero. No independent-column letter is allowed.

**Theorem.** For every m≥2, the exact paid-call cost of
(C^⊗m)⊗(C^⊗m) is two. For m=1 it is one.

This is a fixed-width result in the widened game, not the narrower affine
engine, an all-width two-call program, an addition tariff, a dirty-helper
return theorem or a physical supplier. PR5178 (Nick Petalas,
`5fcfa050f2fc5445d7f0997206c5044b17f7e88f`) leaves the tied-column case open;
its attaining individual-column permutations are not used here.

## 1. The exact free algebra

Write D for the span of d_i=e_i⊗e_i, S for the span of
s_ij=e_i⊗e_j+e_j⊗e_i (i<j), and A for the span of
a_ij=e_i⊗e_j−e_j⊗e_i. Then V⊗V=D⊕S⊕A. Every tied monomial preserves
these three spaces. Let F be the linear span of tied monomials. It is an
algebra, since their products are tied monomials. In fact

    F = End(D) ⊕ End(S) ⊕ End(A).                 (1)

Here is a finite legal synthesis, not an appeal to an arbitrary dense free
map. For each address k, let Z_k be diagonal with entry i at k and 1
elsewhere. On e_p⊗e_q, Z_k⊗Z_k has eigenvalue i^(δ_kp+δ_kq).
For a weight w in {2e_p, e_p+e_q:p<q}, the operator

    P_w = product_k [ (1/4) sum_(t=0)^3 i^(-t w_k)(Z_k^t⊗Z_k^t) ]

projects onto the corresponding one-dimensional diagonal coordinate or
ordered-pair two-space. This follows from the four-term character sum;
all its letters are tied monomials. On the pair {p,q}, let τ exchange p,q.
The operators P_(e_p+e_q)(I±τ⊗τ)/2 separately project onto s_pq and a_pq.
Tied permutations take any diagonal coordinate to any other, or any pair
coordinate to any other, with only a possible sign on A. Thus projector,
permutation and scalar give every matrix unit on each of D,S,A separately.
Their finite sums prove (1). All coefficients can be Gaussian rationals.

A finite linear combination of free words can be executed with zero helpers:
copy the input to one branch per summand, execute that word and scalar on its
branch, sum into a separate accumulator, and reset branches. Products of such
expressions are also finite free programs. This realizes (1) without treating
a matrix unit as an additional primitive. The number of additions/helpers
may grow rapidly with d and is not priced in this declared game.

## 2. Gauge and cross-sector ranks

Let H=[[1,1],[1,-1]] and D0=diag(1,-i). Then C=a D0 H D0.
Tied diagonal maps and scalar multiplication therefore convert a paid call
along the first bit into Q=W⊗W, where W is the unnormalized one-bit Walsh
map, with independent pairs (2p,2p+1). They also convert the dense target
into T=H_m⊗H_m, where (H_m)_(i,x)=(-1)^(i·x). These are invertible free
pre/post gauges, so call cost is unchanged.

Both Q and T commute with the tensor swap. Consequently their only
cross-sector blocks among D,S,A are D→S and S→D. Put r=d/2 and let E_p
be the S coordinate for {2p,2p+1}. Direct expansion gives

    Q_SD d_(2p)=E_p,       Q_SD d_(2p+1)=−E_p,
    Q_DS E_p=2(d_(2p)−d_(2p+1)),

with Q_SD zero on no other D coordinates and Q_DS zero on all other S
coordinates. Thus both cross-sector ranks equal r.

For each nonzero binary address w, let u_w in S have coefficient1 on
pairs {i,j} with i XOR j=w and 0 elsewhere. Let v_w be the row on D
with v_w(x)=(-1)^(w·x). Then

    T_SD = sum_(w≠0) u_w v_w,
    T_DS = 2 sum_(w≠0) v_w^T u_w^T.               (2)

The u_w have nonempty disjoint supports, and the Walsh rows v_w are linearly
independent (H_m H_m^T=dI). Hence both ranks are d−1.

## 3. Lower bound with any finite clean scratch

A zero-call program has input-output operator in F. Before a unique paid
call, every register contains an F-operator applied to the original input.
After that call every register is a sum of an F-operator on the input and
an F-operator applied to the called register. Thus any one-call endpoint is

    F0 + L Q R,       F0,L,R in F.                (3)

This remains valid with arbitrary singular mixing, copies and resets, any
finite number of helpers, and a call on any helper. It follows by induction
on the chronological straight-line steps, not by replacing one call with an
arbitrary sum of unrelated double-coset terms.

By (1), the SD block of (3) is L_S Q_SD R_D and has rank at most d/2.
The target rank is d−1, strictly larger for d≥4. At least two calls are
therefore necessary. For d=2 the target is the single call, and its nonzero
SD block excludes zero calls.

## 4. A literal two-call factorization for every m≥2

Partition the d−1 nonzero addresses into W1,W2, each of size at most r.
For each t, assign its addresses w to distinct indices p=0,...,|Wt|−1.
Define block-diagonal free-algebra maps L_t,R_t by the following entries,
setting all unspecified entries and their A blocks to zero:

    (L_t)_S E_p = u_w,
    row_(2p) ((R_t)_D) = v_w,
    column_(2p) ((L_t)_D) = v_w^T,
    row_(E_p) ((R_t)_S) = u_w^T.

In particular the odd D rows of R_t and odd D columns of L_t vanish.
Using the two explicit blocks of Q gives

    (L_t Q R_t)_SD = sum_(w in Wt) u_w v_w,
    (L_t Q R_t)_DS = 2 sum_(w in Wt) v_w^T u_w^T.

All other cross-sector blocks vanish. Therefore

    F0 := T−L1 Q R1−L2 Q R2

is block diagonal and belongs to F by (1). This proves the exact identity
T=F0+L1QR1+L2QR2, with two actual occurrences of Q, rather than mere
membership in span(FQF).

Keep a saved original input. Prepare R1x and R2x in separate zero banks
using the finite free synthesis of §1, apply one paid call (with its free
gauges) to each, and apply L1,L2. Form F0x freely, add the three outputs,
copy the result into the input register, and reset every helper, including
the saved input. Since only zero helpers were promised, these resets are
legal. The endpoint is exact on every input and consumes exactly two calls.
Undo the target gauge to obtain the stated C target. No ability to reset
arbitrary dirty data is inferred.

## Evidence and limits

The universal theorem rests on the finite character-projector synthesis,
one-call normal form and explicit all-d block factorization above. Small
exact replay checks the complete operator in the original ordered tensor
basis, the free-sector synthesis and hypothesis-removal controls. It is not
an exhaustive program search. This does not contradict the source all-width
m-call lower bound: width is fixed at two, and the free program is allowed
to depend on m. There is no claim about optimal binary-addition counts,
efficient phase/projector generation, physical tape/precision tariffs,
selected κ, or the complete multiplication theorem.

## Open next questions

Determine the fixed-width call cost with only the narrower affine/phase
engine alphabet, where (1) must be re-established rather than assumed.
Separately price the many free linear combinations before considering a
physical application. No such efficiency is obtained here.

Credit Jacob Alan Sussman's PR4628, Nick Petalas's PR5178, eumemic, Swapnil
Jain and the retained register-model lineage. Prepared by JoyboyBrian with
substantial OpenAI Codex assistance. Apache-2.0; no human or kernel approval.

Every nonzero source address v partitions the addresses into a perfect matching {x,x+v}. An allowed tied address permutation conjugates this matching to the first-bit matching, so every allowed paid C_v has the same cross-sector rank and the same one-call normal form used above.
