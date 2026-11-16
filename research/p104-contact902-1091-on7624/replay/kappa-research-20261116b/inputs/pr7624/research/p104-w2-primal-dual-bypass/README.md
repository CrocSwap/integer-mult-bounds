> **Additional exact-Q erasure applicability is unresolved.** This is a conditional candidate, not an equal-premise improvement over prior submissions. The signed receipt lists the five inherited assumptions only; its array does not certify the additional reset applicability required by the six changed matched-base CLEAR forms. Exact rational span certificates and accounted tariffs do not close that gap.
>
> Publication audit: the retained full native/signed execution logs and word bindings were inspected independently, but a clean end-to-end rerun through this final packaged launcher has not been performed. Full reproduction requires the separately pinned #7605 source closure. Run normal Python with assertions enabled; -O/-OO and --skip-pins are rejected. The publication-only launcher guards below do not change the scientific runners or candidate.

# CONDITIONAL κ = 0.003665051802188 — Primal-Dual Stationary Bypasses and Q-Rebased Cleanup on #7616

**Conditional signed κ = 0.003665051802188** (`916262950547/250000000000000`; exact raw crossing `0.0036650518021886040832049218630148 < C < 0.0036650518021886040832049218630149`).

> **Scope and Conditional Premises (MUST NOT be misread as an unconditional theorem or equal-premise dominance claim).**
> 1. **Inherited framework & boundary assumptions:** Conditional on the five retained framework assumptions (`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`), fixed `17 * 68 = 1,156` physical owned-bank reservation (`peak = 50 <= 68`), and the `#7113`/BIT signed caller contract.
> 2. **Stationary CLEAR extension + 6 Q-modified matched-base CLEARs (`clear-form-gap Q1`):** Unlike `#7616` (113 CLEARs = 74 unchanged base + 39 stationary), `#7617` (113), `#7620` (167), `#7621` (167), and `#7623` (180, all preserving the 74 base CLEAR Q-vectors verbatim), this construction contains **204 CLEARs (74 matched-base + 130 strictly stationary)** and in the final cleanup stage (`stage3g -> step1`, 29 replacement hunks) **modifies the exact-Q state vector at 6 matched-base CLEARs** (`base#[27, 37, 44, 54, 62, 63]`, including `base#44` / `owner 1557` at chart `595` and zero-row `base#27`). Every one of the **204/204 CLEAR certificates lies purely in the public-row span (`0..1500`, `cert_owned = []`, `min_other_rank = 1501`)** and all `204` lifetime charges + tape + precision context (`2,430 <= 4,096`) pass complete Step-3 checks (`ordinary = 791,379,412 < 10^9`, lower than pre-cleanup `stage3g`'s `791,407,904`). Even so, `#7609`'s unchanged-events theorem does not automatically cover modified base CLEAR Q-vectors or added stationary CLEARs (`clear-form-gap Q1`; compare PR `#7622`, which explicitly separates its unimplemented whole-private-extent reset premise `U`).
> 3. **Adapted Step-3 runners & vendored open-PR words:** `data/base7605.json.gz`, `data/w7616.json.gz`, `data/edits7605.json`, and `data/invoice-7616.json` originate from open PRs (`#7605`, `#7616`) not yet in `main` `base_commit` `e54523517d0f03e58352e647c403a5af3e525a57`, so they are vendored as data with pinned hashes (`SOURCES.json` pins only merged `main` files). Step-3 full native and 17-stage signed runs use explicit SHA-audited adapters ([adapters/native.json](adapters/native.json), [adapters/signed.json](adapters/signed.json), [windows_path_shim.py](windows_path_shim.py), audited in [evidence/step3-runner-diff-audit.json](evidence/step3-runner-diff-audit.json)).

## Comparison with Recent Open PRs (`#7616` .. `#7623`)

Notice different open PRs invoke different CLEAR-count/premise scopes; declared invoice comparisons (`uniformly_better` via `scripts/compare_recursive_invoices.py`) test histogram arithmetic only and **do not by themselves imply equal-premise dominance** until CLEAR/reset premises match.

| PR / Artifact | Author & Base | Conditional κ | Events / 17-call Paid | CLEARs (Base / Stat / Base-Mod) | Ordinary (17c) / Prec | Key Premise / Overlap vs `step1` |
|---|---|---:|---:|---|---:|---|
| [#7616](https://github.com/CrocSwap/integer-mult-bounds/pull/7616) | SYLforge (`#7605`) | `0.003656628302607` | 76,896 / 110,213 | 113 (74 / 39 / **0**) | 785,258,936 / 2430 | Direct construction base of `step1`; `uniformly_better` (`{1:-85,2:+1139,3:-2397,4:+1054,5:+34,6:+102}`) |
| [#7617](https://github.com/CrocSwap/integer-mult-bounds/pull/7617) | DreamingOfClouds (`#7616`) | `0.00365760025222` | 76,896 / 110,179 | 113 (74 / 39 / **0**) | 781,329,388 / 2430 | `(532/1464, 226/990)` couriers also present in `step1`; `uniformly_better` |
| [#7620](https://github.com/CrocSwap/integer-mult-bounds/pull/7620) | SYLforge (`#7616`) | `0.003661102618151` | 77,194 / 110,145 | 167 (74 / 93 / **0**) | 788,917,744 / 2430 | Independent primal/dual checkpoint (`6c46ad38...`, distinct word); `step1` continues primal/dual chain to 204 CLEARs |
| [#7621](https://github.com/CrocSwap/integer-mult-bounds/pull/7621) | DreamingOfClouds (`#7620`) | `0.0036614625547` | 77,196 / 110,145 | 167 (74 / 93 / **0**) | 785,022,672 / 2430 | Adds `1445/1461` courier (`755`/`757`) + `226` re-stop `719->906` (**neither is in `step1`**) |
| [#7622](https://github.com/CrocSwap/integer-mult-bounds/pull/7622) | Clear1nsight (`#7620`) | `0.003661727792` | 77,188 / 110,111 | 167 (74 / 93 / **1**: `#44/1557`) | 788,882,316 / 2430 | **Assumes unimplemented `common U`**. Shares `902@595` staydrop (same `owner 1557` Q-row `-e451+e1495`), **differs** on `902/1091` `618->373` contact rechart (not in `step1`) |
| [#7623](https://github.com/CrocSwap/integer-mult-bounds/pull/7623) | DreamingOfClouds (`#7621`) | `0.0036624027915` | 77,277 / 110,145 | 180 (74 / 106 / **0**) | 785,921,632 / 2430 | Ships `LOANBUILD` `engine/`. **14/14** `(r, X, p, c)` drop locations overlap `step1`: **10/14** exact `(r,p,c)` ADD match, **4/14** (`#0,#6,#10,#11`) cleaner/further-contracted in `step1` |
| `stage3g` (local ckpt) | on `#7616` | `0.003664744076078` | 77,409 / 110,077 | 204 (74 / 130 / **0**) | 791,407,904 / 2430 | Pre-cleanup checkpoint: zero modified base CLEARs (`diff=[]`); Step-3 not run separately (diagnostic only) |
| **`step1` (this package)** | **on `#7616`** | **`0.003665051802188`** | **77,372 / 110,060** | **204 (74 / 130 / 6)** | **791,379,412 / 2430** | **Full Step-3 native + 17-stage signed + 1,075 Gaussian + 204 public-span Q CLEARs verified** |

Detailed per-instance & hunk evidence: [evidence/overlap-and-clear-justification.json](evidence/overlap-and-clear-justification.json).

## Word Identity & Lineage

| Stage / Artifact | Events | Canonical SHA-256 | Gzip SHA-256 | Notes |
|---|---:|---|---|---|
| `data/base7605.json.gz` (`#7605`) | 76,636 | `e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd` | `37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d` | 74 base CLEARs |
| `data/w7616.json.gz` (`#7616`) | 76,896 | `bced9c9818cbbb130c74af97daa0172e1c5a3734a5c8f64d6f4d18dd79554f7a` | `ed760a6d4efc06ffdc831acd99b1a4661b09eb3cd82e2942a4783f4af0e52110` | 74 unchanged base + 39 stationary = 113 |
| Intermediate `stage1..stage3g` | 76,896 → 77,409 | `4ddf73ac0044a2e297b811c5a983899cbec29f6894c43486f5602c502252122e` (`3g`) | `ad1256b58bd9fe532913f213b12a9860aa171d3f5a2e1dec0cbff92bbad17a07` (`3g`) | 74 unchanged base + 130 stationary = 204 |
| **`data/word.json.gz` (`step1`)** | **77,372** | **`c14f365d254598f6a2daa349b47f815d20c649f0439cc36897b531412e19a3de`** | **`bfe2a4fb54dd82940ba78d8b3efd4f587e3fc9e978ccfd48561199d2c9fb4887`** | **74 matched-base (68 same, 6 Q-mod) + 130 stationary = 204** |

- Exact diff pin from `#7616` to `word.json.gz`: [data/edits-on-7616.json](data/edits-on-7616.json) (SHA-256 `bdad5bbb4692ccf651ec7d5f701aaa9e76a7117b1feeddd2d857f136ba8cda96`).
- Coefficient grid is unchanged from `#7616`: `odd_scale_lcm = 1125`, `dyadic_height = 25`, `max_numerator_bits = 24`, `max_denominator_bits = 20`, `odd = 5901` (zero non-dyadic additions), word precision bits `M=303 / Sigma=299 / Gamma=299`.

### The 6 Q-Modified Matched-Base CLEARs (`stage3g -> step1`, 29 replacement hunks)

Between `stage3g` (`0` modified base CLEARs) and `step1`, there are `29` opcode hunks (zero `INIT`/`CLEAR`/`SCALE`/owned-`MOVE` changes):
- **3 hunks (`#9, #13, #14`):** `role 902` bypasses `chart 595` (`#7608` stay drop), dropping native rank-1+rank-2 → rank-3 (`{1:-1, 2:-1, 3:+1}` per call, `{1:-17, 2:-17, 3:+17}` over 17 calls) and changing `base#44` (`field=1557, chart=595, dim=1`, `sup 4 -> 2`: `{451:-1, 1495:1}`, matching `#7622`).
- **26 hunks:** remove dead/canceling `ADD` instructions across stationary lifetimes and base CLEARs, reducing event count (`77,409 -> 77,372`) and lowering ordinary bill (`791,407,904 -> 791,379,412`, `-28,492`):
  1. `base#27 -> step1#99` (`field=1509, chart=595, dim=1`): `sup 225 -> 0`, `other_rank=1501`, `terms=0` (zero-row CLEAR; dead `ADD 1509, 572, 1` stripped, paired with inverse ADDs at `chart=603`).
  2. `base#37 -> step1#119` (`field=1546, chart=1090, dim=4`): `sup 291 -> 212`, `other_rank=1501`, `terms=38` (dead `ADD 1546, 1397, 1, 1090` stripped).
  3. `base#44 -> step1#147` (`field=1557, chart=595, dim=1`): `sup 4 -> 2`, `other_rank=1501`, `terms=21` (role `902` `F595` bypass).
  4. `base#54 -> step1#184` (`field=1525, chart=245, dim=8`): `sup 2 -> 113`, `other_rank=1501`, `terms=2` (dead `ADD 1525, 769, -1, 245` stripped).
  5. `base#62 -> step1#192` (`field=1513, chart=243, dim=4`): `sup 165 -> 189`, `other_rank=1501`, `terms=3` (dead `ADD 1513, 1389, 4, 243` stripped).
  6. `base#63 -> step1#193` (`field=1509, chart=603, dim=2`): `sup 0 -> 225`, `other_rank=1501`, `terms=20` (paired `chart=603` inverse ADDs stripped).

All **204/204 CLEAR certificates** (197 dirty + 7 zero-row at events `[526, 576, 595, 744, 864, 913, 922]`) use **public rows `0..1500` only** (`cert_owned = []`, zero inter-owned dependencies) and keep fixed reservation `17 * 68 = 1,156` disjoint physical banks (`init_clear_allowance = 816`, `owned_lifetime = 816`, `context_c = 2,430 <= 4,096`).

## Cost, Ordinary Bill & Precision

- Native per-call inventory: `bad_inputs = []`, `total_paid = 6252` (`{1: 3980, 2: 950, 3: 623, 4: 305, 5: 352, 6: 25, 7: 11, 8: 6}`).
- Complete 17-call signed invoice ([evidence/invoice-step1.json](evidence/invoice-step1.json)): `paid_positions = 110,060`, `productive_fields = 22,461`, `rank_surplus S = 1,424`.
- Ordinary upper bill ([evidence/SIGNED.json](evidence/SIGNED.json)): **`791,379,412 < 10^9`** (`margin_to_billion = 208,620,588`).
- Caller grid & precision ([evidence/SIGNED.json](evidence/SIGNED.json)): `context_height = 406`, `context_mass_bits = 1215`, `context_c = 2430 (<= 4096)`, `H = 16608300000000000000000`, `Kstar_bits = 14093`, `preproduct_exact_divisions = 176874`, `safe_valuation_bound = [381, 69, 62]`, `outer = {strict_count: 54, functional_count: 4, minimum_margin: 1e-18, BIT_just_below_effective_rejected: True}`.

## Verification & Receipts

1. **Registered CI-safe package checks (`VERIFY.json`, stdlib only, <20s total):**
   ```sh
   python3.12 -B scripts/research_package.py --package research/p104-w2-primal-dual-bypass
   ```
   - `verify_lifetimes.py`: `PASS_STEP1_LIFETIMES 204 (74 base + 130 stationary), peak 50/68, 17*68=1156 banks`
   - `verify_certificates.py`: `PASS_STEP1_CERTIFICATES 204/204 (dirty=197, zero=7; matched_base=74: 68 unchanged, 6 modified [27, 37, 44, 54, 62, 63]; controls=3/3 rejected)`
   - `price.py`: `PASS_PRICE_STEP1 kappa=0.003665051802188 (bracket [0.003665051802188, 0.003665051802189]); uniformly_better vs #7616 & #7617`

2. **Full Step-3 Adapted Native & 17-Stage Signed Replay ([evidence/NATIVE.json](evidence/NATIVE.json), [evidence/SIGNED.json](evidence/SIGNED.json), [evidence/PRICE.json](evidence/PRICE.json), [evidence/step3-native.log](evidence/step3-native.log), [evidence/step3-signed.log](evidence/step3-signed.log)):**
   ```sh
   python3.12 -B reproduce.py --source /path/to/pr7605/research/p104-timed-helper757 --work /short/work --stage all
   ```
   Observed full replay results on the exact pinned `word.json.gz`:
   - `PASS_W3H_ADAPTED_COMPLETE_NATIVE 0.003664263365377` (`PASS_HOST3 decoupled ports 96 hosted ports 8`, `replayed 77372 events, 3034 chart pairs, 22s`, `PASS_PHYSICAL 29s`, `signed_routes: PASS_PHYSICAL_RANK9_ALGEBRA paid_calls=32`, controls `11/11` rejected).
   - `PASS_W3H_ADAPTED_COMPLETE_SIGNED_APPLICATION 0.003665051802188` (`emit_odd_type_b` 3877 events, `emit_odd_type_ab` 4783 events, caller grid 176874 checks, physical binding `110060 / 13600 / 22461`, fixed tape counts `44333376 / 25399292960`, catalogue `3116/3116` component checks passed).
   - Standalone `512` forward + `512` adjoint Gaussian column + signed Pauli + wrong-phase checks over all `1,075` affected `(a, b)` chart pairs vs `#7481` recorded in [evidence/quick_audits.json](evidence/quick_audits.json) (`650.91s` offline).

## Overlap & Attribution

- Constructed for **SYLforge** (`#7603`, `#7616`, `#7620`) with AI assistance (Antigravity / Gemini / Claude Opus / Codex verification).
- Directly extends `#7616` (`research/p104-w2-stationary-followup`, itself on `#7605`, `#7611`, `#7612`).
- Explicit overlaps: role `902` `F595` bypass overlaps `#7608` (`DreamingOfClouds`) and `#7622`'s `902@595` splice (`Clear1nsight`, same `owner 1557` CLEAR vector, while `#7622`'s `902/1091` `618->373` contact rechart is absent here); role `226` `(719, 127)` overlaps `#7615`/`#7617` (`DreamingOfClouds`); `#7623`'s 14 stop locations (`DreamingOfClouds`, using SYLforge's `#7616`/`#7620` device) match `step1` in location/partners (10/14 exact `(r,p,c)` ADD sequences, 4/14 simpler or further-contracted in `step1`); `#7621`'s `1445/1461` courier and `226` re-stop are absent from `step1`.
- Retained predecessor credits in [NOTICE](NOTICE) and [BASE-NOTICE](BASE-NOTICE): Ali Romman (`#7605`), SYLforge (`#7603`/`#7616`/`#7620`), DreamingOfClouds (`#7601`..`#7623` series), Clear1nsight (`#7244`..`#7481`, `#7612`, `#7622`), Hao Yan / FanPUYen (`#7604`), ToikY (`#7546`/`#7544`), Rohan Arun (`#7113`/`#7277`/`#7480`), CubeJerry (`#7577`), Nick Petalas (`#7326`), dillona, Douglas Colkitt, Tekalign, mightyOil, Maxime Fleury, Antoine Olivier. Apache-2.0.

## Open next questions

1. **Inherited framework & caller assumptions (`TASK.json` Q1):** Do W2's five inherited framework assumptions (`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`), fixed `17 * 68` bank reservation, and the `#7113`/BIT signed caller bounds hold unconditionally? See `docs/audit.md`, `#7605`, `#7616`, `#7620`, and `#7113`.
2. **Q-certified CLEAR content erasure (`TASK.json` Q2 / `clear-form-gap Q1`):** Does formal `owned_erasure` (under verified `204`-lifetime `791,379,412` ordinary / `2,430` precision / `17*68` banks, without needing `#7622`'s separate unimplemented `common U` change) cover arbitrary public-span Q-certified CLEAR erasure for the 130 stationary CLEARs and 6 Q-modified matched-base CLEARs (`[27, 37, 44, 54, 62, 63]`)? Compare `stage3g` (`0.003664744076078`, 0 modified base CLEARs) vs `step1` and inspect [evidence/certs-step1.json](evidence/certs-step1.json) + `verify_certificates.py`.

Publication hygiene: local home prefixes in diagnostic paths and diff headers are replaced with `<LOCAL_HOME>`; scientific values, word bytes, runner diff bodies and receipts are unchanged.
