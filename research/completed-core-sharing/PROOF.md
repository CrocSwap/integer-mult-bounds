# Completed-core sharing with a resolvable triple partition

This is a conditional finite construction over the PR117 producer at commit
cbb05ce504d571546d9b7794c186a613c659c3bf. It uses the interfaces inherited from
PR104: the arbitrary-dirty carrier compiler, copied rational centers,
translated complex endpoints, paid binary address adapters, and the semantic
precision and fixed-tape recursion theorems. The stopped bit layer, all-size
analytic estimates, eligible-prime/field setup and recovery interfaces remain
inherited. The exact coupled exponent and its strict inequalities are checked
separately by the package verifier. This proof does not claim a dense execution
of every Gaussian transform matrix or an unconditional multiplication theorem.

## 1. The completed-core contract and its PR117 binding

Fix one outer triple label $b$. A logical core acts on data $d$ and all its
original dirty auxiliary values $a$ as

\[
 (d,a)\longmapsto(L_b d,a).
\]

The auxiliary block is the identity on **each original role**, with no
data/auxiliary or cross-auxiliary mixing. No original auxiliary is assumed zero.
Let $M$ be the product of carrier shears, $V$ the source injection, and $J$ the
combined rational side/center readout. The transparent word applies, in order,

\[
 M;\ -J;\ M^{-1};\ V;\ M;\ J;\ M^{-1};\ -V.
\]

Its target increment is
$-JMa+JM(a+Vx)=JMVx$, and its inverse cleanup returns every auxiliary
individually. Thus $JMV=I$ proves the displayed contract for arbitrary
Gaussian-rational dirty inputs, including correlated inputs.

The PR117 producer retains the exact disjoint and intersection-two outputs,
24 disjoint centers $A_i$, and decoder/scatter

\[
 T=\frac1{21}\sum_i A_i,\qquad
 T-\frac12\sum_{i\in S}A_i.
\]

The $A_i$ sum input triples avoiding coordinate $i$. For an input meeting $S$
in $j$ coordinates, this center expression has coefficient $(j-1)/2$.
Adding half the disjoint output and subtracting half the intersection-two
output gives

\[
 \frac{j-1+[j=0]-[j=2]}2=[j=3].
\]

The replay checks these supports over the integers, all carrier matches and
all actual source-to-carrier routing. There are 91770 additions, 8120 roots
and 71185 matched uses, giving

\[
 R=91770+8120-71185=28705.
\]

The upstream frame ledger alone is not a signed scalar replay: its addition
events omit signs, and its center incidence placeholders are not the rational
scatter coefficients. The additional audit explicitly binds every operand
to the DAG, every side root and coefficient to its target, and every center
to its excluded coordinate. It evaluates all source indicators through the
actual carrier gates and verifies every intended readout support. This
establishes $JMV=I$ for the actual scalar word. Four arbitrary-dirty integer
cases in each direction also check the signed word and its literal inverse;
these eight finite tests supplement, rather than replace, the universal
inverse-word argument above.

The physical frame replay checks 778984 events, including 236340 moves, with
no frame violation or reflected continuity break. It verifies the exact paid
histogram, local zero source frames and local full pre-exterior sink frames
for every original auxiliary. Each terminal exterior follows the complete
cleanup word; it is not an internal return edge.

Write $C_U$ for the actual partial complex transform on a nondegenerate binary
address subspace $U$, and $F$ for the full address space. Telescoping the gate
frames gives, before the terminal exterior, dirty residual $C_A$ in stage one,
where $A=\mathbf F_2^{24}\otimes\langle t_b\rangle$. Stage two has source
$C_{A^\perp}$ and pre-exterior sink $C_F$, hence residual

\[
 C_F C_{A^\perp}^{-1}=C_A,\qquad
 A=\langle t_b\rangle\otimes\mathbf F_2^{24}.
\]

The source inverse is essential. Reversing the logical shear does not turn
this auxiliary residual into $C_A^{-1}$. Translated endpoint signs, temporary
center copies and data corrections remain those of the inherited compiler.

## 2. Actual phases and completed-core sharing

