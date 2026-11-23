# Binding supplied dyadic arithmetic to the actual external caller

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. This supplements, and does not modify, Nick Petalas's canonical
`integer-rounded-gate` theorem. The source records are in `SOURCES.json`.

## 1. Exact scope and predecessors

Nick Petalas already proves a constant-word shift/add/long-division program
for a four-term rational row with signed B-bit data and C-bit coefficient
numerators/denominators. Its arithmetic width is B+4C+2. Its source fixture
already binds one rational-unitary butterfly to `exact.apply`. We do not claim
either construction or that existing fixture as new. Armin Pourshafeie's
matching-layer semantics and Jose Manuel's rational compiler remain credited
dependencies. Ali Romman's actual external tensor caller has an additional
boundary: each original gate is first lowered to sixteen H operations and
seventeen joined diagonal pairs, and each diagonal is converted to a grid.

This note binds the arithmetic at the latter caller's actual
`Grid.multiply` sites. It supplies a smaller width for that special common
denominator, a constant register schedule, and an exact finite-reference
obstruction. It does not replace the externally lowered word by once-rounded
original gates. Coefficient synthesis, global array movement, native-H private
storage, ownership and reversible restoration remain separate obligations.
All five selected assumptions and the selected kappa remain unchanged.

## 2. Literal caller semantics

Let q=2^P. The source represents a complex value by integer numerators (a,b).
For u=(a,b), v=(c,d), `Grid.multiply` returns

    ((ac-bd+q/2) >> P, (ad+bc+q/2) >> P).                 (1)

Python's signed right shift is floor division by q. Thus (1) rounds each
exact real or imaginary component once to the common grid, with ties toward
positive infinity, including negative halfway values. Its two identity
shortcuts return the same values as (1). Inputs are read before either output
is written. This is the same component rounding rule as `exact.round_q` and
the once-per-output sum in `exact.apply`.

`Grid.word` is a different boundary: it uses Python `round(Fraction)` and
therefore ties to even. At P=2 the exact coefficient 1/8 becomes numerator 0
under `Grid.word`, whereas multiplication of numerators 1 and 2 gives
numerator 1 under (1). The kernel must not replace coefficient conversion.
The supplied rounded coefficient is the input to this arithmetic lemma.

For an original Full gate, expanding its complex rows gives at most four
real rational terms with no increase in component height. A one-wire gate
can be padded by an identity on a zero dummy coordinate. `Full.shear` records
the actual child allocation's coefficient height; `Full.plan` takes the
maximum over its actual atoms, including leaves. This is the correct source
of a declared coefficient bound, not the root allocation's initial scalar
height alone. A concrete two-wire Full fixture below has declared atom
heights 616 for each shear and 240 for each leaf, with actual maximum stored
component height 145. Reusing the initial scalar bound without the post-plan
maximum would miss the stated child contract. The original all-width
rational theorem applies to a Full event when its supplied data and actual
coefficient-height bounds are admitted. This observation does not price its
coefficient preparation or change its event order.

An exact adverse example uses the first two-wire gate emitted by the pinned
`Full.plan` for [[3,1],[1,3]], target precision 1. At external P=2, input
numerators (-1,-1,-1,-1) return the same four numerators under once-rounded
`exact.apply`; the actual sixteen-H lowering with `Grid.word` conversions
returns (0,0,0,0). `check.py` obtains the gate from the source factory. This
small diagnostic proves a semantic distinction; it does not claim failure
at the sufficient production precision.

## 3. Common-denominator arithmetic theorem

Assume B>=2, 1<=P<=B, and all four input numerators lie in
[-2^(B-1),2^(B-1)-1]. There is a supplied-input arithmetic program computing
(1) with every signed arithmetic value fitting

    W = 2B+1.                                             (2)

