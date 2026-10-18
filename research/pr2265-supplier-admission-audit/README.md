# Supplier-admission audit of the #2265 substitution, traced into PR2260

**Status: adversarial audit / research note. No new kappa, no construction.**
No FALSE or MISSING-PROOF premise was found. The finite premises were checked here
with independent code. The remaining premises are interface hypotheses located in
the sources but not provable from shipped data.

## Question

PR #2265 (DreamingOfClouds, head `49ce38fe`) applies the PR1673 capped phase-cell
fusion outer to the PR2260 selective-borrowing supplier (Dugongue, head `fde6b107`).
Its README marks three substitution items as "inherited from PR2260; not
re-derived": the completed-call/dirty-borrowing premise, the semantic guard, and
the equal-chunk bit interchange. The PR asks for an independent check. This audit
asks whether each supplier-admission premise of the substitution has a supporting
statement or data check in PR2260, and whether it holds on the shipped data at
#2265's final point. The audit covers four groups:

- (A) Borrowing stays inside the call and is restored.
- (B) The guard, C_0 and row constants.
- (C) The retained bit endpoint and the interchange premise.
- (D) The numeric substitution facts.

The stop-parameter relations are already #2265 ledger rows and were audited for
T74 in #2286, so they are excluded.

## Result

[INVENTORY.json](INVENTORY.json) lists 15 premises with file:line pins and one
class each:

