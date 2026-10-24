# Streaming norm-six features without a transform table

Krzysztof Wojt, with substantial OpenAI Codex assistance and bounded Luna
support. Apache-2.0. This is a scoped algebraic proof, not a physical supplier
or a new multiplication exponent.

## Premises and new statement

Let `G` be the exact integral Gram matrix supplied by Cinna Davis's #2222,
retained at `research/norm6-dyadic-decoder/sources/P48p-GRAM.json`. Its dimension
is `d=48`. Positive definiteness, the norm-six lattice interpretation and the
49-bit norm-one chart are cited geometric premises. They are not re-audited.
Put `q(x)=x^T G x` and `D=Z[1/2]`. The predecessor's kernel is

```
K(x,y) = ((x^T G y)^3 - 4*x^T G y)/192,   q(x)=q(y)=6.
```

Nick Petalas's #5084 already proves that at most 19,600 dyadic factor pairs
exist, by applying David Ganz / Dugongue's integer-column rank factorization
to the entire finite kernel matrix. Concurrent JoyboyBrian #5132, head
`08572fdb060e73ecc4cb09a024611039881185f4`, independently makes that result
constructive with a sparse transform descriptor and target accumulator array.
It is credited for the public constructibility result; we do not claim another
first closure of that gap.

The new statement is a different evaluation contract: emit all feature pairs
in one pass with only four length-d owned vectors, no per-feature transform
table and no target accumulator array. Including both borrowed input vectors
and 32 scalar/counter/record slots gives `6d+32=320` live integer slots,
in addition to the `d^2=2304` immutable Gram entries. Outputs must be consumed
and released one at a time. The proof below derives a two-coordinate pivot,
local coefficient formulas, their complete preprocessing bounds and the
stream contract. Source features remain integral; streamed target coefficients
have common denominator 256. The 19,600-term and 960,400 algebraic support
bounds are inherited, not newly improved values.

## The integer-valued feature module

Set `f(u)=(u^3-u)/3`, an integer for every integer `u`. Write `v=Gy`. Use the
following #2222 feature pairs `phi_j(x), psi_j(v)` in this order:

| Kind | Source phi | Integral target psi | Count |
|---|---|---|---:|
| f | f(x_i) | v_i^3 | d |
| l | x_i | (v_i^3-4v_i)/3 | d |
| s | x_i^2 x_j, i != j | v_i^2 v_j | d(d-1) |
| t | x_i x_j x_k, i < j < k | 2v_i v_j v_k | C(d,3) |

These are linearly independent polynomials over Q: their cubic leading
monomials are distinct, followed by the independent linear features. Their
formal D-span is therefore free. The cited multinomial identity is

```
sum_j phi_j(x) psi_j(v) = ((x dot v)^3 - 4*x dot v)/3.
```

The total feature count is `N0=C(d+2,3)+d=19648`. Divisions by three define
integer-valued coefficient preprocessing, as in #2222; they are not authorized
dyadic scalar gates on arbitrary runtime data.

For each coordinate define the relation polynomial

```
r_i(x) = x_i (q(x)-6)/2 = sum_j R[i,j] phi_j(x).
```

Even diagonal entries of G make every R entry integral. With `h_i=G[i,i]/2`,
the nonzero candidates in row i are exactly

```
R[i,f_i]       = 3 h_i,
R[i,l_i]       = h_i-3,
R[i,s_(j,i)]   = h_j                     (j != i),
R[i,s_(i,j)]   = G[i,j]                  (j != i),
R[i,t_{i,j,k}] = G[j,k]                  (i,j,k distinct).
```

Here a t subscript is sorted. In particular the leading square term satisfies
`h_i*x_i^3 = 3h_i*f(x_i)+h_i*x_i`; dropping that linear correction would give
the wrong relation. Every `r_i` vanishes on `q(x)=6`.

## A dyadic-unit minor

Use zero-based indices `a=0`, `b=4`. The pinned matrix has

```
G[{a,b},{a,b}] = [[6,-1],[-1,6]].
```

Remove the two s features `x_a^2*x_b`, `x_b^2*x_a`, and all `d-2` t features
`x_a*x_b*x_i` for `i` outside `{a,b}`. Call their index set P and all retained
indices F. Order the relation rows `a,b,other i`, and the pivot columns as
those two s features followed by the t features. Direct substitution gives

