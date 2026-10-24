# What a border controller does and does not buy

The exact identity in [DISCOVERY.md](DISCOVERY.md) gives a polynomial endpoint
after singular scalar conjugation. It does not give an exact native supplier
at a nonzero evaluation. This note separates two possible conversions and
states the additional hypothesis each needs. Its positive result is a
**finite complex linear-circuit approximation lemma**. It does not close the
recursive physical caller, certify a new kappa, or convert the BIT supplier.

## 1. Exact extraction repeats the paid word

Write the full endpoint, including all independently productive helper
fields, as

```
C(epsilon) = D + epsilon C_1 + ... + epsilon^d C_d.
```

Here `D` is the desired diagonal target operator. The main-field conjugation
is exactly `E(epsilon)^(-1) A E(epsilon)` from DISCOVERY.md, with
`w(X_j)=j`, `w(Y_j)=p-1-j`. It therefore has degree `d=p-1` for `p>=2`.
The helper block is independent of epsilon. The inverse powers in the
conjugation prevent executing the word by substituting epsilon zero.

Over a characteristic-zero field, choose `d+1` distinct nonzero rational
nodes `a_0,...,a_d`. Define

```
lambda_j = product over i != j of (-a_i)/(a_j-a_i).
```

Lagrange interpolation gives the exact operator identity

```
D = sum_j lambda_j C(a_j).
```

This is a construction only when the interface permits copying each original
input to owned fields in the required entry charts and combining returned
fields in their common output charts. Under those explicit assumptions, run
the first `d` evaluations on owned copies and retain their returned values.
Run the final evaluation on the original input owners, multiply those outputs
by its nonzero Lagrange weight, and add the other weighted outputs. Erase
only the owned copies. This schedule never erases an original arbitrary
input owner. Arbitrary-input correctness permits correlations among copies;
it does not create additional productive inputs.

If one evaluation has target inventory `T` and paid inventory `P`, this
construction has the original target inventory `T` and paid inventory
`(d+1)P`, before any extra paid adapters. Its native calls on copied helper
inputs are paid on every evaluation too. There is no credit for `(d+1)`
independent copies of the original helper inputs. Copying, accumulation,
initialization, erasure, node coefficients, coefficient heights and storage
are additional implementation obligations. They are not included in a claim
that only the paid inventory scales by `d+1`.

### The stronger fresh-helper policy

For the present controller the exact full endpoint is block diagonal between
mains and helpers. Helper inputs do not influence main outputs, and each
helper is returned through its own target operator. Thus each evaluation can
instead use a **fresh, independent productive helper inventory**, retaining
all those outputs separately. Only the main inputs are copied and combined.
Writing `K=d+1`, the more favorable inventory is

```
targets = T_main + K T_helper,
paid    = K P.
```

These extra helper inputs must be allocated as distinct original productive
fields, not initialized owned copies of one helper set. The first `K-1`
evaluations use owned copies of the main fields; the final evaluation uses
their original owners as above. All `K` helper inventories keep their
independent input and output ownership. The construction still needs the
copy, combination, chart, storage and physical charges already listed.

This policy is stronger than copying every input and discarding all but one
helper output. For example, the p16 complex border in DISCOVERY.md has main
rank mass 35,840, helper rank mass 62,478 and paid rank mass 97,566. Generic
degree-15 interpolation would give the favorable rank-one masses

```
target = 35,840 + 16 * 62,478 = 1,035,488,
paid   = 16 * 97,566         = 1,561,056.
```

It therefore loses 525,568 units of rank-one mass before any extra charges.

The rejection holds for every `p>=2` in this family. The complex local helper
rank mass is 3,471 and the local paid rank mass is 5,327. The per-port target
formula in DISCOVERY.md and the `p-1` paid queries give

```
T_main(1)   = 2016 p + 3584,
T_helper(1) = 3471 (p+2),
P(1)        = 5439 p + 10542.
```

With `K=p` evaluations, paid mass minus productive mass is therefore

