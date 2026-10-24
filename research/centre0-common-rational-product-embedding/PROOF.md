# Common Gaussian-rational product-chart obstruction

Prepared by JoyboyBrian with substantial OpenAI Codex (Astra) assistance.
This is a written algebraic proof with finite exact source checks, not a
proof-kernel result or a replay of a changed native producer.

## Statement and scope

Let F=Q(i), let N=2^m>=128, and identify the N owner coordinates with the
coefficient vector space of E=F[y]/(y^N+1). Let G be the actual 112 by112
centre0 code in PR5101, reconstructed below, and put A=G direct-sum I_(N-112)
and B=G^T direct-sum I_(N-112). For every invertible F-linear S and every
invertible F-linear C, the identity

    (S A S^-1 x)(S B S^-1 z) = C(xz)                 (1)

fails for some x,z in E. Products in (1) are negacyclic products in E.
The same statement holds with the product normalized by 1/N, since F-linearity
of C cancels that common nonzero factor. Here S is a common owner-to-polynomial
basis choice for both operands. No restriction is placed on the output map C
beyond invertibility and F-linearity.

This excludes one precise enlarged record-chart class. It does not exclude
arbitrary complex charts, independent input charts, address mixing, changed
codes, or a different bilinear algorithm. It supplies no physical operation,
price, Gaussian implementation, native lift, or new kappa. In particular the
actual normalizers diag(K_i)^-1 G diag(K_i) have not been commuted through a
central operator. PR5101's source-derived record code is the premise; its
unemitted changed native producer remains unemitted.

## 1. Source-bound low-rank transpose defect

The live inputs are pinned at the package base in SOURCES.json. R is the actual
8 by112 matrix from native-involutive-dual/R.json; J is selected_ports from
its INVOLUTIVE-WORD.json.gz. Let K=R^T/4 and let P equal K on the rows in J and
zero elsewhere. Put U=K-12P and D=diag(0,1,1,1,1,1,1,1).
The centre0 edit of PR5101 gives

    G=I-U D R.

This is reconstructed entry by entry and compared with every entry of the
published CORRECTED-DERIVATION.json F_actual, rather than assuming its G or P.
The verifier checks RR^T=56I, RP=I, hence RU=14I-12I=2I,
and checks the original eight-mode F=I-UR against the source word.
It checks J={0,7,20,23,86,93,108,111} and all 112 owner coordinates.
Consequently (UDR)^2=UD(RU)DR=2UDR, so G^2=I. Thus A,B are invertible.
Since D has rank7,

    rank(G-G^T) <= rank(UDR)+rank(R^T D U^T) <=14.

The exact source values G[0,1]=11/2 and G[1,0]=-1/2 show G-G^T is nonzero.
All rational matrix ranks remain unchanged after extending scalars to F;
nonzero minors characterize rank. Identity padding and common similarity
preserve the rank of B-A. Therefore

    1 <= rank(S B S^-1-S A S^-1) <=14.             (2)

The independent checker additionally certifies rank14 using reduction modulo
101 for the lower bound; the displayed factorization supplies the rational
upper bound. Exact rank14 is not needed for the contradiction.

## 2. Product identity forces a multiplication operator

Let H be any finite-dimensional commutative unital F-algebra and suppose
invertible F-linear maps a,b,c satisfy a(x)b(z)=c(xz) for all x,z.
Writing alpha=a(1), beta=b(1) gives

    c=m_alpha b=m_beta a,

where m_v denotes multiplication by v. Since c and b are invertible,
m_alpha=c b^-1 is invertible. Its surjectivity gives a v with alpha v=1,
so alpha is a unit. Similarly beta is a unit. Commutativity now gives

    b=m_(beta/alpha) a,
    b-a=m_(beta/alpha-1) a.

Thus rank(b-a) is the rank of a multiplication operator on H. This uses the
invertibility of c explicitly; it does not assume alpha is nonzero and hence
a unit in an arbitrary algebra. This elementary unit/isotopy argument is the
one credited in PR5101 to de Groote and the Bürgisser--Ikenmeyer treatment;
we include the full short proof to specify its hypotheses.

## 3. Multiplication ranks over Q(i)

Write d=N/2. Over F,

    y^N+1=(y^d-i)(y^d+i).

Both factors are irreducible of degree d. Indeed every root of either factor
is a primitive (2N)-th root of unity: its N-th power is -1 and 2N is a power
of two. For such a root zeta, Q(i) is contained in Q(zeta), since zeta^d is
+i or -i. The polynomial y^N+1 is irreducible over Q: after substituting y+1,
all nonleading coefficients are even, and the constant coefficient is 2,
not divisible by4. To see the even coefficients, in characteristic2 repeated
squaring gives (y+1)^(2^m)=y^(2^m)+1. Eisenstein at2 applies. Hence
[Q(zeta):Q]=N and [Q(zeta):Q(i)]=N/2=d. Each displayed degree-d factor is
therefore the minimal polynomial over F of any of its roots.

The two factors are coprime (their difference is 2i), so the Chinese remainder
map identifies E with K_plus times K_minus, two fields of F-dimension d.
Multiplication by (u,v) is zero on a factor precisely when its corresponding
coordinate vanishes; otherwise it is invertible on that factor. Its F-rank
is therefore exactly one of 0,d,2d. These are all possible, including the
zero-divisor case; treating E as a field would be incorrect.

## 4. Contradiction and limits

Apply section2 with a=SAS^-1, b=SBS^-1 and c=C. Section3 forces rank(b-a)
to lie in {0,N/2,N}. But (2) puts it between1 and14, while N/2>=64.
This proves (1) impossible for every allowed N and S, with no finite search
over charts and no bound on entries of S or C.

Over C the algebra splits into N scalar factors, so the minimum nonzero
multiplication rank is1; this proof gives no complex-chart obstruction.
With independent charts one can conjugate both involutions to the same
involution, and our common-similarity rank invariant is no longer available.
Neither observation claims that a priced physical rescue exists.

## Evidence and open next questions

verify.py rebuilds the actual code and checks frozen exact receipt fields.
independent.py reads the predecessor matrix directly, obtains a modular rank
certificate, and exercises the algebra's zero-divisor boundary using exact
Gaussian integer arithmetic at N=8. Those finite controls do not prove the
all-N cyclotomic or isotopy lemmas; the arguments above do.

A useful next task would specify either independent native input charts or
address-mixing operations and supply their complete implementation and price.
It must first overcome the actual source product interface, not assume that
commuting phases or rational density imply multiplicativity. The complex
coefficient version is also open here: its field decomposition invalidates
the present rank threshold, and no impossibility is asserted.

Credit: Cao Yifan/intqwq and the PR4610 native lineage; Cinna Davis centre-free
and helper-basis work; Dugongue/mdumitrean PR4929/4948; Chris R/Clear1nsight
PR5101 source derivation; Dillon PR4933 and the retained native, analytic,
precision and compiler predecessors. This package adds the all-common-Q(i)
chart and all-power-of-two-padding obstruction, not the predecessor code.
Apache-2.0. No independent human or proof-kernel acceptance is claimed.
