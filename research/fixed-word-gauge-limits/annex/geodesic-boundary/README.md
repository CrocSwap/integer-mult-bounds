# Common-boundary geodesic annex

This annex adds a reviewed rank obstruction for persistent productive
paths with common input and output frames. It permits arbitrary Clifford
frame gauges and exact fusion of adjacent native steps. Every productive
path, scalar access, and boundary contract remains fixed. The result
does not improve kappa or give a positive supplier exponent.

The [proof](frozen/lanes/source-domain/GEODESIC-BOUNDARY.md),
[producer receipt](frozen/lanes/source-domain/GEODESIC-CHECKS.json), and
[separate review](frozen/lanes/encoded-controller/review/GEODESIC-REVIEW.json)
are exact frozen campaign files. The [source manifest](SOURCES.json) and
[annex manifest](ANNEX-MANIFEST.json) bind the new dependency closure.
Every original primary-package file and its original `MANIFEST.json`
remain unchanged. [PARENT-SNAPSHOT.json](PARENT-SNAPSHOT.json) binds those
54 files. The primary manifest and replay retain their original scope.

## The theorem and the changed boundary premise

For a Clifford frame T in binary dimension n, write `L(T)=S(T)^-1 Z`,
where `Z={(0,z)}`. The frame distance is
`d(L,K)=n-dim(L intersect K)`. An exact native step from T to U has
Fourier rank `rho(U T^-1)=d(L(T),L(U))`. The triangle inequality gives
the sum of native ranks on a path at least its endpoint distance.
Left monomial wrappers preserve the distance. Their phase and address
costs remain nonnegative.

The circuit class has four conditions:

1. Retain the persistent array-register paths. An array permutation
   transports the path labels. Count each native event once.
2. Retain the scalar accesses. ADD and COPY require one common live frame
   on their operands. SCALE keeps the frame. Do not grant free native
   operator-valued scalar coefficients.
3. Do not clear a productive lifetime, reset its frame for free, or move
   it to private zero workspace and replace it by another lifetime.
4. Price every native event, including events that previously had rank
   zero. Exact adjacent fusion is allowed within these same conditions.

If N productive paths start at I and end at the full native frame F_n,
up to left monomial wrappers, then the total rank is at least `n N`.
The argument holds at each allowed tensor power and after averaging
over the finite cover. It does not assume equal values in cover classes.

This application imposes common I/full-F productive boundaries and an
identity joint content map. The primary package instead studies fixed
translation gauges of the original word, with its virtual-Q boundary
contract. The annex does not extend that original-boundary theorem to
every Clifford gauge. The original virtual-Q supplier is itself a
countercontrol to imposing the new common-boundary premise on all
correct suppliers. New lifetime transfers, changed scalar controllers,
joint recursive children, and different boundary encodings are outside
the annex theorem.

## Exact local and global application

Each full-mode and one-sided-mode word has 704 persistent paths. In both
orientations, all 3,486 paid climbs are nested upward steps. Their rank
mass is 5,522 and equals the sum of the path endpoint distances. The
event inventory also keeps all 1,570 rank-zero adapters. Changing the
112 X inputs from their line frames to I and the 112 Y outputs from
their complementary frames to full F raises the local endpoint sum to
5,746. Scalar uses separate the proposed boundary corrections from the
nearest paid climbs. A change of intermediate gauges still obeys the
path bound.

The global application is the direct common-frame inverse of the
one-shot controller. It uses the inherited exact mode endpoint, full-F
monomial access, and whole-owner backfill invoice. Its conditional
counts over all 16 replicas, per cover class, are:

| Quantity | Exact value |
|---|---:|
| Old productive families | 14,336 |
| New stopped mode families | 1,152 |
| Total productive families N | 15,488 |
| Rank mass before boundary normalization | 1,116,288 |
| Common-boundary lower bound `73 N` | 1,130,624 |
| Required added rank | 14,336 |
| Average added rank per replica | 896 |

The explicit input and output line normalizers use `2*4*112=896`
rank-one children per replica. Thus the rank bound is sharp for this
conditional route. Fusion can reduce the event count but cannot reduce
the complete rank mass. The rank-48 coordinate-split plan has moment
one at exponent zero and strictly greater than one at every positive
exponent. Any admitted fusion within ambient rank 73 still has moment
at least one for every nonnegative exponent. A positive supplier
exponent cannot follow from this route by frame gauges or fusion alone.

