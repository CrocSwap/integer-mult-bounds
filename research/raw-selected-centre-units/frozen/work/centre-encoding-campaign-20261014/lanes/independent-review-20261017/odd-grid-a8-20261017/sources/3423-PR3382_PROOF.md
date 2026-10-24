# A phase-complete Gaussian entrance for one literal P104 collector

This result changes the admissible numerical states of one fixed collector.
It does not change its scalar/frame word, claim a new precision threshold,
or provide the missing complete P104 correction and supplier invoice.
The construction is motivated by Clifford-invariant and Barnes–Wall lattice
methods. The proof below uses the repository's exact Gaussian normalization;
it does not invoke a lattice classification theorem or claim a new lattice
family.

The source is ywz65's PR #2586, head
`7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`, retained at
`research/p104-rounded-collector/inputs/WORD.json` and `NATIVE.json.gz`.
Tekalign's PR #3025 binds its first collector and supplies the literal signed
floor pair. Ross Richardson's PR #3068, head
`7d2c519a1fdcc6bf66f6f08757eed7c48762d3f2`, supplies the neighboring
period-domain contract and explicitly leaves a larger state exactness domain
open. Their constructions, inverses, source binding and earlier bounds retain
their credit. Exact consumed bytes and the isolated replay are recorded by
the accompanying source manifest and receipt.

## 1. Coordinates and the explicit code

Put `pi = 1+i`, so `pi^2 = 2i` and `1/pi = (1-i)/2`. An array of
`2^r` Gaussian integers is a function on the binary cube. It has unique
multilinear Newton coefficients:

\[
 f(x)=\sum_{S\subseteq\{0,\ldots,r-1\}}a_S x^S,
 \qquad x^S=\prod_{j\in S}x_j.
\]

Uniqueness follows by Boolean differences, or by the triangular evaluation
matrix indexed by subsets. Define the Gaussian module

\[
 \mathcal B_r=\{f:a_S\in\pi^{|S|}\mathbb Z[i]\text{ for every }S\}.
\]

Its encoder is explicit:

\[
 E_r=E_1^{\otimes r},\qquad
 E_1=\begin{pmatrix}1&0\\1&\pi\end{pmatrix}.
\]

Thus a coefficient pair `(c0,c1)` becomes `(c0,c0+pi*c1)`. Bit `j` is
the address bit `1<<j`; tensor factors may be applied in ascending bit order.
The resulting Newton coefficient is `a_S=pi^|S| c_S`. The reverse sweep
replaces each second entry `b` by `(b-a)/pi`; all divisions are exact exactly
on this image. This gives both an encoder and a membership test. These are
computations with costs, not a free reinterpretation of arbitrary numerical
payloads.

## 2. Exact maximality for simultaneous coordinate prefixes

The source's positive Gaussian pair is

\[
 C(a,b)=\left(\frac{a+b+i(a-b)}2,
                 \frac{a+b-i(a-b)}2\right).
\]

On `(a,a+d)` this is `(a+d/pi, a+d/pi+i*d)`. Consequently

\[
 E_1^{-1}CE_1=\begin{pmatrix}1&1\\0&i\end{pmatrix},
 \qquad (c_0,c_1)\longmapsto(c_0+c_1,ic_1).
\]

This matrix and its inverse have Gaussian-integer entries. It follows that
each coordinate `C_j`, and its inverse, preserves `B_r` in both directions.

For a subset `T` of address bits write `C_T=product_{j in T} C_j`.
The coordinate gates commute. We claim the exact equality of sets

\[
 \mathcal B_r=
 \{f\in\mathbb Z[i]^{2^r}:C_T f\in\mathbb Z[i]^{2^r}
                         \text{ for every }T\subseteq\{0,\ldots,r-1\}\}.
\]

One inclusion follows from the displayed intertwiner. For the other, evaluate
at the all-zero address. A transformed monomial contributes `pi^-|S|` when
`S` is contained in `T`, and otherwise contributes zero. Therefore

\[
 g(T):=(C_T f)(0)=\sum_{S\subseteq T} a_S/\pi^{|S|}.
\]

Every `g(T)` is Gaussian integral by hypothesis. Boolean Möbius inversion gives

\[
 a_S/\pi^{|S|}=\sum_{T\subseteq S}(-1)^{|S|-|T|}g(T)\in\mathbb Z[i],
\]

