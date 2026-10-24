# Paid constant-time native Gaussian weights

Fix positive constants c, C and 0<eta<1. Let n grow, p<=c log2(n+2), and let 0<=x<=C log2(n+2) be a fixed-point argument. A uniform bounded-word RAM can prepare an approximate exp(-x) oracle with absolute error <=2^-p, using O(n^eta log n) bounded-word preparation operations and words, and O(1) bounded-word operations per query. The word-width coefficient and query constant depend only on c,C,eta. This is a fully constructed table, not an assumed transcendental instruction.

Put h=2^(-floor(eta log2(n+2))) and J=ceil(C log2(n+2)/h). Let S=p+ceil(log2(J+1))+c0, where c0 is a sufficiently large constant below. Choose a fixed odd integer d with eta(d+1)>c+eta+2. Above a fixed finite cutoff, the alternating Taylor polynomial

    q0 = sum_(k=0)^d (-h)^k/k!

satisfies 0<=q0<=exp(-h) and exp(-h)-q0<=2^-S. The degree is fixed independently of n. Fixed rational polynomial evaluation uses a fixed number of bounded-word operations; compute it with enough guard bits that its total error is below 2^-S, subtract that certified error margin, then round downward to obtain 0<=qhat<=exp(-h) with exp(-h)-qhat<=C_d 2^-S for an explicit template constant C_d. Increase c0 to absorb C_d and every fixed polynomial-evaluation error constant. The initial finite cutoff can use a direct table constructed with higher precision; it depends only on fixed program constants.

Set Ehat_0=1 and Ehat_(j+1)=floor_S(Ehat_j qhat), where floor_S is rounding downward to the nonnegative binary S-bit grid. Since 0<=qhat<=exp(-h)<=1, every Ehat_j lies in [0,exp(-jh)]. Induction gives

    0<=exp(-jh)-Ehat_j<=j(C_d+1)2^-S.

There are J+1=O(n^eta log n) entries, and each recurrence update is bounded-word multiplication, shift and store. Choosing c0 so that (C_d+1)J2^-S<=2^(-p-4) controls the whole prepared table.

For a query, use binary shifts to compute j=floor(x/h) and u=x-jh in [0,h). Evaluate the same fixed Taylor polynomial at u to error at most 2^(-p-4), multiply by Ehat_j, and round the result with the same guard precision. Then exp(-x)=exp(-jh)exp(-u), all exact factors have magnitude at most 1, and the sum of table, residual and product-rounding errors is less than 2^-p. If x itself approximates a nonnegative intended argument within epsilon, exp(-x) changes by at most epsilon (or exp(epsilon) epsilon if the approximation crosses zero); budget this explicitly when constructing the query.

All rational coefficients 1/k! have fixed-size denominators. Every stored scalar and exact intermediate has O(log n) bits. J and every address also have O(log n) bits. Setup includes all table entries, and query evaluation includes the residual calculation. There is no multiplication or division on a full n-bit operand, no Turing machine and no root/exponential oracle.

## Actual Gaussian caller

The finite-precision resampling formulas in upstream build/sections/07-resampling.tex use coefficients exp(-a z^2) on windows for which a z^2=O(p), after factoring their explicitly stated normalizations. Compute a z^2 by bounded-word arithmetic and invoke the prepared table. Arguments beyond a chosen Cp cutoff can return zero, with exp(-Cp) below the assigned tail budget; the cutoff C must be chosen from that caller's requested error. A fixed approximation to pi at S+O(log p) bits, obtainable by a separately charged ordinary series, suffices for a=pi/alpha^2 or pi alpha^2 after its actual polynomial argument-size bound is included. Polynomially large positive factors can be treated by reversal against a prepared exp(-x) scale, with an additional O(log n) magnitude and precision allowance; this sentence does not replace the actual caller's bound.

Thus the explicit window-product loops of the S map and E=N-I map can prepare each negative Gaussian weight in O(1) native instructions after the paid O(n^eta log n) table. This justifies a direct arithmetic-loop recount rather than dividing a tape-time estimate by p. It does not itself accelerate the number of window visits, prove a blocked chirp convolution, or establish a new complete multiplication exponent.

The exponential table construction is a standard range-reduction/table idea specialized here to the actual O(log n)-argument and O(log n)-precision regime. No worldwide novelty claim is made. The Gaussian resampling identities and stability estimates remain credited to the upstream source and its Harvey-Hoeven references.

## Signed-argument corollary for block chirps

For 0<=x<=C log2(n+2), exp(x)=1/exp(-x). Request the negative exponential with absolute error epsilon<=2^(-p-3) exp(-2C log2(n+2)); use an explicit power-of-two upper bound for this budget. Since exp(-x)>=exp(-C log2(n+2)), its approximation remains at least half that lower bound. The reciprocal identity bounds the resulting reciprocal error by 2 exp(2C log2(n+2)) epsilon, before the final bounded-word division rounding. Reserve a further 2^(-p-2) budget for that rounding. The added fractional bits and positive-result integral bits are both O(log n). Thus the same paid construction supports exp(x) for the full signed interval |x|<=C log2(n+2), with O(1) bounded-word instructions per query. This supplies the possibly positive quadratic weights in a centered Gaussian block/Hankel factorization. The constant-factor word width is fixed before n.
