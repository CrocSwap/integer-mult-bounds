# A native bounded-word inverse for a near-identity band matrix

Let A be an s by s complex matrix with bandwidth h: a_ij=0 for |i-j|>h. Suppose A=I+E and ||E||_infinity<=rho<=1/2. All norms below use complex absolute values. The input entries are explicitly stored bounded-word fixed-point numbers; this is not an assumed inverse oracle. Put H=h+1. Gaussian elimination without pivoting, followed by forward and backward substitution, computes an approximation to A^-1 b in O(s H^2) bounded-word operations, O(s H) space and an explicit absolute error at most

    1000 H^4 u (||b||_infinity+1),

provided local complex rounding errors are at most u<=1/(1000 H^2), and enough integral bits are reserved as below. Constants are deliberately loose. To obtain output error <=2^-P it suffices to choose

    u <= 2^-P / [1000 H^4 (||b||_infinity+1)].

Thus P+log2(||b||+1)+4 log2 H+O(1) fractional bits suffice. If P, log s, log(||b||+1)=O(log n) and h<=n^C for fixed C, all operations use a fixed number of O(log n)-bit words.

## Exact elimination has bounded growth

Initially every row has diagonal-dominance margin

    |a_ii|-sum_(j!=i)|a_ij| >= 1-rho >=1/2,

and absolute row sum at most 1+rho<=3/2. Consider elimination of column k in a remaining row i. Write l=a_ik/a_kk. For the Schur row after deleting column k, the triangle inequality gives

    new margin >= old margin + |a_ik|[1-offsum(row k)/|a_kk|]
               >= old margin.

Similarly its absolute row sum is at most

    old row sum - |a_ik| + |l| offsum(row k)
    <= old row sum.

Consequently all exact pivots are at least 1/2, every surviving row sum is at most 3/2, and every multiplier has magnitude at most 3. These assertions hold for every leading principal subproblem too. The inverse infinity norm is at most 2: if |x_i|=||x||_infinity, then |(Ax)_i|>= (|a_ii|-sumoff)|x_i| >= ||x||/2.

No pivoting is needed. The lower and upper bandwidths remain h: a row only interacts with at most h preceding pivots and at most h following columns. This proves the claimed operation and space counts directly.

## Rounded elimination retains these bounds

Round a multiplier within absolute error u, and each Schur entry update within absolute error u after its exact bounded-word product and subtraction. As long as remaining row sums are at most 2, replacing an exact multiplier by the rounded multiplier perturbs an updated entry by at most 2u, and its final rounding adds at most u. There are at most 2H active entries per updated row and at most H elimination steps affecting that row. The total adverse change in either its row sum or its diagonal-dominance margin is therefore at most 6 H^2 u. The assumption u<=1/(1000 H^2) makes this less than 1/100. By induction the row sums stay below 2, the margins stay above 1/4, pivots have magnitude at least 1/4 and multipliers are bounded by 8. This closes the estimates used in the induction.

Denote the computed factors by Lhat,Uhat. The factor residual is small without exponentially multiplying rounding errors. For one fixed row i, expand its successive updates literally:

    current a_ij = original a_ij - sum_(k already eliminated) lhat_ik uhat_kj
                   + sum(local update roundings).

Each entry has at most H local update roundings. At the removed pivot column, rounding its multiplier contributes at most |uhat_kk|u<=2u. Thus each entry of Lhat Uhat-A has magnitude at most (H+2)u, with at most 2H+1 nonzero entries per row. In particular

    ||Lhat Uhat-A||_infinity <= 6 H^2 u.

Let Ahat=Lhat Uhat. Its row dominance is at least 1/2-6H^2u>1/4, so ||Ahat^-1||_infinity<=4. Also ||Uhat||_infinity<=2 and ||Lhat||_infinity<=1+8h<=9H. Hence

    ||Lhat^-1||_infinity <= ||Uhat|| ||Ahat^-1|| <=8,
    ||Uhat^-1||_infinity <= ||Ahat^-1|| ||Lhat|| <=36H.

The same bounds hold for every computed leading principal pair. They control all forward-substitution prefixes, so no exponential intermediate-growth assumption is being hidden.

## Rounded solves and total error

For each row, accumulate its fixed-point dot product exactly with a bounded-word double-precision accumulator and round only the solved coordinate. Forward substitution then produces yhat with

    Lhat yhat = b+e_f,    ||e_f||<=u.

Thus ||yhat||<=8(||b||+u). Back substitution produces xhat with

    Uhat xhat = yhat+e_b, ||e_b||<=2u,

because rounding a solved coordinate by at most u contributes at most |uhat_ii|u<=2u to that equation. Hence

    Ahat xhat = b+e_f+Lhat e_b,
    ||e_f+Lhat e_b|| <=19H u,
    ||xhat|| <=4(||b||+19H u).

Compare with the true solution x=A^-1 b:

    ||xhat-x|| <=2[6H^2u*4(||b||+19H u)+19H u].

For u<=1/(1000H^2), this is bounded by the stated conservative 1000H^4u(||b||+1). All partial dot products have at most H terms, factors bounded by 8, y bounded as above and x bounded by the same argument on upper triangular suffixes or their solved equations. An additional O(log H+log(||b||+1)+1) integral bits therefore covers every exact sum and product; the exact rational complex division uses a pivot modulus at least 1/4. Fixed extra limbs hold products, accumulators and divisions. Every scalar update consequently costs O(1) bounded-word instructions.

