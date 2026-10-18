# Selected #1094 certificate: invoice/outer recheck and replay-binding gap

**Adversarial audit; no new κ; no defect in the current certificate.**

The committed #1094 certificate passes an independent recheck of its finite
invoice, bootstrap chain and all 47 + 47 outer slacks, and its profile agrees
across five artifacts.

The audit also finds a **check-level binding gap** in the selected record's
reproduce command, `make frontier1094-verify`. That command binds the committed
certificate to its cold replay **only through κ**. A well-formed certificate
that claims an uncertified complex endpoint, with every arithmetic identity
recomputed so κ is unchanged, is:

* accepted by the selected-record check once its hash pin is updated, and
* never compared with the replay output.

Only an exact moment evaluation, outside the reproduce path, rejects it.

The current certificate is not affected. The published replay output and the
recorded `assembly_sha256` are byte-identical to it. A one-line binding is
proposed below as a handoff; it is not applied to the selected script.

## Results

1. **Invoice and outer recheck of the committed #1094 certificate: PASS.** This
   applies Wronskode's
   [frontier1042-invoice-audit-seed81](../frontier1042-invoice-audit-seed81/README.md)
   recheck, unchanged and loaded as its exact Git blob. The recheck covers:
   * profile composition, per-vertex envelope and the nine finite guards;
   * 7 + 7 bootstrap levels and 47 + 47 outer slacks;
   * κ as the last 10⁻¹⁸ grid point below the absorption margin;
   * the four outer controls and all 15 mutation controls.

   The package binds the certificate directly, by path and SHA256
   `1122cb3a…3045` (the `certificate_sha256` of the selected record at the
   base), not through the moving `selected-result.json` pointer. As a positive
   control, it reproduces seed81's published #1042 result exactly from the
   frozen #1042 checkpoint.
2. **Seed81's own entry point is stale.** It requires the *selected* certificate
   to be #1042's, so `make frontier1042-invoice-audit-verify` now stops with
   `FAIL selected certificate path moved`. The #1042 recheck still holds through
   this package's checkpoint-bound loader. The suggested repair is to read
   `certificates/checkpoints/frontier1042.json` instead.
3. **The #1094 invoice arithmetic is unchanged from #1042.** The receipts differ
   in exactly 14 fields:
   * `PREFIX-AND-INVOICE.json`: only three provenance hashes;
   * `OWNERS-AND-PROFILE.json`: those hashes, the idle-remainder profile
     (ranks 1, 2, 3, 7, 16 and 48), the idle child count (7,550 → 7,526),
     `actual_73column_sigmas` and `cross_replica_helper_roles`.

   The envelope and guards are therefore identical to #1042's, which is
   consistent with #1094's idle re-placements.
4. **Profile binding.** The certificate's `complex_profile` equals all four
   other copies:
   * the archived owner receipt's `paid_profile`;
   * the package's `PROFILE.json`;
   * the package's `data/PLAN.json`;
   * the owner-audited profile in `INDEPENDENT1094.json`.

   The maintainer composition (`check_frontier1094.py`) prices the owner-audited
   profile but does not itself compare it with the certificate. The values agree.
5. **Mutant certificate.** The complex endpoint `b` is replaced by `b + 10⁻²⁴`,
   the next grid point. The bootstrap, the 47 outer slacks and both complex
   moment records are recomputed with seed81's formulas, and κ stays
   `836330098538459/5·10¹⁷`. Results by layer:

   | Layer | Mutant |
   |---|---|
   | Seed81 invoice/outer arithmetic (endpoint taken as data) | accepted |
   | `verify_selected_result.check` with `certificate_sha256` re-pinned | accepted |
   | `verify_frontier1094.py` cold replay and its candidate stage | never read the committed certificate |
   | Exact moment, via `selected-suppliers-de-diagnostic`'s enclosure | **rejected**: residual > 1.62·10⁻²⁴ |

   The cold replay contains no reference to the #1094 certificate path, the
   selected record or `certificate_sha256`. Its only certificate-related string
   is the historical `certificates/checkpoints/frontier1042.json` stage.

   Its candidate stage (`complex-t16-rare-pattern-exchanges/verify.py`)
   regenerates the assembly with the unchanged PR1087 strict verifier. It then
   binds only the replay's status, its κ and its `complex_profile`, the last
   to the package's `PROFILE.json`. It never names `complex_lower`,
   `bootstrap`, `outer`, `moments` or `conservative_outer`.

   At the certified endpoint, the residual is below −1.30·10⁻²⁴ (accepted). As
   a control, the selected check does reject a κ edit (`Selected kappa differs
   from finite certificate`). So the record's hash pin says *which bytes* are
   selected, and the replay says *which κ* is reproduced. Nothing on the
   reproduce path says those bytes are the replay's output.

