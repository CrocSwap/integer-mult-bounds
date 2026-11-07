# Whole-bridge carriers in the fixed odd/odd p104 root

Jerry Chen / @CubeJerry, with substantial OpenAI GPT-6 Astra Pro assistance.
Apache-2.0. The root and native invoice are inherited from
CrocSwap/integer-mult-bounds#6833 at
`51f54e3c31f2f3a3e056a483b3ed66ae916ad06a`.
See `retained/SOURCE-PINS.json` for exact retained bytes and `NOTICE` for credit.

**No new κ.** This note changes a carrier *commutation premise*, establishes
its algebraic consequences, and prices a declared relaxation. It does not
construct an admitted supplier, prove the framework assumptions, or establish a
universal obstruction to changing the root or recursive interface.

## 1. Source and the interface under study

Work over a characteristic-zero field. The algebraic identities below also hold
over any field of characteristic other than two. Let the two arm lengths
`a,b` be positive odd integers, put `m=a+b`, and use `n=m+2` field coordinates

\[
 A,f_0,\ldots,f_{a-1},h_0,\ldots,h_{b-1},E.
\]

A coordinate symbol denotes a column, and a superscript `*` denotes its dual
row. Let `F=Σf_j`, `H=Σh_j`, `F_alt*=Σ(-1)^j f_j*`, and
`H_alt*=Σ(-1)^j h_j*`. The `m` full native queries have normalized form

\[
 T_i(S)=I+(S-1)x_i y_i^*,\qquad S^2=I.
\]

Their chronological columns, rows, and productive coordinate masks are

\[
\begin{array}{lll}
L_j:&x=A+f_j+2\sum_{k<j}f_k,&y^*=A^*-f_j^*,\quad M=\{A,f_0,\ldots,f_j\};\\
R_j:&x=-A+h_j+2\sum_{k>j}h_k,&y^*=A^*+h_j^*,\quad M=\{A,h_j,\ldots,h_{b-1}\}.
\end{array}
\]

Between the arms are three thin queries, in this order:

\[
\begin{array}{ll}
x_0=F+H+E,&y_0^*=A^*;\\
x_1=-A+2H,&y_1^*=2A^*-F_{\rm alt}^*+H_{\rm alt}^*+E^*;\\
x_2=-A+2H-E,&y_2^*=3A^*-2F_{\rm alt}^*+2H_{\rm alt}^*+E^*.
\end{array}
\]

Every query has `y_i*x_i=0`. Write `U_i=I-2x_i y_i*` for its `S=-1`
specialization. The complete chronological word has endpoint `-I_n`.
The formulas are checked against the retained constructor for all 25 odd/odd
pairs `a,b∈{1,3,5,7,9}`. These finite checks supplement the source proof and the
symbolic derivation below; they do not prove all arm lengths by enumeration.

The concrete priced instance is `a=b=9`: 18 native calls, 104 ports, one central
rank-one address, and eight fresh address dimensions at each full site. Neither
the root word nor any native helper is changed by the carrier experiment.

### Declared ordinary-carrier contract

A carrier packet consists of a sector-independent field idempotent `J` and one
contiguous interval of full sites. Its support is contained in every productive
coordinate mask in its interval, on **both** the column and row sides. It obeys
`Jx_i=0` and `y_i*J=0` at each covered full native query. Across the central
bridge it must commute with the **entire bridge**, rather than separately
annihilate its three thin queries. Packets whose intervals overlap are mutually
annihilating idempotents in both orders. Packets with disjoint intervals need not
be mutually annihilating. Thus the model does not impose one globally
orthogonal decomposition of all packets throughout the computation.

At site `i` the packets partition the idle part of the productive mask, whose
rank is `|M_i|-2`. An `r`-dimensional field packet covering `l` fresh full sites
incurs `r` paid recursive copies of address rank `8l`. It is **not** priced as
one recursive call of rank `8rl`. The latter interpretation would be a changed
recursive interface and is outside this theorem. Targets are the coordinate
outputs of the source accounting: field `f` has target rank
`1+8#{i:f∈M_i}`. The three thin rank-one jobs and all 18 native signed profiles
remain charged. This also retains source access, helpers, and restoration
already present in those native profiles.