which is membership in `B_r`. In particular `B_r` is the largest integral
module invariant under every coordinate `C_j`. More strongly, no module
assumption was needed for the displayed equality of sets.

The quantifier is **every partial product**. It cannot be replaced by testing
each gate once on the entrance. For `r=2`, the function `pi*x0*x1` has integral
`C_0 f` and `C_1 f`, but `(C_0 C_1 f)(0)=1/pi` is nonintegral. A test that
admits this vector from only the first two outputs has not checked the theorem.

This is not maximality for a fixed completed transform with cancellation,
for an arbitrary nonlinear word, or for Ross's translation-period premise.
His `Gamma` and `Lambda` are different domains. No global containment between
those domains and `B_r` is claimed, and no finite index census is needed here.

## 3. Why the literal floor program becomes exact

For Gaussian integers `a,b`, let `d=a-b`, take componentwise signed floors,
and execute the credited pair:

```text
d = a-b
s = b+floor(d/2)
d = i*d
b' = s-floor(d/2)
a' = b'+d
```

Its inverse uses `-i` in place of `i`. The generic bijection and paired inverse
are PR #3025's result, not a new claim here. Writing the original difference
as `p+iq`, and putting `t=(q mod 2)-(p mod 2)` with residues in `{0,1}`,
direct subtraction from the ideal map gives the same discrepancy in both
output entries:

\[
 (a',b')-C(a,b)=\bigl(t(1-i)/2,t(1-i)/2\bigr).
\]

The same condition gives zero discrepancy for the negative pair. Thus literal
and ideal pairs agree exactly when `p,q` have equal parity, equivalently
`pi` divides `a-b`. This is also exactly the integrality condition for the
ideal pair on Gaussian integer inputs.

For any fixed values of the other bits, the difference of the two entries of
a `B_r` function along bit `j` is divisible by `pi`. After an ideal `C_j` the
entire array remains in `B_r`, by Section 2. Induction therefore proves exact
literal floor execution at every subsequent coordinate stage. This induction
is the all-input argument; checking a linear basis alone would not prove
exactness of the unrestricted nonlinear floor map.

All statements are unchanged after multiplying every array by a common grid
spacing `2^-f`. The integer numerators retain that grid throughout this
restricted execution.

## 4. The actual Gaussian monomial alphabet preserves the code

The authenticated source wrappers send input address `x` to `A*x+b` over
`F_2`, and attach the input-address phase

\[
 i^{p+\sum_j l_jx_j+2\sum_{j<k}q_{jk}x_jx_k}.
\]

Here `A` is invertible, `b` is binary, `p,l_j` are modulo four, and `q_jk`
are binary. These are exactly the `matrix_rows`, `offset`, `linear_Z4`,
`quadratic_rows` and `phase` fields of the retained recipes. The phase is
evaluated before the address permutation; changing that convention changes
the operator.

Every invertible binary affine map is generated by address XORs, bit swaps
and CNOTs: Gaussian elimination supplies swaps and elementary row additions,
and the offset supplies XORs. The phase is a product of global powers of `i`,
single-bit phases `S_j=i^{x_j}`, and `CZ_jk=(-1)^{x_j*x_k}`. Each generator
preserves `B_r`. Here are direct integral coefficient formulas; they are
also useful implementation intertwiners.

| Physical gate | Action on a coefficient pair `(a,b)` |
|---|---|
| `C` | `(a+b, i*b)` |
| `C^-1` | `(a+i*b, -i*b)` |
| `S` | `(a, i*(a+b))` |
| `S^-1` | `(a, -a-i*b)` |
| address XOR `X` | `(a+pi*b, -b)` |

For two bits write a coefficient block as
`a + pi*b*x + pi*c*y + pi^2*d*x*y`. A CNOT with control `x` and target `y`
acts by the substitution `y -> x xor y = x+y-2xy`, and gives

\[
 (a,b,c,d)\longmapsto
 (a,\ b+c+\pi d,\ c,\ (i-1)c-d).
\]

The phase `CZ=(-1)^{xy}=1-2xy` gives

\[
 (a,b,c,d)\longmapsto
 (a,\ b,\ c,\ ia+(i-1)(b+c)-d).
\]

