# Sharp range for all active tensor repetitions

The same role-1256 row prefix maximizes the absolute real or imaginary
component for every positive repetition count m. Its sharp value is

```text
(12927/2)*2^(2m) + (36549/8)*2^(4m) + (51071533/256)*2^ceil(9m/2).
```

This answers the active-tensor question in
[PR #7725](https://github.com/CrocSwap/integer-mult-bounds/pull/7725).
Its one-tile bound is prior work. The proof covers the fixed graph's
172414 ordered prefixes with independent real and imaginary physical
entrances in [-1,1]. It gives an attaining field for every m. The all-m
bound follows from exact polynomial dominance, not a finite repetition sweep.
No new kappa, supplier admission or root-width reduction is claimed.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[verify.py](verify.py) and [CREDITS.md](CREDITS.md).
Python 3.12 and its standard library are sufficient:

```sh
python3.12 -B scripts/research_package.py --package research/relay1256-tensor-prefix-range
```

Both normal and optimized commands print:

```text
PASS_RELAY1256_ALL_TENSOR_PREFIXES 172414 prefixes; all m >= 1
```

The package retains 23 source files without changes. It reuses the graph
reader, backward expansion and exact chart interpreter. Source-aware author
checks do not establish independent human or formal acceptance. Full caller
correlations, child interiors, numerator temporaries, rounding and the
complete root format remain outside scope. All five interfaces remain.

## Open next questions

See [TASK.json](TASK.json) for structured next steps.

- Bind a specific signed caller stage to common root coordinates and test
  whether its correlated native entrances can attain this local maximum.
- Bound numerator temporaries and paid-child interiors before using M(m)
  in a complete precision or signed-width calculation.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
