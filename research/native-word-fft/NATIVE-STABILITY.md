# Direct bounded-word lowering of the closed rational Gaussian kernel

This is a native arithmetic construction. It neither calls a Turing machine nor imports a TM simulation or multiplication routine. Its purpose is to turn an existing exact-scalar Gaussian/Walsh provider into a bounded-word algorithm with an explicit accuracy guarantee.

## A literal sufficient class

Consider a fixed finite provider template with:
- arbitrary independent live arrays and explicitly cleared owned scratch;
- fixed rational complex scalar ADD/SCALE operations, COPY, CLEAR, and exact monomial coordinate/quarter-phase operations;
- recursive children that are exact unitary Gaussian kernels, possibly on disjoint fibers and conjugated by monomial operators;
- a complete exact endpoint equal to the desired unitary kernel on every live input, with owned scratch erased.

Read every coefficient from the literal finite template. Replace each rational scalar operation by its signed integer numerator/denominator calculation followed by rounding to a fixed binary grid. Multiplication/division here is on a fixed number of O(log n)-bit words, not on the full input. Nonzero fixed denominators are explicit integers. Metadata, address calculations and phase choices are integer computations.

This class includes the rational Gaussian kernel in PR #956, whose nonchild coefficients are fixed with denominators supported on 2 and 3 and whose monomial phases are fourth roots of unity. It does not automatically include that PR's separate all-length cyclic Fourier compiler, which prepares additional input-length-dependent scalars through Newton/Toeplitz constructions.

## Prefix norms are derived, not assumed

For one scalar gate x<-x+a*y, the Euclidean operator norm is at most 1+|a|. For x<-a*x it is at most max(1,|a|), including the untouched coordinates. COPY has norm at most sqrt(2), CLEAR has norm 1, and coordinate/quarter-phase monomials have norm 1. These statements hold on all arbitrary inputs, not only on a chosen test vector.

Replace |a| by the explicit rational upper bound |Re(a)|+|Im(a)|. Multiply these elementary bounds over the finite template; enlarge the result to an integer K>=2. This is an effective finite calculation from actual coefficient bytes. It bounds every prefix and suffix of that template when recursive children are treated as their exact unitary operators.

A coefficientwise pass acts as a direct sum of the same fixed bank operation, so its norm bound does not grow with array length. Disjoint completed fiber calls form a direct sum of unitary maps. Completed owned-scratch macros have the extended map U_live direct-sum 0_owned after their initial clearing, hence norm at most 1. A primitive prefix inside one such macro is covered by the same fixed template bound.

Classical base butterflies are grouped into completed unitary two-point kernels. Thus an arbitrarily long sequence of completed classical rounds does not multiply their prefix bounds: a partial primitive prefix lies inside only one current butterfly, while all completed rounds are unitary.

Let D(e) be the maximum recursive call depth at rank e. An expanded prefix or suffix is inside at most one unfinished child at each depth. All its other completed children are unitary. Induction therefore gives the actual bound
$$
\|\text{expanded prefix}\|_2,\;\|\text{expanded suffix}\|_2
\le K^{D(e)+1}.
$$
The exponent is depth, not total work. It does not hide an unproved stability oracle.

## Explicit roundoff theorem

Suppose the exact scalar count is at most
$$
M(e)\le A\,2^e(e+1)^\theta
$$
for fixed A>=1 and 0<theta<=1, and the input entries have absolute value at most 2^b. Use enough integral bits to cover the bound below. At each scalar update, compute the exact rational value from the stored approximants and round its two components toward zero at P fractional bits. Its local complex error is at most sqrt(2)*2^-P.

By linearity, the total output error is the sum of these local errors transported through the exact remaining suffixes. Hence
$$
\|\widehat y-y\|_\infty
\le \|\widehat y-y\|_2
\le \sqrt2\,A\,2^e(e+1)^\theta K^{D(e)+1}\,2^{-P}.
$$
For requested error 2^-B it suffices to choose
$$
P=B+e+\lceil\log_2 A\rceil+
  \lceil\theta\log_2(e+1)\rceil+
  (D(e)+1)\lceil\log_2 K\rceil+3.
$$

Exact prefixes have magnitude at most K^(D+1)*sqrt(Z*2^e)*2^b, where fixed Z counts the simultaneously live array banks in the template. The same sum-of-local-errors argument bounds the approximate prefixes by this quantity plus the displayed error envelope. Thus an explicit integral width is
$$
I=b+\lceil e/2\rceil+
 (D(e)+1)\lceil\log_2K\rceil+
 \lceil\log_2(Z+1)\rceil+3.
$$
Increase it by a constant if output accuracy B is allowed to be negative; the intended use has B>=0. Every stored signed fixed-point numerator uses at most I+P+O(1) bits. Fixed rational numerators/denominators add only a template-dependent constant. Choose the physical word-width coefficient large enough for the exact intermediate numerator products, sums and divisions, or use a fixed number of limbs. This yields O(1) word instructions per scalar update.

When e,b,B=O(log n), D(e)=O(log(e+2)), and A,K,Z are fixed before n, I+P=O(log n). Thus the finite-word program has the same asymptotic arithmetic operation count as the exact-scalar provider, with a computable constant and no TM or bit-cost-machine call. The cutoff can be enlarged until fixed template constants fit; below it the program uses direct unitary butterflies.

## Instantiation of the actual closed provider