```
p P(1) - T_main(1) - p T_helper(1)
  = 1968 p^2 + 1584 p - 3584.
```

It is 7,456 at `p=2` and strictly increases for integer `p>=2`. For the BIT
formal invoice, local helper mass 3,512 and local paid mass 5,129 similarly
give

```
T_main(1)   = 1776 p + 3108,
T_helper(1) = 3512 (p+2),
P(1)        = 5240 p + 10147,
p P(1) - T_main(1) - p T_helper(1)
             = 1728 p^2 + 1347 p - 3108.
```

The last expression is 6,498 at `p=2` and strictly increases thereafter. BIT
still needs its scalar-extension implementation before this evaluation
policy is available; its idealized invoice already has the displayed loss.
Thus generic direct interpolation with these fresh-helper inventories loses
rank-one mass for every `p>=2`, before extra charges. This rejects this
conversion policy, not every border conversion. New policies with other
retained outputs must state their complete operator and paid inventory.

[BUDGET.md](BUDGET.md) proves the stronger scoped rejection: with these fresh
helper inventories, already `K>=2` complete evaluations lose at every moment
`0<=t<=1`, for every `p>=2`. The rank-one formulas above are transparent
special cases, not the sharpest rejection established in this package.

For a required inverse-transpose orientation, the corresponding border is
`E A^(-T) E^(-1)`, since it is the inverse transpose of
`E^(-1) A E`. The opposite scalar wrappers must be used and the full backward
word, charts and costs must be checked; reusing the forward weights without
transposing their placement is not that orientation.

### A black-box evaluation lower bound

Suppose a procedure must recover the constant coefficient of an **arbitrary**
polynomial of degree at most `d`, using its values at `K` distinct nonzero
nodes. If `K<=d`, the polynomial

```
g(epsilon) = product_(j=1..K) (epsilon-a_j)
```

vanishes at all queried nodes but has `g(0)!=0`. The zero polynomial has the
same evaluation transcript and a different constant coefficient. Thus such
a procedure needs at least `d+1` nodes. The argument also applies to an
adaptive deterministic procedure by taking its nodes on the all-zero
transcript. Multiplying `g` by a fixed nonzero matrix gives the operator-valued
version.

This does not prove that the special controller needs `d+1` evaluations:
additional identities or sparse coefficient support can reduce a particular
problem. It proves that a generic interpolation claim needs a degree or
support bound. Nor does it exclude a non-evaluation exactification method.

## 2. Chronological amplification needs a new degree theorem

The inherited product is a chronological program substitution. In
[`research/higher-moment-strictification/vendor/p7-TENSOR.md`](../higher-moment-strictification/vendor/p7-TENSOR.md),
section 1, copies of one supplier pause at a paid position and the other
supplier completes all current jobs before the parents resume. Its proof
uses exact independent endpoints on the current owners. The statement there
explicitly distinguishes this schedule from tensoring a sum of matrix
operators. The same distinction is retained in
[`research/query-thinned-controllers/PROOF.md`](../query-thinned-controllers/PROOF.md),
section 3.

An ordinary matrix tensor power of a degree-`d` polynomial has degree `vd`.
That observation does not establish a `vd` degree bound for the repository's
chronological supplier product. At nonzero epsilon the border word couples
different productive roles. Those are precisely the endpoints which an exact
child call would have returned separately. A proposed formal substitution
must first check its owner maps, scalar rings, matchers, complete spectators
and every intermediate suspended call.

Even after that semantic construction, positivity of endpoint powers alone
does not bound degree polynomially in substitution depth. Here is an explicit
generic counterexample. Let `N=2^v`, use `N+1` scalar roles, and let `E_(i,j)`
be the matrix unit. Compose the elementary upper triangular maps in order:

```
F_i(epsilon) = I + epsilon E_(i,i+1),       i=1,...,N,
F(epsilon) = F_1(epsilon) ... F_N(epsilon).
```