Put M=2^(B-1). Compute ac, bd, ad, bc by signed shift/add multiplication.
Each exact product has absolute value at most M^2. To multiply x and y,
retain the sign, put T=abs(x), D=abs(y), U=0, and repeatedly add T to U when
D is odd, shift D right, and shift T left only if the remaining D is nonzero.
The loop invariant is the usual partial binary product. When y=0, the loop
does not run: the initialized T=abs(x)<=M fits and U=0 is the product.
When y is nonzero, every T and every U is at most abs(x*y): before a shift,
a remaining nonzero bit of y ensures abs(y)>=the next power of two.
Zero x also causes no exception.
The most-negative B-bit input has positive magnitude M, which fits W.
There are at most B iterations per product.

Each sum or difference of two products has magnitude at most 2M^2. The
positive halfway offset is h=2^(P-1)<=M. Consequently every biased numerator
has absolute value at most 2M^2+M < 4M^2 = 2^(W-1), since M>=2.
The final arithmetic right shift cannot increase absolute value beyond the
signed W-bit interval. This proves (2), including extreme negative inputs,
zero factors, cancellation and signed ties. No denominator products or
general long division are required for this common grid.

The ordinary all-rational theorem can also be applied here: treat a+ib as
the supplied scalar coefficient over q, use state (c,d,0,0), and take C=B+1
in general (q may equal 2^B). At the production binding below P<=B-3, C=B
already suffices, giving its unchanged bound 5B+2. Formula (2) is a
specialization for this caller, not a smaller bound for arbitrary rational
four-term rows and not a minimum-width theorem. The same schedule with only
2B bits fails at a=b=c=d=-M: its imaginary sum is 2M^2, outside that signed
range. This is a control for the schedule, not an optimality claim.

## 4. A fixed local register schedule and its cost

Keep the four supplied B-bit inputs intact. Allocate seven W-bit registers:
two output slots, one accumulator R, the offset h, and multiplication
workspace T,D,U. Compute ac into U and copy to R; compute bd into U and
subtract from R; add h and arithmetic-shift R into the first output slot.
Then compute ad and bc in the same workspace, accumulate their sum, add h,
and shift into the second output slot. Both output values exist before the
caller overwrites either input. Reset the five nonoutput registers to zero.

The simultaneous data storage of this schedule is at most

    4B + 7W bits, plus O(log W) control bits.              (3)

Here coefficient inputs count among the four B-bit values; they are not
free read-only constants. The two output slots are included even while all
inputs remain live. `grid_arithmetic.py` is a separate all-width diagnostic
of this schedule, with each register write checked. It is not a mutation or
guard relaxation of the predecessor. Its Python objects and observer
metadata are not a physical storage proof.

The four multiplication loops use at most 4B iterations in total. A fixed
implementation uses O(B) W-bit shifts, tests, additions and comparisons;
scanning each constant-size local register frame gives O(BW)=O(B^2) local
bit work, including local copies and zeroing. This is an explicit quadratic
cost. No fast-multiplication or native-service price is inferred, and the
outer recurrence is not repriced. Transporting actual array/coefficient
words to this frame is still charged to the caller's missing movement bound.

The literal `product_diagonal` on T records makes at most (d+1)T calls:
there are d-1 initial suffix calls, two calls per record, and at most d-1
suffix rebuilds at each of the T-1 transitions. Thus substituting this
local routine at every such call in at most J stages costs
O(J(d+1)T B^2) bit operations for this arithmetic portion alone. Identity
shortcuts can reduce that count; no saving from them is required. This
explicit charge does not include coefficient construction or transport and
does not establish compatibility with an assumed faster service invoice.

Zeroing here means ordinary destructive overwrite. It does not establish
reversible uncomputation, restoration of a dirty owned region, or erasure
permission in a more restrictive machine model. Those cleanup obligations
remain retained. Statement (3) is a local simultaneous live-value bound,
not a count of every word resident in the surrounding tensor execution.

## 5. All-size supplied-word binding from the frozen precision theorem

Retain exactly the spectral-downset theorem's hypotheses and unchanged
literal caller. With d axes, binary widths ell_i>=1, and L=sum ell_i, set

    E=ceil(257L/2)+1354d,  A=20L+303d,
    J=20000(d+1)(max ell_i+2)^6,
    C0=4J(d+1)^2+d+1,
    P=4p+A+2E+bit_length(C0),   p>=1.

