# Validation record

Prepared for alluri-ritual with substantial OpenAI Codex assistance. Apache-2.0.

Checked locally on 2026-10-13 UTC, macOS 26.6.2 arm64. The fourteen-window
continuation starts from PR681 commit `80d4edbc2d53f058787cb5c43bd0fc22c7e7fdff`,
whose exact repository base is
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.

- CPython **3.14.3**: complete fresh constructor, local certificate, both raw
  native/emitted/independent replays and frozen receipt comparison pass.
- CPython **3.11.15**, with `-I -O -B`: same complete replay and byte-equivalent
  deterministic receipt pass. The inherited checkers are launched in isolated
  subprocesses with their assertions enabled.
- Search replay: Python 3.11 and 3.14 reproduce the historical 35-gate word
  after 1,024 trials and the new 34-gate/128-primitive word after 512 two-sided
  trials, 4,096 middle orders and three scale-relocation improvements.
- Both raw words: 716 arbitrary input columns per orientation; full frame,
  compensation, source/helper restoration and private-work clearing checks.
  Fourteen new corruption controls pass, including all-block inventory,
  register and frame controls. The inherited local audit rejects four
  controls per word: wrong scale, missing center, wrong common frame and wrong
  child rank.
- Relocated minimal source closure, in a path containing spaces, passes under
  isolated optimized Python. Five package controls reject a modified pinned
  constructor, a fabricated original circuit window, a corrupt expected result,
  missing source pins and an already existing output directory. The last check
  verifies that a pre-existing marker file is preserved.
- `python3 -B scripts/verify_selected_result.py` passes: the existing selected
  exact κ, original source inventory and proof supplements remain bound.
- Staged whitespace and changed-path checks pass; additions are confined to
  `research/complex-factory5-resynthesis/`. No pre-existing supplier or selected
  artifact is modified.

`RESULT.json` is a deterministic scientific receipt, not a timing report. Source
archives retain exact byte hashes. Generated gzip files are compared through
all decoded JSON fields/canonical JSON hashes, excluding only inherited
runtime seconds and gzip-container hash fields from receipts. Macro counts,
matrices, column counts, frame/phase inventories, width arrays, primitive bills,
prefix bounds and control outcomes remain covered.

Commands:

```sh
python3 -B research/complex-factory5-resynthesis/verify.py
python3.11 -I -O -B research/complex-factory5-resynthesis/verify.py
python3 -B research/complex-factory5-resynthesis/search.py
python3 -B research/complex-factory5-resynthesis/test_package.py
python3 -B scripts/verify_selected_result.py
```

Expected final markers are `PASS_COMPLEX_FACTORY_RESYNTHESIS`,
`PASS_SEARCH_FACTORY`, `PASS_PACKAGE_CONTROLS` and the selected-record PASS.

The full repository suite and cold selected-provider replay were not run:
this standalone addition changes no selected supplier, assembly, generator or
existing artifact. Clifford phase lowering, global invoice/hosting, Linux CI,
Lean and integration through later transported recipes are not claimed.
There was no independent human or delegated-agent review. The proof boundary
is stated in `PROOF.md` and the README.

The combined word changes all fourteen windows at once. Full raw scalar
operations fall from 16,972 to 15,488; emitted real primitives fall by exactly
10,192 in each orientation. Recomputed prefix bounds are 68,417 forward and
1,649,462 inverse-transpose, requiring 17 and 21 bits under the inherited
checker, versus the raw original's 37 and 40. The selected payload allowance
is not changed. Source compensation, recursive profile, boundary frames and
all 3,110 directed phase edges are identical.
