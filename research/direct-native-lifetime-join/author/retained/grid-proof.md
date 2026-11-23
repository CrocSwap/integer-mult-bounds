# Exact output-grid binding for the direct word's native Hadamard calls

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. **Source-bound interface theorem; no new kappa.**

## 1. The boundary being proved

The original direct-circulant caller is Ali Romman's #7849 at
`3615fd982f2f4dc7172bef6f0dc9a4f77d5ab6dd`. The frozen #8093 parent is
`8559a122f55614163c037b3c20a21f449a0531f6`. Its precision theorem bounds the
literal rounded tensor word while treating each `hadamard(data, strides)`
as exact. The literal routine performs sums and differences. The retained
native service promises a normalized layer, evaluated exactly and then
truncated toward zero to its requested grid. Its requested return grid is
different from its private internal grid.

This note proves which requested precision and complete-field conversion
make that latter return equal the former exact operation. It gives a sharp
limitation for a coarser return grid under the stated scaling. It does not
reconstruct the native service or claim its physical realization follows
from the interface proof.

The normalized layer and C/S/b identity are already in canonical
`05-layers.tex`; native common-grid and changing-phase estimates come from
`FRAMES.md`. The new result is their exact external input/output binding to
this caller and its proved computed radius. The parent arithmetic supplement
explicitly excludes this native-H boundary. The original outer note already
says to pay for a unit-disk shift and undo it; that idea, the native
common-grid theorem and O(p) existence are credited, not new claims. Here
the requested return precision is explicit, its final truncation is proved
transparent, the actual returned integer encoding is identified, and a
one-bit-smaller return contract is disproved. We also check that the raised
precision stays within the original direct geometry's asymptotic reserves.

`SOURCE-BYTES.json` pins all retained sources by Git blob and SHA256. The
historical normalized-layer proposition has additional parameter and
geometry hypotheses. This result does not erase them or apply it verbatim
outside its domain. Actual native realization, stock and tariff remain
explicit inherited contracts.

## 2. Complete-field theorem

Let T=2^L, P>=1 and E>=0 be integers. The input is the complete array
`x_j=(a_j+i b_j)/2^P`, 0<=j<T, with integer a_j,b_j and |x_j|<=2^E.
Choose h>=1 distinct actual address bits. Their strides are distinct powers
of two s with 2s<=T. Let A_s replace every paired values (u,v) by
(u+v,u-v), and let A be the product of these h raw layers. Different
selected bits commute and every unselected bit remains a spectator.
Arbitrary values and correlations are permitted throughout the complete
field, including positions called holes by an outer caller.

Put H0_s=A_s/2 and let H0 be their h-fold tensor action. Thus

    H0 = 2^(-h) A.                                      (1)

This is not the unitary matrix A/sqrt(2). The pinned source distinguishes
the normalized H0 from that unitary matrix.

Retain this service contract at requested precision Q: on a complete
Q-grid field of modulus at most one, the native provider computes H0
exactly, then truncates real and imaginary components toward zero to the
Q-grid. It retains the selected stride orientation, absolute phase, full
spectators, ownership and legal geometry. Its private precision, scratch,
all-column realization, stock and physical cost require their own proofs.
Only this functional contract is used in the following implication.

Set

    R = E+1,       Q = P+R+h.                           (2)

Make a private complete field by shifting each supplied integer numerator
left by h and declaring its fractional exponent Q. Its numerical value is

    (2^h a_j+i 2^h b_j)/2^Q = x_j/2^R = z_j.

Hence |z_j|<=1/2, within the unit-disk contract. Equation (1) gives

    H0 z = (A x)/2^(R+h).

Every component of A x is an integer divided by 2^P because A has integral
entries. Therefore H0 z is already on the Q-grid. The final toward-zero
truncation is the identity, including for negative values. If its returned
integer pair is (c_j,d_j), then

    (c_j+i d_j)/2^Q = (A x)_j/2^(R+h),
    (c_j+i d_j)/2^P = (A x)_j.                         (3)

The native returned integers are exactly the required external raw-H
integers. The inverse numerical scaling is the paid format change Q to P;
a second integer shift would be wrong. Input shifts, full-field delivery,
output copying and cleanup are still actual scans. Relabelling a
denominator does not make those scans free.

