# R438 bit supplier: one improving transport, optimal window-respecting re-hosting, and two PR1345 atlas fixes

**Finite conditional bit-supplier construction and a tool fix. No new κ.** The selected record is
complex-bound: complex is 0.001675462676808103522925, κ is 0.001672660197076918, and bit (PR589) is
0.001733427039589844234749. Every bit value here is larger, so κ is unchanged.

Everything is **conditional on [PR1043](https://github.com/CrocSwap/integer-mult-bounds/pull/1043)**
(Ali Romman, the R438 source-boundary word with helper 470 deleted). PR1043 is open and not admitted. Its
review requests the C++17/Boost native lane.

| bit endpoint c (exact grid, accepted at c, rejected at c + 1e-24) | value | vs PR1043 |
|---|---|---|
| PR589 (selected bit supplier, control) | 0.001733427039589844234749 | |
| PR1043 R438, its own in-place hosting (control) | 0.001734176288479865766692 | |
| R438 + one transport, PR1043 hosting | 0.001734220472884893243548 | +0.0025% |
| R438, **optimal window-respecting re-hosting** | 0.001734802047828389852783 | +0.0361% |
| **R438 + transport + optimal re-hosting** | **0.001734846264120199151475** | **+0.0386%** (+0.0819% vs PR589) |

## What is new

1. **One improving transport** (`verify_transport.py`). A elementary op 2027, `444 += 77` (receiver
   444 reads source 77), moves from frame 186 to slot 154 at frame 79. That is next to the existing
   frame-79 reads of source 77 by 390 and 391. Slots 155 and 425 are equivalent.
   - Effect: the paid profile changes by +e1 − 2e2 + e3 at equal rank mass 5,121. It goes from
     {1:1321, 2:1344, 3:78, …} to {1:1322, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:18}, with ADDs
     unchanged at 24,248.
   - Format: the gate format is kept; A stays at 2,074 gates with the same 18 multi-source gates.
   - The word is rebuilt from PR1043's stdlib builder. Its content sha matches PR1043's CERTIFICATE and
     FRAME-PATHS. The transported word is stored in `words/`, gzip sha256 pinned.
   - Checks: it passes PR1043's own replay (arbitrary dirty endpoint, precision bounds unchanged) and
     `research/e8-bit-p111-tuned/code/xcheck_p.py` (H1–H5, K = D, C = U⁻¹, F2 replay on all 660
     columns).
   - Local optimality after the move: PR886 `frameopt` finds 0 improving components (its degraded
     control finds 37). The patched PR1345 atlas finds 0 improving singles and 0 improving pairs
     (224,369 + 218,448 pairs scored).
2. **Optimal re-hosting of R438's slack** (`verify_rehost.py`). Deleting helper 470 leaves 54
   width-8 slack units per replica instead of 45. PR1043 folds them back into their own hosts
   (remainders {10:5, 12:3, 14:1}) and runs no hosting search.
   - **Optimum.** Under the PR1023 slot model, an exact top-3 interval DP proves the unique optimum:
     10 fully idle rank-42 slots plus one rank-42 slot holding one helper. The idle profile per
     replica is {2:433, 4:444, 6:444, 7:666, 34:1, 42:10}. Mass (1,808,352) and children (904,320)
     are unchanged.
   - **Cross-check.** A branch-and-bound enumeration over all 10,556,685 layouts agrees. The
     runner-up `10×(42,5)+(14,1)+(28,3)` is worse by Σg 0.0079020 per replica. S = 45 reproduces
     PR589's layout and PR1023's own `width8_optimality`.
   - **Windows.** All 22 splits of the slack over children 4 and 6 are stage-window feasible. This
     uses seed72's `maxflow_assign` and a separate Hall test, and tightened windows are rejected.
   - **Placement.** An explicit placement of 3,942 helper occurrences per replica (126,144 owner
     roles) passes seed14's `placement_audit` and a separate audit. Both audits reject 9 mutations.
     There are 29 controls in all.
3. **Two crash bugs in PR1345's transport atlas** (`atlas_bugs.py`, `atlas.patch`, 3 lines). PR1345
   head is b54a856a.
   - `dict()` raises "got multiple values for keyword argument 'improving'" at line 282 whenever an
     improving move exists.
   - After that fix, a `Fraction < tuple` comparison fails at line 416; `best[0]` should be
     `best[0][0]`. Line 375 has the same pattern, shown only on sample values.
   - The atlas's improving branch was therefore never exercised. On PR589's word nothing improves, and
     the patched atlas reproduces PR1345's `result.json` exactly, so PR1345's conclusion stands.
   - On R438 the unpatched atlas crashes. The patched one finds the transport above.

Two adversarial AI verifier passes re-derived these results independently: the word rebuild, an
independent replay, a Decimal root for both endpoints, the layout counts and the DP optimum, plus
their own mutations. Their hygiene findings are fixed here. Details are in `NOTES-transport.md` and
`NOTES-rehost.md`.

## Reproduce

From the repository root, CPython ≥ 3.10, standard library only, no network. PR1043 and PR1345 inputs
are vendored byte copies with sha256 and blob pins under `vendor/`.

```sh
python3 -I -B research/bit-r438-transport-rehost/verify_transport.py        # ~40 s; --full adds the atlas runs (~3 min)
python3 -I -B research/bit-r438-transport-rehost/verify_rehost.py --check research/bit-r438-transport-rehost/verify_rehost.receipt.json   # ~5 s
python3 -I -B research/bit-r438-transport-rehost/atlas_bugs.py              # ~2.5 min; --full also runs the pristine atlas on PR589
```

Expected final lines start with:
- `PASS_R438_T154_TRANSPORT`
- `PASS_R438_WINDOW_REHOST S=54 opt=10x(42,5)+1x(42,4) …`
- `PASS_PR1345_ATLAS_BUGS`

All three were run on CPython 3.14.4 (Linux x86_64). The registered Python 3.12 replay was not run
locally.

## Scope and limits

These are finite, local and slot-model certificates; none is a supplier admission, and none changes κ.
- **Not run:** PR1043's native pipeline (NumPy, SymPy, SciPy, C++/Boost), so there is no emitted hosted
  template, no full `audit_hosted_k`, no `assemble9` precision charges and no outer assembly.
- **Hosted profiles are assembled, not emitted.** They are built as `288·local + 32·remainders`.
  PR1043's `check_hosted_change` therefore passes as a consistency check only.
- **Not checked:** projector compatibility of mixed occupancy (#1307), cross-replica owner maps, banks
  and recipe changes.
- **Search limits:** the pair census uses products of single-move option lists computed on the unchanged word. Its reported zero-improvement result is restricted to those fixed lists; jointly enabled new frame or commutation choices are not covered. Transport triples and cross-section or boundary-adaptive moves are not searched.
- **Conditionality:** every row is conditional on PR1043's word and its admission.

## Open next questions

- **Native lane.** Do PR1043's native 5/9/11-stage checks and hosted emission accept the transported
  word and the re-hosted layout? First step: run PR1043's `verify.py --output` lane on the
  `words/r438-t154.json.gz` word with the new selection. This needs C++17/Boost.
- **Deletions.** Is each further helper deletion worth about +0.08% under optimal re-hosting? A float
  screen suggests about +0.079% per deletion, which is more than a window-respecting width-7
  conversion. First step: extend `verify_rehost.py`'s DP to S = 45 + 9d with Hall checks per d. Only
  PR1043's helper 470 is known to be removable on the fixed word.
- **Larger moves.** Are there improving transport triples or cross-section transports on R438? First
  step: run the patched atlas with triples restricted to the components that touch 444 and 77.

## Credits and licence

- PR1043 (Ali Romman): the R438 word, its builder, replay and hosting code (vendored).
- PR1345 (hipotures): the transport atlas (vendored with the fix as a patch).
- PR589 and PR555 lineage: the tuned bit word.
- PR1023 (bit589 width packing): slot model and `g_interval`.
- `bit589-width7-windows-seed72` and `bit-helper470-window-placement-seed14`: windows, allocation and
  placement audit.
- PR886: frameopt.
- `e8-bit-p111-tuned`: `xcheck_p.py`.

Original notices are retained in `vendor/`. Prepared by Sagar Thakrar with substantial AI assistance
(Claude Code, Anthropic, Claude Opus 5.5). An AI scouting pass, two AI builders and two adversarial AI
verifiers were used; no independent human review is claimed. Apache-2.0.
