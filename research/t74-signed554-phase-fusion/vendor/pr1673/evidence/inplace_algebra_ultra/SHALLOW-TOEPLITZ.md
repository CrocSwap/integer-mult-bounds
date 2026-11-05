# Shallow, stable, dimension-preserving Toeplitz circuits

Status: a positive algebraic circuit construction for **dyadic local tiles**. It gives the missing full-Toeplitz primitive in the normalized Sylvester merge. It does not reconcile the anchor coordinates with the original Gaussian gauges; that remains a separate obligation. The construction uses no data ancilla, no zero-initialized coordinate and no fan-out. Fixed coefficient generation is allowed polynomial time in the local tile size and precision.

## 1. Result

Let N be a power of two, and let H be an N by N real or complex Toeplitz matrix with

    max(||H-I||_1, ||H-I||_infinity) <= delta < 1/4.

There is an N-wire linear circuit applying H, with O(log^4 N) rounds of disjoint invertible 2 by 2 gates and diagonal gates, O(N log^4 N) gates, and polynomial-in-N bounds for all coefficients and all partial circuit operator norms and inverse operator norms. Constants depend only on delta.

For any requested output accuracy 2^-p, rounding the coefficients to p+O(log N) bits gives operator error at most 2^-p; arithmetic at that precision also gives uniform forward error 2^-p on bounded inputs, after allowing the same O(log N) guard bits. A rational approximation to the input Toeplitz coefficients and all required gate coefficients can be generated using poly(N,p) bit operations. This coefficient preprocessing may use polynomial extra memory; the **data circuit** still has exactly N live coordinates.

The same result applies to upper or lower triangular Toeplitz matrices with max(||T-I||_1,||T-I||_infinity)<=eta for **any fixed eta<1**, with only O(log^2 N) rounds and constants depending on eta. In particular eta=1/2 is permitted for the generator-normalization step below, even though the full-Toeplitz statement uses delta<1/4. Descendants need bounded norm and inverse, not continued distance below 1/4. This independent triangular construction is important: a contiguous bottom-recursion / shear / top-recursion has linear depth even though its work is quasi-linear.

## 2. Dirty Toeplitz shear is a shallow circuit

For disjoint m-coordinate vectors x and y, implement

    (x,y) -> (x,y+Tx),

where T is Toeplitz, in O(log m) rounds when m is dyadic. It is an invertible square map on the existing 2m wires.

Write the first column and row of T as c_0,...,c_(m-1) and c_0,r_1,...,r_(m-1). Set

    g_0=h_0=c_0/2,
    g_j=(c_j+r_(m-j))/2,
    h_j=(c_j-r_(m-j))/2,              1 <= j < m.

Then T=C(g)+C_-(h), where C is a circulant and C_- is a negacyclic circulant. For a unitary m-point FFT F, C(g)=F^* diag(DFT(g)) F. A circulant shear therefore consists of F on x and y in parallel, the disjoint pairwise shears y_j+=DFT(g)_j x_j, and F^* on x and y. Every FFT stage consists of disjoint unitary 2 by 2 butterflies; bit reversal is a disjoint swap stage.

For gamma=exp(pi i/m), D=diag(1,gamma,...,gamma^(m-1)),

    C_-(h)=D^-1 C(Dh) D.

Use diagonal twists before and after the same circulant-shear circuit. The two completed shears commute. Source x is restored after each. No circulant inverse is needed, so zero Fourier multipliers cause no problem. Every gate is invertible even when T itself is singular.

All intermediate norms are polynomial in m and the l1 norm of the Toeplitz symbol. In the 2-norm, FFT and twist stages are unitary, and the spectral diagonal has norm at most the symbol l1 norm.

## 3. Independent triangular primitive: parity splitting

Let T_N(f) be lower triangular Toeplitz multiplication by f modulo z^N. Write

    f(z)=e(z^2)+z o(z^2).

Reorder the existing coordinates into even and odd powers, N=2m. Then

    T_N(f) = [ E  ZO ; O E ],

