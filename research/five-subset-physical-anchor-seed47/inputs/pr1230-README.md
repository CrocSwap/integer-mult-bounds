# Sharp multiway capacity of one weight-five common frame

**Structural research note; no new kappa or physical supplier.** One common
legal frame at h=9 supports at most **36** entries of a signed rank-one
weight-five block when both endpoint families contain a degenerate pair.
An explicit **6×6** block attains this bound. Its complete dirty-helper
scalar wrapper takes **24 signed ADDs**, saving twelve versus 36 direct
entries, with all twelve orthonormal residual bases exhibited.

This extends [PR1173](https://github.com/CrocSwap/integer-mult-bounds/pull/1173)
from independently completable pairs to simultaneous multiway sharing at
one station. It changes the common-frame obligation, not just the seed or
size of a previous label census. The sharp nine-coordinate threshold and
PR920's dimension/residual facts remain predecessor results.

From the repository root, Python3.9+, standard library only:

```sh
python3 -I -O -B research/five-subset-common-frame-seed48b/test_package.py
```

Expected final marker:
`PASS_COMMON_FRAME_WEIGHT5_PACKAGE frames=5334 area=36 adds=24 controls=PASS no_new_kappa`.
See PROOF.md for the complete finite-domain argument, WITNESS.json for the
literal scalar word and twelve residual bases, CENSUS.json and INDEPENDENT.json
for exact independent exhaustive receipts, and VALIDATION.md for completed
checks and limitations. Individual replay commands are census.py,
independent.py and verify.py under the same Python flags. None rewrites saved
evidence; their explicit generation options are documented in their usage.

Both enumerations cover **5334** U4 lifts, of which **2048** are nondegenerate,
and agree on every legal frame's maximum. Dimension-five separators follow
by transposition. The primary additionally checks 18160 anchored source
subsets and 20200 qualifying saturated target classes. These counts include
anchored duplicates across source-pair choices; no global labeled census
or unique-frame count is inferred from them.

The macro's conditional incident rank bill is **12 rank-three + 12 rank-four
edges, mass84**. The helper, sources and outputs are explicit dirty roles;
cleanup and old-helper cancellation are included. Those edge ranks exclude
unimplemented global caller/boundary, exact phase, half-factor, copy/lifecycle,
hosting, precision and analytic obligations. A full recursive invoice is
not supplied. The selected frontier and upstream/ are unchanged.

Exact base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.
Fresh OS assignment seed **48** (a repeated numeric draw from a new OS call),
structural track. CLAIM.json records three candidate tasks, the new common-frame
scope, bounded stopping rule and overlap review. Source pins and retained
predecessor documents are in SOURCES.json. PR1173 is pinned at
`72bfdf66d9823244ee8dab4c8898af834e34853b`; no predecessor code is imported.

Credit Douglas Colkitt's signed parity kernel and historical obstruction;
ArnavSwiggy's PR920 residual criterion/floor; @woklerx's PR1139 triple
classification; ToikY's PR1173 and seed47 frame-completion note; icekylinx's
general Clifford-frame rank construction and the retained format lineage.
Prepared for **@ToikY** with substantial **OpenAI Codex** assistance, including
two bounded workers for primary/independent census and review. The separately
implemented checks are AI-assisted evidence, not independent human review.
Apache-2.0; original retained notices are preserved. See NOTICE.md.

## Open next questions

Can this 6×6 common-frame block be embedded in a real parity-side circuit with
all caller, phase, helper boundary and recursive costs paid? This determines
whether the local twelve-ADD saving survives physical realization. A feasible
first step is to compile just the explicit thirteen-register word into the
historical frame format and replay all phases against its exact integer
endpoint, including the side-matrix factor 1/2. The current blocker is the lack
of a compatible caller/source-access and helper lifecycle construction; the
incident mass84 is not an admission certificate. Stop that route if the
complete favorable invoice loses the local saving. This question does not
reopen the unchanged rejected global ParitySide DAG.
