# Shared midpoint recharts on changed P104 helper paths

**NO VERIFIED GAIN.** Exact Δκ = 0, a 0% change from the independently
reproduced conditional κ = `0.00364665195644` on exact
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
`aaeec8c0acf01e99a5f331ef363a698d9c084ace` with signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.

A common intermediate chart could reprice two paid MOVE paths around
a literal ADD while preserving their endpoints and paid clocks. Two
literal walks exhaust ten frozen changed-role anchors. The moving
helper always has the required MOVE pair. Every other operand has
an adjacent ADD on at least one side, so no anchor has the required
four-MOVE topology. [Exact contact receipt](receipts/R108-AGREEMENT.json).

Two of those ADDs share role 452 and form one genuine closed
three-role component with roles 1250 and 532 on chart 746. Its sole
strictly positive actual price uses a common rank-four chart. The
entrance union has rank five and the exit intersection rank six, so
no rank-four chart can work. An additional same-six-leg check
excludes using two distinct coframes by moving either of role 452's
paid clocks between the two ADDs. No scoped case remains unresolved.
[Exact geometry and chronology receipt](receipts/R111-AGREEMENT.json).

## Replay

From a clean checkout, use CPython 3.12 with assertions enabled:

```sh
python3.12 -I -B research/p104-changed-shared-midpoint-bound/replay.py
```

The standard-library replay authenticates the exact native word and
published predecessor receipts, regenerates the ten-anchor stock and
both contact walks, reconstructs the closed component's complete
paid delta, and checks the exact GF(2) spans and chronology witnesses.
It rejects modified stock and price inputs. Use `--out fresh-directory`
to retain all nine receipts. It needs no Git metadata, network, external
dependency root or previous temporary state.
[Provenance](PROVENANCE.json) · [Path-keyed hashes](LOCAL-PINS.json) ·
[Proof and full price](PROOF.md).

## Open next questions

Can a different paid itinerary create a coframe of a feasible rank
while leaving enough margin for the complete changed bill? Start
with one explicit route change and price its paid calls, routing,
ownership, restoration, precision and tape before testing signed
arbitrary-input action. This package closes the ten exact pairs,
one exact common-chart component, and the stated fixed-six-leg
two-coframe chronology. Other components, changed outer charts,
additional legs and moved ADD clocks remain outside this scope.

## Credit

[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
supplies the exact native word and comparator, and
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
the signed caller. [#7358](https://github.com/CrocSwap/integer-mult-bounds/pull/7358)
and [#7361](https://github.com/CrocSwap/integer-mult-bounds/pull/7361)
supply the four-MOVE and closed-component rechart methods on inherited
roles. Their changed-role guards exclude this component.
[#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338)
previously recorded the same chart-746 block for a different
compensated paid-fusion test. [#7365](https://github.com/CrocSwap/integer-mult-bounds/pull/7365)
supplies the changed-role anchor and price stock.
[#7319](https://github.com/CrocSwap/integer-mult-bounds/pull/7319)
supplies the helper census, [#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362)
the complete stock receipt and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
the exact tariff. OpenAI Codex and subagents materially assisted
the proof, implementation, independent replay and packaging.
