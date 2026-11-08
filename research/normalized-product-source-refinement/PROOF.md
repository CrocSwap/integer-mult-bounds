# Independent numerical refinement of the retained normalized-product source

Canonical source base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The exact files and Git/SHA256 pins are in SOURCES.json. This is an independent
source audit of the numerical assertion in #3709, used as a premise by #3787.
The classical interval and FFT estimates belong to those predecessors. The
new contribution is the source-derived symbolic certificate and its complete
numerical composition, rather than a new FFT identity or a sampled replay.

## 1. The statement and retained primitive premises

Fix integers A,C>=1, p>=2 and 1<=ell<p. Put r=2^ell, N=2r and m=ell+1.
In particular m<=p; admitting ell=p would change the stated parameter domain.
Every one of the C2^A records contains two complete polynomials of length r,
whose Gaussian p-grid coefficients lie in the closed unit disk. Define Q_p
by componentwise truncation toward zero to that grid. Under the retained
canonical primitive and successful-entry contracts below, the actual pinned
`RingProduct.run` numerically returns exactly

    Q_p(u v / r) in C[X]/(X^r+1)

for every input record, with the original record/coefficient/component order.

The retained premises are explicit:

1. `Count`, its copy/add/subtract/multiply/divide/compare primitives and the
   encoded `indices` and `Counter` loops have their exact nonnegative integer
   meanings. A declared dyadic word is read/written in canonical LSB-first
   order. These are the retained bit primitives, not real-number arithmetic.
2. The unsigned `WordProduct` child returns the exact 2n-bit product of its
   two n-bit operands and has the retained consumed-output/ownership ABI.
   The present certificate checks the actual signed wrapper, complete width
   of its read and sign combination; it does not reprove Karatsuba recursion.
3. The source's successful-entry packet, codec, allocation and ownership
   contracts hold. Every numerical operation sees its live complete operands.
   This package supplies a numerical refinement, not a new tape-cost or
   exceptional-cleanup theorem. Failure inputs need not be restored here.

The source `WordProduct` file is pinned; its primitive theorem remains
credited. No floating-point multiplier, input-dependent lookup or unpriced
numerical oracle is introduced into the retained machine. The independent
checker itself uses symbolic host arithmetic to verify the source; it is not
proposed as the multiplication algorithm or charged to its running time.

This closes the identified numerical implication under those primitive
contracts. It does not discharge the complete selected compiler, ownership,
analytic, physical-dispatch or numerical-storage framework. No new kappa,
no changed selected record and no new asymptotic cost bound are claimed.

## 2. What is mechanical, and what is a written induction

The checker parses authenticated Python ASTs. It never imports the retained
checker or invokes its numerical test oracles. `ast_machine.py` implements a
finite expression/statement vocabulary and rejects unknown syntax, calls,
attributes or branches in each interpreted region. The integer algebra is a
sparse canonical polynomial over distinct opaque atoms. Addition and
multiplication normalize only ring identities; rounding atoms are never
distributed through a sum or product.

Certificate equality of two DAGs is kept separate from a source runtime
predicate. Distinct formal polynomials do not prove unequal runtime values.
Source comparisons, identity, membership, dictionary keys, `bool`, `type`,
`isinstance` and zero tests accept only concrete finite controls or explicitly proved domain
predicates. In particular, a zero test on an arbitrary Taylor term cannot
be resolved merely because its formal atom is not the zero polynomial.
Positive atom premises are declared for each complete magnitude partition;
unresolved symbolic branches reject the certificate.

Its complete symbolic obligations include:

* all signed-helper branches, including zero, equality and both magnitude
  orders, followed by the actual scalar child-result read and sign wrapper;
* the actual DIF, DIT and pointwise numerator/rounding DAGs on arbitrary
  integer inputs and arbitrary formal precision;
* all fifteen product-plan fields and nine twiddle-plan arithmetic fields;
* floor/ceiling division, both signed interval-accumulation directions, both
  padding endpoints and all ordered-interval inward branches;
* all four Taylor phases, both last/nonlast cases, initialization, 2T term
  count, degree update, returned endpoint order and final padding;
* actual stage input/output stream order, two-word Gaussian widths, dyadic
  group-division transitions, every stream/FFT loop bound, FFT length progression,
  matched pointwise records, the complete run composition and integer recovery;
* zero/quarter/generic twiddle indices, the literal lower-pi angle, both
  returned interval pairs, inward shifts, complete component emission and
  both Fourier direction signs, including zero imaginary components.

The unbounded repetitions are handled by the written invariants below. Their
source loop bounds, local bodies, dataflow and arithmetic transitions are
checked; the checker does not automatically prove a general Python while
program correct. Binary shifts/nearest, Machin tail bounds, the reachable
Taylor width guard, source dyadic admission and the FFT index induction are
written mathematical obligations tied to the exact source bytes.

