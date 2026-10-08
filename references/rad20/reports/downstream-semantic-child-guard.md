# A linear exact guard from completed child interfaces

This is a sharper estimate for the same untruncated complex layer. It
does not change the finite circuit, recursive time recurrence or scalar
operations. The earlier guard concatenates the internal arithmetic
depth of every recursive child. The exact completed child has a much
smaller dyadic denominator and norm bound, so internal excess precision
does not accumulate between completed calls. The proposed whole-layer
guard has C1=1, with explicit fixed C0 below. The [independent transfer review](review-semantic-child-guard.md) is
positive. This guard alone does not promote a new multiplication witness;
its proposed bulk composition has additional transfer obligations.

The primary local source is the pinned CrocSwap/integer-mult-bounds
revision bcd4ebde8692383539f8a48734e5fbf3a18a32c2, especially
`upstream/build/sections/03-motifs.tex` (binary phase and corrected
inverse child) and `05-layers.tex` (individual C kernel, recursive
selected-bit calls and exact guard). The new compact input
6e564879f51ae16f23d392e9e196c605f36d90df retains those exact coefficient
interfaces. Its new control, padding and repair operations only permute
complete encodings. The accepted changed finite complex network retains
the same forward and inverse child kernels and its independently proved
fixed scalar node charge E=64(W+m+1)^3.

## Exact completed maps

The individual kernel is

```
C = ((1+i)I + (1-i)X)/2,
C^-1 = -i Z C Z,  Z=diag(1,-1).
```

For f selected address bits, the completed call is C tensor f, after
the specified binary address basis change and its inverse. Every entry
of this tensor is in 2^-f Z[i]. Its maximum absolute row sum is
(sqrt(2))^f<=2^f. The corrected inverse has the same grid and norm bound,
because signs and fourth-root phases preserve both. These statements
hold for arbitrary signed complex role inputs, including nonzero
scratch; they do not require the inputs to lie in the unit disk.
Address permutations, complete-field padding/crop and exceptional repair
do not change coefficient values.

Consequently, if a call starts with values in 2^-(p+b) Z[i] and modulus
at most 2^b, its completed values lie in 2^-(p+b+f) Z[i] and have modulus
at most 2^(b+f). Its internal implementation may use a larger temporary
bound A(f), but that excess is absent from the exact completed map.
No rounding, truncation, new check or precision rewrite is performed at
this boundary. All coefficients remain in the fixed fine-grid encoding;
the completed values simply have exact zero bits below the coarser grid.
The single original truncation occurs after the entire normalized outer
butterfly layer, as required by the source.

## Internal-node recurrence

Define A(e) as a uniform relative upper bound on both dyadic denominator
exponent and logarithmic magnitude for every intermediate of an exact
recursive C-layer on e=m^k axes. The bound is relative to an arbitrary
incoming grid and magnitude exponent. At a leaf, the retained exact
individual computation gives A(e)<=8e.

An internal node has s child calls, each on f=e/m selected bits, and
total fixed scalar/correction charge at most E. Before any currently
active child, all prior completed children contribute at most sf to
both semantic exponents. The scalar schedule contributes at most E.
Only the active child's internal excess A(f) must then be added.
After it completes, its excess is replaced in the bound by f. Thus

```
A(e) <= A(e/m) + s*e/m + E.
```

Scalar gates are accounted for by the same E proof: additions or
subtractions increase logarithmic magnitude by at most one, halves
increase the grid exponent by at most one, and signs/i preserve both.
Saved-input evaluation of grouped gates is already included in E.
Its charge is fixed per node, independent of record count. The common
address basis changes and the new compact router are value permutations.
No arithmetic chain from another child is silently ignored: each prior
completed child's full output increment f is explicitly included.

Let j be the actual number of internal levels, including stopping above
the retained d^beta threshold. Unrolling gives

```
A(e) <= 8e/m^j + (s/m)e * sum_(v=0)^(j-1) m^-v + E*j
     <= [8 + s/(m-1) + E] e
     <= (8+B)e <= 2B e,  B=s+E.
```

