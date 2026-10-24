# Independent review of arbitrary-source compact routing

Reviewed on 2026-10-08 against the original conditional address-movement
interface at CrocSwap/integer-mult-bounds commit
`bcd4ebde8692383539f8a48734e5fbf3a18a32c2`, the independently reviewed compact
control interface at `6e564879f51ae16f23d392e9e196c605f36d90df`, and the new
[routing argument](compact-arbitrary-source-routing.md). The executed producer
source is `ad6aafb2c1bd89e5b333bbcabd5460600f3f24737649ea2e7cd06986635bb297`.
This is a positive transfer review of a new movement argument, conditional on
the retained original equal-width chunk interchange. It does not certify an
unconditional multiplication algorithm, arbitrary computed-key sorting, or
the proposed bulk resampling replacement.

## Algebra and exceptional addresses

The active-mask qualification is necessary and sufficient for the stated
simultaneous shear. In the four-update identity, the packed control updates
are masked as well as the two target updates. On a good address each used
control digit avoids its top value and each target guard absorbs the bounded
signed displacement. Therefore one completed identity restores every control
digit and every target guard, while changing exactly its active target
parities. Sources outside the simultaneous target set are unchanged even if
they occupy another target's guard or an inactive selected position. Reading
those sources only between completed identities consequently gives the same
load and unload value. Dirty temporary fields are permitted.

Every actual modular rotation remains a bijection on all addresses: its
offset is determined by fields preceding its target. The inverse must run
the reversed operations and recompute each control from the current address.
Treating controls as their original values would be invalid on bad addresses.
The ideal shear fixes the bad predicate because it fixes guards and temporary
digits. Since the actual bijection agrees with it on the good set, both good
and bad sets are invariant. The independently inherited correction
`T(S^-1(current_address))` is therefore a permutation of precisely the bad
holes, with distinct destination keys. No good payload is corrected.

The bound `p*(2*2^-G+8*2^(G-K)) <= 5/(128*p^3)`, with
`G=4*ceil(log2(p))+6` and `K=64G`, is a local union bound for each invocation.
It does not require a small union over the entire recursive program. The
original two-piece rotation scans, amortized counters and fixed-tape radix
repair are retained. Descriptor/key arithmetic is charged once per complete
record or controlling fiber, not once per payload bit. Every fiber contains
at least one enlarged record, so at most M such charges occur. A
superpolynomial enlarged record absorbs the polynomial per-record work.

## Complete coordinate permutations and short coefficient records

For `n>=64G`, `H=ceil(n/K)*G<=n/32` makes all nine scratch fields disjoint.
The three matching cohorts avoid, respectively, reservoirs R0, R1 and R2.
The last cohort meets both of the first two disjoint reservoirs and hence
cannot meet the third. Original equal-H interchanges place the chosen
reservoir at the two front fields and the back field; reversing those
interchanges restores all original coordinate names. A matching swap is
the three directional XOR shears, each with disjoint complete source and
target sets. Residue classes use O(K) compact calls, and the final incomplete
guard segment uses O(K) exact elementary XORs. The two-involution cycle
factorization then implements any supplied coordinate permutation.

Elementary XORs do not use an unpaid arbitrary-prefix descriptor oracle.
Original width-one placements expose source and target at the first two
slots; the fixed four-quarter CNOT permutes complete suffix blocks, and the
placements are undone. This costs O(V) under the original block-counter
interface, regardless of record width. Thus the small-n fallback and the
incomplete-guard contribution are bounded by volume times a polylogarithm.
The full cost is `O(V*n^tau*polylog(p)+poly(p))`, with the explicit additive
term paying a polynomial-size supplied map and parameter preparation.

The short-record spectator step is essential for CRT and resampling.
For `n>3*ell`, the first, second and last disjoint ell-bit fields supply
three matching cohorts. Moving the unused field to the suffix enlarges a
record by `2^ell` without adding coordinates or stream volume. Each class
avoids its entire spectator field. Taking the third field at the actual
suffix makes the placements legal also when `3*ell<n<4*ell`; a consecutive
third front field could partially overlap its destination. The three-H
back reservoirs use the same suffix convention. For `n<=3*ell`, elementary
routing costs `O(V*n)<=O(V*p^(1-epsilon))<=O(V*p^tau)` for `epsilon>a`.
The intended full tensor volume absorbs the explicit polynomial setup term.
No newly proved router is used to construct its own paid spectator records.

## Independent finite controls

[review_arbitrary_routing.py](../code/review_arbitrary_routing.py) imports no
producer. It follows every original field placement and restoration,
three-shear matching, two-involution permutation, packed modular rotation,
current-control inverse and pointwise exceptional correction. The
[fresh run](../runs/20261008T023243Z-review-arbitrary-routing/) passed:

- All 4,280 payload-address permutations for every one of 152 permutations
  on two through five coordinate bits.
- 450 complete routing probes in nine larger and boundary layouts, including
  the `n=3*ell`, `3*ell+1`, `n=9H` and small-prefix fallback interfaces.
- 55,170 compact invocations, 110,340 actual inverse compositions, 36,461
  nontrivial corrections, 35,400 dirty-field invocations, 570 sources at
  inactive selected positions and 29,600 sources inside active guards.
- 428,712 original chunk interchanges and 112,024 elementary four-quarter
  CNOTs, with all named coordinates restored to their intended positions.

Seed 211, Python 3.14.4, one worker. The external timed run used 2.51 seconds
and 22,216 KiB peak RSS. Certificate SHA256:
`8de361d30dce8801a629d8613b5b8e6ea0149c634e8de4af19b7d01eb715cbbd`.
Reviewer source SHA256:
`c73182a04a6a08d75632aa74f122df2ac2dd7b6deb8dbcb5b42087cb553f94b1`.

Large probes are exact individual address operators, not exhaustive
`2^512`-record stream executions. Pointwise correction here is complemented
by the producer's complete small-stream stable-radix controls. Neither
finite experiment proves the all-size tape cost: the explicit scan, record
and density arguments above supply that transfer. The larger cases use
small G to exercise exceptional behavior rather than model an asymptotic
precision cutoff.

## Conclusion and reproduction

The arbitrary-source router has a valid conditional algebra, layout and
fixed-tape cost argument after the explicit active mask, suffix spectator
convention and additive polynomial setup qualifications. No remaining
structural counterexample was found. Its legitimate application is one
known coordinate permutation on a complete binary rectangle. Replacing d
separate Gaussian exposures additionally requires the independent analytic
and tape review of the proposed bulk microbox construction. No literature
novelty claim is made.

Run `python3 -B code/review_arbitrary_routing.py --output <fresh-path>` from
the topic directory. This uses only Python's standard library; the exact
executed command, versions, input identities, source digests, log location
and reservation release are retained in the run protocol. Original inputs
and the executed sources were not changed.
