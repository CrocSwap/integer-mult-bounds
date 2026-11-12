# Bound the retimed Type A stage-8 host

**NO VERIFIED GAIN.** Keep the exact [#7404](https://github.com/CrocSwap/integer-mult-bounds/pull/7404)
retiming at the first Type A port, demote QUERYs 1580 and 1659 to unit ADDs,
and request retirement of the central phase on productive roots 0 and 18.
The required stage-8 host cannot fit four ingress and four egress fields
with fixed phase-even adapters and feedthrough on the compared sectors.
At central sign +1, the body difference has determinant 16 on the original
four-role block. The central sign difference has 320 entries outside that
block, including (8,1) = −2.

The comparison uses [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
at aaeec8c0acf01e99a5f331ef363a698d9c084ace and the signed
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
caller at 07a76c5e2738882c0cb322278e56f6cae3c9885d. The strongest reproduced
comparable exponent saving remains 0.00364665195644.

The one-port optimistic price was positive before the support check,
below 0.04270044187346692 raw. A 96-port relaxation assuming compatibility
is below 4.099242419852824 raw. The verified exclusion is for this exact
port, one J clock and one root pair. See [proof and scope](PROOF.md).

From a clean checkout with CPython 3.12 and assertions, run

    python3.12 -I -B research/p104-retimed-type-a-stage8-host-bound/replay.py

The replay binds the exact public inputs and reproduces the directed
price, forward matrices and independent reverse-covector receipt.
It also checks the physical sign witnesses and rejects altered caller
bytes. See [verification](VERIFICATION.md) and [provenance](PROVENANCE.json).

## Open next questions

Can an enlarged or phase-dependent host implement both aggregate reads,
the scatter and the dirty-input return contract under the same paid bill?
Start with one specified extra ingress or egress path at clock 1423.
Check its support, chronological availability and unchanged returns,
then price all new fields and adapters. Other root pairs, other clocks,
odd feedthrough and different skeletons were outside the test.

## Credit

Clear1nsight's [#7404](https://github.com/CrocSwap/integer-mult-bounds/pull/7404)
at aadd1de3e520cfd1e5b062729bd76f543dc879f4 supplies the exact 14-idle
retiming and the original carrier evidence. The retained signed caller
and native comparator are credited to Rohan Arun's
[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) and
Clear1nsight's [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334).
[#7401](https://github.com/CrocSwap/integer-mult-bounds/pull/7401) supplies
the fixed-skeleton two-root comparison, and
[#7344](https://github.com/CrocSwap/integer-mult-bounds/pull/7344) the
retained-J phase capacity question.
[#7360](https://github.com/CrocSwap/integer-mult-bounds/pull/7360)
supplies the physical character witness method, and
[#7362](https://github.com/CrocSwap/integer-mult-bounds/pull/7362)
the exact price receipt. OpenAI Codex and subagents materially assisted
the proof, implementation and independent verification. Apache-2.0.