The AST outline checks bind every modeled successful-path body to its actual
parent, loop target, context binding and exit. They reject normal-completion
`for` clauses and preserve the literal success flag that prevents returned
output from being erased. Finding a valid but unreachable subtree is not
enough. These checks intentionally accept only the retained control
structure. This is a source-specific audit, not a general proof kernel. A
semantically equivalent rewrite may require a new certificate. The semantic
mutants exercise the numerical acceptance mechanisms after changing source
text in memory; their rejection does not depend on an earlier file hash.

## 3. Exact signed integers, shifts and final rounding

Every nonnegative integer pair is in one of six disjoint shape classes:
`(0,0)`, `(x,0)`, `(0,x)`, `(x,x)`, `(x+y,x)`, `(x,x+y)`, with x,y>0 where
used. For all four sign pairs the interpreter executes the actual source
`Signed.__init__`, copy, negation, add and difference. Zero normalization is
included. Polynomial equality establishes their signed integer meanings over
all members of these classes, not at a finite list of magnitudes.

The actual `Arithmetic.multiply` sends copies of the two magnitudes and the
declared n to the retained child, doubles the read width to 2n, consumes that
whole returned word and combines signs by inequality. The independent packet
model refuses a different read width or an unconsumed return. For the four
sign cases its numerical value is exactly the signed product. All source
butterfly calls must pass `word_width=Q+3`; this is checked at the DAG edges.

Here are the source-loop refinements used for the shift helpers. If a
canonical magnitude has bits b_i, its value is sum b_i 2^i. `left_shift` first
appends exactly t zeros, then copies every old digit once and normalizes.
After k copied digits its output prefix is the original prefix times 2^t.
Thus its returned magnitude is 2^t x. `right_shift` first advances at most t
digits, stopping advancement once RIGHT is seen, and then copies exactly the
remaining suffix. Its value is floor(x/2^t), including x=0 and t beyond the
original width. Both helpers restore the borrowed input head. Normalization
changes no integer value.

`scaled` and `truncate` execute their actual source wrappers around these
helpers. Retaining the input sign gives respectively 2^t z and trunc_0(z/2^t)
for every signed integer z. Their source caller DAG keeps that final
truncation as one opaque atom. An extra truncation inside a butterfly cannot
be simplified away by the algebra.

For t>=1, `nearest` first performs the same magnitude right shift, examines
the original digit at t-1 and increments the retained magnitude iff that
digit is one. If x=2^t q+d, 0<=d<2^t, the result is
`q+1_{d>=2^(t-1)}`. Restoring the sign is rounding to the nearest integer,
with exact half ties away from zero. The recovery argument below has error
strictly below 1/8, so no tie occurs. This numerical identity, the exact
source index `amount-1` and the source bit-at primitive are not replaced by
an assumed generic floating-point round operation.

## 4. Actual inward twiddle source

The nine symbolically reconstructed fields are

    T=Q+64, J=Q+8, R=Q+ceil(log2 T)+12,
    U=2^R, B=2^Q, shift=R-Q, padding=24T,
    half=L/2, width=Q+2.

The source admission loop works on a copy of L, divides it successively by
two, rejects a nonzero remainder and counts the divisions. For a dyadic
2<=L<=2^Q and Q>=16 it terminates after log2 L divisions without changing
the supplied descriptors. Its optional Machin branch executes exactly when
L/2>2; lengths 2 and 4 use only the exact special values.

For arctan(1/d), d=5 or239, the actual loop starts with d^1 and odd1, then
multiplies the power by d² and increments the odd counter twice. Hence its
j-th denominator is (2j+1)d^(2j+1). The two directions of `interval_sum`
are mechanically checked; negative terms subtract the upper endpoint from
the lower sum and the lower endpoint from the upper sum. The source floor
and ceiling helper is checked from the exact Euclidean quotient/remainder
relation in all zero/nonzero remainder and upward/downward cases. The
arctangent tail and Machin combination use the retained estimates in #3709,
which can be checked independently as follows. Each floor/next-grid interval
has width one ulp. At Q>=16,
`R<=2Q+18<4J+2`, and the alternating omitted term is less than
`5^(-(2J+1))<2^(-(4J+2))<1/U`. Padding each arctangent by one ulp at
both ends therefore encloses it with width at most J+2. The literal Machin
combination `16 atan(1/5)-4 atan(1/239)` gives width at most20(J+2).
The series bounds give `pi>281476/89625>25/8` and `pi<16/5`, while
`20(J+2)/U<=5/1024`. Both pi endpoints consequently satisfy the source's
strict guard3U<lo<=hi<4U. These tail/guard derivations are written proofs;
the arctangent and Machin loops are not automatically interpreted.

