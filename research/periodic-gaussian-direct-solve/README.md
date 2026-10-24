# A certified direct consumer for the periodic Gaussian reference

**Constructive finite-source result with an all-input error proof; no new
kappa.** The complete inverse action for the original
`Reference(384,1,2,4,18,320)` can use a sparse direct factorization instead of
119 whole-period updates. It retains all 385 rows, the true periodic entries,
hole 192, arbitrary signed complex inputs, and the original 33-bit input and
output grid. The internal factor and solve grid has 48 fractional bits.

The solve uses **1,398 integer products**, compared with **731,136** in the
weighted recurrence of [PR #5216](https://github.com/CrocSwap/integer-mult-bounds/pull/5216).
Preparation adds 319 factor products, 349 factor divisions and 668 exact
factor-certificate products. Both methods retain the original coefficient
producer. Its cost is substantial and is not a free input oracle.
The new solve performs 2,310 component divisions/truncations, including final
rounding back to the source grid. These product counts are not a comparison
of total bit operations. [TIMING.json](TIMING.json) records local sequential
wall-clock trials, including direct factor preparation and reuse separately.

This is a host-array consumer with a verified finite source. It is not a
physical tape implementation, a production-parameter theorem, native supplier
admission or a new multiplication exponent. The selected kappa remains
`60403/20000000`.

## Predecessors and changed contract

Jose Manuel supplied the immutable rational Reference. JoyboyBrian's
[PR #5159](https://github.com/CrocSwap/integer-mult-bounds/pull/5159) supplies the
complete periodic coefficient table, all-output recurrence, source gap,
input ownership and analytic perturbation budget. His PR #5216 reduces the
recurrence from 275 to 119 updates. Both are retained and replayed here.

Dugongue's [PR #4554](https://github.com/CrocSwap/integer-mult-bounds/pull/4554)
already gives a native band/Woodbury construction. Ryanson Jonathan's
[band audit](../pr4554-banded-inverse-check/README.md) checks that construction.
Classical Gaussian elimination, diagonal dominance and periodic band solving
are not new results of this package. The existing `band_solve` executable
requires `||A-I||_infinity<=1/4`; its proof starts with a small-norm hypothesis.
The actual source here has a funded gap about 0.06334, and its stored
off-diagonal row norm exceeds one half. That executable contract does not
admit this fixture. No check in that implementation is weakened.

The new result is an actual source-compatible direct consumer with a checked
factor residual. The certificate replaces the small-norm premise at this
boundary. The sparse kernel retains cyclic fill and checks every original
stored coefficient. It does not discard corner entries to claim a band.
All predecessor files and source pins remain unchanged.

## Certificate theorem

Use the maximum over coordinates of `|Re z|+|Im z|`. Let the exact source
be `H=I+A`, where `A` is real, nonnegative, has zero diagonal, and its row
sums are at most `1-d`, with `d>0`. Downward coefficient rounding to grid
`2^-P` gives `Hhat=I+Ahat`, with the same row bound and

```text
||H-Hhat|| <= delta = m 2^-P,
```

where `m` bounds the number of stored off-diagonal entries per row. The
original producer proves these relations for its supplied source. The
verifier checks its bytes, literal support and original rational entries.

Let the stored real factors be unit lower triangular `L` and upper
triangular `U` with positive diagonal. No claim about their quality is
assumed from the elimination algorithm. Multiply their sparse rows exactly
and check the coefficient residual

```text
eta = ||LU-Hhat|| < d.
```

The checker includes every nonzero product and every original input entry.
Let `l=||L||`, `v=||U||`, `w=max_i U_ii` and `h=2^-b`, where `b>=P` is the
internal factor grid. These constants are computed with exact integers and
rational arithmetic. In this package `P=33`, `b=48` and `m=8`.

Row diagonal dominance gives `||H^-1||,||Hhat^-1|| <= 1/d`. For example,
choose a coordinate of maximum complex-l1 norm and apply the triangle
inequality to that row. The same argument, with row perturbation at most
`eta`, gives

```text
||(LU)^-1|| <= 1/(d-eta).
```

Let `u` be an arbitrary input on the source grid with norm at most `Y`.
Forward and backward substitution accumulate each dot product exactly and
round the solved component once toward zero. Thus their literal outputs
`z,y` satisfy

```text
Lz = u + e_f,       ||e_f|| <= 2h,
Uy = z + e_b,       ||e_b|| <= 2wh.
```

There are two real components per coordinate. The second residual includes
the diagonal multiplier. Consequently

```text
LUy = u + e_f + L e_b,
rounding = 2h(1+lw),
||y|| <= B = (Y+rounding)/(d-eta).
```

Also `L^-1=U(LU)^-1`, so
`||z|| <= v(Y+2h)/(d-eta)`. These bounds apply to the full solve and all
stored coordinates. They also bound each partial dot product by the row
absolute sum times the coordinate bound. The kernel checks its integer
word limit and these coordinate limits during execution. Preparation also
checks the uniform accumulator bound
`2^(2b) max(Y+(l-1)Z, Z+vB, Y, Z, B, 1) < 2^width`, where
`Z=v(Y+2h)/(d-eta)`. Thus every allowed input fits the accepted solve word
limit; input-dependent overflow is not hidden in the theorem.

Now compare the computed output with the original source solution:

```text
||y-H^-1 u|| <= ((delta+eta)B+rounding)/d.
```

The final two components are truncated to the original `P`-bit grid, adding
at most `2*2^-P`. Preparation accepts only when the sum is at most
`2^(-t)/2`. This proves the requested source error for **every** admitted
input, not only the finite test vectors. If the inherited analytic matrix
has reference error `E<d`, its separate funded term is
`Y E/[d(d-E)]`. The literal fixture meets the combined `2^-20` target.
The analytic source theorem is inherited, not proved again here.

The algorithm may reject a different matrix, precision or word limit. The
theorem certifies every accepted unchanged `Prepared` object returned by
`prepare`; an arbitrary caller-constructed object is outside that contract.
The general certificate does not assert that preparation succeeds or stays
sparse for every periodic family.

## Complete preparation, solve and storage

Preparation calls the unchanged Reference producer and stores all 3,072
original off-diagonal records, including quantized zeros. The 3,457 source
entry requests, 384 rational weight records, four kernel values and retained
pi intervals remain paid source setup. The original interval precision and
large rational coefficients are not replaced by floating approximations.
The imported source modules and their caches remain live during verification.

Elimination retains a column-to-row index for active entries. It visits each
actual nonzero column entry and updates every surviving pivot-row entry.
Zero integer entries can be omitted after their rounding and update have
been paid. The exact residual checker catches any omitted nonzero effect.
For this fixture the factors contain 349 lower and 735 upper records. The
active elimination coefficient count peaks at 1,084. This count excludes
copies, index sets and original source storage. A conservative setup storage
allowance is the original table and source caches, four copies of the factor
record set, column/row indices and `O(N)` scalar/control slots. Certificate
row scratch has at most nine index/value records. These are logical records,
not a measured Python heap or random-access-free tape bound.

Each solve borrows an immutable 770-component input. It owns two
770-component work vectors and returns a new 770-component output. The final
output coexists with the scratch vectors until cleanup. The bill includes
1,398 products and subtractions, 1,540 forward/backward component divisions,
770 final grid truncations, input scalings, accumulator loads, solution writes,
output copying, coordinate-range checks and 1,540 scratch-slot clears.
128-bit magnitude limits are checked for factor and solve arithmetic. Exact
certificate inequalities use host integer/rational arithmetic separately.

The factor table is retained for reuse. Scratch is cleared on return or
exception. This means logical slot clearing; it is not allocator zeroization.
The independent verifier also retains original coefficients, both outputs and
its exact residual state. Verification storage is additional to consumer
storage. Source preparation dominates these small local runs; a large reuse
speedup is not an equal speedup of cold source generation.

## Verification

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/periodic-gaussian-direct-solve
```

Both normal and optimized commands must print
`PASS_PERIODIC_GAUSSIAN_DIRECT_SOLVE products=1398 previous_products=731136 no_new_kappa`,
then the registered package pass marker. Normal execution writes no files.
`--record PATH` regenerates the exact receipt. `--timing PATH` records local
wall-clock trials separately. `--small` runs the independent small oracle and
controls without source preparation.

The full check regenerates the original table, reads all 148,225 original
matrix entries and checks the returned residual against those rational
entries. It also replays the unchanged 119-update consumer. An independent
pivoted rational Gaussian solver checks 105 complex right-hand sides on 35
small matrices. Controls reject mutable or malformed input, out-of-range
values, small words, unfunded precision, negative/duplicate coefficients,
corrupt factors, factor order and a factorization with the real periodic
entries removed. The hole output and borrowed input are retained exactly.
The result receipt binds the package source and metadata hashes.

## Open next questions

Bind this factor owner and its 33-bit input/output contract to one admitted
physical caller. Charge coefficient preparation, ordered tape delivery,
retained factors and restoration. The next production-family proof must
bound fill, factor certificate success, word widths and complete costs across
its actual parameters. A finite source speedup does not supply that proof.

## Credit and source pins

Prepared for Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Credit Jose Manuel, Dugongue, JoyboyBrian and Ryanson Jonathan as specified
above. Their source notices retain Vlado Vojdanovski, Jeremy Kothe, Cinna Davis,
Mason Hale, James Reed and the earlier Gaussian/precision lineage. No
independent human or proof-kernel review is claimed. [SOURCES.json](SOURCES.json)
pins every consumed source and the material proof provenance to main
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority revision 7.
