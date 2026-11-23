# Source-ordered compiler cuts and a smaller interval envelope

This supplement completes the interrupted audit of the exact stored word used
by the direct-circulant precision application. It is a scoped mathematical
interface result, not a complete multiplier or physical-tape theorem. All
norms below are Euclidean operator norms unless stated otherwise.

Canonical source: `e54523517d0f03e58352e647c403a5af3e525a57`,
`research/rational-unitary-fft`. Executable bytes, predecessor notes and their
exact origins are authenticated by `ORIGINS.json`.

## 1. Results, premises and the precise cut boundary

Let `N=2^d`. Retain the source's admission and coefficient construction:

* the exact rational reference matrix and every leading section are admitted
  with component envelopes `lambda,Q >= 1`;
* `chi=lambda*Q`, every ideal completed-atom downset and its inverse have norm
  at most `B=256*N^3*chi^12`;
* the displacement identities, exact generator-rank bound, certified phase
  enclosure and coefficient-defect bounds are those of the pinned source;
* each stored atom differs from its ideal endpoint by at most `eta`, and
  `theta=(3*N-2)*B^2*eta <= 1/4`;
* inversion uses the exact inverse of the same stored gate coefficients.

Put `L0=max(1,lambda,Q)` and retain the literal source fragment constant

```
rank = 2*d+8
alpha = 8*rank*N^2*chi
KG = 2*N+64*N^2*chi
Hgen = max(3200*N^3, 2+2*KG)*(10+4*alpha+2*KG)
U = lambda+lambda^2*Q
H = max(Hgen, U+1, 2*Q)
K = 2*L0*B*H.
```

**Result A.** At a cut after an arbitrary subset of a matching layer in the
actual stored full compiler word, its prefix, suffix, inverse prefix and
inverse suffix all have norm at most `K`. No extra generic interpolation
factor is needed for this particular source hierarchy.

**Result B.** For any two ordered such cuts, the intervening exact stored
operator and its inverse have norm at most

```
S = B^2*H^2/(1-theta) <= (4/3)*B^2*H^2 < 2*B^2*H^2.
```

The convenient rational envelope `2*B^2*H^2` improves the source's generic
`K^2=4*L0^2*B^2*H^2`. It uses a *single consecutive normalized perturbation
product*, not separately bounded approximate endpoints.

A cut is between whole invertible one- or two-wire mathematical gates. It is
not a cut between writing the two outputs of one gate to physical storage.
For example, the swap matrix is unitary, but overwriting its first coordinate
before computing the second can have intermediate map `[[0,1],[0,1]]`, which
is singular. Nothing here supplies an inverse for that intermediate map or
accounts for its saved temporaries.

The ideal downset and coefficient/rank/phase hypotheses retain their original
proof obligations and credit. This supplement proves the source-specific
fragment extension and the relative-interval implication; finite replay is
corroboration and source binding, not a universal proof by exhaustion.

## 2. Every actual primitive fragment has the original cap

The adapted `engine.Builder` obtains exactly two spectral matchings. Each
cross-bank gate is a lower shear on one source/target pair. Every other gate
is supported entirely in one bank and is exactly unitary, including the
rational FFT butterfly and independently prepared twist entries. For a
partial matching, the product of any selected bank-local gates is still
unitary on its own support with identity elsewhere.

Write `S(A)=[[I,0],[A,I]]`. For a bank unitary `V=diag(Vx,Vy)`,

```
V*S(A)*V^-1 = S(Vy*A*Vx^-1).
```

Consider any contiguous primitive gate interval. Move bank unitaries through
shears using this identity. The resulting shear parameter is a sum of at
most two unitary transforms of masked spectral diagonals. Masking a diagonal
cannot increase its norm. The two stored spectral diagonal norms are at most
`Mg+v` and `Mh+v`, so the interval is a bank-unitary product times a shear
whose parameter has norm at most `Mg+Mh+2*v`. Since
`||S(A)||,||S(A)^-1|| <= 1+||A||`, every interval and its inverse satisfy

