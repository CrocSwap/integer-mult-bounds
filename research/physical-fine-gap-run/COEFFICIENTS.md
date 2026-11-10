# Certified pages for the physical fine-gap run inverse

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Numerical/source proof for the joint run implementation. The q-LDU
identity, recurrence factorization and local recentering are inherited from
CrocSwap/integer-mult-bounds#5571, not new claims.

## 1. Exact target and source gate

Use the retained Reference with source size S, excess K_source,
theta=K_source/S, rho=1+theta and a=pi alpha^2, alpha>=1. The ordinary
source interval [s,s+n) satisfies 0<=s<s+n<=S, n>=1, constant
c_i=floor(theta i+1/2), and 2(n-1)<S. Endpoint phases certify constant
phase because c_i is nondecreasing. Cyclicly joined runs crossing the
original period cut are excluded.

Put beta_i=theta i-c_i, q0=exp(-a rho), F_0=1 and
F_r=product_(k=1)^r(1-q0^(2k)). The ideal block is
B_ij=D_i q0^((i-j)^2)/D_j, D_i=exp(a beta_i^2/theta).
D_i is never produced. F indices are relative to the ordinary interval's
first row and do not change when data is reversed.

The inherited factor order is

    F^-1 ; R_- ; C_- ; F ; R_+ ; C_+ ; F^-1.

For sigma=+1 (lower) or -1 (upper), C_sigma solves
y_i=z_i-mu_i*y_(i-sigma), first predecessor zero, with
mu_i=exp[-a(rho-sigma(beta_i+beta_(i-sigma)))].

## 2. Six streams and one common grid

Borrow six streams: F^-1,F,mu_minus,mu_plus,residual_minus,residual_plus,
plus Count descriptors n,L,W,f. All signed records have width W and
fractional grid 2^-f, using the imported two's-complement Signed ABI.
F streams are in ordinary order; each orientation uses traversal order.
Its first mu is zero. The upper pass reverses data before and after its
residual/recurrence pair.

At traversal offset k, b=min(L,n-k) output rows use input window
[max(0,k-L),k+b), length m<=2L, cropping the first min(k,L) outputs.
Anchor u at the actual first output row. All participating |i-u|<=L.
For each block the residual page concatenates m inverse gauges,
m signed kernel values, then b output gauges. The gauges are
exp(-a theta(i-u)^2) and exp(+a theta(i-u)^2). The kernel is

    k_r=(-1)^r exp[-a(3rho-2sigma beta_u)r]/F_r  for r<=L,
    k_r=0                                     for r>L.

One lower convolution precedes the crop and output scaling. Integer
convolution completes before its single toward-zero shift by f. The
recurrence likewise truncates only the completed difference
(z_i<<f)-mu_i*y_previous. No product-first rounding is inserted.

## 3. Explicit range and error allocation

Use component-l1 for complex coordinates; the real program runs twice
on the same pages. Let X>=1 bound the incoming component-l1 radius and
let 0<eps<=1 be the requested error against the ideal block inverse. Choose
a power of two K>=1+1/(3alpha^2 theta). Then ||C_sigma||_infty<=K,
because mu<=exp(-a theta)<=1/(1+3alpha^2 theta). Also
2/3<=F_i<=1, ||F^-1||<=2 and ||R_sigma||<=2. Every prefix or suffix
of the seven completed ideal factors has norm at most 16K^2.

Set Z=128K^2(X+1). Choose a positive L0 with

    3*2^[-6alpha^2(L0+1)] <= eps/(224K^2 Z),

and set L=min(n,L0). If L>=n-1 the finite residual has no omitted terms;
otherwise the displayed quantity bounds its row tail, using #5571's
geometric bound, pi>3 and e>2. In particular n=1 is admitted.
Set h=ceil(8alpha^2 theta L^2) and A=2^h. The local positive gauges
are at most A by pi<4 and e<4. Define

    E0=max(K^2(Z+3), A*((L+5)*Z+8), Z+2).

The producer certifies inward-magnitude coefficients with error at most
eta=2*2^-f. Choose f with

    eta <= eps/(224K^2 E0),   eta<=1/4.

A rounded diagonal on an actual incoming vector of radius at most Z
has error at most (Z+2)eta. A recurrence with inward mu has computed
radius at most K(Z+1); its local equation residual gives total error
at most K^2(Z+3)eta. The argument applies to its actual rounded inputs.

For a residual block, telescope the three coefficient factors. Their
entrywise absolute errors have row sum at most [2+A(L+3)]eta: the exact
signed kernel has absolute row sum at most 2, each input inverse gauge
is at most 1, and each output gauge is at most A. Input-scale, completed
convolution and output-scale rounding add at most (6A+2)eta. Thus

    residual error <= A*((L+5)*Z+8)*eta + tail*Z.

Each completed stage consequently has error at most
xi=eps/(112K^2). Telescope against the ideal linear factors, not against
a presumed linear rounded map. The seven errors amplify by at most
7*16K^2, giving final error at most eps. Computed completed-stage radii
are at most 16K^2 X+7*16K^2<=Z, closing the induction.

The common record carrier must additionally cover local partial values:
U=8AK(Z+1) bounds their decoded magnitudes. It is enough to use
W>=max(f+ceil(log2(U+1))+2,ceil(log2(n+1))+2) with the imported
sign-record convention. This also pays encoded run/block loop counters;
the fixed number of online control fields has total width O(W).
Packed convolution products and raw scalar products use the imported
larger temporary widths; they are not claimed to fit W before rescaling.

