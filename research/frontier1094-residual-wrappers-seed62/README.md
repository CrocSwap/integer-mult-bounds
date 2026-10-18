# The selected frontier1094 word's 36 residual wrappers are exact

**Supplier-boundary audit: an independent, byte-bound check. No new κ, and no existing check is changed.**

- Track: 60–74 (adversarial audit), assignment seed 62, drawn with the OS CSPRNG via Python `secrets`.
- Card: `supplier-boundary-audit`, with the scope **refined** in [TASK.json](TASK.json).
- Base: `179089e4`. The selected record frontier1094 is unchanged.

## The obligation and where its acceptance came from

Lemma A's exact part (`research/e8-lemma-a-lean`, `research/e8-lemma-g-lean/PROOF.md` §4) concerns every helper that enters at a nonzero frame E or ends below FULL at a hyperplane U. Each such helper needs a stored wrapper (L, R) with

`L ∘ (C_[w] ⊗ I) ∘ R = T_end ∘ T_E⁻¹`,  w = dim end − dim E,

where end is FULL, or U for a hyperplane end. For the selected gauge44 provider these are the 36 records in `RESIDUAL-ADAPTERS.json`, raw sha256 `383f40aa`.

The selected chain binds the bytes of that file, but not their exactness:
- **The bytes are pinned.** Both the owner audit's `source_artifacts` and the certificate's fresh invoice (`input_sha256.fresh_invoice` → `PREFIX-AND-INVOICE.json` → `providers.gauge44.artifacts`) pin it.
- **The chain's own audit checks structure only.** `gauge44-slots-t16/code/audit_allcold.py` (lines 56–61) checks only each wrapper's `frame`, `terminal`, `vectors`, `terminal_vectors` and ranks.
- **Exactness is established only by the producer's own code.** `hpe_adapters_local.py` generates the wrappers and decodes them again with the same `clifford_exact` primitives, then writes `WRAPPER-CHECKS.json` (`PASS_RESIDUAL_WRAPPERS_ARE_EXACT`, sha256 `0ae753d6`).
  - The fresh invoice pins that receipt's bytes, but no chain code reads its status or content.
  - The cold replay re-runs the same producer, for example `gauge44-slots/construction/slots/verify_slots.py:103`.
- **#1781 (ours) left these records out** of its independent check. It covered the 2,896 child records and the 224 endpoint adapters.

## What this package checks

### Binding
- It reuses the merged #1781 binding, which our package imports with its digests pinned. The chain runs: selected record → frontier1094 certificate → capsule → owner audit → gauge44 word and programs.
- `RESIDUAL-ADAPTERS.json` must match the owner audit's own digest.
- The `split-centres` decoy, which has the same basename, differs by digest.
- The certificate's fresh invoice pins both `RESIDUAL-ADAPTERS.json` and `WRAPPER-CHECKS.json`.
- The global8 twin is byte-identical. This is informational only.

### Inventory
- **The keys.** The 36 keys are exactly the word's entering helpers ending at FULL (key = start) together with its hyperplane-ending helpers (key = start:final). That gives:
  - 22 FULL-ended records;
  - 12 cold hyperplane-end records (`0:U`);
  - 2 entering hyperplane-end records (`2:999` and `3:998`).
- **The records.** Every record's frames, vectors and ranks match the word, and all 72 monomials are well formed.
- **The program events.** In both programs, every residual event is a `pre` or a `post`. Each of the 240 wrapped helpers has exactly one of each, with the right key. Its first event is the `pre` and its last is the `post`. Our open #1964, from another session, checks this placement as part of Lemma G's H1. Each orientation has 480 events, with widths {4: 112, 5: 64, 7: 60, 8: 244}.
- **Record fields.** Every record has exactly its expected field set.

### Two kernels
- **Kernel B** ([closed_form.py](closed_form.py), new, standard library only) computes amplitudes directly from closed forms:
  - the frame operator from its closed formula;
  - the monomial records from their closed forms;
  - F_w from the √X product.

  It works on sparse exact columns and evaluates no gate list.
- **Kernel A** is #1781's packed Gaussian-integer evaluator (`clifford.py`).

Both must find every identity exact on all 512 columns, with the global phase included.

### Calibration of kernel B
Before any record is judged, kernel B must pass three checks:
- **Frame operator.** Kernel B must reproduce #702's 14 frame-kernel digests and #1415's three operator digests of T_U ∘ T_E⁻¹. These cover frames of rank 1, 4 and 8 and the conjugate transpose.
- **Monomials and F_w.** On every column, kernel B's monomial and F_w must equal kernel A's: for 10 record monomials, and for F_w with w = 1, 4, 8 and 9. Without this check, those two conventions would be anchored only by the records under test.
- **Lean pairs.** Records `3:998` and `2:999` must be field-for-field equal to Exact.lean's pair 2 and pair 3. For `2:999`, #1611 had already shown this for this word.

## Results ([RESULT.json](RESULT.json))

| | Records | Exact (kernel B) | Exact (kernel A) | K (C gates per identity) |
|---|---|---|---|---|
| FULL-ended | 22 | 22 | 22 | 9 |
| Cold hyperplane-end `0:U` | 12 | 12 | 12 | 4 (8 records), 8 (4 records) |
| Entering hyperplane-end | 2 | 2 | 2 | 8 |