Here j<=log_m(e)<=e for e>=1, m>=3, and B>=8. An already-leaf root
obeys the same bound. This is uniform in beta and in the entire stopped
tree; the former coefficient exponent log_m(s) is unnecessary.

## Complete layer and explicit guard

The base-m decomposition partitions the active axes into disjoint
pieces of sizes e_a=m^k with sum e_a<=d. Even conservatively summing
the new bounds for their full exact implementations gives

```
sum_a A(e_a) <= 2B*d.
```

Alternatively, completed pieces have the same semantic increments e_a
and only the active piece retains its internal excess. Both arguments
are linear and need no bound on the number of pieces. The individually
processed row/front/back axes and the two outer phases, b^D conversion
and final denominator shift are covered by the retained additional
18d units. Therefore every intermediate in the complete outer layer is
bounded by

```
A_layer <= (2B+18)d < C0*d,
C0 = 32*m*B^2,  C1=1,  Delta=ceil(C0*d).
```

The strict constant inequality holds for m>=3 and B>=8. The former
constant 32mB^2(1+1/zeta) would also suffice, but zeta and the associated
piece-count exponent are no longer needed. This fixed constant preserves
the same E and finite network; it does not hide a p-dependent coefficient.

As in the retained encoding proof, p+Delta fractional bits and Delta+3
integer/sign bits represent every real and imaginary component exactly.
For d=floor(b_input^epsilon) and any fixed epsilon<1, these widths are
O(p). A sufficient exact numeric cutoff is

```
log2(b_input) >= ceil(bit_length(2*C0)/(1-epsilon)),
```

with the retained initial b_input/p size bounds. It makes Delta<=p
eventually by the same integer-power comparison used previously.
Time costs for arithmetic, rewinds and address movement are unchanged:
the program still uses the common guarded O(p)-bit words and does not
truncate its recursive outputs. This is a proof of a smaller necessary
guard, not a new arithmetic primitive or stronger machine model.

## Consequence and scope

The scalar constraint becomes epsilon<1 instead of
epsilon[1+(nu-1)(1-beta)+zeta]<1. It is inactive for the already accepted
balanced a/2 family, whose CRT/resampling exposure margin remains.
If the separately proposed router and microbox schedule remove that
exposure cost, the remaining complete inequalities still include

```
kappa<epsilon*q, q<a,
kappa<r-delta, kappa<1-epsilon-delta,
epsilon+r<1, delta>0.
```

They impose the scoped supremum a/(1+a), rather than a. A limiting
witness must keep every Gaussian, normalization, compact reservation,
K geometry and record cutoff strict; none is discarded here. This is
not an unrestricted integer-multiplication ceiling. Exact prospective arithmetic and the separate bulk tape review remain
distinct from this independently accepted guard derivation. Novelty is unclaimed.

## Executed and independent controls

[Producer run 20261008T024303Z](../runs/20261008T024303Z-downstream-semantic-guard/)
passes5460 exact forward/inverse tensor entries, arbitrary incoming grids,
temporary fine-grid excursions,240 stopped recurrences and24 mixed
sequential child calls. Its source is
[downstream_semantic_guard.py](../code/downstream_semantic_guard.py).
The finite surrogate supports the semantic argument; it does not replay
the full large phase network.

The [independent review](review-semantic-child-guard.md) reads the original
parked-stream and returned-role interfaces and retains the fixed integer
encoding throughout its own controls. It asserts1,130,200 divisions even,
compares the closed tensor map with cancellation-heavy exact recursion,
and preserves a negative eager-rounding control. It uses no implicit
Fraction compaction as a substitute for fixed encoding. Its terminal
[run 20261008T025235Z](../runs/20261008T025235Z-review-semantic-guard/)
accepts C1=1 with the same E and C0=32mB^2. Original producer source and
certificate bytes are unchanged after review.
