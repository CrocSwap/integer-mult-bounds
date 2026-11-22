# Optimal height allocation within the signed fixed-resource family

This construction installs ordinary heights (8192,124847,524288) and Gaussian height 490664. It holds the signed K7 and weighted Gaussian sources, finite debits and largest actual height 524288. The resulting **conditional κ is 0.0038982141167032**, an exact increase of 395879/1250000000000000, or (395879/48727672500)%, over independently reproduced #8068 at κ 0.00389821380. The complete recurring log₂ ceiling falls by 260 to 318292451. [Exact comparator #8068](https://github.com/CrocSwap/integer-mult-bounds/pull/8068) · [Proof and scope](PROOF.md) · [Complete signed invoice](RESULT.json)

The two neighboring heights 490664 and 490665 attain the same exact rate ceiling within the declared height and clock budget. This package uses 490664, with the smaller recurring coefficient. The old Gaussian height falls short at the new booked rate. The old ordinary stage vector still funds it. The calendar checks the exact family bound and these controls alongside all retained lower-band, signed phase and owner tests.

Use Git and CPython 3.12 from the exact checkout.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-optimal-allocation
```

Ali Romman supplied the signed weighted multiplier, physical owner and return controls, ordinary and Gaussian finite costs and complete native tape proof. SYLforge supplied K7. #8068 supplied the exact capped signed comparison and verified physical gallery. OpenAI Codex materially assisted the exact allocation proof, implementation and independent verification. [Signed predecessor #8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057)

## Open next questions

A certified improvement within the same resource cap requires a different paid word, a stronger supplier or a smaller complete finite debit. The ceiling here holds the three-stage architecture, supplier tariffs and full clock inequalities fixed. Portable setup for the changed profile needs its own trace.
