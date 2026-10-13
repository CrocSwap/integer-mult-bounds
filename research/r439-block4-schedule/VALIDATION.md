# Execution record

Executed on 2026-10-13, Windows x64, CPython **3.13.3**. The experimental base
is `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`. All commands below were run;
their scope is finite circuit verification, not a full multiplication theorem.

## Focused checks

| Check | Observed result |
|---|---|
| `python -I -B research/r439-block4-schedule/verify.py` | PASS; 661 columns in both directions, 13 rejected controls, complete certificate agrees |
| Same command with `-O` | PASS; checks remain active without Python assertions |
| `factor_search.py --output build/r439-block4-candidate-replay.json` | Byte-identical to `CANDIDATE.json`; exact minima 17 + 14 |
| `search.py --output research/r439-block4-schedule/INITIAL-SEARCH.json` | 2,000 trials, 20 identity factorizations below 41 steps, zero reverse-dominated candidates; a bounded failed search |
| Minimal isolated copy, in a path containing spaces, with `-I -O -B` | PASS using only the nine pinned source files and this package; no Git repository or third-party Python modules required |
| Isolated copy with a mandatory source pin removed | REJECT: `missing or unexpected source pin` |
| Isolated copy with one input gzip modified | REJECT: `source pin:` before decompression |
| Isolated copy with a forged stored addition count | REJECT: `stored certificate mismatch` |
| Isolated copy with a forged factor minimum | REJECT: `search coverage` |
| `python -B scripts/verify_selected_result.py` at the experimental base | PASS selected record, exact kappa, original source inventory and proof supplement: `1661202643272239/1000000000000000000` |

The local payload is 93 bits on both words. The candidate canonical JSON hash
is `a2b74144199d772676abdefdc24e572d2ecb443ccfa372988212f0793cd919c0`.
The source container and all owning checker hashes are in `SOURCES.json`.

## Native checks

The original C++ files were compiled unchanged with **MSVC 19.44.35223.0**,
Visual Studio Build Tools 2022's x64 developer environment, and Windows SDK
10.0.26100.0. Flags: `/std:c++17 /O2 /EHsc /bigobj`, with
`HDIM=8`, `NCOPY=9`, `VPORTS=111`, `RHELP=439`; the bridged variants additionally
use `KPAIRS=4` and `KPAIRS=5`. The repository's pinned portable `bits/stdc++.h`
and JSON header are included unchanged.

Boost **1.87.0** headers came from the official archive
`https://archives.boost.io/release/1.87.0/source/boost_1_87_0.tar.gz`, SHA-256
`f55c340aa49763b1925ccf02b2e83f35fdcf634c9d5164a2acb87540173c741d`, checked
against the archive's published JSON receipt before extraction. This is a
build dependency only; no Boost code is copied into this contribution.

From that developer environment:

```sh
python -B research/r439-block4-schedule/native.py \
  --work build/r439-block4-native-final --cxx cl.exe \
  --boost-include "C:/Users/Gautam Gupta/AppData/Local/Temp/integer-mult-boost-headers/boost_1_87_0"
```

The work directory was fresh. Both the initial certificate-generating native
run and this fresh default comparison run passed:

```text
PASS_R439_BLOCK4_NATIVE before+after columns=883/1327/1549 bridge_controls=6/18/24 payload_bits=93
```

The native emitter and independent emitter agree byte for byte on both full
record streams. Both words pass chronological legality, source ownership and
copy lifecycle, plus all physical F2 columns at five, nine and eleven stages.
All 6/18/24 omitted-bridge controls are rejected **per word**. Native scalar
counts, paid histograms and exact payload bounds agree with the Python replay.
`NATIVE-CERTIFICATE.json` retains the complete receipts except elapsed seconds
and the local stream pathname; no proof-relevant field is removed.

An initial attempt used an incomplete Visual Studio 18 Community installation
(missing `vcvarsall.bat` and C++ standard headers). The successful runs use the
already installed Build Tools 2022 environment; no system installation was
repaired or changed.

## Repository and review boundaries

`make verify` was attempted and could not start: GNU Make is not installed in
this Windows environment (`make : The term 'make' is not recognized`). No
repository-wide suite pass is claimed. No full selected-frontier cold replay,
new global hosted owner program, global invoice, new outer assembly, Lean
theorem or remote CI result is claimed. The existing supplier packages and
selected frontier were not modified or globally regenerated.

Main advanced during the experiment to
`f567884aeb8851b6e794af1184119a3bfbe1e631` (#799 with #589). The new selected
record, current status and maintainer review were read. All nine pinned input
files match that main commit exactly. The original experimental base is kept.

The final overlap review covered open PR metadata through **#842**, searches
for R439 and "block 4" in titles/bodies, the earlier review ledger, and the
related PRs discussed in the README. No competing block-4 change was found.
There was still no pinned coordination issue. The local claim records the
result and source link. Related work is credited without claiming composition
or whole-PR approval.

Only `research/r439-block4-schedule/` is added. Staged whitespace and source
preservation checks passed before the contribution commit. The result
remains subject to independent review; all inherited realization, hosting,
precision/tape, signed decoder and analytic assumptions remain explicit.
