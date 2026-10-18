# Exact incident-residual costs for the historical parity decoder

**Structural decoder research / scoped negative result; no new kappa.**
Of the 692 completable degenerate nodes of the pinned `ParitySide(10)` DAG,
560 admit an incident-safe minimum frame, 12 need one extra dimension,
100 need **two** extra dimensions, and 20 admit no incident-safe frame at any
dimension. Here incident-safe means that every actual ancestor source line
and descendant target line has a zero or nonalternating residual. It does
not mean that the node frames fit together into a legal circuit.

This adds the missing line-residual analysis to
[ToikY's PR #972](https://github.com/CrocSwap/integer-mult-bounds/pull/972),
which computes pointwise minimum separating frames and explicitly leaves
incident residuals open. It applies the distinction studied by
[ArnavSwiggy's PR #920](https://github.com/CrocSwap/integer-mult-bounds/pull/920)
to an entire fixed DAG's radical-one nodes, with arbitrary numbers of
source and target labels. It neither replaces those contributions nor
reopens the historical large-DAG repair search.

## Reproduce

From the repository root, Python 3.11 or later, standard library only:

```sh
python -B research/parity-incident-completions/check.py
```

The offline checker verifies the source pins and signed scalar kernel,
reconstructs the fixed graph, enumerates all 3,096 distinct minimum frames,
tests actual residual vector sets, checks the 112 larger-frame witnesses,
and rejects the missing intermediate dimensions. It reports
`PASS_PARITY_INCIDENT_COMPLETIONS` with the counts above. Run the 22-test
corruption and residual regression suite separately with
`python -B research/parity-incident-completions/test_check.py`.
See [VALIDATION.md](VALIDATION.md) for the commands actually run and their limits.

Regenerate to a fresh path and check that result:

```sh
python -B research/parity-incident-completions/produce.py --out /tmp/parity-incident.json
python -B research/parity-incident-completions/check.py --certificate /tmp/parity-incident.json
```

On Windows, substitute a writable temporary filename for the `/tmp` path.
The certificate is deterministic; neither generation nor checking searches
the web or requires a solver.

## Complete finite domain and results

The assignment seed was **47**, sampled from OS randomness. This selects
the structural-decoder track and `h=10` from the historical small domains
8 and 10. The seed is not a claim of novelty: the new obligation is incident
residual legality and its exact local dimension cost, beyond PR #972.

The fixed DAG has 2,271 active nodes, including 120 inputs; 1,577 source
spans are nondegenerate and two nodes already have common-span obstructions.
The domain here is **all 692 remaining degenerate source spans**, each with
one-dimensional radical. The latter two categories are identified to bind
the domain, not subjected to a new all-frame census.

| Exact result on the 692 nodes | Count |
|---|---:|
| Distinct minimum separating frames | 3,096 |
| Minimum frames passing every source/target line residual | 2,538 |
| Frames rejected at a source / target / both | 158 / 400 / 0 |
| Nodes with an incident-safe minimum | 560 |
| Nodes requiring exactly one extra dimension | 12 |
| Nodes requiring exactly two extra dimensions | 100 |
| Nodes admitting no incident-safe frame at any dimension | 20 |

Of the 560 nodes with a safe minimum, 510 accept every minimum frame and 50 accept
only some. Of the 132 failures, the 12 dimension-three cases have explicit
dimension-four witnesses. The 100 dimension-seven cases have an alternating
allowed extension space, so dimension eight is impossible; dimension nine
works with zero outgoing target residual. The 20 dimension-five cases
already fill the target orthogonal complement, so there is no room to repair.

The [proof](PROOF.md) establishes the exhaustive coset enumeration, the
characteristic-vector test used by the producer, and the dimension lower
bounds. The checker independently enumerates vector sets and tests actual
residuals. Its only reused computation is the pinned historical DAG
constructor; it does not use the producer's linear-algebra implementation.
This is computational cross-checking with AI assistance, not independent
human review or a formal proof of the multiplication theorem.

The stopping rule is exhaustion of those 692 nodes and every one-dimensional
extension coset giving a minimum sandwich. Larger-frame witnesses and exact
dimension exclusions settle all 132 failed nodes. No time-limited failure to
find a frame is reported as impossibility.

## Cost decision and scope

Twenty nodes fail a necessary condition for the historical nested,
nondegenerate, orthonormal-residual interface even if scalar gates, source
access, helpers, copies, cleanup and recursive children were all free.
The unchanged DAG therefore cannot become a legal supplier merely by choosing
larger local frames. No large supplier implementation or assembly optimization
is justified by this mechanism alone.

The 212 additional local dimensions required by the 112 repairable nodes
are **not** a gate count, helper invoice or additive recursive cost. A paid
construction would still need simultaneous nesting, every internal residual,
source access, dirty compensation, copy/restoration work, recursive calls,
physical hosting, precision/tape and analytic transfer. The selected result's
all-size/compiler and other inherited assumptions remain untouched.

This result does not exclude changed DAGs, duplicated sums, different source
or target labels, encoded carriers or a different phase-transfer interface.
It makes no runtime or exponent improvement claim. `upstream/` and all
selected-frontier artifacts are unchanged.

## Provenance and credit

Base commit: `407d52ff15b2217b6e22bce44728b4c3907b6515`.
At that base the selected conditional value is
`1661960547713947/1000000000000000000`, from Jonathan Capalbo's T37/PR #942
composition. Its selected record, actual T37 construction, assembly and
maintainer review were read; historical parity numbers were not treated as
the current frontier. The new result does not depend on running that supplier.

[SOURCES.json](SOURCES.json) records source-file hashes and exact predecessor
heads. Credit Douglas Colkitt's historical parity-side work for the signed
kernel, common-span obstruction, characteristic criterion and failed repair;
DreamingOfClouds' format-limit analysis for frame restrictions; ToikY's #972
for the pointwise all-node census; and ArnavSwiggy's #920 for incident-residual
completion analysis and the six-dimensional control. The historical generator
retains its existing attribution and license.

Prepared for GitHub contributor **woklerx**, with substantial **OpenAI Codex**
assistance in mathematics, implementation, independent checking, review and
writing. New files are under the repository's Apache-2.0 license. No predecessor
package code is vendored or modified.
