# An absolute-error numerical caller with retained inverse state

This result supplies a complete integer numerical execution of the selected
[PR #6030](https://github.com/CrocSwap/integer-mult-bounds/pull/6030) word and its literal inverse. It also proves error bounds for every
tensor width. It does not supply a physical reversible circuit, a fast recursive
native child, a fixed multitape schedule or a new complete kappa. The selected
frontier and all five framework assumptions remain unchanged.

## Source and contract

The source is the 22,803-event selected word pinned in SOURCES.json. It has
770 public fields, 29 owned labels, 31 INIT/CLEAR lifetimes, 23 COPY events,
18,404 ADDs, 861 SCALEs and 3,453 MOVEs. A field has N=512^f complex coordinates,
where f is a positive integer. The operator at each frame is the tensor power
of its 512-coordinate source frame. This defines the explicit tensor lift of
this fixed word. It does not identify every recursive caller with that lift.

Every stored real and imaginary component is an integer times the same positive
grid spacing h. Public input integers are arbitrary. Each forward rounding
stage receives a new uniform seed, conditional on the entire previous state.
It can use one seed for all coordinates of that stage. The inverse retains and
reuses that stage's seed. No later forward stage can reuse it under this proof.

The source compiler gives a recipe L C_r R for every one of the 2,886 distinct
MOVE edges. The independent coordinate implementation checks all 512 columns
of every recipe: 1,477,632 column comparisons. Both source modules run unchanged
with assertions enabled. The new matrix interpreter uses the same route tables
as the sampler, with exact linear pair arithmetic. Integer range checks keep
all matrix comparisons below the int64 limit. The rank counts for ranks 1
through 8 are 2219, 457, 496, 100, 163, 11, 6 and 1. Their weighted sum is 5952.
The source's last MOVE Boolean is an ownership flag, not an inverse flag.

## Completed numerical primitives and their inverses

The central Gaussian pair is

```text
C = [[1+i, 1-i], [1-i, 1+i]] / 2.
```

For integer Gaussian x,y put s=x+y and d=x-y. If Re(s)+Im(s) is even, let
c=0. Otherwise let c be sign(Re(s)) when Re(s) is odd, and `i*sign(Im(s))`
otherwise. With a fresh fair sign sigma, use

```text
d' = i*(d-sigma*c)+sigma*c,
x' = (s+d')/2,  y' = (s-d')/2.
```

All halves are exact integers. The sum s stays fixed, so the inverse uses
-i in the same formula and the same sign. The mean is the ideal C pair. The
squared error is h^2 when c is nonzero and zero otherwise. Thus one complete
layer of N/2 pairs has conditional mean-zero defect, squared error at most
`N*h^2/2`, and pathwise norm at most `h*sqrt(N/2)`. A common sign for the layer
is sufficient. These pair facts and their construction are prior [PR #6532](https://github.com/CrocSwap/integer-mult-bounds/pull/6532) work.

A rank-r tensor native operator has `r*f` such layers, between its exact tensor
monomials. Use a fresh sign at each layer and reverse layers in the opposite
order for decoding. Conditional zero mean and unitary ideal layers give

```text
E(native output | input) = (L C_r R)^tensor f input,
E(||native defect||^2 | input) <= r*f*N*h^2/2,
||native defect|| <= r*f*h*sqrt(N/2).
```

The stage construction need not attain the least variance of the complete
native operator. [PR #6540](https://github.com/CrocSwap/integer-mult-bounds/pull/6540) gives a different changed-grid interface and sharper
pointwise variance class; its grid and residue contract is not substituted here.

For a scalar q=p/D in lowest terms, D is a power of two in the source. Given a
fresh uniform u in [0,D), round each component v by `floor((p*v+u)/D)`. Integer
q needs no seed and is exact. For noninteger q, each coordinate has the exact
mean `q*v`, variance at most 1/4 and absolute error below one grid unit. Hence a
complete complex field has variance at most `N*h^2/2` and pathwise norm at most
`h*sqrt(2N)`. Dependence between coordinates does not change these bounds.

ADD performs y += `round(q*x)` and preserves x. Its inverse subtracts the same
integer increment from the restored x, with the retained seed. It needs no
residue label. Every noninteger SCALE in this source has p=+1 or p=-1. Store
for each real component the residue `v=(p*x+u)` mod D, using log2(D) bits. From
the rounded y, recover `x=p*(D*y+v-u)`. Integer SCALE factors are signed powers
of two; their inverses divide exactly on the reached image.

COPY has coefficient one. Retain its old destination, then copy the source.
Its inverse checks the copied value and restores the old destination. CLEAR
retains the entire old field, and its inverse restores it. INIT inserts a zero
field; its inverse checks zero and removes that field. Thirty of the 31 ideal
CLEAR inputs are nonzero. This construction does not treat their data as free
clean scratch or prove that the retained values can be erased from outputs.

Reverse all 22,803 instructions. Each step receives the state that its forward
step produced, because later steps have already been reversed. The local
inverse rules therefore recover every public input exactly. This is a bijective
encoding of reached states with a retained record, not a full-state permutation
on identical finite hardware registers. No unpriced dirty compensation follows.

## Exact decoded transfer coefficients

Decode each field by its current unitary frame. Ideal MOVE is then the identity;
ADD, SCALE, COPY and resets act by their displayed scalar word. The source frame
and ownership ledger is checked at every event. Independent forward and
transposed backward sweeps agree on every signed defect coefficient of every
final field. Reverse-cut checks also reconstruct each peak below.

For cut t and field v, let c_j be the signed scalar transfer from a completed
instruction's defect to that field. Retain a defect only for native MOVEs and
noninteger ADD/SCALE instructions. Define

```text
M(t,v)  = sum_native j rank(j)*c_j^2,
S(t,v)  = sum_noninteger scalar j c_j^2,
AM(t,v) = sum_native j rank(j)*abs(c_j),
AS(t,v) = sum_noninteger scalar j abs(c_j).
```

Shared earlier errors must be combined with their signs before squaring.
COPY propagates an existing error; it is not a fresh independent error. CLEAR
kills later transfer but cannot remove an earlier prefix excursion. The exact
maxima of all four scores occur at cut 20644, field 558:

```text
M  = 23423,
S  = 161509/8,
AM = 2957,
AS = 4917/2.
```

Cut numbers count completed source events. The maximum ideal row L1 norm is
850, at cut 20479, field 558. Every ideal final row has the source's required
identity or identity-plus-productive-input form. RESULT.json records all 799
final scores, coefficient digests, peak checks and ideal CLEAR inputs.

## All-width absolute error bounds

Let e(t,v) be the difference from the ideal execution with the same input.
All ideal charts and transfer coefficients are deterministic. At each native
microstage, the later ideal stages form a deterministic unitary map. Fresh
conditional zero mean makes distinct microstage and scalar defects orthogonal
in expectation, even when their inputs depend on earlier rounded values.
For every field at every cut,

```text
E||e(t,v)||^2 <= (N*h^2/2) * (23423*f + 161509/8),
||e(t,v)|| <= h*sqrt(N/2) * (2957*f + 4917)  for every seed stream.
```

There is no division by the input norm and no small relative-error premise.
The bound is valid for every input size. It also holds at zero input; in that
case this specific program in fact remains exactly zero.

For a Hilbert-space martingale with increments bounded by deterministic b_j,
its sum S satisfies `Pr(||S||>=R) <= 2*exp(-R^2/(2*sum b_j^2))`. For completeness,
put a=||x|| and d=Re<x,z>/a, with ||z||<=b. The increasing convex function
`cosh(lambda*sqrt(s))` lies below its secant on [(a-b)^2,(a+b)^2]. Therefore

```text
cosh(lambda*||x+z||)
 <= cosh(lambda*a)*cosh(lambda*b)
    + (d/b)*sinh(lambda*a)*sinh(lambda*b).
```

Conditional zero mean removes the second term. The zero-a or zero-b cases
follow directly. Iterate, use cosh(x)<=exp(x^2/2), and apply Markov's inequality
with lambda=R/sum(b_j^2). This proves the stated bound. Zero total increment
bound gives zero error separately. This classical argument is also retained
in [PR #6526](https://github.com/CrocSwap/integer-mult-bounds/pull/6526); no new concentration inequality is claimed.

For a fixed cut, each native microstage contributes a squared bound
`c_j^2*N*h^2/2`. Each noninteger scalar contributes at most `4*c_j^2*N*h^2/2`.
Only one field changes at each source event. A union over the 22,803 event
destinations covers all fields at all prefixes, including fields later cleared.
For every epsilon>0,

```text
Pr(max_all_fields_and_prefixes ||e|| >= epsilon)
 <= 45606 * exp(-epsilon^2 / (N*h^2*(23423*f + 161509/2))).
```

Unlike a relative contract, these deterministic absolute bounds require no
feedback stopping argument. Scalar and native coordinate correlations are
allowed; fresh forward randomness remains a necessary premise.

At f=1, `h=epsilon*2^-12` makes every individual RMS error below epsilon.
With `h=epsilon*2^-16` the simultaneous failure probability is below 2^-40.
These are different guarantees, not least physical precisions or a direct
comparison with [PR #6526](https://github.com/CrocSwap/integer-mult-bounds/pull/6526)'s input-relative guards. The rational certificate proves
an even weaker exponent 8388608/208355 sufficient: the first 65 positive terms
of its exponential already exceed `45606*2^40`. The actual width-one binary-grid
exponent at 16 bits is twice that value.

For a simple all-width rule, let b be the least nonnegative integer with
4^b>=f. Since f>=1, each displayed squared bound is at most f times its
width-one value. It suffices to choose

```text
h = epsilon * 2^(-ceil(9*f/2)-8-b)  for individual RMS error,
h = epsilon * 2^(-ceil(9*f/2)-11-b) for simultaneous failure below 2^-40.
```

The direct width-one RMS check improves the first sufficient rule by one bit.
No probability statement is inferred from the deterministic test seed stream.

## Complete direct work and retained-state bill

The literal reference uses ordinary integer operations and indexed storage.
A forward run uses `2976*f*N` rounded pair butterflies and 6906 tensor monomial
coordinate passes. A route pass reads f address digits per coordinate. The
inverse pays the same counts. Each pair uses at most 13 real additions or
subtractions, four exact halves and three sign changes, plus parity, bounds
and control checks. Each monomial applies at most two payload sign changes
per coordinate. There is no free native query or free Gaussian tensor power.

The 18,404 ADDs and 861 SCALEs each evaluate two scalar components per
coordinate. ADD also pays two destination additions per coordinate. Reverse
ADD repeats its quantizer and subtracts. Reverse SCALE reads its residue or
performs an exact signed power-of-two division. The coefficients have absolute
numerators at most 16 and denominators at most 16, so their ordinary integer
work is linear in the signed payload width. Packing, reads, writes, domain
checks and buffer initialization are included, not treated as zero work.

The exact retained budget for this uncompressed schedule is

```text
fresh retained seed bits       = 5952*f + 18592,
division residue bits          = 578*N,
retained old whole-field values = 23 COPY + 31 CLEAR = 54 fields,
peak live plus retained values  = 824 fields.
```

At width one these are 24,544 seed bits and 295,936 residue bits. The forward
schedule allocates 31 zero fields and copies 23 destinations. Reverse traversal
releases the corresponding values after use. These are upper bounds for this
specific record format, not joint information minima or clean hardware costs.
The checker also keeps copies of all 770 initial fields and all 770 output
fields to compare its inverse. Those verification copies are additional
storage and field-copy work; they are not included in the 824-field schedule.

The two monomial routes for each distinct edge store 512 nine-bit destinations
and 512 two-bit phases each: 32,507,904 logical table bits for all 2,886 edges,
plus the small source recipes and rank/frame tables. The compiler and table
setup are finite costs. The dense all-column comparison is verification work,
not a hidden zero-cost runtime primitive.

For input components of magnitude below 2^w, w>=1, the ideal field norm is
at most `850*sqrt(2*N)*2^w`. The pathwise bound above bounds the additional error.
A sufficient signed stored-component width is

```text
W = w + ceil(9*f/2) + ceil(log2(1700+2957*f+4917)) + 2.
```

Six more bits suffice for displayed pair/scalar temporary arithmetic. This is
a sufficient width, not an optimum. The reference uses `O(f*N*W)` indexed bit
work per full forward/inverse word, with the fixed event counts above; address
arithmetic also costs O(f) bits and is covered since W>=f. Its data storage is
`O(N*W)`, with all field/verification-copy constants stated above, plus residues,
seeds and fixed route tables. A physical sampler, reversible gate lowering,
fixed tape routing, retained-data cleanup, accelerated recursive child costs,
outer error recovery and independent proof acceptance remain open. The direct
`O(f*N*W)` evaluation is not priced as the selected fast recursive supplier.

## Verification and limits

The registered normal and optimized commands regenerate every source recipe
and compare every matrix column. Source assertions stay enabled in a normal
subprocess. Both exact transfer sweeps and all reverse peak checks run.
Local finite checks enumerate pair inputs, every seed for all source scalar
coefficients, signed division residues and a complete mixed stochastic
trajectory. A 262,144-coordinate rank-eight tensor round trip exercises all
16 active layers. A separate exact-grid tensor input is seed independent and
agrees on all 262,144 coordinates with the source oracle. A dense width-one
run executes and reverses the complete
source word. A separate source-coordinate decoder checks all 770 final fields.
Semantic controls retain lost-residue, wrong-seed, reused-seed, signed-COPY,
CLEAR-prefix, global-phase and conjugation failures. Source byte changes are
rejected. RESULT.json gives the exact counts and hashes.

These checks and the written proof establish the stated numerical contract.
They do not constitute an independent human review, proof-kernel acceptance,
a full predecessor scientific replay, a selected cold replay, or any of the
five complete framework assumption discharges.