```
R_P = [ B  T ],       B = [-1  3],       T[:,i] = [G[i,b]],
      [ 0 -I ]           [ 3 -1]                  [G[i,a]]

B^-1 = (1/8) [1 3; 3 1].
```

Thus `det(R_P)=(-8)*(-1)^(d-2)`, exactly `-8` for d=48. This is a unit in D.
All 48 relations are independent and generate a direct summand of the formal
D-feature module: projection to the pivot coordinates restricts to the
invertible map R_P on their row span. In particular the relation submodule
is saturated over D. No full-shell matrix rank computation or unproved odd
pivot inversion is used.

The shell relation gives

```
phi_P = -R_P^-1 R_F phi_F,
K(x,y) = (1/64) sum_(j in F) phi_j(x) (psi_j(v) - (R^T lambda)_j),
lambda = R_P^-T psi_P(v).
```

There are `N0-d=C(d+2,3)=19600` retained feature slots. Some coefficients or
features may vanish on particular points; exact full-shell rank and term
minimality are not asserted.

## Explicit coefficients and the off-shell identity

For an arbitrary integral vector v, the above solve is the following formula:

```
mu_a = v_a^2*v_b + 3*v_b^2*v_a,
mu_b = 3*v_a^2*v_b + v_b^2*v_a,
mu_i = G[i,b]*mu_a + G[i,a]*mu_b - 16*v_a*v_b*v_i  (i != a,b),
c_j  = 8*psi_j(v) - sum_i R[i,j]*mu_i.
```

Here `mu=8*lambda` is integral. Each pivot c_j is identically zero. Every
retained pair is **phi_j(x), c_j(Gy)/512**, and all runtime coefficients are
dyadic. The exact identity, valid even off the shell, is

```
sum_j phi_j(x)*c_j(v)/512
  = ((x dot v)^3 - 4*x dot v)/192
      - (mu dot x)*(q(x)-6)/1024.
```

It follows by subtracting `(1/512) sum_i mu_i*r_i` from the uncompressed
identity. This proves the desired kernel for every integral norm-six source
x and every integral target y, without enumerating either set. Both x and y
must have norm six for the uniform bounds in the next section. Changing the
shell condition changes the displayed defect; it cannot simply be omitted.

## Coefficient and source-value bounds

The actual pinned Gram has `6 <= G[i,i] <= 10` and `|G[i,j]| <= 5` off the
diagonal. Every R column has at most three entries and l1 norm at most 15:
the f bound is 15, l bound 2, s bound 10, and t bound 15.

Put `M=max(1,max_i |v_i|)`. Every original target has magnitude at most
`2 M^3`, including `|(v_i^3-4v_i)/3| <= (M^3+4M)/3 <= 2M^3`.
The explicit formulas give

```
|mu_a|, |mu_b| <= 4 M^3,
|mu_i| <= 5*4 M^3 + 5*4 M^3 + 16 M^3 = 56 M^3,
|c_j| <= 8*2 M^3 + 15*56 M^3 = 856 M^3.
```

For a norm-six target y, Cauchy-Schwarz in the positive definite G inner
product gives `|v_i|^2=|<e_i,y>_G|^2 <= 6G[i,i] <= 60`. Since v_i is integral,
`M <= 7`. Consequently

```
|c_j| <= 856*7^3 = 293608 < 2^19,
|c_j/512| <= 36701/64 < 574.
```

This is a uniform bound over the entire shell, not a maximum found among
sampled vectors. Denominator 512 is a common upper bound, not a sharpness claim.

For source coordinates the dual Cauchy-Schwarz bound is
`|x_i|^2 <= 6*(G^-1)[i,i]`. The verifier computes G^-1 over Q and checks all
2,304 entries of `G G^-1=I` by exact multiplication. Its generated receipt
records `Dmax=max_i (G^-1)[i,i]=172` and `X=floor(sqrt(6Dmax))=32`. Therefore every
retained source feature is integral and has magnitude at most `X^3`: this
is immediate for linear/mixed cubic features and follows from
`|f(u)| <= (|u|^3+|u|)/3 <= X^3` when `|u| <= X` and `X>=1`.
In particular their magnitude is at most 32,768. Positive definiteness is the
cited premise behind both Cauchy-Schwarz uses.

## Reference preprocessing bound

