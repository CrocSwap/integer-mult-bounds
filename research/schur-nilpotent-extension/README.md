# Nilpotent identity-block Schur deletion: the whole residual and its weight

This is a written algebraic side result with bounded exact corroboration,
prepared for ssafwann with substantial OpenAI Codex (gpt-6-astra) assistance,
one agent; Apache-2.0. It answers the whole-residual extension handoff in
[PR5256](https://github.com/CrocSwap/integer-mult-bounds/pull/5256) for nilpotent
compressed products. That pending PR is motivation, not a theorem premise.
Independent human and formal proof-kernel review are unclaimed.

**Result.** Fix a commuting idempotent pair and its four joint-sector dimensions.
Among identity-block deletions with a specified nilpotent matrix H and maximal
Schur-commutator rank, the entire ordered residual pair has one simultaneous
conjugacy orbit. We give an explicit representative over any field. In odd
characteristic its central operator has one chain of length k and one of length
k+1 for every H Jordan block of length k, plus specified scalar summands. Over
finite fields we count exactly the splits and complete headers in this fixed-H
event. This is not the unconditional mass of the residual orbit.

The generic factor equivalence and stabilizer method are predecessor results;
the contribution is their application to this Schur family, the explicit
complementary attachments, and the resulting whole-residual Jordan law. This
does not reopen the earlier minimum-dimension problem or scalar state census.
No selected-frontier file changes: selected conditional κ remains 0.00302015.
Physical header selection/emission, reads, owned/borrowed state, dirty restoration,
precision, storage, stock, dispatch and the complete consumer bill remain
unknown, not zero.

## Contract and statement

Let F be any field, U=F^d with d>=1, and P0,Q0 commuting idempotents on V.
Write V as its ordered joint eigenspaces V00,V10,V01,V11, of dimensions r_j.
A split is i:U->V and π:V->U with πi=I. A complete header is an ordered basis
M=[i,B], with B an ordered basis of ker π. In that header put

```text
P=M^-1 P0 M=[I b; c D],       Q=M^-1 Q0 M=[I f; g E],
S=D-cb,                     T=E-gf,
H=π P0 Q0 i,                K=ST-TS,          Z=(S-T)^2.
```

Block idempotency gives S²=S and T²=T. Consequently
Z=S+T-ST-TS commutes with both residual maps.

Restrict to headers with the displayed common identity pivot, nilpotent H,
and rank K=2d (called sharp here). Set a=dim ker H, W=I-H. Then necessarily

```text
r00=d+s00, r10=d+s10, r01=d+s01, r11=d+a+s11,   s_j>=0.       (1)
```

Conversely every such profile admits a sharp split with that exact H. For fixed
H and profile, all resulting ordered pairs (S,T) are simultaneously similar.
Their representative is the minimal pair below, plus the scalar pairs

```text
(0,0)^s00 direct-sum (1,0)^s10 direct-sum
(0,1)^s01 direct-sum (1,1)^s11.                              (2)
```

There is no claim that different H/profile data always give distinct orbits.

Choose N:F^a->U whose image complements im H. On U^3 direct-sum F^a, with
coordinates (x,y,z,t), the minimal pair is

```text
S(x,y,z,t) = (H(x-z)-Nt, 0, W(z-x)-Nt, t),
T(x,y,z,t) = (0, H(y-z)-Nt, W(z-y)-Nt, t).                   (3)
```

Its dimension is 3d+a. All choices of N yield the same ordered-pair orbit.

If char F is not 2, put R=2I-H. In coordinates (u,v,t,c), (3) is a common
zero summand of dimension d and the following core on U^2 direct-sum F^a:

```text
           [ H/2   H/2  -N ]                [  H/2  -H/2  N ]
S_core  =  [ R/2   R/2   N ],    T_core  =  [ -R/2   R/2  N ].       (4)
           [  0     0    I ]                [   0     0   I ]
```

If the nilpotent Jordan block lengths of H are k_1,...,k_a, the complete
Jordan form of Z is

```text
direct-sum_i (J_(k_i)(0) direct-sum J_(k_i+1)(0))
 direct-sum 0_(d+s00+s11) direct-sum I_(s10+s01).             (5)
```

In particular, for j>=1,

```text
rank Z^j = rank H^j + rank H^(j-1) + s10+s01,                (6)
m_Z(t) = t^(max_i k_i+1) (t-1)^epsilon,
epsilon = 1 if s10+s01>0, otherwise 0.
```

Nilpotent Jordan blocks exist over every field. The odd-characteristic
qualification matters: for F2,d=1,H=0 and no padding, Z=0, whereas (5) would
contain J2(0). Equations (1)--(3) and the counting result below still hold in
characteristic two; (4)--(6) are not asserted there.

Over F_q (any prime power), write G_r=|GL_r(F_q)|, G_0=1. The number of sharp
splits for the **fixed original ordered pair** and **exact matrix H** is

```text
N_H = (G_r00 G_r10 G_r01 G_r11) /
      (G_s00 G_s10 G_s01 G_s11 q^(a^2+2a s11)).              (7)
```

The number of complete ordered headers in this event is N_H G_(n-d), where
n=sum r_j. All those headers reach the same residual orbit, but headers with
other H may reach it too. Thus (7) does not compute its unconditional transition
probability or the number of occurrences of one coordinate representative.
There is no division by GL_d or by a similarity-class size: H is fixed in the
ordered leading coordinates, and changing i's basis changes the split.

## Proof

### The sector data and existence

Let E_j be the four joint-sector projectors, Y_j=E_j i and X_j=π|V_j.
The equations πi=πP0i=πQ0i=I and πP0Q0i=H give

```text
X00Y00=-W, X10Y10=W, X01Y01=W, X11Y11=H.                    (8)
```

We use the all-field sharp-sector criterion of Nick Petalas
[PR4746](https://github.com/CrocSwap/integer-mult-bounds/pull/4746): under these
identity-pivot hypotheses, rank K=2d iff each of Y10,Y01,Y11 is injective and
each of X10,X01,X11 is onto. This criterion, and its factor-capacity consequence,
are credited premises, not newly claimed results. Since H is nilpotent, W is
invertible; (8) also makes Y00 injective and X00 onto.

For any onto X:F^r->U and injective Y:U->F^r with XY=A, the intersection
im Y intersect ker X is Y ker A. Hence r>=d+nullity A. Applying this to (8)
gives (1). Attainment uses

```text
X00=-W, X10=X01=W, X11=[H,N],
Y00=Y10=Y01=I,     Y11=[I;0],                               (9)
```

with unused zero columns/rows for the s_j padding coordinates. Their combined
πi is -W+W+W+H=I, both compressed projectors are I, and all four X/Y pairs
have full ranks. The cited criterion gives sharpness.

### Why the whole ordered residual is forced

We use the inclusion/observation extension principle of codyw912
[PR4735](https://github.com/CrocSwap/integer-mult-bounds/pull/4735), generalized
by MatShep [PR4762](https://github.com/CrocSwap/integer-mult-bounds/pull/4762).
Here is its short specialization, to expose exactly the required hypotheses.

Suppose X,Y and X',Y' have the same ambient dimension, X,X' are onto, Y,Y'
are injective, and XY=X'Y'=A. On L=im Y, the map Yu->Y'u is an isomorphism
respecting X and X'. Its restriction sends L intersect ker X to
im Y' intersect ker X', because both are the images of ker A. Extend it to
an isomorphism ker X->ker X', and therefore to L+ker X. Complete the domain
and target bases by lifts under X and X' of the same basis of a complement
to im A in U. The resulting invertible g obeys

```text
gY=Y',                 X'g=X.                              (10)
```

Apply (10) independently in the four sectors to any sharp split and (9),
including its padding. Their direct sum g commutes with P0,Q0 and satisfies
gi=i', π'g=π. For any headers M,M' completing the splits,

```text
(M')^-1 g M = diag(I_d,L),             L invertible.
```

The two full pairs and hence their Schur complements are conjugated by this
block-diagonal map. Thus L simultaneously intertwines S,T with S',T'. This
controls the entire residual, including coordinates outside im K. It is not
merely equality of central spectra. It also proves independence of N.

In the padded representative, i and π vanish on each unused sector direction.
Those directions are therefore untouched scalar residual summands, giving (2).
For the minimal representative, ker π has the parametrization

```text
(v00,v10,v01,v11,extra11)
 = (x+y+W^-1 Hz+W^-1 Nt, x, y, z, t).                       (11)
```

The residual of P0 on ker π is P0-P0 i πP0, and similarly for Q0: this follows
by subtracting the lower-left times upper-right block using πP0i=πQ0i=I.
Substitution of (11) gives exactly (3).

### The extra nilpotent chains in odd characteristic

Both W and R are invertible. Set

```text
u=x-y,   v=x+y-2z,   c=z+WR^-1 v+R^-1 Nt.
```

This is an invertible change of coordinates: z=c-WR^-1v-R^-1Nt,
x=z+(v+u)/2 and y=z+(v-u)/2. Substitution into (3) shows both maps kill
c-directions and have output c=0; their remaining action is (4). In particular,
with Θ=H(2I-H)=HR,

```text
S_core-T_core = [ 0 H -2N ],
                [ R 0   0 ],
                [ 0 0   0 ]

Z_core = [ Θ 0    0 ],
         [ 0 Θ -2RN ],
         [ 0 0    0 ].                                     (12)
```

The invertible R commutes with H, so rank Θ^j=rank H^j for every j. Thus Θ has
exactly H's nilpotent block lengths. Put B=-2RN. Since R preserves im H and
induces an invertible map on U/im H, im B complements im Θ=im H. For
E=[Θ B;0 0], acting on U direct-sum F^a,

```text
E^j = [Θ^j Θ^(j-1)B;0 0],
im E^j = im Θ^(j-1),                 j>=1.                 (13)
```

Consequently E has the nilpotent chains k_i+1: their rank sequence is
sum_i max(k_i+1-j,0)=rank H^(j-1), which uniquely determines a nilpotent
Jordan partition. Combine (12), the d common zero coordinates, and the scalar
summands (2) to obtain (5), (6), and the stated minimal polynomial.

### The exact fixed-H weight

For a sector product A of nullity c, take r=d+c+s. The argument (10) says GL_r
acts transitively on its full-rank factor pairs. We specialize the extension
stabilizer calculation of Nick Petalas
[PR4915](https://github.com/CrocSwap/integer-mult-bounds/pull/4915); the generic
method is credited rather than presented as new.

Put L=im Y and K0=ker X. Choose

```text
F^r = (L intersect K0) direct-sum R0 direct-sum Z0 direct-sum J,
dimensions: c, d-c, s, c,
L=(L intersect K0)+R0,     K0=(L intersect K0)+Z0.
```

The stabilizer gY=Y, Xg=X consists exactly of

```text
[ I 0 U V ]
[ 0 I 0 0 ]
[ 0 0 G E ]
[ 0 0 0 I ],
```

where G is arbitrary in GL_s and U,V,E have dimensions c-by-s, c-by-c,
s-by-c. Indeed g-I vanishes on L and has image in K0; these are precisely
the two stabilizer equations, and invertibility is equivalent to that of G.
Its order is G_s q^(c^2+2cs), so the sector factor count is
G_r/(G_s q^(c^2+2cs)). In (8), the first three products have c=0 and the last
has c=a. The four factor choices are independent: (8) already ensures all
split/pivot equations. Their product proves (7). Every split has exactly
G_(n-d) ordered bases of ker π, proving the complete-header count.

## Concrete first fixtures

For F3,H=J3(0), the minimal input profile is (3,3,3,4), n=13. The residual
has dimension 10 and Z has blocks (4,3,1,1,1). This explains the t^4 whole
minimal polynomial that motivated the handoff; a restricted t^3 annihilator
cannot remove the extra length-four chain.

For d=1,H=0, profile (1,1,1,2), over F3 equation (7) gives
2^3*48/3=128 splits and 128*|GL4(F3)|=3,105,423,360 complete headers.
The complete split inventory contains 19,602 splits; the verifier computes
literal Schur ranks on every identity-pivot H=0 candidate and constructs an
actual ordered-pair intertwiner for every sharp one. Over F2 the count is
3 splits / 60,480 headers, recovering the earlier ssafwann
[PR4678](https://github.com/CrocSwap/integer-mult-bounds/pull/4678) fixture,
not claiming it as new. Binary padding in sectors 00,10,11 gives respectively
18,18,21 splits; padding 11 to dimension 3 checks the mixed exponent 2a s11.

## Reproduction and evidentiary limits

```sh
python3.12 -B scripts/research_package.py --package research/schur-nilpotent-extension
python3.12 -I -W error -B research/schur-nilpotent-extension/verify.py
python3.12 -I -W error -O -B research/schur-nilpotent-extension/verify.py
```

The standard-library checker uses explicit exception-based checks. It does not
import predecessor executables, access the network, invoke Git, or write files.
It checks:

- All 834 nilpotent H in the complete domains d=1,2,3 over F2/F3 and d=1,2
  over F5. Full commuting pairs are built and literal Schur complements
  compared by invertible coordinate maps to (3); all 765 odd-field cases are
  also compared to (4), with their full central rank sequences checked.
- 45 padded fixtures, including J3 and J3 direct-sum J1. Both ordered padding
  decompositions and concrete factor/header/residual intertwiners are checked.
- Five exhaustive scalar split domains, with all 188 sharp outcomes transported
  to the canonical ordered residual; six independent full-rank factor censuses
  check the stabilizer denominator (including binary d=2,r=4).
- Nine rejecting controls: nonsquare/nonnilpotent H, negative padding, binary
  use of the odd formula, missing extended chain, missing stabilizer exponents,
  and a rank-defective factor. Normal and optimized runs exercise the same checks.

These are finite prime-field corroborations of the written proof, not an
exhaustive theorem check over arbitrary fields or a proof-kernel certificate.
The symbolic argument covers arbitrary fields / prime powers at the stated
boundaries. General nonnilpotent H, the characteristic-two central Jordan law,
later full-guard survival, unconditional state multiplicities, physical supplier
costs and selected-caller admission are unproved here. No Lean, Docker or full
selected scientific cold replay is claimed. The prior source-binding orientation
stopped at a sparse-omitted checkpoint; it was not a baseline pass.

The package records exact main-source pins, source-head citations, overlap
coverage, verification environment and scope change in TASK.json/SOURCES.json.
Only these five package files are proposed for archive. Committed-byte,
source-history and exported read-only checks are recorded in the PR/handoff
because a package cannot embed its own final commit ID without changing it.

## Open next questions

1. For this same nilpotent family in characteristic two, determine the full
   central Jordan partition from (3), starting with H=J2 and H=J3. The odd
   change of coordinates is invalid there. This is a distinct bounded algebraic
   question; no claim is held and no further census is authorized by this note.
2. If a named consumer actually needs these states, specify its header law and
   cost allowance before asking for unconditional or later-guard transition
   probabilities. Equation (7) is only fixed-H event mass. Different H may
   coalesce into one residual orbit; physical cover and selection costs remain
   unknown. Without that contract, stop this branch at the present result.

## Attribution and source status

Exact main-based source bytes are pinned in SOURCES.json. These are archived
predecessors, not automatically scientifically accepted theorems. We rely on the
stated sharp criterion in #4746 and give the used factor/stabilizer specialization
above so its application is independently reviewable.

- Nick Petalas: [#4746](https://github.com/CrocSwap/integer-mult-bounds/pull/4746)
  all-field sector criterion/construction, [#4597](https://github.com/CrocSwap/integer-mult-bounds/pull/4597)
  ordered Schur factorization, [#4801](https://github.com/CrocSwap/integer-mult-bounds/pull/4801)
  scalar central law/block question, and #4915 extension-stabilizer weights.
- MatShep #4762 and codyw912 #4735: factor-system equivalence and extension lemma.
- ssafwann: [#4657](https://github.com/CrocSwap/integer-mult-bounds/pull/4657),
  [#4671](https://github.com/CrocSwap/integer-mult-bounds/pull/4671), #4678,
  and pending #5256 at `c72d6ff431cf5c979f5010018d8eba0c15577bce`; the last supplies
  the handoff and adapted matrix helpers, with no runtime dependency on its branch.
- Ryanson Jonathan #4609/#4617 and lee-phys #4634 retain sharpness/seed credit.
  Mihir Srivastava #4689, JoyboyBrian #5072 and Krzysztof Wojt #5128 are distinct
  successor state/incidence/arbitrary-pivot results, not reclassified as ours.
- Cinna Davis #4100 and source527/commdata2338/Jose Manuel retain the BIT/header
  and normalizer context. Repository workflow tooling retains its original credit.