In a common Walsh coordinate system,

\[
 C_U=H^{-1}\operatorname{diag}(i^{q_U(x)})H,\qquad
 q_U(x)=\operatorname{wt}(P_Ux)\pmod4.
\]

For orthogonal nondegenerate $U,V$, their projected vectors are orthogonal, so

\[
 \operatorname{wt}(u+v)
 =\operatorname{wt}(u)+\operatorname{wt}(v)
   -2|\operatorname{supp}(u)\cap\operatorname{supp}(v)|
 =\operatorname{wt}(u)+\operatorname{wt}(v)\pmod4.
\]

Consequently $C_UC_V=C_{U\oplus V}$ exactly, including its scalar phase.
The actual weight modulo four matters: a triple line has active phase $-i$.

Partition the 2024 triple labels into the supplied 87 groups $J$, each with
binary Gram matrix $I$. For each stage and group allocate $R$ original dirty
streams, replacing the old role index $(\mathrm{stage},b,u)$ by

\[
 (\mathrm{stage},J,u),\qquad b\in J.
\]

This is a new input allocation, not an aliasing of independent old values.
Different roles within one core and the two stage banks remain distinct.
Keep every original scalar gate, internal transformation, temporary copied
center and data correction. Run the complete cores of each group consecutively,
omitting only their terminal auxiliary exteriors.

Within a stage, distinct outer labels use disjoint data fibres. Their grouping
therefore preserves the data map. Each completed core is block diagonal and
accepts every physical scratch state, including the transformed state left by
earlier cores. No residual is commuted through an internal gate, no clean
scratch is assumed, and no inter-core frame conversion is inserted for free.

After a group, each shared role has residual $C_{G_J}$, where

\[
 G_J=\bigoplus_{b\in J}A_b,\qquad \dim G_J=24|J|.
\]

Apply $C_{G_J^\perp}$ to that role. The total action is exactly $C_F$.
A group of size 24 needs no correction. The argument is a whole-state linear
identity, valid with arbitrary spectators and parallel address columns.
The inherited interstage data macros, rank-one copied endpoint corrections,
data signs and bank normalization are retained.

## 3. The signed 87-group partition and its paid adapters

