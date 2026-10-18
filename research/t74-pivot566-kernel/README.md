# Pivot-566 helper-donor kernel on PR1319's T74 exact fill

**Conditional κ = 0.001676896669021299** on PR1319's unchanged strict T74 chain, **+4.144e-8** over PR1319
(0.001676855229071321). Stacked with PR1549's 200-digit refinement of the same assembly, the refined value is
**κ = 0.001676896669021299307750710997267962671611490016339159610658…724841**, above PR1549's 0.0016768552290713218862064567722745926195124487395104752628…03439 by the same 4.144e-8.
This is a conditional finite construction, like its predecessors: all inherited all-size compiler, common-label/mutable-source
realization, whole-call hosting, precision/tape, exact recovery, analytic transfer, PR559 recurrence correction and
PR589 bit H1–H5 assumptions remain. Nothing here is a formal verification of the multiplication theorem.

## What changes

Only the two local words. PR1319's owner map, dispatch (249 gauge44 / 417 extra calls), parent template,
construction recipe, idle remainder (H48 = 22,748), interfaces (ports, centres, start_extra, helper_final) and every
predecessor file are unchanged. In both PR1297 words (gauge44 and extra, which have identical gates), the kernel for cold
pivot q = 566 is:

| Edit (original B indices) | Gate |
|---|---|
| delete B755 | `494 -= q` (an early read of q, which is later written at B866 and restored in the early cleanup at position 85) |
| helper window on 98 | `98 -= q` before B520; `98 += q` at early-cleanup position 86, right after q's restoration |
| donor window on 590 | `590 -= q` before B0; `590 += q` before B47 |
| donor window on 672 | `672 -= 2q` before B0; `672 += 2q` before B224 |
| direct reads | `150 += q` and `209 -= q` before B0 |

Every new read of q sees its initial value, so the program changes only in q's column. The complete B + early-cleanup
map is unchanged on all 522 touched registers (exact Fractions), and the remaining cleanup is identical. With exactly
optimal frames (PR1186 frame model: tail-mutable chains, cone caps, cut equality, integer duality gap 0), the per-call
paid profile moves by **H1 +1, H2 −2, H3 +1** on both words, which is rank-mass-neutral and saves 1,855 cost units at
PR1319's endpoint.
The new local profiles are gauge44 `{1:2347, 2:502, 3:415, 4:130, 5:82, 8:8}` and extra `{1:2339, 2:510, 3:419, 4:126, 5:82, 8:8}`.
The global T74 profile becomes `{1:1559766, 2:337668, 3:278058, 4:84912, 5:54612, 8:5328, 48:22748}`.

## Evidence

- **Exact rebuild** (`rebuild.py`, standard library). PR1297's pinned words plus `inputs/EDITS.json` reproduce the shipped
  words' scalar programs. The full B + early-cleanup map, the remaining cleanup and all interfaces are identical.
- **Restoration argument** ([RESTORATION.md](RESTORATION.md), checked by `kernel_check.py`, receipt
  `evidence/KERNEL-CHECK.json`). Every inserted or deleted read of q sees q's initial value, so only q's column can
  change. The nine terms' propagated differences cancel exactly, register by register. At the end of B they touch no
  port, so the derived compensation (7,208 gates) is unchanged, and the whole program map is unchanged. Two frame
  chains change (registers 150 and 494), giving H1 +1, H2 −2, H3 +1. Four mutated kernels are rejected.
