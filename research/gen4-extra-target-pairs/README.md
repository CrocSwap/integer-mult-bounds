# Twenty additional target pairs on PR283

This package raises the conditional exponent from PR283's
`0.000726111344123732762670617` to

```
kappa = 726214631355537156447271 / 10^27
      = 0.000726214631355537156447271
```

The gain is 0.0142247% over that pinned construction and 1.75490% over PR275's
earlier zero-frame result. Twenty of PR281's additional target pairs compose
with PR283's sink/kernel/endpoint word. The other forty proposed pairs fail
the unchanged native geometric boundary checks and are excluded.

| Quantity | Pinned PR283 | This composition |
|---|---:|---:|
| Target groups | 220 | 240 |
| Local scalar ADDs | 617,132 | 617,152 |
| Normalized recursive calls | 11,673,360 | 11,670,960 |
| Local paid rank mass | 422,844 | 422,844 |
| Literal stock, 120 replicas | 2,551,580 | 2,551,580 |

The exact incremental local histogram is `{3:-20, 18:-20, 21:+20}`. Each pair
replaces a rank-18/rank-3 split with a rank-21 child. Its setup/restoration
adds two scalar ADDs and removes one previous prefix read. Every gain is
recomputed from the emitted word; exponents from separate proposals are not added.

## Reproduce

Obtain PR283 at commit `65768f62d4fde0d1fa7fc84f71678522a84aaa6c`, preserving
exact file bytes (`core.autocrlf=false` on Windows). Use Python 3.11+, SymPy
1.14.0, GCC with C++17 support and Boost headers:

```sh
python -m pip install -r /path/to/pr283/research/gen4-composed-endpoints120/requirements.txt
python -B research/gen4-extra-target-pairs/verify.py \
  --base /path/to/pr283/research/gen4-composed-endpoints120 \
  --output /tmp/gen4-extra-target-pairs --cxx g++
```

On Homebrew macOS, supply the installed GCC executable, such as
`--cxx /opt/homebrew/bin/g++-16 --boost-include /opt/homebrew/include`.
Apple Clang does not provide the prerequisite's `bits/stdc++.h` header.
The output directory must be new and outside both source packages.

Verification starts with PR283's complete fresh source-bound replay, including
all nine original PR276 stages. It uses PR283's unchanged native target,
geometry, bank, global-column and exact-pricing implementations. A separate
Python checker repeats all 19,914 local columns in both directions, rejects
omissions specifically in the new pairs, and binds the literal counts and
finite invoice. Source manifests are checked before and after. No saved PASS
receipt substitutes for prerequisite execution. Final receipts are
`VERIFICATION.json` and `candidate/INDEPENDENT.json`; allow about ten minutes.

`PROOF.md` gives the identity, boundaries and price. `SOURCE.json` pins inputs.
Notices preserve contributor and AI-assistance attribution. The older PR275
package is a historical result and is not an input to this construction.

This is a conditional finite construction under the retained all-size
compiler, weighted-chart, restored-row, routing, selector, prime-supply,
precision/recovery, complex and analytic hypotheses. It is not a full Lean
proof or a practical multiplication benchmark.
