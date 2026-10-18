# Bind the retained PR589 supplier identity

**Supplemental source-binding guard and finite audit; no new kappa.**

[PR1277](https://github.com/CrocSwap/integer-mult-bounds/pull/1277) identifies a
remaining question: the PR799 assembly can name a false `bit_supplier` commit
and Git blob while retaining its accepted numerical result. Its primary finding
and suggested ancestry-equality repair belong to Sagar Thakrar. This package
answers the separate supplier-identity question with an opt-in executable guard.
It changes no existing file or production acceptance predicate.

All four committed PR741/PR799/PR1042/PR1094 assemblies and the archived PR589
bit result pass. The guard independently connects the cited source to its
actual word and deficit, rather than treating a successful endpoint comparison
as proof of provenance. Normal verification is read-only.

## Exact boundary and evidence

The trusted historical selection is main
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`; its reviewed PR589 head is
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.
[SOURCES.json](SOURCES.json) pins every external input and the governing source
code. The guard imports no supplier, frame checker or moment engine.

1. **Git provenance.** The original source uses `research/e8-bit-p111/`.
   Main retains it as `research/e8-bit-p111-tuned/`. The EXPECTED record and
   compressed word are byte-identical at the exact PR589 head, the integration
   commit `b3eb785ac5b4b1ca2beea0f80db078a505626a90`, and the pinned live inputs.
   Git confirms that PR589 is a direct parent of that integration commit and
   that the integration precedes this package's base. The original-to-retained
   rename is checked explicitly; the assembly's retained path is not assumed to
   have existed on the original contributor branch.
2. **Word-to-deficit binding.** Following the source format's D/A frame
   assignments up to COPY and performing separately implemented rational row
   elimination gives nine ranks `[7,7,7,7,7,7,7,7,7]`, hence decoder constant 63.
   With the retained nine-stage, 32-replica layout, `K=4`, `M=64`, `v=111`,
   `W=28416`, the full recorded profile has rank mass 1808352. Both sides give
   `MW - mass = T(2Kv - L*cst) = 10272`.
3. **Consumer guard.** Every assembly must name that exact source commit,
   integration commit, repository, PR, retained path and EXPECTED blob, and the
   independently derived word/deficit. Its bit input digest, endpoint, decimal
   and bad-residue surcharge must agree with that source. A supplied bit result
   must preserve the entire priced profile, inventory and recorded bit budget.

The EXPECTED Git blob is `e293ddc557742637f9f679f083a1a282d87b1b13`; the
compressed word blob is `85a4499bf9e4911a705d50567a2c2ef6cf23739a`.
The decompressed word SHA256 is
`5642fd0e35a1acc11acff8d0c08350c1617e95f310d4d35ad63a651f9eeeba0b`.
These are source pins, not hashes of newly regenerated gzip containers.

[RESULT.json](RESULT.json) is deterministic. Ten test groups include 23
rejection fixtures: six false provenance fields with unchanged endpoint and
kappa; a different real commit containing the identical EXPECTED blob; a
compensating `[6,8]` COPY-rank substitution preserving total rank 63; an actual
COPY-frame change; profile mass/type faults; endpoint/digest/surcharge/deficit
faults; bit-result faults including a rank-mass-preserving histogram change;
the CLI zeroed-source fixture; and corrupted relocated source bytes.

The positive tests cover the four actual assemblies, the actual bit result,
and physically relocated inputs using the same Git object database. Checks run
under `-I -O -B`; this guard does not rely on Python assertions.

## Reproduce and use

Python 3.12 or later, Git, full repository history and no Python dependencies:

```sh
python3 scripts/research_package.py --package research/retained-bit-supplier-binding --check-only
python3.12 scripts/research_package.py --package research/retained-bit-supplier-binding
```

Expected: `PASS_RETAINED_PR589_SUPPLIER_BINDING assemblies=4 deficit=10272`,
ten passing tests, and `PASS_REGISTERED_RESEARCH_PACKAGE`.

After a replay that retains **this exact PR589 supplier**, additionally guard
its actual outputs:

```sh
python3 -I -O -B research/retained-bit-supplier-binding/verify.py \
  --assembly /absolute/replay/global/ASSEMBLY.json \
  --bit-result /absolute/replay/ancestor/bit/RESULT9.json
```

Paths are explicit; the guard never follows a receipt's machine-local ancestor
path. A different word or source version requires a new contract and pins.
`--write /absolute/receipt.json` explicitly writes a freshly checked receipt;
otherwise the default fixture run also compares against committed RESULT.json.

## What this establishes, and what remains

This adds the executable supplier-identity check requested in PR1277; it does
not replace PR1277's broader equality-to-the-recorded-ancestry repair. The
earlier finding that a zeroed supplier passes `check_selected` is credited to
PR1277 and was not freshly replayed here. This package freshly tests rejection
by the new guard, including its real CLI. It does not claim that the unchanged
production pipeline now rejects the fixture.

The frame trace is used only to measure COPY ranks, not to establish frame
legality, scalar restoration or H1-H5. The recorded global profile and bit
budget remain inputs. No native/scalar/phase/emitted-controller replay,
orthogonal-chart proof, cold supplier rebuild, certified moment endpoint,
complex-side verification, all-size/compiler, hosting, precision/tape,
exact-recovery or analytic-transfer proof is performed. No full multiplication
theorem, runtime improvement, selected-frontier change or execution
authentication is claimed.

## Task and overlap

Card `supplier-boundary-audit`, refined to the PR589 identity boundary; chooser
nonce `78116c731f9a59be32e8cd1544265921`, adversarial-audit track, priority
revision 2. [TASK.json](TASK.json) records the scope, method, domain and stop rule.
The card's historical owner audit and current `research_baseline.py` both pass
as orientation controls; they are not new results.

An entry snapshot covered 806 open PRs including drafts, with complete PR
pagination. The repository overlap helper searched their titles/bodies and
local top-level package notes/ledger. Discussions' start-here, listing and live
handoff thread were read, but complete Discussion pagination was unavailable.
The browser was signed out and the GitHub connector exposes no Discussion-write
tool, so the claim is local. No absence-of-overlap or novelty proof is asserted.
Final refresh details are recorded in TASK.json and the PR.

Nearest work: PR1277 at `02d279515ff1fc468ab99a19d89461f1b6391507` owns the
finding and supplies the explicit next question. PR1307 audits the selected
bit allocation's physical projectors; PR1312 audits complex-owner X2 coverage.
Neither is an input here. This package adds source-to-Git and word-to-deficit
enforcement, not another owner-window or projector census.

## Open next questions

Should a future unpinned replay wrapper require both this guard and PR1277's
ancestry equality? This would protect the cited supplier identity as well as
the particular retained ancestry receipt. The smallest useful step is to apply
both in a successor wrapper, check PR1277's false-supplier/timing variants and
then run a complete cold replay. Maintainer acceptance and versioned source and
coverage pins block adoption; changing frozen supplements is outside this
contribution. The structured question is in TASK.json.

## Credit

Sagar Thakrar / PR1277 for the finding and next question; DreamingOfClouds /
PR589 and eumemic / PR555 for the word and retained checker/hosting lineage;
PR545's rank-mass identity; Douglas Colkitt for the integration and composition
bindings; Rohan Arun, Jeremy Kothe, Hao Yan and the selected complex lineage;
nightangelflowerwin-ops / PR865 and Lucas Steinmetz / PR838 for the replay
coverage lineage. Existing source notices and licenses are retained.

Prepared by Arham Tahir with substantial OpenAI Codex assistance in research,
implementation, verification and writing. No subagents or independent human
peer review. New material is Apache-2.0.
