# Nine additional paired helper extractions

Starting from [Jeremy Diviney's PR2908](https://github.com/CrocSwap/integer-mult-bounds/pull/2908)
at `51309592971e3b5be935599eed2a95404dc7781e`, this package restores nine more
helpers while preserving all previously restored endpoints. Three extractions
use the existing frames; six more become possible after explicit frame refits.
The complete local profile changes by **9H1 + 18H3 − 18H4**. A literal owner
allocation realizes the resulting improvement after charging all nine extra
private buffers. The resulting bound is

**κ = 0.001721588647197801880605 − 10⁻⁴⁶ − 10⁻⁷⁰**,

an increase of **0.000001190309843563994674** (about **0.06919%**) over
pinned PR2908. The exact claim and release bindings are in [CLAIM.json](CLAIM.json).

This is a finite conditional supplier/outer certificate, with the inherited
all-size, compiler and theorem hypotheses still outstanding. It does not change
the maintainer-selected result or claim an unconditional multiplication theorem,
practical timing improvement, packing optimum, or independent human review.

| Quantity | Pinned PR2908 | This construction |
|---|---:|---:|
| Independent input columns | 632 | 632 |
| Live helpers | 408 | 408 |
| Private zero buffers | 73 | 82 |
| Width8 helpers | 87 | 96 |
| Width9 helpers | 231 | 222 |
| Local H1 / H2 / H3 / H4 / H5 / H8 counts | 2407 / 640 / 262 / 128 / 26 / 8 | 2416 / 640 / 280 / 110 / 26 / 8 |
| Live / physical families | 66304 / 66795 | 66304 / 66804 |

The 74 replicas, 666 calls, 271728 helper roles and inherited chronology are
retained. The paid global histogram includes every actual unused owner
remainder. [CONSTRUCTION.md](CONSTRUCTION.md) proves the paired identities and
explains the frame changes; `data/TRANSFORM-*.json` supplies every literal gate
and frame edit. The source-bound builder preserves the predecessor chain.

## Reproduce

The bounded registered replay uses Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/paired-helper-extension --check-only
python3.12 -B scripts/research_package.py --package research/paired-helper-extension
```

It reruns the exact nine-stage construction, both all-input forward/dual
audits, 36 semantic rejection controls, the actual owner allocation and
directed rational moment. It authenticates the recorded native and complete
outer-release receipts. It does **not** rerun native or integrated outer
admission; the complete command below does that.

For separate local and allocation checks, use fresh output directories:

```sh
python3.12 -B research/paired-helper-extension/verify.py --work /tmp/paired-local
python3.12 -B research/paired-helper-extension/check_allocation.py --work /tmp/paired-owners
```

For complete source/native/physical/outer admission, obtain the exact ancestor
Git objects, then run the public driver. It exports and authenticates the
predecessors without changing the checkout and does not fetch from the network.

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git \
  51309592971e3b5be935599eed2a95404dc7781e \
  18d03c447886895ef9abf888398178e0428533ca \
  e9307b48d7d1b690939935ecef0f8e524e6d92f4
env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3.12 -B research/paired-helper-extension/reproduce.py \
  --repo . --work /tmp/paired-complete
```

Use the numerical dependencies recorded in `evidence/ENVIRONMENT.json` for
the complete inherited replay. The default rebuilds the retained parent/native
evidence. `--retained /path/to/prior-run` explicitly reuses its `native-cache`
and `NATIVE-RECEIPT.json`, after complete source/claim/cache and all 16 retained
parent stages are authenticated. Both changed native providers are always
fresh in the public driver. The recorded public run used explicit retained-cache reuse; both changed
native chains and the full current admission were fresh. The reused parent
cache came from an earlier fresh PR2894 replay in the same session. See
`evidence/RETAINED-ORIGIN.json` and `evidence/FULL-REPLAY-RESULT.json`.
`--dry-run` only authenticates the PR2908 export and writes a recipe.

Exact hashes bind immutable source archives. Regenerated words are compared
by complete decoded content, so gzip container differences do not change the
mathematical comparison. The source identity is closed: all 632 files in the
derived source are accounted for, including the declared producer and checks.

## Open next questions

1. Can another profitable paired direction be extracted while preserving all 82
   restored endpoints? Recompute exact paired nullspaces on the final word and
   price the input/output gates, frame changes and new buffer before synthesis.
   A nominated direction alone does not establish another improvement.
2. Can a better literal allocation close more of the packing relaxation gap?
   Start from the shipped fill and explore bounded relay moves or changes to
   chronology, with exact owner-window and family checks. A fractional optimum
   is not an admitted bound.

Credit: Jeremy Diviney's paired extraction and structural checker; Jeremy
Kothe's PR2894/2833 supplier, frame accounting and cleanup; Yiyang Lu's staged
native/overlay tooling; and the retained owner, packing and exact-audit authors.
See [CREDITS.md](CREDITS.md) for the complete immediate lineage. Mason Hale,
with substantial OpenAI Codex assistance, including parallel cross-checks.
