# Full-bank retirement at a completed binary child

## 1. Statement and exact scope

This note extends the auxiliary-projector obstruction in
CrocSwap/integer-mult-bounds#6726, `frozen/RESEARCH-NOTES.md`, to an entire
coupled bank. It does not assume an invertible auxiliary prefix, a projector,
or a one-dimensional auxiliary rotation. It also prices the particular escape
obtained by synthesizing a central-dependent cut basis with new thin queries.
**No new κ.**

Let F be a field, let L and R be independent invertible body symbols, and work
in the free rank-two algebra

    A = F[L^±1,R^±1,S]/(S²−1).

The elements 1 and S are linearly independent over F[L^±1,R^±1], including in
characteristic two. In the source normalization S=λq⁻¹. An *ordinary* matrix
has entries in F, independent of S,L,R. All four banks X,Y,A,B have width w;
their inputs are arbitrary and independent. The full binary endpoint is

    C = LR [ I  S I  0    0
             0  I    0    0
             0  0    S I  0
             0  0    0    S I ].                         (1)

At the cut immediately after the complete left child, the fixed active
history gives

    x = L(B − S Y + S A),       y = L(Y − S B),
    (a,b)^T = K (X + S Y − S A, Y)^T.                    (2)

Here K is any 2w by 2w matrix over A. This deliberately grants more auxiliary
processing than the source's ordinary rotated idle projection. A K need not
admit a legal completion to (1); granting it can only strengthen the negative
result. An actual application still requires the prescribed full endpoint.

Retiring r independent scalar channels requires ordinary input and output
columns U,Uo and rows D,Do, with

    C U = t Uo,       Do C = t D,       Do Uo = I_r.     (3)

Thus D U=I_r. At the cut P defined by (2), it requires a resident column V
and cut row Bc satisfying

    P U = m V,       Bc P = m D,       Bc V=I_r.        (4)

For an ordinary retirement V and Bc are ordinary. Conditions (3) allow
different ordinary input and output bases, mixing all four banks. The old
scalar target t is LR or SLR and the proposed prefix m is L or SL. This is a
necessary independent-channel interface, not just a rank nomination.

## 2. The full endpoint forces the old channel into the auxiliary bank

If t=LR, comparison of the S coefficients in C U=LR Uo forces
U_Y=U_A=U_B=0. Comparison in Do C=LR D forces Do_X=Do_A=Do_B=0,
so D has only a Y block. Consequently D U=0, contrary to (3).

If t=SLR, comparison of constant coefficients in the column identity forces
U_X=U_Y=0. The row identity similarly forces Do_X=Do_Y=0. On the auxiliary
bank C is exactly SLR I, so Uo=U and Do=D, with both U and D supported on
A,B. Allowing arbitrary ordinary mixing with active fields therefore does
not enlarge the eligible scalar-target channels.

## 3. No ordinary full-bank cut pair

Write U=(0,0,U_A,U_B)^T and D=(0,0,D_A,D_B).

For m=L the Y block of P U is −SL U_B. Its odd coefficient forces U_B=0;
then the X block SL U_A forces U_A=0. No nonzero channel exists.

For m=SL the X block is L U_B+SL U_A. Its even coefficient forces U_B=0.
Now write the arbitrary ordinary cut row as Bc=(p,q,u,v), and put
(W1,W2)=(u,v)K. Equation (2) gives

    Bc P = (W1,
            −SL p + L q + S W1 + W2,
            SL p − S W1,
            L p − SL q).                              (5)

The X coefficient of Bc P=SL D forces W1=0, and the A coefficient then
gives D_A=p. The B coefficient gives

    p − S q = S D_B.

Because p,q,D_B are ordinary, its even coefficient is p=0. Hence D_A=0.
Together with U_B=0 this gives D U=0, contradicting independence. This
proof makes no restriction on K, including its S dependence, and works
for every w and r≥1. It does not assume the cut row is auxiliary-supported.

## 4. The central-dependent escape has a forward-and-restoration debt

Keep the ordinary source and target bases in (3), but permit a
central-dependent cut basis G and its restoration H=G⁻¹. Each is implemented
by invertible ordinary matrices and new rank-one thin central queries

    I + S u v^T,       u,v ordinary,       v^T u=0.

The fixed active history is unchanged. Queries already in that history are
not free extra gates in G or H. If G uses kf new queries and H uses kr, write
G=G0+S G1 and H=H0+S H1. Multiplication by an ordinary matrix cannot increase
odd-part rank; multiplication by one central query changes the odd part by
one rank-one matrix. Therefore rank(G1)≤kf and rank(H1)≤kr.

Let E select the r retired coordinates after G. Now allow both the cut row
Bc=E G and resident column V=H E^T to depend on S; conditions (4) remain
necessary. For m=SL, the active blocks of P U=SL V give

    V_X=U_A+S U_B,       V_Y=−U_B.

The odd X block of V is U_B, so rank(U_B)≤rank(H1). The X, A and B blocks
of (5), with Bc now central-dependent, give

    W1=0,       p=D_A,       q=S D_A−D_B.

Thus the odd Y block of Bc is D_A and rank(D_A)≤rank(G1). Independence gives

    I_r=D_A U_A+D_B U_B,
    r≤rank(D_A)+rank(U_B)≤kf+kr.                       (6)