## Proposed handoff (not applied)

Add one requirement in `scripts/verify_frontier1094.py` after the replay:

```python
require(sha(work/'candidate/strict/ASSEMBLY.json') ==
        read(ROOT/'certificates/selected-result.json')['certificate_sha256'],
        'Replay output is the selected certificate')
```

If cross-platform byte determinism is in doubt, compare parsed JSON instead.

This package shows the requirement holds on the published replay output: the
archived `candidate/strict/ASSEMBLY.json` and the recorded `assembly_sha256`
both equal the certificate. It also shows the requirement rejects the mutant.

A fresh cold replay with the added line was **not** run here. It needs the full
#1042 baseline replay, which is long, and editing the selected reproduce script
is a maintainer decision.

Statically, `scripts/verify_frontier1042.py`, `verify_frontier942.py`,
`verify_frontier890.py` and `verify_frontier799.py` also contain no reference
to their committed certificates. They were not audited further.

## Reproduce

Standard library only, plus `git` with history for the base commit. From the
repository root:

```sh
python3 scripts/research_package.py --package research/frontier1094-certificate-binding-audit --check-only
python3 -I -B research/frontier1094-certificate-binding-audit/verify.py
```

Expected (about 5 seconds):

```text
PASS_FRONTIER1094_CERTIFICATE_BINDING_AUDIT invoice_outer=PASS controls=15 receipt_delta=14 profile_copies=5 mutant_accepted_by=arithmetic,selected_check mutant_rejected_by=exact_moment no_new_kappa
```

[RESULT.json](RESULT.json) is the regenerated receipt; `--write` rewrites it.

Five pieces of audited code are loaded as exact Git blobs at base `0b1cccf8`,
so a later repair does not change what this package checked:

* seed81's `verify.py`;
* the endpoint package's `verify.py`;
* `scripts/verify_selected_result.py`;
* `scripts/verify_frontier1094.py`;
* the candidate stage `research/complex-t16-rare-pattern-exchanges/verify.py`.

The data inputs are pinned in [SOURCES.json](SOURCES.json). The mutant exists
only in a temporary directory during the run. The script refuses to run under
`-O`.

## Scope and limits

This audits the binding and arithmetic from the frozen receipts to κ. It takes
the receipts' semantic content as data: words, owners, hosting and local
replays. It re-establishes no moment endpoint beyond the two exact residual
evaluations above.

* **Not run:** the cold replay, the native or hosted pipeline, and the
  all-size/compiler, precision/tape, analytic and H1–H5 obligations. These are
  unchanged and inherited.
* **Environment:** run on Windows with CPython 3.14. The registered Python 3.12
  replay was not run locally; `--check-only` passes.

## Open next questions

1. **Should the selected reproduce path bind the certificate to the replay
   output?**
   * *Why it matters:* today a promotion that commits a non-replay certificate
     with the same κ would pass `make frontier1094-verify`. The certificate's
     endpoints and outer slacks are what downstream audits read.
   * *First step:* add the requirement above and run one cold
     `make frontier1094-verify` on Linux, comparing raw and parsed equality.
   * *Blocked by:* maintainer authorization to edit the selected reproduce
     script, and the long cold baseline replay.

## Related work

* **#474** (artuskg, open) identified the same class of gap for the historical
  gen4 record. Its `gen4-bank-verify` "does not compare that replay's
  certificate with the frozen publication", and it adds a recursive comparison
  helper, `scripts/check_selected_replay.py`. That helper is a natural way to
  implement the handoff above for #1094. This package claims no priority for
  the pattern; it establishes the gap on the current selected path, with a
  concrete mutant.
* **#1277** (merged) covers the reuse-mode ancestry binding of the same
  replay, and **#1654** (open) is the overlap receipt for the #1094
  replay-tooling family. Neither adds a certificate-to-replay comparison.
  #1654 also notes the same moving-pointer staleness in another capsule audit.

## Credit

Prepared for rtyu193-rgb with Claude Code (Anthropic Claude Opus 5.5) in one
session, with no subagents and no independent human review. Apache-2.0.

* **Wronskode:** the seed81 invoice/outer recheck, reused unchanged.
* **Navinor:** the `selected-suppliers-de-diagnostic` exact moment enclosure,
  reused unchanged.
* **Douglas Colkitt:** the selected reproduce scripts and the
  `check_frontier1094.py` composition.
* **Construction lineage:** Rohan Arun (#1094), with Jeremy Kothe's k8/T16
  construction and the supplier lineage credited in the selected review. Josie
  Elliston (#1091) and Sagar Thakrar (#1069) supplied the auditors applied by
  that composition.

No predecessor file is modified.
