# Two-sided helper extraction on PR2894

The explicit input/output basis change isolates helper408 as an additional
restored cold helper. Its width drops from 9 to 8, with one additional private
zero buffer. Both changed providers pass exact 632-input forward/dual audits
and the full five-stage native chain. A repaired T74 owner allocation gives

**κ = 0.001720398337354237885931 − 10⁻⁴⁶ − 10⁻⁷⁰**, conditional on the inherited
supplier/outer theorem hypotheses. This is **+2.13808976768352857×10⁻⁷**
(about **0.0124%**) over [PR2894](https://github.com/CrocSwap/integer-mult-bounds/pull/2894)
at `18d03c447886895ef9abf888398178e0428533ca`. The selected repository result
is not changed. The exact headline and full release receipt are bound in
`CLAIM.json` and `evidence/`.

This changes the local gate word and the cold-helper endpoint; the subsequent
owner repair is necessary to realize a gain. Keeping the old fill loses.
[CONSTRUCTION.md](CONSTRUCTION.md) explains the paired-nullspace identity and
complete cost changes. The method uses standard exact linear algebra; no
claim of a new general mathematical theorem or packing optimum is made.

Credit: Jeremy Kothe's PR2894/2833 supplier and allocation, Yiyang Lu's PR2857
shared-kernel/native/overlay work, Dugongue's PR2863 packing, Marius-Paul
Dumitrean's PR2843/2802 lineage, Philippe Van Velzen's PR2853 cost work,
Tekalign's admission/owner checkers, and the retained exact/native authors.
Our contribution is the helper408 extraction, independent structural
certificate, actual allocation repair and explicit 73-buffer integration.
See [CREDITS.md](CREDITS.md). Substantial OpenAI Codex assistance; no independent
human review is claimed.

## Reproduce

Tested on Linux, Python 3.12.3. The registered replay needs NumPy 2.5.4 and
runs the exact construction, semantic controls, both fresh native chains,
owner checks and rational moment. It authenticates the stored full-release
chain; it does not rerun complete integrated admission.

```sh
python3.12 scripts/research_package.py --package research/two-sided-helper-extraction --check-only
python3.12 scripts/research_package.py --package research/two-sided-helper-extraction
```

For a direct local-only check (standard library, fresh output directory):

```sh
python3.12 -B research/two-sided-helper-extraction/verify.py --work /tmp/helper408-local
python3.12 -B research/two-sided-helper-extraction/check_allocation.py --work /tmp/helper408-owners
```

For complete source/native/physical/outer admission, first obtain the exact
upstream Git objects. The driver exports them without changing the checkout
and verifies the complete predecessor manifest before executing its code.

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git \
  18d03c447886895ef9abf888398178e0428533ca \
  e9307b48d7d1b690939935ecef0f8e524e6d92f4
nice -n 15 env OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3.12 -B research/two-sided-helper-extraction/reproduce.py \
  --repo . --work /tmp/helper408-complete
```

Use the numerical dependencies recorded in `evidence/ENVIRONMENT.json` for the
complete inherited replay. Outputs must be fresh and external. The default
rebuilds the retained native/parent evidence. `--retained /path/to/prior-run`
explicitly reuses that run's `native-cache` and `NATIVE-RECEIPT.json`, only after
full source/claim/cache and all 16 parent stages are authenticated. The recorded
run reused retained evidence from our previous complete replay, and freshly
replayed both changed providers. It does not claim all retained work was fresh.
`--dry-run` only exports/authenticates PR2894 and writes the recipe.

The integrated certificate uses 74 replicas, 666 calls, 271,728 helper roles,
66,304 live families and **66,795 physical families**, including all **73**
private zero buffers. The exact paid histogram includes every residual owner
child. All inherited phase, cleanup, prefix, stock, geometry, rejection and
outer checks remain required. No fractional packing estimate is used as a
certificate.

## Open next questions

1. Can a second independent paired input/output direction be extracted while
   preserving helper408? Repeat the exact nullspace construction on the new
   word, then charge its actual native and owner costs. A modular nominee or
   local width reduction is insufficient.
2. Can a better literal allocation approach the new inventory's relaxation?
   Start from the shipped feasible fill and test bounded exchanges or
   relocations. Full exact admission remains mandatory for any higher claim.

The structured questions, stopping rule and original task card are in
[TASK.json](TASK.json). Initial failed screens, solver timeouts and the
successful deterministic repair are summarized in `evidence/SEARCH.json`.
