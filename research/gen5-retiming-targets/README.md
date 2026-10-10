# Gen5 source retiming and target-prefix compression

**Conditional κ = 744118535019311029483079 / 10^27 =
0.000744118535019311029483079**, 0.1794423% above freshly reproduced PR285.

This package ports two independently discovered optimizations to PR285's actual
gen5 word: 880 source-frame retimings and 220 target-prefix groups. The target
search examined 2560 admissible boundaries using exact prefix columns. Closing
at the latest admissible boundary gave no savings; earlier boundaries expose
220 dependencies. The source search derives its frames from the new word's
operand chronology. Neither selection reuses gen4 record indices.

| Quantity | PR285 baseline | Composition |
|---|---:|---:|
| Local recursive calls | 92502 | 91393 |
| Local scalar ADDs | 574832 | 574392 |
| Local rank mass | 411356 | 411356 |
| Normalized calls, 120 replicas | 11438160 | 11305080 |
| Literal stock, 120 replicas | 2494140 | 2494140 |

Source retiming removes 880 local children. Target compression removes another
229 children and 440 scalar ADDs. The complete doubled PR285 bank layout is
retained: 329868 banks per stage and 9531600 role/replica/stage assignments.
The complex supplier and all inherited hypotheses remain unchanged.

## Reproduce

Use Python 3.11+, SymPy 1.14.0, GCC/C++17 and Boost headers. Obtain PR285 at
`b40c1a3d8f40ee3764b9f13fe850f663f2d8c834`, then run:

```sh
python -m pip install -r /path/to/pr285/research/five-stage-gen5-banks/requirements.txt
python -B research/gen5-retiming-targets/verify.py \
  --base /path/to/pr285/research/five-stage-gen5-banks \
  --output /tmp/gen5-retiming-targets --cxx g++
```

The output directory must not exist. For Homebrew GCC, add
`--cxx /opt/homebrew/bin/g++-16 --boost-include /opt/homebrew/include`.
The wrapper freshly verifies all nine PR285 stages, exports its word, rebuilds
the native tools, applies both selections, and reruns geometry, Gram, banks,
global columns, exact moments and the literal finite invoice. A separate Python
checker verifies the final columns, actual circuit differences and cost formula.
Saved PASS receipts never replace execution. Source manifests are checked before
and after the run. CI executes the full command on Python 3.11 and 3.13.

The primitive coefficient is 180164370784684201, with a 95-bit payload bound,
eight ordinary levels, the fixed prime 2^127-1, 47 strict assembly inequalities
and rejection of the adjacent finite grid point. This is a conditional finite
construction, not a formally verified complete theorem or a measured multiplier.

See [PROOF.md](PROOF.md), [SOURCE.json](SOURCE.json) and [NOTICE.md](NOTICE.md).