For the generic source index 0<k<L/2, `TwiddlePlan.value` computes
`angle=floor(pi_lower*k/(L/2))`; thus angle/U lies in [0,4), with angular
error less than `[20(J+2)+1]/U<20T/U`. This includes the additional floor
ulp: J+2=Q+10 and T=Q+64 leave more than enough slack. The index-zero and quarter-turn branches return exact
`(B,0)` and `(0,B)` before the direction sign. The certificate executes the
actual zero, quarter and generic source branches, including the literal
lower pi endpoint, divisor, Taylor call, both width guards, inward argument
order and shift. It composes only interval contracts established earlier in
the audit; the all-size enclosure/guard proofs remain the written ones here.

The Taylor loop starts lo=hi=U, degree1, four zero signed accumulators and
phase0. At phase0/1 it adds the current interval to the cosine/sine pair;
at phase2/3 it subtracts in interval order. It decrements the remaining
counter once. Unless that was its final term, it replaces the bounds by

    lo'=floor(lo*angle/(U*degree)),
    hi'=ceil (hi*angle/(U*degree)),

increments degree and advances the phase modulo4. Every one of these
symbolic source transitions is checked, for arbitrary lo,hi,angle,degree,R.
The source width guard is a recorded mathematical obligation, not silently
assumed from an arbitrary method name. Its reachable invariant is
`w_j<=16`: starting at w0=0, the first bounds are2,6,10,12, and
`w_(j+1)<=4w_j/(j+1)+2` keeps later widths below16. The numerator bounds
remain ordered because angle>=0 and floor/ceiling divisions have the checked
directions. This proves that the guard is met on every reachable iteration.

There are exactly2T terms, with T terms per component. Beyond these terms,
the alternating magnitudes decrease, so each omitted component is bounded
by `4^(2T)/(2T)! <= (16/T)^T`. Since T>=80 and2T>Q+12, this is less
than2^(-Q-12). The source pads every endpoint by24T ulps and
the certificate reconstructs that actual constant, sign and endpoint order.
In R-grid units the tail is less than2^ceil(log2 T)<=2T; together with the
angular error below20T this is below the24T pad at each endpoint. Each
component's T signed term intervals have total width at most16T ulps, so
padding both endpoints adds48T and gives width at most64T ulps. Thus each
true cosine/sine lies in that interval, including the floor error above.
The complete ordered-interval partition used by `inward` proves that its
selected Q-grid component has the true sign and no larger absolute value.
The error is at most h+64T/U<=65h/64 for h=2^-Q. The complex twiddle error
is therefore <2h and its modulus is <=1.

The source emits exactly L/2 twiddles. Its literal sign branch is checked
for both directions, both signs and zero: `opposite=False` conjugates the
positive-angle sine, whereas `opposite=True` preserves it. Hence the
forward and opposite stages have the required negative and positive roots.

## 5. Actual butterflies and complete stream order

The certificate reconstructs each complete numerator before its one final
truncation. With integer real/imaginary inputs a,b,c,d and twiddle u,v, B=2^Q,
it checks exactly

    DIF: trunc((a+c)/2), trunc((b+d)/2),
         trunc((u(a-c)-v(b-d))/(2B)),
         trunc((v(a-c)+u(b-d))/(2B));
    DIT: trunc((Ba+uc-vd)/(2B)), trunc((Bb+vc+ud)/(2B)),
         trunc((Ba-uc+vd)/(2B)), trunc((Bb-vc-ud)/(2B));
    product: trunc((ac-bd)/B), trunc((ad+bc)/B).

Here each expression is an integer output numerator and trunc means toward
zero. These identities are arbitrary-input polynomial/DAG equalities, not
the outcome of sampling input columns. The source wrapper and the source
stream body are both checked: two words from the buffered first half, two
from the sequential second half and two from the table are consumed once;
the first returned pair goes to top and the second to bottom.

The group-count loop starts groups=N and divisor=L. After j nonterminal
divisions their values are N/2^j and L/2^j. The final divisor1 becomes zero
with remainder1 and exits without another group division. The source's
nonterminal and terminal transfers are separately checked. Thus groups=N/L.
The literal stage copies exactly `2*(L/2)*(Q+2)` bits for its first half,
executes L/2 complete butterflies, appends top before bottom and repeats for
every group of every record. The loop bounds and these concatenations are
part of the source certificate.

