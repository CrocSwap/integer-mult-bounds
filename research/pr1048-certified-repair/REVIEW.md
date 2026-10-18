# Separate Astra review and bounded rerun

The final bounded package passes the separate implementation and a fresh
end-to-end rerun. There is no remaining blocker to its stated pricing and
finite-domain claims. This review does not approve PR1048's original search
exhaustion, a new supplier, or a new multiplication bound.

Reviewer: a separate GPT-6 Astra agent at xhigh, requested by Brian Ross,
2026-10-13. The primary implementation, coverage implementation and this
review are substantially AI assisted. This is separate-agent review and a
code-disjoint checker, not independent human peer review or a formal proof.
The reviewer consulted CONTRIBUTING, the central PR ledger, current status,
the frozen predecessor sources, and the primary pricing/coverage code.

The checkout is `research/pr1048-certified-bounded-repair`, based on
`ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`. The reviewed SHA256 values of
`pricing.py`, `coverage.py`, `independent.py`, and `run.py` are recorded in
[the reviewer rerun receipt](evidence/INDEPENDENT-RERUN.json). That receipt
also binds the interpreter, exact commands, elapsed times and stdout.
No push, publication, paid computation or selected-frontier rebuild occurred.

## Findings and fixes

1. The initial driver would have checked the retained pricing JSON while
   regenerating a different output directory. The reviewer identified this
   stale-receipt risk. `independent.py` now accepts `--pricing` and
   `--coverage`, and the driver supplies the freshly generated files. Coverage
   writes its complete receipt with `--output`; its compact stdout is parsed
   separately rather than mistaken for the complete certificate.
2. The integration run exposed an isolated-mode import failure:
   `from pricing import ReferencePricer` could not find a sibling under
   `python -I`. The main agent replaced it with an explicit file-based module
   load. The reviewer confirmed that the final isolated-mode wrapper succeeds.
   This changed loading, not mathematical semantics.
3. The reviewer found that the initial retained COPY snapshot used the last
   A frame or the start frame, omitting a possible D-only predecessor. The
   coverage agent changed the snapshot to apply D before A. Every retained
   register in the frozen PR589 word has an A touch, so this fix does not
   change the reported real-word domain or counts. It corrects the stated
   more general local replay contract.
4. The review kept literal-domain differences separate from differences in
   reachable profiles. The final receipt explicitly checks the latter.
   Cross-section omissions are omissions of ordered paths from the old loop;
   they do not prove that the final word cannot be reached another way.
   The retained cross-section examples are exact profile ties.

No unresolved arithmetic or enumeration discrepancy remains within the
declared bounded domain after those fixes.

## What was independently reconstructed

For the fixed pipeline, direct subtraction gives

```
F_candidate(a) - F_reference(a) = 288 * 64^a * J_delta(a)
J_delta(a) = sum_r delta[r] * r^(1-a) + lambda * sum_r delta[r]
lambda = 32 * 64^2 / 10^16
```

All supported residual terms are nondecreasing, and the positive surcharge
makes the residual strictly increasing and unbounded. Together with the
exact check `F(0)<0`, this proves one positive root. At the reference root,
negative J means a strictly larger candidate root; nonnegative J means a
no-larger root. This argument does not order arbitrary profiles at an
arbitrary fixed exponent.

The checker imports only Python's standard library. It does not import
`pricing.py`, `coverage.py`, the original `bitprof.py`, or PR1182's repair for
acceptance. Its logarithm uses a positive atanh series after reduction to
[1,2], with an explicit rational geometric tail. Its exponential uses a
degree-72 positive Taylor polynomial and an explicit geometric tail. Every
rounding step is exact floor/ceiling integer division at scale 10^90.
The implementation documents the bounds and enforces the argument domains.
There are no float or transcendental-library acceptance decisions.

It directly encloses F at both actual PR589 endpoints:

```
L = 1733427039589844234749 / 10^24
U = 1733427039589844234750 / 10^24
-3/10^18 < F(L) < -2/10^18
 3/10^18 < F(U) <  4/10^18
```

The exact larger rational enclosures are retained in
[INDEPENDENT.json](evidence/INDEPENDENT.json). It also checks the fixed
`n=288p+idle` inventory, the surcharge, candidate positive-root conditions,
PR555 versus PR589, abstract signed improvement/worsening controls, and the
exact zero-profile-delta tie. A broad mixed-sign comparison stays unresolved.

For coverage, the separate checker reconstructs ranks by integer row
elimination with gcd reduction, span closure by exact rank tests, profiles by
an event replay, and literal move domains by prefix/suffix frame arrays.
It checks stable operation identities, current positions, frame masks,
commutation barriers, nesting and resulting retained COPY snapshots. It
reconstructs every first and second candidate-set digest and the complete
profile-delta occurrence histogram, then independently prices all 24 deltas.
It fully replays the 14 ordinary/cross-section named two-move witnesses and
the additional reachable-set difference witness.

Both implementations cache profile values for a fixed state, frame and the
two registers' touch positions. This is valid because those data fix their
frame itineraries; all other register contributions and the full-frame
cleanup support are unchanged. The candidate slots are still counted
separately. Neither implementation identifies continuation states merely
because their paid profiles agree.

