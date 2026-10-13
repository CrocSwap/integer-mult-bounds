# Proof note: the global code for provider helper count R (R = 492 in complex-571-cold14-k492)

**Scope.**
- Code: `code/{bind_providers_portable,emit_allcold,audit_allcold,invoice_allcold,assemble,assembly_controls,generated_identity_controls,witness}.py` of this package.
- Base: complex-571-cold14-b3, whose six global scripts are byte-identical to complex-571-cold14-e1's.
- The generalisation is GlobalR's (scratch `GlobalR/generalise-R.diff`), with three review fixes:
  1. The width-8 spot check is restored, not dropped.
  2. The cold-helper width-swap control is restored without the skip.
  3. The register of the generated-identity same-rank start-frame mutation follows the helper map.

**Geometry.** There are v = 112 data ports and h = 9. A provider word has R helper registers `[2v, 2v+R)`, so n = 2v+R. Two helper counts appear in the code:
- **R**: the helper count of the provider words that the hosted calls run. It is read from `word['R']`, and every step asserts that all providers share one value.
- **R0 = 504**: the helper count of the fixed *parent* template, which is the baseline558 split-centres word and its dedicated-bank global template. The parent enters only as geometry and an overcharge envelope:
  - `parent_live` 11704 = 7168 + 9·504 banks;
  - `parent_physical` 12218 = 11704 + 504 + 8 + 2.

The inherited code wrote both counts as the literal 504. That is sound when R = R0 and wrong otherwise.

**Spot helpers.** `witness.SPOT` = `SPEC.width_spot_helpers`, defaulting to PR558's helpers (270, 282, 294, 306). For a K-triangle package, `verify.py` asserts that the spec value equals the images of those four helpers under the constructor's `HELPER-MAP.json`. Here that is [264, 276, 288, 300].

**Per-site revert controls.** `revert_controls.py` (scratch `Stack492/`) runs each control:
1. It patches one site back to its 504 text in a temporary copy of `code/`. The site's text must match exactly once.
2. It re-runs the chain listed in the tables below on the fixture's own inputs.
3. It records `pass_identical`, `pass_changed` or `fail`, with the failing assertion.

Expectations: on R = 504 every revert must pass with identical outputs, apart from `seconds` fields. On R ≠ 504 every R site must fail; the R0 and cosmetic sites must pass.

## Sites (32), each with its revert control and the observed result on the R = 492 strict fixture

Fixture: `cands/K1/strict`, the strict `verify.py` run of this package (κ 0.00163542231500688). Report: `REVERT-492.json`, **ALL_AGREE, 32 sites, 47.7 s**.