```
Hprimitive = 1+Mg+Mh+2*v.
```

This proves all four fragment bounds at arbitrary matching subsets with the
original constant. It uses the actual spectral orientation and exact bank
unitarity; it is false for general compensated nonunitary bank changes.
Conjugating just the twiddle of a complex butterfly also does not in general
produce that butterfly's inverse: the full gate order and adjoint are needed.

This is the source-structure route suggested by the open child-fragment
question in Brian/JoyboyBrian's #4755. His #4976 establishes a valid generic
`sqrt(2)` interpolation loss, including sharp examples. We do not claim that
generic result can be improved to one.

## 3. The parity child retains its original cap at matching subsets

The pinned `triangular.Triangle` composes equal-size sibling programs through
`parallel`, and explicitly checks their macro `(start,stop)` partitions agree.
At a given macro fragment, sibling pieces are therefore a direct sum. Each
shear piece is exactly the primitive of Section 2, with the admitted
`Mg+Mh+2*v <= 6`; all its four fragments have norm at most seven. A stored
scalar leaf and its reciprocal have norm at most four; a selected subset of
disjoint leaves has the maximum of its selected scalar norms and one.

For completeness, the retained macro perturbation step is as follows. If
`A_j` are ideal macros, `Q_j=A_j...A_1`, and
`G_j=Q_j^-1*(Ahat_j-A_j)*Q_(j-1)`, then

```
Z_j = Q_j^-1*Qhat_j = (I+G_j)*Z_(j-1).
```

With the source ideal prefix/inverse-prefix bound `Btri=100*m^3` and its
allocated sum of defect bounds at most `1/4`, every consecutive product of
`I+G_j`, and its inverse, has norm less than two. Thus stored completed
prefixes and inverse prefixes have cap `2*Btri`; suffixes and inverse
suffixes have cap `4*Btri`, using the ideal whole endpoint and inverse cap
two. Combining a matching-subset fragment cap seven with those checkpoint
bounds gives at most `28*Btri < 32*Btri = 3200*m^3` in all four cases.

The near-identity admission, ideal macro bound and local coefficient-error
inequalities are retained from Jose Manuel's `TRIANGLE-PROOF.md`; no new
claim about arbitrary matrices satisfying only whole-matrix conditioning is
made. The point proved here is that the actual primitive and scalar pieces
support the same numerical constant at the additional matching-subset cuts.

## 4. The bounded-generator child also retains its cap

One generator term uses the source order

```
P; S(G); P^-1; S(-G),
```

with the same stored `Phat`, its exact stored inverse, and compensation built
by negating the same stored spectral multipliers in their original order.
Let `p=Phat`, `h=Ghat`, `a=alpha+1`, `k=KG+1`. Here `A` is the sum of
stored completed term operators strictly before the current term, and `C`
is the sum of the current term plus all later stored completed term
operators, measured before the current term starts. Thus the full stored
endpoint is `S(A+C)`. The retained construction ensures `||p||<=2`,
`||p^-1||<=4`, `||h||<=k`, and both of these term sums have norm at most `a`.

Writing `L(B,D)=[[B,0],[D,I]]`, the four checkpoint prefixes have forms

```
L(p,A), L(p,A+h*p), S(A+h*p), S(A+h*(p-I)),
```

and the four remaining suffixes have forms

```
L(p^-1,C*p^-1), L(p^-1,C*p^-1-h),
S(C-h*p), S(C-h*(p-I)).
```

Use `L(B,D)^-1=L(B^-1,-D*B^-1)`. Direct substitution bounds every listed
operator and inverse by `4+4*a+2*k = 10+4*alpha+2*KG`. The final checkpoint
uses the bound for a complete term sum. No commutation of `p,h,A,C` is used.

Inside one of the four calls, Section 3 bounds the triangular fragments by
`3200*m^3`; Section 2 bounds a scaled shear and its compensation fragments by
`2+2*KG`. Multiplying one fragment bound and one checkpoint bound proves

