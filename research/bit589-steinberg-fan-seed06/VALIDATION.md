# Validation and handoff

Executed on 2026-10-14 in Linux with CPython **3.12.14**, standard library only.
The exact starting commit is
`92da4d718f1d4cf8de4e6ee947ddc7b180ce1c31`.
All new files are confined to this package; no supplier, selected certificate,
upstream source or existing verifier is changed.

## Completed checks

The single recommended reproduction command, from the repository root, is:

```sh
python3 -I -B research/bit589-steinberg-fan-seed06/verify.py
```

**PASS.** The complete certificate is recomputed and compared by canonical
decoded JSON, then independently checked. Expected output:

```text
PASS_INDEPENDENT_INTEGER_KERNEL_MAJORIZATION pairs=316 orders=948 rank_schedules=1671
PASS_BIT589_STEINBERG_FAN pairs=316 orders=948 rank_schedules=1671 improving=0 controls=8 no_new_kappa
```

Coverage is 316 adjacent windows, 948 corrective orders and all 1,671 feasible
rational rank triples: 982 identical profiles, 689 strictly worse profiles,
zero improvements, 19 distinct deltas. All 1,898 forward/inverse scalar
replays pass on 661 source, target and dirty-helper columns, with explicit
COPY/ERASE and rebuilt literal cleanup. The ADD count is 24,305 before and
24,307 after each expansion. The local histogram, COPY ranks and retained
nine-stage remainder match the pinned PR589 receipt exactly.
The source cleanup's grouped reversal and full frames are checked explicitly;
reversing the commuting sources inside a compressed gate is immaterial.

```sh
python3 -I -O -B research/bit589-steinberg-fan-seed06/test_package.py
```

**PASS: 18 tests.** These include changed source bytes, a removed window,
duplicated corrective order, false intersection rank, missing rank triple,
same-mass false histogram, forged concavity slack, false coverage total,
duplicate JSON keys, invalid histogram counts, a missing scatter read and
omitted cleanup. The eight mathematical controls reject dropped gates,
incorrect order, wrong equal-rank containment, an unpaid climb and a false
universal obstruction. Both chain orientations are checked on all eight
Boolean inputs. A genuine improving boundary fixture is detected, and an
intersection of positive rank with no common listed root is computed exactly.
Recompression with a different gzip timestamp is accepted.

During test development, one slack-mutation test initially failed because it
assigned the value already present. It was corrected to increment that value;
every certificate-mutation test now first verifies that its input changed.
The final 18-test run has no failures. This was a test-fixture failure, not a
counterexample to the scoped inequality.

```sh
python3 scripts/research_package.py --package research/bit589-steinberg-fan-seed06
```

**PASS_REGISTERED_RESEARCH_PACKAGE**, outcome `negative-result`. This runs the
normal complete replay and the optimized 18-test suite through `VERIFY.json`.

**PASS, isolated source export:** copied only this package and its four declared
input files to a fresh directory outside the checkout, then ran its absolute
`verify.py` path using `python3 -I -O -B` from `/tmp`. No Git metadata, checkout
imports or third-party modules were available there. The final source version
passed both checkers in about 18 seconds; this is an observed runtime, not a
performance claim.

The orientation command `python3 -B scripts/research_baseline.py` also returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. This is explicitly a source-binding
check, not a full replay of the selected assembly.

## Current-state and overlap refresh

The selected record was followed to
`research/community-frontier1094-audit/SELECTED-SOURCE.json`,
`research/community-frontier1094-audit/ASSEMBLY.json` and
`docs/research/community-batch1099-review.md`. Its accepted conditional value
is κ = **0.001672660197076918**; the complex supplier binds, and PR589 remains
the bit supplier. This package changes neither value nor admission status.

At 02:11 UTC, Git transport reported upstream main
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Its changes since the starting commit
are reconciliation/closure records. All four live input files and the selected
record remain unchanged. Read-only PR-head checks returned:

| PR | Observed head |
|---|---|
| 933 | `b9348c6907516e55dc07e135ad4d7a480d4f9840` |
| 1345 | `b54a856aa79857d91cd5d65f8f7144e26c8c084f` |
| 1382 | `cf17b06c00c50a22315f210c5f6b5197c860abdd` |
| 1413 | `6294a110530807dcbd8252440f191e2020b67a71` |
| 1048 | `07730cd8302c378607259a9ad0efb73e0b57a2f2` |
| 1520 | `69e353410ae1e6f0555b5add9720f3e691a762b9` |

The public open-PR searches for `Steinberg` and `bit frame`, and active
Discussions, were refreshed at the same time. These are partial public-page
checks, not a complete API queue snapshot. PR933's earlier inverse-expansion
neutrality remark is explicitly corroborated, with narrower fixed-contact
scope and a different rational flag/all-exponent proof. The comparison with
PR933 is in README.md. No novelty is inferred from an empty search.
PR1048's paid-profile/transport note and the newly posted PR1520 J3
precision tradeoff were then read at the pinned heads. Their different
scopes and attribution are recorded in README.md.

Posting access is unavailable under the assigned publication workflow. The
scope claim and its completed-result update are kept locally in `CLAIM.json`.
The intended publication branch is
[`research/seed06-bit589-steinberg-fan-20261014`](https://github.com/CubeJerry/integer-mult-bounds/tree/research/seed06-bit589-steinberg-fan-20261014).
Publication status and the verified remote commit are supplied in the handoff;
this note does not itself attest to a push.

## Not run and remaining scope

No native 5/9/11-stage supplier replay, hosted emission, full
`make frontier1094-verify`, remote CI, proof assistant, or other Python/OS
version was run. No improving candidate survived the favorable local budget,
so those construction-admission checks are not asserted.

The exact obstruction covers only one adjacent phase-A corrective expansion,
the pinned source-list order, fixed neighboring contacts and the retained
hosting remainder. It does not cover nonadjacent or multiple expansions,
global reframing, new helpers, COPY changes, new geometry or changed hosting.
The rational-frame model relaxes physical admission; the full multiplication
theorem's inherited compiler, mutable-source, precision/tape and analytic
assumptions remain unresolved here. **No new κ.**

Prepared for **@CubeJerry** with substantial **OpenAI Codex** assistance;
predecessor attribution and source pins are retained in README.md and SOURCES.json.