The actual FFT driver has m iterations, starts length=N for DIF and2 for
opposite DIT, and executes exactly one correctly signed table/stage per
iteration. Its source length update is respectively division or
multiplication by two. For N=2^m the lengths are therefore N,N/2,...,2 and
2,4,...,N. For the index induction with ideal roots, a length-L DIF stage first produces
`(a_j+a_(j+L/2))/2` and `omega_L^j(a_j-a_(j+L/2))/2`. A normalized
length-L/2 transform on the first block gives the even frequencies of the
normalized length-L transform; the second block gives its odd frequencies.
Induction therefore orders the frequency bits in reverse and gives precisely
`P F_minus/N`, with P the bit-reversal permutation. The opposite DIT is the
reverse sequence of these combinations: at one pair, its positive-root
matrix times the negative-root DIF matrix is I/2. Reversing all m stages
thus gives `F_plus P/N`. It consumes that same bit-reversed frequency order.
The complete pointwise source pairs corresponding
frequency records, so no independent reversal or changed record order is
inserted. This index induction is written; its local read/write bodies and
every controlling source loop bound are mechanically bound.

The source lift inserts Q-p low zeros before each complete p+2-bit signed
word. This changes its integer numerator by2^(Q-p), exactly preserving its
value at precisionQ. It then appends r complete zero Gaussian coefficients.
Hence the length-N input has degree<r and its ordinary product has degree
at most2r-2<N. The source lift and zero-count expressions are checked.

## 6. Precision and exact source recovery

The certified source ProductPlan uses

    s=ceil(log2(12m+2))+3, Q=2p+2m+s.

Since m<=p and p>=2, 16<=Q<=8p. For the upper bound,
`ceil(log2(12p+2))+3<=4p`; it holds at p2 and the exponential comparison
increases faster at the next integer p. Each stage length is at most N=2^m,
so its twiddle admission log2 L<=Q is met.

The exact normalized butterfly with any inward twiddle is nonexpansive in
the maximum complex norm of its two operands and preserves the unit disk.
Component truncation also preserves that disk. Replacing the ideal twiddle
costs <2h and the final component truncation costs <sqrt(2)h, so a stage
adds <4h. Both forward transforms have error <4mh. The product is
1-Lipschitz in each disk operand, and its final truncation adds <2h.
The opposite transform therefore leaves total error <(12m+2)h.

The complete run certificate checks two forward transforms, one pointwise
pass, one opposite transform and recovery in that order. With each transform
normalized by N, the ideal final values are ordinary convolution divided by
N². For original p-grid inputs their coefficients are Gaussian integers
divided by2^(2p)N². Scaling the strict error gives

    error < (12m+2)2^(2p+2m-Q) = (12m+2)2^-s <=1/8.

Thus dividing each Q-grid numerator by2^s and applying the actual `nearest`
recovers the exact ordinary integer coefficient. No ties occur. The source
first recovers and buffers all r lower coefficients. It then recovers the r
upper coefficients, verifies the final degree2r-1 coefficient is zero,
subtracts upper from lower, and only then truncates by2^(p+ell). Its exact
read widths, ordering, subtraction direction, last-coefficient guard and
final shift are in the recovery certificate. Consequently its returned
p-grid numerator is exactly that of Q_p(uv/r) modulo X^r+1.

All coefficients of the normalized negacyclic product remain in the unit
disk, being averages of r signed products of disk elements. The final
p+2-bit format therefore fits. The ordinary integer buffer uses
2p+ell+3 bits, while a coefficient has complex magnitude at most
r2^(2p). Intermediate butterfly magnitudes are O(B), and multiplicands fit
in Q+3 bits. These facts establish the primitive scalar-width precondition
used by the actual signed wrapper. Its integer sums are exact Counts, with
no early fixed-width overflow inserted by the symbolic model.

## 7. Interpretation, controls and limitations

This is an independent source-level numerical review of the retained theorem.
It preserves the exact domain, all exposed primitive contracts and the full
ordinary/negacyclic normalization. No production supplier is executed here.
The all-size conclusion comes from the source-derived local certificates
and the written inductions, not a finite product census. The finite control
partitions are exhaustive partitions of symbolic magnitude/phase/control
domains, not a claim to have enumerated all runtime packet sizes.

The registered source mutants include premature truncations, wrong signs,
wrong returned word width, a wrong padding constant, wrong quotient direction,
wrong FFT group division and stage counts, reversed halves, an omitted
opposite transform, wrong negacyclic subtraction and wrong output scale.
Unknown syntax and an unknown call in an unexecuted exception path are also
rejected in the interpreted vocabulary. The unchanged physical source
checks in #3709 remain credited evidence rather than rerun as a new result.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Credit
Jose Manuel / jmbarrancoml for #3709/#3787, their exact source implementations,
proofs and inherited notices. Credit the classical Karatsuba, radix-two FFT
and directed Machin/Taylor methods and their retained authors. This is not
independent human review or formal-kernel verification. Apache-2.0.