These counts concern integer arithmetic to compute label-dependent constants.
They are not ADD counts, bit complexity or a paid fixed-tape implementation.
Integers are exact, and each exact division by three is separately charged.

For one source, precompute d squares and d cubes; form all retained s features
with one more multiplication each and all retained t features with two each.
Compute the d f values with one subtraction and one exact division by three.
The total is

```
d(d-1)+2*C(d,3)+2 multiplications,
d subtractions and d exact divisions by three.
```

For one target, first compute `v=Gy` using at most d^2 multiplications and
d(d-1) additions. Compute all N0 original targets using at most four
multiplications and two additions per feature, and d exact divisions by
three. Reuse the two pivot s targets and the d-2 pivot t targets to compute
mu: at most `3d-4` multiplications and `2d-2` additions. For each of the
`N=C(d+2,3)` retained columns, forming `8*psi_j - sum_i R[i,j]*mu_i` uses at
most four multiplications and three additions. Encode the denominator 512
once. Thus a simple evaluator has the conservative upper bounds

```
target multiplications <= d^2 + 8N + 7d - 4,
target additions       <= d^2 + 5N + 3d - 2,
target exact divisions by three = d.
```

At d=48 these are 36,850 source multiplications and 48 source subtractions;
at most 159,436 target multiplications and 100,446 target additions; and 48
exact divisions by three on each side. Precomputing/storing the sparse R
and enumerating the features also takes O(d^3) integer entries/operations.
All these per-label bounds are independent of the number of shell points.
The reference implementation favors transparent formulas; the counts describe
the explicit reuse schedule just given, not an instrumented Python instruction
count. A primitive integer operation is not being priced as unit bit cost.

## The streaming contract

The previous reference formulas describe a full feature vector, but need not
materialize it. For integers u,w, `u*w*(u+3*w)` and `u*w*(3*u+w)` are even:
if either factor is even this is immediate, and otherwise both parenthesized
sums are even. Hence every mu_i above is even. Put `nu=mu/2`, so

```
nu_a = v_a*v_b*(v_a+3*v_b)/2,
nu_b = v_a*v_b*(3*v_a+v_b)/2,
nu_i = G[i,b]*nu_a + G[i,a]*nu_b - 8*v_a*v_b*v_i.
```

Each retained target numerator `e_j=c_j/2` is computed locally:

| Feature | Numerator e_j; final coefficient is e_j/256 |
|---|---|
| f_i | 4v_i^3 - 3h_i nu_i |
| l_i | 4(v_i^3-4v_i)/3 - (h_i-3)nu_i |
| s_(i,j) | 4v_i^2 v_j - G[i,j]nu_i - h_i nu_j |
| t_(i,j,k) | 8v_i v_j v_k - G[j,k]nu_i - G[i,k]nu_j - G[i,j]nu_k |

These use at most three entries of one R column, obtained directly from G.
Do not construct R. Traverse f, l, s, t in the lexicographic order specified
above, skipping the 48 pivots, and emit `(key, phi_j(x), e_j(Gy))`. Each retained
key occurs once. The parity reduction is a common-denominator bound, not an
optimality claim or the main contribution.

**Ownership and lifetime.** G and both integer coordinate vectors x,y are
borrowed, read-only inputs. The caller must keep them immutable for the whole
iterator lifetime; the implementation does not snapshot or police concurrent
mutation. Each output record belongs to the consumer, which must release it
before requesting the next to use the stated bound. Retained outputs and any
physical data on which coefficients will act are additional caller storage.
There is no assertion that every physical decoder consumer can obey this
contract. Early close releases the iterator's state.

The evaluator owns four length-d vectors: v, nu, x-coordinate squares and
v-coordinate squares. It stores no feature keys, R rows, transform edges or
target accumulation vector. Its remaining state is a fixed number of scalars:
dimension/pivots, three loop indices, Gram-dot accumulator, pivot product and
two pivot numerators, h, current source and target, and the one emitted record.
Allowing 32 scalar/counter/record slots covers those values and temporary
arithmetic results in a sequential register implementation. Therefore

```
owned vector slots                         = 4d,
borrowed source/target coordinate slots     = 2d,
scalar/counter/one-record slots            <= 32,
live slots excluding the immutable Gram   <= 6d+32 = 320,
immutable Gram slots                       = d^2 = 2304,
combined total                            <= d^2+6d+32 = 2624.
```

