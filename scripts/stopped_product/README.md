# Selected rational-center producer

Run from the repository root:

```sh
python3 scripts/stopped_product_producer.py --output /tmp/stopped-product-producers.json
```

Only the new aligned complex producer at h=24 is rebuilt. It retains all
24 disjoint-point sums and decodes the total by exact division by21. The
pair-star input order is aligned with global pairs. Its generator adapts
`structured_bulk.complex`, preserving exact support, output orthogonality,
binary frame nesting and nondegeneracy checks. Rational decoder and scatter
coefficients are checked with `Fraction`; their only odd denominator is21.
The unchanged deterministic matcher compares every count and histogram
entry against `stopped-product-complex-input.json`.

The h23 bit record is compared with the preceding validated copied-center
input. No old bit DAG, matching, or corner is regenerated. Both copied-center
histogram transformations reuse the established exact rank-mass checker.

All DAGs, labels and the compiled matcher are temporary by default;
`--work-dir` retains them. Python assertions must be enabled. Standard-library
Python and a C++17 compiler suffice. No binary archive is an input.

The odd-grid extension is a written recursive invariant, not a claim proved
by the finite scalar tests. With dyadic root inputs, K=G(D+1) supplies enough
odd-divisor reserve along the active chain. A completed child preserves its
incoming odd valuation; it does not generally make rational child inputs
dyadic. Only the completed outer dyadic operator restores the original
dyadic grid. No child return is rounded.

Copyright 2026 icekylinx, Apache-2.0. New selected alignment, rational centers
and integration were prepared with OpenAI GPT-6 Astra/Codex assistance.
Underlying paired producers and deterministic carrier matching retain the
previous contributors' attribution in `NOTICE` and `SOURCES.json`.