No new numerical error is introduced. If a different provider returns
approximate H0 values, its error is multiplied by 2^(R+h), so this theorem
does not apply without a separate error budget.

### Sharp requested-grid boundary

For fixed P,E,h and the same R, put real numerator 1 at one selected-bits
basis address and zero elsewhere. Its modulus 2^-P<=2^E meets the domain.
On its spectator fiber H0(x/2^R) has values

    +2^(-P-R-h) or -2^(-P-R-h),

whose reduced dyadic denominator exponent is exactly Q. Returning at Q-1
with componentwise toward-zero truncation makes that nonzero fiber zero.
The normalized entrance itself lies on the Q-1 grid because h>=1, so this
is an admitted input to the coarser service, not an input-format violation.
Subsequent scaling cannot restore it. The same witness works with a
negative numerator or an imaginary numerator. Thus Q is the least
universal integer requested output precision for this radius scaling and
this exact-then-truncate service. This is not a lower bound for arbitrary
algorithms or private storage, and it does not claim the basis state is
reached in a production multiplication. Changing the output contract is
another possible solution.

## 3. Binding to the literal tensor word

For each stride the pinned `hadamard` visits `lo=start,...,start+stride-1`
and `hi=lo+stride`, at starts separated by 2*stride. It reads a,b,c,d
before writing either pair output. It is therefore A_s on both real and
imaginary components. Induction over the actual stride tuple proves A,
including nonconsecutive selected bits. The entire T-record field is needed.

In `TensorWord.__init__`, axis i has side `2^ell_i` and first stride equal
to the product of earlier sides. A stage uses `strides[i] << bit` on
distinct active axes. When its local schedule supplies 0<=bit<ell_i,
these select positions `sum_(j<i) ell_j+bit`. The axis intervals are
disjoint, so the nonempty tuple satisfies the theorem with h its length.
`None` emits an empty tuple and no H call. Width-class packing and route
generation remain responsible for valid local bits; this format lemma
does not validate the complete compiler from a stride list.

Canonical `05-layers.tex` has

    C = ((1+i)/2) I + ((1-i)/2) X,
    S = diag(1,i),              b=(1-i)/2,
    H0 = b S C S.

On h selected bits it uses `b^h S_h C_h S_h`, with scalar
`(-i/2)^floor(h/2) b^(h mod 2)`. These are the exact signs and absolute
phase in (1); equality up to phase is insufficient. The checker exercises
this Gaussian-rational identity and final toward-zero grid conversion
separately from the literal integer `hadamard` routine.

All T records participate. A zero-filled outer hole cannot be omitted:
an intermediate raw H can mix it. The normalized provider's full-array
hypothesis remains. The proof also allows dirty hole values under the
same radius and shape contracts.

## 4. Computed radius and noncircular replacement

The frozen parent arithmetic supplement, Section 5, instantiates the
accepted spectral-downset theorem for the unchanged external chronology:

    E=ceil(257L/2)+1354d,       A0=20L+303d,
    J=20000(d+1)(max ell_i+2)^6,
    C0=4J(d+1)^2+d+1,
    P=4p+A0+2E+bit_length(C0).

It proves ||z||<=2^E for computed states of the unlimited-integer reference
word on represented half-disk inputs. Its finite maximum Z obeys

    Z<=2^E/2+a(1+Z),       a<1/4.

For 2^E>=1, `(2^E/2+a)/(1-a)<=2^E`. This bounds computed states; an ideal
prefix cap alone would not suffice. The cited theorem accounts for
separate diagonal/H stages and coefficient rounding.

First consider that well-defined integer reference execution, with no
arithmetic overflow in `hadamard`. Its radius theorem applies at each H
entry. Replace H calls one at a time by the adapter. Earlier states agree
by induction, so the next H entry inherits the reference radius and is
admitted by (2). Equations (1)--(3) yield precisely the next reference
state. Other instructions are unchanged. This derives equality throughout
without presupposing the replacement execution stays inside its own
capacity. Conjugation in the opposite-sign call preserves radius and grid,
so the same proof applies. No extra analytic error is charged.

