# Bound a signed idle pair with two-term erasure

**NO VERIFIED GAIN.** At events 1339 and 1340 of the exact [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113), two independent Type B lanes receive the same signed rank-nine map. On one fixed parked fibre and at width one, even granting each lane a free map of the form $aI+bD^2$, the residual rank is at least 480. One rank-nine core on one lane volume supplies at most 392. Arbitrary linear ingress and egress in the residual factorization cannot close this gap. [#7481 application](https://github.com/CrocSwap/integer-mult-bounds/pull/7481)

From a clean POSIX checkout with CPython 3.12 and assertions enabled, run the two finite verifiers and the directed price check together.

```sh
python3.12 -I -B research/p104-signed-idle-erasure-bound/replay.py
```

[Proof and exact scope](PROOF.md) · [Verification](VERIFICATION.md) · [Source pins and credit](PROVENANCE.json)

## Open next questions

A mixed parked fibre or a wider erased-action family changes the residual model. Before testing another site, pin one concrete erased operator and bound its two-lane residual rank and the complete price of its ingress, egress and restoration. The width-one result decides the stated all-width architecture. It leaves the stage-nine pair, different widths as separate finite experiments, other core ranks, and the remaining transport models open.
