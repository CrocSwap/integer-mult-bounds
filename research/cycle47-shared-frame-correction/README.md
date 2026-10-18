# Shared correction basis for two plane-upgraded frames

**Exact local mechanism; no new κ or complete supplier.** This package answers a follow-up to the
single-frame plane-upgrade probe in [Discussion #2278](https://github.com/CrocSwap/integer-mult-bounds/discussions/2278).
For the selected P112 label set, two distinct orthogonal frames with the same binary direction use
correction matrices in one common rational rank-8 row space. The verifier constructs the coefficient
maps and tests their integrality denominator and F2 support ranks over the complete finite domain.

## Scope and model

The input is the selected 112-label `complex-nine-native/DATA-PHASES.json` member. The certificate
maps its 112 q labels bijectively to the 112 live lines of the exact E8 root-line model. It checks the
entire selected-label pairing and all eight deleted-frame signatures before using integer inner
products. For a frame `S` and binary direction `r` with `beta(r,a)=1` on `S`, let

```text
T(S,r) = { b in P112 \ S : beta(r,b)=0 and <a,b> is odd for some a in S }
M(S,r)[a,b] = <a,b> for b in T(S,r), and 0 otherwise.
```

Each `M(S,r)` is an exact 8 by 112 correction matrix of rational rank 8. Within each fixed-r
family, `verify.py` chooses one matrix `M0`, computes each exact coefficient matrix `C` from a
fixed nonsingular 8-column minor, and verifies `M=C M0` entrywise. Every family has denominator
LCM 2, so the common basis can be written `B=M0/2` with integer coefficient matrices `D=2C` and
`M=D B`. Their combined F2 row span has rank 4 in every family. Thus every pair in a same-r family
uses one rank-8 rational basis and at most a rank-4 F2 coefficient interface. The witness pair in
`CERTIFICATE.json` has pair coefficient rank 1. This is a finite exact construction, not an
inference from equal ranks.

The exhaustive domain contains all 1,260 orthogonal frames in P112, all 16 valid r values per frame,
all 135 distinct common directions, and all 1,539,720 same-r unordered frame pairs (20,160
frame-direction correction blocks). The certificate contains an explicit q-to-line map and a witness
pair; the verifier recomputes the entire census.

## Cost screen and limits

The selected local profile is `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` per call, with `m=73`,
896 families, nine stages, centre charge 64, and exact selected ceiling endpoint
`1690054109089/10^15`. At the 5% target `a*=35491136290869/20000000000000000`, the existing exact
ceiling calculator gives:

| Favorable scenario | Centre charge | Unpaid coordinates/family | Relaxation at a* | Gate |
|---|---:|---:|---:|---|
| One frame with its full correction charge | 72 | 15/14 | 1.000367800102… | fails |
| Two frames with one shared correction charge | 72 | 8/7 | 0.999388703606… | passes |
| Two frames charged independently | 80 | 8/7 | 1.000490187164… | fails |

These are exact outward intervals from the pinned calculator, displayed as decimals. The passing line
is only a favorable local screen. It does not include source access, copies, hosting, legality and
timing of both frames, interface transitions, restoration, precision/tape charges, all-size
realization, or the matching bit-side construction. The common rational basis has denominator 2;
its precision must be charged in a completed supplier.
Accordingly this package claims a shared correction mechanism, not an admitted local profile, a new
conditional bound, or a κ improvement.

## Reproduce

Python 3.10+ and the standard library are enough for the direct verifier:

```sh
python3 -B research/cycle47-shared-frame-correction/verify.py
```

Expected final line:

```text
PASS_CYCLE47_SHARED_FRAME_CORRECTION: 112 labels; 1260 frames; 1,539,720 pairs; 20,160 exact factorizations; ...
```

The registered package metadata uses the repository's Python 3.12 runner. Source commits, Git blobs,
and SHA-256 pins are in [SOURCES.json](SOURCES.json); exact run settings and controls are in
[VERIFY.json](VERIFY.json). Cycle metadata and remaining obligations are in [TASK.json](TASK.json).

## Open next questions

1. Embed the common-basis identity into a real nine-stage schedule where both frames and their source
   data are available, then account for all reads, copies, frame transitions and restoration.
2. Price the rational coefficient denominator and precision in the producer's actual coefficient
   convention. The local rank/F2 census does not establish that the projected +8 remains the complete
   correction charge.
3. Only after those steps, combine the local profile with a matching bit-side improvement and rerun
   the selected-record acceptance gates.

## Provenance, predecessors and credit

- Cycle 47; seed `95720468bbdedd321824e249074fc5a3`; track `complex-mechanisms`; task
  `complex-rank-shape-decoder`; scope key `02b31ebd160542c86299`; priority revision 4.
- Exact base commit `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; selected-record SHA-256
  `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- The direct predecessor is philippeVV's single-frame question in [Discussion #2278](https://github.com/CrocSwap/integer-mult-bounds/discussions/2278).
  Related but distinct work: [PR #1825](https://github.com/CrocSwap/integer-mult-bounds/pull/1825),
  [Discussion #2126](https://github.com/CrocSwap/integer-mult-bounds/discussions/2126),
  [PR #2041](https://github.com/CrocSwap/integer-mult-bounds/pull/2041), and
  [Discussion #2292](https://github.com/CrocSwap/integer-mult-bounds/discussions/2292). Current nearby
  work in [Discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245) and
  [PR #2251](https://github.com/CrocSwap/integer-mult-bounds/pull/2251) finds a 96-dimensional pooled
  correction space for P104's fixed trace; it concerns a different live set, matrix and timing model.
- The exact E8 line model follows the pinned `complex-frame-pair-decoders/verify.py` geometry;
  pricing reuses the pinned `complex-local-word-ceiling/ceiling.py` interval calculator. Their
  authors and upstream notices remain attributed in those source files.
- Prepared by Cinna Davis with substantial OpenAI Codex assistance. No independent human review is
  claimed. Apache-2.0.
