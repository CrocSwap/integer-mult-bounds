# Adjacent ADD/SCALE exchange bound for the retained P104 word

**NO VERIFIED GAIN. Exact conditional κ change 0%.** On the exact
[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
word, a single adjacent mixed ADD/SCALE exchange cannot improve the
paid signed price in the tested scope. The 22 owned SCALEs supply
44 normalized neighboring positions. The census resolves all 44.
Three have other operation types, 13 have disjoint roles, 21 have the
same chart or a unit scale, and seven are legal after conjugation and
the owned-route checks. All seven worsen the complete price.

## Scope and exact price

Normalize adjacency by ignoring only MOVE events. Keep both scalar
operation charts, the original scaled owned role and its lifetime,
all other scalar contacts, caller and productive endpoints fixed.
Allow one shared owned-role itinerary to change. The revised ADD
coefficient must be nonzero, have denominator supported on 2, 3 and 5,
and satisfy the inherited magnitude gate. For ADD from s to d and
SCALE on r by λ, the signed exponent is
`e = [r = d] − [r = s]`. Moving SCALE before ADD multiplies the ADD
coefficient by λ to the power e. Moving it after ADD uses the
inverse factor. The primary and independent engines check the
reversed linear action on both basis inputs.

Let the four local chart contacts be L, A, B and R. The old path is
L→A→B→R and the exchanged path is L→B→A→R. Both old exterior edges
and the middle edge are authenticated against the literal MOVEs.
New nonidentity edges must be strictly nested. The middle tariff
is unchanged by reversing its owned direction. Reprice the two
exterior edges once each on the full 17-copy signed invoice.

The best legal pair is at clocks 39791 and 39793 on owned role 1503.
Its old exterior ranks are (0,5), and its new ranks are (1,6).
The new signed ADD coefficient is 2. The exact paid old-minus-new
histogram is `{1: -17, 5: +17, 6: -17}`. The moment change is
`17(H₅ − 1 − H₆)`, where Hᵣ = r raised to 1−κ at the pinned
old crossing upper. It is about −33.83316615340068 raw units.
Across the seven cases, the only signed deltas are negative
multiples of a single tariff or the sums `17(H5−H1−H6)` and
`17(H4−H2−H6)`. All are strictly negative for `0 ≤ κ < 1`,
including throughout the incumbent crossing interval. Additional
ordinary or physical charges cannot make an exchange improve the
invoice. The independently reproduced comparable κ remains
0.003645669928698.

## Evidence and replay

The [primary price](receipts/primary/PRICE.json) is saved before
testing any changed pair. The [primary result](receipts/primary/SUPPORT.json)
records all slot dispositions and exact paid changes. The
[independent result](receipts/independent/RESULT.json) reconstructs
the full old caller bill, tests the exact local itineraries by
subspace inclusion and derives the reversed coefficient by solving
the two-coordinate action. Its tighter rational price intervals
are contained in the primary bounds. Controls test both scalar
orders and shared operand roles, reject a wrong sign and illegal
coefficients, and reproduce the pinned #7298 ADD/ADD result.

From a clean checkout with CPython 3.12 and assertions enabled:

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-adjacent-add-scale-exchange
python3.12 -B scripts/check_research_commit.py --package research/p104-adjacent-add-scale-exchange --check-modes --check-source-history
~~~

For a Git-free export run
`python3.12 -I -B research/p104-adjacent-add-scale-exchange/replay.py`.
[PROVENANCE.json](PROVENANCE.json) pins all six public source files
by exact commit, path, Git blob and SHA-256. [LOCAL-PINS.json](LOCAL-PINS.json)
pins the bundled files by relative path. Replay uses only the
standard library and does not require an existing checkout or
prior temporary state.

## Credit

[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) at
`ed090b57ed88f8859e5ff4643645099e6ba856ea` supplies the native
word and comparable price. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
at `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the signed
17-copy caller. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
at `c522451caf287bb3c16eaece72be4c263315dca4` supplies the exact
adjacent ADD/ADD precedent, price conventions and replay control.
[#7297](https://github.com/CrocSwap/integer-mult-bounds/pull/7297)
supplies the same-word fixed-chronology tariff comparison, and
[#5565](https://github.com/CrocSwap/integer-mult-bounds/pull/5565)
supplies the older commuting-contact precedent. OpenAI Codex and
subagents materially assisted.

## Open next questions

Can a different scalar chronology remove an observation without
adding a new exterior paid edge? One bounded test would price
consecutive public MOVEs across a provably silent intervening
scalar contact. This scope leaves such deletions, coupled exchanges,
changed charts and lifetime changes open. A price survivor still
needs exact signed forward and adjoint action, ownership,
restoration and complete precision and tape checks.