Each elementary map has diagonal identity, degree one and only positive
off-diagonal epsilon powers. Every intermediate product has the same
properties, apart from its growing degree. The `(1,N+1)` entry of the final
product is exactly `epsilon^N`: the only contributing chain uses all `N`
successive matrix units. Hence the degree is `2^v`. The ordered composition
can be represented by a binary substitution tree of height `v`, with the
children executed serially. Its execution still contains `2^v` elementary
maps; tree height is not execution length.

This example is not a counterexample to the specific native controller or a
claim that its degree must grow exponentially. It refutes the implication
“nonnegative endpoint powers plus substitution depth `v` implies degree
`O(v)`.” A compatible global grading, special coefficient support or another
extraction method remains necessary before claiming polynomial extraction
overhead for the actual product.

In particular, if an exactification of a legal amplified word uses `K_v`
evaluations **and retains only its original productive inventory**, its
paid/target moment ratio before additional charges is

```
K_v * (P_t/T_t)^v,
```

before completion, extra adapters or other charges. Retaining fresh productive
helper outputs changes the denominator and requires a separate inventory,
as in section 1. In either policy, an exponential repetition count cannot
simply be discarded as a polynomial factor. Formal moment advantage alone
does not pay it.

## 3. A sufficient finite complex approximation lemma

Approximation offers a different route over the complex numbers. The
following lemma applies to a **fully flattened finite circuit**, with all
scalar operations and paid calls included. It is a numerical statement;
it assumes no unproved native implementation or cost theorem.

Fix a norm on every intermediate space. Include owned-zero initialization
and the final output projection as linear embeddings/projections of norm at
most one. Suppose the exact circuit endpoint is `C(epsilon)` and, for every
`0<epsilon<=1/2`, the following hold:

1. `C(epsilon)=D+epsilon R(epsilon)` and `||R(epsilon)||<=H`.
2. Every contiguous subword, including prefixes and suffixes, has norm at
   most `H epsilon^(-h)`, where `H>=1` and `h>=0` are fixed.
3. The numerical execution has at most `J>=1` additive error sites. The
   error inserted at each site has norm at most `2^(-P)`.

Site 3 can include input rounding and approximate paid calls. A coefficient
approximation is covered only after its action on the bounded operand has
been shown to meet that additive-error allowance. Merely storing each
coefficient to `P` fractional bits does not establish that premise.

Let requested precision `s>=1` be an integer and assume
`||x||<=2^(b s)` for a fixed `b>=0`. Choose integers

```
k >= max(1, ceil((b+1)s + log2(4H))),
epsilon = 2^(-k),
P >= ceil(s + 2 + log2(JH) + h k).
```

Then the returned numerical value `y` satisfies

```
||y-Dx|| <= 2^(-s-1) < 2^(-s).
```

**Proof.** The exact border error is bounded by

```
||C(epsilon)x-Dx|| <= H 2^(-k) 2^(b s) <= 2^(-s-2).
```

Each local numerical error propagates through a suffix of norm at most
`H 2^(h k)`. Linearity and the triangle inequality therefore give total
rounding error at most

```
J H 2^(h k) 2^(-P) <= 2^(-s-2).
```

Adding the two bounds proves the claim. This propagation uses the exact
linear operators with local numerical discrepancies represented as additive
errors; it does not assume that each gate itself is stable. QED.

The same subword bound gives, at every intermediate cut,

```
||computed state||
  <= H 2^(h k) (2^(b s) + J 2^(-P))
  <= 2 H 2^(h k + b s).
```

For fixed `H,h,J,b`, both the required fractional precision and this magnitude
allowance are `O(s)` bits. If the scalar coefficients of the finite word are
fixed Laurent expressions in epsilon, their exponents are fixed and their
epsilon-dependent dyadic shifts also have `O(s)` length. These are numerical
size bounds, not a proof of the execution time of shifts, scalar arithmetic,
coefficient generation, movement or paid primitives.

