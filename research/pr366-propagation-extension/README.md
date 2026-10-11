# Ten coupled frame retimings after PR369

Conditional exponent saving:

`κ = 804946219504150552042557 / 1000000000000000000000000000`

approximately **0.000804946219504150552**, an increase of
**3.2623579769e-9** over [PR369](https://github.com/CrocSwap/integer-mult-bounds/pull/369)
at its source package commit `dcb21903720bd2e30b1eadef680f39e4fc2d7232`.
The complete final word is rebuilt and priced; gains are not added numerically.
The bit side binds and E8 is unchanged.

This package preserves the published `pr364-kernel-extension` directory.
It adds ten frame retimings in four connected groups, using the established
recursive frame propagation rule. These groups use mutually disjoint
register sets. Their frozen assignments are applied in three source-bound
stages: the first pair, the second pair, then the last two groups together.

| Group | Earlier ADDs, all 13 → 12 | Later ADD, 15 → 14 |
| --- | --- | --- |
| 1 | 8353 += 7736 | 7736 += 6997 |
| 2 | 8337 += 7716 | 7716 += 6994 |
| 3 | 8744 += 7780; 8744 += 8548; 8548 += 7780 | 8548 += 7231 |
| 4 | 6846 += 6587 | 6587 += 6386 |

For each group, lowering the later gate alone breaks exact frame containment
on the shared register. Lowering its predecessor or predecessor triangle as well repairs this.
The complete signed scalar sequence and all endpoint maps stay unchanged.
The emitter rebuilds MOVEs just before use. It checks actual integer source
spans, every used frame and the full binary operator.

The local paid-child histogram changes by
`{1:-3, 2:-5, 3:+4, 4:+1, 9:+3, 10:-3}`. Paid rank mass remains 168686;
357762 local unit ADDs and helper residual rank 131846 are unchanged.
The final word has 405675 records and adds five frames to PR369's registry.
Its records SHA-256 is:

`b0fd6cfb9a976e07c3860a5fddd34962504db31163d5346f96fc5e7c6624fdb0`

## Replay

From a checkout containing the unchanged PR369 package and its ancestors:

```sh
python3 -m pip install -r research/pr366-propagation-extension/requirements.txt
python3 -B research/pr366-propagation-extension/verify.py \
  --output /tmp/pr366-propagation-proof \
  --boost-include /path/to/boost
```

Use a fresh output directory outside `research/`. Python 3.11+, a C++17
compiler and Boost headers are required. Omit `--boost-include` if the
headers are installed on the default include path; `--cxx` selects a
compiler. Assertions must remain enabled. The inherited shell replay
requires source, output, interpreter, compiler and Boost paths without
whitespace; the wrapper checks this before doing work.

The default entry point always runs the complete pinned parent verifier.
It then re-emits and fully checks each of three stages, checks the four failed
single-gate controls, and independently replays all 10010 local formal
columns with the inherited twelve kernel ADD-omission controls. Fresh
native checks cover physical legality, all 11930 global columns, bridge
omission controls, the 93-bit prefix bound and changed-frame nondegeneracy.
Exact 100-replica banking and both rational moment engines are rerun.
The full inherited fallback, eight finite bootstrap steps and all 47 strict
outer constraints are retained.

`EXPECTED.json` pins portable exact arithmetic and finite receipts. Fresh
runs must reproduce it; clocks, machine paths and self-manifest hashes are
excluded. `CERTIFICATE.json` is written only after all checks pass and both
package manifests are checked again. See `PROOF.md` for the dependency
argument and `NOTICE.md` for source credit.

## Conditional scope

This is a finite conditional construction and exact assembly result.
PR369's native downstream admission, changed projector charts, complete
finite invoice and all-size compiler, routing, restored-row, prime-supply,
precision/recovery and analytic interfaces remain open or conditional.
No new native invoice, signed integer decoder equality, Lean proof or
unconditional multiplication theorem is claimed. The banking normalization,
fallback allowance and recursive transfer are unchanged from PR369.

Prepared with substantial OpenAI Codex assistance; Apache-2.0.
