# Packing ceilings of the open complex κ claims

**A review aid built on [#1240](../complex-local-word-ceiling/README.md). No new κ; no claim is accepted or
rejected.**

Thirty open PRs state a conditional κ above the selected 0.001672660197076918 (listed 2026-10-13). For each
one, I looked inside a single package for four things:

- a complex profile whose κ equals the title κ;
- its live stock W and call count N;
- its idle-remainder histogram;
- the coverage law `mass = 72W + 64N` holding for that profile.

**14 claims** meet all of this and are pinned by PR head, path and Git blob in `SNAPSHOT.json`; `rebind.py`
re-reads them. The other 16 are listed with the reason. Each covered profile splits into a local word and idle
remainders. #1240's exact relaxation then bounds what any hosting, owner or idle repacking of that word can
reach.

## Result

All 14 obey the coverage law at 896/9 live families per call. Every claim's endpoint lies below its own word's
ceiling. They have **nine distinct per-call paid rank profiles** in two groups. The W-labels below
identify profiles, not proven circuit identities.

| Profile | Local profile per call | Approximate cap on κ | vs. selected word | Claims (κ, headroom left) |
|---|---|---:|---:|---|
| W1 | `1:2406 2:432 3:426 4:138 5:84 8:8` | **0.0016873148** | +0.007% | #1124, #1130 (0.0016730, 0.86%) |
| W4 | `1:2406 2:432 3:424 4:142 5:82 8:8` | 0.0016872744 | +0.004% | #1152 (0.0016743, 0.77%) |
| W5 | `1:2412 2:418 3:434 4:138 5:84 8:8` | 0.0016872431 | +0.002% | #1157 (0.0016741, 0.78%) |
| W2 = selected word | `1:2412 2:418 3:432 4:142 5:82 8:8` | 0.0016872026 | 0 | #1129, #1131 (0.0016741, 0.78%) |
| W8 | `1:2358 2:504 3:408 4:134 5:80 8:8` | 0.0016843188 | −0.171% | #1195 (0.0016757, 0.52%) |
| W9 | `1:2364 2:498 3:414 4:126 5:84 8:8` | 0.0016842610 | −0.174% | #1196, #1204, #1225 (0.0016756, 0.52%) |
| W3 | `1:2364 2:498 3:412 4:130 5:82 8:8` | 0.0016842207 | −0.177% | #1148 (0.0016756, 0.52%) |
| W6 | `1:2372 2:494 3:414 4:126 5:84 8:8` | 0.0016838172 | −0.201% | #1178 (0.0016752, 0.52%) |
| W7 (mixed providers, mean per call) | `1:2353.0 2:509.0 3:412.5 4:127.5 5:82 8:8` | 0.0016836800 | −0.209% | #1193, #1239 (0.0016758, 0.47%) |

What this shows:

- **Within the stated model, every covered profile and any repacking that preserves it satisfies κ < 0.001687314840.** The whole
  covered queue is a packing contest inside a 0.87% band above the selected κ.
- **The leading claims (#1148 line) sit on *lower*-ceiling words.** Their joint-entrance words move local mass
  from rank 1 to rank 2: 5,590 against 5,584–5,586 per call. That lowers the ideal limit by about 0.17–0.21%.
  They lead because they are packed closer to their limit (0.47–0.52% headroom left, against 0.77–0.86%).
  This is a comparison of realized profile costs with their relaxations. It does not independently
  validate helper placement or classify every circuit change; the relaxed paid-profile cap did not improve.
- **For reviewers:** claims with the same paid profile share this relaxation cap, but may use different
  circuits. A lower upper bound does not imply a lower attainable optimum. The optimistic headroom from
  the leading covered claim to the highest cap is about 0.7%; realizing it is an open construction problem,
  not a consequence of transplanting another word's packing fraction.

## Not covered

The 16 claims not covered (#1104, #1107, #1111, #1117, #1121, #1150, #1154, #1169, #1172, #1175, #1176, #1183,
#1192, #1201, #1207, #1218) record no complex profile matching the title κ together with an idle histogram in the
same package. Their words may differ. Adding a `local_profile_per_call` and `idle_histogram` to each claim's
result JSON would make them checkable; see the workflow feedback in #1200.

Caps are planning bounds (`κ < a/(1+a)`). They allow fractional counts and ignore helper widths, windows and
chronology. They bound repacking of a fixed word under a fixed template, coverage law and halving guard, and
nothing else. The snapshot reflects PR heads at 2026-10-13; #1172 moved between listing and fetch, and its
fetched head was used.

## Reproduce

```sh
python3 -I -B research/complex-queue-ceiling-census/verify.py            # ~12 s, PASS_COMPLEX_QUEUE_CEILING_CENSUS
python3 -I -B research/complex-queue-ceiling-census/rebind.py --fetch    # network; re-reads every pinned blob
```

This package depends on `research/complex-local-word-ceiling/ceiling.py` (#1240). During integration,
its source binding was updated to merged #1240, whose calculator adds the optional `unpaid=1`
parameter. The census uses that unchanged default and reproduces its original `RESULT.json`
byte for byte. `TASK.json` and `SOURCES.json` retain the original base and changed source pins.

## Open next questions

- **Can a W1/W2-type word be packed as tightly as the #1148 line?** The highest relaxed cap leaves at most about +0.7% over the leading covered claim;
  reaching the same fraction of a cap does not itself realize all of that headroom. A first step is to transplant the #1148 line's owner/entrance packing method onto
  W1's helper widths and measure the realized fraction of the cap. The blocker is that the joint-entrance method
  changes the word, so the transplant must keep W1's paid profile.
- **Which change raises a cap rather than packing toward it?** Only a lower local excess spend (#1240's budget)
  or a changed coverage law does. A first step is to screen each proposal's per-call profile with
  `ceiling.ceiling(...)` before a full replay. It is not blocked.

## Credit

Every construction belongs to its PR's authors: tomdif (#1148 line), rohanarun, jeremykothe2 and the other
listed contributors. The coverage identity is PR1012's. Prepared by Douglas Colkitt with substantial Claude
(Anthropic) assistance. Apache-2.0.
