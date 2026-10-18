# Screening the queue-ceiling census's uncovered sixteen

**Review aid built on [CrocSwap/integer-mult-bounds#1240](../complex-local-word-ceiling/README.md) and
[CrocSwap/integer-mult-bounds#1264](../complex-queue-ceiling-census/README.md). No new kappa; no claim is accepted or
rejected.** Prepared by Aaron Wang / navinor, with help from opencode. Apache-2.0.

The queue-ceiling census screened 14 of the 30 open complex kappa claims and listed 16 as not
covered: "no profile whose kappa equals the title kappa, with live/calls and an idle histogram in
the same package". This package screens all 16 at their snapshot-pinned heads. The reason the
census could not see their data is naming, not absence: the same four inputs are recorded under
`global_profile`/`profile`, `idle_profile`, `complete_invocations`, inside an `expected` block,
or (for CrocSwap/integer-mult-bounds#1175) README prose. With those aliases and the census's own `live*9 == 896*calls` rule,
every one of the 16 has all four inputs, and each recorded profile satisfies the coverage law
`mass = 72*live + 64*calls` exactly.

## Result

**30 of 30 census-listed claims are now screened. No newly screened word raises a cap.**
The 16 claims sit on 11 distinct per-call local words (7 new against the census's nine). The
highest cap among them is **0.0016872744** (word N1, identical to census W4), **+0.004%** over the
selected word's cap 0.0016872026 and *below* the census's best cap 0.0016873148 (W1). So the whole
covered queue remains a packing contest inside the +0.87% band above the selected kappa
0.001672660197076918; extending coverage to the 16 did not surface a word that raises the limit.

| Word | Local profile per call | κ cap | vs selected word | Claims |
|---|---|---:|---:|---|
| N1 = census W4 | `1:2406 2:432 3:424 4:142 5:82 8:8` | **0.0016872744** | +0.004% | CrocSwap/integer-mult-bounds#1104, CrocSwap/integer-mult-bounds#1107, CrocSwap/integer-mult-bounds#1117, CrocSwap/integer-mult-bounds#1121, CrocSwap/integer-mult-bounds#1150, CrocSwap/integer-mult-bounds#1172 |
| N5 = census W2 = selected | `1:2412 2:418 3:432 4:142 5:82 8:8` | 0.0016872026 | 0 | CrocSwap/integer-mult-bounds#1175 |
| N2 (new) | `1:43307/18 2:7633/18 3:15661/36 4:5003/36 5:82 8:8` | 0.0016863769 | −0.049% | CrocSwap/integer-mult-bounds#1111 |
| N3 (new) | `1:42949/18 2:8135/18 3:15623/36 4:4753/36 5:82 8:8` | 0.0016845577 | −0.157% | CrocSwap/integer-mult-bounds#1154 |
| N4 = census W3 | `1:2364 2:498 3:412 4:130 5:82 8:8` | 0.0016842207 | −0.177% | CrocSwap/integer-mult-bounds#1169 |
| N7 (new) | `1:262220/111 2:55462/111 3:45824/111 4:14338/111 5:82 8:8` | 0.0016839954 | −0.190% | CrocSwap/integer-mult-bounds#1183 |
| N10 (new) | `1:261194/111 2:56488/111 3:45782/111 4:14158/111 5:82 8:8` | 0.0016836930 | −0.208% | CrocSwap/integer-mult-bounds#1207 |
| N11 = census W7 | `1:783550/333 2:169496/333 3:137362/333 4:42458/333 5:82 8:8` | 0.0016836800 | −0.209% | CrocSwap/integer-mult-bounds#1218 |
| N9 (new) | `1:261194/111 2:56488/111 3:45560/111 4:14602/111 5:80 8:8` | 0.0016836527 | −0.210% | CrocSwap/integer-mult-bounds#1201 |
| N8 (new) | `1:261860/111 2:55822/111 3:46004/111 4:14158/111 5:82 8:8` | 0.0016835547 | −0.216% | CrocSwap/integer-mult-bounds#1192 |
| N6 (new) | `1:42607/18 2:8981/18 3:14921/36 4:4591/36 5:82 8:8` | 0.0016831053 | −0.243% | CrocSwap/integer-mult-bounds#1176 |

Every claim's recorded endpoint lies below its own word's relaxation (the exact `ceiling()`
bracket), and every recorded kappa lies below its cap, as for the census's 14. Fractional counts
are exact reduced rationals: the per-call split divides by the call count (144 or 333).

Two per-claim notes:

- **CrocSwap/integer-mult-bounds#1175 is the selected word with a new idle packing.** Its recorded global profile splits into
  the selected local word exactly (`1:2412 2:418 3:432 4:142 5:82 8:8`, 72 calls on 7,168 live),
  with idle remainder `{1:1214, 2:1, 32:1, 48:2443}`. Its recorded kappa 0.001674083482880778
  sits 0.78% below the W2 cap (the selected record's own endpoint sits 0.87% below it). This is
  the "pack a selected-type word tightly" route from the CrocSwap/integer-mult-bounds#1166 handoff, already pursued there.
- **CrocSwap/integer-mult-bounds#1175's PR title kappa 0.001675338871723469 differs from every kappa its package records**
  (the package's headline is 0.001674083482880778). The screen uses the recorded value and flags
  the mismatch; which profile the title value belongs to is the authors' to say.

## Method

Per claim, the four census inputs are read from the claim's own package at its pinned head and
blob: the global paid profile, the idle-remainder histogram, live stock W and call count N
(`complete_invocations` or the `live*9 == 896*calls` rule). Accepted aliases are recorded per row
in [SNAPSHOT.json](SNAPSHOT.json); `rebind.py` re-reads the pinned blobs and checks the recorded
values. [verify.py](verify.py) then repeats the census's checks with `../complex-local-word-ceiling/ceiling.py`:
the coverage law, the idle split (idle ≤ profile, idle ranks ≤ 51), 896/9 live families per call,
the per-word exact packing ceiling, the claim's endpoint below its word's relaxation, and the
recorded kappa below its cap. Five rejection controls mutate the snapshot (coverage law, idle
split, families per call, endpoint above relaxation, title mismatch) and must fail.

## Reproduce

Standard library only, from the repository root (about 9 s):

```sh
python3 -I -B research/complex-queue-ceiling-uncovered/verify.py
python3 -I -B research/complex-queue-ceiling-uncovered/rebind.py --fetch   # network; re-reads pinned PR blobs
```

Expected final lines: `PASS_COMPLEX_QUEUE_CEILING_UNCOVERED claims=16 words=11 new=7 max_cap=0.0016872743702513531 controls=5`
and `PASS_SNAPSHOT_REBOUND_UNCOVERED 16`.

## Scope and limits

- Caps are planning bounds (`κ < a/(1+a)`) for hosting, owner and idle repacking of each claim's
  own recorded word under the coverage law, 896/9 live families per call and the halving guard.
  They ignore helper widths, windows and chronology, and do not bound changed words, templates or
  outer recipes.
- The screen reads what each package records. It does not re-derive any profile from a circuit,
  re-run any claim's replay, or validate helper placement; a recorded profile could in principle
  disagree with its own construction. Two heads (CrocSwap/integer-mult-bounds#1172, CrocSwap/integer-mult-bounds#1175) moved since the census listing;
  the pinned heads are current at snapshot time (2026-10-14).
- Structured-input claims in these packages often carry the status "pending native and strict
  admission"; nothing here strengthens those statuses.
- No new kappa, no accepted or rejected claim, and no selected-record change.

## Open next questions

- **Which proposal raises a cap rather than packing toward it?** Now that all 30 census-listed
  claims are screened inside the +0.87% band, the next cap-raising candidate must come from a
  changed local excess spend or a changed coverage law. First step: screen each new proposal's
  per-call profile with `ceiling.ceiling()` before a full replay. Blocker: none.
- **Should claims record `local_profile_per_call` and `idle_histogram` in their result JSONs?**
  This screen needed alias names and, for CrocSwap/integer-mult-bounds#1175, prose parsing; CrocSwap/integer-mult-bounds#1175's title kappa also
  disagrees with its package. First step: adopt the census's field names (or the CrocSwap/integer-mult-bounds#1200 request's)
  in each claim's result JSON. Blocker: the claim authors own those files.

## Credit

Every construction belongs to its claim's authors: G. V. Chudnovsky (CrocSwap/integer-mult-bounds#1175), tomdif and the
CrocSwap/integer-mult-bounds#1148-line authors (CrocSwap/integer-mult-bounds#1169 lineage), Rohan Arun ([PR 1183](https://github.com/CrocSwap/integer-mult-bounds/pull/1183) / [PR 1192](https://github.com/CrocSwap/integer-mult-bounds/pull/1192) / [PR 1201](https://github.com/CrocSwap/integer-mult-bounds/pull/1201) / [PR 1207](https://github.com/CrocSwap/integer-mult-bounds/pull/1207) / [PR 1218](https://github.com/CrocSwap/integer-mult-bounds/pull/1218) lineages), and
the authors of CrocSwap/integer-mult-bounds#1104/#1107/#1111/#1117/#1121/#1150/#1154/#1172/#1176 as cited in their packages.
The coverage identity is CrocSwap/integer-mult-bounds#1012's; the ceiling model and the queue-census method are Douglas
Colkitt's ([CrocSwap/integer-mult-bounds#1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240),
[CrocSwap/integer-mult-bounds#1264](https://github.com/CrocSwap/integer-mult-bounds/pull/1264)). This package was prepared by
Aaron Wang / navinor, with help from opencode.
