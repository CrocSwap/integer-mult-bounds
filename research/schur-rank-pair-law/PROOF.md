# Joint nullities of a matrix and its identity shift

This proof was produced by Nick Petalas. Apache-2.0.

The subspace inclusion-exclusion method and Gaussian coefficients are classical.
The contribution here is an explicit joint law, with all lifting factors retained,
and its substitution into ssafwann's binary sharp Schur-header count from #4678.
No priority claim about finite-field enumeration outside this repository is made.

## Statement

Let q be a prime power and d a nonnegative integer. Let C_d(a,b;q) count matrices
H in M_d(F_q) with nullity H=a and nullity(I-H)=b. Write

\[
{n\brack k}_q=\prod_{r=0}^{k-1}\frac{q^n-q^r}{q^k-q^r},\qquad
\mu(k)=(-1)^kq^{k(k-1)/2}.
\]

The Gaussian coefficient is zero for k outside 0..n. For 0<=a,b<=d with a+b>d,
C_d(a,b;q)=0. Otherwise, put t=d-a-b. Then

\[
\boxed{\begin{aligned}
C_d(a,b;q)
={d\brack a}_q{d-a\brack b}_q q^{ab}
\sum_{i=0}^{t}\sum_{j=0}^{t-i}
&\mu(i)\mu(j){t\brack i}_q{t-i\brack j}_q\\[-2pt]
&\cdot q^{ij+bi+aj+d(t-i-j)}.
\end{aligned}} \tag{1}
\]

This is an exact integer formula. For each nullity pair it has
(t+1)(t+2)/2 summands, so the entire distribution has O(d^4) explicit summands.
This counts arithmetic summands, not bit operations or measured runtime.
Gaussian coefficients and powers can be precomputed. The small standalone
implementation instead evaluates their bounded products directly.

## Proof

The zero and one eigenspaces of H are disjoint. Indeed, Hv=0 and Hv=v imply
v=0. This proves the a+b>d exclusion.

There are

\[
B_d(a,b)={d\brack a}_q{d-a\brack b}_q q^{ab} \tag{2}
\]

ordered pairs of disjoint subspaces A,B of dimensions a,b. Choose A, choose
the b-dimensional projection of B in V/A, and choose a lift of that projected
subspace. Relative to a fixed complement, the lift is the graph of an arbitrary
map into A, with q^(ab) choices. This proves (2).

Fix one such pair, write W=A+B, and let t=dim(V/W). We count H for which
ker H=A and ker(I-H)=B. Prescribing H to be zero on A and the identity on B
leaves d*t free matrix entries, hence q^(dt) extensions before excluding
larger eigenspaces.

For a vector space L of dimension m, the elementary subspace identity is

\[
\sum_{U\le L}\mu(\dim U)
=\sum_{k=0}^m {m\brack k}_q(-1)^kq^{k(k-1)/2}
=\begin{cases}1&m=0,\\0&m>0.\end{cases} \tag{3}
\]

For completeness, the finite q-binomial expansion of
`product_(r=0)^(m-1)(1-q^r z)` has coefficient
`(-1)^k q^(k(k-1)/2) [m choose k]_q` at z^k. Induction on m, multiplying by
the last linear factor and using the Gaussian recurrence, proves this
expansion. Setting z=1 gives (3).

For any H extending the prescription on A+B, apply (3) to ker H/A and
ker(I-H)/B. The product of the two subspace sums is one exactly when both
kernels equal their prescribed subspaces, and is zero otherwise. Summing over
H and exchanging these finite sums gives a signed sum over super-subspaces
A'>=A and B'>=B, of respective dimension increments i,j. A pair with nonzero
intersection has no compatible H, since its intersection would have to be
both fixed and killed.

It remains to count the disjoint super-subspace pairs. Their projections into
V/W are disjoint subspaces I,J of dimensions i,j. To see disjointness, suppose
x in A' and y in B' have the same nonzero image in V/W. Write x-y=a+b with
a in A,b in B. Then x-a=y+b is a nonzero vector in A' intersect B', which is
impossible. The same argument shows A' intersect W=A and B' intersect W=B.

