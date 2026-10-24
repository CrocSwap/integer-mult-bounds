# Weighted powers of the actual periodic Gaussian reference

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Reference/geometry attribution: Jose Manuel, Vlado Vojdanovski, Jeremy Kothe,
Cinna Davis; interval arithmetic Mason Hale. The complete rounded service
and its original error/workspace proof are inherited, pinned inputs.

## Quantified source contract

Take exactly the unmodified `Reference` constructor: integers S>K>0,
alpha>=1, entry_bits b>=8, source halfwidth w>=0 with 2w<S, and an
admitted target halfwidth. Put theta=K/S, rho=1+theta, a=alpha²,
phase_i=nearest_up(theta*i), beta_i=theta*i-phase_i in [-1/2,1/2).
The selected rows i+phase_i are distinct; all other rows are holes.
H is its ACTUAL rational narrow matrix, not an ideal Gaussian substituted
for its shared-weight branch. Put A=H-I. All its off-diagonal entries are
nonnegative. For the numerical adoption below also require the original
`prepare(reference,target,Y)` to succeed with its positive funded gap d;
this is an additional assumption, not a consequence of this theorem.
No arbitrary caller-constructed Plan is certified.

For each retained nonzero source offset h=j+lift*S-i, define ideal weights
D_i=exp[-pi*a*(1/4-beta_i²)/theta] and k_h=exp[-pi*a*rho*h²].
On a hole set D=1 and the corresponding kernel row/column to zero.
Let C on selected rows have entries k_h for 0<|h|<=w and zero elsewhere.
Because 2w<S these are unique cyclic offsets, not duplicated period images.
Define epsilon=2^(-b-6), lambda=1/(1-epsilon). Then the main result is

    0 <= A <= lambda D C D^-1                         (entrywise). (1)

Every downward coefficient quantization Ahat also satisfies (1).

## Every source branch, including period crossings

For every retained pair, beta_i+theta*h differs from beta_j by the integer
phase_j-phase_i+lift*K. The nearest representative beta_j minimizes absolute
value in this residue class, including the exact half-integer tie. Hence
Delta=(beta_i+theta*h)^2-beta_j²>=0. Direct expansion gives

 ((rho*h+beta_i)^2-beta_j²)
   - [rho*h²-(beta_i²-beta_j²)/theta] = (rho/theta)*Delta >=0. (2)

Consequently the ideal entry is <=(D_i/D_j)k_h for positive and negative h,
for both lift signs and for different phases. No monotonicity across the
phase jump is assumed. Same-phase lift-zero entries have Delta=0 exactly.
The source cross-cell and cross-period branches use inward absolute
quantization of a nonnegative exponential interval, so their rational
entries are <= their ideal values. Omitted entries are zero; diagonal
entries and hole identities become zero in A, closing the complete matrix
partition. The exponent is nonnegative in the admitted source branch as
already checked by its exponential domain; alternatively the ideal narrow
construction supplies that domain. We do not alter any source branches.

For a shared ratio let f=a*(1/4-beta_i²)/theta and B=a/(4theta).
The source relative receipt uses L=ceil(8B). Since pi/log(2)<5<8,
exp(-pi*f)>=2^-L. Its explicit absolute error times 2^L is <=epsilon.
Its value is the downward floor of the lower interval endpoint, so

    (1-epsilon)D_i <= weight(i) <= D_i.

The retained kernel is also inward: kernel_value(h)<=k_h. Thus its actual
ratio is <=lambda(D_i/D_j)k_h. This proves (1), including the only branch
where replacing the rational reference by an ideal exponential would be
invalid. The source's validated interval enclosure and relative-error
receipt are inherited; no numerical sampling proves these inequalities.

## Uniform contraction, retained gauge, and tail

All coefficients are positive. Entrywise multiplication therefore gives
A^j <= lambda^j D C^j D^-1, and similarly for Ahat, for j>=1.
For j=0 use the identity norm bound separately. The circular kernel has
row sum <=2 sum_{h>=1}exp(-pi*a*h²). Use pi>3, e³>20 and
h²>=1+3(h-1). A rational upper bound is

    r=2 lambda/[20^a (1-20^(-3a))] <1.                   (3)

The last inequality follows already at a=1,b=8, where lambda<=16384/16383;
the denominator increases with a. For example r<1/9 follows by elementary
rational cross multiplication at these endpoint values. e³>20 follows by
summing its positive Taylor terms through degree8. The bound is independent
of theta; it is deliberately conservative, not the optimal spectral radius.
The gauge is retained:

    cond_infinity(D) <= exp(pi*a/(4theta)) <= 2^G,
    G=ceil(5a/(4theta)).                                (4)

Here pi<22/7 and log2>2/3 imply pi/log2<5. In particular this is NOT a
uniformly bounded inverse condition number or a free gauge transformation.
No weights are numerically applied by the implementation.

