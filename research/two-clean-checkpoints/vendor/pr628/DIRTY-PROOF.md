# Cyclic inverse shears with dirty array restoration

This extends the classical rounded cyclic-inverse primitive of PR628. It removes
its need for a clean length-L intermediate array. It does not supply a common-label
Clifford realization, reversible bit arithmetic, transform layout, or the complete
integer-multiplication reduction. No new kappa follows from this lemma.

## Contract

Input x, target y and h borrowed arrays are complex dyadic grids of spacing u=2^-w.
Every array has length L>=1 and may initially contain arbitrary data. The arrays
are distinct. Their initial infinity norms are at most D. Read-only phases tau_i
have modulus one. Phase generation/storage and coefficient preparation are paid;
there is no free phase table. The primitive adds an approximation to Q(W)^-1 x
to y, restores x and every borrowed array exactly, and needs only a constant number
of clean scalar arithmetic registers besides loop counters and factor descriptors.
Here (Wx)_i=tau_i*x_(i-d), initially for d=+/-1 in a cyclic layout, and
Q(z)=r^-1 product_(j=1)^n(z-rho_j), n=r-1, with stable reciprocal/inner factors
of norm at most 1-beta. The final increment can depend on the initial dirt within
the stated approximation error. Exact independence of the increment from dirt is
not claimed for rounded arithmetic.

## One factor

First consider T x = y defined by y_i=x_i+b_i*y_(i-d), |b_i|<=1-beta.
Choose the cyclic order in direction d. Let z be the zero-boundary causal solution
and p_i the product of b from the first position through i. Let c be the complete
product. Then y_i=z_i+p_i*s, s=z_last/(1-c). The stable cyclic equation itself
implies ||y||<=B/beta when ||x||<=B, so |s|<=B/beta.

On the dyadic grid, perform the causal pass directly in x, skipping the first
position: x_i += round(b_i*x_previous). These are integer lifts. Reversing their
order and subtracting the same rounded source products restores x exactly,
including arbitrary nonzero initial values. During the first pass also accumulate
the rounded scalar product c_hat. Compute s_hat=round(z_hat_last/(1-c_hat)).
In a second pass accumulate rounded prefix products p_hat_i and add
round(m_i*(z_hat_i+round(p_hat_i*s_hat))) to the appropriate target position.
Finally undo the causal lifts. Each target position is written exactly once;
its existing value never enters the computed increment. Scalar arithmetic and
coefficient scratch can be cleared classically; no reversible arithmetic gate
claim is made. Three passes suffice, excluding validation scans and paid
coefficient access. O(1) clean scalar words and O(log L) indexing bits suffice.

Nearest complex rounding has norm error at most u. Assuming u<=beta^2/2,
|z_hat-z|<=u/beta, |p_hat-p|<=u/beta, |c_hat-c|<=u/beta, and
|1-c_hat|>=beta/2. Using s=z_last/(1-c), rather than separately bounding the
numerator and denominator, gives

    |s_hat-s| <= u + (2/beta)*(u/beta + (B/beta)*(u/beta))
              <= 5*(B+1)*u/beta^3.

Also |p_hat|<=1+u/beta<=3/2. Hence the corrected output before m multiplication
has error at most 12*(B+1)*u/beta^3. If |m_i|<=r, the final rounded multiplication
has error at most a*(B+1)*u, a=13*(r+1)/beta^3. None of these constants depends
on L.

For an outer root, b_i=rho^-1*tau_i, m_i=-rho^-1. For an inner root, scan in
direction -d with b_i=rho*conjugate(tau_(i+d)); the value at position i is
multiplied by conjugate(tau_i) and added at i-d. This is
(W-rho I)^-1=(I-rho W^-1)^-1 W^-1. The scalar r is included in one leaf's
multiplier. Each exact factor has operator norm at most K=r/beta. No permutation
of the mutable source array is required for the inner factor.

## Product of factors

For exact linear maps A,B and a dirty scratch array z, the sequence

    z += B*x; y += A*z; z -= B*x; y -= A*z

adds AB*x to y and restores z. Split the factor list in halves recursively;
use one distinct borrowed array per recursion depth. A negative call executes
the exact inverse instruction word (reverse operation order and invert signs).
It is not obtained by negating signs in the original order.

The rounded construction still restores every borrowed array and x exactly.
Inductively each call preserves its input and all deeper scratch, and its increment
is independent of its target. The paired calls computing B therefore see the same
input and deeper initial dirt. Never use an ancestor input or target as deeper
scratch: the ancestor target may have changed between the paired calls. This is
an explicit alias exclusion in the executable contract.

There are h=ceil(log2 n) borrowed arrays and at most N=4*n^2 leaf calls. Pad to the
next power of two for this count if desired (identity leaves require no rounded
inverse). The implementation splits without padding and checks the actual count.

For the ideal elementary shears, the joint max norm grows by at most C=1+K per
leaf. With a*u<=1 the computed trajectory satisfies

    M_j+1 <= G^j*(D+1), G=C+1.

Comparing the complete rounded word with the ideal word on the same initial
arrays, and summing the propagated leaf errors, gives

    E_N <= N*a*(D+1)*u*G^(N-1).

The ideal word cancels all borrowed initial data exactly. This proves the target
error bound for every length and every initial dirt bounded by D, while actual
restoration is exact without an error allowance. Choosing

    w >= p+1+ceil(log2(N*a*(D+1)))+(N-1)*ceil(log2 G)

and enforcing a*u<=1 and u<=beta^2/2 gives execution error <=2^(-p-1).
PR628's coefficient/phase perturbation bound, budgeted to <=2^(-p-1) for the
original x, then gives total <=2^-p. That perturbation bound scales with ||x||;
for general input bound X use p+ceil(log2(max(1,X))) in its preparation budget.
The initial borrowed dirt does not enter the ideal operator perturbation bound.

PR628 has log2(beta^-1)=O(r^3). Therefore these deliberately loose budgets need
w=O(p+log(D+1)+r^5) bits, and O(r^2) passes. Inside a leaf, the causal state and closure scalars add at most another
O(log(beta^-1)+log r) magnitude bits. Maximum transient magnitudes thus add
O(log(D+1)+r^5) integer bits, already covered by this word-size bound. Standard
fast fixed-precision arithmetic yields soft-O((L*r^2+r^3)*(p+log(D+1)+r^5))
bit work plus charged phase-oracle and routing costs. Factor preparation and
coefficient enclosures are inherited from PR628. Borrowed storage is
O(L log r) words; clean arithmetic storage is O(w+log L) bits up to the chosen
multiplication implementation's workspace, plus O(r) read-only factor descriptors.
A machine with only a fixed number of dirty data arrays is not covered by this
contract. Arbitrary stride still incurs PR628's explicitly charged routing.

## Executable evidence

`dirty.py` uses exact rational arithmetic and explicit nearest dyadic rounding.
It checks generic variable-coefficient leaves, dense independently assembled
factor inverses, both orientations, nonzero targets, several initial dirty arrays,
exact source/scratch restoration, exact whole-word inversion, and the leaf count.
Finite checks support the implementation; the inequalities above are the all-L
argument. The exact-rational prototype does not itself implement the claimed
fast fixed-precision arithmetic cost.
