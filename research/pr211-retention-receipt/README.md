# PR211 source retention and saved-certificate reconciliation

**Research consolidation; no new kappa.** All 25 paths in Rohan Arun's
[#211](https://github.com/CrocSwap/integer-mult-bounds/pull/211)
(`c63e50a5dde96fe1459d6b29e55e47f42f104347`) and its 6,191 cascade-optimized
operation frame bases are authenticated offline by raw Git commit, tree and blob
identities, reconciled against the Round-9 replay record and parent PR205's
certificate, and credited in [CONTRIBUTORS.md](../../CONTRIBUTORS.md).

At base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, the
[PR ledger](../../docs/research/pr-ledger.json) records PR211 as
`partially_reviewed` with `integration_location: []` because PR211 was in draft
state when the `next100` reconciliation batch (`#153–#303`) selected 100
non-draft PRs, even though PR211 had already passed
`complete-changed-work-replay-passed` at the exact same head in the
[Round-9 audit](../community-round9-audit/review-ledger.json) and its 6,191
cascade-optimized frame bases were incorporated into downstream `next100`
packages. This receipt establishes exact 25-path source coverage and restores
missing PR211 credit in [CONTRIBUTORS.md](../../CONTRIBUTORS.md) without
changing ledger dispositions or converting source retention into mathematical
approval.

## Exact sources and coverage

| Role | Commit and path |
|---|---|
| Original comparison merge-base | `3b6b66891c0ac888521cf591fe306c6286601d4f` |
| Direct parent (PR205) | `95c58706ad231d532bd7038308946a0344d08186` (`research/packed-diagonal-bit`, tree `409a4737d6ca0aa6c59f40b732c5d4608e705246`) |
| PR211 head | `c63e50a5dde96fe1459d6b29e55e47f42f104347` (`research/cascade-frames-bit`, tree `1708e493cbb1931e4fd11eca058b72193dfec3ac`) |
| PR210 retained frame bases | `b0c058ba979c748bb3a8604bfb6502e9fac9b84d:research/coordinated-crossover-pr200/search/pr211-frames.json` |
| PR217 retained compressed bases | `b739fc226a54a4a507989aa1bef092d491287451:research/butterfly-coordinated-bit-211/opframe-bases.json.gz.b64` |
| Published `next100` archive | `bd1b279e5e5449f81ca262c1647961e81dd69e50`, tag `archive/pr-reconciliation-next100-20261013` |

[SOURCE-PROOF.json](SOURCE-PROOF.json) contains 41 raw Git objects: six commits,
21 trees, and 14 blobs. Its authenticated commit differences establish:

1. **12 inherited PR205 paths (`MERGE_BASE..PR205`):** PR211's direct parent is
   Rohan Arun's incorporated [#205](https://github.com/CrocSwap/integer-mult-bounds/pull/205).
   All 11 files in `research/packed-diagonal-bit` (common subtree
   `409a4737d6ca0aa6c59f40b732c5d4608e705246`) and
   `.github/workflows/packed-diagonal-bit.yml` (blob
   `b00ddc44b8f866f57a62a82dd7ba6b43894301b6`) survive unchanged in PR211.
2. **13 direct PR211 paths (`PR205..PR211`):** PR211 adds the 12-file subtree
   `research/cascade-frames-bit` (`1708e493cbb1931e4fd11eca058b72193dfec3ac`)
   and `.github/workflows/cascade-frames-bit.yml`
   (`aed05819ec6a716b8de02d243b447031ef1309a1`):
   - `opframe-bases.json` (4,977,602 bytes, Git blob
     `8433d7724cbed83401fa42beee8653c62657ec0d`, SHA256
     `56b2ed0f6b867e8cafdc32ac70419cfda36d02838844572098b3fc77f8026e58`) is
     retained byte-for-byte in eumemic's incorporated
     [#210](https://github.com/CrocSwap/integer-mult-bounds/pull/210) at
     `research/coordinated-crossover-pr200/search/pr211-frames.json` and as
     gzip+base64 (`6b3b66eaa484a50f1f45ab9f7515a1b4ff26897f`) in Henry Grant's
     incorporated [#217](https://github.com/CrocSwap/integer-mult-bounds/pull/217)
     at `research/butterfly-coordinated-bit-211/opframe-bases.json.gz.b64`,
     whose decompressed payload matches both hashes identically.
   - `NOTICE` (`9edc2572378be7a7819f229de985eeaffa1173b6`), `banks.py`
     (`6505ebd37e3414016168511cca7c2f69216cc9f1`) and `controls.py`
     (`51235415282f631caa4402e80b72f84915ff977d`) match their retained copies
     in PR205 (and `NOTICE` is also retained in PR210, PR217 and
     [UPSTREAM-NOTICE](UPSTREAM-NOTICE)).
   - All 9 remaining direct files (`.github/workflows/cascade-frames-bit.yml`,
     `README.md`, `SOURCE.json`, `arithmetic.py`, `audit.py`,
     `certificate.json`, `frames.py`, `packing.py`, `verify.py`) are stored as
     authenticated raw Git blobs in [SOURCE-PROOF.json](SOURCE-PROOF.json).

## Saved-certificate and histogram reconciliation

The standalone checker imports no predecessor code. It reconciles five
authenticated objects: the 6,191 frame bases in `opframe-bases.json`, PR211's
`SOURCE.json` and `certificate.json`, PR205's baseline `certificate.json`, and
the Round-9 fresh replay log
[`pr211-changed.log.txt`](../community-round9-audit/pr211-changed.log.txt):

- **Frame-base inventory:** `opframe-bases.json` contains 6,191 distinct
  operation indices in `0..40,265` with integer basis matrices of dimensions
  `3..21` (65,501 total basis rows of length `h = 24`).
- **Round-9 certificate equality:** All five sections of `fresh` in
  `pr211-changed.log.txt` (`admitted`, `physical`, `arithmetic`, `independent`,
  `bank_controls`) match PR211's `certificate.json` identically, with
  `pinned_bit_files = 2,242`.
- **34-sink terminal reduction:** Between `overridden_profile` (`W = 20,668`,
  `R = 17,148`, `rank_per_vertex = 1,486,160`) and `profile` (`W = 20,634`,
  `R = 17,114`, `rank_per_vertex = 1,483,712`), the 34 terminal sinks apply
  `terminal_child_delta = {"3": -102, "21": -102}`, reducing rank mass by
  `3 * 102 + 21 * 102 = 2,448` while preserving `deficit_per_vertex = 1,936`.
- **Unpacked and 3-copy banked child-histogram deltas (PR205 -> PR211):**
  Replacing PR200's frames with PR211's 6,191 cascade-optimized frames leaves
  all common parameters (`m = 72`, `W = 20,634`, `N = 1,936`,
  `total_rank = 1,483,712`, `maxchild = 60`) invariant and changes the unpacked
  child histogram only on internal ranks `1..19` in exact multiples of `3`:

```text
du = +366*H1 + 2022*H2 - 333*H3 - 873*H4 - 552*H5 + 213*H6 - 369*H7
     - 675*H8 - 84*H9 + 270*H10 + 123*H11 + 336*H12 - 24*H13 - 210*H14
     + 81*H15 + 108*H16 + 132*H17 - 282*H18 + 282*H19.
```

  This shifts child count by `+531` while conserving rank-weighted mass
  (`sum r * du[r] = 0`). Completed-bank packing (`copies = 3`, `banks = 45,842`,
  `W = 56,402`, `rank_mass = 4,055,136`, `deficit = 5,808`) pops the `6,600`
  rank-60 gauge children and triples all internal multiplicities, so the banked
  histogram delta is `dp = 3 * du` (`+1,593` children, `0` rank-mass delta).
- **Exact rational recurrence and assembly:** The three-level ordinary-leaf
  recurrence `a_j = (1 - c)*c + c*a_{j-1}` and balanced assembly ceiling with
  `eta = beta = 10^-24` reproduce PR211's conditional grid value
  `kappa = 683847872495777/10^18` above PR207 (`1366380910073/(2*10^15)`) and
  PR205 (`683061299399923/10^18`).

## Reproduce

From the repository root, using Python 3.12 and its standard library:

```sh
python3.12 scripts/research_package.py --package research/pr211-retention-receipt
```

This runs the read-only checker and 19 unit tests: one positive case and 18
failure controls. Expected output includes:

```text
PASS_PR211_RETENTION_AND_CERTIFICATE_RECONCILIATION paths=25 direct=13 frames=6191 child_delta=531 mass_delta=0
Ran 19 tests
OK
PASS_REGISTERED_RESEARCH_PACKAGE research/pr211-retention-receipt outcome=completed
```

The direct `python3 -I -O -B research/pr211-retention-receipt/verify.py` command
needs neither Git nor network access, only this package and the four immutable
audit inputs listed in [VERIFY.json](VERIFY.json). To recollect
`SOURCE-PROOF.json` from locally fetched Git objects, run
`python3 -I -B research/pr211-retention-receipt/collect.py --output /tmp/pr211-proof.json`.

## Task and overlap

Assigned by `scripts/choose_research_task.py` without rerolling (OS-random seed
`a690c28b61e61a128b496b24d98aba3b`, track `consolidation`, task `overlap-receipt`,
scope key `757723e3fd38f20fa774`), refined to PR211 source retention,
downstream `next100` (`#205/#210/#217`) frame-base authentication, Round-9
certificate reconciliation, and `CONTRIBUTORS.md` attribution repair. Among the
12 `partially_reviewed` starting-snapshot PRs with empty `integration_location`,
PR99 was already closed by `research/pr99-retention-seed99`; PR211 was selected
because it already has a passing Round-9 exact-head replay in `main` and 42+
downstream `next100`/`third100`/`fourth100` citations, yet had zero mentions in
`CONTRIBUTORS.md` and no competing open PR or discussion claim. The
[coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18936472)
was posted before package implementation.

## Open next questions

No further source-retention experiment for PR211 is justified by this receipt:
all 25 changed paths (12 inherited from PR205 and 13 direct files) and the 6,191
frame bases are accounted for and reconciled with the Round-9 certificate. That
does not settle inherited all-size compiler, completed weighted/restored
selector, routing, precision/recovery, or formal multiplication proof
obligations, which remain outside this source-retention result; neither the
ledger's historical disposition nor the selected frontier is changed.

## Credit

Rohan Arun (@rohanarun) supplied PR211's cascade-optimized operation frames and
PR205's completed-bank bit supplier. eumemic supplied PR210's coordinated
crossover integration and PR168 lineage; Henry Grant (@hcg890) supplied PR217's
paid XOR butterfly integration; Dugongue supplied PR207/PR216/PR227; Chafik
Boukhalfa (@chafreaky) supplied PR200's diagonal bit word and checkers; Evan
McKinney (@evmckinney9) supplied PR197's completed-bank packing; Avi Eisenberg
(@ikeboy) supplied PR193's complex supplier; maxime-fleury supplied PR204; and
Douglas Colkitt and the maintainer audits retained the Round-9 and `next100`
records. The original [UPSTREAM-NOTICE](UPSTREAM-NOTICE) is preserved byte for
byte.

Prepared by steph4n (@steph4n-gh) with substantial Google Gemini assistance in
source investigation, implementation, verification and writing. No independent
human review is claimed. New work is Apache-2.0; predecessor licenses and
notices remain in force.