where E=T_m(e), O=T_m(o), and Z=T_m(z). All these m by m triangular Toeplitz matrices commute. Set

    k=o/e mod z^m,
    s=e-z o^2/e mod z^m.

The exact factorization is

    [ E ZO ; O E ]
      = [ I 0 ; T_m(k) I ]
        diag(T_m(e),T_m(s))
        [ I T_m(zk) ; 0 I ].

Thus apply the right Toeplitz shear, the two child triangular circuits **in parallel**, and the left Toeplitz shear. The recurrence for rounds is

    D_tri(N) <= D_tri(N/2)+O(log N),

giving D_tri(N)=O(log^2 N). The two recursions act on disjoint coordinates. Inverses are obtained by reversing the gate sequence and inverting every gate, at the same depth.

Stability is not proved by multiplying coefficient l1 bounds afresh at each depth. Each child is a principal submatrix or principal Schur complement of the original triangular matrix, after a coordinate permutation. If the initial T_N(f) differs from I in both 1- and infinity-norm by at most eta<1, every descendant M satisfies

    ||M-I|| <= eta+eta^2/(1-eta)=eta/(1-eta)

in both norms, and ||M^-1||_2 <= 1/(1-eta). This follows directly by expressing the descendant as a Schur complement of a principal block of the original matrix; nested elimination and restriction preserve that description. Hence all local diagonal blocks and local Schur multipliers have constant 2-norms. Their triangular Toeplitz coefficient l1 norms are at most sqrt(N) times these constant bounds. The dirty shear circuits from section 2 therefore remain polynomially bounded.

## 4. Full Toeplitz recursion: displacement rank grows additively

Use the Sylvester shift displacement

    Delta_m(M)=Z_m M-M Z_m.

A Toeplitz H has rank Delta_N(H)<=2. At a node of size 2m, partition

    M=[ A B ; C D ],
    Z_(2m)=[ Z 0 ; E Z ],       E=e_0 e_(m-1)^T,
    K=A^-1 B, L=C A^-1, S=D-C A^-1 B.

The usual block factorization is

    M=[ I 0 ; L I ] diag(A,S) [ I K ; 0 I ].

Again A and S run in parallel. To bound ranks, let U=[-C A^-1,I] and V=[-A^-1 B;I]. Then M V=[0;S], U M=[0,S], and direct block multiplication gives

    Delta_m(S)=U Delta_(2m)(M) V-S E A^-1 B.

Therefore rank Delta(S)<=rank Delta(M)+1. Also, the upper-left block of Delta_(2m)(M) is Delta_m(A)-B E, so rank Delta(A)<=rank Delta(M)+1. At depth d, both children thus have displacement rank at most 2+d.

The top-right block of Delta(M) equals Delta(B), while its bottom-left equals E A+Delta(C)-D E. Consequently

    rank Delta(B)<=r,
    rank Delta(C)<=r+2,
    rank Delta(K)<=rank Delta(A)+rank Delta(B)<=2r+1,
    rank Delta(L)<=rank Delta(C)+rank Delta(A)<=2r+3.

All shear matrices have displacement rank O(log N).

Every recursive M is a principal Schur complement of the original H. Since H=I+R and both ||R||_1 and ||R||_infinity are at most delta,

    max(||M-I||_1,||M-I||_infinity) <= delta/(1-delta),
    ||M^-1||_2 <= 1/(1-delta).

The inverse assertion also follows because M^-1 is a principal submatrix of the inverse of a principal submatrix of H. Thus A,S,K,L are uniformly bounded in 2-norm independently of recursion depth.

## 5. Bounded-generator shear compiler

For an m by m matrix T define its Stein displacement

    E_T=T-Z T Z^T=-Delta_m(T) Z^T+T e_0 e_0^T.

Its rank is at most rank Delta(T)+1. Choose an orthonormal basis g_1,...,g_r for the column space of E_T, and put h_j=E_T^* g_j. With conjugates interpreted appropriately,

    E_T=sum_j g_j h_j^*,
    T=sum_j L(g_j) U(conj(h_j)).

