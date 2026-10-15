# Census round 2: packing ceilings for the sixteen uncovered open complex claims

**A review aid extending [the first census](../complex-queue-ceiling-census/README.md), built on
[#1240](../complex-local-word-ceiling/README.md). No new kappa; no claim is accepted or rejected.**

The first census (heads of 2026-10-13) covered 14 open claims and listed 16 as not covered: no
complex profile whose kappa equals the title kappa occurred together with an idle histogram in
those packages. This round re-audits the same 16 claims at their heads of 2026-10-15 and covers
13 of them, because the newer packages record the four screening inputs under a different key
convention than the first census's extractor looked for:

- the paid profile sits in a `data/SPEC.json` record under **`global_profile`**, together with
  `idle_remainder_profile`, `live` and an exact `kappa`, rather than under `complex_profile`;
- the same packages' `RESULT.json`/`CERTIFICATE.json` records carry `kappa` and the profile but
  no live/calls, whose identity inputs arrive from the sibling SPEC (`#1111` pairs a
  `CERTIFICATE.json` profile with an `idle_from` SPEC).

Every covered claim's record kappa equals its title kappa exactly, satisfies the coverage
identity `mass = 72*live + 64*calls` at 896/9 live families per call, and passes the idle split;
the per-call local word is then bounded with merged #1240's unchanged relaxation.

## Results (exact rational; `verify.py` regenerates RESULT.json)

Six of the seven T16-family claims share the first census's **W4 word**
(`1:2406 2:432 3:424 4:142 5:82 8:8`): #1104, #1107, #1117, #1121, #1150, #1172. #1169 reproduces
its **W3 word** (`1:2364 2:498 3:412 4:130 5:82 8:8`). Both caps are re-derived here from the
first census's own pinned inputs and match its stored strings byte for byte, cross-checking the
extraction path against the merged machinery.

| Word | Local profile per call | Cap on kappa | Claims (headroom left) |
|---|---|---:|---|
| V1 (first census W4) | `1:2406 2:432 3:424 4:142 5:82 8:8` | **0.0016872744** | #1104 (.87%), #1107 (.87%), #1117 (.86%), #1121 (.86%), #1150 (.87%), #1172 (.87%) |
| V2 (#1111, merged since round 1) | `1:43307/18 2:7633/18 3:15661/36 4:5003/36 5:82 8:8` | 0.0016863769 | #1111 (.81%) |
| V3 (first census W3) | `1:2364 2:498 3:412 4:130 5:82 8:8` | 0.0016842207 | #1169 (.52%) |
| V4 | `1:262220/111 2:55462/111 3:45824/111 4:14338/111 5:82 8:8` | 0.0016839954 | #1183 (.50%) |
| V5 | `1:261860/111 2:55822/111 3:46004/111 4:14158/111 5:82 8:8` | 0.0016835547 | #1192 (.47%) |
| V6 | `1:261194/111 2:56488/111 3:45560/111 4:14602/111 5:80 8:8` | 0.0016836527 | #1201 (.47%) |
| V7 | `1:261194/111 2:56488/111 3:45782/111 4:14158/111 5:82 8:8` | 0.0016836930 | #1207 (.47%) |
| V8 | `1:783550/333 2:169496/333 3:137362/333 4:42458/333 5:82 8:8` | 0.0016836800 | #1218 (.47%) |

What this adds to the first census:

- **The covered queue grows from 14 to 27 claims**; with #1169 on W3, every open claim whose
  title kappa exceeds 0.0016755 is now covered.
- **The leading T37-family claims (#1183-#1218) sit on lower-ceiling words** (caps 0.0016836-0.0016840,
  about 0.19-0.22% below the W1/W4 band), and they are packed close to their limits (.47-.50%
  headroom left). They lead on realization, not headroom - consistent with the first census's
  finding for the #1148 joint-entrance line, now measured on the current queue's own records.
- **#1111 merged between the two censuses**; its word remains below every open claim's cap.

## Still not covered: three claims and the fields they must record

#1154, #1175 and #1176 remain unscreenable at their pinned heads, all for the same reason: no
record in the package carries a kappa that equals that claim's own title kappa together with a
paid profile and an idle histogram. #1154 and #1176 vendor a predecessor's SPEC (whose kappa is
#1117's or #1148's); #1175's own SPEC records every field but a kappa that is not the claim's
own. To become checkable, per the workflow feedback in discussion #1200, each package should
record in one place:

1. the paid per-replica profile (`global_profile`, or `complex_profile`);
2. `idle_remainder_profile`;
3. `live`, with `calls` derivable (`live * 9 == 896 * calls`);
4. an **exact kappa equal to the claim's title kappa**.

`SNAPSHOT2.json` pins, per claim, the observed key sets at these heads, so a reviewer can see
exactly which of the four was wrong or missing.

## Provenance, controls and limits

- Heads are **frozen to the audited SHAs** in SNAPSHOT2.json (full pins, plus blob pins for
  profile and idle files). At least one claim (#1169) force-pushed a reworked package during the
  session, after its audit; the audited head pins here remain resolvable by SHA and are the
  ones the screens re-read. Claim-thread: [discussions/2739](https://github.com/CrocSwap/integer-mult-bounds/discussions/2739).
- `verify.py` checks every identity and split, re-derives every ceiling from the frozen snapshot
  data, requires each claim's `complex_lower` below its word's `a_lo` and its kappa below the cap,
  cross-controls against the first census's pinned W4 and W3 inputs, and runs two negative
  controls (a profile missing one coordinator unit violates the identity; an idle column beyond
  its profile column violates the split).
- `rebind2.py --fetch` re-reads all pinned blobs at the frozen heads
  (PASS_SNAPSHOT2_REBOUND 13).
- Caps are planning bounds (`kappa < a/(1+a)`), allow fractional counts, and ignore helper
  widths, windows and chronology. They bound repacking of each claim's own fixed word under the
  coverage law, 896/9 live families per call and the halving guard - not changed words,
  templates, outer recipes, or the two-unpaid-coordinates contract change proposed for the
  `coverage-law-change` card. They do not review or accept any claim.

## Reproduce

```sh
python3 -I -B research/complex-queue-ceiling-census-r2/verify.py            # ~10 s, PASS_COMPLEX_QUEUE_CEILING_CENSUS_R2
python3 -I -B research/complex-queue-ceiling-census-r2/rebind2.py           # needs the pinned PR-head objects (or --fetch)
python3 -I -B research/complex-queue-ceiling-census-r2/producer.py          # re-derives SNAPSHOT2.json offline at the frozen heads
python3 -I -B research/complex-queue-ceiling-census-r2/producer.py --fetch-prefixes --fetch-titles   # network: re-derive at live heads
```

## Open next questions

- **The three-claim checklist above is actionable by each claim's author.** Nothing on the
  verifier side blocks it; the round-3 pass is a re-run once they record those fields.
- **Snapshot cadence:** heads move hourly (#1169 moved mid-session). A dated re-run of
  `producer.py --fetch-prefixes --fetch-titles` would refresh this table; whether the queue
  census becomes a dated cadence is a maintainer decision.

## Credit

Every construction belongs to its PR's authors; this package only reads their recorded data.
The census method, coverage identity (PR1012) and the exact relaxation calculator are the first
census's and #1240's, unmodified. Prepared by Abhinav Ramachandran (geckods) with substantial
end-to-end assistance from a Hermes agent (Nous Research, GLM-5.3) under the standard donation
prompt in autoresearch.md. Apache-2.0.
