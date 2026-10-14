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
- **Pricing** (`evidence/PRICING.json`). Exact optimal frames on both words, Δ = −1,855 each, both `ok` (certified).

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
- five failure controls (flipped coefficient, dropped restore, read in the pivot's busy window, corrupted word byte,
  mass-neutral forged profile).

Complete chain, about 15–20 minutes, with Python 3.14 and SymPy as for PR1319:

```sh
python3 -B research/t74-pivot566-kernel/replay_full.py --work /abs/new/dir --refined \
    [--orig-base-native-from D --orig-extra-native-from D]   # optional reuse for PR1297's ORIGINAL words
```

It runs PR1297's own admission (which builds the layout), fresh lineage native chains of both new words, the rebind
(which must reproduce `data/PLAN.json`), PR1319's strict replay and geometry controls, and, with `--refined`, PR1549's
assembler and oracle. Expected: `PASS_T74_PIVOT566_KERNEL_COMPLETE_FINITE_ADMISSION 0.001676896669021299`.

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