## 4. Certified inward coefficient generation

All geometry is exact rational arithmetic. The source interval producer
encloses exp(-pi x) for nonnegative rational x. Use internal grid

    Q=f+2h+2ceil(log2(n+1))+16

and source working grid 2Q+32. Rescaling its returned enclosure to Q
adds at most two units; its width is at most three Q-grid units.
Compute q0^2 powers and F_i by outward Q-grid multiplication. A direct
width induction gives at most 10i units for the i-th power: the q0^2
interval has width at most eight units and each product adds at most two
units. Each F update then adds at most 10i+2 units. Summing for
1<=i<=n-1 gives 5n(n-1)+2(n-1)<=6n^2 units for every F_i.
Reciprocals of F_i, whose lower endpoints are
above 1/2, have width at most 26n^2 units. A residual numerator divided
by F_r has width at most 34n^2 units.

For a local inverse gauge the exact value is at least 1/A. The extra
2h bits ensure its lower endpoint is positive and at least 1/(2A).
Its reciprocal interval has width at most 14A^2 Q-grid units. Hence
every final coefficient interval has width below one f-grid unit.
The implementation checks these widths and positivity explicitly.

Store floor(lower_endpoint*2^f), then restore the kernel's sign. The
absolute coefficient error is at most two f-grid units, not one; the
interval uncertainty is included. All magnitudes round inward, preserving
mu contraction. Zero has the canonical nonnegative sign. No assumption
that an irrational exponential's exact floor can be cheaply decided is
needed. Neither beta_i^2/theta nor a full-run gauge is evaluated.

The f allocation is greater than h+1, so an inverse gauge whose certified
lower endpoint is at least 1/(2A) remains strictly positive on the data
grid. Both serialized local-gauge families are checked positive. F and
F^-1 are positive by their fixed lower bounds. Recurrence and residual
coefficients may legitimately quantize to zero.

## 5. Comparison to the fixed rational reference

This is a direct local comparison. The nearest source lift of any pair
in an admitted ordinary interval is zero because 2(n-1)<S. Retained
same-phase entries obey RAW-GAUSSIAN-PROOF.md's shared-ratio entry bound;
unretained offsets are covered by its Gaussian row tail. Both diagonals
are one. Thus its E_N bounds ||H_run-B||_infty directly. A principal
periodic-N comparison alone would not justify this step without aliases.

Let d_ref be exactly `Reference.narrow_gap`, as defined in the pinned
source, and d_B=d_ref+E_N. This identity does not permit substituting an
arbitrary stronger gap certificate for d_ref. The same
source nearest-neighbor bound certifies the ideal block gap d_B. The
resolvent allowance for input radius X is

    E_ref = X*E_N/(d_ref*d_B).

For requested final accuracy 2^-t the producer allocates eps=2^(-t-1)
to physical ideal-block execution and requires E_ref<=2^(-t-1). It
rejects an underfunded fixed Reference. Increasing its entry precision
changes the reference and must be an explicit new source object.

The comparison and resolvent identity are inherited mechanisms. The new
claim concerns their source-bound certified pages and actual physical
consumer. Complete cyclic Schur recovery, selected/hole transport,
normalization and the outer Gaussian/integer caller remain outside this
run-only result. No new kappa is asserted.

## 6. Preparation and online cost boundary

Interval/scalar preparation is an explicit polynomial-time integer
algorithm, with ordinary multiplication/division, and is charged once
per source axis. It is not a measured finite-control tape trace. Page
serialization writes O(n) signed records, O(nW) bits, on a fixed number
of tapes. There is no analytic validation per online right-hand side.

Let B dominate Q, the rational geometry input heights, alpha^2, the fixed
Reference entry precision, and 16. The interval source uses O(B) Machin
terms with temporary rational heights O(B^2), then O(B) dyadic Taylor
terms and at most O(B) range-reduction/squaring steps. Ordinary schoolbook
products/divisions and conservative Euclidean reduction give O(B^8) bit
work per requested decay, including source setup. There are O(n) decays
and interval/geometry operations, so O(n B^8) is a conservative complete
preparation bound. Working and retained page space is O(nB+B^2), including
the rational-series temporaries, cached final pi intervals, all six page
streams and serialization. One fixed Reference descriptor can be prepared
once per axis at the same polynomial tariff; no Reference entry or global
weight is needed by this producer. Over the ordinary source-run family,
sum n=S, giving O(S B^8) setup and O(SB+B^2) retained/setup space.

These are upper bounds for explicit integer algorithms, not a claim that
the receipt's arithmetic-call counters are binary step measurements.
Decimal receipt/hash construction also fits this polynomial setup bill.
In the fine-gap production
regime theta=Theta(p^-2), a=Theta(log p), target/input logarithms O(p),
we have L=O(p/log p), A=O(1), f,W,Q=O(p), and polynomial(S,p) setup.
For arbitrary finite parameters, retain the explicit h, Q and W instead
of asserting these optimized bounds.

For an original run family of S records the favorable physical tariff is
O(S M(W)+(S/L+number_of_runs)M(LW)+SW), with short windows capped by n.
Here M is the imported exact bit multiplication cost, including its own
numerical recovery and unamortized preparation. The inherited
M(v)=O(v log^2(v+2)) gives O(S p log^2 p) in the production regime.
The joint physical proof must price actual page traversal and reuse too.
