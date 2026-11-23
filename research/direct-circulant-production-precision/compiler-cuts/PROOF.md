# Source-alphabet bounds at every complete-gate compiler cut

Status: author proof; separate review pending. No new kappa or complete
canonical assumption discharge is claimed.

## 1. Exact claim, novelty and premises

This completes the interrupted audit of the literal rational compiler at
canonical commit `e54523517d0f03e58352e647c403a5af3e525a57`. The immutable
sources and predecessor reports are authenticated in `ORIGINS.json`.

For the actual `engine.Builder` alphabet, the four bounds for prefixes,
suffixes, inverse prefixes and inverse suffixes extend to a cut after **any
subset of the complete one/two-wire gates in one matching layer**, with the
same constants as the complete-layer bounds. For the actual composed
`Triangle`, `Program` and `Full` factories, this preserves respectively

\[
 K_\triangle=3200m^3,\qquad
 K_G=\max(3200m^3,2+2k_G)(10+4\alpha+2k_G),
\]

and the source `Full.allocation` constant

\[
 K_{\rm Full}=2L_0\mathcal B\mathcal H,\quad
 L_0=\max(1,\lambda,Q),\quad
 \mathcal B=256N^3(\lambda Q)^{12}.                 \tag{1}
\]

Here `k_G`, `alpha` and `H` have their existing source definitions, made
explicit below. An arbitrary segment is conservatively bounded by
`K_Full^2`; the numerical conclusion does not include an intermediate
coordinate assignment inside a two-wire gate.

Brian/JoyboyBrian's #4755 supplies the exact source-timed trace identity.
His #4976 proves the sharp generic `sqrt(2)` extension from adjacent
matching-layer bounds and asks whether this particular alphabet avoids
that loss. The answer here is affirmative **for these stated source
envelopes**, by the same-direction two-bank invariant in section 2. It does
not assert zero-loss interpolation for arbitrary adjacent matrices, nor
that a partial cut is bounded by the measured maximum of adjacent cuts.
Jose Manuel/jmbarrancoml supplied the original compiler, allocation,
conditioning estimates and the underlying local bounds. We retain those
credits rather than present the complete compiler as a new construction.

The following source premises are explicit. The complete leading-section
conditioning and component bounds must be valid for the unchanged root.
The exact rank/displacement producer, phase-service certificates and
per-atom operator-error estimates must satisfy their documented contracts.
The data interpretation is the exact stored-coefficient linear program.
The proof supplies the missing fragment extension and verifies its
composition; it does not independently derive the algebraic rank theorem,
certify an analytic mass estimate, price preparation/delivery or identify
online Python arithmetic with a multitape machine.

## 2. The bank-triangular invariant

Use the Euclidean operator norm and order coordinates as the complete source
bank followed by the complete target bank. Every non-crossing elementary
gate in `Builder` is unitary within one bank. The swaps are unitary. A
stored phase has modulus one. Its stored butterfly is

\[
 \begin{pmatrix}a&bw\\b&-aw\end{pmatrix},\qquad
 a,b\in\mathbb Q,\quad a^2+b^2=1,\quad |w|=1,
\]

so its columns are orthonormal. This uses exact rational identities, not
closeness to a unitary gate. The inverse source uses the inverse of the
same stored matrix; conjugating only its twiddle would be incorrect.

Every cross-bank layer is a complete matching of gates

\[
 (x_j,y_j)\longmapsto(x_j,y_j+\ell_j x_j).
\]

Selecting any subset replaces its diagonal multiplier `D` by a diagonal
matrix `D_E` with some entries zero. Hence `||D_E|| <= max_j |ell_j|`.
There are exactly two such layers: cyclic followed by negacyclic. Both
point from the same source bank into the same target bank. The retained
twists and transforms between them act separately within the two banks.

More generally, a word consisting of bank-local unitaries and same-direction
shear matchings has an operator of the form

\[
 A=\begin{pmatrix}U&0\\X&V\end{pmatrix},\qquad U,V\text{ unitary}.
                                                               \tag{2}
\]

Initially `X=0`. A bank-local unitary multiplies `X` by a unitary and
preserves its norm. Left multiplication by a shear `S(D)` changes it to
`X+D U`; consequently each shear contributes at most `||D||`. Induction
gives `||X|| <= sum ||D||`. Moreover

\[
 A^{-1}=\begin{pmatrix}U^{-1}&0\\-V^{-1}XU^{-1}&V^{-1}\end{pmatrix}.
\]

