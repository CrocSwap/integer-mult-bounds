# Target-known Walsh16 lattice-certificate derivation

Qualified conditional derivation. A finite certificate satisfying the explicit obligations below gives an all-integer codec and two-sided inverse, with the stated additional zero/sum/error consequences. This does not establish that the source's actual table satisfies those obligations, construct a new table, independently repeat a finite matching/search, or discover its theorem or sharp constant.

## Role and reading boundary

The coordinator supplied this target and hypotheses after the round claim. I have not read current6574 PROOF, construction, kernel, verify or a current peer/coordinator draft before sealing this note. My current-batch role is target-known/current6574-source-unread; history across older long batches is uncertain and is not declared blind or never-exposed. I did not author the earlier FOUR-AXIS scout. The coordinator disclosed informal preclaim reasoning. No source/new scientific program, import, constructor, enumeration, census, numerical test, proof assistant or kernel was executed. This is written algebra and metadata only.

I choose the PLUS convention F(x)=(H x+c_q)/4. Actual source sign, phase, table ordering and inverse lookup must be checked after sealing; a minus-offset source can be translated by c=-a but must not be silently identified with this convention.

## 1. Exactly all residue keys, algebraically

Index rows and columns of H by F2^4 and write H_(s,t)=(-1)^(s dot t). Orthogonality gives H^2=16I. For any signed integer vector x, define A=sum_t x_t mod4 and B=sum_t (x_t mod2)t in F2^4. Then

    (Hx)_s = A-2(s dot B) mod4.                       (1)

Indeed H_(s,t)=1-2*1_(s dot t=1), and the parity of the sum over those t is s dot B. This uses exact integer congruences and holds equally for negative or arbitrarily large x.

Let q(A,B)_s=A-2(s dot B) mod4 with A in Z/4Z and B in F2^4. These64 vectors are distinct: q_0=A, and q_(e_j)-A determines B_j because it is0 or2 mod4. They are all attained. If B is nonzero, set x_B=1,x_0=A-1 and all other components zero; if B=0 set x_0=A. Formula(1) then gives the chosen key. Thus

    K = {Hx mod4:x in Z^16} = {q(A,B)}

has exactly64 elements, established without enumerating x or a source table. Fibers are the cosets of the homomorphism x -> Hx mod4. A complete certificate must cover exactly this set, not merely the observed keys of finite input fixtures. This is an algebraic description of the supplied target quotient, not a new count of source matches or rows.

## 2. Sufficient finite certificate and forward branch

For every q in K, suppose a certificate supplies an integer vector c_q of length16, satisfying:

1. c_q+q=0 componentwise mod4;
2. Hc_q is componentwise divisible by4;
3. t(q)=(Hc_q/4) mod4 lies in K, and q -> t(q) is a permutation of K;
4. a back-offset table is indexed by these TARGET keys and stores

       d_(t(q)) = -Hc_q/4.                            (2)

All exact comparisons use integer vectors and not rounded floating arithmetic. Items2 and membership of t are convenient explicit checks; with q a genuine key and item1 they also follow algebraically: choose x_q with Hx_q=q mod4, write c_q=-Hx_q+4k, and obtain Hc_q/4=-4x_q+Hk, whose residue belongs to K. They are not independent hypotheses that one can vary while retaining all their stronger antecedents. The permutation and exact back-offset association remain substantive conditions.

For an arbitrary integer x, take its unique key q=Hx mod4 and define

    F(x)=(Hx+c_q)/4.

Item1 makes F(x) integral. Moreover

    H F(x) = 4x+Hc_q/4,

so its output key is precisely t(q). Each branch consequently maps into the declared target-key coset. A permutation of labels alone is insufficient unless the actual integer offsets satisfy the congruence and back-offset identities too.

## 3. BOTH inverse compositions on every integer vector

For an arbitrary integer y of key t=Hy mod4, define

    G(y)=(Hy+d_t)/4.

