# Completed verification and limits

On 2026-10-13, macOS arm64, CPython3.9.6, standard library only:

```sh
python3 -I -O -B research/five-subset-common-frame-seed48b/test_package.py
python3 -B scripts/verify_selected_result.py
```

Expected final lines:

```text
PASS_COMMON_FRAME_WEIGHT5_PACKAGE frames=5334 area=36 adds=24 controls=PASS no_new_kappa
PASS selected record, exact kappa, original source inventory and proof supplement: 836330098538459/500000000000000000
```

Primary and independent enumerations passed in normal and optimized modes.
They independently enumerate all 5334 anchored lifts and agree on all 2048
legal-frame maxima, histogram counts and digest
`ac3520884ea295130595b20b4703217ed6838ba49dae1e4ca63412371803be7a`.
The primary replay took about1.4s and the independent about2.0s on this host;
these timings describe verification, not a supplier performance comparison.
All twelve residual bases, all thirteen integer endpoint columns, and the
literal inverse passed. The witness verifier checks twelve semantic negative
controls, including omitted dirty cancellation that clean input columns miss.

The package test replays all three commands under isolation and optimization,
checks exact cross-implementation receipts, relocates the package to a spaced
path, and rejects ten actual on-disk faults: an omitted outgoing basis,
boolean sign, wrong word, missing source pin, duplicate JSON key,
incomplete primary coverage, corrupted independent receipt, missing independent
receipt without auto-creation, changed repository source and changed verifier
source. The in-memory controls separately omit both incoming and outgoing bases. No saved evidence is rewritten
by default verification. The original package hashes are unchanged after its
corruption tests. Missing evidence is a failure.

Investigation base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.
The final upstream refresh found
`49b3157d1d89adcef16df8be98445451672be5ba`; its updated AGENTS/CONTRIBUTING/
autoresearch/package guidance was read. All six pinned scientific/context
inputs remain byte-identical, including the selected record and review. The
new package includes the requested open next question. The optional package
generator/replay registration is not used; the explicit standalone replay
and source guards are retained. upstream/ and every existing repository file
are unchanged.

Overlap was checked using relevant open PR bodies and exact predecessor heads,
the ledger, prior parity-side/frame negative results, and the live Discussion
board. The final latest-30 open-PR refresh reached PR1227; PR1226's masked
root-star census and PR1224's nine-term E8 normal form are different objects.
PR1173 proves pairwise existence and PR1139 triple classification; this package
adds simultaneous common-station capacity, not a repeated pair census. All
other scopes are checked only to the extent described here; no novelty theorem
is claimed. The newly introduced find_overlap.py was additionally run offline
against local notes: twelve possible matches, no usable remote cache. Live
connector/browser checks supplied the remote coverage, not that offline run.
The Discussion board still had no matching common-frame claim. No pinned sprint
coordination issue exists, so the claim/result is retained locally.

Not run: repository-wide regeneration, full selected-construction cold replay,
native/physical admission, Linux replay, formalization or independent human
review. This exact finite census plus explicit reduction argument is not a
formal proof of the full multiplication theorem. All supplier hosting,
precision/tape and analytic-transfer conditions remain unresolved here.