The diagonal blocks of `A` and `A^-1` have norm one, while the off-diagonal
blocks have equal norms. Splitting each matrix into its diagonal and
off-diagonal parts proves

\[
 \|A\|,\|A^{-1}\|\le1+\sum\|D\|.                \tag{3}
\]

A complete-gate cut inside any matching layer is legitimate because the
gates have disjoint supports and commute. A selected subset of a unitary
matching is unitary; a selected subset of a shear matching has the same
orientation and no larger coefficient bound. Apply (2)-(3) directly to
the prefix, suffix, or any chronological interval. Each meets at most the
two original spectral matchings. With the source kernel envelopes `M_g`,
`M_h` and multiplier error `v=2^-S`, all four cut operators obey

\[
 \boxed{1+M_g+M_h+2v.}                            \tag{4}
\]

This is exactly the existing primitive envelope. No interpolation factor
is required. Matrix multiplication order is retained throughout; two
noncommuting transforms on a common bank have not been interchanged.

Both structural premises matter. Compensated nonunitary bank operations can
have arbitrarily large intermediate norms despite an identity endpoint.
Opposite-direction shears with coefficient two have product
`[[5,2],[2,1]]`, whose norm exceeds `1+2+2=5` since its first column has
squared norm 29. Thus the conclusion does not follow just from two
spectral sweeps or an invertible final map.

## 3. Aligned parity-triangular children

We retain the source component-l1 near-identity admission. Its Schur
argument gives ideal completed shears of norm and inverse norm at most
five, middle blocks at most two, and primitive envelopes at most seven.
For a recursive ideal prefix or inverse prefix the recurrence

\[
 B(m)\le\max(7,5B(m/2),70),\qquad B(1)\le2
\]

is bounded by `B=100m^3`. Siblings act on disjoint supports. The source
explicitly checks equal sibling macro-boundary partitions in
`Triangle.parallel`, so there are `q=2 log2(m)+1` aligned macro layers.
The exact ideal endpoint and its inverse have norm at most two.

Let `A_j` be ideal macros, `Ahat_j` their stored counterparts, and let
`||Ahat_j-A_j|| <= epsilon`. Write `Q_j=A_j...A_1`. Put

\[
 G_j=Q_j^{-1}(\widehat A_j-A_j)Q_{j-1},\qquad
 Z_j=Q_j^{-1}\widehat A_j\cdots\widehat A_1.
\]

Then `Z_j=(I+G_j)Z_(j-1)` and `sum ||G_j|| <= theta=q B^2 epsilon <=1/4`
under the source allocation. Every consecutive product `W` of these
factors has both norm and inverse norm at most `(1-theta)^-1<2`:
use `prod(1+a_j)<=1/(1-sum a_j)` and
`prod(1-a_j)>=1-sum a_j`. Completed stored macro prefixes and their
inverses are therefore bounded by `2B`; suffixes and their inverses by
`4B`. In particular, the suffix is `Q_q W Q_j^-1`, where `W` is a single
consecutive product. Bounding two unrelated perturbation products would
lose a gratuitous factor and is not the argument used here.

Inside one active macro, every disjoint primitive child has all four
fragment bounds at most seven by (4). A scalar leaf has stored modulus
between one quarter and three, so its complete or empty fragment and
inverse have norm at most four. Their direct sum contributes the maximum,
including a selection that finishes some scalar gates but not others.
Multiplying one completed-prefix/suffix bound by that maximum gives

\[
 \boxed{K_\triangle=32B=3200m^3}                  \tag{5}
\]

at arbitrary complete-gate subsets. The same statement holds for the
literal stored inverse word by exchanging prefixes with inverse suffixes.
This does not replace inverse macros by independently rounded forward
macros or use an adjoint for a nonunitary scalar.

## 4. Compensated bounded-generator words

Use the source exact generator decomposition and its fixed-scale bounds

\[
 \alpha=2rmB_E,\qquad k_G=2m+16mB_E.
\]

For one term, the exact stored chronology is
`p; S(h); p^-1; S(-h)`. The inverse uses the same stored triangular
transform, and the compensation negates the same stored multipliers while
retaining the original cyclic-then-negacyclic order. The endpoint is
`S(h(p-I))`. It restores the source bank exactly at the algebraic level.
Under the source defect allocation, preceding and remaining sums have
norm at most `a=alpha+1`; `||p||<=2`, `||p^-1||<=4`, `||h||<=k=k_G+1`.