We price any additional ordinary adapters as free. This is an optimistic
relaxation for an obstruction: a real nonnegative adapter invoice cannot improve
its result. It is not a license to make recursive Gaussian maps, fresh source
windows, new helpers, or independent outputs free. Non-idempotent cancellation,
sector-dependent recursive adapters, revised native interfaces, alternative
output representations, and changed roots are not covered.

## 2. Why an ordinary moving frame does not create a moving carrier

For an independent fresh-address operator `W`, define

\[
 D_J(W)=I+J\otimes(W-I).
\]

Suppose a normalized block `K(S)` with `K(1)=I` transparently relocates this
same address job:

\[
 K(S)D_J(W)=D_{J'}(W)K(S).
\]

Assume `J,J'` are field idempotents independent of `S,W`, and that the identity
is an operator identity including the `S=1` sector. Specializing there gives
`(J-J')⊗(W-I)=0`; for nontrivial `W-I` this forces `J'=J`. The remaining condition
is commutation with `K(S)`. For a block polynomial in a common involution `S`,
it is enough to check its two specializations, so only `[J,K(-1)]=0` remains.

If the neutral specialization is an ordinary invertible field adapter `B_0`
instead of `I`, the same equation gives `J'=B_0 J B_0^-1`. Removing this known
ordinary adapter and expressing both endpoints in a common chart returns the
previous statement. A sequence of such ordinary chart changes provides no extra
transparent carrier directions. Adapters depending on the fresh address job or
on the recursive sector are explicitly excluded from this reduction.

This is a statement about **full projectors**, not only their images. A shear
can preserve an image line while altering its dual row. Conversely, a swap can
satisfy a minus-sector relocation identity with distinct endpoint projectors
while failing the neutral sector. Both mistakes have executable controls.

## 3. Exact central-bridge decomposition

Define

\[
\begin{split}
v&=A+F-H,\qquad z^*=-A^*+F_{\rm alt}^*-H_{\rm alt}^*,\\
u&=F+H,\qquad w^*=2A^*-F_{\rm alt}^*+H_{\rm alt}^*,\\
P_E&=EE^*,\qquad P_v=vz^*,\qquad N=uw^*.
\end{split}
\]

Oddness of both arms gives

\[
z^*v=1,\qquad z^*u=w^*v=w^*u=0.
\]

`P_E,P_v` are mutually annihilating rank-one idempotents, `N²=0`, `rank N=1`,
and each product of `N` with either projector is zero. Multiplying the three
thin transvections in their chronological order gives

\[
 \boxed{B:=U_2U_1U_0=I-2(P_E+P_v)-2N.}
\]

This can be derived without a large matrix multiplication. In terms of the
three columns `u,v,E` and rows `w*,z*,E*`, the thin data are

\[
x_0=u+E,\quad x_1=u-v,\quad x_2=u-v-E,
\]

\[
y_0^*=w^*+z^*,\quad y_1^*=w^*+E^*,\quad y_2^*=2w^*+z^*+E^*.
\]

The only nonzero pairings among these aggregate vectors are `z*v=E*E=1`.
Expanding the three rank-one factors yields the boxed identity. It implies

\[
 B^2=I-4N,\qquad (B-I)^2(B+I)=0.
\]

On `im(P_E+P_v)` the bridge is `-I`; on its complementary invariant subspace it
is `I-2N`. Consequently its minus-one column eigenspace is exactly
`span(E,v)`, and its minus-one row eigenspace is exactly `span(E*,z*)`.

Every full native query annihilates these two planes: `y_i*E=y_i*v=0` and
`E*x_i=z*x_i=0`. They are the complete common native idle planes. Indeed, the
native `m×m` Gram matrix is `G_ij=sgn(i-j)` in chronological order. For even
`m`, a vector in its kernel must alternate in sign by subtracting successive
rows; the first row then forces its first entry to vanish. Hence `G` is
invertible, so the native columns and rows each have rank `m`, leaving precisely
two-dimensional annihilators.

It follows that **every idempotent with column image in `span(E,v)` and row
image in `span(E*,z*)` is native-idle and commutes with the whole bridge**.
This includes `P_E`, which does not annihilate the individual thin queries.
Thus the whole-block contract strictly expands the previous pointwise-thin
annihilation contract. It does not imply that such a carrier is supported by a
particular productive mask.

### Independent eigenspace interpretation

The independent review observed a useful strengthening. For every full site,
`w*x_i=1` on the left arm and `-1` on the right, while `y_i*u=-1` on the left
and `1` on the right. If `J` commutes with `B`, then it commutes with
`N=(I-B²)/4`. The full-site annihilation conditions therefore imply

\[
 Ju=0,\qquad w^*J=0.
\]

For example, `JNx_i=NJx_i=0` and `Nx_i=±u`. Thus a crossing carrier uses actual
bridge eigenspaces, not the nontrivial generalized plus-one direction. This
supplies a separate eigenspace calculation of the finite capacities in Section
6. The cyclic-closure proof below only needs an upper bound and does not assume
that arbitrary nonsemisimple commutants attain it.

## 4. Original masks and activating the empty field

Any original left mask intersects any original right mask in `{A}`. A projector
supported there has form `c AA*`; its required native annihilation makes `c=0`.
Thus the original productive masks support **no nonzero crossing packet**,
even under whole-bridge commutation and ordinary chart changes.

The projector `P_E` is a new whole-bridge carrier, but `E` is originally inactive
at all fresh sites. Activating it at `w≥1` sites changes its target rank from `1`
to `8w+1`. Even if all new idle work can be pooled into one job of rank `8w`,
its signed change at `f(r)=r^t`, `0<t<1`, is

\[
 f(8w+1)-f(1)-f(8w)<0.
\]

Strict concavity gives this inequality. If the sites cannot actually be pooled,
splitting the paid job only increases its concave moment. Therefore arbitrary
pure-`E` activation cannot help under the declared target/copy contract.

Any nonzero projector on the complete common native idle plane other than
`P_E` has a nonzero `v` component in its column image or a nonzero `z*` component
in its row image. Since both vectors have nonzero coefficients on every one of
the `m+1` nonempty coordinates, such an activation requires all those coordinates
in its productive mask. This is a support statement, not a general theorem
about arbitrary carriers confined to smaller subsets of native queries.

## 5. Universal full-span dense-mask invoice obstruction

Consider making all `m+1` nonempty fields productive at all `m` full sites.
The native rank-two active part leaves at least `m-1` idle field copies per
site. Give the proposed rewrite the most favorable possible pooling: ignore all
geometric and commutation restrictions on these idle copies and allow each paid
job rank to be any positive number at most `L=8m`. Total paid rank mass is at
least `L(m-1)`. Since `f(r)/r` is decreasing,

\[
 \sum_{\rm paid} f(r)\ \ge\ (m-1)f(L).
\]

With the original `E` output and three thin rank-one charges retained, the ideal
outer signed gain per port is consequently at most

\[
 G_{\rm dense}=(m+1)f(L+1)-(m-1)f(L)-2.
\]

The exact source outer gain is

\[
G_{\rm source}=f(L+1)+f(8a+1)+f(8b+1)-2
 +\sum_{j=1}^{a-1}\Delta f(8j)+\sum_{j=1}^{b-1}\Delta f(8j),
\]

where `Δf(r)=f(r+1)-f(r)`. There are `m-2` increments in the sums, each at least
`Δf(L)` by concavity. Therefore

\[
\begin{split}
G_{\rm source}-G_{\rm dense}
&\ge f(8a+1)+f(8b+1)+f(L)-2f(L+1)\\
&\ge f(1)+f(L)-f(L+1)\\
&=1-\Delta f(L)>0.
\end{split}
\]

The second inequality follows from `x+y=L+2`, `x,y≥1` and the fact that a
concave sum at fixed total is minimized at an endpoint. This proof works for
**every pair of positive odd arms** and every `0<t<1`, and even relaxes the idle
job ranks to real numbers. Adding `E` to every stage worsens the ideal by another
`1-Δf(L)`.

All native terms are identical before and after the rewrite, so the comparison
is also a complete signed-invoice comparison. For `a=b=9` at the predecessor's
stated `κ=.00337180`, exact interval arithmetic gives a per-port loss exceeding
`0.417979705566714323`, before any additional adapter charge. This is a universal
proof about full-span dense activation, not a finite failed search.

## 6. All 81 central partial-dense masks

Full-span activation need not be optimal. We therefore check a distinct bounded
family on the unchanged `9|9` root. Number full sites `0,...,17`, with the bridge
between `8` and `9`. For each `p∈{0,...,8}` and `q∈{9,...,17}`, replace every
mask at sites `p,...,q` by all 19 nonempty fields; keep all other masks unchanged
and leave `E` inactive. These are exactly 81 cases, without random seeds.

For a subinterval `I=[c,d]`, let `M_I` be its masks' intersection. Let `X_0` be
the column space spanned by the full-query columns in `I` and every coordinate
column outside `M_I`; let `Y_0` be the analogous row space. If `I` crosses the
bridge, close these spaces under it:

\[
 X=X_0+BX_0+B^2X_0,\qquad Y=Y_0+Y_0B+Y_0B^2.
\]

Otherwise set `X=X_0`, `Y=Y_0`. The degree-three bridge polynomial proves this
is the entire cyclic closure. Any legal projector covering `I` annihilates `X`,
and its image lies in `ker Y`. Its image is disjoint from `X`, since it is
idempotent and kills `X`. Hence

\[
 \operatorname{rank}J\le c_I:=n-\operatorname{rank}X-
 \operatorname{rank}Y+\operatorname{rank}(YX).
\]

Here `YX` means the pairing matrix in any bases of the row and column spaces.
The last term is essential: subtracting nullities alone does not account for
the primal/dual pairing. This is a necessary capacity bound, without a claim of
simultaneous attainability.

Let `z_J` be total field rank assigned to packet interval `J`. Packets covering
a common interval are mutually annihilating, so their sum is an idempotent and
the preceding bound applies to the sum. Consequently every legal packet
schedule satisfies

\[
 z_J\ge0,\qquad
 \sum_{J\supseteq I}z_J\le c_I,\qquad
 \sum_{J\ni i}z_J=d_i:=|M_i|-2.
\]

Relax ranks to nonnegative real variables and minimize
`Σ_J z_J f(8|J|)`. This LP is still optimistic: it omits projector realization,
ordinary adapters, and integrality. A lower bound on its paid objective is
therefore valid for the declared physical packet model.

### Exact dual certificate

For interval inequality multipliers `α_I≤0` and site equality multipliers
`β_i` of either sign, it suffices to verify, for each candidate job `J`,

\[
 \sum_{I\subseteq J}\alpha_I+\sum_{i\in J}\beta_i\le f(8|J|).
\]

Then every feasible paid objective is at least `Σα_I c_I+Σβ_i d_i`.
`dual-certificate.json` retains all 81 multiplier vectors as integers divided
by `10^8`. The replay constructs every capacity exactly and checks all
`81×171=13,851` dual-column inequalities using outward **rational** bounds on
`r^(1-κ)`. A floating LP solver was used only to discover candidate dual vectors;
its statuses, objective values, and tolerances are not verification premises.

The complete optimistic gain is bounded above by

\[
18\{\operatorname{moment}({\tt HELPERS})-
       \operatorname{moment}({\tt LOCAL\_PAID})\}
+104\{\operatorname{moment}({\tt targets})-3-
       \operatorname{paidLower}\}.
\]

The fixed profiles are extracted from the retained `pricing.py`. Source helpers,
local paid jobs, target changes, all idle work, and three thin jobs are included.
At the source's stated `κ=.00337180`, every complete upper bound is negative.
The largest of the 81 certified upper bounds, at `[p,q]=[8,9]`, is

\[
 -21065220134325490533/500000000000000000
 = -42.130440268650981066.
\]

Thus this finite family does not even retain the predecessor's stated moment
inequality at that κ. This numerical statement is only at the declared κ;
no unproved monotonicity in κ or general impossibility conclusion is inferred.
The full-span result of Section 5 is separately uniform in κ.

The relaxed model is genuinely larger than pointwise thin annihilation. For
`I=[8,9]` with all 19 nonempty fields available, its whole-bridge capacity is 15,
whereas requiring annihilation of each thin query gives capacity 14. Independent
review derives the capacities from plus/minus eigenspaces rather than this
cyclic-closure implementation and agrees on all 13,851 interval entries.

## 7. An 18-dimensional algebraic quotient and its unresolved stage interface

Put `R=I-P_E-P_v`. All full native queries are supported on the `m`-dimensional
invariant complement `W=im R`. The bridge decomposition gives

\[
 BR=(I-2uw^*)R.
\]

Hence on `W` the complete `m+3`-query root reduces algebraically to the same
`m` full queries with **one** middle rank-one square-zero query. Its endpoint
is `-I_W`. In the full `n`-space, the shortened word has endpoint `I-2R`.
This is a constructive root identity, not an admitted supplier improvement.

For the concrete `9|9` root, let `P_i` be the original full productive coordinate
mask projector and set `Q_i=R P_i R`. Exact computation establishes

- `rank[P_i,R]=2` at all 18 full sites;
- `Q_i` contains the native query: `Q_i(x_i y_i*)=(x_i y_i*)Q_i=x_i y_i*`;
- `rank(Q_i²-Q_i)=1` at all 18 sites;
- `rank[Q_i,Q_j]=2` for all 153 distinct pairs.

The masks therefore do not descend through the original splitting, and their
direct compressions are neither idempotent nor mutually commuting. Ordinary
similarity preserves these defects. The source's productive-target accounting
cannot simply be carried through this compression.

This does **not** rule out other productive projectors or correction terms on
`W`. The independent review supplies an explicit local repair. Define the
original native active rank-two projectors

\[
\begin{split}
\Pi_{L_j}&=(A+2\sum_{k<j}f_k)A^*+f_jf_j^*,\\
\Pi_{R_j}&=(A-2\sum_{k>j}h_k)A^*+h_jh_j^*.
\end{split}
\]

They are idempotent and retain `N_i=x_i y_i*` in both orders. Put
`H_i=R\Pi_iR`. On the declared `9|9` instance the independent exact check gives

\[
H_i^2-H_i=c_iN_i,\quad H_iN_i=N_iH_i=N_i,\quad N_i^2=0,
\]

where `c_{L_j}=(-1)^j` and `c_{R_j}=-(-1)^j` for `j=0,...,8`.
Consequently

\[
\widetilde\Pi_i=H_i-c_iN_i
\]

is idempotent: its square minus itself is
`c_iN_i-2c_iN_i+c_iN_i=0`. All eighteen repaired projectors have rank two and
retain the native query. This is a constructive local stage identity, with
finite exact evidence retained in `review/EXPECTED-GEOMETRY.json`.
The first repaired pair still has a rank-two commutator, so these particular
repairs do not form one common coordinate system of targets.

Joint target geometry and the complete paid invoice remain required. There is
no claim that an arbitrary 18-dimensional root cannot have legal stages. The
mathematical remaining question is a common or otherwise rigorously priced
target representation for the shortened word, including all induced idle work
and any recursive change of representation. See [the independent review](review/REVIEW.md)
for the separate derivation and replay.

## 8. Verification scope and inherited assumptions

`verify.py` is a standard-library exact checker, not a proof assistant. It
verifies retained byte hashes and Git blobs; independent root formulas for 25
finite shapes; the bridge decomposition, closure polynomial and quotient word;
all concrete compressed-stage defects; the fixed complete native invoice;
all 81 dual certificates; and eight failure/contract controls. It compares its
exact report with `EXPECTED.json` and retains checks under `python -O`.

The universal claims in Sections 2–5 are established by the arguments above.
The 81-case certificate establishes the explicitly bounded claim in Section 6.
Neither layer checks or removes `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, or `analytic_recovery`, the framework assumptions
inherited by the multiplication project. Pending source status and selected
frontier status are separate: this package changes neither admission nor the
selected result.
