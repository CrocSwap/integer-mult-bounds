# One finer ordinary debit for the signed weighted multiplier

This isolated package retunes the ordinary finite-factor debit from `1405/1024` to `11239/8192` and transfers one height level from ordinary stage two to the Gaussian stage. With ordinary heights `(8192,124863,524288)` and Gaussian height `490639`, the signed all-size construction supports conditional κ `0.00389821412325`. The reference is [#8070 at 7d65b2c6](https://github.com/CrocSwap/integer-mult-bounds/commit/7d65b2c6a19941b9922d5e4c86c495aa37073141), which certifies `0.0038982141226643`. The difference is exactly `5857/10^16`. The new rate clears the exact #8070 family ceiling. [Proof and complete invoice](PROOF.md) · [Exact result](RESULT.json)

The original paid schedule, ownership and restoration contract, precision model and five assumptions from the signed construction still apply. The recurring log₂ C bound is `318292071`, 100 below #8070. The maximum native height is `524288`, entry conversion uses `515` bits, and fixed serial setup is below `2^228`.

Use Git and CPython 3.12 from a clean checkout.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-weighted-ordinary-debit-11239
```

The seven registered modes authenticate the frozen public inputs, apply the retune and check complete price, calendar and signed stage seams, both physical widths, exterior and nonzero nested returns, full signed multiplication, and fixed setup. Negative controls cover the former ordinary debit, the former Gaussian height and a corrupted signed return. The signed arithmetic and operand restoration checks apply to both tiers. The independent physical coefficient fixture uses the entry tier.

## Open next questions

A distinct paid route may lower the measured recurring cost or fund a higher Gaussian rate. A follow-up should first price one concrete allocation or operator against this profile, check its first affected signed read and then charge every required return. This package establishes an exact crossing for the stated profile. Additional allocations and paid schedules remain open.