For `L(B,D)=[[B,0],[D,I]]`, the four checkpoint prefixes are

\[
 L(p,A),\quad L(p,A+hp),\quad S(A+hp),\quad S(A+h(p-I)).
\]

If `C` is the sum from the current term onward, their suffixes are

\[
 L(p^{-1},Cp^{-1}),\quad L(p^{-1},Cp^{-1}-h),\quad
 S(C-hp),\quad S(C-h(p-I)).
\]

Use `L(B,D)^-1=L(B^-1,-DB^-1)` and
`||L(B,D)||<=max(||B||,1)+||D||`. All four checkpoint operators and
inverses are bounded by

\[
 C_G=4+4a+2k=10+4\alpha+2k_G.                   \tag{6}
\]

The triangular fragments have cap (5). Scaled positive and compensation
shears have cap `2+2k_G` by (4) and the source scaled-multiplier envelope.
The latter inequality retains its literal allowance: `k_G>=2` and the
source `v<=1/2` give `1+sqrt(2)k_G+2v<=2+2k_G`.
Only one child is active within a generator term. Thus all four
complete-gate fragment bounds are

\[
 \boxed{H_G=\max(3200m^3,2+2k_G)C_G.}           \tag{7}
\]

For rank zero the source emits an empty identity word. For disjoint active
generator words in a parent, their direct sum uses the maximum of (7).
The argument uses completed-sum bounds, rather than multiplying one
shear amplification for every generator term.

## 5. The chronological Full word

Fix a valid unchanged Toeplitz root of dyadic size `N`, with complete leading
section bounds `||T||<=lambda`, `||T[0:b,0:b]^-1||<=Q`, and the source's
stronger component-envelope guards when calling its executable factories.
Write `chi=lambda Q>=1`. We recall the exact downset proof so that the
fragment composition's dependence is explicit.

Every contiguous Schur descendant has norm at most
`U=lambda+lambda^2 Q` and inverse norm at most `Q`. Its scalar unit-LDU
factors have direct norm at most `W=3N chi^2` and inverse norm at most
`V=6N chi^4`. The row/column tails of scalar elimination are bounded by
`UQ<=2chi^2`; the Frobenius estimate gives `W`, and
`u^-1=M^-1 l delta`, `l^-1=delta u M^-1` give `V`. Partial pivot
diagonals and their inverses have norm at most `2chi^2`.

The atom order is upper shear, both disjoint child programs, lower shear;
leaves are scalar pivots. For every ideal completed downset `I`, its product
is `L(I)D(I)U(I)` in that order. `L(I)` is a direct sum of full lower factors
on maximal completed subtrees. If `F` is the partition at the unvisited
upper frontier, `U(I)=U_F^-1 u_root`. These identities follow by tree
induction and never commute overlapping factors. Consequently the product
and inverse product have norm at most

\[
 V(2\chi^2)(VW)=216N^3\chi^{12}<\mathcal B.       \tag{8}
\]

There are `J=3N-2` atoms. With per-atom stored defect at most `eta` and
`theta=J B^2 eta<=1/4`, the normalized-product argument in section 3
applies in **any** topological atom order. Every ideal prefix is a downset,
so (8) controls its factors. Completed stored downsets and inverses have
cap `2B`; a remaining stored suffix after any downset and its inverse have
cap `2L_0 B`. For the suffix, cancellation gives the exact expression
`T W Q_j^-1` with one consecutive normalized factor product `W`.

At a gate cut, use the actual source timestamps: completed atoms satisfy
`stop<=k`, active atoms satisfy `start<=k<stop`, and the rest are unstarted.
Zero-duration identity atoms complete at their actual source time; they
are not delayed to a later display position. Both `I` and `I union A` are
downsets. Active atoms are incomparable and have disjoint supports.

Write each active stored endpoint as `Ahat_a=T_a F_a`. Reorder only gates
on disjoint incomparable atom supports to obtain the predecessor's exact
trace identities

\[
 P=F\widehat Q(I),\quad S=\widehat R T,\quad
 P^{-1}=\widehat Q(I)^{-1}F^{-1},\quad
 S^{-1}=T^{-1}\widehat R^{-1},                  \tag{9}
\]