The explicit packing instantiates Lemmas 2.2 and 2.4 of Xiande Zhang and
Gennian Ge, *Maximal resolvable packings and minimal resolvable coverings of
triples by quadruples*, Journal of Combinatorial Designs 18 (2010), 209-223,
[DOI 10.1002/jcd.20234](https://doi.org/10.1002/jcd.20234);
[primary author copy](https://staff.ustc.edu.cn/~drzhangx/papers/mrpacking.pdf).
The supplied generator implements and exhaustively checks the finite
construction; no external implementation or redistributed paper is needed.

There are 83 full classes, each consisting of six disjoint quadruples.
Replacing each quadruple by its four triple faces gives an orthonormal
24-vector group. The 32 remaining triples lie in four disjoint six-point
sets, choosing one endpoint from each of three fixed pairs in each set.

For the signed variant, fix choices $c,d$ in the latter two pairs and let the
first pair be $\{a,b\}$. Group the two triples $\{a,c,d\},\{b,c,d\}$.
Their orthonormal complement inside that six-point set consists of the other
two tetrahedron faces $\{a,b,c\},\{a,b,d\}$ and the two unused unit coordinates.
Combining corresponding pairs from all four six-point sets yields four groups
of eight triples, each with an explicit 16-vector complement: eight vectors
of weight three and eight unit vectors. This is the accepted signed variant;
it does not use the wholly alternating complements of the disjoint-pair variant.

The phase checker verifies exact coverage, every Gram entry of each completed
24-vector basis, the actual projections and all quadratic phase coefficients
on zero, the coordinate vectors and their pairwise sums (301 points).
These points determine a weight-of-linear-map quadratic modulo four. A direct
phase proof is also available: on one tetrahedron, at input weights
$0,1,2,3,4$, the numbers of odd face parities are $0,3,2,1,4$.
Three times those counts equal the original weight modulo four. Thus every
full group has exactly the full phase, with no leftover linear character.
The partial groups and their complementary faces have the same identity;
the unused units supply their ordinary positive phases.

In the displayed complement basis the operator is eight $C^{-1}$ directions
and eight $C$ directions. With

\[
 C=\frac12\begin{pmatrix}1+i&1-i\\1-i&1+i\end{pmatrix},
 \qquad Z=\operatorname{diag}(1,-1),\qquad C^{-1}=-iZCZ,
\]

one positive width-16 child, paid diagonal $Z$ signs and paid binary orthogonal
basis adapters implement the complement. The scalar $(-i)^8=1$ already before
tensoring with the other 24-dimensional factor. Hence either stage orientation
uses one width-384 child per nonzero complement, with spectators unchanged.
The inherited binary-address compiler pays the adapters and signs as local
work; they are not extra Gaussian children or free tape permutations.

The new outer complements must be distinguished from the producer's 3308
internal alternating rank-two residuals. Their actual four-term Gauss sums
are $+2$ in 1284 cases and $-2$ in 2024 cases. They retain the inherited
general rank-two Gauss normal form, including its binary adapters and unit
phases. They are not replaced by two positive orthonormal directions.
No new odd divisor or recursive rank is introduced by either type of adapter.

## 4. Complete child list and allocation

Let $h=24$, $m=576$, $v=2024$, $N=v^2=4096576$ and $\ell=552$.
The new allocation is

\[
 W=2N+2(87)R=13187822.
\]

The copied-center histogram $H'_r$ replaces 24 rank-24 original transitions
by rank-one transitions and retains every rank-23 copy transform. Its mass is

\[
 \sum_r rH'_r=hR+\ell=689472.
\]

All recursive children are:

| Class | Multiplicity | Width |
|---|---:|---:|
| Shared-role complement | 229640 | 384 |
| Internal copied-center | $2vH'_r$ | $r>0$ |
| Data macro | $2N$ | 529 |
| Data front | $4N$ | 23 |
| Endpoint copy | $N$ | 1 |

The exterior multiplicity is $2R\cdot4$. The $2R\cdot83=4765030$ zero-rank
bridges are omitted. All other child classes are unchanged. Since the groups
cover all $v$ labels, the complete list has

\[
 s=Wm-N+2v\ell=7594323392,\qquad Wm-s=1862080.
\]

The largest child is 529. The finite role map supplies a schedule on $W$
equal-volume streams, so each child has volume fraction $1/W$.
Complete-row padding and depth-first recursion use this new allocation;
the old stream count cannot be used with the new denominator.

## 5. Shared histories, the odd grid and coefficient height

A completed core is Gaussian dyadic: its data action is a framed integer shear
and its dirty block is $C_A$. The local divisor 21 cancels exactly on completion.
Sequentially reused scratch therefore preserves its existing odd-denominator
exponent. The new complement adapters are permutations and unit signs and
introduce no odd denominator or coefficient growth.

There are still the same $2v$ cores and core scalar gates at each node.
The increased PR117 scalar count is retained:

\[
 g_h=592224,\qquad G_0=N+2v(g_h+2h)=2401613632.
\]

The exact common grid $2^{-P}21^{-K}$, with $K=G_0(D+1)$, covers the active
chain of unfinished calls of depth $D$. No child is rounded or re-encoded.
At the outer return the exact full tensor operation on every original role
is Gaussian dyadic, allowing exact odd-grid unscaling.

Binary height and magnitude can accumulate across completed cores. The
semantic bound charges the sum of **all** child widths $sf$, every local
scalar operation and one unfinished child at an intermediate peak. It does
not rely on a path confined to one old scratch bank. The verifier retains
the full unreused PR117 semantic constants and checks local charges,
completed-child induction, odd-grid width and stock reserves for

\[
 (W,s,\text{largest child})=(13187822,7594323392,529).
\]

The new sharing and signed-complement composition introduce no additional
physical premise. The exact recurrence, stopped-bit transfer and coupled
assembly remain separately checked under the inherited analytic, physical,
tape, field/prime and recovery interfaces stated at the start.