PR #956 is pinned at fa4df77c9dfdbac93368d95dcb361e69b3b65464. Its optimized source uses m=73, largest child rank 48, productive stock W=58,899, and a complete exact profile. Its own all-input recurrence is
$$
t(e)\le\sum_r(H_r/W)t(rf(e))
+A\,[a+m+2\lceil\log_2(e+2)\rceil+1],
$$
where t(e)=T(e)/2^e, f(e)<=e/73 and the explicit integer-root certificate funds theta=1023/1024.

The actual contraction gives
$$
D(e)\le 1+
\left\lceil \frac{\log(e+1)}{\log(73/48)}\right\rceil.
$$
All source bank/owner constants are fixed before e. The elementary template bill supplies a finite upper bound for the number and coefficient sizes of its nonchild passes, from which K above is computable. In particular this does not replace a varying exact scalar of unknown condition by a word operation.

Therefore this pinned rational native Gaussian/Walsh provider admits a bounded-word approximation program of work
$$
O\bigl(2^e(e+1)^{1023/1024}\bigr)
$$
and arbitrary requested error 2^-B with the explicit precision formula above. For the unnormalized Walsh conversion H_e=(1-i)^e D_e C_e D_e, first request kernel error 2^{-(B+ceil(e/2)+1)} and add ceil(e/2)+1 integral bits for the final scaling. Since |(1-i)^e|=2^{e/2}, the final error is at most 2^-B. These additions remain O(e). Quarter-phase D_e is exact. The power (1-i)^e is an exactly representable Gaussian integer and can be prepared by O(e) bounded-word updates, absorbed by the displayed work bound. No integer-multiplication theorem follows merely from this kernel statement.

The same argument applies to a different *actually constructed* fixed rational provider and its proved recurrence; it does not assert a better profile or select unknown scalar coefficients. In particular, a critical-root compiler word must first have an actual admitted algebraic finite-word construction. Removing tape tariffs alone is not that construction.

## Boundary for cyclic transforms and multiplication

A separate cyclic transform requires explicit algorithms for roots, scalar preparation, conditioning, numerical errors, and convolution/recovery. Nonzero prepared denominators alone do not imply polynomially bounded inverse magnitudes. The exact-scalar PR #956 cyclic section does not supply the quantitative bounds needed here merely by proving nonzeroness.

Root/phase tables and ordinary bounded-word FFT base multiplication can instead be constructed directly, but their complete caller and accuracy costs must be provided. No base multiplication TM is permitted in such an assembly. The nine/54-row TM outer ledger cannot simply have all costs divided by word width: each retained operation must be rebuilt as array/word arithmetic and re-invoiced.

This is a positive finite-word native kernel theorem and a concrete assembly interface. It does not establish a new integer-multiplication exponent or worldwide priority for standard roundoff analysis.


## A quantitative bound for the actual shear preparation

One denominator family in the actual cyclic compiler is already quantitatively safe. Write mu=a+ib with a,b real, and put t1=1+mu*conjugate(mu), t2=mu-t1. Then
$$
t_1=1+a^2+b^2\ge1,\qquad
\operatorname{Re}(t_2)=-[(a-1/2)^2+b^2+3/4]\le-3/4.
$$
Consequently |1/t1|<=1 and |1/t2|<=4/3, uniformly in mu. This is stronger than nonzeroness and is a direct sufficient stability bound for these two divisions. If mu is approximated within delta<=1 and |mu|<=U, then the induced t1 perturbation is at most (2U+1)delta; t2 adds another delta. Provided the t2 perturbation is at most 3/8, its reciprocal perturbation is at most (32/9) times that perturbation, by the identity 1/z-1/z'=(z'-z)/(zz'). Thus this shear preparation is polynomially conditioned whenever U is polynomially bounded. The Newton c-inverses and complete cyclic circuit still require their own quantitative analysis. Credit: ram_cost identified the completion-of-squares argument during this session.

## Polyloglog overhead still retains a strict saving

For completeness, a direct finite-word compiler need not retain a constant number of words to preserve an exponent saving. Suppose an actually constructed native transform on N data words has exact arithmetic work O(N (log N)^{1-kappa}) with fixed kappa>0, and an explicit numerical analysis and implementation bound every scalar update, preparation and packing overhead together by (loglog(N+4))^C for a fixed C. Then the finite-word cost is
$$
O\bigl(N(\log N)^{1-\kappa}(\log\log(N+4))^C\bigr)
=O\bigl(N(\log N)^{1-\kappa'}\bigr)
$$
for every fixed 0<kappa'<kappa. Indeed, setting x=loglog(N+4), the ratio is at most a constant times x^C exp(-(kappa-kappa')x), which is bounded for x>=0. This is a positive absorption theorem; it does not assert that the unresolved Newton/Toeplitz preparation meets its explicit hypothesis. It is useful when a separately derived precision budget is O(log N (loglog N)^c): elementary schoolbook limb multiplication and long division on (loglog N)^c limbs have polynomially many limb operations, and therefore satisfy this overhead condition. No unbounded exact-scalar instruction or TM multiplication routine is invoked.

## Credit and evidence

The closed exact provider, arbitrary-input identity, ownership, recurrence, finite-profile certificate and explicit pass constants are predecessor results from #956 and its #390/Sussman/P193, native, frame/bank, bridge and normalization lineage. Prepared for Dugongue with substantial OpenAI Codex assistance. The roundoff proof above is informal; no new Lean or GPU process was run. Source inspection is not independent acceptance of the predecessor's complete theorem.