The [one-shot content proof](frozen/lanes/encoded-controller/ONE-SHOT.md),
[content review](frozen/lanes/encoded-controller/review/ONE-SHOT-REVIEW.json),
[native mode review](frozen/lanes/interface-proof/ONE-SHOT-MODE-REVIEW.md),
[mode receipt](frozen/lanes/interface-proof/ONE-SHOT-MODE-REVIEW.json),
[owner review](frozen/lanes/interface-proof/HOSTING-PATCH-REVIEW.md), and
[owner receipt](frozen/lanes/interface-proof/HOSTING-PATCH-REVIEW.json)
are inherited application evidence. Their relevant source receipts and
Walsh-mode proof are included. This replay does not rerun those native
or whole-owner checks. The numerical global application retains those
premises. It does not emit a global word, establish a new owner
allocation, price scalar or address work, or admit a supplier.

## Replay

Use Python 3.10 or later and its standard library. Use one CPU and allow
at least 3 GiB of memory. Keep this annex inside the full
`fixed-word-gauge-limits` package, since it consumes the already-pinned
parent source members and reader. Use a new external output directory.
From the repository root after publication:

```sh
python3 -I -O -B research/fixed-word-gauge-limits/annex/geodesic-boundary/replay.py --out /tmp/geodesic-boundary-annex
```

Expected final line:

```text
PASS_GEODESIC_BOUNDARY_ANNEX
```

The driver runs two checks in sequence. The producer audits all four
mode words and the conditional global invoice. The separate checker
rebuilds all 1,004 canonical Lagrangians by Gaussian nullspaces and uses
symplectic pairing ranks. Its complete two-bit control covers 720 frames,
518,400 ordered frame pairs, 3,375 metric triples, and 34,560 left
monomial checks. The general theorem rests on the written metric proof.

Three damage controls reject a wrong native rank, a productive-array
CLEAR, and an unequal-frame scalar access. A further matrix-order
control rejects the wrong relative operator order. These controls are
separate from the primary package's controls.

Normal and optimized cold replay results are in
[VALIDATION.json](VALIDATION.json). The producer receipt differs only in
the hash of the pinned portable parent reader. The independent receipt
updates actual file paths and hashes and runtime memory metadata; the
frozen historical `review_update` note stays in its original receipt.
All other typed JSON fields match. The exact I/O changes are recorded in
[PORTABILITY.patch](PORTABILITY.patch). No mathematical function changed.
No Git, network, search solver, or source monkey patch is needed.

## Source, credit, and limits

All mathematical source pins remain historical
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The
[archive check](ARCHIVE-CHECK.json) verifies the complete source archive
and the exact two members already present in the primary package.
The inherited selected assembly is historical. The publication base
remains `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, whose selected
construction is conditional
[PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470).
No transfer of this rank bound to that changed construction is proved.

The canonical-subspace port-gauge triangle argument is prior work in
[Section C.2, Theorem N](https://github.com/CrocSwap/integer-mult-bounds/blob/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/research/format-limits-corrected/README.md#L392-L438).
Its source credits DreamingOfClouds with Claude Opus 5.5 assistance.
The exact [source notice](sources/research/format-limits-corrected/NOTICE.md)
and [source license](sources/research/format-limits-corrected/LICENSE)
are retained. This annex gives the Lagrangian form for arbitrary Clifford
gauges, the actual mode-word audit, and the stated common-boundary
application. It claims no priority for the triangle argument.

The source-domain lane supplied the theorem and producer. The
encoded-controller review lane supplied the separate pairing and group
check. The history-encoding, encoded-controller, and interface-proof
lanes supplied the inherited mode, content, and hosting evidence.
The original supplier credit and Apache-2.0 notices remain in the
[primary notice](../../NOTICE.md) and [license](../../notices/LICENSE).
Substantial OpenAI Codex assistance was used. These are separate agent
reviews, not human peer review.

An implementation with new productive lifetimes, a different boundary
encoding, or a changed content controller needs its own proof. This
annex performs no new search and gives no general circuit lower bound,
new supplier admission, complete multiplication result, or kappa change.