These formulas use `x^2=x`, `y^2=y` and `2=-i*pi^2`. The other bits contribute
the same common coefficient factors, so the formulas apply at every rank.
Bit swaps simply permute coefficient indices. The listed self-inverse gates
remain self-inverse under conjugation; `C` and `S` have the integral inverses
shown above. Global Gaussian units preserve the module. Thus every full source
wrapper, and its inverse, preserves `B_r`.

No unrestricted phase or permutation is admitted by this argument. For example,
the cubic phase `(-1)^(x0*x1*x2)` applied to the constant one produces Newton
coefficient `-2` at degree three. It is not divisible by `pi^3`, so the result
leaves `B_3`. The quadratic source schema matters.

The old structured phase witness is a positive control here. The constant one
and `i^{x_j}=1+(i-1)x_j` both belong to `B_r`, because `i-1=i*pi`.
The latter leaves the older `Gamma` period lattice, as credited in PR #3068.
That earlier counterexample did not claim that it creates a lifting error.

## 5. One complete source-bound collector

Use zero-based events **2025–2039** of the retained PR #2586 word. They are:

1. Allocate zero private `C` at the common source frame.
2. Add `D31,D30,D29,D28,D27` to `C`, in that order.
3. Apply the literal rank-seven transport `U` at event 2031.
4. Add `C` to the arbitrarily dirty query `Q7` at its common frame.
5. Apply the separately archived return `V` at event 2033.
6. Subtract the five original sources in reverse order; erase exact zero `C`.

The source arrays have 512 complex entries and nine address bits. Both native
recipes have the form `M_left C_0 ... C_6 M_right`. The complete surrounding
wrapper acts on all nine bits, so the contract is `B_9`, not an unproved
rank-seven block restriction. Source authentication binds the two event
occurrences, their frames, the common-chart ADDs and their actual recipes.
The predecessor's exact native interpretation is retained; the finite operator
check of `VU=I` is separate from the lattice exactness argument.

Assume the five source arrays and the initial query belong to `2^-f B_9`.
They are otherwise arbitrary, independently dirty and potentially correlated.
The five sources remain available and unchanged across this whole interval.
The private `C` is owned and starts zero. No alias of those distinct roles or
nonzero private initialization is granted.

Let `s` be the sum of the five sources. Module closure gives `s in 2^-f B_9`.
By Sections 3–4 both actual transports execute their exact ideal maps on this
domain. The query becomes `Q7+U*s`. Since `VU=I`, the private register returns
to `s`; subtracting the unchanged sources makes it exactly zero. Thus the
literal endpoint is

\[
 (D31,\ldots,D27,Q7,C=0)
 \longmapsto(D31,\ldots,D27,Q7+U\sum_jD_j,C=0).
\]

The query remains in the same declared lattice and grid. There is no rounded
query defect, per-input grid selection, residue history or numerical downcast
in this restricted-state execution. This permits the separately archived `V`;
the unrestricted approximate lifting contract instead needs its paired inverse.
They must not be interchanged when counting operations.

This is a boundary assumption at the actual collector cut. The earlier producer
has not been proved to supply this state for arbitrary unrestricted inputs.
The later whole word also has additional operations. A repeated collector is
valid only when its sources, frames, permissions and declared lattice are
available at its own cut.

## 6. Quarter ADD and the exact meaning of an encoder

Whole-array ADD by any Gaussian-integer coefficient preserves `B_r`. For an
integral array `z`, a quarter source `z/4` belongs to `B_r` exactly when
`z` belongs to `4B_r`. Integral components alone do not imply that condition.
At rank one `(4,0)` belongs to `B_1`, but `(4,0)/4=(1,0)` does not. Extend
the pair constantly in the other eight bits for the actual nine-bit counterexample.
Conversely `z=4E_r c` always has the admissible quarter `E_r c`.
The named collector contains only unit ADDs, so this counterexample marks the
external interface; no quarter instruction is treated as free within its bill.

Encoding arbitrary raw coefficients `c` as `E_r c` changes the logical action
of a physical native map `U` to

\[
 T=E_r^{-1}UE_r.
\]

The gate formulas prove that `T` is an explicitly described Gaussian-integral
automorphism for the stated alphabet. They do **not** say `UE_r=E_rU`.
Already `C E_1 != E_1 C`; a control checks this distinction. Substituting this
representation into a caller expecting a different map requires its own
intertwining adapters and their complete costs.

