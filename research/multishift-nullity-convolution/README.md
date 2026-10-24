# Multi-shift nullity convolution

**Algorithmic improvement; no new kappa.** Evaluate the existing exact
joint-nullity distribution with O(n+t(m+1)^2) rational operations, where
m=n-sum(a_i), instead of binom(m+t,t) feasible dimension tuples. The
[proof](PROOF.md) covers every prime power and every set of distinct
scalar shifts. It does not assume independent ranks.

The implementation keeps O(m) live coefficients and O(n) factorial
values. These are arithmetic and storage counts, not bit-complexity
claims. At q=17, n=24, t=17 and a_i=0, it uses 5525 coefficient products;
the direct formula has 151584480450 terms. [RESULT.json](RESULT.json)
retains the exact 709-digit count.

## Evidence and replay

The [verifier](verify.py) compares 2821 cases with the direct formula,
checks 21805 literal matrices in 11 contexts (including F4), checks 481
nullity bins, checks three full distributions and their marginals, and
checks eleven failure controls. It also compares two-shift results with
the unchanged predecessor executable. The source hash and the saved
result must match. There are no assert-based acceptance checks.

From the repository root, use CPython 3.12 with no third-party packages:

```sh
python3.12 -I -W error -B research/multishift-nullity-convolution/verify.py
python3.12 -I -W error -O -B research/multishift-nullity-convolution/verify.py
python3.12 -B scripts/research_package.py --package research/multishift-nullity-convolution
python3.12 -I -B research/multishift-nullity-convolution/benchmark.py
```

Expected status: `PASS_MULTISHIFT_CONVOLUTION_NO_NEW_KAPPA`.
[BENCHMARK.json](BENCHMARK.json) records five alternating-order runs at
q=7,n=12,t=7. Both methods return the same exact count. The reference visits
only feasible simplex tuples. Time is not an acceptance test. The large
q=17 case was not compared with its 151 billion-term reference.

Normal and optimized CPython 3.12.13 passed. An official Git-free package
export and the source and receipt corruption controls are recorded in the
PR evidence. No Lean, Docker, native supplier admission, selected cold
replay or full multiplication theorem was checked. The algebraic proof
has author review; no independent human or proof-kernel review is claimed.

## Sources and attribution

Base: `7c472563474e60185e6ca101a17622133d047e56`, priority revision 7.
[SOURCES.json](SOURCES.json) pins all consumed files. The selected result
and catalogue are historical provenance, not runtime dependencies.
The retained [Discussion #5261](DISCUSSION-5261.md) gives the multi-shift
formula and its proof. Its source URL and SHA256 are recorded; a Discussion
is mutable, so this package retains the consumed text. Nick Petalas
(@petalas) supplied the two-shift result and field arithmetic in
[PR #4803](https://github.com/CrocSwap/integer-mult-bounds/pull/4803).
The Schur application comes from ssafwann's
[PR #4678](https://github.com/CrocSwap/integer-mult-bounds/pull/4678),
as credited in that source. Gaussian inversion and generating functions
are classical methods. No external mathematical priority is claimed.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
New work: Apache-2.0. Prior source notices remain unchanged.

## Open next questions

State one nonbinary Schur weight for an actual producer ensemble and test
whether it depends only on these nullities. This gives a concrete use for
the faster count. A paid selection and emission algorithm, physical reads,
dirty restoration and the complete consumer bill still block a supplier
claim. This package does not reserve that work.