The accepted theorem supplies infinity-norm prefix and interval cap R=M0=2^E,
single exact diagonal scalar bound b_i=2^(302+20ell_i), local defect
epsilon(1+||z||), epsilon=(d+1)^2 2^(-P+A), and at most J stages.
Coefficient errors and private phase synthesis remain paid by that theorem.

Conversion changes a complex scalar by at most 2^-P<=1, so each supplied
table factor has modulus at most b_i+1<=2b_i. Put F_i=2b_i>=2. For any
suffix of k factors the actual rounded product has modulus strictly less
than 2 times their product of F_i. Inductively, the k-1 multiplication
rounding errors, each at most 1, give the product plus the proper suffix
products; division by the full product bounds the added terms by the
geometric sum sum_(j>=1) 2^-j<1. This argument uses upper bounds F_i,
never divides by actual table entries, and permits zero factors. The literal
odometer invariant says a stored suffix is always a product of its current
factors, not a sum of errors from all earlier records. Therefore every
retained suffix and each final diagonal multiplier has modulus <2^(A+1).

The represented data states at external stage boundaries obey ||z||<=R.
For completeness, let Z be the maximum over the finite computed run and
a=J M0 epsilon. Variation of constants and the half-disk input give
Z<=R/2+a(1+Z). The frozen selector gives a<1/4, so
Z<=(R/2+a)/(1-a)<=R for R>=1. This uses a finite maximum and a valid local
defect inequality, not a circular assumed bound on the computed states.
During a simultaneous diagonal's coordinatewise scan, a coordinate is
either its old or new stage value; the same bound applies. Thus all actual
Grid.multiply inputs and outputs, including retained coefficient caches,
fit the common signed width

    B = P + max(A,E) + 3.                                 (4)

Indeed numerator magnitudes are below 2^P times max(2^(A+1),2^E), strictly
below 2^(B-1). P<=B-3. The original rational-row coefficient premise is also
now explicit: for a supplied complex grid scalar use integer numerators
a,b and denominator q=2^P; their component heights are at most C=B.
The fixed local routine (2) consequently covers every actual multiply site
in `product_diagonal`, including its suffix updates and identity shortcuts.
It leaves `Grid.word`, native H, `public`, `public_product`, coefficient
construction, array routing and event ordering unchanged.

For the valid constructor geometry sides=(2,), digit_bits=5, p=30, the frozen
selector gives P=3438, A=323, E=1483. Thus B=4924, W=9849, and (3) is
88639 data bits plus controls for one local frame. This is a sufficient
arithmetic bound, not an observed peak or full multiplier space claim.

## 6. Finite reference obstruction

The predecessor's universal written theorem has all B>=2,C>=1. Its literal
diagnostic API separately requires B<=2048, C<=256, W<=3074. We preserve
these guards byte for byte. In the actual `Multiplier.operand` source at
the valid geometry above, the operand 1 produces numerator

    2^P/(4*2^5) = 2^3431.

A positive numerator of that size requires signed B>=3433. The literal
capped predecessor API cannot admit even this actual caller input, whereas
the universal written theorem and the separately proved program above do
not have that finite cap. The checker invokes the extracted source operand
method with an identity CRT route at this one-axis position and verifies
that rejection leaves the supplied state unchanged. This is a precise
integration limitation of the finite reference, not a counterexample to
Nick Petalas's mathematical theorem.

## 7. Evidence and remaining boundary

The checker authenticates supplied source bytes, executes literal source
ASTs, compares to independent Fraction rounding, checks actual Full.shear
events and actual lowering, and tests the separate fixed-register program.
It includes all signed small inputs, extreme wide inputs, positive and
negative ties, zero coefficients, one-bit underallocation, identity
shortcuts, changed imaginary sign, per-product rounding, coefficient tie
substitution, premature input overwrite, and the capped production call.
Normal and optimized interpreter receipts must agree. Finite checks support
source bindings and reject adverse controls; Sections 3--5 are the all-size
argument. No claim of a complete physical `precision_tape` discharge follows.
