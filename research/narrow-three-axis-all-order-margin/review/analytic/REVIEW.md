# Root review of the all-order source-margin analytic argument

Disposition: the analytic inequalities and stated source specialization are
valid, conditional on the exact finite algebraic certificate. A separate
worker has independently reconstructed that certificate by Kronecker
substitution and division-free Berkowitz determinants, including all lower
coefficient vanishing, so acceptance does not rest on six sampled centers.
This is independent model-assisted mathematical review, not human approval
or proof-kernel verification.

## Continuous determinant argument

The symmetries used are precisely axis permutation and simultaneous full
bit complement. The latter transposes the tensor, and E(A^T)=E(A)^T.
Complete ordering makes the 12-element action free. All six permutations
of the chosen centers pay the variable relabellings. Reversal is not silently
used as a forward determinant symmetry.

For a homogeneous Taylor polynomial of degree K, its gradient one-norm on
[0,1]^3 is at most K times its coefficient one-norm. Thus the independent
maximum 156 and center minimum 7/131072 imply a lower bound
7/131072 - 156*2^-24 = 740*2^-24 > 2^-15 throughout the stated boxes.
The independent weighted coefficient mass 6656 bounds all binomially shifted
coefficients. At h<=2^-30 its higher-degree tail is less than 2^-17*h^K,
leaving at least 2^-16*h^K in the leading w coefficient.

The complete determinant mass is at most 8!*2^8 < 2^24. Every tensor entry
is one monomial, and every displacement entry is a difference of at most
two. Nonnegative w degrees permit the full higher-w tail bound
2^24*w^(d+1) <= 2^-18*w^d*h^4 <= 2^-18*w^d*h^K. The residual determinant
therefore exceeds 2^-18*w^d*h^K. For d<=3, h^K>=h^4>=w; for d=4 the
complete classification has K=0. This proves the common bound D=2^-18*w^4.
Both the continuous variation and every omitted coefficient are paid.

## Physical source parameters

For p>=2^20, L=ln(16p) satisfies L<=p/9216: the difference is positive
at the endpoint and increases. The retained integer alpha gives
4L<=a<=9L, hence a<=p/1024, h=a/p^2<=2^-30 and a>32.
The upper bound a<=9L follows directly by expanding the square of the
ceiling bound; it is valid already at L>=4 using pi<4.
Also w/h^4 <= 2^-32/a^4 <= 2^-42 as required.

The proposed gamma intervals stay strictly inside the original fine-prime
interval. Their minimum center difference exceeds 1/8 after tolerances.
The exact identity s/t=1/(1+gamma/(2p^2)) gives both fine guards,
s>t/2>=p^4, and pairwise prime gaps exceeding t/(32p^2).
The earlier pinned source theorem supplies the actual extremal same-cell
factor, retaining its phase and chirp conventions.

Writing chi=gamma+p^2/s and c=(1-exp(-h*chi))/h is exact, not an asymptotic
replacement. Since 0<chi<1 and 0<=chi-c<=h*chi^2/2, the source's c lies
within 2^-26+2*p^-70+2^-31 < 2^-24 of the selected center.
The physical lower entry V=w*exp(a/s) differs from the common w. It is
not discarded: |V-w|<=4*a*w/t. Relative to the allowance 2^-73*D its
ratio is at most 2^309*a*p^54/t <= 2^299*p^55/t <= 2^-41.
This uses the explicitly stronger t>=p^72 and p>=2^20 hypotheses.

## Inverse and perturbation accounting

For the common-lower tensor all entries lie in [0,1], so ||E(B)||<=8.
Each factor inverse has norm at most four, giving ||B^-1||<=64 and
||E(B^-1)||<=128. Also 0<det B<=1. The identity

    det E(A^-1) = det(A-Z^T A Z)/(det A)^2

follows from det(I-UV)=det(I-VU). Its numerator equals det E(JAJ),
where J reverses the order. The all-order theorem therefore applies to it
without a special reversal symmetry assumption. Dividing determinant by
the seventh norm power proves forward 2^-21*D and inverse 2^-49*D margins.

Factor perturbations of at most zeta produce tensor entry error at most
3*zeta+3*zeta^2+zeta^3<=7*zeta. At zeta<=2^-71*D this is below
2^-68*D. A tensor entry error epsilon gives operator error <=8*epsilon.
The Neumann condition holds with ample margin; the inverse displacement
changes by at most 2^17*epsilon<=2^-51*D. This is smaller than half the
claimed inverse margin; the forward perturbation costs at most 16*epsilon.
The surviving bounds 2^-22*D and 2^-50*D are conservative.

The matched-alias bound 4*exp(-a*t^2/8) is <=2^-73*D because
 a*(t^2/8-8)>=93*ln 2 for a>=1,t>=32.
Physical V adjustment, aliases and further table rounding each use at most
2^-73*D, whose sum is strictly below the complete factor allowance.
Since D>=2^-306*p^-72, ceil(379+72*log2 p) fractional accuracy bits
suffice for that further rounding. At p=2^20 this is 1819, and the
difference from p increases thereafter. The inverse here is the exact
inverse of the chosen rounded factor tensor, not a principal source-inverse
section or a separately rounded inversion algorithm.

## Existence, finite witnesses and limits

The Proth predicate in the source fixtures proves primality: the witness
forces every prime divisor to be 1 modulo 2^m, while odd k<2^m makes
sqrt(k*2^m+1)<2^m. It does not merely provide a probable-prime test.
The finite fixtures establish the local guards, not a complete outer run.

The root independently checked Trudgian's primary theorem 2 at
https://arxiv.org/html/1401.2689v2#S2. The stated error term and range
are transcribed correctly. On [t/2,t] the two endpoint errors are bounded
by 2*t*ell^(-3/4)*exp(-sqrt(ell/12.91)). Each new interval has length
at least t/(2^27*p^2). Their error/main-term ratio is bounded by
2^28*p^2*ell^(1/4)*exp(-sqrt(ell/12.91)), tending to zero at the
retained fixed-epsilon scale ell=Theta(p^(1-epsilon)). The proof claims
only eventual existence; it does not assert primes in every such finite
interval or an effective practical threshold.

The equally spaced-center example cancels the first Taylor coefficient,
not the whole physical determinant. It correctly shows why pairwise gaps
alone do not establish this chosen certificate. Growing dimension,
arbitrary source triples, full coefficient generation, numerical inversion
and complete outer recovery remain outside the theorem. No selected
foundational assumption or complete multiplication exponent changes.