Here L(g) is lower triangular Toeplitz with first column g, and U(h) is upper triangular Toeplitz with first row h. The second identity is the finite telescoping sum T=sum_(k=0)^(m-1) Z^k E_T (Z^T)^k. All g_j have 2-norm 1, and all h_j have 2-norm at most ||E_T||_2=O(1). Their coefficient l1 norms are O(sqrt(m)).

A zero or tiny first coefficient of h is harmless. Choose an integer gamma >= 2||h||_1 (a fixed conservative gamma=64N suffices under the stated bounds), and set

    P=I+U(h)/gamma.

P and P^-1 have constant norm, and P is upper triangular Toeplitz. On the same two existing vectors, one generator term is implemented by

    x <- P x,
    y <- y+gamma L(g) x,
    x <- P^-1 x,
    y <- y-gamma L(g) x.

The result is y<-y+L(g)U(h)x and x is restored. Source transforms use section 3; the other two operations use section 2. Each term costs O(log^2 m) rounds. There are O(log N) terms, hence O(log^3 N) rounds for a full low-displacement-rank shear.

Although the partial generator sum can be larger than its final T, its norm is at most the sum of O(log N) products of O(sqrt N)-norm factors, hence O(N log N). Within a term the source norm remains constant times its entry norm and the target norm is polynomially bounded. Terms are completed as shears with one common source, so their partial sums add; one must not charge a product of polynomial factors for every generator.

The full recurrence is therefore

    D_full(N) <= D_full(N/2)+O(log^3 N)=O(log^4 N).

## 6. Global prefixes, rounding and preprocessing

At each block-LU node the completed right shear, completed middle block, and completed left shear have constant norm and constant inverse norm. At an intermediate time there is at most one unfinished generator compiler or one unfinished triangular compiler along each recursive path; disjoint paths form a direct sum. If B(N) bounds a full circuit prefix and inverse prefix, this gives B(N)<=max(C B(N/2),N^C), hence B(N)=N^O(1). The same argument applies to suffixes and to the triangular compiler.

There are N polylog(N) arithmetic gates. Perturbation of one bounded gate by epsilon contributes at most N^C epsilon to the whole operator, by the prefix/suffix bounds. The sum over all gates remains N^O(1) epsilon. Therefore p+O(log N) coefficient/arithmetic bits suffice; there is no N or N^2 precision term on the data.

The coefficients are fixed before seeing the data. One concrete polynomial-time generation route is:

1. Approximate the original Toeplitz symbol by dyadic rationals at p+O(log N) bits, preserving Toeplitz structure. The operator perturbation is at most N times the entry perturbation.
2. Compute every recursive Schur matrix as a principal Schur complement of this original rational matrix. Its entries are ratios of minors of that original matrix, so numerator and denominator bitlengths are polynomial in N and p. Avoid an unnecessarily expanded recursive rational expression.
3. For each Stein displacement, use exact rational elimination to select independent columns and rational, unnormalized Gram-Schmidt to obtain orthogonal vectors v_j. Then g_j=v_j/sqrt(v_j^*v_j) and h_j=E_T^*v_j/sqrt(v_j^*v_j). The resulting generators have the bounded norms proved above. Nonzero rational residual norms are at least 2^-poly(N,p), so poly(N,p) offline precision suffices for their normalization. Equivalently a high-accuracy SVD may be used.
4. Compute the finite series divisions and FFT roots to p+O(log N) final bits. All final data-gate coefficients are polynomially bounded. Offline intermediate rational numerators may be longer; they never become data wires.

This separates polynomial-time coefficient setup from bounded-precision data application. Applying an algebraic-RAM theorem directly to arbitrarily large integers would not provide this separation.

## 7. Normalized Sylvester merge

For two b-point children, N=2b, the normalized map supplied by the radical-reduction branch is

    S(B,A)=f(z)B(z)+z^b g(z^-1)A(z),
    f(z)=product_lower(1+(x/zeta)z),
    g(z^-1)=product_upper(1+(zeta/x)z^-1).

Let h=g(z^-1)/f(z), K_ij=h_(i-b-j), H_ij=h_(i-j), 0<=i,j<b. The exact identity is

    S=T_f [ I K ; 0 H ].

