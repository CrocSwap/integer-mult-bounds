# Polynomial-size, degree-controlled count formulas in characteristic two

An independent derivation supplies the explicit count-bit bounds. [Bit formulas](char2-count-bit-formula.md)

All logarithms are binary. Let F4 contain omega with omega^2+omega+1=0.
At a spectral tuple, m independent order-three queries have eigenvalues
omega^{k_j}, k_j in {0,1,2}. A fixed shift beta gives the ordinary digits
b_j=k_j+beta_j modulo three and the ordinary integer count c=sum_j b_j.
The affine source indicators I_(j,1), I_(j,2) are exactly the two binary
digits of b_j: each takes values in {0,1} subset F4 at every allowed tuple.
They are affine in the individual query powers q_j and q_j^2.

## 1. An actual formula for a binary sum bit

Consider two binary integers with bit formulas x_i,y_i, i>=0. In
characteristic two use the following ripple-carry formulas:

    c_0=0,
    c_(i+1)=x_i*y_i+(x_i+y_i)*c_i,
    z_i=x_i+y_i+c_i.                                    (B1)

For Boolean values these are exactly the carry and sum bit. The expression
for c_(i+1) contains the entire c_i expression **once**. All other input
occurrences are copied: there is no circuit-sharing convention.

Assign bit i the syntactic-degree budget 2^i. If x_i,y_i have degree at
most 2^i, induction gives deg(c_i)<=2^i and deg(z_i)<=2^i. Indeed the
two products in c_(i+1) have degree at most 2^{i+1}. Degree here is the
ordinary syntactic query degree: multiplication adds, addition takes the
maximum, affine leaves have degree one, and constants degree zero.

Suppose the formulas for x_i and y_i each have at most S_i nodes, with
S_i>=1. Formula-node counts include every leaf and binary operation. From
(B1), |c_(i+1)|<=|c_i|+4S_i+4, and consequently

    |z_k| <= 2S_k+3+sum_(i<k)(4S_i+4)
          <= 8 sum_(i=0)^k S_i.                        (B2)

This last inequality is uniform in k; the previous carry is not recopied
at each multiplication term. An expanded sum-of-products representation
of the carry would lose precisely this useful formula bound.

## 2. Balanced addition gives polynomial formula size

Pad the m digit inputs with zero digits to m0=2^r, where
r=ceil(log2 m). At a leaf use I_(j,1) for bit zero, I_(j,2) for bit one,
and zero for every higher bit. Thus every leaf-bit formula has size one
and bit k has degree at most 2^k. Merge adjacent equal blocks using (B1),
retaining only the first t bits when only a residue modulo 2^t is needed.

Let S_(r,k) bound the size of the **fully unfolded formula** for bit k of
the sum over 2^r leaves. Equation (B2) gives

    S_(0,k)=1,
    S_(r,k)<=8 sum_(i=0)^k S_(r-1,i),
    S_(r,k)<=8^r binom(r+k,k).                           (B3)

The last line follows by induction and the hockey-stick identity
sum_(i=0)^k binom(r-1+i,i)=binom(r+k,k). In particular

    S_(r,k)<=2^{4r+k}.                                  (B4)

This is polynomial in m whenever k=O(log m). It is materially sharper
than replacing every S_(r-1,i) by its maximum and obtaining (8k)^r;
the indices along a formula branch never increase as one descends the
addition tree. The argument counts all copied subexpressions.

For an arbitrary integer u, add the fixed t-bit residue of -u modulo 2^t
to the count using (B1). Its input bits are constants of size one. The
same bound with one extra addition level gives formulas B_k for the bits
of (c-u) modulo 2^t satisfying

    deg(B_k)<=2^k,
    |B_k|<=8^{r+1} binom(r+k+1,k)<=2^{4(r+1)+k}.         (B5)

When D<=m and t=ceil(log2(D+1)), every k<t satisfies k<=r, so
|B_k|<=16m0^5<=512m^5. The construction is a bounded recursive traversal
whose actual time and retained space are polynomial in these explicit
formula lengths.

## 3. Recovering the integral truncated predictor on spectral tuples

For any integer a, including negative a, and h<2^t, the parity of the
generalized binomial coefficient binom(a,h) depends only on a modulo 2^t.
Indeed in F2[[T]],

    (1+T)^{2^t}=1+T^{2^t}=1 modulo T^{2^t};             (B6)

both positive and negative integer powers preserve that congruence because
1+T is a unit. If a0 in {0,...,2^t-1} has bits a_k, then

    (1+T)^{a0}=product_(k<t)(1+T^{2^k})^{a_k}.

Therefore

    binom(a,h) mod2 = product_(k: h_k=1) a_k.            (B7)

This is also the elementary coefficient proof of the relevant binary
Lucas identity. No division by a factorial occurs.

Define an actual arithmetic formula, with copied B_k subexpressions, by

    L_h = product_(k: h_k=1) B_k,     L_0=1,
    P_beta = omega^(u-sum_j beta_j)
                 sum_(h=0)^D (omega-1)^h L_h.           (B8)

At every allowed spectral tuple, L_h=binom(c-u,h) reduced modulo two.
Thus P_beta equals exactly the value of the original integral order-three
count predictor specialized to F4. On the central window u<=c<=u+D it
equals omega^(c-sum beta_j), the required target.