| Class | Count | Premises |
|---|---:|---|
| COVERED (checked by #2265 or a PR2260 check it reruns; independently re-confirmed here) | 9 | A2 restoration replay, A3 hosting 72x436 and owner rows, B2 C_0<2^210000, B3 row 16467<20161, C1 bit endpoint, D1 73²>2·48², D2 W/mass/deficit, D3 q<a_eff<b<c, D4 endpoint and kappa |
| TRUE-unencoded (true under an independent exact check; not checked by #2265 or a check it reruns) | 1 | A1 call closure, namespace/metadata part only: warps = WITNESS pairs, public arrays = namespace minus removed aliases, owned arrays outside the namespace, handoffs exactly on the borrowed sources |
| INHERITED-traced (statement located; interface premise not checkable from finite data here) | 5 | A4 serialization windows, B1 semantic guard units, C2 equal-chunk interchange, C3 C_1=1, D5 endpoint admissibility (surcharge envelope or PR559 license) |
| MISSING-PROOF / FALSE | 0 | none |

A2, B2 and B3 are COVERED because #2265's `verify.py` reruns PR2260's `local/verify.py`
(both restoration replays) and `local/invoice.py` (#2265 `verify.py:43`, `:68-69`).
This audit re-confirms them with independent code.

A1 is only partly new. The same rerun already enforces event closure: PR2260's
`local/check_trace.py` keeps state only for the trace's `active_registers` and the arrays its
own COPY/zero-buffer events create, so an event on any other register fails `local/verify.py`.
That script also requires exactly 76 created private arrays, all cleared by the postlude
(`local/verify.py:91-92`), and pins 660 public columns and 76 private fields in
`expected-local.json`. Rank-0 handoffs are enforced at `check_trace.py:75`. The owner-row facts
are checked by PR2260's `owners/verify.py` (`:87`, `:88-89`, `:95`, `:106`, `:113`), which #2265
reruns at `verify.py:44`; they are listed under A3. What these checks do not bind is the
namespace. `check_trace` takes `active_registers` as given and accepts, for example, the forward
trace with COPY register 1364 renamed to removed alias 597. The shipped trace is hash-pinned, so
this concerns what the replay checks, not the shipped data. Only the namespace/metadata sub-facts
are TRUE-unencoded (INVENTORY `class_scope`, `covered_part`).

What the independent checks establish:

- **A1, call closure.** Both orientations of the literal local word were checked: 21,065 forward and 21,381 backward events. Every event touches only the call's 660 public arrays (224 data, 436 helpers) and 76 owned private arrays; PR2260's replay already enforces this. Checked only here:
  - the 44 warps equal the 44 pairs of PR2260's `local/inputs/WITNESS.json` (a selected subset of PR2226's witness);
  - the public arrays are exactly the original 704-register namespace minus the 44 removed aliases, and the 76 owned private arrays lie outside that namespace, so no event references a removed alias;
  - all 44 borrowed sources are public inputs of the same call, and handoffs occur exactly once at each of them, with paid rank 0 in the WITNESS and warp metadata.
- **A2, restoration.** An exact replay over a free group of reference-change symbols with rational coefficients was written for this audit. It starts every public array as an independent label, so arbitrary dirty contents are covered.
  - In both orientations, all 660 columns end at the declared normalized shear and all private arrays end at zero.
  - The paid profile is {1:2424,2:418,3:429,4:141,5:42,8:8}.
  - This is a third replay of PR2260's event model, not a different model; see Scope.
- **A3/D2, owner recount.** The pending children were reconstructed from the hosted parent's pooled blocks plus its idle residuals: 16,128 children with rank mass 387,072. The new owners host 254,088, leaving 132,984.
  - The residual histogram {1:1724,3:20,5:1469,6:18,7:494,32:11,39:7,48:2493} reproduces PR2260's EXPECTED and its PROOF.md partition.
  - 72·local + residual equals the SPEC profile, with mass 520,704 and deficit 2,560.
  - All 31,392 owner rows lie in inherited pending children of the same hosted parent. Within each child the rows form disjoint exact prefixes, and no row uses an active data family of its own call. PR2260's `owners/verify.py` checks the same facts.
- **B2/B3, finite constants.** The values were recomputed from the retained formulas: 7745 physical families, stock bit length 2641, row 16467 < 20161, and 200012 required C_0 bits. The |O(2k+1,2)| formula was checked by brute force for n = 3 and 5.
- **C1, bit endpoint.** c equals PR2260 BIT-EXPECTED, which is byte-identical to the base `research/e8-bit-p111-tuned/tune/EXPECTED.json`. The conservative bit moment at c is 1 − 1.599e-24.
- **D3/D4, endpoint and ordering.** The moments were evaluated with 320-digit correctly rounded decimal ln/exp, with error below 1e-316:
  - native moment at C: 1 − 8.387e-12;
  - conservative moment at C: 1 − 2.884e-200;
  - conservative moment at C + 1e-200: 1 + 3.157e-202.

  In exact rationals: a − q = 5e-281, b − a = 1.5e-280, c − b = 5.0014e-5, and kappa = C − 1e-246 − 1e-222.

### New observations (not defects)

1. **One borrowed source is a data input.** 43 of the 44 borrowed sources are helper inputs. The other is register 73, the X-side data input, borrowed for removed alias 653.
   - The pair originates in PR2226's 80-alias witness (head `dacaf3d8`, `research/anticipatory-dirty-borrowing/WITNESS.json`) and is carried into PR2260.
   - PR2260's model already covers it: `PROOF-LOCAL.md:22` treats all "660 independent public/data/helper inputs" as arbitrary. Only helper-specific wording elsewhere (for example PR2226's "high helpers can use distinct retired fields" and the outer's "dirty helper/spectator coordinates") is imprecise. This is a precision note, not a gap.
   - This stays inside the call.
   - In the forward orientation it is returned to its input.
   - In the backward orientation it ends as the declared shear column X_73 − Y_185.
   - So the "completed call" premise holds for this word, but a reader should not take "borrowed = helper" literally.
2. **Guard units (B1) are a lineage-wide question, not a PR2260 gap.** Both self-consistent readings pass at the supplier: under the lineage's fixed-bit rule the prefix is 248 < 512, and under PR2260's per-lambda rule it is 244·lambda < 512·lambda.
   - The only PR2260-specific point: `finite-invoice.json` states "Payload512 is a per-lambda magnitude coefficient, not a fixed bit count", and no retained-lineage source for that convention was located. The selected lineage compares a lambda-free prefix with a fixed 512 (`docs/research/community-batch952-review.md:51`, `scripts/verify_frontier1094.py:94-96`, `direct-delivery504-global/code/invoice_final.py:238-241`).
   - Mixed readings only matter if units are combined inconsistently. Against a fixed 512, PR2260's literal prefix 207 + 37·lambda fits for lambda ≤ 8 (its relaxed bound 244·lambda for lambda ≤ 2). If the row term 2·payload = 1024 scaled with lambda, row < 20161 would need lambda ≤ 4.
   - The same mixed readings bind the selected #1094 equally or more tightly: its row 16469 would need lambda ≤ 4, and its 397-bit prefix with the 37-bit conversion scaled would need lambda ≤ 4. `verify.py` checks all five thresholds exactly.
   - The outer consumes 20161 as a fixed degree gap (PR2260 `PROOF.md:104-105`). For #2265 the PR1673 outer needs only an O(g) supplier guard constant (review, lines 73–78).
3. **Identical invoice fields are explained, not copied.** PR2260's physical_stock_bits 2641, row 16467 and required_C0_bits 200012 equal direct-delivery504's exactly. The reason is that both stocks (7682 and 7745 families) have the same bit length after multiplying by |O(73,2)|, and the C_0 field is dominated by 2^100000.
4. **Endpoint admissibility is a disjunction (D5).** The bad-residue surcharge only lowers C, and #2265 also certifies the native moment below one at C (1 − 8.39e-12). C is therefore admissible if *either* the retained envelope 32 m ΣH / 10^16 W is an adequate bad-residue bound for the PR2260 cover, *or* the PR559 native-complex license applies to it; the selected lineage uses that license (compare `research/audit-frontier890-endpoint-seed73/AUDIT.md` F3–F5). Neither disjunct is proved for the PR2260 cover; it is inherited. The comment "only conditionally portable to the new cover" in the engine PR2260 vendors (via base `research/frame-domain-ceiling/engines/moment.py:62`) is inherited verbatim from the long-vendored PR361 / e8-r740-lineage engine. Byte-identical copies (sha256 `81cbc864…`) include `research/direct-delivery504-global/inputs/data-base/work/pr361/code/engines/moment.py`. The comment predates PR2260, so it does not refer to PR2260's cover.

## Reproduce

From the repository root, after `git fetch origin pull/2260/head pull/2265/head`.
The verifier attempts this fetch itself if the pinned heads are absent, and falls back to
fetching the two pinned SHAs directly if a PR head has moved (GitHub serves PR-network
commits by SHA). Offline replay needs the pinned commits already present.

```sh
python3 -B research/pr2265-supplier-admission-audit/verify.py
```

Expected output, in about 3 seconds with stdlib only. Tested under Python 3.14 only; the
package runner's registered interpreter (3.12) was not available locally.

```
PASS_PR2265_SUPPLIER_ADMISSION_AUDIT controls_rejected 15 of 15
```

The full receipt is compared with [EXPECTED.json](EXPECTED.json). Use `--write` to regenerate it.

### Negative controls

Each control must be rejected by the named check:

- **Borrowed source.** Moved to a removed alias, or to register 2000 outside the call.
- **Events.** One ADD reads a removed alias.
- **Replay.** Forward: one logical monomial warp is dropped, or one helper ADD coefficient is doubled. Backward: one dual monomial symbol is inverted.
- **Owner rows.** One row overlaps the previous block, or one row is placed on its call's active data family.
- **Halving guard.** A mass-preserving child rank 52 (48 + 4 → 52) is introduced.
- **Invoice data.** The guard coefficient is changed to 245, or the row coefficient to 16466.
- **Endpoint.** It is raised by one 1e-200 grid step.
- **Kappa.** It is raised by 1e-240.
- **Bit endpoint.** It is set equal to b, or raised by 1e-18.

## Sources and pins

- Base commit: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Base-tree inputs are pinned in [SOURCES.json](SOURCES.json):
  - `research/e8-bit-p111-tuned/tune/EXPECTED.json` (sha256 `b9f0e5ca…`);
  - `research/direct-delivery504-global/evidence/audit/PREFIX-AND-INVOICE.json` (sha256 `ce1bfa49…`);
  - `scripts/verify_frontier1094.py` (sha256 `c7e20f59…`), read as text for the #1094 prefix and row constants.
- PR2260 head `fde6b107e26a14da5bac5b66913c914708ea6901` and PR2265 head `49ce38fee91f33edb54645724e7be9530f5631f6`. The 18 blobs read from these heads are SHA-256 pinned in `verify.py` (`PINS`). Examples: forward trace `a9d513bc…`, OWNERS `892b49f9…`, HOSTED-PARENT `f713f8e6…`, ENDPOINT `aefecb3b…`, LEDGER `df357ddc…`.
- No code from either PR is imported or executed. The vendored copy of PR2260 inside #2265 is byte-identical to PR2260's head, verified with `diff -r` during the audit.

## Scope, inherited assumptions, unresolved obligations

- The audited line is PR2260/#2265 (kappa ≈ 0.0016834). It is not the leading open conditional claim: newer open PRs (#2284 at 0.00168357; #2288, #2302 and #2309 at ≈ 0.001696, T74 lineage) are not covered.
- This is a finite data audit at one point: #2265's final point and PR2260's shipped word. It is not a proof of the capped-fusion theorem, of the all-size compiler, or of any multiplication theorem. #2284's "modern outer" point was not audited. Its `outer/ENDPOINT.json` at head `e71574b9` has a different schema (an 8-digit endpoint with no surcharge_weight) and a different profile (93-row owner delta, a rank-40 child), so the keys are not identical.
- The replay is limited to PR2260's event model:
  - It checks the literal events under PR2260's documented semantics: free reference-change symbols, GF(2) frames, destructive COPY/CLEAR. It was written after reading PR2260's description and its row interpreter, so it is an independent *implementation* of the same model, not an independent model.
  - The native Clifford lowering, phases, the lambda-fold lift and the physical charts are not rechecked.
- The 63-bit ideal local bound is taken from PR2260's precision receipts and is not recomputed. The 160 time windows (A4) are not re-derived.
- All INHERITED-traced items remain open obligations of PR2260 and PR1673: the all-size fixed-tape/route realization, the exact completed-child interface, the C_1 = 1 semantic guard, the equal-chunk interchange, and surcharge portability.
- The #2265 conclusion stays exactly as conditional as PR2260 and PR1673. This audit removes no hypothesis; it confirms that the finite supplier premises hold on the shipped data.

## Open next questions

1. **Payload unit convention (B1).**
   - *Question:* where does the retained lineage define whether the 512-bit payload and the 20161 row allowance scale with lambda? PR2260 asserts a per-lambda payload without a located source.
   - *Why it matters:* both self-consistent readings pass, but mixed readings give lambda ≤ 4 thresholds for PR2260 and for the selected #1094 alike (lambda ≤ 8 or ≤ 2 for PR2260's prefix against a fixed 512).
   - *First step:* locate the all-size compiler's definition of lambda and of the row coefficient (direct-delivery504 / PR523 invoice notes), then restate both rows in matching units.
   - *Blocker:* the definition of lambda is spread over historical notes.
2. **Endpoint admissibility for the PR2260 cover (D5).**
   - *Question:* does either disjunct hold for the PR2260 cover: the bad-residue envelope "32 m ΣH / 10^16 W" is adequate, or the PR559 native-complex license applies?
   - *Why it matters:* #2265 certifies C under both the native and the conservative moment, so one of the two is needed.
   - *First step:* list the cover-specific hypotheses of the PR559 exact-cover argument (`research/complex-multicold/vendor/pr559/PROOF.md`) and of the envelope derivation, and test them against PR2260's cover.
   - *Blocker:* the envelope derivation may only be in older PR discussions.
3. **Data-input borrow.**
   - *Question:* should the helper-specific prose in PR2226/PR2260 say that one alias (653, from PR2226's witness) borrows the public X_73 input?
   - *Why it matters:* PR2260's model (`PROOF-LOCAL.md:22`) already covers it and data borrowing is invisible at the call boundary, but helper-only wording elsewhere does not match the data.
   - *First step:* a one-line note next to the helper-borrowing sentences.
   - *Blocker:* none.

## Credit

The audited and predecessor work is by:

- PR #2265: DreamingOfClouds, the outer retune.
- PR #2260 and #2284: Dugongue, the selective-borrowing supplier and owners.
- PR #2226: Cinna Davis / 1337isnot1337, the borrowing architecture and the 80-alias witness containing the X_73 borrow.
- PR #1673: Vlado-V, the capped phase-cell fusion outer and its substitution review.
- PR #2220: jeremykothe2, the retune ledger.
- PR #2180 / #2161: dataisfire.
- PR #1758: jeremykothe2 (gauge-free interiors).
- PR #1786: chafreaky (Chafik Boukhalfa).
- The e8-bit-p111-tuned and direct-delivery504 packages.

Concurrent related audit: #2286, which covers the T74 side-condition inventory and states that supplier admission was not checked there. #2286 was opened from the same GitHub account (thakrarsagar) by a different, concurrent sprint session.

Reviewer fixes in this revision (internal sprint review): the guard-unit observation was rescoped as lineage-wide, A2/B2/B3 were reclassified as COVERED, D5 was restated as a disjunction, the X_73 borrow was credited to PR2226, a tautological control was replaced by two invoice-data mutations, and a backward-orientation replay control was added.

Correction after independent re-audit (2026-10-15): A1 had been labelled TRUE-unencoded as a whole, as if #2265 and the PR2260 checks it reruns left call closure unchecked. In fact PR2260's `local/check_trace.py` (run by `local/verify.py`) and `owners/verify.py`, both rerun by #2265, already enforce event closure and the owner-row facts. The label is now limited to the namespace/metadata sub-facts, and the owner-row facts moved to A3. `TASK.json` (stale control and class counts, pre-review open questions) was brought up to date, and the provenance of the engine comment in D5 was corrected. The counts (9/1/5, 0 MISSING-PROOF, 0 FALSE), the verifier and `EXPECTED.json` are unchanged.

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
