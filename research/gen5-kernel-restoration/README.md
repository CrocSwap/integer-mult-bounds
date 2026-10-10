# Gen5 collective kernels with 440 early helper restorations

This package composes 440 early signed restorations with the exact PR290
450-entry collective-kernel word. Its conditional finite construction admits

`kappa = 745272866677869825771952 / 10^27`.

This is 0.074977% above the independently reproduced PR290 bound
`0.000744714499357628`, and 0.155127% above PR275's previous gen5 package.
The all-size hypotheses remain conditional. This is neither an unconditional
multiplication theorem nor a practical runtime benchmark.

## Reproduce

Use Python 3.11 or later on a little-endian host, GCC with C++17, Boost headers,
and the pinned prerequisite's `requirements.txt` (SymPy 1.14.0). Obtain
`chafreaky/integer-mult-bounds` at commit
`739c3bb0ad0596f427e0a72a2ebeca23277217a3`; its package is
`research/five-stage-gen5-collective-kernels`.

```sh
python -m pip install -r /path/to/pinned-pr290/research/five-stage-gen5-collective-kernels/requirements.txt
python -B research/gen5-kernel-restoration/verify.py \
  --base /path/to/pinned-pr290/research/five-stage-gen5-collective-kernels \
  --output /tmp/gen5-kernel-restoration
```

The output directory must not exist. Optional `--cxx` selects GCC and
`--boost-include` selects its header directory. The wrapper compiles every native
program, runs all ten untouched PR290 stages, regenerates coordinate and role
metadata from its actual source, checks the post-kernel role/index mapping and
word, emits the restorations, and rebuilds the bank, global and finite invoices.
No cached PASS receipts or machine-specific paths are inputs. Expect several
minutes and a few GB of memory. Individual subprocesses have a ten-minute limit.
Python 3.11 and 3.13 run in the dedicated GitHub Actions workflow.

All package files are hashed in `MANIFEST.json`. Both source trees are checked
before and after replay, including unexpected files and symlinks. Successful
output is `VERIFICATION.json`; per-stage logs are under `logs/`, and detailed
receipts under `candidate/`. `SOURCE.json` records exact prerequisite pins.

## Contribution

At the first cleanup gate, each selected helper has one remaining signed
restoration. Its donor and destination frames have rank 22 and a nondegenerate
rank-23 union. Moving that restoration to this earlier cut allows the helper to
finish at rank 23. The signed shear commutes through its entire relocated
interval: the destination is untouched and the donor is never written. The 440
donor and destination sets are disjoint. `PROOF.md` explains the admission chain.

| Quantity | PR290 | With early restorations |
| --- | ---: | ---: |
| Local rank mass | 410334 | 409894 |
| Local scalar additions | 565050 | 565050 |
| Normalized stock | 497806 | 497366 |
| Literal stock | 2489030 | 2486830 |
| Retained kernel entries | 450 | 450 |

The incremental paid histogram is `{1:+1320, 2:-880}`. Calls increase by 440
locally; the improvement comes from reduced endpoint rank and stock. All 450
kernel entries and their entrance-rank saving of 1022 remain in place.

The final invoice includes 985 exact endpoint charts, 9,531,600 bank assignments,
11,449,320 normalized calls, selector charge 2,251,679,266,800 and primitive
coefficient 181,440,420,660,517,801. The actual chart maximum is 318 factors;
the retained conservative ceiling of 744 and normalizer 983 remain charged.
Signed prefix bounds are 67,127 and 2,360,408, producing a 97-bit payload bound.
All eight finite levels, the fixed prime and 47 strict rational constraints are
recomputed. The adjacent kappa grid point fails `margin2`.

The exact final word SHA-256 is
`8cfe069d7714b332d44f9ede431f4a902834963dac974436590cbec33ccb27f6`.
This package supersedes the earlier `gen5-retiming-targets` result numerically;
that package remains an independently reproducible historical contribution.
