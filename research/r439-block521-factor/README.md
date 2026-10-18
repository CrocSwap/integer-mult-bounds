# R439 frame 521: 47 to 31 additions

**Finite bit-circuit construction; no new kappa.** This replaces the selected PR589 tuned R439 word's phase-B block at frame 521, `B[314:361]`, with an exact 31-addition positive-integer factorization. The old block uses 47 additions. Its required literal reverse cleanup loses the same 16 additions, so complete local ADDs fall from **24,305 to 24,273**. No helper, source read, copy, frame transition, or recursive child is added.

The construction is independently reviewable, but it is not an unrestricted XOR-minimum claim and does not update the selected word or certificate. The current selected conditional value remains `kappa = 0.001661634653669567`; the selected composition is complex-bound. A hosted program, physical invoice, supplier binding, and outer assembly for this candidate have not been built.

## Reproduce

From repository root, using Python 3.11+ and the standard library:

```sh
python3 -I -B research/r439-block521-factor/verify.py
```

Expected final line:

```text
PASS_R439_BLOCK521_FACTOR gates=47->31 ADDs=24305->24273 columns=661 controls=7 rank_mass=5129 kappa=unchanged
```

The verifier checks source SHA-256 pins; the exact integer block map; all 4,096 Boolean block inputs; entrywise domination of the reverse positive map; the splice and literal cleanup; every register frame path; all 661 dirty-input endpoint columns; the inherited H1-H5 interface; paid profile and rank mass; exporter records; positive-prefix payload; and seven meaningful corruptions. It imports the pinned owning interface checker and record exporter, but never imports the search.

The bounded nomination can also be reproduced:

```sh
python3 -I -B research/r439-block521-factor/search.py --output /tmp/r439-block521.json
cmp /tmp/r439-block521.json research/r439-block521-factor/CANDIDATE.json
```

## Exact object

The source is `research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz` at SHA-256 `e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`. The half-open slice is `B[314:361]`, frame 521, on ordered registers `[10,13,32,34,39,42,76,79,83,85,104,107]`. `CANDIDATE.json` records all replacement gates and binds them to base commit `f567884aeb8851b6e794af1184119a3bfbe1e631`.

Both old and new blocks have the same 12-by-12 positive-integer transfer matrix. Therefore they agree over every commutative coefficient ring and, in particular, on arbitrary dirty F2 inputs. Cleanup is rebuilt as the literal reverse of all source/helper writes in A followed by B at the full frame, preserving H4 and restoring the same arbitrary contents.

## Costs and bounds

| Complete local quantity | Original | Candidate |
|---|---:|---:|
| Frame-521 additions | 47 | 31 |
| Frame-521 cleanup additions | 47 | 31 |
| Complete ADD records | 24,305 | 24,273 |
| All scalar records | 27,234 | 27,202 |
| Rank-seven COPY / ERASE pairs | 9 / 9 | 9 / 9 |
| Paid rank mass | 5,129 | 5,129 |
| Positive forward prefix | 49,347 | 41,191 |
| Positive reverse prefix | 1,113,070 | 1,005,338 |
| Local payload | 93 bits | 92 bits |

The reverse candidate matrix is entrywise no larger than the old one, with 28 strict entries and entry sum 135 instead of 405. All 661 register frame paths and the complete paid histogram `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` remain unchanged. Every gate and its restoration are included in the bills.

## Bounded search

The assignment seed was drawn from operating-system randomness: **10**, placing the work in the bit-supplier track. Three narrow candidates were frames 507, 521, and 522; `10 mod 3 = 1` selected frame 521. A preliminary orientation run on frame 507 found a 24-gate candidate, but frame 521 remained the claimed and packaged seed-selected object.

The committed search runs exactly 12,000 seeded trials. Each trial performs legal row or column subtractions that retain a nonnegative integer matrix and stops at the identity, when no subtraction is available, or at the incumbent gate count. It found 1,323 integer factorizations; seven also satisfied reverse domination. The incumbent sequence was 36, 34, 33, 32, and 31 gates, with 31 first reached at trial 2,157. This completed finite search is only evidence within the stated randomized class; it is not an impossibility result or proof that 31 is minimal.

## Scope and assumptions

This package proves a finite circuit replacement and verifies its local scalar/interface accounting. It does not regenerate nine-stage hosting, a physical invoice, the selected supplier binding, or the 47-constraint outer assembly, and claims no new kappa. Finite replay does not prove the complete multiplication theorem.

The selected construction's inherited all-size/compiler, common-label/mutable-source, whole-call hosting, precision/tape, exact-recovery, and analytic hypotheses remain open. `upstream/`, the selected frontier, and predecessor packages are unchanged.

## Attribution

This builds on eumemic's PR555 R439 construction and interleaved interface, DreamingOfClouds' PR589 tuning, Dylan Crow's exporter/checker lineage, and all predecessor notices retained by those packages. PR873 supplied a useful independent-verifier pattern and a distinct nearby frame-508 construction; this work targets frame 521 and uses a different bounded positive-factor search.

Prepared by **martin Rv** with substantial **OpenAI AI assistance** in search design, implementation, verification, and writing. New files are offered under Apache-2.0. No delegated workers or independent human review are claimed.

## Maintainer checkpoint binding

The integrated package reads `certificates/checkpoints/frontier799.json` instead
of the moving selected-result pointer. The checkpoint bytes have the original
SHA-256; no source digest or mathematical witness was changed. This package
does not claim to replace the current selected construction.