By the permutation, there is a unique q with t=t(q). Equation(2) gives d_t=-Hc_q/4, hence t+d_t=0 mod4 and G(y) is integral. Also

    H d_t = -4c_q,
    H G(y) = 4y-c_q = q mod4.                         (3)

Thus G(y) returns to the CORRECT source-key coset q, not merely to some integral vector. This source-key calculation is essential to the right inverse.

For every integer x of key q, the key of F(x) is t(q), and

    G(F(x)) = (4x+Hc_q/4+d_(t(q)))/4 = x.

For every integer y of key t, equation(3) ensures that F selects c_q after G, and

    F(G(y)) = (4y+Hd_t/4+c_q)/4 = y.

Both compositions are proved on all integer vectors, not only on matched representatives, a fixture box, a finite residue grid or the image of a previously tested forward call. This establishes a bijection Z^16 -> Z^16 from a valid complete certificate. It is not a bijection of every finite machine-register subset.

## 4. Zero and real error require their own conditions

Let T=H/4, so T is an orthogonal real matrix. The forward error is exactly c_q/4. Therefore an additional rowwise bound ||c_q||_2^2<=64 gives

    ||F(x)-Tx||_2^2 <=4.                              (4)

This norm condition alone does not give zero preservation. Require c_0=0 separately; then F(0)=0, t(0)=0 and d_0=0, hence G(0)=0. Conversely F(0)=0 in this convention forces c_0=0. Inverse error uses its associated d_t if needed; this note does not infer the same rowwise inverse-offset norm merely from the forward norm without checking the relevant norm preservation. In fact H/4 is orthogonal, so ||d_t||=||c_q|| and the analogous bound follows when(2) holds.

## 5. Complex quarter-rotation and weighted sum

Put d_j=(-i)^popcount(j), D=diag(d_j), and U=-D T D. D and -D are Gaussian-unit diagonal maps, so they preserve Z[i]^16, zero and Euclidean norm. Define componentwise realification R(w)=F(Re w)+i F(Im w), and

    C(z) = -D R(Dz).

Its ideal linear map is U, exactly, in this chosen phase convention. Since R is a bijection of Gaussian-integer vectors, so is C. Do not assume F is odd when simplifying its inverse. The correct inverse expression is

    C^-1(z) = D^-1 [G(Re(-D^-1 z))+iG(Im(-D^-1 z))].   (5)

Composition follows by the inverse diagonal phases and the two real inverse identities above. The source's literal phase convention still needs post-seal binding.

Weighted complex sum is an ADDITIONAL algebraic obligation, not a consequence of(4). Let d be the vector of diagonal entries of D and let1 denote the all-ones row. Tensor factorization gives

    (d^T H)_t = product_j(1-i*(-1)^t_j)
              = -4 i^popcount(t),
    d^T T = -conjugate(d)^T,
    1^T U = 1^T.

The factor -4 is (1-i)^4; it must not be replaced by+4. The correction to the complex sum of C is

    -(d^T c_q+i d^T c_r)/4,

where q and r are the independent real/imaginary keys of Dz. Thus a sufficient rowwise condition for exact complex sum preservation is

    d^T c_q=0 for every q.                            (6)

For these real integer offsets it means both real weighted sums and imaginary weighted sums vanish: the weight is1 at popcount0 or4, -1 at popcount2, -i at popcount1 and+i at popcount3. Ordinary unweighted sum zero is not interchangeable with(6). Under the complete independent real/imaginary key domain, the vanishing correction for every pair also forces(6): put q=r to obtain (1+i)d^T c_q=0. With C bijective and sum-preserving, its inverse also preserves sum by applying that identity to C^-1(y). No sum claim follows solely from offsets being small or from U being sum-preserving.

## 6. Complex error and the credited sharp witness

For each complex input the correction has real/imaginary parts c_q/4 and c_r/4 before the final unit phases. Hence(4) in each component yields

    ||C(z)-Uz||_2^2 = (||c_q||^2+||c_r||^2)/16 <=8.   (7)