- **Local admission.** The unchanged `research/gauge44-frames-x/independent/audit_local.py` passes on both shipped
  words, and its recounted paid profiles equal the PLAN. The lineage native chain
  (`research/k8-eight-ends/replay_native.py` from PR1297's layout: native, ledgers, local replay, wrappers, phases)
  passes on both words. Its pinned artifacts equal those of the PR1186 toolkit's chain, except receipt timing fields.
- **Strict T74 admission** (`evidence/STRICT-T74.json`). PR1319's own `replay.py` passes with PR1319's plan rebound only
  in its provider fields (`rebind.py`):
  - bind, emit, audit with 15 mutations, invoice, assembly and the independent owner audit;
  - 114 admission, 12 bit-supplier, 8 independent-owner, 6 geometry and 4 outer-grid mutations rejected;
  - all 47 outer constraints strictly positive;
  - 319,680 roles; prefix 1,441 bits, charged at 2,048; row coefficient 19,545 < 20,161;
  - result `PASS_STRICT_MIXED_T74_EXACT_FILL`, κ = 0.001676896669021299, complex lower endpoint
    0.001679713374784385769573, conservative κ 0.001676896666184798.
- **Stacked refinement** (`evidence/REFINED-R200.json`). The same strict replay with PR1549's unchanged refined assembler
  (vendored with its fine engines and PR1519's parity repair), PR1549's settings (endpoints 1e-200, grid 200 digits,
  margins 1e-250, 90 bootstrap steps) and this construction's own 200-digit certified endpoints passes:
  `PASS_STRICT_MIXED_T74_EXACT_FILL`, κ = 0.0016768966690212993077507109972679626716… PR1549's fine-engine oracle check also passes.
  The endpoints were certified by bisection with the same engines, accepting at the endpoint and rejecting one grid
  step above (`evidence/ENDPOINTS-R200.json`).
- **Pricing** (`evidence/PRICING.json`). Optimal frames for the PR1186 toolkit's integer cost weights on both words,
  Δ = −1,855 each (c_1 − 2c_2 + c_3 at PR1319's endpoint), both `ok` (certified).
- **Ancestor and kernel replayed side by side** (`evidence/FULL-REPLAY.json`, `evidence/INTERFACES.json`). One fresh
  `replay_full.py` run, with no native reuse, covers PR1319's own admission of the unchanged ancestor and then the
  kernel; see Revision 2 below.

## Reproduce

Bounded check, standard library plus the pinned repository files (also the registered hook):

```sh
python3 -B research/t74-pivot566-kernel/verify.py
python3.12 scripts/research_package.py --package research/t74-pivot566-kernel
```

Expected: `PASS_T74_PIVOT566_KERNEL_BOUNDED 1676896669021299/1000000000000000000`. It checks:
- every input pin, and every PR1319 file against PR1319's MANIFEST;
- the exact rebuild and the unchanged `audit_local.py` on both words;
- the global profile bookkeeping;
- κ and the conservative κ recomputed from the profile with the retained moment engines and the 47-constraint outer
  witness;
- the binding of the recorded strict, refined and native receipts;
- the restoration argument (`kernel_check.py`, which must reproduce `evidence/KERNEL-CHECK.json` exactly, with its four
  mutated-kernel controls);
- five failure controls (flipped coefficient, dropped restore, read in the pivot's busy window, corrupted word byte,
  mass-neutral forged profile).

Complete chain, about 13 minutes fresh, with Python 3.14 and SymPy as for PR1319:

```sh
python3 -B research/t74-pivot566-kernel/replay_full.py --work /abs/new/dir --refined \
    [--orig-base-native-from D --orig-extra-native-from D]   # optional reuse for PR1297's ORIGINAL words
```

It runs, in order:
- PR1297's own admission (which builds the layout and runs fresh native chains of PR1297's original words);
- PR1319's admission of the unchanged ancestor (regenerated owners, template and PLAN bound by payload, container and
  payload controls, strict T74 replay and geometry controls on PR1319's own data);
- fresh lineage native chains of both kernel words and the rebind (which must reproduce `data/PLAN.json`);
- PR1319's strict replay and geometry controls on the kernel;
- `kernel_check.py` and `interfaces.py`;
- with `--refined`, PR1549's assembler and oracle.

Expected: `PASS_T74_PIVOT566_KERNEL_COMPLETE_FINITE_ADMISSION 0.001676896669021299`. The scripts refuse `-O`, because
their assert statements are the checks.

## Revision 2 (2026-10-14): separate replay and restoration argument

The maintainer's continuation point asked for three things:
- resolve the inherited PR1319 admission (controller, geometry, invoice and semantic regenerated-artifact checks);
- review the kernel's restoration argument;
- replay the kernel's complete native and whole-call interfaces separately from the unchanged ancestor.

This revision answers them as follows.

- **Restoration.** [RESTORATION.md](RESTORATION.md) gives the argument over the whole audited program: the lemma, the
  nine-term ledger, the compensation, the frames and four controls. `kernel_check.py` checks every step exactly and is
  part of the bounded hook.
- **Inherited admission.** PR1319's recorded blocker is container bytes. Its `verify.py` binds the regenerated
  `OWNERS.json.gz` by the hash of its gzip bytes (PLAN `assignment_sha256` and `replica_lift.owners_file_sha256`), and
  gzip output depends on the zlib build. `replay_full.py` runs PR1319's unchanged `reconstruct.py` and
  `lift_parent.py` and checks every regenerated payload against PR1319's pinned files. The pinned owners container then
  stands in for the regenerated one.
  - Container control: the owners are recompressed with other gzip bytes. Exactly those two PLAN fields change, and
    the payload hash (`assignment_content_sha256`) does not.
  - Payload control: one re-timed role is rejected.
  - PR1319's strict T74 replay (controller audit with mutations, invoice, assembly, admission and bit controls) and its
    geometry controls then pass on PR1319's own data with fresh natives: κ = 0.001676855229071321, its claim.
  - PR1319's package is not modified.
- **Separate native and whole-call replay.** In the same fresh work directory the kernel words get their own fresh
  native chains, rebind and strict T74 replay (κ = 0.001676896669021299). `interfaces.py` compares the two runs:
  - **Call interfaces.** Every interface the hosting reads from a local word is identical on both words: ports,
    centres, register count, and each helper's entrance frame, end frame and width (`call_interfaces_identical`).
  - **Native artifacts.** `RESIDUAL-ADAPTERS.json` and `WRAPPER-CHECKS.json` are byte-identical on both words. The
    canonical and full words, local programs (+7 events per orientation), local checks, frame audit, independent local
    replay, Clifford recipes and review differ, as the changed gates and frames require.
  - **PLAN.** It differs from PR1319's only in each call's `local_program_sha256`, the providers' program and artifact
    hashes and paid profiles, and the global profile.
  - **Strict T74 receipts.** Both replays agree on every hosting quantity: calls, roles, provider counts, live, deficit,
    rank mass, idle remainder, width inventories, prefix bits (1,441, charged at 2,048), physical row coefficient
    (19,545 < 20,161) and control counts. The actual 73-axis charts and the idle-remainder frames are byte-identical.
    The runs differ in the profiles, the program-dependent hashes and invoice counts, and κ.

The scripts used to rely on `assert __debug__`, which `-O` strips along with every other check. `verify.py`,
`replay_full.py`, `kernel_check.py` and `interfaces.py` now refuse `-O` explicitly.

## Overlap and novelty

Open PRs, discussions (`scripts/find_overlap.py 'pivot 566' 'helper-donor' 'cold kernel'`, plus a direct search of all
open PR bodies and the last 100 discussions) show no other pivot-566 kernel or post-PR1297 kernel. Every κ claim built on
PR1319 (PR1377, PR1424, PR1444, PR1458, PR1464, PR1479, PR1485, PR1510, PR1513, PR1534, PR1536, PR1549) keeps the
construction unchanged and refines digits only. Their owners, plan, template, dispatch, profile and words are
byte-identical to PR1319's, so this kernel stacks on all of them. PR1338's census and PR1337's census used the
restricted two-shock family (helper cut + donor pair); this seven-insert kernel lies outside it.

## Open next questions

The structured list is in [TASK.json](TASK.json):
1. Do other written cold pivots admit kernels of the same seven-insert shape? 81 of 278 remaining pivots were searched;
   the first step is the slot-screened search on the remaining 197.
2. Can the never-written copy-window pivots (439/444/438/440 and the −51,648 group) gain with edits that also re-time
   port-chain gates (a two-column identity)? Every insert-only, window, partial-deletion and tail-undo family is
   neutral or infeasible on these words.
3. Can the frames be re-derived independently? The shipped words carry solver-derived frames; audit_local and the native
   chain validate them, but the frame optimum itself is reproduced only with the unmerged PR1186 toolkit.

## Credit

See [NOTICE.md](NOTICE.md).
- Rohan Arun: PR1319 T74 exact fill; PR1297/PR1286 kernels and words.
- Jeremy Kothe: PR1274, the first helper-donor kernel; PR1377 → PR1536 refinements.
- Jeremy Diviney: PR1193.
- Thomas DiFiore (tomdif): PR1148; chafreaky: PR1196; Marius-Paul Dumitrean: PR1195 source-holder fusions.
- midhatn: PR1549 refined assembler.
- philippeVV: PR1519 repair.
- Hanson Sun (bbMisk): PR1431.
- The retained lineage named in those packages.

Prepared by Marius-Paul Dumitrean with substantial AI assistance (Anthropic Claude, via Claude Code). Apache-2.0.