## 5. Requested, stored and private widths

Input integers have magnitude at most 2^(P+E). After the h-bit left shift
they have magnitude at most 2^(Q-1); the native disk-interface signed width
Q+2 safely covers both signs. A raw output integer has magnitude at most
2^(P+E+h), so signed width

    W_return=P+E+h+2                                   (4)

suffices without the caller's sharper next-stage bound. In the actual
reference trace its returned data fit the parent's existing
`B=P+max(A0,E)+3` by reference agreement. A larger native frame may not be
silently squeezed into B-bit records before the service returns.

There is a distinct, explicitly conditional internal specialization. If
the retained native common-grid theorem applies to this complete h-bit
invocation, incoming q-grid components strictly below 2^g have

    F_private=q+h, W_private=q+g+2h+3,
    W_temporary=W_private+26.

Our unit-disk entrance permits g=1. With q=Q this gives

    F_private=Q+h,
    W_private=Q+2h+4,
    W_temporary=Q+2h+30=P+E+3h+31.                    (5)

Requested Q, private F_private and stored W_private are different. This
is a specialization of the retained contract, not an independent proof
of its identities, compiler depth, source coefficients or owned storage.

The terminal normalization needs its own argument: `FRAMES.md` states an
additional O(h) boundary allowance and does not itself assert that its C
interior formula covers b^h. Here the credited canonical
`compiled-root-clifford-precision/PROOF.md` numerical-wrapper lemma supplies
an explicit terminal macro at the same F_private. Write k=floor(h/2).
Each entry of the tensor C_h has denominator at most 2^ceil(h/2). For h=2k this follows
from products of (1+i)/2 and (1-i)/2: every product is a Gaussian unit
times 2^-k. For h=2k+1 it is a Gaussian unit times (1+i)/2^(k+1).
This exact entry description includes the entire tensor, its phases and
arbitrary Gaussian q-grid inputs. The output at the completed S C S cut,
represented at F_private=q+h, consequently has both integer components
divisible by 2^k. The initial normalization shift by k is exact.

For odd h the shifted real and imaginary integers have the same parity:
each Gaussian product of (1+i) with an integer complex pair has that
property; addition and fourth-root phases preserve it. The optional final
b therefore uses the complete even numerators (a+b,b-a), then exact division
by two. The phase (-i)^k permutes/signs components. Every division contracts
the complex modulus, and b does too. Its two predivision sums require at
most one additional signed bit, already within the retained +26 allowance.
Thus (5) covers this explicit boundary macro without any extra fractional
bits. `finish_c_endpoint` implements that macro and rejects missing divisor
or parity; an arbitrary private-grid pair is not a legal C endpoint.
This proves a sufficient terminal implementation, not a statement that a
different provider's unspecified normalization uses these exact widths.
The normalization/parity lemma remains credited predecessor work; its
source-specific use here closes the apparent gap in (5).

### The raised precision remains linear on the production geometry

Let ell_i>=1, L=sum ell_i>=1, d<=L, h<=d and max ell_i<=L. Then

    C0 <= 80000(2L)^3(3L)^6+2L < 2^29 L^9.

Since `ceil(log2 L)<=L-1`, it follows that
`bit_length(C0)<=29+9ceil(log2 L)<=29L`. Therefore

    P<=4p+3318L,       E<=1483L,
    Q<=4p+4803L,       W_temporary<=4p+4835L.            (6)

The source production controller has T<=2^(p/6), hence L<=p (the weaker
inequality suffices). Thus Q<=4807p and W_temporary<=4839p, both below
8192p. This is a uniform explicit comparison, not an observed small test.
With `s=ceil(log2(p+2))` and `s_Q=ceil(log2(Q+2))`,

    s_Q<=s+13.                                        (7)

The original `axis_packs` still uses public p. In its eventual nonterminal
range d>s^2, each pack has h<=d/s. The source production widths obey
ell_min>=2^15 s^3 and d<=L/(2^16 s^3). Recompute the native descriptor
using Q, with `G=4s_Q+6` and `K=128G`. Equation (7) gives
G<=62s and K<=7936s. Thus every axis admits the K-bit window, including
its most significant selected bit via the source's offset rule, since
2^15 s^3>7936s for s>=1.

