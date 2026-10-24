# Two boundary layers of a finite Gaussian inverse

JoyboyBrian, with substantial OpenAI Codex assistance. Scoped written theorem;
finite controls are corroboration, not formal verification. Apache-2.0.

## Statement and embedding

Fix alpha>0, put b=pi/alpha². Let 0<theta<1, h=sqrt(theta),
rho=1+theta, N=floor(1/theta), n=N-1 and c=1/(2rho). On 0<=k,i<N set
K[k,i]=alpha^-1 exp(-b(i-k/rho-c)²). No band truncation is made.
Let S=diag((-1)^i) and A=S K^-1 S. Write
P(t)=product_(r>=1)(1-exp(-2tr)), and a=alpha exp(b/4)/P(b)^3.
On H=L²(0,infinity) direct-sum L²(0,infinity), let T have kernel

    T(x,y)=exp(-b(y²-x²)) 1{x<=y}.

Partition the finite indices at floor(N/2). U_h maps e_i to the normalized
indicator h^-1/2 1_[hi,h(i+1)) in the first summand on the left half;
on the right half it maps e_i to the analogous indicator indexed by n-i
in the second summand. U_h is an isometry. Its adjoint averages over cells;
the orthogonal complement of its image is mapped to zero. Then

    || U_h (h A) U_h* - a(T direct-sum T) || -> 0.

In particular,

    sqrt(theta) ||K^-1||₂ -> alpha exp(b/4)/(2 sqrt(b) P(b)^3).

This is for each fixed alpha. Uniformity for alpha growing with theta is
NOT asserted. The section is N=floor(1/theta), beta_0=-1/2; changing section
length or starting phase can change the limit. The result determines the
finite matrix boundary layers, not merely a formal differential expression.

## Exact predecessor identity and full coefficient

Credit the finite Gaussian q-LDU identity to the lineage retained by Vlado
Vojdanovski/#1673 and Jose Manuel/#4193, reproduced by JoyboyBrian/#5103 and
Nick Petalas/#5150. Set gamma=b/rho, q=exp(-gamma), Q=q²,
P_j=product_(r=1)^j(1-Q^r). For G[i,j]=q^((i-j)²),

 G^-1[i,j]=(-1)^(i+j) sum_(k=max(i,j))^(N-1)
              q^(2k-i-j) P_k/(P_i P_(k-i) P_j P_(k-j)).

K=Dr G Dc with the exact positive diagonals in #5103. For i<=j, d=j-i,
define the FULL positive coefficient (not just its first summand)

 F_ij = sum_(r=0)^(N-1-j) Q^r P_(j+r)/(P_i P_(d+r) P_j P_r).

Then

 A_ij = alpha exp(E_ij) F_ij,
 E_ij = b beta_j²/rho² - gamma theta(j²-i²),
 beta_j=theta j-1/2.                                      (1)

For i>j the same coefficient after reflection i'=n-i,j'=n-j satisfies

 E_ij = b beta_j²/rho²
        - gamma theta[(j'+delta)²-(i'+delta)²],
 delta=1/theta-n in [1,2).                               (2)

The coefficient is invariant under simultaneous reflection because G and
G^-1 are. These are exact formulas. In particular all entries of A are
nonnegative. The predecessor entry lemma gives F_ij<=P(gamma)^-3.
Both exponents are <=b/4. The upper triangle is attached to the left edge;
the strictly lower triangle is attached to the right edge. We assign the
diagonal only to the upper triangle.

Here is the coefficient limit with an explicit error. For gamma>=b/2 put
r0=exp(-b) and p0=exp(-r0/(1-r0)²). Then all finite products and P(gamma)
are >=p0, because -log(1-z)<=z/(1-z) and geometric summation apply.
Also |P_j-P(gamma)|<=r0^(j+1)/(1-r0). For i>=m, d>=m and N-j>=m+1,

 |F_ij-P(gamma)^-3| <= E_m,
 E_m=5 p0^-5 r0^m/(1-r0)².                              (3)