```
Hgenerator = max(3200*m^3,2+2*KG)*(10+4*alpha+2*KG)
```

at arbitrary matching subsets. A zero-rank generator emits no layers and is
an identity atom, with no unfinished fragment. The exact generator identity,
the additive endpoint defect, and its preparation/rank admission remain
the credited predecessor results.

## 5. Source-time downsets and the four full-word cuts

Use the source atom DAG: upper shear, both child programs, lower shear; a
leaf is one scalar. Incomparable atoms have disjoint logical intervals,
regardless of physical wire names. Upper atoms finish before descendants
start, and lower atoms start after every descendant finishes.

At a cut in matching layer `k`, before choosing its gate subset, classify

```
I = {atoms with stop <= k}
A = {atoms with start <= k < stop}.
```

The source timestamps include zero-duration identity atoms at their actual
position. Both `I` and `I union A` are downsets; members of `A` are pairwise
incomparable. A fragment may be empty or already contain the whole last
matching layer, which does not invalidate this convention.

For each active atom split its exact stored endpoint as `Ahat_a=T_a*F_a`.
Brian's #4755 trace argument, applied to these actual timestamps and local
plans, gives the exact identities

```
Cprefix = F*Qhat(I),       Csuffix = Rhat*T
Cprefix^-1 = Qhat(I)^-1*F^-1
Csuffix^-1 = T^-1*Rhat^-1,
```

where `F,T` are direct sums of the active prefixes and tails with identity
elsewhere, and `Rhat` is the product of unstarted endpoints. Only disjoint
work moves past an active fragment. In particular `F*Qhat(I)` cannot be
replaced by `Qhat(I)*F`.

Sections 2–4, and the stored scalar margin `|ahat|>=1/(2*Q)`, prove the
direct/inverse cap `H` for `F,T`. The number of active atoms introduces no
factor: a direct sum has the maximum of its blocks' spectral norms.

In a legal atom linearization extending `I`, normalized perturbation gives
completed prefix/inverse-prefix caps `2*B`. Extending `I union A` first
gives remaining endpoint/inverse endpoint caps `2*L0*B`. These are the
predecessor's standard consecutive-product estimates, rederived in Section 6.
Multiplication proves Result A. Unequal sibling durations and simultaneous
nonempty fragments require no aligned full-compiler macro boundaries.

## 6. Nested downsets give the stronger interval bound

Take two source-ordered cuts `u<=v`, with completed sets `Iu,Iv`. Then
`Iu subset Iv`. A finite DAG admits a topological order listing `Iu` first,
then `Iv minus Iu`, then the complement: every predecessor of a member of a
downset is in that downset. Stored endpoints of incomparable atoms commute,
so products computed with this legal order agree with the source products.

Write `Q_j=A_j...A_1`, `Qhat_j=Ahat_j...Ahat_1`. For this single order,

```
G_j = Q_j^-1*(Ahat_j-A_j)*Q_(j-1)
Z_j = Q_j^-1*Qhat_j
Z_j = (I+G_j)*Z_(j-1)
sum_j ||G_j|| <= theta.
```

If `i=|Iu|` and `j=|Iv|`, cancellation gives, in the stated order,

```
W = Z_j*Z_i^-1 = (I+G_j)...(I+G_(i+1))
Qhat_j*Qhat_i^-1 = Q_j*W*Q_i^-1.
```

Let `g_l=||G_l||`. For a consecutive product,

```
||W|| <= product_l(1+g_l) <= 1/(1-sum_l g_l),
||W^-1|| <= product_l(1-g_l)^-1 <= 1/(1-sum_l g_l).
```

The first scalar inequality follows by comparing the finite product's
elementary symmetric sums with the geometric series in `sum g_l`; the
second uses `product(1-g_l)>=1-sum g_l`. Every `g_l<1` because their sum
is at most `theta<=1/4`. The inverse factors are genuine Neumann inverses.
Thus both norms are at most `1/(1-theta)`. Since ideal prefixes correspond
to downsets, `||Q_i^±1||,||Q_j^±1||<=B`, and

