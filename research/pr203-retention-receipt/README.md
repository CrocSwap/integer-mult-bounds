# PR203 source retention and saved-certificate reconciliation

**Research consolidation; no new kappa.** All 29 paths (`195,812` bytes) in
huxint's [#203](https://github.com/CrocSwap/integer-mult-bounds/pull/203)
(`d2873e20750d0949d2ad75cbc4cd82b5b1a74e84`,
`research/percent-exponent-architecture`) are authenticated offline by raw Git
commit, tree and blob identities, linked to their pinned upstream inputs in
Rohan Arun's [#187](https://github.com/CrocSwap/integer-mult-bounds/pull/187)
and Avi Eisenberg's [#193](https://github.com/CrocSwap/integer-mult-bounds/pull/193),
reconciled against the Round-9 replay record and recomputed exact rational/binary
screens, and credited in [CONTRIBUTORS.md](../../CONTRIBUTORS.md).

At base `534de584c7c9b7abd621a0d8cec959d021e5b510`, the
[PR ledger](../../docs/research/pr-ledger.json) records PR203 as
`partially_reviewed` with `integration_location: []` because PR203 had
`draft: true` when the `next100` reconciliation batch (`#153–#303`) selected 100
non-draft PRs, even though PR203 had already passed `scoped-replay-passed` at the
exact same head in the
[Round-9 audit](../community-round9-audit/review-ledger.json) and its structural
ceilings, copied-center support lower bound, common-triangular-flag theorem, and
87-topology balanced-Fano stub-reuse screen were cited across incorporated
`next100` packages ([#204](https://github.com/CrocSwap/integer-mult-bounds/pull/204),
[#288](https://github.com/CrocSwap/integer-mult-bounds/pull/288)) and merged
three-register bit-obstruction packages on `main`
(`research/bit-three-register-lower-bound`,
`research/bit-dyadic-ternary-catalyst`,
`research/bit-faithful-finite-address`,
`research/bit-identical-three-targets-dirty`,
`research/bit-dirty-auxiliary-registers`,
`research/three-register-modular-audit`). This receipt retains all 29 original
files as authenticated Git objects and restores missing PR203 credit in
[CONTRIBUTORS.md](../../CONTRIBUTORS.md) without changing ledger dispositions or
converting source retention into a new construction or universal barrier claim.

## Exact sources and coverage

| Role | Commit and path |
|---|---|
| Original comparison merge-base | `3b6b66891c0ac888521cf591fe306c6286601d4f` (Round-8 `main`) |
| PR203 head | `d2873e20750d0949d2ad75cbc4cd82b5b1a74e84` (`research/percent-exponent-architecture`, tree `1f3d82dd561239625548eba0b3f01728c5aacd38`) |
| PR187 pinned bit checkpoint | `201737a1ec4f936e166e2481fb9e88104cb2ccc7:research/source-assisted-bit-bootstrap/emitted-physical.json` (blob `035552f14bf74ae7c951aa0a0cc5382b6e51e4ea`) |
| PR193 pinned complex checkpoint | `187e1010ac8b259af8e9b5166f68b64bc27b4b47:research/source-assisted-v4/certificate.json` (blob `1bf00cdb8472c0992a9846af38778ed86eb909e0`) |
| PR193 pinned Fano baseline scripts | `187e1010ac8b259af8e9b5166f68b64bc27b4b47:scripts/experiments/balanced_fano.py` (`136446fa017ae8370c3f069d98ba278f4c5f96ce`) and `scripts/experiments/fano_completion.py` (`86a0ec6e62fc9a371f03d0e87457a085c9e494f3`) |
| Published `reconciliation92` archive | `b91de239a64d24d8aee409a0f4ac3e00710ae5c1`, tag `archive/pr-reconciliation100-20261013` (retains PR187) |
| Published `next100` archive | `bd1b279e5e5449f81ca262c1647961e81dd69e50`, tag `archive/pr-reconciliation-next100-20261013` (retains PR193, PR204, PR288) |

[SOURCE-PROOF.json](SOURCE-PROOF.json) contains 60 raw Git objects: six commits,
21 trees, and 33 blobs. Its authenticated commit differences and tree walks
establish:

1. **Complete 29-file PR203 inventory (`MERGE_BASE..PR203`):** PR203's direct
   parent is Round-8 `main` (`3b6b66891c0ac888521cf591fe306c6286601d4f`). It adds
   `.github/workflows/percent-exponent-architecture.yml` (blob
   `b22fdbd4e01db1c284bf028d4f8f2da716327340`) and the 28-file subtree
   `research/percent-exponent-architecture`
   (`1f3d82dd561239625548eba0b3f01728c5aacd38`), matching the 29 `source_files`
   recorded in the Round-9
   [`review-ledger.json`](../community-round9-audit/review-ledger.json) and the
   27-file SHA256 manifest in `research/percent-exponent-architecture/SOURCE.json`
   (which hashes every package file except `SOURCE.json` itself). All 29 blobs
   (`195,812` bytes total) are stored verbatim in
   [SOURCE-PROOF.json](SOURCE-PROOF.json), and `NOTICE`
   (`617d9e0ac5ca10d23741382e96ca8bb524ca4013`) is preserved byte-for-byte in
   [UPSTREAM-NOTICE](UPSTREAM-NOTICE).
2. **Upstream provenance authentication (`PR187` and `PR193`):**
   - `inputs/bit-pr187.json` pins `201737a1ec4f936e166e2481fb9e88104cb2ccc7:research/source-assisted-bit-bootstrap/emitted-physical.json`
     (SHA256 `5f1f1d978937b816a14b07fee5ac8fc31f3a9aaf05046a477e8be57bb6d07ce6`),
     retained via `archive/pr-reconciliation100-20261013`, and extracts its
     exact physical profile (`W = 21,108`, `m = 72`, `h = 24`, `v = 1,760`,
     `rank = 1,517,840`, `deficit = 1,936`, `loss = 528 = h(h-2)`).
   - `inputs/complex-pr193.json` pins `187e1010ac8b259af8e9b5166f68b64bc27b4b47:research/source-assisted-v4/certificate.json`
     (SHA256 `d84406d2fcc6990deba2b135509e6d86600e57123d88f9b21f7b7240e1aeb513`),
     retained via `archive/pr-reconciliation-next100-20261013`, and extracts its
     exact `complex_profile` (`W = 12,052`, `m = 66`, `h = 22`, `v = 1,320`,
     `rank = 794,112`, `deficit = 1,320`, `loss = 440 = h(h-2)`).
   - `references/SOURCE.json` pins `scripts/experiments/balanced_fano.py`
     (SHA256 `1586fb1db4f40e79e97bae59f47192675663403bbcacbf5f4e0b702edfd22b0a`)
     and `scripts/experiments/fano_completion.py` (SHA256
     `6cade2a36b910bf7e68a872dc4fd3560837935cffe80f9526cd012a28b247738`, also
     retained identically on `main`).

## Saved-certificate and screen reconciliation

The standalone checker imports no predecessor code. It recomputes and reconciles
all four exact mathematical screens in PR203 against the saved certificates and
the Round-9 replay log
[`pr203-replay.log.txt`](../community-round9-audit/pr203-replay.log.txt):

- **Fixed-itinerary and odd-cube ceiling certificate (`ceiling-certificate.json`):**
  Using 40-term rational `atanh` logarithm enclosures on `GRID = 10^24` and
  12-term positive Taylor uplift:
  - For `complex-pr193` (`m = 66, h = 22, v = 1,320`), discarding all auxiliary
    entropy yields `retained_loss_a_ceiling = 62500000000000000000000/14097718425315630061316769`
    ($\approx 0.004433$) and `free_center_a_ceiling = 125000000000000000000000/14097718425315630061316769`
    ($\approx 0.008867 < 0.009$).
  - For `bit-pr187` (`m = 72, h = 24, v = 1,760`), discarding all auxiliary
    entropy yields `retained_loss_a_ceiling = 25000000000000000000000/5108721919863830223667609`
    ($\approx 0.004894$) and `free_center_a_ceiling = 500000000000000000000000/56195941118502132460343699`
    ($\approx 0.008897 < 0.009$).
  - Across all `182` finite odd-cube cases (`4 <= p <= 29`, odd `3 <= d < p`,
    `133` with positive deficit, scan SHA256
    `cebf8348bf5dc03f528e809648ed3062340b1d7aaf7b47924e157659f0e374ac`), the
    destructive-parity itinerary peaks at `(p = 14, d = 5)` with
    `a_ceiling < 0.005164` (`1291/250000`), and arbitrary local data chains of
    endpoint distance `h - 1` peak at `(p = 13, d = 5)` with
    `arbitrary_local_chains_a_ceiling < 0.008094` (`4047/500000`), while the
    `p >= 30` tail stays below `2 / ((12*30 - 2) * ln 3) < 0.005086`.
  - Exact Walsh projector and $K^2 = \frac{1}{4} I$ checks pass for
    `d in (3, 5, 7)`, all five copied $t$-star binary span checks attain rank
    $2p - 2t$, and the one-deficit `(m = 3, W = 30)` vs `(m = 3, W = 31)` bit
    recurrence brackets `1/99`.
- **Rank-minimal copied-center lower bound (`center-basis-certificate.json`):**
  For `p in (5, 6, 11, 13, 16)` (`h = 2p`), the $h \times h$ rational port
  incidence Gram matrix is invertible (`incidence_rank_Q = h`), single-star and
  omitted-pair combinations achieve sharp $\mathbb{F}_2$ source-support rank
  $h - 2$ (loss floor $h(h - 2)$), the `p = 4` excluded-domain control drops to
  support rank $4 < 6$, and all $3^{10} - 1 = 59,048$ nonzero ternary coefficient
  vectors at `p = 5` have certified $\mathbb{F}_2$ support rank at least $8$.
- **Common-triangular-flag obstruction (`triangular_obstruction.py`):**
  Recomputes the exact rational basis-conjugation and commutativity rejection
  controls (`rank_lower_bound = W * m`, zero rank deficit under any common
  upper-triangularizing flag).
- **87-topology balanced-Fano stub-reuse screen (`enumeration-controls.json`,
  `fano-all-permutations.json`, `fano-reuse-certificate.json`,
  `discovery/receipts/vector-k*.json`):**
  Recomputes all 8 direct full-word brute-force controls and all 87 chronological
  balanced-Fano stub-reuse topologies (specification SHA256
  `c423c71fd035fbb6b0428163b87680939eb3a6596962082e39d0823f3e3183b2`, width
  histogram `{"6": 4, "7": 32, "8": 38, "9": 12, "10": 1}`), reconciles the 16
  obstruction-preserving topologies (`ids = [0, 3, 4, 13, 16, 34, 36, 37, 41, 43,
  47, 50, 60, 62, 67, 70]`, width histogram `{"7": 2, "8": 7, "9": 6, "10": 1}`)
  with the 16 `PASS k/16` lines in `pr203-replay.log.txt`, and verifies the
  five block-vector solver discovery receipts (`k = 2, 3, 4`, with canonical
  internal edge bases closing all 16 cases to `unsat` for `k = 3` and `k = 4`).

## Reproduce

From the repository root, using Python 3.12 and its standard library:

```sh
python3.12 scripts/research_package.py --package research/pr203-retention-receipt
```

This runs the read-only checker and 21 unit tests: one positive case and 20
failure controls. Expected output includes:

```text
PASS_PR203_RETENTION_AND_CERTIFICATE_RECONCILIATION paths=29 bytes=195812 odd_cube=182 center_sweep=59048 fano_topos=87
Ran 21 tests
OK
PASS_REGISTERED_RESEARCH_PACKAGE research/pr203-retention-receipt outcome=completed
```

The direct `python3 -I -O -B research/pr203-retention-receipt/verify.py` command
needs neither Git nor network access, only this package and the seven immutable
repository inputs listed in [VERIFY.json](VERIFY.json). To recollect
`SOURCE-PROOF.json` from locally fetched Git objects, run
`python3 -I -B research/pr203-retention-receipt/collect.py --output /tmp/pr203-proof.json`.

## Task and overlap

Assigned by `scripts/choose_research_task.py` without rerolling (OS-random seed
`563d7e55de5891491987f38cb6b1508a`, track `consolidation`, task
`overlap-receipt`, scope key `757723e3fd38f20fa774`), refined to PR203 source
retention, upstream PR187/PR193 input authentication, Round-9 replay and
saved-certificate reconciliation, and `CONTRIBUTORS.md` attribution repair.
Among the remaining `partially_reviewed` starting-snapshot PRs with empty
`integration_location` (`#99` and `#211` having already been closed by
`research/pr99-retention-seed99` and `research/pr211-retention-receipt`), PR203
was selected because it already has a passing Round-9 exact-head replay in
`main` and is cited across incorporated `next100` PRs (`#204`, `#288`) and six
merged three-register bit-obstruction packages on `main`, yet had zero of its
29 files in `HEAD` and zero mentions in `CONTRIBUTORS.md`. The
[coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18961859)
was posted before package implementation.

## Open next questions

No further source-retention experiment for PR203 is justified by this receipt:
all 29 changed paths (`195,812` bytes), upstream PR187/PR193 inputs, and the
ceiling, copied-center, common-triangular-flag, and 87-topology Fano screens are
accounted for and reconciled with the Round-9 replay record. That does not
discharge C++ or solver re-execution during offline replay, nor does it extend
PR203's scoped architectural ceilings to overcomplete center sets, non-triangular
non-commuting frame families, larger block-vector Fano gates ($k \ge 5$), or the
inherited all-size multiplication theorem; neither the ledger's historical
disposition nor the selected frontier is changed.

## Credit

huxint supplied PR203's conditional architecture ceilings, rank-minimal
copied-center support lower bound, common-triangular-flag obstruction, and
87-topology balanced-Fano stub-reuse screen. Rohan Arun (@rohanarun) supplied
PR187's source-assisted bit checkpoint; Avi Eisenberg (@ikeboy) supplied PR193's
source-assisted v4 complex checkpoint; icekylinx, eumemic, an664, DaysSky
(PR192), and romainhedouin (PR183) supplied the paired-cube, bank-sharing,
entropy-ceiling, and balanced-assembly lineage credited in PR203's notice;
maxime-fleury (PR204) and eumemic (PR288) cited PR203 in `next100`; and Douglas
Colkitt and the maintainer audits supplied the Fano baseline scripts and
retained the Round-9, `reconciliation92`, and `next100` records. The original
[UPSTREAM-NOTICE](UPSTREAM-NOTICE) is preserved byte for byte.

Prepared by steph4n (@steph4n-gh) with substantial Google Gemini assistance in
source investigation, implementation, verification and writing. No independent
human review is claimed. New work is Apache-2.0; predecessor licenses and
notices remain in force.
