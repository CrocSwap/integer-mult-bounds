# Validation of the helper315 conditional improvement

On 2026-11-14, Python 3.12.16 (Clang 23.1.3), macOS 26.5 arm64, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/p104-role315-direct-lift
```

**PASS_REGISTERED_RESEARCH_PACKAGE**, outcome completed, exit 0. All six registered commands passed. The fresh native stage took 124.74 seconds and the signed stage 142.32 seconds; including independent rational and physical checks, the whole run took about five minutes. Both stages generated fresh receipts and compared their deterministic content against the committed expectations. Earlier bootstrap stages separately passed in 126.23 and 141.34 seconds. [data/REGISTERED.json](data/REGISTERED.json) records the final run and source-manifest digest. Execution times are environment measurements, not mathematical certificates.

The independently authored rational checker and the local physical checker also passed under optimized Python (`-O`). Their explicit checks are not disabled assertions. The complete inherited application and the directed ceiling proof require assertions enabled; the registered commands provide that environment and isolate bytecode caches.

Evidence:

| Obligation | Result |
| --- | --- |
| Exact retained sources | 100 files match the original Git commits; extracted #7603 word/receipt match its unchanged archive |
| Literal change | Only helper315's two rank-one MOVEs become one rank-two MOVE; 78 intervening events have no read/write of315 |
| Independently authored rational check | All 1,569 endpoint rows and 74 erased rows match across #7546, #7601, #7603 and candidate; helper315 identity/target preserved |
| Physical change | All 512 forward/adjoint columns, rank-two support and absolute phase; 35 affected lineage chart pairs additionally replayed |
| Complete signed application | 3,039 maps, 104 main-boundary pairs, 17 native calls; all 54 strict + 4 functional outer predicates |
| Complete invoice | Paid 110,383; targets 22,461; surplus 1,424; versus #7603, ΔP₁=−34 and ΔP₂=+17 |
| Ordinary / precision / tape | Ordinary 782,716,348 < 10⁹; c=2430; 298,536 monomial slots; 25,454,373,504 elementary-record upper bound; 43,923,200 scalar-service upper bound |
| Conservative public claim | κ=0.0036502223357, probe 0.00365022233577; minimum outer margin 10⁻¹⁵; public tape inequalities pass |
| Stronger framework claim | κ=0.003650222335827; complete application passes, minimum outer margin 10⁻¹⁸ |
| Scoped ceiling | Exact negative derivative over [0,0.00376669], unique root within (0.0036502223358272,0.0036502223358273); the fixed-scalar no-contact family is exhausted |
| Rejecting controls | Wrong direct chart/source, missing paid MOVE, inherited coefficient errors, hidden owned erasure, dropped quadratic/global phase, restored old invoice, insufficient BIT bound |

The package metadata/pins check passed. Canonical main was fetched again before submission and remained `e54523517d0f03e58352e647c403a5af3e525a57`; relevant guidance and the selected record were unchanged. The fresh overlap snapshot at 14:06:59–14:08:18 UTC covered 903 open PR titles/bodies and bounded discussion tails; #7603 remained the strongest comparable open candidate and its head was unchanged. See [data/overlap.json](data/overlap.json) for coverage limits.

Publication byte comparison and replay-selection commands:

```sh
python3.12 -B scripts/check_research_commit.py --package research/p104-role315-direct-lift
python3.12 -B scripts/research_package.py --changed-since origin/main
```

Mathematical replay uses only committed package-local sources. The optional Git source-history audit is not claimed: the working clone is shallow. Unmerged predecessor commits are attribution in SOURCE-VERSIONS.json, not runtime Git pins; the required bytes are retained and authenticated. Generic SOURCES.json provenance resolves only against the main base commit. No external predecessor fetch is needed by the replay.

## Existing shared CI failure

The unchanged base reproduces one failure among the six tests in `test_research_current_status.py`: `CurrentCiNavigationTests.test_current_ci_section_matches_selected_record`. `docs/ci.md` still names #6030 / `make frontier6030-verify`, while the selected record requires #7000 / `make frontier7000-verify`. This package changes neither file. [PR7276](https://github.com/CrocSwap/integer-mult-bounds/pull/7276) already addresses that shared navigation issue; this research contribution does not duplicate it. The targeted run had 5 passes and 1 failure, not a green shared suite. Hosted Actions may stop in planning before the registered research replay; see the PR's actual checks for its hosted outcome.

All checks here are finite, source-bound author checks with separately scoped agent review. The five inherited framework assumptions remain. No independent human acceptance, formal-kernel theorem, complete materialized multiplier, full historical test suite or selected-frontier promotion is claimed.