These are slots of the stated indexed-integer algorithm, not a claim that
CPython represents every object in one machine word. There is no per-feature
immutable descriptor or descriptor-generation phase. Gram access, loop
generation and emitted-record transport are charged below as indexed work,
but no physical tape placement or time/space hierarchy theorem follows.

For comparison, [#5132's stated evaluator bounds](https://github.com/CrocSwap/integer-mult-bounds/blob/08572fdb060e73ecc4cb09a024611039881185f4/research/norm6-constructive-feature-evaluation/PROOF.md)
allocate 19,712 target slots, 64 source slots, and 245,884 immutable descriptor
slots including the Gram. The new contract removes the target accumulator and
transform tables instead of merely shrinking their coefficients. This compares
two explicit upper allocations, not a lower bound on every implementation of
the concurrent construction. The feature bases differ, so their coefficient
arrays must not be substituted without the corresponding source features.

## Streaming work and intermediate widths

Computing v uses d^2 products and d(d-1) additions. Computing nu from the
shared product `p=v_a*v_b` uses at most `4d-3` products, `2d-2` additions and
two exact divisions by two. The two square arrays use 2d products. Each
emitted pair needs at most eight products and three additions/subtractions:
the t case has two source products, six target products and three subtractions;
the f/l/s cases use no more. Only the f-source and l-target need an exact
division by three. Public h_i values are obtained by halving a Gram diagonal
at most 3d times. Thus with `N=C(d+2,3)` the combined source/target stream uses

```
multiplications           <= d^2+6d-3+8N = 159389,
additions/subtractions    <= d^2+d-2+3N  = 61150,
exact feature divisions by three       = 2d = 96,
exact pivot divisions by two           = 2,
public diagonal halvings              <= 3d = 144.
```

The counts permit integer multiplication by constants rather than treating it
as free. They bound one explicit schedule; optimal arithmetic cost is not
claimed. Validating the fixed Gram/preconditions is a separate O(d^2) setup
check. A conservative indexed read/write bound for setup plus evaluation is
`128N+32d^2=2582528`: fewer than 64 indexed accesses suffice per attempted
feature (including skipped pivots and diagonal s indices), N+2d<=2N, and
32d^2 covers Gram, vector setup and validation. Comparisons/loop control can likewise be
charged a constant per attempted feature. Random-access integer operations
remain a model, not free physical routing.

Every intermediate integer in this preprocessing fits 19 signed bits at the
actual shell. Indeed X,Y<=32 and V<=7. Ordered Gram-dot prefixes have magnitude
at most `480Y<=15360`; the final v bound is used only after the dot product
finishes. Source squares/cubes and the `u^3-u` prefix have magnitude at most
32800. Pivot products/numerators are bounded by 49 and 1372. The nu partial
accumulations and final values have magnitude at most `28*7^3=9604`.
Each target numerator, including every displayed left-to-right prefix, has
magnitude at most

```
4*2*7^3 + 15*28*7^3 = 146804 < 2^18.
```

In the l case the pre-division numerator `v_i^3-4v_i` has magnitude at most
371. Indices, counters and denominator metadata are smaller. Thus no large
canceling Gram prefix is incorrectly priced with the final V bound. The
resulting source feature bound is 32768 and common target scale is 256.

An optional exact consumer may accumulate `sum phi_j e_j` as records arrive,
using one additional integer slot. All partial sums have magnitude at most
`19600*32768*146804 = 94285280051200 < 2^47`, so a signed 48-bit accumulator
suffices in that abstract consumer. The final exact value is K after division
by 256. This consumer is a diagnostic for the feature identity; it does not
implement a variable-data native decoder or change the cost of obtaining labels.

## What is not proved

No exact rank, minimal denominator, optimal coefficient bound, full-shell
factor table or physical source/target schedule is supplied. The binary chart
still bounds every factor support's binary pairing rank by 49, so the inherited
algebraic separate-copy upper bill remains `49*19600=960400`. This bound does
not price source access, arbitrary dirty state, frames, ownership, restoration,
native operations, precision, tape movement, the recursive compiler or the
outer multiplication construction. Those obligations remain open.

The exact executable checks corroborate the formula and source binding. They
are not independent human review or formal proof-kernel acceptance. The written
identity, rather than finite samples, supplies the full-shell conclusion.
