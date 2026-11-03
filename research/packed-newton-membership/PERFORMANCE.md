# Local timing evidence

This contribution was produced by Nick Petalas. Apache-2.0.

The complete public membership call takes 45.35% less median time on one
accepted rank-nine fixture. This includes type and size validation, packing,
the full transform, unpacking and every divisibility check. It includes the
new 8192-bit component-limit check. It does not time only packed subtraction.

The fixture is the positive encoding used by PR5374's existing benchmark at
coefficient width 1025 bits. Encoded input components reach 1034 bits. The
exact input SHA256 is
`151857dd471120344f0f7c0e8c5ab6542b8f7d815e5cbb56348eacd77f3c770b`.
The same arrays and positive endpoint are used on both sides. No result is
cached. Input encoding is outside the API timer on both sides.

Five fresh processes per side ran 1000 calls each, alternating order between
trials. All 10,000 complete calls accepted, with zero errors. Separate
processes ran the complete inherited scientific replay five times per side;
all ten returned the same complete result hash and zero errors.

| Timed work | Reference median, range in seconds | Packed median, range in seconds |
| --- | --- | --- |
| 1000 complete rank-nine API calls | 0.290105, 0.271077 to 0.366769 | 0.158548, 0.147782 to 0.162996 |
| Complete source scientific replay call | 0.907932, 0.901498 to 1.010443 | 0.859743, 0.850917 to 0.915044 |
| Whole fresh process for that replay | 0.948728, 0.938971 to 1.104224 | 0.899336, 0.890138 to 0.956943 |

The API ranges do not overlap. Complete-replay timing is inconclusive:
its observed median falls by 5.31%, but the ranges overlap and the gap is
smaller than the observed variation. No end-to-end replay speedup is claimed.
Whole-process timing includes process startup, plan initialization, source
authentication, imports, output comparison and printing. None of these
measurements predicts a collector, tape implementation or supplier speedup.
The change is opt-in; the shared default command is unchanged.

Environment: CPython 3.12.15, macOS 27.0.1, arm64, standard library only.
The shared host has 18 logical CPUs; the pre-measurement load averages were
2.99, 2.77 and 2.08. Other work was not stopped. Alternation and the reported
ranges expose the observed scheduling variation. Both implementations use
their ordinary interpreter configuration with no tuning knobs changed.

## Limiter and end-to-end share

An untimed cProfile run of the new API spent 0.2905 of
0.3898 profiled seconds cumulatively in validation and
packing, while the packed transform itself spent 0.0109 seconds.
Packing and validation now dominate. The old API's nested validation
generators and scalar transform account for most of its profile. The
improvement includes fusing validated input reduction into packing as well
as batching the arithmetic.

A separate untimed full-replay profile spent 0.5868 of 3.1432
profiled seconds cumulatively in the bounded membership predicate, about
18.7%. The unchanged Gaussian source validation alone spent
1.8896 seconds cumulatively. Profile durations are diagnostic and are
excluded from the timing table. The unchanged work limits the end-to-end gain.
The complete replay preserves its independent decoder,
subset checks, rejection tests and all 96 literal collector prefixes.

## Repeat

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/packed-newton-membership/benchmark.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/packed-newton-membership/benchmark.py --sample reference --profile
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/packed-newton-membership/benchmark.py --sample packed --profile
```

The benchmark prints every unrounded sample, per-sample error and work counts,
fixture/result hashes, environment, and hashes of its four controlling files.
It writes no files. Timing is not a registered correctness acceptance gate.
The ordinary registered replay reruns the exact preservation checks.