The source gathers at most k=2hK positions, so k<=15872d. Its untouched
suffix condition has the explicit bound

    (k+1)s_Q^2 <= (15872d+1)196s^2
                < 48L/s                               (8)

whenever the production nonempty width rule gives L>=2^16s^3. Indeed
3110912/65536 + 196/65536 <48. Consequently this allowance is below L/4
for s>=192. The additional fixed number of O(kG) reservoirs use an
O(1/s^2) fraction of L; each fixed source constant is absorbed beyond an
effective cutoff. The product-stock logarithms retain
O_F(log(h+1)+h^(1/250)(s_Q)^3+1). Their polylogarithmic small-pack cutoff
and h/16 deferred-phase argument persist because (7) changes only fixed
constants and `5(1-1/250)>3` still holds. Small packs use the existing
sequential tail with its original charged polylogarithmic factor.

This shows that raising the precision in this adapter does not by itself
break the newer direct geometry's eventual width, suffix and stock scale
inequalities. It does not supply the actual native implementation or its
reservoir constants. In particular, the historical theorem restricted to
d=Theta(q^epsilon), fixed epsilon<1, still cannot simply be invoked for
this near-linear geometry. The direct outer construction's separate
geometry/realization argument remains a dependency.

## 6. Complete conversion scans and historical backing

Use a separate complete conversion field while the original caller field
stays owned. Copy/shift all input components, run the native service after
that copy finishes, copy all returned components to the original owner,
then retire the conversion field. No productive input credit is earned
by the correlated copy. The two conversion directions and destructive
retirement cost O(T(B+W_temporary)) bit scans plus metadata of length
O(P+E+h+L), in addition to the provider's native invoice. Fixed-width
padding and bounded shifts are sequential bit scans; there is no
whole-field copy per scalar. Native spectator restoration and internal
frame cleanup remain charged to that provider.

For the full run h<=d, reserve one conversion window with the root maximum
temporary width P+E+3d+31. Reuse the same window serially and erase its
entire reserved interval after each call. Additional historical backing
is O(T(P+E+d)), not a sum of newly located frames per call. Original caller
storage and all native private banks remain additional. On the production
controller these conversion scans are O(Tp) per H call and add O(Tp)
historical backing. The source's polylogarithmic number of calls keeps
the corresponding outer scan factor; this is not a proof of its complete
accelerated tariff or the full multiplication recurrence.

## 7. Evidence, limits and next questions

`check.py` authenticates all retained source bytes, extracts the literal
`hadamard` by AST, and compares its action to a Gaussian-rational C/S/b
normalized-service oracle. It covers signed complex data, nonconsecutive
bits, spectators, dirty positions, both scalar parities and wide shifted
integers. The one-bit-smaller return loses a basis input exactly. Controls
cover wrong phase, final rescaling, stride selection, partial fields and
source corruption. Parameter checks bind the actual P,E formula, Q and
distinct private widths. Normal and optimized receipts must agree. These
finite checks corroborate source binding; Sections 2--6 are the universal
argument.

The result closes the external format/truncation implication for a supplied
normalized native layer. It does not establish native primitive realization,
owned erasure, compiler closure, total precision/tape cost, coefficient
production, CRT/recovery or an unconditional multiplication theorem. All
five canonical assumptions and the selected kappa stay unchanged. Changed
#7981 chronology requires a new applicability check.

The next step is to bind a concrete native provider's actual requested
output parameter, private format and complete geometry to (2) and (5).
Then combine the conversion window with that provider's arena lifetime
proof, accounting for both historical extents. More finite basis tests
would not discharge either obligation.

Credit Ali Romman for the direct caller and mixed-rank frames; Douglas
Colkitt and native-layer contributors for `05-layers.tex`; Ross Richardson
and the fixed-root/common-grid contributors for the Clifford precision
argument; Jose Manuel, Vlado Vojdanovski, Chafik Boukhalfa, Nick Petalas and
Brian/JoyboyBrian for the compiler/numerical lineage; and the preceding
#8093 author/reviewer packages. Model-assisted review is not independent
human or formal-kernel acceptance.
