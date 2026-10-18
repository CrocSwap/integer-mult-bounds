# Rank-one connector-map change across a source update

**Result type:** a finite, exactly replayed construction family with a complete
local XOR invoice. It is not a selected-supplier admission or a new conditional
integer-multiplication bound.

## Assignment and scope

- Track: `recursive-interfaces`; accepted OS seed:
  `0e9d3469c47e870c84c141c97ae63540`.
- Catalogue task: `persistent-boundary`, priority revision 3, refined to a
  source update followed by a rank-one change to the connector map.
- Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
- Selected-record SHA-256:
  `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Claim: see [CLAIM.md](CLAIM.md) for the local scoped claim and its live-board
  status.

`SOURCES.json` pins the selected record, its review, exact source manifest,
assembled certificate, `Makefile` reproduction rule and selected verifier,
along with the nearest persistent-connector predecessor packages and task
catalogue.

The task asks whether two consecutive calls can remove restoration work that a
later call would otherwise reconstruct. This instance makes both calls
observable at their proper points. The first call uses `B`; after the source
changes, a rank-one delta `R` changes the connector to `B' = B + R`. The first
output is kept, the changed source feeds the second output, and the dirty
connector is restored exactly at the pair boundary.

## Construction and evidence

For every `n >= 2` over F2, the proof uses `B = J_n`, `R = E_00`,
`B' = B + R`, and `C = e_0 + e_1`. Since `BC = 0`, after mutating
`x' = x + C u`, the identity

```text
z0 + B x + R x' = z0 + (B + R) x'
```

lets the shared dirty connector move from the first call's state directly to
the second call's state. The exact call schedule, entry/exit contract and
derivation are in [PROOF.md](PROOF.md). More generally, for any two call maps
`B1,B2`, the required connector patch is exactly
`(B1+B2)x' + B1 C u`; the verifier checks this identity on all 2x2 map pairs.
The same construction extends to every nonzero even-weight `C` by taking a
unit rank-one `R=E_(i,j)` with `C_j=1`; the executable all-state census uses the
canonical representative above.

The verifier includes two exact invoices. In the direct matrix-entry alphabet,
the restored-call baseline costs `4 n^2 + 4 n`, while the pair costs
`2 n^2 + 4 n + 2`; at `n=4`, that is `80 -> 50`. Since `J_n` has a shared
parity, it also gives both schedules one clean scratch bit `t` and charges its
full common supply/release cost `p_t`. Even giving the baseline that parity
across the two calls while it still restores the connector, the invoice is
`10n+4+p_t` versus `8n+4+p_t`, saving `2n` (`44+p_t -> 36+p_t` at `n=4`).
Strict independent calls cost `12n+4+p_t`, saving `4n`. All source updates,
readouts, parity gates, map-delta gates and scratch restoration are counted.
For another complete-call tariff, the pair saves `c_B+c_B' - c_patch - Delta_I`;
`Delta_I` includes added setup, interface, dispatch, routing, hosting or
restoration cost. The matrix-entry bills are not claims of minimum linear
circuit complexity.

The verifier checks the general transition identity on all 32,768 choices of
two 2x2 maps, source-update vector and dirty inputs, and checks the explicit
even-`C`/unit-`R` family on 444,800 small dirty transition states. It also checks the
complete dirty-state map and inverse at every state for `n=2..5` (2,236,928
arbitrary `x,u,z,y1,y2` inputs per schedule; the factored version has its
declared clean scratch `t=0`), and recalculates the bills. Four controls fail:
omit the rank-one patch, use its stale pre-mutation source, close with `B`
instead of `B'`, or omit `B1 C u` from the general correction when `B1 C` is
nonzero. It uses only the standard library.

```sh
python3 -B research/rank-one-connector-delta-seed0e9d/verify.py
python3 scripts/research_package.py --package research/rank-one-connector-delta-seed0e9d --check-only
python3.12 scripts/research_package.py --package research/rank-one-connector-delta-seed0e9d
```

The verifier ends with `PASS_RANK_ONE_CONNECTOR_DELTA` and reports the exact
state, matrix, gate-column and invoice counts. The registered runner ends with
`PASS_REGISTERED_RESEARCH_PACKAGE research/rank-one-connector-delta-seed0e9d outcome=partial`.

The local interpreter is Python 3.14.7; the verifier and metadata check passed
there. The registered replay command enforces Python 3.12, which is unavailable
locally; CI is the remaining 3.12 replay.

## Relation to prior work and limits

Woklerx's [mutable-source persistent-connector package](https://github.com/CrocSwap/integer-mult-bounds/tree/0b1cccf86e2f5132ed286a26ef0a681a495740ea/research/mutable-source-persistent-connector),
which follows Ross Richardson's dirty-connector work in [PR #934](https://github.com/CrocSwap/integer-mult-bounds/pull/934),
uses the same connector map on both calls and pays an adapter `B C u`. Here
`B C=0`, but the second map changes by `R`; the correction `R x'` depends on
the current source and is not the prior source-independent `D u` adapter.
[Woklerx's connector-delivery-cut result](https://github.com/CrocSwap/integer-mult-bounds/commit/7c573bc769798ce4e336fd5be630060bd9d69a71)
proves an exact weighted persistence optimum for read-only sources and fixed
maps under sequential output-delivery cuts. This construction changes the
source and changes its map by rank one at the pair boundary, outside that
fixed-map contract. [PR #1524](https://github.com/CrocSwap/integer-mult-bounds/pull/1524)
prices unrestricted words for the five-source mutable-source connector while
retaining its common query map; this result changes the map itself by `R`.
[Navinor's PR #1155](https://github.com/CrocSwap/integer-mult-bounds/pull/1155)
defers a restoration across a read-free batch and requires a composable
restoration family; this schedule retains the first output read and uses an
explicit rank-one connector transition. [Hanson Sun's PR #1522](https://github.com/CrocSwap/integer-mult-bounds/pull/1522)
shares source queries across outputs while the connector-map interface stays
fixed. Discussion #1694 / [Cinna Davis's PR #1707](https://github.com/CrocSwap/integer-mult-bounds/pull/1707)
shares a common output-map evaluation across multiple targets. Those are
adjacent interface optimizations with different changed hypotheses.

No selected owner schedule instantiates this `B, C, R` pattern. The map-update
and source-update expenses have not been assigned a selected recursive tariff;
there is no supplier admission, all-size assembly, precision transfer, or new
`kappa`. The fast `make selected-record-check` passes; the full selected replay
`make frontier1094-verify` was not run because this package does not alter the
selected construction. The local gate count is evidence for this finite linear
interface only.

## Open next questions

Find a concrete selected-call pair where the source changes by `C u`,
`B_old C=0`, and `B_new-B_old` has a cheaper exact implementation than
`c_B_old+c_B_new`. First extract both complete typed contracts from one pinned
supplier source, then price every map call, source read, frame transition,
scratch preparation, restoration, dispatch and host operation. The blocker is
an identified selected supplier caller satisfying those equations.

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance in derivation,
exact replay, cost accounting and prose. The prior dirty-connector contract and
source-mutation identity are credited to Ross Richardson and Woklerx; adjacent
work is credited in the overlap references above. Apache-2.0.