```
||Qhat_j*Qhat_i^-1||, ||Qhat_i*Qhat_j^-1||
    <= B^2/(1-theta).
```

Now use the two actual cut factorizations from Section 5. The segment is

```
C(v)*C(u)^-1 = Fv * Qhat(Iv)*Qhat(Iu)^-1 * Fu^-1.
```

The inverse reverses this order. Both boundary fragment factors have norm
at most `H`, proving Result B. No ideal *whole* endpoint enters this
argument. This is why the old extra `L0^2` is unnecessary for relative
intervals. The proof also covers identical completed sets, empty fragments,
zero-duration calls and final/root cuts.

## 7. Consequence for the unchanged direct-circulant word

The parent precision proof already establishes

```
B <= 2^68*t^39, H <= 2^26*t^11, K <= 2^98*t^52
```

for one padded root of width `t>=2`. Therefore the new result gives

```
every original one/two-wire gate and its inverse <= 2^189*t^100,
```

because such a gate is a segment between adjacent source cuts. The prior
application used `K^2 <= 2^196*t^104`. This is an improved sufficient
envelope for the **unchanged stored word**; it does not change coefficient
construction, the source allocator or the operation count. A later selector
revision must propagate this bound through all sixteen-H lowering, routing,
tensor, cache and bootstrap terms and receive its own review.

## 8. Exact finite evidence and failure detection

`audit.py` imports authenticated source *factories* but uses a separate
Gaussian-rational representation, matrix multiplication, elimination,
Hermitian PSD test, predecessor reconstruction and cut oracle. It does not
call the source matrix/inverse helpers to establish the checked identities.
The compiler itself necessarily uses its retained exact arithmetic.

The recovered baseline covers 135 primitive cuts and 540 exact PSD
certificates, plus 882 full-word cuts and 3,528 four-way trace equalities.
The asymmetric size-four word contains a zero-duration upper atom, 50 cuts
with simultaneous nonempty fragments and reversed physical wire order.
The source atom coefficient defects and forward/stored-inverse endpoints
are checked separately. Full-word norm checks use a deliberately conservative
Frobenius consequence and do not infer the universal spectral theorem.

Controls reject a delayed zero-duration predecessor, the wrong prefix order,
a conjugated-twiddle replacement for a complex inverse, a scalar adjoint in
place of its reciprocal, a singular coordinate-write splice, compensated
nonunitary bank changes and generic loss-free matching interpolation.

The source phase and generator/rank semantics are retained dependencies;
the checker is not an independent transcendental oracle, an all-size source
operational semantics proof or a physical bit-cost implementation.

## Open next questions

1. Independently review the numerical child-fragment bridge and the two-cut
   normalized-product identity, particularly inverse order and same-layer cuts.
2. Propagate the new gate envelope through the complete explicit numerical
   selector while retaining every rounding and private native-service premise.
3. Nick Petalas's #4852 and Brian's #4977 supply a smaller ideal downset
   envelope. Can it be applied to this unchanged, already overprecise stored
   word without modifying its allocation or silently changing source pins?
4. Join the exact mathematical cut theorem to actual physical output-write
   temporaries and coded-field movement. This audit does not price those cuts.

## Credit and status

Jose Manuel (`jmbarrancoml`) supplied the rational full/parity/generator
compiler and polynomial precision analysis; Vlado Vojdanovski supplied the
recursive and displacement constructions; Chafik Boukhalfa supplied certified
phases. Brian/JoyboyBrian supplied #4755's source-time trace audit and #4976's
generic matching interpolation; Nick Petalas supplied #4852's block-solve
downset improvement, used by Brian's #4977. Ali Romman supplied the direct
circulant application. Their frozen sources and original notices remain
unchanged. Prepared for Jerry Chen / `@CubeJerry` with substantial OpenAI
assistance. This author-stage audit awaits separate model-assisted review;
neither human review nor formal-kernel acceptance is claimed. All five
canonical assumptions and the selected kappa remain unchanged.
