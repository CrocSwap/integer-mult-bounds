# Bound lane-wise BIT IDLE regrouping

**κ change 0%.** Keep the exact #7001 paired BIT endpoint, all 36 old LOCAL calls and the productive targets. Allow arbitrary copy and port mixing, rectangular scalar contexts and separately charged IDLE masks that vary by lane. The complete optimistic raw target margin is strictly below **−8.16416603986435** at **10018846261809/2500000000000000**.

The [lane-wise proof](NONUNIFORM.md) ties the body saving to the head correction. If `K` is the greatest number of common masks between an opposite active stage pair and `e` is the total excess body incidence, the head correction has rank at least `444 + K − 5e`. Separating cross-half masks bounds their best compression credit, including every possible excess incidence. Directed arithmetic maximizes the relaxed price at `K = 28, e = 0`. Giving cross-mask credit without the corresponding head debit yields a positive false control. The [uniform case](PROOF.md) gives sharper rank bounds when a common mask spans all 111 lanes.

## Relation to earlier work

[#7160](https://github.com/CrocSwap/integer-mult-bounds/pull/7160) derives the original-body QUERY rank floor. [#7162](https://github.com/CrocSwap/integer-mult-bounds/pull/7162) varies LOCAL multiplicities on the 38-role model with whole-layer masks and their uniform 111-job tariffs. Here the 36 LOCALs are fixed. Mask incidence and rank are counted on the full 4,218 root coordinates, permitting nonuniform masks and arbitrary rectangular cross-port context. The new inequality charges the head cost of actual shared body lanes and bounds leakage at nonsaturated stages. [#7177](https://github.com/CrocSwap/integer-mult-bounds/pull/7177) changes the LOCAL operator itself, which is outside this proof.

## Clean replay

From a clean checkout, with CPython 3.12 and assertions enabled:

~~~sh
python3.12 -B scripts/research_package.py --package research/paired-bit-lanewise-idle-bound
~~~

The registered replay authenticates four exact in-tree sources from canonical commit e54523517d0f03e58352e647c403a5af3e525a57. It reconstructs the complete paid and productive histograms, verifies all 81 opposite-stage supports and 24 oblique and rectangular rank controls, evaluates the directed price and independently confirms the maximum with rational arithmetic. It compares three receipts byte for byte. A changed invoice byte and an image-only false sharing projector are rejected.

## Open next questions

Can a new paid operation carry different mask directions across its lanes under one concave charge, or couple head and body at a lower complete price? Start with two lanes and distinct masks. Specify the exact arbitrary-input signed action, charge its native, ordinary and tape costs, and show both lane returns. Such a changed primitive, changed productive stock and changed native operators remain open. This proof concerns the fixed formal and tariff model. A complete supplier or multiplication theorem is not asserted.

## Credit

Credit [#7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001), [#6726](https://github.com/CrocSwap/integer-mult-bounds/pull/6726), [#6834](https://github.com/CrocSwap/integer-mult-bounds/pull/6834) and [#6980](https://github.com/CrocSwap/integer-mult-bounds/pull/6980) for the retained word, caller and paid invoice. Credit #7160 and #7162 for prior stage-rank and uniform price arguments. OpenAI Codex and subagents materially assisted. Apache-2.0.