## Gaussian caller and credit

If the actual Gaussian inverse map N has a rigorously truncated bandwidth h=O(sqrt(p)/alpha), truncation norm error eta and ||N-I||<=rho<1/2, apply this theorem to the stored truncated matrix A. Perturbing its right-hand solve changes the ideal inverse by at most ||N^-1||*eta*||A^-1|| times the right-hand norm, so tail and coefficient errors can be invoiced explicitly. Matrix formation, proof of the bandwidth and row-sum tail bound remain the caller's responsibility. This theorem does not assert those facts merely from the name 'Gaussian'.

The elimination and diagonal-dominance arguments are classical numerical linear algebra. This document supplies a direct native sufficient algorithm and explicit word/precision/cost accounting; it does not claim a new best multiplication exponent or worldwide novelty. The Gaussian resampling caller is credited to the upstream construction and its cited Harvey-Hoeven sources.


## The actual periodic Gaussian inverse, with a constructive reduction

Here the band hypothesis can be proved from the actual upstream formula, rather than postulated. Let s<t, alpha>=2, r=t/s>1, q_i=floor(ri+1/2) and beta_i=ri-q_i in [-1/2,1/2]. The source defines N=C T D. Its entries are

    N_ij = sum_(ell congruent j mod s)
             exp[-pi alpha^2 (r(ell-i)+beta_i)^2 + pi alpha^2 beta_j^2].

For d=|ell-i|>=1, each positive summand is at most

    exp[-pi alpha^2(d^2-d)],

because |r(ell-i)+beta_i|>=d-1/2 and |beta_j|<=1/2. Truncate the sum to |ell-i|<=h. The omitted absolute row sum is at most

    2 sum_(d>=h+1) exp[-pi alpha^2 d(d-1)]
    <=4 exp[-pi alpha^2 h(h+1)].

The final inequality follows by bounding the successive-term ratio by exp[-2pi alpha^2(h+1)]<1/2. Choosing

    h = ceil(sqrt((P ln 2+ln 16)/(pi alpha^2)))+1

therefore makes the row-sum tail less than 2^(-P)/4. This is the required h=O(1+sqrt(P)/alpha), with no unknown localization assumption. For s>2h, each retained entry has at most one integer representative in the window, so formation takes O(s h) explicitly generated coefficients. In the actual assembly s is superpolynomial in the precision, hence this condition eventually holds. Smaller s may instead use dense O(s^3) elimination; when s<=2h this is O(s h^2).

Suppose the actual source's proved estimate ||N-I||<=2^(-alpha^2 theta) is at most 1/8, as it eventually is in the intended regime. All entries are nonnegative real numbers and diagonal retained entries include 1. Removing the positive tail can only decrease the row norm of N-I. Form the retained periodic matrix A to coefficient row-sum error at most 1/32, by allocating O(log h) extra fractional bits per entry. Then ||A-I||<=1/4 and ||A^-1||<=4/3. Its difference from N is the explicitly controlled tail and coefficient-formation error; allocate both to the requested P-bit accuracy instead of fixing the error at 1/32 when final accuracy is required.

To handle the wraparound without assuming it is an ordinary band matrix, let A0 be A with only its wraparound corner blocks removed. Those off-diagonal entries are nonnegative. With coefficient errors included conservatively, ||A0-I||<=1/4. The removed corner matrix can be written U V, where V selects the first and last h coordinates, and U has those 2h columns equal to the removed corner columns. Thus rank(UV)<=2h, ||V||<=1 and ||U||<=1/4. All these are literal stored matrices.

Factor the ordinary band matrix A0 using the theorem above. Solve its system for b and for the 2h columns of U. Denote the results by y=A0^-1 b and X=A0^-1 U. The small matrix

    S=I+V X

has ||S-I||<=1/3, because ||A0^-1||<=4/3. It is itself strictly row diagonally dominant, with inverse norm at most 3/2. Factor this explicit 2h by 2h matrix with the same constructive elimination, solve S z=V y, and return x=y-Xz. Direct multiplication verifies A x=b. Thus the algorithm is not hiding a small inverse oracle.

The work is O(s h^2): ordinary band factorization costs O(s h^2), its 2h right-hand solves also cost O(s h^2), and the final dense factorization costs O(h^3)<=O(s h^2). Formation of Xz and every small-matrix operation is included. The storage is O(s h). All exact inverse/operator norms above are fixed constants; numerical approximations to X can use per-entry error budget epsilon/(2h), and all finite sums use O(log s+log h) extra guard bits. The explicit band error theorem then gives any requested final accuracy with P+O(log s+log h+log(||b||+1)) bits. This is O(log n) in the intended regime. Bounded-word coefficient preparation is provided by NATIVE-EXP-TABLE.md, including the charged setup.

Finally, ||N^-1|| is bounded by 8/7 from the original 1/8 estimate. The identity N^-1-A^-1=N^-1(A-N)A^-1 controls truncation and formation errors directly by at most (8/7)(4/3)||A-N||. This completes a positive direct native algorithm for the actual Gaussian inverse, not merely a conditional band-matrix interface. The exact source localization, contraction and resampling identities remain predecessor facts; the native band/Woodbury evaluation and its accounting are the assembly given here.