All 36 wrappers are exact.

### Controls
Each mutation below is rejected on every record it applies to:
- global phase +1;
- input character (`linear_Z4 += 2`);
- a CZ term in Q;
- an offset translation;
- swapped wrappers;
- width −1 and width +1;
- a transposed matrix (36/36 each);
- hyperplane-end records evaluated against FULL (14/14);
- a FULL-ended wrapper reused for a hyperplane end (2/2);
- another basis of the same span (2/2, while the same rows reordered pass);
- kernel B's own phase and width mutants (8/8).

The tests also reject the decoy, a flipped archive byte, a dropped `pre` event, an event read with the wrong key, and a wrong record vector. [test_package.py](test_package.py) has 17 tests.

## Overlap

Prior coverage, checked against the repository:
- **The Lean pairs.** `2:999` and `3:998` are the Exact.lean pairs (#593, with #1415's semantic binding). #1611 tied `2:999` to pair 3 for this word.
- **The cold rank-4 records.** The eight records `0:124`…`0:327` are byte-identical to records in earlier provider files. One example is `research/complex-sw4-frame8-validation`; the `community-k492-audit` copies match up to the terminal frame id. #702 checked that family's cold wrappers by amplitudes, for PR626.
- **The four cold hyperplane-end records `0:1000`…`0:1003`.** They are hyperplane cases of #1697's audit of all 511 cold hyperplane terminals. That audit used wrappers its own run generated, not this word's stored bytes.
- **What was producer-only.** The 22 FULL-ended entrance wrappers had only producer evidence.

What this package adds: all 36 are now checked from the **selected** word's bound bytes, by two kernels, and tied to its programs.

## What this does not show

- **The executor bridge.** It does not show that the emitted program applies these records with exactly these semantics (Lemma G's H1 and the label bridge; see #1964).
- **Other recipes.** The child and endpoint records are #1781's, and the identity adapters are not checked.
- **Lean.** There is no Lean proof for the 34 records outside the Exact.lean pairs.
- **κ.** There is no new κ.

## Reproduce

```sh
python3 -I -B research/frontier1094-residual-wrappers-seed62/verify.py        # about 40 s; PASS_FRONTIER1094_RESIDUAL_WRAPPERS_EXACT
python3 -I -B -m unittest discover -s research/frontier1094-residual-wrappers-seed62 -p test_package.py
python3 scripts/research_package.py --package research/frontier1094-residual-wrappers-seed62 --check-only
python3.12 scripts/research_package.py --package research/frontier1094-residual-wrappers-seed62
```

Requires standard-library Python 3.10 or later. It was run on Python 3.12.15 and 3.14.8 (macOS 26.5, arm64).

## Open next questions

1. **Does the emitted executor apply the child, endpoint and residual records with exactly these semantics?**
   - Why it matters: record-level exactness, here and in #1781, still needs the bridge rec(A, B) = record circuit.
   - First step: replay one helper's full event sequence (`pre` wrapper, climbs, `post` wrapper) through an independent statevector executor and compare the result with C_[w] ⊗ I.
   - Blocked by: an independent executor for the emitted program format.
2. **Should the chain check the exactness receipt's content, not just its bytes?**
   - Why it matters: the fresh invoice pins `WRAPPER-CHECKS.json`, but nothing in the chain reads its status. This package's RESULT is an independent receipt that could be checked instead.
   - First step: propose a status check, or this package's RESULT digest, at the next frontier1094 integration.
   - Blocked by: a maintainer decision.
3. **Can Lean's `Clifford.check` kernel-check the 36 packed identities for this instance?**
   - Why it matters: two of them are already Lean-proved, so the rest would turn this replay into a formal result.
   - First step: emit the 22 FULL-ended identities as Lean `check` terms and time `lake build`.
   - Blocked by: a Lean toolchain, which is not installed here.

## Credit

- **Lean packages:** Lemma A (#516) and Lemma G (#509), both by DreamingOfClouds and formalizing #484.
- **The producer of the residual wrappers and `WRAPPER-CHECKS.json`:** `hpe_adapters_local.py` (DreamingOfClouds, after PR #458 by chafreaky). It uses `clifford_exact.py` (icekylinx), whose exact phase lowering adapts PR425 (jacklightChen).
- **`HyperplaneEnd/Exact.lean`:** jeremykothe2 (#593).
- **Calibration sources:** #1415 (commdata2338) and #702 (BigCactusLabs).
- **The packed kernel and binding:** our #1781.
- **Related checks:**
  - #1697 (navinor): all 511 cold hyperplane terminals;
  - #1611 (bbMisk): binding helper 450's wrapper pair;
  - #1964 (ours, open): Lemma G H1 extended labels.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic) via Claude Code.
- Parallel read-only scout and judge subagents selected the obligation and traced the producer-only evidence.
- The closed-form kernel, the verifier and the controls were then written fresh.
- A post-PR adversarial review corrected the supplier trace (the fresh invoice pins the receipt's bytes) and the overlap, and added the kernel cross-check and further controls (second commit).

No claim was posted to Discussions. New material is Apache-2.0.
