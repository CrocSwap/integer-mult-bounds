# Encoded endpoints at the multiplication interface

The outer algorithm does not require the natural order of Fourier
coefficients. It already retains two record permutations. It does require
the correct coordinatewise product before the opposite transform. A
general invertible code cannot pass through that product without work.

There is a useful change of interface. A fixed tensor-word code can be
decoded once at the end of a complete transform within the selected
asymptotic budget. This statement does not permit a decoder at every
butterfly layer. The unresolved construction problem is to carry the code
through the intervening layers and twiddles, with a bounded final word.

## 1. Source boundary

The source snapshot is commit
`3ae9a6f3ac74ded022ab3b4872a7357a621af6fb` of
`CrocSwap/integer-mult-bounds`. The selected certificate is still
[PR1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094), with
`kappa = 836330098538459/500000000000000000`. This note does not change
that selection. The checker pins the certificate, its review, the
selected replay archive, and the following source files.

- [The simultaneous layer](https://github.com/CrocSwap/integer-mult-bounds/blob/3ae9a6f3ac74ded022ab3b4872a7357a621af6fb/upstream/build/sections/05-layers.tex)
  uses the finite supplier for `C` tensor powers. It obtains rows from
  existing data by a radix split. Every productive role can contain an
  arbitrary input. The exact child contract acts on every role. The
  padding rows can be removed only after their correct output is zero.
- [The synthetic transform](https://github.com/CrocSwap/integer-mult-bounds/blob/3ae9a6f3ac74ded022ab3b4872a7357a621af6fb/upstream/build/sections/06-transforms.tex)
  places a twiddle after each forward parallel layer. The stored forward
  map is `L B F^-`; its opposite consumes that order as
  `F^+ B^-1 L^-1`. The common record permutation passes through the
  coordinatewise polynomial product.
- [The source transform](https://github.com/CrocSwap/integer-mult-bounds/blob/3ae9a6f3ac74ded022ab3b4872a7357a621af6fb/upstream/build/sections/07-resampling.tex)
  retains a permutation `R`. Its convolution identity explicitly uses
  the same permutation on both forward outputs.
- [The final assembly](https://github.com/CrocSwap/integer-mult-bounds/blob/3ae9a6f3ac74ded022ab3b4872a7357a621af6fb/upstream/build/sections/08-assembly.tex)
  transforms both operands, multiplies corresponding complex
  coefficients, then uses the opposite transform and fixed scales.
- [The selected outer engine](https://github.com/CrocSwap/integer-mult-bounds/blob/3ae9a6f3ac74ded022ab3b4872a7357a621af6fb/research/complex-sw4-frame8/vendor/main/research/complex-k492-owner-repair/vendor/multicold/engines/outer.py)
  gives the current balanced-prefix parameters and strict margins. The
  older numerical constants in the upstream exposition are not the
  selected numerical parameters.

The local names `X` and `Y` are supplier role banks. They are not the two
integer operands. Mixing these banks mixes records of one transformed
operand. The same record code would then act separately on both integer
operands.

All results below are exact identities before truncation. The selected
all-size, compiler, hosting, precision, tape, analytic, and bit-supplier
assumptions remain in force. A changed complete program also needs its
own precision and cost proof.

## 2. The unchanged product allows only a common monomial code

Let `a,b` be arbitrary vectors in `C^n`. Let `E,F` be invertible linear
codes on the two operands. Suppose an invertible linear map `D` satisfies

```text
D ((E a) pointwise-multiply (F b)) = a pointwise-multiply b
```

for every `a,b`. Then there are a permutation matrix `P` and invertible
diagonal matrices `D_alpha,D_beta` such that

```text
E = D_alpha P,       F = D_beta P,
D = P^-1 (D_alpha D_beta)^-1.
```

To prove necessity, take distinct coordinate vectors `e_i,e_j`. Their
product is zero. Since `D` is injective, each row `r` satisfies
`E_ri F_rj=0` for `i != j`. Both rows are nonzero. If their supports
contain `i` and `j`, this equation forces `i=j`. Thus each row has one
nonzero entry and the two row supports agree. Invertibility makes their
common support map a permutation. The case `i=j` gives the stated `D`.
Substitution proves sufficiency.

The result permits different scalar codes on the two operands. If the
same code is used on both, its scales are squared at the product. Merely
applying `E^-1` after the product is generally incorrect. Reciprocal
operand scales or an explicit product scale can correct them.

The same conclusion holds if the final decoder mixes polynomial
coefficients, provided it is invertible and the operand codes act by
the same complex scalar matrix on each coefficient. Use constant
polynomials in the necessity proof. This is the actual coefficientwise
supplier setting. The ring `C[y]/(y^r+1)` has zero divisors; this note does
not classify all linear codes over that ring. In particular, a common
ring automorphism, such as a permitted `y -> y^k`, is a separate
compatible operation with its own implementation cost.

There is also a coupled-operand version. Suppose an invertible linear
map on `(a,b)` supplies `n` pairs of linear forms `(u_j,v_j)`, and an
invertible linear decoder maps their `n` products to all `a_i b_i`.
Then each pair is, up to nonzero scales, `(a_i,b_i)` or `(b_i,a_i)`, with
one permutation of `i`. Indeed each `u_j v_j` is in the span of the
`a_i b_i`. Its quadratic-form rank is at most two. A nonzero sum of
`k` different `a_i b_i` has rank `2k`. Thus `k=1`; unique factorization
of polynomials gives the two stated factors. This also excludes an
arbitrary borrowed input from either factor. There is no claim for
extra products, a restricted input subspace, or a nonlinear decoder.

## 3. Two actual failures of direct product compatibility

For an odd nonzero binary line `q`, the intrinsic line operator is

```text
C_q = a I + b X_q,       a=(1+i)/2,       b=(1-i)/2.
```

The inputs `delta_0` and `delta_q` have disjoint support, but

```text
(C_q delta_0) pointwise-multiply (C_q delta_q)
    = (delta_0+delta_q)/2.
```

The same failure holds for `C_q^-1`. No invertible linear opposite
consumer can map this nonzero product to zero. By contrast, `C_q^2=X_q`
and `C_q^4=I` are permutations. The diagonal `S` factors that convert
`C` into the outer `H_0` layer do not change this support test. The
checker verifies the test for all 112 actual supplier ports.

The proposed archive controller has a second witness. Use its frozen
[ordered rules](../encoded-controller/QQ16-ARCHIVE-CONTROLLER.md).
In the sector constant in both cover and address, fix one query
coordinate and write each bank as `(u,a,t)` along the three disjoint
port sets `(U,A,T)`. The actual Gram identities are
`R_U K_U=12I`, `R_A P_A=I`, and `R_T P_T=I`. The full nine-call word,
with its retained ordinary terminal, has

```text
final X_A,0 = P_A (12 u_0+a_0+t_0).
```

Take one operand supported on `K_U e_k` in original `X_U,0`, and the
other on `P_A e_k` in original `X_A,0`. Their original coordinatewise
product is zero because `U` and `A` are disjoint. At the displayed
output their product is `12 (P_A e_k)^2`, entry by entry, and is nonzero.
For `k=0`, the first A port gives `3/4`. The independently reconstructed
24-coordinate endpoint agrees with every entry of the frozen receipt,
for both the base and exposed-driver variants.

This is a compatibility test of the proposed logical endpoint. It does
not certify the new whole global native program. Conversely, lack of
that native certification is not used as a reason to reject the logical
code. The displayed code itself does not preserve the unchanged
product. A new product algorithm or an explicit decoder remains possible.

## 4. An odd line code does not pass through the actual twiddle as a rename

Take one axis at current synthetic length four and fix its lower index
bit to one. The actual twiddle in Section 06 is `diag(1,t)`, where
`t=y^(-r/2)` and `t^2=-1`. On a `q` orbit with that axis in `q`, direct
multiplication gives

```text
C diag(1,t) C^-1 = (1/2) [[1+t, i(1-t)],
                          [-i(1-t), 1+t]].
```

All four entries are units in the polynomial ring, since
`(1-t)(1+t)=2`. For `lambda` independent tensor columns, choose the same
legal lower-bit setting in one axis per column and zero in the other
axes. The conjugated twiddle has `2^lambda` nonzero record entries in
each row of this subcube. The entries are products of units, so zero
divisors do not remove the support.

A monomial operation preserves the support size of a dependency row.
A binary ADD can at most double it along a dependency path. Therefore
a fixed finite word of monomial operations and binary ADDs cannot
implement these transported twiddles for all positive `lambda`; the
maximum ADD depth must be at least `lambda`. This includes arbitrary
borrowed inputs, since the exact target rows must have zero coefficients
on those inputs. It is not a native-child lower bound or a lower bound
against recursive or size-dependent programs. It isolates the failure
of the proposed free frame transport.

## 5. A terminal decoder can be affordable

Here is a sufficient interface theorem. Let the complete stored forward
transform be `T_-`, and let `T_+` be its correct opposite consumer,
including the retained layout permutations. Suppose new complete
procedures compute `E_- T_-` and `E_+ T_+`. Suppose:

1. Both codes have explicit inverses as fixed finite tensor words.
   Their number of scalar gates, charts, and tensor factors is
   independent of the transform size. Their fixed-width scalar maps
   are dyadic units; their binary charts have a fixed-size base matrix.
   A tensor factor acts on at most `O(d)` selected bits.
2. All address and source accesses have the retained stream interface.
   Charts on full `K`-bit chunks use the admitted packed coordinate-map
   engine. Selected-bit-only charts can use elementary split/merge
   kernels. The data record width is `Theta(p)` and `dK=o(p)`.
3. The encoded procedures satisfy the required contract on every other
   physical field. The inverse words preserve arbitrary borrowed state.
   The number of complete transforms is fixed.

Then decode each forward result once, perform the original pointwise
product, run the encoded opposite, and decode once more. This gives the
same exact multiplication computation. The added time is

```text
O(V (d + (dK)^tau)),
```

where `V` is logical bit volume and `tau=1-a` is the retained bit
exponent. The added exact denominator depth and logarithmic prefix
norm are `O(d)`. These are extra precision obligations, not free gates.

For the time bound, apply each tensor `C` or `C^-1` by the individual
selected-bit kernel in Section 05. Each kernel includes its split,
arithmetic, merge, counters, and cleanup, and costs `O(V)` per bit.
The fixed number of full-chunk binary charts costs
`O(V((dK)^tau+1))` by the same retained coordinate-map interface used
by the supplier. The scalar scans cost `O(V)`. A selected-bit-only
linear chart can instead be factored into `O(d)` two-bit operations.
Split into its four bit classes, permute those streams, and merge;
the complete ranges give the same residual address order in each
stream. These are `O(V)` operations under the same record and counter
bounds. No array access is free in either argument.

Each exact tensor kernel adds a bounded denominator depth and a bounded
logarithmic norm. Each fixed scalar word adds a constant. Hence `O(d)`
extra exact grid bits suffice for the decoder. If approximate transforms
are used, their error target must also include this inverse norm. An
extra `O(d)` fractional-bit reserve suffices for that bound. Since
`d=o(p)`, the record width remains `Theta(p)` and the exponent is
unchanged. A new finite guard and final rounding proof are still needed
for a concrete program. This theorem does not silently reuse the old
finite guard value.

For the selected parameters, `d=p^(epsilon+o(1))` and
`K=p^(epsilon c+o(1))`. The exact certificate gives

```text
1-epsilon-kappa > 5/10^19,
a-kappa > 28/10^7,
1-epsilon(1+c) > 0.
```

Thus both terms in the added invoice are
`o(V p^(1-kappa))`, even with fixed logarithmic factors. This is an
asymptotic conclusion. The first margin is very small and gives no
practical threshold.

There are two limits. First, the supplier returns one parallel layer,
not a complete transform. The full synthetic transform has
`ell=log2(r)=Theta(p/d)` rounds. Here `K` is the packed chunk width;
it is not the number of rounds. A direct decoder after every round
has an `O(V ell d)=O(Vp)` tensor-kernel term. This particular upper
bound does not prove the selected target `O(Vp^(1-kappa))`. This is
a failed invoice, not a lower bound. Second, transporting a code
across many rounds may make its inverse word grow with `ell`, or
make a tensor factor act on `Theta(p)` bits. Mere invertibility does
not meet hypothesis 1. A bounded propagation law or a different
complete-transform construction is needed.

The archive controller has an explicit finite logical inverse. That is
a reason to pursue such propagation. It does not yet supply it, and
Sections 3 and 4 explain why the unchanged consumer does not do so.

## 6. The selected roles cannot all be removed from the ledger

The original selected replay gives `W=14336` productive families,
`m=73`, and paid rank mass `1041408`. Its rank mass deficit is `5120`.
For a positive saving `b`, the moment condition for `W-k` productive
families requires

```text
sum_r h_r (r/m)^(1-b) < W-k.
```

Since every paid `r` is strictly between zero and `m`, this implies
`sum_r r h_r < m(W-k)`. This necessary condition uses the complete
recursive profile, not only a local child count.

Grant the removal of every rank-eight child for free: there are
`1152=144*8`, with total rank mass `9216`. The remaining mass is
`1032192`, and `mW-1032192=14336`. Consequently `k` can be at most
`196`. There are `8*8*16=1024` A families in the eight banks of sixteen
replicas; A and T together use `2048`. Discarding all these A outputs
therefore fails even this favorable unchanged-profile screen.

This statement does not cover a different child profile, a different
row layout, partial subspace productivity, or children omitted because
a new source is known to be zero. Those changes need a new supplier
and invoice. Arbitrary old selected inputs cannot be declared zero.

## Verification and next construction target

Run:

```text
python3 -I -O -B check_outer_encoding_interface.py
```

Expected first line:

```text
PASS_OUTER_ENCODING_INTERFACE
```

The checker uses exact rational arithmetic. It reads pinned Git objects
and pinned campaign evidence. It rebuilds the complete archive sector
from numerical local block matrices and the source schedule, then
compares both full endpoints and inverses. It checks the actual Gram
identities, all 112 odd-line witnesses, the exact twiddle identity in
`Q[i,t]/(i^2+1,t^2+1)`, the selected asymptotic margins, and the full
rank-mass screen. It does not import a producer checker. The general
classification and stream-cost theorem are proofs in this note; a
finite computation does not replace them.

The next positive target is precise: construct a bounded-size family of
codes which contains a useful centre-saving endpoint, has a proved
transport rule through the actual butterfly and twiddle rounds, and
has a fixed tensor-word terminal decoder. Then the outer assembly can
pay that decoder once. The present archive endpoint and odd line frame
policies do not yet meet this target. No new supplier, kappa improvement,
or general multiplication lower bound is claimed.

This work uses the selected community construction and the campaign's
archive controller. It was prepared with OpenAI Codex assistance.
