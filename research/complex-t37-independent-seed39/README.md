# Independent U8/T37 construction with paid payload1024

Independently developed from PR890 and PR870, this package supplies a literal T37 whole-owner schedule with the claimed
conditional exponent saving **κ = 0.001661960547713947**. Its full replay must
finish with `PASS_STRICT_U8_T37_PR589_COMPOSITION` before the claim is admitted.
The exact gain over PR890's constructed T21 candidate is **0.000000002773066918**.
This is a small improvement, about **0.000167%**, not a substantial advance
toward κ > 0.01. It does not change the repository's selected result.

The construction changes the previously fixed complex prefix allowance from
512 to 1024 and pays the larger row charge. It combines the pinned T21 and
T16 schedules, changes ten owner records, and leaves remainder profile
`{48:11086,1:6}`. There are 333 complete U8 invocations and 167832 whole helper
roles. See [PROOF.md](PROOF.md) for the exact exchange, normalized-moment
comparison, complete finite charge, inherited assumptions and search scope.

## Reproduce

From the repository root, with Python 3.12, NumPy, SciPy, SymPy, a C++17
compiler and Boost headers installed:

```sh
python3.12 -B research/complex-t37-independent-seed39/verify.py --work /tmp/t37-cold
```

Use a fresh output directory outside the checkout. Set `BOOST_INCLUDE` if
Boost headers are outside `/usr/include`. The unchanged bit589 ancestor
compares regenerated gzip containers byte-for-byte; Python 3.12.14 was used
here because the host Python 3.14 produced different compressed bytes for
identical decompressed content. This package's new owner and plan checks use
canonical content identities, with positive recompression controls.

The default command rebuilds the complete PR589/PR741/PR799 ancestry, then
the U8 word, every scalar column, frames, wrappers, phase edges, physical
owners, emitted controller, invoice, two exact moment engines and all 47
outer inequalities. Reuse is available only for a complete, source-bound
PR799 replay **and** its complete PR741 ancestry:

```sh
python3.12 -B research/complex-t37-independent-seed39/verify.py --work /tmp/t37-strict \
  --baseline799 /tmp/frontier799 --ancestor741 /tmp/frontier799/ancestor
python3.12 -B research/complex-t37-independent-seed39/package_controls.py \
  --replay /tmp/t37-strict --baseline799 /tmp/frontier799 \
  --ancestor741 /tmp/frontier799/ancestor --out /tmp/t37-package-controls.json
```

The fixed inherited stage inventory and source/artifact/log bindings are
rechecked. No optimizer or discovery switch is exposed by the replay.
Expected final values: complex prefix779 < charged1024; physical row17495
< limit20161; rank mass2408256; deficit11840; κ as above. `RESULT.json` binds
the actual artifacts and completed stages. Receipts do not authenticate
execution history and finite tests are not a formal proof of the full theorem.

## Review boundaries

- `build_owners.py` reconstructs pinned predecessor owners and applies the
  ten explicit edits. `independent_check.py` expands actual source events,
  checks every owner and orthogonal chart, and recounts the profile.
- `build_parent.py` constructs the five-bank-group overcharge envelope;
  `check_parent.py` independently checks its exact routes and complements.
- `source_adapters.py` exposes every replication and payload substitution
  through counted literal edits, keeping the vendored source unchanged.
- Controls include all 30 inherited/new omitted owner edits, both omitted
  interleaving delays, underpaid payload512, malformed orders, partial-bank
  mutations, all inherited admission/bit/controller controls, and five
  targeted payload mutations that must reach their precise assertions.
- `price.py` uses both unchanged exact moment engines, the unchanged bit
  bootstrap, all 47 outer constraints and an exact majorization comparison.

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. Source pins, licenses,
predecessor credits and substantial OpenAI Codex assistance are recorded in
[NOTICE.md](NOTICE.md), `VENDOR-PINS.json`, `DEPENDENCY-PINS.json` and the
package manifest. `SPRINT-CLAIM.json` records seed39 and the local claim;
no pinned sprint coordination issue was available.

Concurrent credit: Jonathan Capalbo’s PR942 at `1960cfa919a0945d0ca4cb14ea96237000037903`, published during this work’s verification, reaches the same κ with eight owner edits and an all-T bound. This package uses a different ten-edit schedule and adds an independent full reconstruction with 47 package controls and five assertion-targeted payload controls. No unique record or priority claim is made.
