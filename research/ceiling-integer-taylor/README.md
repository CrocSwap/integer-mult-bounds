# Exact integer Taylor arithmetic for the ceiling replay

The complete retained `complex-local-word-ceiling/levers.py` replay took
**3.914 seconds before and 0.635 seconds after** this opt-in arithmetic
replacement (medians of three alternating fresh-process pairs, CPython
3.12.7 on this Windows host). All seven exact ceiling brackets, the complete
stdout and all 1,238 ordered exponential input/output records agree. Timing
includes source authentication and tracing. Host contention was uncontrolled;
the measured 6.16x ratio is descriptive, not a portable performance guarantee
or a correctness gate.

Profiling the unchanged actual entry point placed 4.132 of its 4.261 seconds
inside `exp`, including 644,657 calls to `math.gcd`. The retained Taylor loop
constructs and reduces several Fractions at every step. The replacement
keeps a common integer denominator until the final dyadic rounding. It does
not cache successful checks, skip terms, change precision or alter a bound.
`PROFILE.json` and `TIMINGS.json` retain the measured evidence.

## Exact equivalence

The retained `ceiling.py` has fixed precision 256 and accepts
`0 <= lo <= hi <= 1/2`. Its lower endpoint sums a Taylor series at lo; its
upper endpoint sums at hi and adds the same retained remainder bound.
For either rational endpoint `y=p/q`, q positive, define

```text
P_0 = D_0 = S_0 = 1
P_k = p P_(k-1)
D_k = k q D_(k-1)
S_k = k q S_(k-1) + P_k.
```

Induction gives `P_k=p^k`, `D_k=q^k k!`, and
`S_k/D_k=sum_(j=0)^k y^j/j!`. The retained loop stops at the first k>=1 with
`t_k*y < 2^(-precision-8)`. Since all quantities are nonnegative and q>0,
this is exactly the integer comparison

```text
(P_k p) * 2^(precision+8) < D_k q.
```

The strict inequality is preserved, including equality at the threshold.
For y=0 both loops stop at k=1 and return one. For other admissible y,
`y^(k+1)/k!` tends to zero, so both loops terminate at the same k.

The lower endpoint is the same floor of `2^precision S_k/D_k`. The upper
endpoint is the same ceiling after adding `2 t_k y/(k+1)`, whose numerator
and denominator in this representation are

```text
numerator   = S_k q (k+1) + 2 P_k p
denominator = D_k q (k+1).
```

Thus the output rational interval is exactly unchanged for every rational
input in this domain and nonnegative integer precision, not merely close
enough to make the same acceptance decision. The analytic enclosure and
Taylor remainder argument remain the retained engine's work; this is an
implementation equivalence. No new numerical bound or kappa is claimed.

## Scope and use

`adapter.py` authenticates every declared live input by SHA-256 and Git blob
before importing source code. It loads a fresh engine, substitutes only its
`exp` callable in memory, and invokes the complete unchanged original entry
point. The original logarithm cache, halving guard, coverage-law checks,
binary search, controls and exact receipt check still run. The engine and
fixtures on disk, their pins and the selected record remain untouched.
The adapter restores temporary import-path, module and argument state after
the call. Use it as a separate replay process, not concurrently in threads.

```sh
python3.12 -I -O -B research/ceiling-integer-taylor/adapter.py --fixture levers
python3.12 -I -O -B research/ceiling-integer-taylor/adapter.py --fixture selected
python3.12 scripts/research_package.py --package research/ceiling-integer-taylor
```

`--mode baseline` runs the same wrapper with the retained Fraction loop.
The returned JSON includes complete ceiling-call arguments/brackets, stdout,
and a compact digest/count of every exponential call. During verification,
the entire ordered arrays of exact rational calls are also compared directly;
the digest is a compact receipt, not the sole equality predicate.

The two actual original fixtures exercise 2,602 exponential calls. The
selected verifier checks its full original receipt, previous-record binding,
guard/mass controls, worse-profile comparison and 25 seeded idle histograms.
An independent power/factorial oracle checks 1,792 endpoint-and-stopping
results, including zero, precision 0 through 512, 300-bit denominators, and
five exact stopping-threshold equalities. Domain errors, an omitted factorial
and downward upper rounding are distinguished. A Git-free optimized replay
and actual engine/fixture/receipt corruptions exercise the public paths.

Regenerate timing evidence separately, choosing a new output path:

```sh
python3.12 -I -O -B research/ceiling-integer-taylor/benchmark.py --rounds 3 --output NEW_TIMINGS.json
```

Every timed replay checks complete receipt equality; timing is never a pass
threshold. The benchmark is this complete planning tool, not the selected
cold multiplication replay, the whole CI suite or a theorem about runtime
at arbitrary dimension. No changed physical construction or compiler is
supplied. Wider production adoption would require dependency and source-pin
review; this package leaves the frozen engine unchanged.

## Provenance and credit

Started from refreshed canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. Fresh picker
seed `351ad04a28c291a2fdd8e8be5a9fbd82` selected verifier engineering and
the replay-runtime card. The prescribed source-binding baseline passed.
`TASK.json` retains the original card; `OVERLAP.json` records current PR
coverage and the stale Discussion-snapshot limitation.

Douglas Colkitt and the original Claude-assisted ceiling engine retain
credit for the intervals, logarithms, stopping rule, fixtures and planning
model. Sagar Thakrar / PR1012 and the selected construction's retained
lineage retain coverage-law and source credit. The source-pinning convention
and prior replay optimization packages are acknowledged; this is an integer
arithmetic loop replacement, not a new caching method. Prepared by ywz65 with
substantial OpenAI Codex assistance in derivation, implementation, measurement,
checking and writing. No independent human review is claimed. Apache-2.0.

## Open next questions

Does the same exact recurrence help other retained interval engines? First
compare their stopping and remainder rules, then measure one unchanged full
fixture. Matching function names or approximate bounds is insufficient.

Should this replacement be promoted into the production ceiling engine?
First inventory every live source-pin dependency and preserve its historical
evidence, then replay the affected consumers. The opt-in result does not
authorize changing frozen source manifests or establish those consumers.
