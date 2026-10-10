# five-stage-gen5b-full

**Conditional κ = 187495641816757 / (25·10¹⁶) = 7.49982567267028·10⁻⁴** (+0.438% over PR #296's gen5b word
7.46709720962478·10⁻⁴; +0.011% over PR #299; +0.599% over PR #295; +0.789% over PR #287).

This package composes, on chafreaky's **gen5b** bit word (PR #296: #285's generator with an exactly optimal local
design and a debt-10 all-but-one module; #233's complex supplier), every bit-side stage of the gen5 lineage, each
re-derived on gen5b with its own discovery script and frozen selection:

| stage (credited) | on gen5 (#287/#290/#291/#295) | on gen5b (this package) |
| --- | ---: | ---: |
| concave-descent retiming (#287; #296's re-derivation) | 904 gates | 904 gates (#296's selection) |
| target-prefix squares (eumemic #268; #287; #296's re-derivation) | 220 squares | 220 squares (#296's selection) |
| collective response-kernel entries (chafreaky #290, Dugongue #254/#283) | 450 entries, rank 1,022 | **1,734 entries** (920 twin pairs, 431 triples, 383 quadruples), entrance rank **2,196** |
| second concave descent with constructed frames (rohanarun #291) | 89 gates | 87 gates (32 new bases) |
| early restoration of cleanup helpers (utcorvusvolat-dotcom #280; chafreaky #295) | 440 helpers | 440 helpers |
| terminal sinks (Dugongue #283; chafreaky #295) | 8 sinks | 8 sinks (R 15,434 → 15,426) |

The pipeline is #295's (`portable_bit.py`: parity → descent → target → kernel → **second descent** → restore → sink,
then the global lowering, scalar, primes, banks, complex, math and finite stages) with the second descent inserted
between the kernel and restoration stages; every transform is unchanged from #295/#291. The gen5b word and the
re-pinned word constants (R = 15,434, 18,954 formal columns, 753,472 parity ADDs, entrances 20 × 2,182, 21 × 34,
18 × 16, 17 × 2, path census 17,194) are #296's.

* **Kernel entries on gen5b.** #295's discovery (`discovery/coll/load.py` → `families.py` → `pack.py`, then
  `build_selection.py`) on the gen5b word after the descent and squares: 13,200 plain dirty helpers, 1,632 triangles
  and 10,041 quadruples at class level, 6,863 families with a common cut and a nondegenerate common entrance; the
  greedy packing under the deficit-fixed φ ledger keeps 1,720 (vs 450 on gen5: gen5b's alternative local design makes
  far more helper responses coincide); 250 randomized-order restarts of the same greedy (`discovery/pack_restarts.md`)
  improve the packing to **1,734 entries at φ −3,860** (the single greedy pass gives −3,799). The φ ledger reproduces
  every κ below exactly.
* **Bank tiling.** With 1,574 residual-23 pivots, #283's (r⁴, 4³⁰⁻ʳ) pivot banks would need more rank-4 blocks than the
  2,182 width-4 helpers supply, so `bank_template.build_patterns` gives each pivot residual r the banks (r⁴, 24ᵃ, 4ᵇ)
  with 120 − 4r = 24a + 4b, taking plain 24-blocks from the (24⁵) banks; every bank still partitions its 120
  coordinates, all 4,628,100 assignments are enumerated and the per-pattern endpoint controls run as before
  (807,280 banks; 910 charts; selector calls 905,935,487,400 < 2⁴⁰).
* **Second descent, restorations, sinks.** `descent4g`'s constructed-frame descent on the kernel word keeps 87 gates
  (local delta {1: +39, 2: +150, 3: −78, 4: −48, 5: +24, 7: −48, 9: +24, 12: −24, 14: +24, 18: −39, 19: +39}; +63
  calls at unchanged rank mass); #295's restoration screen finds 440 helpers at the first cleanup ADD (record 757,551;
  delta {1: +1320, 2: −880}; completion P_σ + I − P_E); #295's sink screen finds 8 legal sinks (delta {3: −8, 21: −8}).

| one invocation, m = 120 | #296 (gen5b) | this package |
| --- | ---: | ---: |
| helper registers R | 15,434 | **15,426** |
| independent entrances | 2,234 | **3,968** |
| literal stock, 60 replicas | 1,236,750 | **1,229,680** |
| priced calls / rank mass | — | 482,890 / 2,691,520 |
| κ | 7.46709720962478·10⁻⁴ | **7.49982567267028·10⁻⁴** |

Conditional, finite construction under the retained public all-size hypotheses of the source527 lineage (no Lean
certificate for the bit side). The bit side binds below #233's complex supplier. #285, #287, #290, #291, #295 and
#296 are open PRs; their word, generator and stages are inherited unchanged and not re-proved.

## Verify

    python -m pip install -r research/five-stage-gen5b-full/requirements.txt    # sympy 1.14.0
    python3 -B research/five-stage-gen5b-full/verify.py --output /tmp/gen5b-full-verification   # about 7 minutes; not under -I
    python3 -B research/five-stage-gen5b-full/gen5bit/producer/regenerate.py --work /tmp/gen5b-regeneration

`verify.py` is #295's; it prints `PASS_IMMUTABLE_GEN5_KERNEL_RESTORE_SINK_FIVE_STAGE_BANKED_CONSTRUCTION` with the
pinned κ. The workflow `.github/workflows/five-stage-gen5b-full.yml` runs it on Ubuntu.

## Files

#295's package with: #296's `gen5bit/`, `descent-selection.json`, `target-selection.json` and word constants
(`prepare.py`, `code/physical527.py`, `parity_transform.py`, `virtual_check.py`, `scalar_check.py`, `raw_ledger.py`,
`finite_check.py`, `bank_template.py`, `bank_check.py`, `math_check.py`, `code/global_lowering.py`); the re-derived
`kernel-selection.json`, `restore-selection.json`, `sink-selection.json`; the new `descent2-selection.json` with
`raw_ledger.rebind_descent2` and its call in `portable_bit.py`; the generalized pivot bank patterns; regenerated
`expected/kernel-pins.json` and `MANIFEST.json`; the discovery scripts updated for the extra stage; this `README.md`/
`PROOF.md` and `NOTICE.md`; #295's, #290's and #287's README/PROOF kept as `README-PR295.md`, `PROOF-PR295.md`, …
Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0.