Every L_h has syntactic degree at most sum_(k:h_k=1)2^k=h. Consequently
P_beta has syntactic degree at most D. This degree proof uses no Boolean
quotient simplification or cancellation; the equality with the source
predictor is asserted on the actual order-three spectral tuples, where
the input indicators are Boolean. Nonmultilinear intermediate formulas
are allowed and are essential to the small size.

For D<=m and m>=2, the displayed expression has at most
(D+1) times t copies of formulas bounded in (B5), plus a polynomial
number of arithmetic nodes. For example the deliberately loose uniform
bound

    size(P_beta) <= 2^20 (m+2)^8                         (B9)

holds. All scalar coefficients are in F4; they can be generated by
ordinary integer residues and fixed four-element arithmetic. The formula
shape and its degree budgets do not depend on beta. Coefficient values
and zero leaves are not used to shrink its architecture.

## 4. Full-rate cyclic factorization with a single exponential budget

Apply the characteristic-two cyclic formula lemma in
[formula-full-rate-linearization.md](formula-full-rate-linearization.md). A degree-D formula with S sum
gates becomes D affine pencils, with every cyclic product equal to
P_beta times the entire identity, on at most

    w_m <= D^S <= 2^{m^{C0}}                            (B10)

independent rows for one absolute C0. The larger bound handles the bounded
initial range. Arbitrary independent inputs occupy every row; there is no
designated-output or zero-scratch interpretation.

Take the constant-tail source window

    B=3ceil(sqrt m),   u=m-B,   D=2B.

For all sufficiently large m, D<=m. The fraction of shifts beta in
{0,1,2}^m outside this window at any frequency is at most
2 exp(-9/2)<1/32, by the source count tail estimate. Direct-sum the
3^m equally weighted shifted formulas and duplicate by 32. Their common
full-rate row count R=32*3^m*w_m still obeys 2^{m^{C1}}, and there are
exactly D=O(sqrt m) routed pencil stages. Every final multiplier lies in
F4, and the central-window complement is an effectively known containing
exceptional set of size at most R/32.

For completeness choose one finite coefficient algebra explicitly. Let
M0 be the least common multiple of all positive odd integers at most D,
let tau be the least power of three at least R, and put M=M0*tau. Take

    E=F4[Z]/Phi_M(Z).                                   (B11)

Here M is odd and at most 2^{m^{C2}}. Every odd factor length needed by
the characteristic-two sum construction divides M, and Z^(M/d) satisfies
the corresponding primitive-d cyclotomic relation. The element Z^{M0}
provides tau distinct check nodes. Its power-of-three difference units
have the explicit source product formula with product three, which equals
one in characteristic two. The F4 scalar omega is already in the base;
it need not be identified with a chosen power of Z.

Construct Phi_M by bounded divisor enumeration and exact monic integer
division, then reduce modulo two. All loop counts, degrees and coefficient
bit lengths during that construction are polynomial in M. Formula matrices,
the direct sum, the common ring arithmetic and all repair tables use
2^{m^{C3}} time and space for an absolute C3 by explicit list-and-arithmetic
algorithms. Every E element is a coordinate vector over F4; no alphabet
truth table is enumerated or treated as a unit-cost oracle.

Finite verification of the complete row identity and all exceptions may
enumerate all 3^m spectral tuples and use dense coordinate arithmetic.
That also fits 2^{m^{C4}}. Small m use the known total generic constructor;
the finite cutoff D<=m is directly checked. There is no unknown initial
trial on which this constructor can hang.

**Theorem B5.** The explicit construction (B1)--(B11) establishes B's
hypothesis IP4: full-rate order-three prediction in characteristic two,
O(sqrt m) normalized active pencil volume, F4-valued final multipliers,
known defect at most 1/32, and finite descriptions, actual generation and
workspace bounded by 2^{m^C} for one absolute C.

This theorem concerns the fixed-field representation. Its physical and
whole-input consequences require the separately audited characteristic-two
label geometry, order-three closure, rational Walsh preparation, and the
existing physical/compiler/common-cap proofs.

Credits: the source integral predictor and repair; the elementary binary
addition and binomial identities; the established cyclic matrix-factorization
construction as attributed by B/C; @CubeJerry; AI-assisted formula and
bounded-generator derivation during S002.

## 5. Independent exact replay

Route A replayed both separately written checkers in isolated directories.
B's checker passed 5,460 adder truth cases, 137,214 shifted Lucas cases,
120 serialized actual-formula evaluations, 525 size/degree recurrence
cases, and 45,864 F4 predictor cases, including its negative controls.
C's checker passed 13,996 bit assignments, including 4,786 negative
offsets, 178,330 generalized-binomial residues, 260 copied size/degree
budgets, 18 indicator cases, and 9,702 predictors with 3,259 central
matches, plus three negative controls. The replay directories are
`count-formula-replay-b/` and `count-formula-replay-c/`.

These independent finite tests support the particular identities and
formula accounting. The unbounded size, degree, generator and full-rate
claims are justified by the proofs above; no giant template or complete
tape multiplier was executed.
