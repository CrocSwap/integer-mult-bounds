# Independent invoice arithmetic

The invoice projections preserve the paid and target histograms from PRICE.json, and use the same signed 17-call invoice contract as #7631. They are inputs, not proof of their scientific applicability. No diagnostic credit is applied. Rank surplus 1424 is reported separately and is not an extra moment term.

From a checkout containing this package and the upstream scripts:

```sh
P=research/p104-e1-role457-on7631
python3 -B scripts/compare_recursive_invoices.py "$P/invoices/source.json" "$P/invoices/candidate.json"
python3 -B scripts/evaluate_recursive_power.py "$P/invoices/zero.json" "$P/invoices/source.json" --exponent 498166403402839/500000000000000 --bits 256
python3 -B scripts/evaluate_recursive_power.py "$P/invoices/zero.json" "$P/invoices/candidate.json" --exponent 498166403402839/500000000000000 --bits 256
python3 -B scripts/evaluate_recursive_power.py "$P/invoices/zero.json" "$P/invoices/candidate.json" --exponent 6227/6250 --bits 256
```

The first exponent is 1 minus 0.003667193194322; the last is 1 minus 0.00368. For the evaluator's paid-minus-target convention, the expected classifications are respectively `new_cost_higher`, `new_cost_lower`, and `new_cost_higher`. The projection does not validate the caller, signed catalogue, full bills or supplier.
