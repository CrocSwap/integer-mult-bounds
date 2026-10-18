# Validation

The first bounded pilot matched all ordered solutions and measured a3.58x
enumeration gain and2.20x section-D gain. The final implementation also
precomputes reverse neighborhoods and does not assume matrix symmetry.
The initial package-control fixture mistakenly chose an inadmissible first
frame; it failed explicitly before receipt recording. The control now selects
the first admissible reference frame and checks that it has eight solutions.
The first saved-receipt comparison exposed integer versus string JSON-key
sorting in the chain dictionary. Canonicalization now converts keys to JSON
strings before sorting; the existing receipt is replayed without regeneration.

Final isolated optimized recording and benchmark passed:

```text
python -I -O -B research/frame-pair-enumeration-fast-seed93/verify.py --record --benchmark
PASS_FRAME_PAIR_FAST_S93 frames=1260 decoders=7168 term_ranks=57344 chain=25 inherited_controls=6 package_controls=10
```

The three kernel trials alternate execution order, compare complete ordered
stream digests each time, and use identical frame inputs. BENCHMARK.json
contains raw timings and environment details. D/E/H timing includes full
source checks and instrumentation, but excludes module loading and final
canonical serialization; the kernel timing excludes frame generation and
hash computation. These scopes are explicit, not whole-command timings.

No native toolchain, hosted CI or full repository suite was run. The package
does not edit a generator, selected construction or predecessor source, so
its scoped exact replay is the relevant check. Publication and acceptance
remain separate from these local results.

After the key-normalization correction, default isolated optimized replay
passed against the existing certificate without regeneration. The repository's
`python -I -B scripts/verify_selected_result.py` passed with exact unchanged
kappa1661960547713947/1000000000000000000. A separate agent compared the mask
algorithm and all D/E/H coverage to the pinned reference and found no additional
ordering, mathematical or benchmark issue. This is agent review, not human
peer review.