Indeed replace P_(j+r), P_i, P_(d+r), P_j by P(gamma) in each term.
The numerator and three inverse factors have telescoping error bounded by
4 p0^-5 r0^(m+1)/(1-r0). Sum Q^r<=1/(1-r0), and bound the omitted tail
by p0^-4 r0^(N-j)/(1-r0). The limiting infinite sum is
P(gamma)^-2 sum Q^r/P_r =P(gamma)^-3: the sum telescopes since
Q^r/P_r=1/P_r-1/P_(r-1) for r>=1. This is why the prefactor contains
THREE infinite-product factors. Dropping all but r=0 does not recover it.
Finally logarithmic differentiation of the convergent product gives

 |P(gamma)^-3-P(b)^-3| <= L_b h²,
 L_b=6 b p0^-3 r0/(1-r0)³,                              (4)

using b-gamma<=b h². Termwise differentiation is justified by the same
summable bound 2 sum k r0^k/(1-r0).

## Uniform tails, including the middle and cross-edge entries

Set C=alpha exp(b/4)p0^-3. For i<=j the matrix entry is at most
C exp[-gamma h²(j²-i²)]. For i>j use the reflected bound with delta>=0,
which is no larger than C exp[-gamma h²(j'²-i'²)].
Fix R>=1, h<=1/2, J=floor(R/h), and suppose 2J<=N. Remove the left
upper-triangular J by J corner and the right strictly-lower J by J corner.
For the upper remainder j>=J, j²-i²=(j-i)(j+i)>=(j-i)J. Every row sum
and every column sum of h times this remainder is bounded by

 C h sum_(d>=0) exp(-gamma h² J d)
 <= C(h+1/(gamma h J)) <= C(h+2/(gamma R)).

The inequality 1/(1-exp(-z))<=1+1/z follows from exp(z)>=1+z.
The lower remainder has the identical bound by reflection. Schur's test
therefore bounds their SUM in operator norm by 2C(h+4/(bR)). This bound
includes the middle and cross-edge blocks; no unproved localization is used.
The two retained corners act in different summands of H, so are a direct
sum, not a sum on a shared output. In particular their norms do not add
in quadrature.

For the continuum operator, remove its [0,Jh]² triangle. The same row and
column integral bound gives norm <=1/(b Jh)<=2/(bR). After multiplying
by a<=C and allowing both summands, the continuum tails cost <=4C/(bR).
Together the discrete and continuum tail errors are safely bounded by

    4C(h+4/(bR)).                                       (5)

This also proves boundedness of T, by a compact-window bound plus its tail.

## Compact-window comparison and a quantitative convergence regime

Suppose J>=m>=1 and N-J>=m+1 as well. On each corner the integral kernel
of U_h(h A)U_h* is A_ij on its h by h cells: the h in h A cancels the
normalization h^-1 from the two indicators. On cells with i>=m and
j-i>=m, (3)-(4) control the coefficient. Everywhere both the discrete
kernel and the proposed limiting kernel have magnitude <=C.

For x in [hi,h(i+1)), y in [hj,h(j+1)), 0<=i<=j<J, compare E_ij
(or its reflected form) with b/4-b(y²-x²). Direct expansion, using
|beta_j|<=1/2, gamma=b/(1+h²), delta<2, R>=1 and h<=1/2, gives

 |E_ij-[b/4-b(y²-x²)]| <= D,
 D=12b(R+1)²h.                                        (6)

For example the beta²/rho² discrepancy is at most b[h(R+2)+h²],
the gamma discrepancy at most b h²(R+2)², the reflected delta term
at most4bRh, and rounding x,y to cell endpoints at most4b(R+1)h.
Their sum is bounded by (6). Each exponential argument is <=b/4, so
the mean-value theorem gives an absolute exponential error <=exp(b/4)D.

The exceptional cells i<m or j-i<m have total area <=2mhR in each
corner. The strict diagonal convention and cells straddling x=y are
included in j-i<m. Their kernel difference is bounded by2C. Thus the
Hilbert-Schmidt bound for both exceptional regions is at most
8C sqrt(mh(R+1)), using the triangle inequality generously. The remaining
two squares of side Jh<=R contribute at most

 2R alpha exp(b/4) [E_m+L_b h²+p0^-3 D].                 (7)

Combining (5)-(7) gives the following explicit finite error bound:

 ||U_h(hA)U_h* - a(T direct-sum T)||
 <= 4C(h+4/(bR)) + 8C sqrt(mh(R+1))
       + 2R alpha exp(b/4)[E_m+L_b h²+p0^-3 D].          (8)

