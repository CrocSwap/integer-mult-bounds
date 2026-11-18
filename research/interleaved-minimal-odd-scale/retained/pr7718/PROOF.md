# Physical substitution of the minimal odd scale

For the fixed graph in [PR #7717](https://github.com/CrocSwap/integer-mult-bounds/pull/7717),
replace native odd scale 2083725 with 11025 in each invocation. Keep
binary height 20, caller scale 2025, all paid/productive jobs, storage and
root formats unchanged. Under the same five framework interfaces, this
preserves the complete conditional application and lowers its conservative
scalar-service rate from `2^29` to `2^22`. It does not improve kappa.

The graph hash is
`5183479ecac34a1cb5c046f202e19d7161679265fe121b4a0af922fe344d8fc1`.
Its 1470 arbitrary public owners, 1070 helpers and 6054 paid routes are
unchanged. The minimum normalized product grid 90316800 was already
reported by the source. The new result is its physical odd-scale
substitution, sharp physical necessity and complete finite cost consequence.
The minimum-grid criterion and per-call clearing method are prior work;
[CREDITS.md](CREDITS.md) gives their sources.

## Coefficient lattice and physical charts

Let `R=Z[i,1/2]`, the ring of Gaussian numbers with binary denominators.
At a literal scalar-product site, let c_j be the normalized rational
coefficient of independent public owner j, including that product's
scalar factor. Let A be the current chart and B_j the entrance chart.
Under the retained native interface, the physical block on owner j is
`c_j A B_j^(-1)`. All these ordered chart maps and inverses have entries
in R on the same complete root factor, including spectators and absolute
phase. No active-coordinate projection occurs.

For a positive odd scale S, the product is in R for every independent
R-valued physical input exactly when every `S*c_j` is in R. For sufficiency,
each matrix block has entries in R. Thus each product and each partial
sum does too. Induction follows the actual operation order. For necessity,
independence isolates one owner block. If all its entries are in R,
multiplication by its inverse chart gives `S*c_j I` with entries in R.
Thus the odd part of the denominator of each reduced c_j must divide S.
The least common multiple of those odd parts is the exact minimum S.

This is an odd-divisibility criterion. A finite binary guard must still
bound powers of two, and a magnitude bound must still prevent overflow.
The criterion is valid for arbitrary R-valued inputs, including correlated
values at a particular call; independence is needed for the universal
minimum over the native contract. It does not assert that a restricted
correlated consumer cannot use a smaller scale.

The hypotheses are material. Multiplication by three is not invertible
over R and can conceal coefficient 1/3. Correlated inputs x=y can cancel
`x/3-y/3`. The unitary global phase `(3+4i)/5` introduces an odd denominator
although its modulus is one. The checker verifies these counterexamples.
They show why nonunit charts, input restrictions and arbitrary global
phases are outside the theorem. They are not reported as failures of the
selected Gaussian-dyadic contract.

## Exact certificate and sharp physical witnesses

A separate coefficient pass begins at the source's sufficient integer
grid. It computes every literal product in the published donor order.
If the resulting integer coefficient values are v_i and the starting
grid is Q, their exact denominator lcm is `Q/gcd(Q,v_1,v_2,...)`.
This is the credited grid criterion. It gives 90316800, with odd part
`11025=3^2*5^2*7^2` and binary height 13. All 9966426 products are covered.
We retain height 20 instead of using 13 in the physical substitution.

Three rational column replays check sharp coefficients without the
integer-grid evaluator. All named entrance charts are the empty chart,
so a literal physical unit basis vector at address zero is an admissible
input. Put all other public inputs at zero. The exact chart interpreter
then gives the following actual pre-product component under scale S/p.

| Omitted prime p | Input owner | Product node / donor | Normalized coefficient | Physical chart amplitude | Under-scaled physical value |
| --- | ---: | --- | --- | --- | --- |
| 3 | 1277 | 100783 / 93721 | 1927/576 | -1/8 at chart 118 | -2360575/1536 |
| 5 | 1207 | 98406 / 91748 | -1/25 | -1/4 at chart 324 | 441/20 |
| 7 | 278 | 97179 / 88440 | -20/147 | 1/2 at chart 595 | -750/7 |

Each value retains its omitted odd prime in the denominator. No number
of extra binary fractional bits can represent it. At scale 11025 the
same components are dyadic. Thus every admissible odd S is divisible by
11025. These witnesses use the fixed graph; they do not alter the paid
meeting at chart 118 or take any related construction search.

The integer single-column controls stop at their first inexact product.
For p=3, the numerator 38675660800 divided by three has remainder one.
For p=5, -462422016 divided by five has remainder four. For p=7,
-1572864000 divided by seven has remainder six. The receipt binds each
failure to its owner, donor and actual grid.

## Per-call substitution and nested precision

The implemented grid is `11025*2^20=11560550400`. A full replay checks all
1470 endpoints, every separate product and all addressed installations.
The independent helper returns are identities, and the source main map
is retained. Its completed endpoints are dyadic before scaling, so
unscaling by 11025 is exact. The caller retains its separate 2025 scale
and binary height nine; all 4192 events and 16 native occurrences match
the source receipt.

Use the existing [common-root induction](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/odd-native-common-grid/PROOF.md).
Each native invocation scales its own actual entrance, runs its exact
word and unscales its completed endpoint. An unfinished invocation adds
its exterior scalar debt. A completed endpoint removes only the extra
debt relative to its entrance; it does not reset inherited debt or the
physical root grid. The finite ideal recursion is defined before its
exact simulation. No exact rounded-child oracle is assumed.

The new odd scale is 189 times smaller. Its dyadic allowance is unchanged.
Consequently every positive path-mass and binary-height bound used in the
source application still dominates the new implementation, at each
unfinished context. Keep the source's conservative 338 binary bits,
588 mass bits and context constant 1176. Keep its signed width
`W=p+h+2D+3`, fractional grid `2^(-p-D)` and temporary width `W+26`.
The retained `H=14708600000000000000` still gives depth-guard argument
bit length 14083. The checker repeats that guard. All caller, native
spectator and compiler schedules stay unchanged.

This argument binds the smaller scale to the existing root proof.
It does not discharge the entire precision_tape assumption, prescribe
new external preprocessing, admit arbitrary early rounding, or change
the exact native and compiler interfaces.

## Complete finite cost consequence

The physical engine checks the new scale on the same owned-bank schedule.
There are 8999 numerical homes per native call, with the same dummy,
guide and four separately guarded streams. Every input snapshot survives
until final installation. Full retirement and guard restoration pass.
A live-sender overwrite and partial payload clear are rejected.
The four-address fixture checks storage operations; the inherited laws
supply arbitrary-width whole-extent behavior.

All ordinary counts and layout formulas are compared exactly with the
source receipt. They are unchanged. The complete 16-call caller retains 124816384 scalar
services and 54112 odd conversions. Each native invocation retains
1526938 resets and 414942 selected transfer legs.
There are still 100416 paid jobs and 20656 productive jobs.

The 796 distinct scalar/conversion factors now need at most 14 bits.
All 4776 signed bit-service cases pass. Under the retained service formula
`2^max(20,bits+8)`, the conservative rate falls from `2^29` to `2^22`.
Only that rate changes in the complete ordinary bill. Full-view movement,
guide setup/retirement, scalar conversions, held stock and padding remain
charged. This reduces one upper-bound coefficient by a factor of 128.
It is not a measured runtime, memory, total-cost or cutoff reduction.

The source's complete signed invoice and conditional kappa are unchanged.
No price or compiler search is repeated. The source phase catalogue,
all-column lift, owned erasure, compiler, fixed-tape law and analytic
recovery retain their stated evidence and limitations. No selected
frontier change, independent human acceptance, formal-kernel proof or
materialized all-size rounded multiplier is claimed.

## Verification boundary

Normal and optimized replay use unchanged source engines plus the new
coefficient/physical witness checks. The normalized minimum is not
counted again as a result. The source constructor is not imported.
Retained bytes and the graph hash bind the exact interface. Full native
catalogue and predecessor suites, selected cold replay, Lean and Docker
were not run. See RESULT.json for exact positive and failure evidence.