where `F,T` are direct sums of active fragments/tails and identities,
and `Rhat` is the stored product of unstarted atoms. `Rhat` is bounded
using a legal order `I,A,remaining`; it is not obtained by illegally moving
an overlapping unfinished atom through a completed one.

The complete source rank and displacement contracts give

\[
 r_*=2\log_2N+8,\quad \alpha_*=8r_*N^2\chi,
 \quad k_{G,*}=2N+64N^2\chi,
\]

\[
 H_*=\max(3200N^3,2+2k_{G,*})(10+4\alpha_*+2k_{G,*}),
 \quad\mathcal H=\max(H_*,U+1,2Q).              \tag{10}
\]

Equations (7) and the admitted scalar margin bound every active fragment,
tail and inverse by `H`. A direct sum costs no active-atom multiplicity.
Combining (9)-(10) proves (1) for all four cut operators. This includes
unequal sibling durations, a complete selected last gate of an atom still
classified active, reversed physical labels, and arbitrary subsets of one
global matching layer. For `N=1`, only the admitted scalar atom is present;
the same formula is conservative.

For cuts `a<=b`, the interval is `P_b P_a^-1`, hence has cap `K_Full^2`.
This is the factor relevant to errors injected inside the word. It is not
valid to substitute an endpoint condition number for an interval bound.

## 6. Caller applicability and exact boundary

The local result applies to the same canonical Full word instantiated by
#8093's direct-circulant argument, under its retained phase, rank,
conditioning and per-atom defect contracts. Its source `K<=2^98 t^52`
can therefore be used at arbitrary whole-gate matching subsets without
the additional generic `sqrt(2)` allowance. It does not change that PR's
selector, claim optimal precision, or remove every retained compiler
premise. It supplies a coherent proof-interface supplement to #8093.

#8092 concerns an alternative joint native/compiler construction over
larger fixed finite carriers. It is not the same rounded rational
Toeplitz word. Neither its arithmetic/field claims nor its retained tape,
ownership or analytic obligations are discharged by this lemma. If a
later caller replaces an atomic gate by a recursive service, that
service's internal fragment and inverse bounds must be separately proved;
an identical endpoint is insufficient.

Inside a two-coordinate operation, one output may have been written while
the other still holds its old value. Even a swap has the intermediate
coordinate-splice matrix `[[0,1],[0,1]]`, which is singular. Thus the
inverse-cut statement has no such scope. Extra scratch registers and
physical arithmetic require a different state representation and cost
proof. Reordering disjoint complete gates leaves the layer's rounding
vector unchanged when inputs and coefficients are fixed, but extra
rounding events must be charged separately. No new round-trip theorem,
complete physical tariff or unconditional multiplier follows.

## 7. Executed evidence and open next questions

`audit.py` executes pinned unmodified factories but uses a separately
implemented Gaussian-rational matrix engine, elimination, Hermitian PSD
test, cut classification and atom-owner reconstruction. It covers actual
primitive spectra, every selected matching subset in the bounded fixtures,
noncommuting source prefixes, unequal siblings, zero-duration atoms, and
the normalized suffix cancellation. Finite executions corroborate the
universal proof; they are not its quantifier argument. `EVIDENCE.json`
records exact counts. Normal and optimized runs are reproduced with

```sh
python3 -I -B audit.py
python3 -I -O -B audit.py
```

The copied interrupted receipt predates this proof. A new receipt must be
written by this resumed task before claiming execution, and a separate
review must inspect the frozen proof and the retained source contracts.

Open next questions:

1. Bind one downstream lowered caller's non-coordinate arithmetic states
   to a reversible enlarged-state representation with explicit scratch and
   rounding costs. Begin with the concrete swap splice above; invertibility
   of the original two-wire matrix alone cannot do this.
2. Independently certify the retained all-size phase and rank contracts
   used by the Full admission, without treating finite generator checks as
   universal rank proofs. The present result isolates the source fragment
   premise rather than re-proving every compiler component.
3. For an altered recursive replacement alphabet, establish its own local
   fragment invariant before importing (1). The two-bank same-direction
   structure is the first discriminating condition to check.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit Brian/JoyboyBrian (#4755, #4976), Jose Manuel/jmbarrancoml, Vlado
Vojdanovski (#1673), Chafik Boukhalfa (#628), the retained Stein producer
and interval source authors, and Ali Romman's downstream construction.
This is model-assisted mathematical work, not external human review or a
formal kernel proof of the multiplication theorem.