For clarity, one fully specified optional cold preparation realizes this
different `T` contract. Keep five arbitrary raw Gaussian coefficient source
arrays borrowed and unchanged, and give the query mutable ownership. Allocate
five zero source banks, copy the borrowed sources into them by five full-array
ADDs, and encode the five banks and query. Run the original collector on these
six encoded fields. Decode the query and all five banks. Each source bank is
then exactly its original raw source; subtract that borrowed source, check zero
and dispose of the bank. The query endpoint is `q+T*sum(sources)`.

This construction uses six encodes, six decodes, five copy ADDs, five cleanup
ADDs and five additional owned array lifetimes. It demonstrates a complete
logical codec schedule with literal restoration. It does not admit that `T`
as a requested recursive caller, give a free borrowed-input conversion, or
establish an advantage over an existing `U` implementation.

## 7. Gate, codec and storage ledger

All counts in this section concern a direct scalar reference with explicit
array access. They are not tape time, native child tariffs or a lower bound.
Gaussian units, signed arithmetic and addressing are separate operations.

An encode or decode sweep has `r*2^(r-1)` tensor pairs. Encoding a pair uses
one multiplication by `pi` and one Gaussian ADD. Decoding uses one Gaussian
subtraction and one exact division by `pi`. Multiplication by `pi` is
`(a-b,a+b)`; exact division is `((a+b)/2,(b-a)/2)`. Thus each encode pair costs
four real additions/subtractions, while each decode pair adds two exact real
halvings. Each loads four real components and writes two. An in-place sweep
uses the owned numerical array and four real work words; loop/control storage
and physical routing are additional. Borrowed input cannot be overwritten to
obtain this in-place price.

At `r=9`, each direction has **2,304 pairs**. The optional cold schedule therefore
adds 13,824 `pi` multiplications, 13,824 exact `pi` divisions, 110,592 real
additions/subtractions, 27,648 exact real halvings and its ten full-array copy/
cleanup ADDs. Those ten ADDs add 10,240 real additions/subtractions, 20,480
real-component reads and 10,240 writes. The codecs add 110,592 component reads
and 55,296 writes. Five extra owned banks add 2,560 complex words and 5,120
component initializations and zero checks each. These quantities are additional
to the direct collector below; they are not paid by an abstract rank count.

For the literal collector, both seven-stage transforms use `7*512=3,584`
pair applications altogether. Each credited signed-floor pair costs eight
real additions/subtractions, four real floor halvings and one Gaussian quarter
turn. The eleven field ADDs cost `22*512` more real additions/subtractions.
The four actual wrapper cycle counts, in chronological order, are

\[
 U_{right}:64,\quad U_{left}:128,\quad V_{right}:160,\quad V_{left}:64.
\]

The credited one-zero-Gaussian-scratch cycle algorithm uses `N+c` swaps for a
wrapper with `c` cycles and `N` unit phase applications. Here it gives **416
cycles and 2,464 swaps**, plus 2,048 phase applications. The old paired-inverse
schedule's 384 cycles and 2,432 swaps do not price these separately archived
return wrappers. The phase acts on the cycle scratch before each swap, so its
arithmetic is counted without an extra full-array phase pass.

| Direct collector operation | Count |
|---|---:|
| Signed-floor pair applications | 3,584 |
| Real additions/subtractions, including all eleven field ADDs | 39,936 |
| Real floor halvings | 14,336 |
| Pair Gaussian quarter turns | 3,584 |
| Actual wrapper Gaussian swaps | 2,464 |
| Actual wrapper unit phase applications | 2,048 |
| Butterfly real-component reads / writes | 14,336 / 14,336 |
| Field-ADD real-component reads / writes | 22,528 / 11,264 |
| Wrapper-swap component reads / writes, including scratch | 9,856 / 9,856 |
| Private initialization / zero-check component inspections | 1,024 / 1,024 |

The 10,240 source-component reads are a subtotal of the field-ADD reads, not an
extra charge. The direct contract has five borrowed source arrays, one mutable
query, one owned zero private array and one zero Gaussian wrapper scratch,
with constant pair work. The optional cold schedule supplies the five source
arrays by additional owned copies. Source plans, range/type validation,
permissions, address/control work, physical movement, allocator behavior,
recursive children, precision metadata and final endpoint consumption require
their actual caller's tariff. They do not acquire a zero price from these
scalar counts.