The finite constants can be obtained crudely when every primitive is a fixed
Laurent polynomial in epsilon with bounded operator coefficients: expand
each finite contiguous subword, bound its negative exponents, and sum its
coefficient norms. The resulting `h,H` may be enormous. This general
observation alone does not give a uniform all-column bound; the next
subsection supplies one for the raw forward controller under explicit norm
contracts.

### Conditional raw-controller norm bound at every column multiplicity

The following specialization connects the lemma to the changed **raw forward
complex controller**, without asserting an implementation of its paid primitives.
Use the infinity norm on the complete vector of live data and owned fields.
At column multiplicity `f>=1`, assume:

- each completed paid rank-`r` oracle and each rank-`r` Gaussian factor used
  in the endpoint formula, in either required orientation, has operator norm
  at most `2^(r f)`;
- each retained monomial route has norm one;
- the literal scalar word has fixed coefficients independent of `f`, or its
  aggregate scalar norm allowance below is bounded by `S_0+S_1 f`.

These are norm assumptions on completed operations. They do not bound a
paid primitive's internal numerical errors or runtime. Whole-job adapters
which are not unit-norm monomial routes must receive their actual norm
allowance as well.

For each scalar record choose an upper bound `a_j>=1` for its operator norm,
and put `S=sum_j log2(a_j)`. A scalar ADD of coefficient `c` has bound
`1+|c|`; a SCALE has bound `max(1,|c|)`. A COPY which *replaces* its destination,
a clear and a signed swap have norm at most one. If copying is emitted as a
clear followed by ADD, count that ADD with norm two when bounding every
intermediate cut. Its zero-destination invariant alone does not bound errors
inserted between those two records. Integer upper bounds such as
`ceil(log2(a_j))` may be used to compute `S` without transcendental arithmetic.

Let `R=sum_r r P_r` be the raw paid rank mass, with every occurrence counted.
Every contiguous subword of the unwrapped raw word then has norm at most

```
H_0(f) = 2^(R f + S).
```

Indeed, multiply the corresponding record bounds. All bounds are at least
one, so any contiguous subword is bounded by the product for the complete
word. With the p16 complex invoice in DISCOVERY.md, `R=97,566` exactly.
The scalar allowance `S` is finite and computable from the retained literal
coefficient list; no numerical value is claimed here. The predecessor's
`10^9` nonrecursive-record allowance is not by itself a bound on coefficient
heights and is not substituted for `S`.

Now put the contracting wrapper `E(epsilon)` before the raw word and the
expanding wrapper `E(epsilon)^(-1)` after it, acting only on main fields.
The largest weight is `p-1`. Every partial input wrapper has norm at most
one. Every partial output wrapper has norm at most `epsilon^(-(p-1))`:
its individual scalings act on distinct fields, so their combined infinity
norm is their maximum, not their product. Consequently every contiguous
subword of this wrapped circuit has norm at most

```
H_0(f) epsilon^(-(p-1)).
```

The endpoint remainder has a separate bound from the explicit U,V formulas.
Every off-diagonal row has at most `p-1` entries. Each entry is a signed
difference of two products containing at most `p+2` stage factors, each used
at most once, and one central rank-one factor. Noninitial stage factors have
rank eight. The initial factor is `D_0=F_9 Q^(-1)`, as specified in the source
controller proof. Bound it by `2^(10f)` using its rank-nine and rank-one
factors separately; no cancellation or phase normalization is needed for
this conservative estimate. Thus each term has norm at most
`2^([3+8(p+2)] f)`. Dividing the off-diagonal
polynomial by epsilon leaves nonnegative powers whose values are at most one
for `0<epsilon<=1/2`. Therefore

```
||[C(epsilon)-D]/epsilon||
  <= H_1(f) = 2(p-1) * 2^([3+8(p+2)] f).
```

The extra two units are solely a conservative operator-norm allowance. They
do not change the productive or paid rank inventories inherited from the
source native contract.