Choose I and J disjoint in V/W. Equation (2) in dimension t gives

\[
{t\brack i}_q{t-i\brack j}_q q^{ij}
\]

choices. For fixed I,J and a fixed section V/W -> V, the possibilities for
A'/A are graphs of maps I -> W/A, giving q^(bi) lifts. Similarly B'/B has
q^(aj) lifts. Each pair of lifts is disjoint because I,J are disjoint, and
every allowed A',B' occurs once. Thus the required number is

\[
{t\brack i}_q{t-i\brack j}_q q^{ij+bi+aj}. \tag{4}
\]

For each such pair, H is prescribed on A'+B', of dimension a+b+i+j, and
is arbitrary on a complement. There are q^(d(t-i-j)) extensions. Multiplying
by the inclusion-exclusion weights mu(i)mu(j), summing over i+j<=t, and then
multiplying by (2) proves (1).

## Substitution into the binary Schur-header law

This part uses the one-block counting theorem of **ssafwann, #4678**, head
`af9cf805c501e4e9e947c98c0b97b2281b6b6e97`. It does not reprove or audit that
theorem. Its archived README is pinned as provenance in SOURCES.json.

Fix commuting binary idempotents P,Q in dimension n. Let their joint-sector
dimensions, ordered as 00,10,01,11, be r00,r10,r01,r11. A complete header is
an ordered basis M in GL_n(F2). Its split pair consists of the first d columns
of M and first d rows of M^-1. Let N count complete headers with both leading
blocks I_d and Schur-commutator rank 2d, and let Z count complete headers with
both leading blocks I_d. These are one-block events, not full-guard chains.

Use ssafwann's factor counts, restated for clarity. Put

\[
I(s,k)=\prod_{j=0}^{k-1}(2^s-2^j),\quad G(s)=I(s,s),
\]

with I(s,k)=0 unless 0<=k<=s. Define

\[
U(r,d,\rho)=\sum_{k=\rho}^{\min(d,r)}
 {d-\rho\brack d-k}_2 I(r,k)2^{d(r-k)},
\]

\[
A(r,d,\rho)=I(r,d)2^{\rho(r-d)}I(r-d,d-\rho)
\]

when r>=d, and zero otherwise. U counts arbitrary factorizations XY=T of a
fixed rank-rho d-by-d matrix through a dimension-r space. A also requires X
surjective and Y injective. These formulas and the G(n-d) completion
multiplicity are credited inputs from #4678.

For each (a,b) put h=d-a and w=d-b. Grouping that theorem's sum over actual
H by the exact nullity pair gives

\[
\boxed{\begin{aligned}
N=G(n-d)\sum_{a=0}^d\sum_{b=0}^{d-a}
 C_d(a,b;2)\,&U(r_{00},d,w)A(r_{10},d,w)\\
 &\cdot A(r_{01},d,w)A(r_{11},d,h),\\
Z=G(n-d)\sum_{a=0}^d\sum_{b=0}^{d-a}
 C_d(a,b;2)\,&U(r_{00},d,w)U(r_{10},d,w)\\
 &\cdot U(r_{01},d,w)U(r_{11},d,h).
\end{aligned}} \tag{5}
\]

This substitution is the improvement. There is no enumeration of 2^(d*d)
compressed products, and no independence approximation. The predecessor's
complete-header density remains N/G(n) and its conditional density remains
N/Z when Z>0. Split-pair counts are N/G(n-d) and Z/G(n-d).

For four equal dimension-d sectors, all three A factors require h=w=d.
The U factor then also equals G(d). Consequently

\[
N/G(3d)=C_d(0,0;2)G(d)^4. \tag{6}
\]

At d=4, C_4(0,0;2)=5824. The sharp and identity-pivot split-pair counts from
(5) are respectively

```text
962018618785136640000
8291457123053721102581760
```

Each becomes a complete-header count after multiplication by G(12).
These are formula evaluations, not a literal census of GL_16(F2).