| site | file | generalised | revert (504 text) | kind | why it is the same quantity | R=492 observed |
|---|---|---|---|---|---|---|
| bind.word_R | bind | `(v,h,centres)==(112,9,8)`, R a positive int, one R across providers | `(v,h,R,centres)==(112,9,504,8)` | R | the bound word's own helper count | fail (AssertionError) |
| bind.helper_range | bind | `range(2*112,2*112+word['R'])` | `range(224,728)` | R | helper registers are `[2v,2v+R)` | fail (IndexError) |
| bind.spot_width8 | bind | `widths[h]==8 for h in SPOT` | `… in (270,282,294,306)` | R (helper map) | the same four PR558 helpers, renumbered | fail (AssertionError) |
| emit.R_from_providers | emit | `R=pc['R']` (all providers equal) | `R=504` | R | hosted calls run the provider words; the old code took R from the parent | fail (IndexError) |
| emit.roles_72R | emit | `len(roles)==72*R` | `72*504` | R | one role per (call, helper) | fail |
| emit.widths_range | emit | `for h in range(R)` | `range(504)` | R | one width per helper | fail (IndexError) |
| emit.all_helpers_owned | emit | `set(bycall[k])==set(range(R))` | `range(504)` | R | every helper of a call is owned | fail |
| emit.physical | emit | `physical=DATA+C+R+2` | `+504+` | R | stock = data + centres + R helpers + 2 coefficient columns | fail (independent audit) |
| emit.reserved_tableau | emit | `[DATA+C,DATA+C+R]` | `+504` | R | the private tableau holds R helper columns | fail (independent audit) |
| emit.parent_R0 | emit | `parent physical-live==C+R0+2` | `C+R+2` (provider R) | R0 control | parent stock identity | fail |
| emit.version_label | emit | `'round20-R%d-…'%R` | `'round20-R504-…'` | cosmetic | a label that no check reads | pass_changed (expected pass) |
| audit.spot_width8 | audit | `widths[h]==8 for h in SPOT` | PR558 indices | R (helper map) | as bind | fail |
| invoice.recount_R | invoice | `(v,h)==(112,9)`, helpers = `w['R']` | `(v,helpers,h)==(112,504,9)` | R | helper count of the recounted word | fail |
| invoice.run_R_n | invoice | common provider R, `n=2v+R` | `helpers=504; n=728` | R | n = 2v+R | fail |
| invoice.parent_R0 | invoice | `parent_physical==parent_live+parent_helpers+…` | `+helpers+` | R0 control | parent stock identity | fail |
| invoice.route_items | invoice | `+2*call_count*helpers` | `*504` | R | per-call in/out routes of the R hosted helpers (PR531 invoice_final); assemble recounts with `2*72*R` | fail (assemble) |
| assemble.R | assemble | `R=invoice['helpers']` | `R=504` | R | invoice helper count, equal for every provider | fail |
| assemble.owners_per_call | assemble | `==2*112+R` | `==728` | R | whole owners per call = 2v + R | fail |
| assemble.hosted_72R | assemble | `==72*R` (new, stronger) | `==72*504` | R | one helper owner chart per (call, helper) | fail |
| assemble.stock_helpers | assemble | `local_helpers=R` | `504` | R | physical stock term | fail |
| assemble.provider_helpers | assemble | `p['helpers']==R` | `504` | R | provider helper count | fail |
| assemble.provider_n | assemble | `p['n']==2*112+R` | `728` | R | exact columns | fail |
| assemble.width_sum | assemble | `9*R-entrance-codim` | `9*504-…` | R | Σ widths over R helpers | fail |
| assemble.width_len | assemble | `len(widths)==R` | `504` | R | one width per helper | fail |
| assemble.exact_columns | assemble | `all_exact_columns==2*112+R` | `728` | R | n = 2v+R | fail |
| assemble.dirty_columns | assemble | `dirty_helper_columns==R` | `504` | R | R helper columns restored | fail |
| assemble.local_adapters | assemble | `16*(macros+children+2*112+R+8)+64*73` | `+728+8` | R | adapter formula with n = 2v+R | fail |
| assemble.route_items | assemble | `+2*72*R+` | `+2*72*504+` | R | matches the invoice term | fail |
| assemble.parent_banks | assemble | `+9*parent_banks+`, with `parent_banks=(11704-7168)/9` asserted = 504 | `+9*504+` | R0 | parent geometry, independent of the providers | pass_identical (expected pass) |
| assemble.spot_width8 | assemble | `p['widths'][h]==8 for h in SPOT` | PR558 indices | R (helper map) | as bind | fail |
| controls.swap_spot | assembly_controls | `cold_helper_width_swap_h` for h in SPOT | `for h in (270,282,294,306)` | R (helper map) | at a PR558 index of width 9 the swap is the identity; strict mode then reports "Invalid admission receipt accepted" | fail (`ck:cold_helper_width_swap_294` accepted) |
| identity.start_register | generated_identity_controls | `r = 2*112 + SPOT[2]` | `r = 518` | R (helper map) | same-rank start-frame mutation of an entering helper (PR558 helper 294; image 288, register 512) | fail (StopIteration: register 518 is rank 0 here) |

### Other changes in this package's verifier, beyond GlobalR
- In `generated_identity_controls.py`, the mutation `all_exact_columns` → 727 became `all_exact_columns − 1`. This value is 727 for R = 504, so it is bit-exact there, and it stays a wrong column count for any R. On R = 492 the old 727 was also wrong (actual 716), so it was not unsound, only literal.
- `verify.py` gains the `k_triangle` base, the `port_stage` and `frame_regroup` step types, the shadow chains, the `width_spot_helpers` ↔ HELPER-MAP check, and support for PR531's `{algorithm, sha256}` source manifest. None of these touch R constants. `verify.py`'s other `224` uses are 2v.

### Unchanged quantities, independent of R (asserted as before)
- v = 112, h = 9, 8 centres, M = 73, live 7168.
- Deficit `73·7168 − mass = 2560`, so rank mass is 520704.
- The halving pair [5329, 4608], from maxchild 48.
- `endpoint_adapters == 224`, which is 2v.
- The gate-move indices `-224` and `112<=e[1]<224`, which are v quantities.

### How R enters κ
κ = `outer_witness(b)`, where b is the certified complex lower endpoint of the moment problem for the global paid profile H (W = live = 7168, deficit 2560). R therefore enters κ only through H: each provider's local paid profile over its dispatched calls, plus the idle remainders the owner map leaves. The physical stock (7168 + 8 + R + 2 = 7670 here), owners_per_call (2v+R = 716), hosted residuals (72R = 35424) and the routing term enter only the strict finite inequalities. All of these get easier as R shrinks.

## Evidence
- **R = 492.**
  - `REVERT-492.json`: ALL_AGREE, 32/32. Every R site fails, both R0 controls fail, `assemble.parent_banks` passes identically, and the version label passes changed.
  - Fixture spot widths at the PR558 indices: ck [7,8,9,7], jp8 [8,9,9,8]. At the map images they are [8,8,8,8] for ck, jp8 and atm3 (the bind/audit/assemble checks pass).
- **R = 504.** `REVERT-504.json`: ALL_AGREE, 32/32 pass_identical. The fixture is GlobalR's `run504b` (a full generalised run of complex-571-cold14-e1, κ 0.001626010676080313 = SPEC), run with this package's eight global files and that package's data. So the restored checks and the helper-map defaults reproduce the 504 outputs exactly.
- **Strict.** This package's strict `verify.py` passes with these files: PASS_COLD14_NATIVE_COMPLEX_AND_CITED_BIT, κ 0.00163542231500688.