For z=(2+2i)e_0, Dz=z and Tz has all16 coordinates equal to(1+i)/2. Final multiplication by -D rotates each coordinate by a Gaussian unit, so each ideal output coordinate still has real and imaginary parts in Z+1/2. Every Gaussian-integer output is at squared distance at least1/4+1/4=1/2 per coordinate, for a total at least8. Therefore any integer-output approximation to this U has error at least8 on that witness, and a valid certificate satisfying(7) attains that lower bound. This is the supplied source's sharpness mechanism/constant, not a new independently located witness, table or theorem.

Zero and weighted sum constraints must still be imposed separately. The lower-bound witness by itself proves neither an all-input upper bound nor invertibility or sum preservation.

## 7. Discriminating written controls — UNEXECUTED

1. An incomplete key table leaves some integer inputs undefined: the explicit representatives in Section1 show every K-key is reachable, not merely a theoretical unused row.
2. Target-key collisions destroy the inverse association. Without error/zero restrictions, choose each c_q=-Hx_q for a representative x_q. All congruences hold and all x_q map to0; t(q)=0 is constant. This is a witness for the need for the permutation, not a counterexample to a certificate retaining all its obligations.
3. Index d by the source key instead of the target key when t is nontrivial. The needed composition cancellation is d_(t(q))=-Hc_q/4; a same-row label does not establish it.
4. Reverse only the sign of(2). The residual Hc_q/4+d_(t(q)) no longer cancels, and integrality can fail too. A numerical norm match is not the exact vector identity.
5. Permit an offset not congruent to -q; at q=0, c=e_0 has tiny norm but produces a fractional output on x=0. Norm bounds do not imply lattice closure.
6. Infer zero or weighted sum from norm alone. The individual row c=4e_0 has squared norm16 and satisfies zero-key congruence but would move0. The row c=4(e_0-e_3) has norm squared32 and ordinary sum zero, yet d^T c=8 because popcount(3)=2. These are rowwise nonimplication controls, not asserted complete alternative matching certificates.
7. Drop the norm bound and retain only congruence: an individual zero-key row c=12e_0 has squared error9 on zero, exceeding the real bound4. Again this challenges the weakened implication, not the valid table.
8. Use a wrong outer phase, commute a nonlinear F through a minus sign, or replace complex weighted sum by ordinary offset sum. Neither lattice bijectivity nor real error alone binds the desired U or sum equation. Equation(5) avoids an unproved oddness simplification.
9. Treat the all-integer bijection as a fixed finite-register permutation. If c_0=0, take x_t=M H_(s,t) for a positive integer M. Its key is0 and F(x)=4M e_s, so an input bounded coordinatewise by M can exit that same box. A reported4096-bit API cap/4090-bit headroom must be separately checked against actual code; it is not a theorem that the entire bounded register domain is mapped into itself.

Hc divisibility and target-key membership are not offered as independently droppable controls while congruence and genuine-key coverage are retained, because Section2 proves those consequences. No control above was executed, and no source fixture or source mutant outcome is claimed.

## Post-seal binding and scope

The necessary next written check is that the actual source's complete key set, integer offset shape, chosen plus/minus sign, target-key permutation, back-offset association, c0, row norms, weighted constraints and literal complex phases match these hypotheses, and that any finite API cap/headroom is described separately from the all-integer formula. Its actual64-row matching existence,3072 table data,4096-pair checks and fixtures remain source-owned and UNREPLAYED. Source target/certificate representation may use a different signed key order or stored minus offsets; this note does not guess that convention.

No covariance, phase equivariance, fourth-power identity, inward-norm monotonicity, arbitrary family restriction, actual caller binding, sampling/native/physical invoice, optimization, all-five-assumption discharge or kappa/frontier change is proved. Source6574 owns its construction, theorem, sharp constant and original finite evidence. Walsh/Hadamard orthogonality, congruence/coset algebra, exact inverse composition and half-grid nearest-lattice reasoning are standard methods. This is a substantial OpenAI Codex target-known external written derivation, not human/kernel certification or a source scientific replay.