| Independently checked quantity | Result |
| --- | ---: |
| First literal moves over the five named operations | 9,950 |
| Explicit selected first states | 10 |
| All adjacent second-operation identities, both sections | 150 |
| Second literal moves | 125,698 |
| Cross-section second moves | 9,424 |
| Unique signed local deltas | 24 |
| Strictly better occurrences | 0 |
| Exact identical-profile ties | 56,685 |
| Strictly worse occurrences | 78,963 |
| Unresolved occurrences | 0 |

The separate reconstruction verifies four pairs of equal-profile first
states with different literal continuation domains. Exactly one pair has
different reachable final-profile sets: B[1] at original frame 217 in slot 0
admits delta `{1:4, 2:-2}`, whereas its neutral placement in slot 367 does not
within the declared second domain. The supplied second move is B[368] to
slot 92, at closure mask `408817318573603981982687085723648`.
The checker fully replays it. Its J is strictly positive, so this extra
profile is strictly worse, not an improving omission.

## Semantic rejection controls

The separate checker rejects seven pricing/source corruptions: shifting the
reference bracket to the wrong tick (rejected by actual endpoint signs),
omitting the surcharge parameter, omitting it only in a numerical signed
sum, failing to reverse negative-coefficient interval bounds, promoting an
unresolved sign, removing a mandatory source, and corrupting a source pin.
The mandatory 36-file manifest is itself canonically pinned; all file bytes
are rehashed, including 24 original Git blob identities.

Two additional controls use the already reconstructed coverage semantics:

- Remove a cross-section second-operation row and refresh occurrence counts,
  continuation digests, price totals and related numerical summaries. This
  still fails the independently reconstructed mandatory second domain.
- Change an advertised local delta and recompute its rigorous rational price
  and aggregate counters. This still fails the reconstructed semantic
  profile histogram.

Thus refreshed hashes and internally consistent summaries cannot replace
the missing semantics. The controls do not merely check that a stored hash
changed. Their actual rejection reasons are recorded in INDEPENDENT.json.

Methodological credit: Brian Ross's
[Krenn independent verifier](https://github.com/brianross93/Krenn/blob/ab446724a61a293a3268c63b9e9e721c6a360561/experiments/krenn_quantum_graph/independent_verifier.py)
and [semantic corruption tests](https://github.com/brianross93/Krenn/blob/ab446724a61a293a3268c63b9e9e721c6a360561/tests/test_krenn_artifacts.py),
and [ThetaTwist exact arithmetic](https://github.com/brianross93/thetatwist/blob/b4ec6c13088b89961834cc675b44b81372199b02/src/thetatwist/core.py).
These are methodological adaptations with no copied code. Supplier,
original-search, counterexample and bracket-repair credit is retained in
[NOTICE.md](NOTICE.md).

## Fresh rerun evidence

The first standalone arithmetic pilot completed in 0.58 seconds. A timed
complete independent reconstruction completed in 2.016 seconds. The final
reviewer wrapper run was bounded by a 60-second subprocess timeout and
completed in **41.507 seconds**, with empty stderr and exit code 0, under
Python 3.13.2 on the development Mac. No resource escalation was needed.

The exact command, including its generated temporary output directory, is in
INDEPENDENT-RERUN.json. From the repository root it was:

```sh
python3 -I -O -B research/pr1048-certified-repair/run.py --out /var/folders/0x/h7yfchhj50j3jlykl2m_rx0c0000gn/T/pr1048-independent-review-wvac5jlm/receipt
```

Actual stdout:

```text
pricing.py: PASS_CERTIFIED_REFERENCE_PRICING
coverage.py: BOUNDED_COVERAGE_RECONSTRUCTED
independent.py: PASS_SEPARATE_RATIONAL_PRICING_CHECK
PASS_LOCAL_BOUNDED_REPAIR
```

The wrapper's three child commands all returned 0: pricing 8.868 seconds,
coverage 30.603 seconds, independent reconstruction 1.986 seconds. Fresh
PRICING.json and INDEPENDENT.json equal the retained JSON objects exactly;
COVERAGE.json equals the retained object after omitting only its timing
field. These are finite-verifier timings, not multiplication-runtime claims.

## Remaining boundaries

The ten selected first states are an explicit bounded input domain. This
checker verifies their legality and all declared adjacent continuations; it
does not independently reimplement the original heuristic's nomination
labels or its first-state selection recipe. Those labels and the synthetic
legacy COPY-rule failures are observational comparisons rerun through the
retained legacy adapter. It does independently check the real literal domains,
profiles, reachable-set differences, endpoint signs and signed prices.

There is no complete first-state search, proof of safe heuristic pruning,
disjoint-move reduction, all-frame/subspace enumeration, Steinberg search,
645,900-pair exclusion, full scalar/native supplier admission, or all-size
multiplication theorem here. Counts are ordered paths, not distinct final
words. The retained supplier realization, compiler, hosting, precision and
analytic obligations remain outside this review. No claim requires closing
PR1048 or changing the selected result.