For m=L, the odd active blocks of V are (U_A,−U_B)^T. They have column
rank r because U has rank r. Hence kr≥r, which also implies (6).
These bounds do not assume V remains ordinary after permitting G to use
queries. Counting only the forward basis can give a false stronger bound.

The same bound holds when r0 channels have prefix L and r1 have prefix SL.
Order the source/target channels accordingly, and let M be the active-column
part of the odd cut-row matrix and N the active-row part of the odd resident
matrix. Their blocks are

    M0=[D_A0,−D_B0],    M1=[0,D_A1],
    N0=[U_A0;−U_B0],    N1=[U_B1;0].

Thus M0 N0=I_r0, M1 N1=0 and r1≤rank(M1)+rank(N1). For completeness, if
M=[M0;M1] and N=[N0,N1], the elementary rank inequality

    r0+rank(M1)+rank(N1)≤rank(M)+rank(N)

follows by choosing row and column complements
M0=A M1+M0' and N0=N1 B+N0', with ranks of the primed matrices at most
rank(M)−rank(M1) and rank(N)−rank(N1). Since M1 N1=0,
I_r0=A M1 N0'+M0' N0; subadditivity of rank proves the inequality.
Consequently r0+r1≤rank(G1)+rank(H1)≤kf+kr. Mixed prefix types therefore
cannot share queries so as to escape the total debt.

There is an exact sharpness example for (6). Take w=1, K=L I, and retire
both old auxiliary channels through SL. The four-gate cut basis is

    X ← X + S Y;     A ← A + X;
    Y ← Y − B;       Y ← −Y.

After these gates the four fields are

    (SL A, SL B, L(X+S Y), L Y).

One forward query thus exposes **two** independent channels. Swap X,Y with
genuinely fresh arbitrary inputs E,F, apply the inverse four-gate basis,
finish the right child and the remaining R idles on A,B, finish the original
binary tail, and swap A,E and B,F at output. The exact six-input endpoint is

    Xout=LR(X+S Y),  Yout=LR Y,
    Aout=SL A,      Bout=SL B,
    Eout=R E,       Fout=R F.                          (7)

The inverse basis uses a second query, attaining kf+kr=r=2. A one-channel
version with K=diag(L,LR) also exists: use the cut basis
`X←X+S Y; A←A+X; SWAP(X,A)`, swap A with a fresh E, undo the basis, and
finish the word. It gives old A target SL, old B target SLR and fresh E
target R, again at the cost of two new queries. The replay checks these
whole arbitrary-input endpoints and rejects omitted restoration queries,
wrong fresh-input routing, and wrong final target association.

The query-rank debt concerns this basis-and-inverse construction with new
thin queries. It does not assert the same tariff for a packed spectator
oracle, an altered suffix that eliminates restoration, or a redesigned
history that reuses an existing query.

## 5. Even an optimistic complete price is unfavorable

Let the left and right body ranks be positive integers a,b and let
H(x)=x^t with 0<t<1 (t=1−κ). Replacing one paid idle of rank a+b by
paid ranks a and b, and replacing its old target of rank a+b+1 by targets
of ranks a+1 and b, changes target-minus-paid credit by

    g(a,b)=H(a+1)−H(a)−H(a+b+1)+H(a+b).

For a pure L prefix, the new targets instead have ranks a and b+1;
the gain is g(b,a). Strict concavity gives 0<g(a,b)<H(a+1)−H(a)<1,
and likewise 0<g(b,a)<1. Each new rank-one thin
central query costs H(1)=1. For r independently retired channels of either prefix type L or SL,
even granting all ordinary routing and restoration for free, Section 4
imposes k=kf+kr≥r paid thin queries, so

    total change ≤ Σ_i g(a_i,b_i) − k < r−k ≤ 0.        (8)

The two-channel escape (7) exactly attains the query-count lower bound,
but its gain is still strictly smaller than that cost. Coupling ordinary
controls cannot remove this rank debt. For independent per-port instantiation, the physical factor 104 multiplies
both sides and preserves the sign. Arbitrary coupling of distinct physical
central operators S_q is outside this common-S theorem. Additional nonnegative charges only worsen this optimistic budget. A
changed productive-helper contract is outside its scope and must be priced
afresh.

The inequality is a universal analytic result, not a conclusion from a
finite search. It rules out an improvement of the full supplier
through this particular added-query internal fragmentation mechanism.

## 6. Limits and questions that remain open

The fixed active prefix (2), ordinary old scalar-target bases, and thin
query alphabet are substantive hypotheses. This note does not exclude a
cut inside a child, a changed active history, mixing different old body
monomials, a different target contract, reuse of existing query work, or
cheaper packed operator-valued controls. It does not prove a global native
or root optimum. It neither replays nor strengthens the five retained
framework assumptions of the selected construction. The source's root
fragments occur at different cuts and are not contradicted.

The most concrete remaining question is whether a redesigned active history
can supply the necessary odd row or column from already paid work while preserving every
arbitrary-input endpoint and a profitable full invoice. Any such proposal
must identify the particular existing query being reused and prove the
new prefix and suffix, rather than treating S as an ordinary free scalar.

The ordinary controls in this theorem are F-valued and S-independent.
Fixed source normalizers can be analyzed in a central-character sector when
they reduce to such scalar units. No general reduction of physical address
translations or arbitrary operator-valued controls to this model is assumed.
See HEADER-SATURATION.md for the separate changed-history theorem; its
positive body and atomic-stage hypotheses replace the fixed prefix.
