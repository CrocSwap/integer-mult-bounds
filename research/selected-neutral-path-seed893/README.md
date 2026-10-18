# One neutral step opens a strict selected-packing improvement

**Concrete two-step packing witness. Conditional fixed-word endpoint only; no supplier admission or new kappa.**

On the selected PR1094 owner ledger, no legal single whole-role relocation strictly lowers the idle moment. A neutral move can open a strict one:

1. Move width-7 helper `(stage=7, replica=2, helper=230)` from `(owner=1, child=14, port=57)` to `(13,15,14)`. Both bins have capacity rank 32. Their free remainders change `(0,7) -> (7,0)`, so the full idle histogram is unchanged. The call event is at 268, strictly inside the destination window `(255,430)`.
2. Move width-7 helper `(stage=1, replica=15, helper=226)` from `(11,8,103)` to the now-free `(1,14,57)`. This call event is at 181, strictly inside the destination window `(92,272)`. Before step 1 the destination had remainder 0 and this move did not fit. After step 1 it has remainder 7. The changed remainder pair is `(1,7) -> (8,0)`.

For every real `0<a<1`, `p=1-a` lies in `(0,1)` and `t^p` is strictly concave. The first step permutes `(0,7)`. The second replaces `(1,7)` by the more unequal equal-sum pair `(8,0)`, so `8^p+0^p < 1^p+7^p`. Thus the second step strictly lowers the idle moment uniformly over the full exponent interval.

The final idle profile is `{1:2275, 3:377, 7:6, 8:1, 48:4866}` versus the selected baseline `{1:2276, 3:377, 7:7, 48:4866}`. The neutral step preserves `{0:24730, 1:2276, 3:377, 7:7, 48:4866}` including the zero bins. The resulting 69,120-role map passes the inherited complete owner audit, including event windows, family uniqueness, exact occupied prefixes, rank mass `1,041,408`, deficit `5,120`, and halving guard.

## Exact pricing

The pinned outward-rounded child-moment calculator prices the unchanged local profile `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` on all 144 calls and the complete idle histogram, normalized by `144*(896/9)` families. Certified grid brackets are recorded in `CERTIFICATE.json`:

- Existing idle profile endpoint: approximately `0.001675462676808`.
- After the two moves: approximately `0.001675464332527`.
- Certified endpoint increase is at least `291277/175921860444160` (about `1.6558e-9`).
- The selected word's packing relaxation cap remains `a < 0.001690054109089`; the new endpoint is about 99.14% of that cap. The witness closes about 0.0114% of the remaining gap from the selected actual endpoint to the cap.
- The unchanged bit supplier endpoint is exactly `1733427039589844234749/1000000000000000000000000` (about `0.00173342704`), above the new complex endpoint. Thus complex remains the binding primitive in the retained supplier comparison; the certificate records the exact remaining margin.

This is a fixed-word packing improvement under the inherited coverage model. It does not reconstruct the source controller or full invoice and does not update either supplier endpoint, the selected record or `kappa`. The selected-record hash and `kappa=836330098538459/500000000000000000` remain unchanged.

## Reproduce

```sh
python3 -I -O -B research/selected-neutral-path-seed893/verify.py
# PASS_SELECTED_NEUTRAL_PATH_WITNESS path=neutral_then_strict two_role_map_audit=PASS new_kappa=NO
python3 -I -O -B research/selected-neutral-path-seed893/test_verify.py
python3 scripts/research_package.py --package research/selected-neutral-path-seed893 --check-only
```

The registered replay manifest uses Python 3.12. The exact interval model and owner data are pinned in `SOURCES.json`; the verifier regenerates the complete certificate and refuses input drift. See `TASK.json` for chooser seed, priority revision, live overlap, claim and precise scope.

## Predecessors and overlap

PR #1094 supplies the selected owner construction; PR #1091 supplies the retained owner audit; PR #1240 supplies the fixed-word packing ceiling. The one-relocation obstruction is in `research/frontier1094-single-relocation`. Open PR #1790 gives a complete no-improving census for **simultaneous** two-role swaps and leaves neutral-then-improving sequential paths as open questions. This package adds one explicit positive sequential path; it does not enumerate the open class or independently replay PR #1790.

## Open next questions

1. Does this owner map survive source-bound controller reconstruction and the full supplier invoice? Rebuild the selected supplier using the final ownership map and run the pinned controller, invoice and selected-record replay. The relevant full rebuild was not run in this bounded cycle.
2. How many legal neutral-then-strict paths exist in the fixed selected map? Enumerate canonical ordered relocation pairs while updating touched-bin capacities and retaining the event-window and family rules. PR #1790 already lists this wider domain; avoid duplicating its scope without coordination.

## Credit

Selected construction: Rohan Arun, PR #1094. Owner geometry and the inherited owner audit: Josie Elliston, PR #1091 / `research/t16-owner-audit-seed67`. One-role relocation model and uniform concavity comparison: `research/frontier1094-single-relocation`. Fixed-word packing relaxation: Douglas Colkitt, PR #1240 lineage. This contribution was prepared by OpenAI Codex with substantial AI assistance in deriving the witness, implementing the exact checker and writing the analysis. Apache-2.0.
