# Reproducing the exact directed-price check

`invoices/source.json` and `candidate.json` contain the full actual signed paid and target histograms from `RESOURCE-PRICE-PROJECTION.json`, with a common declared contract copied from the source-specific invoice. `invoices/zero.json` has the same contract and empty histograms. Each is an `integer-mult-recursive-invoice/v1` input. Counts and the declaration are evidence inputs; the comparator does not prove their scientific applicability. The separately reported rank surplus 1,424 is not an extra term in this moment computation. Ordinary and precision expenses are separately recorded in the resource receipt.

From the root of a checkout containing this package and the main scripts at base `e54523517d0f03e58352e647c403a5af3e525a57`, run:

```sh
P=research/p104-e4-direct-on7627
python3 -B scripts/compare_recursive_invoices.py "$P/invoices/source.json" "$P/invoices/candidate.json"
python3 -B scripts/evaluate_recursive_power.py "$P/invoices/zero.json" "$P/invoices/source.json" --exponent 498166863599/500000000000 --bits 256
python3 -B scripts/evaluate_recursive_power.py "$P/invoices/zero.json" "$P/invoices/candidate.json" --exponent 498166863599/500000000000 --bits 256
python3 -B scripts/evaluate_recursive_power.py "$P/invoices/zero.json" "$P/invoices/candidate.json" --exponent 6227/6250 --bits 256
```

The first exponent is `1 - 0.003666272802`; the last is `1 - 0.00368`. At the conservative claim the expected classifications for source and candidate are respectively `new_cost_higher` and `new_cost_lower`; at the goal the candidate is `new_cost_higher`. These labels are for `paid minus targets`, the negative of the receipt's moment sign. The comparison prints the full signed delta; inspect it rather than treating a concave-order classification as the price result. The separately retained `RESOURCE-PRICE-PROJECTION.json` gives both directed engine intervals, actual crossing endpoints and their signs, not just this CLI's reproduction. These commands cover standalone invoice arithmetic. Full circuit, supplier, ownership, signed catalogue and compiler review depends on the evidence and assumptions described in the README.

## Checking declared predecessor bytes

Obtain a checkout or export rooted at [#7627’s exact head](https://github.com/CrocSwap/integer-mult-bounds/tree/f9bdd00d3869ef6e82227a9acf4633f102540f54). It must contain the paths recorded under `public_predecessor_path` in the signed and resource closure maps. Check those bytes with:

```sh
python3 -B "$P/INTEGRITY.py" --predecessor-root /path/to/pinned-7627-checkout-or-export
```

This verifies all 44 declared public predecessor entries by size and SHA-256. The maps identify withheld host originals and their hashes. This command has no access to those originals.
