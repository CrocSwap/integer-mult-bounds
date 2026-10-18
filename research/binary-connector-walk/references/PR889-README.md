# Batch product shears with a common right factor

**Recursive-interface construction; no new κ.** This package supplies an exact
multi-output version of the dirty product commutator from Chafik Boukhalfa's
[PR628](https://github.com/CrocSwap/integer-mult-bounds/pull/628), with a literal
instruction generator, complete local cost recurrence, a restricted-query
optimality argument, and independent exact checks.

For the seed-58 fixture, five outputs share eight rightmost factors. Batching
uses **246 primitive factor-shear calls**, versus **680** for five separate
balanced binary products, with **four borrowed dirty arrays in either case**.
The comparison is between these explicit binary schedules. Multiway echoes and
arbitrary circuits are outside the comparison. The 434-call reduction (about
63.82%) is not a measured runtime or an integer-multiplication exponent gain.

From the repository root, Python 3.9+ and the standard library suffice:

```sh
python3 -I -O -B research/dirty-fanout-batch/verify.py
```

Expected: `PASS_DIRTY_FANOUT_BATCH`, 128 free-word cases, 795 dense cases,
`680 -> 246 leaves`, four dirty arrays. The default command checks the complete
committed [certificate](CERTIFICATE.json); `--write` regenerates it instead.
`python3 -I -O -B research/dirty-fanout-batch/test_package.py` checks relocation
and rejects deliberately broken packages.

## Contract and exact identity

Let x, y_1,...,y_k and every borrowed array be independent arbitrary elements
of R^L, with distinct storage and unchanged read-only coefficients. R may be a
noncommutative ring; A_i and B are additive linear operators, in the indicated
order. The goal is simultaneously

```
x -> x,          y_i -> y_i + A_i B x,          all borrowed arrays restored.
```

A child `target += F(source)` preserves its source and all its own scratch.
It is independent of the target's previous value. Its negative call is the
literal reverse instruction word with signs reversed. Every source/target and
coefficient array is excluded from borrowed storage. All outputs are reserved
throughout the batch. No concurrent observer may use the temporary output
values. Common B and its input x must stay identical across the two calls.

With one arbitrary dirty connector z, execute:

1. `z += B x`.
2. For every i, `y_i += A_i z`.
3. `z -= B x`.
4. For every i in reverse order, `y_i -= A_i z`.

The two observed values of z are z_0+B x and z_0. Thus the increment is
A_i(z_0+B x)-A_i z_0=A_i B x. All dirt cancels, and z returns to z_0. No
commutation of A_i with B, or of individual factors, is used. Neither A_i
nor B needs to be invertible; their additive shears are invertible. Distinct output
ports make the A_i calls commute with one another after their private scratch
has been restored. The emitted negative block nevertheless uses the literal
inverse, so no extra commutation assumption is needed for its implementation.

This is the familiar commutator identity applied to a direct-sum output map;
we make no algebraic or literature-priority claim. The contribution is the
explicit batched interface, executable factor lowering, pricing, and controls.
It changes the demanded output family; it is not a new single-output echo tree.

### A sharp bound in the specified star-query model

Allow only signed queries `z += ±B x` and `y_i += ±A_i z`, with one connector,
read-only x, private query scratch restored before return, and no other data
operations. Treat the maps as free formal operators. At an A_i query, write
z=z_0+t Bx. Final dirt independence forces the signed coefficient sum on A_i z_0
to vanish, while correctness requires the signed sum of the corresponding t's
to be one. Therefore there must be at least two A_i queries for every output.
At least one B query is needed for a nonzero signal; restoration of z requires
at least one opposite B query. Hence every admissible word uses at least
`2k+2` queries. The construction attains it, including under arbitrary positive
per-operator query prices. This does not bound models admitting combined-output
queries, extra connectors, direct A_i B queries, or other linear operations.

The finite regression exhausts all 9,331 signed star words of lengths zero
through five for k=2. Their failure supports the implementation of the universal
argument above; enumeration is not the proof of that argument.

## Recursive lowering and exact cost

Factor lists are in **application order**: `[B0,B1,A0]` means A0 B1 B0.
Each product is lowered with PR628's balanced binary dirty commutator, using
one distinct array per active recursion level. All child calls operate on
**full length-L rows**. Batching never divides their charged volume by k.
Let C(F;L,w) be the complete cost of an additive product child, with both signs
bounded by the same price and with its heads returned to the documented entry
positions. For a leaf j let c_j include arithmetic, source and coefficient
access, target update, phase/descriptor work, routing and head returns. Then

```
C([j]) = c_j + dispatch_leaf
C(F_right followed by F_left)
  = 2 C(F_right) + 2 C(F_left) + dispatch_node
C_batch = 2 C(B) + 2 sum_i C(A_i) + dispatch_batch.
```

No child or inverse is free. The unbatched *same-root-split* comparator costs
`2k C(B) + 2 sum C(A_i) + dispatch_separate`, so the recursive saving is
`2(k-1) C(B)` before comparing dispatch and layout overhead. If source access,
layout or external frames differ, use their actual c_j; the operation count
alone does not imply a bit-cost improvement.

For an unweighted balanced product of n factors, L(1)=1 and
L(n)=2L(floor(n/2))+2L(ceil(n/2)). Writing p=2^floor(log2 n), induction gives
L(n)=p(3n-2p). Scratch is ceil(log2 n). The batch's dirty requirement is
`1 + max(ceil(log2 |B|), max_i ceil(log2 |A_i|))`, in addition to its source
and k output arrays. Child scratch is reused only after return; all sibling
outputs remain excluded. There is no clean length-L array.

For seed 58, k=2+(58 mod 5)=5, |B|=1+(58 mod 17)=8, and |A_i|=i:

| Schedule | Complete leaf calls | Dirty arrays |
|---|---:|---:|
| Separate products, each split into the common B and its A_i | 758 | 4 |
| Separate balanced products of lengths 9,10,11,12,13 | 680 | 4 |
| Shared B batch | 246 | 4 |

A separate integer DP checks the minimum over all ordered **binary** splits
for n=1,...,64 and agrees with the balanced counts. No all-arity optimum is
asserted; PR673, PR730 and PR822 investigate different tree/allocation classes.
The certificate lists exact per-factor multiplicities and three positive
nonuniform price assignments for every sampled batch, rather than crediting
only the convenient common-factor calls.

### Fully charged dense reference realization

There is also a simple, deliberately slow implementation of each matrix leaf.
For every target entry, form the dot product in one scalar accumulator, then
add/subtract it to the target. All matrix coefficients are read-only. The
source and target rows are distinct. The certificate records, for each schedule
on identical 3-by-3 inputs and the same role layout:

- N L² coefficient reads and N L² source reads;
- N L target read/write updates;
- N L² multiplications, N L(L+1) additions (including zero-initialized sums),
  and one sign negation per negative target update;
- literal one-tape head travel, measured in word slots, including returning
  to slot zero after **every** primitive call;
- coefficient storage, data storage and every emitted instruction record;
- array-length/role-alias checks and the explicit preflight matrix-row and
  coefficient-alias checks (N L and N R L respectively, for R live roles).

The tape layout puts all mutable rows first and the coefficient matrices
second. Within a dot product it visits coefficient then source for each term,
then the destination, and returns home at leaf end. The head-travel sum is
`sum |next_position-current_position|` for that literal trace. Coefficients and
source entries must be loaded into a constant number of scalar arithmetic
ports. This reference makes no locality or free-gather assumption.

For word size w, multiply this travel by w, add O(w) per load/store, the listed
counts times integer multiplication/addition costs M(w), A(w), and charge
O(N(log(number of roles)+log(number of factors))) instruction/control bits
and O(N) generator records. Also charge the listed descriptor/alias preflight
comparisons at the required index/pointer bit width; they are not arithmetic
leaf calls. This invoice describes the reference algorithm, not CPython
interpreter wall time. Input coefficient preparation is additional and
paid once for each distinct factor, equally available to both comparators.
The seed matrices are already supplied exact integers; a cyclic-inverse or
phase oracle would need its own preparation and validation bill.

For integer matrices of row norm at most K=L H, input magnitude at most D,
and N leaf calls, exact states are bounded by D(1+K)^N. Thus signed word length
`2 + ceil(log2(max(1,D))) + N ceil(log2(1+K))` suffices. The same conservative
word length from the larger comparator can be used for all schedules. This
is a finite dense-matrix realization, not an efficient common-label/tape
compiler for the selected supplier.

## Rounded leaves: restoration and accuracy are different

A deterministic grid leaf `target += F(source)` can be inverted exactly by
subtracting the same computed increment. Literal inverse words then restore
all source/borrowed arrays even when F is nonlinear from rounding, provided
read-only data and all excluded arrays are respected. B's paired calls see
the same source and deeper dirt: intervening A_i calls restore their source
z and private scratch. The final A_i calls use the restored connector.

The target increment need not be the exact, dirt-independent A_i Bx in this
case. For example floor((z+1)/2)-floor(z/2) depends on dirty z. We include this
negative control and make no substitution of approximate linearity for exact
linearity in the identity or query minimum above.

For a separate accuracy bound, suppose the ideal primitive operators have
infinity norm at most K and each rounded primitive's increment error is at
most u, uniformly on the actual trajectory. A full ideal shear has norm at
most 1+K. Telescoping the N perturbed shears gives

```
error <= u sum_(j=0)^(N-1) (1+K)^j <= N u (1+K)^(N-1).
```

For u=2^-w, `w >= p + ceil(log2 N) + (N-1)ceil(log2(1+K))` suffices for error
at most 2^-p. Actual state magnitudes are bounded by (D+1)(2+K)^N for u<=1,
which must also be included in integer-word storage. Coefficient perturbation
and preparation errors must be added separately; source-dependent error
bounds require checking the resulting magnitude bound, not silently using
this uniform-u premise. Twenty-seven exact grid experiments compare a floor
rounding interpreter with independent dense ideal products and check the full
error bound and exact all-role reversal.

## Verification scope, provenance and stopping rule

[CLAIM.md](CLAIM.md) records the OS seed, three candidates, overlap review and
local claim. Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
[Source pins](SOURCES.json) retain the original proof, implementation reference
and notice from PR628 at `0768f97d06c623b8211e651543c66135796b62bf`, with Git
blob and SHA256 hashes. Those source files are references; their cyclic-scan
implementation is not imported or asserted to have been revalidated here.

The test domain is fixed: common lengths 1..16, fanout 1..8 with left lengths
1..k; dense domains/fixtures listed in verify.py; and the seed-selected example.
Random dense inputs use Python Random(58); the track draw used OS randomness.
This is a bounded constructive check, not a search for a new multiplication
bound or an impossibility claim outside the stated star-query model.

The selected #799/#589 result at this base is κ=1661634653669567/10^18. Its
native calls are not assumed to have the shared source, coefficient, frame,
volume and exclusivity contract used here. No current invoice term is removed.
Existing owner obligations, ordinary child widths, read-only source access,
common-label realization, precision, layout and all-size analytic transfer
remain unresolved for any supplier application. This package changes no
selected certificate or upstream manuscript. See [NOTICE.md](NOTICE.md) for
attribution and substantial AI assistance.