Thus on exactly 2b data coordinates apply the K dirty Toeplitz shear, the b-wire full Toeplitz H circuit, and the 2b-wire triangular Toeplitz T_f circuit. At sufficiently separated geometric nodes, ||H-I||_1 and ||H-I||_infinity are below 1/4; the f symbol also differs from 1 by a fixed number below 1. This gives O(log^4 b) rounds, bounded intermediate amplification and p+O(log b) data bits in the normalized anchor coordinates. The whole map is square and invertible.

Dyadic child sizes are explicit in this construction. Local tiles may be selected dyadic without padding every tensor axis; arbitrary-length global boundaries still need a layout treatment. Also, converting raw Gaussian coefficient arrays into the common anchor may have exp(O(a b^2)) range. This theorem does not authorize that conversion at bounded precision. The Gaussian gauge/localization branch must establish compatible input/output gauges.

## 8. Relation to the papers and controls

The following primary sources were read end-to-end, including appendices:

- Giorgi, Grenet and Roche, *Fast In-place Algorithms for Polynomial Operations: Division, Evaluation, Interpolation*, arXiv:2002.10304v3. Its RAM model has read-only inputs plus distinct output storage, and its unwritten output is used as temporary memory. This does not establish an N-wire reversible interpolation circuit.
- Dumas and Grenet, *In-place fast polynomial modular remainder*, arXiv:2302.13600v6. Its accumulated convolution/Toeplitz routines and reversible quotient/remainder transform are directly relevant. Its triangular Toeplitz recursion is work-efficient but the two recursive data calls are sequential.
- The same arXiv's expanded v7, *Fast in-place accumulation*. Sections 2, 6 and 7 provide the accumulated linear compiler, Toeplitz-like sum-LU formula, and reversible remainder routines. The final paragraph explicitly leaves floating-point behavior of undoing operations for future study. The present prefix/suffix proof supplies an analysis for this restricted near-identity use.

The parity split and the bounded-generator low-displacement LU combination above are new derivations in this work, not assertions copied from these sources.

`check_circuits.py` compiles actual no-ancilla 1x1/2x2 gate layers, checks pairwise disjointness and invertibility, and replays all input columns. `CIRCUIT-REPLAY.json` records dyadic sizes 2,4,8,16. Current full-Toeplitz endpoint errors are at most 4.5e-15 in double precision. It also replays the normalized Sylvester merge for b=1,2,4,8, with maximum error 1.7e-15; at b=8 the circuit has 16 wires, 608 rounds and 2,464 gates. Omitting the compensating generator subtraction yields error 1.0. `check_exact_algebra.py` verifies 340 parity-factor matrix entries and 26 Schur displacement/rank nodes using exact rational arithmetic. These controls support the algebra but are not substitutes for it.

## 9. Extension to positive-definite Toeplitz matrices

The near-I hypothesis of the full-Toeplitz theorem is sufficient, not necessary. Suppose H is Hermitian positive definite and mu I <= H <= M I, with mu>0. Every principal submatrix has spectrum in [mu,M]. Every principal Schur complement S also does: S^-1 is a principal block of the inverse of a principal submatrix, whose spectrum is in [1/M,1/mu]. Thus every recursive A,S has norm at most M and inverse norm at most 1/mu. The shears K,L have norm at most kappa=M/mu. The displacement-rank formulas are unchanged.

Use orthonormal g generators and h of norm O(kappa), and choose gamma>=2||h||_1. The triangular source transform P is still near I, so the depth O(log^4 N) is unchanged. Generator-stage amplitudes and coefficients are poly(N,kappa). Across the O(log N) completed ancestor factors, the bound becomes

    log(max prefix/inverse-prefix norm)
       = O(log N * log(2+M+1/mu) + log N).

If M and 1/mu are exp(O(u)), this is O((u+1)log N). The corresponding data precision is p+O((u+1)log N), and g-axis tensorization adds O(g(u+1)log N) guard bits. This is a usable broad-Gaussian extension once a separate spectral argument supplies the stated eigenvalue interval. Reversing the circuit applies H^-1; the inverse itself need not be Toeplitz.
