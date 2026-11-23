# Fixed-prime dyadic matcher route descriptors

This scoped supplement constructs one rational full-GL factor descriptor
for a complete dyadic matcher and a fixed odd prime q. It works at every
q-power width, retains both coupled role routes and the exact inverse word,
and fits the source route counts with all carry fields charged.

See `PROOF.md` for the all-size construction, coefficient and carry bit
bounds, physical tariff interpretation, attribution and limitations.
`ORIGINS.json` pins the retained sources. This package awaits separate
mathematical review.

From this directory:

```sh
python3 -I -W error -B routes.py
python3 -I -W error -B check.py --output EVIDENCE.json
python3 -I -O -W error -B check.py --output EVIDENCE-OPTIMIZED.json
```

The constructor writes the deterministic compressed descriptor catalogue
and a readable examples file. The verifier imports no constructor or
earlier basis checker. The finite catalogue covers 513 complete
nested-difference matchers, 111 essential stage routes, five boundary
fixtures and four odd primes. The mathematical statement is proved for
every complete fixed dyadic matcher and odd prime; finite tests do not
establish that universal quantifier by themselves.

The q alphabet allows nonunit additive numerators. Only denominators and
the numerators of scaling/pivot units must be prime to q. The source
`2N^3`, `N^3`, `N^2` counts refer to charged service records, not bit steps.
The final physical prime bound, all other selected assumptions and the
outer fine-prime obligations remain unchanged.