The independent helper block contributes zero to this difference. The port
copies are block diagonal, so their count does not multiply the infinity
norm. Taking `H_f=max(1,H_0(f),H_1(f))` and `h_f=p-1` proves the two norm
premises of the finite lemma for this raw controller, conditional on the
displayed completed-operation contracts. For each fixed `p`,
`log2(H_f)=O(f)` when `S` is fixed or `O(f)`.

Thus the raw epsilon wrapper does not itself force superlinear precision in
`s+f`. A runtime or native-supplier conclusion still requires the actual
input magnitude, scalar coefficients, numerical paid-oracle error contracts,
number of error sites and physical costs. The backward orientation needs its
own endpoint remainder estimate for the inverse-transpose word. The raw
bound does not transfer `h_f=p-1` unchanged to a chronological amplified or
recursively compiled word; that word needs its own global bound and matching
proof.

### Column multiplicity and recursive use are separate obligations

If column multiplicity is `f`, denote the actual constants by `H_f,h_f,J_f`.
A sufficient precision condition is

```
h_f <= h_0,
log2(H_f) + log2(J_f) = O(s+f),
log2(input norm bound) = O(s+f).
```

Then the same calculation gives precision and magnitude allowances
`O(s+f)`. If the actual caller also guarantees `f=O(s)`, these are `O(s)`.
These uniform bounds are not established for an amplified or recursive
physical caller; the preceding subsection only binds the raw forward word
under its norm contract. In particular, a growing `h_f` can
invalidate the claimed linear precision allowance. A bound on `log J_f`
also does not establish the time needed to execute `J_f` operations.

Any amplification must be flattened first and given one global error budget.
Inflating precision anew at every recursive call does not prove this bound.
The exact same paid calls may occur in the fixed circuit, but their numerical
implementations must support the resulting global magnitude and precision
requests at the claimed physical cost. Existing contracts for a fixed exact
word with fixed coefficients cannot be cited as already covering the new
precision-dependent scalar family.

This lemma supplies no exact linear endpoint at a fixed nonzero epsilon.
Uniform absolute approximation over all unbounded inputs would be impossible
unless `C(epsilon)=D`: scale any input on which their difference is nonzero.
The actual input magnitude contract is therefore essential.

## 4. Why this does not settle BIT

The binary controller's scalar coefficient arithmetic is characteristic two.
Reducing the integral border identity modulo two is valid formal algebra,
but it supplies no Archimedean small parameter or rounding operation. In the
base field, the only nonzero scalar is one, at which the unwanted powers are
not suppressed.

Evaluation in a finite extension, or coefficient storage in a truncated
polynomial ring, changes the representation. An implementation must count
all coefficient coordinates, native calls on those coordinates, scalar
linear maps, copies, storage and the return to ordinary BIT. The copies are
owned data, not extra independent productive inputs. The odd-prime cover of
the rational index charts is a separate interface and does not itself supply
these scalar-value operations.

No lower bound excluding every finite-field exactification is claimed. The
point is that the complex approximation lemma does not provide one.

## Open next questions

The ambitious positive route is a globally budgeted approximate complex
supplier: bind the displayed border to an actual all-column native word,
prove the norm and conditioning bounds for a legally flattened compiler,
then substitute its magnitude, precision and paid-call demands into the
actual recursive physical caller. This could remove the whole-idle endpoint
requirement rather than improve its constants. Success is not established by
the formal moment or by the finite lemma alone.

For an exact supplier, the first unresolved target is a compatible global
grading or extraction method with subexponential overhead under the actual
chronological product. BIT additionally needs an explicit scalar-extension
implementation and its complete return cost. Until those obligations are
closed, this package supplies a border identity and scoped numerical lemma,
not a new admitted supplier or multiplication theorem.

Credit the chronological compiler and product work of Jacob Alan Sussman,
zxv and Cinna Davis, and their retained native, BIT and physical-interface
predecessors. The interpolation identity and finite linear error propagation
are standard tools; their use here identifies the missing conversion contract.
Prepared for Dillon with substantial OpenAI Codex assistance. Apache-2.0.
