# Minimal physical odd scale for the interleaved graph

The fixed graph in [PR #7726](https://github.com/CrocSwap/integer-mult-bounds/pull/7726)
can use native odd scale 176715 in place of 2650725. Keep binary height 21,
caller scale 2025, all public owners, paid routes, storage and root formats.
The conservative scalar-service rate falls from `2^30` to `2^26`.
No new kappa follows. The five framework interfaces remain conditional.

The graph hash is
`ba59d5db17c40185c8608a734ced10135d8c041e432c3840e9034868781c31a2`.
It has 1260 arbitrary public inputs, 860 helpers and 5810 paid routes.
The source already reports normalized minimum product grid 723824640.
That minimum is prior evidence. This result supplies the physical
substitution, sharp physical witnesses and complete finite cost comparison.
The ring criterion and per-call proof are from
[PR #7718](https://github.com/CrocSwap/integer-mult-bounds/pull/7718).

## Exact coefficient and physical contracts

Let `R=Z[i,1/2]`. At each literal pre-product, let c_j be the normalized
rational coefficient of independent owner j, including the scalar factor.
With current chart A and entrance chart B_j, the physical owner block is
`c_j A B_j^(-1)`. The inherited ordered chart maps and their inverses have
entries in R. They act on the complete root factor, including spectators
and absolute phase. This contract does not permit a coordinate projection.

An odd scale S works for all independent R-valued inputs exactly when
every `S*c_j` is in R. Sufficiency follows by matrix multiplication and
induction through each product and partial sum. For necessity, isolate
one independent owner. If its scaled block has all entries in R,
multiply on both sides by the inverse charts. Then `S*c_j I` has entries
in R. Thus the odd denominator of c_j divides S. The least common multiple
of all reduced odd denominators is the exact required odd scale.

The criterion does not determine a sufficient binary height or magnitude
bound. The construction below retains those source bounds. The universal
minimum uses independent inputs. A caller with restricted correlations
can have a different minimum.

The source grid `2650725*2^21` is sufficient. A separate integer coefficient
pass evaluates all 10483566 individual owner products in their actual
order. For starting grid Q and integer values v_i, the denominator lcm is
`Q/gcd(Q,v_1,v_2,...)`. The result is
`723824640=176715*2^12`, with `176715=3^3*5*7*11*17`.
The implementation retains height 21. It uses grid 370598215680.

## Sharp physical witnesses

Five separate Fraction column replays check coefficients without the
integer-grid evaluator. The chart interpreter then evaluates the actual
Gaussian-dyadic product components. In general, if `B_j e_0=x/2^b`, use
integer physical input x. Its normalized input is `2^b e_0`; this factor
must be included. The verifier checks the exact chart inverse and records
the complete integer input. For all five witnesses here, b=0 and x=e_0.
All other independent inputs are zero.

| Omitted prime | Input owner | Product node / donor | Coefficient | Chart and component at address 0 | Value at scale S/prime |
| --- | ---: | --- | --- | --- | --- |
| 3 | 1145 | 91875 / -1146 | -8/27 | chart 3, real 1 | -52360/3 |
| 5 | 1175 | 88808 / -1176 | 1/10 | chart 3, real 1 | 35343/10 |
| 7 | 21 | 101078 / 98960 | -16/7 | chart 757, imaginary -1/8 | 50490/7 |
| 11 | 651 | 88457 / -652 | 25/88 | chart 3, real 1 | 401625/88 |
| 17 | 1127 | 92252 / 92148 | -117/272 | chart 114, real -1/8 | 1216215/2176 |

Each value retains its omitted prime in the denominator. Extra binary
fractional bits cannot remove it. At scale 176715 every component of
each witness is dyadic. The coefficient valuations prove that every
admissible odd scale is divisible by 176715, including all three factors
of 3. Integer column controls also record the first inexact division at
scale `(176715/prime)*2^21` for each prime.

The checker retains three contract controls. A nonunit chart times three
can conceal 1/3. Correlated inputs can cancel `x/3-y/3`. The unitary phase
`(3+4i)/5` can add a denominator of five. These examples explain the stated
hypotheses; they are outside the inherited Gaussian-dyadic chart contract.

## Each invocation and the root grid

At the smaller scale, exact replay checks all 1260 public endpoints and
all 10483566 separate products. Independent helper endpoints are identities;
the source main map is unchanged. The completed map is dyadic before the
extra scale, so endpoint unscaling is exact. The signed caller receipt is
recomputed and compared in full. Its scale 2025 and height nine are retained.

Use the retained [common-root proof](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/odd-native-common-grid/PROOF.md).
Each invocation scales its actual entrance, runs its exact word and
unscales its completed endpoint. Completion removes only the extra debt
relative to that entrance. It does not reset inherited debt or the common
physical root grid. The finite ideal recursion is defined before exact
simulation. No exact rounded-child oracle is introduced.

The odd scale is 15 times smaller; the binary allowance is unchanged.
The old positive path-mass and binary-height bounds therefore dominate
each unfinished context. Retain 339 context binary bits, 587 mass bits,
context constant 1174, fractional grid `2^(-p-D)`, signed width
`W=p+h+2D+3` and temporary width `W+26`. Retain compiler bound
`H=14806300000000000000`. Its repeated depth-guard check gives argument
bit length 14083, strictly below H. The retained envelope records the old
odd scale because it remains a conservative bound, not the new exact scale.

## Complete finite bill

The addressed schedule is replayed with the new grid. It retains 8335
numerical homes, one dummy, one guide and four independent guarded streams
per invocation. Inputs remain available until final installation. Every
retirement and guard restoration passes. A live-sender overwrite and a
partial payload clear are rejected. This finite fixture has four addressed
cells per home; the inherited tape laws supply whole-extent behavior.

Every ordinary count and layout formula is compared with the source
receipt. All are unchanged except the scalar-step rate. The complete
16-call bill retains 123035648 scalar services, 47392 odd conversions,
96512 paid jobs and 17296 productive jobs. Each native call retains
1523290 reset services and 412390 selected transfer legs. Full movement,
setup, retirement, conversions, stock and padding remain charged.

The same 1108 distinct scalar and conversion factors now require at most
18 coefficient bits, in place of 22. All 6648 signed bit-service cases
pass. The retained formula `2^max(20,bits+8)` gives `2^26`, in place of
`2^30`. This is a factor of 16 reduction in one upper-bound coefficient.
It is not a measured runtime, memory, total-cost or cutoff reduction.
The paid/productive invoice and the conditional kappa are unchanged.

## Evidence boundary

The source constructor and physical/caller engines are retained byte for
byte. The coefficient witness pass and physical columns are new checks,
adapted from the credited prior verifier. This is author checking with
shared dependencies, not blind or independent human acceptance.

The full phase catalogue, native all-column lift, owned erasure, compiler
search, precision tape and analytic recovery retain their source evidence
and open obligations. Source binding does not prove these interfaces.
No historical suite, selected cold replay, Lean or Docker run is included.
The selected frontier is unchanged. RESULT.json contains the complete
finite receipt and negative controls.