## 8. Finite headroom

Let `H` bound the absolute value of every real and imaginary component at a
codec's own entrance. During an encode the exact largest real component row
sum after at most `r` factors is bounded by

\[
 M_r=\sum_{k=0}^r {r\choose k}
       (|\Re\pi^k|+|\Im\pi^k|).
\]

This follows by expanding a tensor row; its entries are powers of `pi`, one
for each subset. A smaller partial row is covered by the same nonnegative
bound. For `r=9`, `M_r=3363`. Thus `M_r H` bounds stored encoder components;
`3 M_r H` is a conservative bound for its two-step arithmetic temporaries.

A row of a `k`-factor inverse sweep is a signed sum of `2^k` inputs divided by
`pi^k`. Its real component row sum is
`2^k (|Re pi^-k|+|Im pi^-k|)=|Re pi^k|+|Im pi^k|`, at most
`2^ceil(r/2)`. Therefore decoder components are bounded by `2^ceil(r/2) H`,
and its subtraction/numerator temporaries by four times that amount. These
are sufficient arithmetic bounds, not a compression or precision advantage.

For the direct collector suppose its six admitted entrance fields have
integer numerator components bounded by `H`. The sum of five sources has
Hilbert norm at most `5 sqrt(2N) H`. Every exact native prefix is unitary,
including each wrapper. At `N=512`, **160 H** bounds every native-prefix real
component; **161 H** bounds the updated query. A conservative signed-floor
pair scratch bound is **800 H**. Gathers and ungathers are bounded sums of at
most five unchanged sources. Partially written stages store either preceding
or completed pair values, so these same bounds cover the entire execution.

For the optional cold caller, now let `H` bound its **raw coefficient** entrance.
Encoding gives `3363 H`; the collector therefore gives an encoded query bound
`161*3363 H=541443 H`. Decoding that query gives at most
`32*161*3363 H=17326176 H`. The conservative complete scratch bound is four
times this last quantity, **69304704 H**, which also dominates the encoder,
native pair, source-bank decoding and cleanup temporaries. These composed
bounds make the optional caller's finite-width obligation explicit; they are
not measured peaks or necessary widths.

For a nonnegative integer component bound `M`,
`1+ceil_log2(M+1)` signed bits suffice. This states an explicit finite range;
an actual fixed-width implementation must use that range, retain the required
grid and charge its bit arithmetic. The older sharp scalar-grid/Clifford
denominator results remain credited and unchanged.

## 9. Evidence boundary and stopping decision

The written arguments hold at every finite rank. The new managed-Python model
and finite source checks are bounded by nine address bits, 512 complex entries
and 8,192 magnitude bits per admitted input or returned array component.
Signed storage may require another bit; exact arithmetic temporaries have the
additional finite headroom derived above. The functional model allocates fresh
lists, while the direct ledger prices the separately specified in-place codec
and credited cycle-scratch algorithm. It is not a measurement of Python
allocation. Membership checks and snapshots inside verification are test work;
a production caller must establish or pay for its lattice entrance.
Managed allocation and verification snapshots are not a physical memory
implementation. Exact checks use explicit exceptions, including under Python
optimization.

Finite verification binds the two archived recipes, checks exact operators and
both literal directions on admitted states, tests dirty collector endpoints,
and exercises the missing-prefix, phase-alphabet, wrong weighting, quarter-ADD,
intertwiner and source/invoice failure boundaries. The separate checker uses
its own representation and does not derive a nonlinear universal theorem from
finite basis samples. Source-native correctness, physical ownership, eventual
recursive prices and human/proof-kernel admission remain separate premises.

The result stops at a phase-compatible exactness theorem, one actual complete
local collector, an explicit codec/intertwiner, and their full direct logical
ledger. It neither proves that earlier arbitrary P104 inputs satisfy the
entrance nor extends the contract to the later quarter ADDs. A larger caller
needs an actual admitted source of this state and a compatible fully charged
consumer. No selected frontier, all-size supplier, new scalar-grid guard,
physical storage saving or new kappa follows.

Prepared by Clear1nsight with substantial OpenAI assistance. Separate automated
derivation and review are not independent human or formal-kernel verification.
Apache-2.0; predecessor authors and original source notices retain their credit.
