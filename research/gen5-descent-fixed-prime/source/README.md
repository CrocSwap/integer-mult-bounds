# five-stage-gen5-kernels-descent

**Conditional κ = 744728650221677 / 10¹⁸ = 7.44728650221677·10⁻⁴** (+1.42·10⁻⁸, +0.0019% over PR #290's
7.44714499357628·10⁻⁴; +0.0817% over PR #287; +0.262% over PR #285's gen5 word).

PR #290 (chafreaky) is PR #287's gen5 package (DreamingOfClouds' gen5 word, rohanarun's 904-gate concave-descent
retiming and 220 target-prefix squares) with a 450-entry collective response-kernel stage after them. This package is
#290's package with **one added stage at the end of the bit pipeline: a second run of #287's `descent_transform.py`**
on the word after the kernel entries, with its own frozen `descent2-selection.json`.

* **What the stage does.** The concave-descent search behind #287 is re-run on #290's final word with constructed
  candidate frames — for each internal ADD gate, the minimal join and the maximal meet of its operands' neighbouring
  frames on their chains, not only frames the word already uses. It keeps 89 single-gate frame reassignments onto 32
  new bases (explicit rational rows in the selection). Local paid histogram delta
  {1: +41, 2: +154, 3: −82, 4: −48, 5: +24, 7: −48, 9: +24, 12: −24, 14: +24, 18: −41, 19: +41}: the local call count
  *rises* by 65 (five-stage calls 477,859 → 478,184; priced banked calls 475,180) at unchanged rank mass 2,746,720, but
  the concave weight Σ r·ln(120/r) that the moment certificate prices falls, so κ rises. Sources, targets, entrances,
  kernel entries, banks, charts, the scalar word (565,050 weighted ADDs) and every endpoint are unchanged.
* **Checks.** `descent_transform.py` (unchanged from #287/#290) consumes the frozen selection, rebuilds every MOVE from
  the retimed gate needs and independently checks the byte-identical scalar/COPY projection, nested chains, fixed
  source/dirty/target endpoints, unchanged COPY lifetimes, nondegenerate endpoint bases, both reflected annihilator
  ledgers and the exact integer source span of every non-target operand inside its new frame; the new bases are
  registered and their determinants are evaluated by `prime_check` with every other actual basis. `raw_ledger.
  rebind_descent2` recounts the five-stage profile through #290's `pins.pin`; every count the stage changes is a
  recomputed pinned value in `expected/kernel-pins.json` (`descent2_selected_gates`, `descent2_removed_calls`,
  `descent2_local_delta`, `descent2_five_stage_calls`, `priced_five_stage_calls`, `kappa`, …). Then every stage of #290's
  verifier runs fresh — virtual, raw, bit (descent, target, kernel, second descent), scalar, primes, banks, complex,
  math, finite — with its omitted-stage negative controls.

| one invocation, m = 120 | PR #287 | PR #290 | this package |
| --- | ---: | ---: | ---: |
| entrances | 2,554 | 3,004 | 3,004 |
| five-stage calls | 473,599 | 477,859 | **478,184** |
| literal stock, 60 replicas | 1,247,070 | 1,244,515 | 1,244,515 |
| κ | 7.44120696397042·10⁻⁴ | 7.44714499357628·10⁻⁴ | **7.44728650221677·10⁻⁴** |

Conditional, finite construction under the retained public all-size hypotheses of the source527 lineage (no Lean
certificate). The bit side binds. #285, #287 and #290 are open PRs; their stages are inherited unchanged and not
re-proved.

## Verify

    python -m pip install -r research/five-stage-gen5-kernels-descent/requirements.txt    # sympy 1.14.0
    python3 -B research/five-stage-gen5-kernels-descent/verify.py --output /tmp/gen5-kernels-descent-verification   # about 5 minutes; not under -I

`verify.py` is #290's; it prints `PASS_IMMUTABLE_GEN5_KERNEL_ENTRIES_FIVE_STAGE_BANKED_CONSTRUCTION` with the pinned κ.
The workflow `.github/workflows/five-stage-gen5-kernels-descent.yml` runs it on Ubuntu.

## Files

#290's package with: `descent2-selection.json` (new), the modified `portable_bit.py` and `raw_ledger.py`
(`rebind_descent2`), regenerated `expected/kernel-pins.json` and `MANIFEST.json`, this `README.md` and `PROOF.md`,
`NOTICE.md`; #290's README/PROOF kept as `README-PR290.md`, `PROOF-PR290.md` (and #287's as `README-PR287.md`,
`PROOF-PR287.md`). Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0.