All constants and hypotheses have been displayed. One explicit convergence
regime is h<=1/64, R=h^-1/10, m=ceil(h^-1/5), J=floor(R/h), N=floor(h^-2).
Here 2J<=N, J>=m, N-J>=m+1; these follow from R/h=h^-11/10,
m<=2h^-1/5 and h<=1/64. Every term of (8) tends to zero, including
R r0^m. Alternatively first choose R, then m, then h. Constants can be
very large for large alpha; this is not a uniform growing-alpha estimate.

## Exact half-line norm and the endpoint domain

Let L=-d/dx+2bx on its maximal domain of locally absolutely continuous
u with u,Lu in L²(0,infinity). No boundary condition is imposed on u at0.
For compactly supported smooth f, u=Tf is locally absolutely continuous,
satisfies Lu=f and lies in L². The homogeneous solution exp(bx²) is not
in L², so this inverse is unique. Boundedness extends T to all L² and
identifies it with L^-1 by closedness (or the distributional equation).

The adjoint is L*=d/dx+2bx on its maximal L² graph domain with g(0)=0.
Integration by parts first on compact intervals proves the boundary term;
cutoffs and the graph norm give the stated domains. More explicitly the
Dirichlet form identity below controls both g' and xg. Truncation and
mollification with the zero trace show that smooth compactly supported
functions on [0,infinity) vanishing at0 form a graph core. At infinity
the boundary term vanishes by those cutoffs. These facts also follow by
solving the first-order distributional adjoint equation and imposing its
boundary pairing with arbitrary u(0).

For that core, integration by parts gives

 ||L*g||² = integral [|g'|²+4b²x²|g|²-2b|g|²]
           >=4b ||g||².                                (9)

A direct proof of the inequality, requiring no oscillator spectrum, is the
ground-state identity with v=x exp(-bx²):

 integral [|g'|²+(4b²x²-6b)|g|²]
   = integral v² |(g/v)'|² >=0.

Use a cutoff at0 first; g(0)=0 makes the limiting boundary term zero.
The identity extends by the graph core. Duality then gives
||Tf||<=||f||/(2sqrt(b)): for every core g,
<Tf,L*g>=<f,g>, and the range of L* is dense (ker L=0).
Density and (9) bound this functional on that range, giving the asserted
bound without a boundary assumption on Tf itself.
Equality is attained at f(x)=x exp(-bx²), since

 T f(x)=exp(-bx²)/(4b),
 ||exp(-bx²)||² / ||x exp(-bx²)||²=4b.

Therefore ||T||=1/(2sqrt(b)). This is a half-line Dirichlet condition on
the ADJOINT, derived from the original Volterra inverse, not an assumed
Neumann condition on a full-line oscillator. The direct sum has the same
norm as either summand. Norm continuity in (8) completes the theorem.

## Relationship to the formal prediction and limitations

Ryanson Jonathan/#4408 observed theta^-1/2 growth; #4435 proposed
exp(pi alpha²/4)/(2alpha sqrt(pi)) by a two-frequency approximation and
explicitly left the boundary condition and rigorous upper argument open.
JoyboyBrian/#5103 proved a full-cell upper order; Nick Petalas/#5150 proved
a matching edge lower order. Those results and classical q-binomial
identities are credited dependencies, not new deliverables here.
The exact fixed-alpha coefficient above keeps the entire theta product.
No replacement of it by the formal large-alpha expression is made, and no
joint theta/alpha limit is inferred. The new result is the complete
operator-norm boundary-layer limit with its domain and explicit remainder.

The exact-real theorem does not supply coefficient preparation, an inverse
application algorithm, rounded prefixes, integer width, physical movement
or storage, native supplier admission, outer transfer or integer recovery.
No selected frontier or multiplication theorem changes.

## Open next questions

1. Obtain useful uniform constants for the production growing-alpha regime;
   (8) is explicit but too coarse to assert that regime.
2. Classify sections whose endpoint distance or length scales like sqrt(theta),
   where a different limiting interval or boundary layer can occur.
3. Bind an actual rounded complete Gaussian caller, preserving all preparation,
   prefix, movement and storage charges, before substituting any new guard.