For ||u||_infinity,l1<=Y and J terms in sum_{j=0}^{J-1}(-A)^j u,
(1)--(4) and absolute convergence give the tail certificate

    T_J=Y 2^G r^J/(1-r).                               (5)

The same applies to Ahat. Large intermediate rational integers used to
certify (5) are setup state; we report outward rounded bounds, not huge
unfunded printed decimals. No production p-family or growing-alpha
corollary is asserted.

## Complete numerical adoption, not only a tail estimate

Retain original prepare's exact coefficients, quantization grid h=2^-P,
funded row gap d, radius R=(Y+2h)/d and m=2w. Its computation is
z_0=u, z_{k+1}=u-trunc_P(Ahat z_k), with one final component truncation
per row, and every complex component pair measured in l1. The inherited
proof gives ||z_k||<=R and local error <=m h R+2h against u-A z_k.
Since ||A||<=1-d, the propagated numerical error is <=

    N=(m h R+2h)/d.

Replace ONLY the tail with (5). Thus returned z_{J-1} has error <=T_J+N
against H^-1u. The checker selects J with T_J<=2^-target/4, leaves P and
R unchanged, and checks the complete bound <=2^-target/2. This proof extends
the arithmetic engine's prepared-plan precondition to the specific
`adopt(reference,original)` result; it does not certify arbitrary replacements.
Caller must supply original from the same unmodified prepare invocation.
`adopt` is a trusted preparation function under that explicit precondition,
not an authentication API for untrusted Python objects.

If separately inherited analytic error ||H-H0||<=E<d is admitted, add
Y E/[d(d-E)], as in the predecessor. The actual checker funds that sum below
2^-20 and independently computes the original-rational H residual divided
by d. The analytic source theorem remains inherited, not reproved here.

For Reference(384,1,2,4,18,320), Y=1,target=20: G=1920,
r is the exact rational (3), d=4151/65536, P=33. The exact loop chooses
J=120 instead of276, hence119 instead of275 updates. The same complete
385-row output includes hole192 and every wrap. The original source is
regenerated, not inferred from a frozen finite packet. A dropped-wrap
trajectory fails the target: its residual divided by 2-d is a lower bound
on its true error, since ||H||<=2-d. A separate exact geometry discriminator shows
an actual entry exceeds the ungauged small-kernel majorant; the gauge cannot
be deleted. Finite branch controls supplement (2), not replace its proof.

## Complete cost, storage, setup and ownership

Let N=S+K and M=2wS. Original preparation is unchanged and NOT free: N+M
source entry requests, interval/pi caches, rational weights and entries,
and integer coefficient table coexist. The finite receipt records exactly
the predecessor setup inventory including max declared6830 interval bits,
384 eight-field weight receipts and retained pi cache. The original scalar
row-gap iteration-selection loop still runs in prepare (276 iterations in
this fixture); we do not hide it just because adoption replaces its result.
Weighted selection additionally performs J rational multiplications and
comparisons on explicit certificate integers, plus powers20^a and2^G.
This setup may have large integer bit cost. Its exact rational intermediates
have O(J*(b+a)+G+target+logY+logS+logK) bits under ordinary rational arithmetic; no
constant-time real exponential is called by the new certificate.

Actual service work is exactly2M(J-1) integer products and accumulator
additions,2N(J-1) component roundings, subtractions and update writes.
With M3072,N385,J120 this replaces275 complete updates by119, a reduction
of156 complete updates; table generation, delivery into host memory and
all setup remain charged. All input validation scans,4N scratch initialization,
2N output copying and4N scratch clearing remain unchanged and recorded.
The maximum signed accumulator width bound remains
2P+ceil(log2(max(1,R)))+2. Storage:2N input components,4N scratch components,
2N output components coexisting before finally cleanup, M persistent
(index,coefficient) records, fixed loop/accumulator scalars, and preparation
certificate integers plus source caches. No sequence of old iterates is retained.
The original immutable borrowed input and table are unchanged; returned
immutable output is caller-owned; both scratch arrays are zero-filled and
cleared even on exception. This is logical slot cleanup, not allocator
zeroization. The new plan shares the immutable table; keeping the old plan
adds a few scalar fields, not another coefficient copy.

Consequently steady-state host arithmetic has the predecessor bound
O(J M M_int(2P+logR)+J N(P+logR)), plus all stated setup/scans/clears.
This is a genuine complete finite consumer saving, not merely a Gaussian
constant improvement. It is NOT a physical tape tariff: no repeated physical
trajectory, new coefficient-delivery protocol, Core seam speed, multiplication
bound or selected-frontier improvement is claimed. PR5190's separately
published physical single-update invoice is not imported or relied on.

## Open next questions

Can an admitted production family absorb the exponential gauge in its
iteration budget and pay the original setup and physical delivery costs?
That question requires a complete family/caller ledger, not extrapolation
from this finite saving. Can a sharper weighted bound improve the *complete*
consumer cost enough to justify its more expensive certification?
