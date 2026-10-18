# A six-vertex support budget excludes `2,3,4^4,6^5`

Eleven independent P112 pieces of weights bounded by `2,3,4^4,6^5` cannot
have code-intersection dimension at least five over a characteristic-zero
field. This removes one actual profile from the historical 77-profile
TWOSIDE `(5,6)` residue in DreamingOfClouds/PR3154.

Five small pieces have common support at most thirty. Quotient normalization
leaves six independent affine vertices. Their original pieces allow 108
support incidences, whereas the all-root branch requires at least 120 and
the mixed root/D7 branch at least 121. The [proof](PROOF.md) states all
hypotheses and the characteristic-zero argument.

The new finite check enumerates all 4,459 four-cliques in the retained
58-vertex anchored graph, including 3,136 independent cases. A second
implementation uses Gram intersections, edge-pair joins and integer ranks.
The all-root A5 spectrum and the complete 788,035-six-flat capacity census
are also replayed. [RESULT.json](RESULT.json) retains the exact quantities
and an attaining mixed witness. Fourteen behavioral controls cover source,
data and graph mutants, both rank algorithms, common shifts and cuts.

The original card was `formal-interface-lemma`; [TASK.json](TASK.json)
records the changed scope to this live finite decoder handoff. This is a
written proof with exact finite evidence. Full C5, `C(P112)>=64`, supplier
admission and a new kappa do not follow. The selected frontier is unchanged.
The standard Weyl-chamber theorem and original decoder reduction remain
explicit dependencies. Internal review and separate finite algorithms do
not constitute independent human or proof-kernel review.

## Reproduce

From a Git checkout, with Python 3.12 or the tested `uv` command:

```sh
uv run --python 3.12 --no-project python -W error -B scripts/research_package.py \
  --package research/p112-six-vertex-budget
```

The registered replay checks metadata and historical baseline provenance,
then runs the primary verifier, separate checker and behavioral controls.
It declares one unchanged external data input. No solver or third-party
Python package is needed. [CHECKS.json](CHECKS.json) records local coverage
and environment; [ENGINEERING.md](ENGINEERING.md) records implementation bounds.

A Git-free export can run the mathematical checks directly. Export this
package, place the pinned data file at a chosen external path, then run:

```sh
python3 -W error -B verify.py --data /path/to/pinned/data.txt
python3 -W error -B independent.py
python3 -W error -B test_verify.py
```

`--write PATH` on the primary verifier creates a comparison receipt at an
explicit output path. Ordinary replay compares against the committed receipt
and writes no artifacts. The registered runner isolates bytecode caches;
direct `-B` alone prevents writes but does not isolate existing cache reads.

## Prior coverage and credit

DreamingOfClouds/PR3154 supplies TWOSIDE and the original residue. Nick
Petalas/PR3176 supplies the retained E8/P112 geometry, support-72 alphabet,
anchor symmetry, graph and root-star traversal. The new contribution is
the six-vertex/thirty-cut support budget and its application to this named
eleven-piece profile. The earlier two-flat weight-only rules require at
least twenty certified cuts here. Other profiles and unknown actual support
overlaps are not classified by that applicability check.

[SOURCES.json](SOURCES.json) records exact predecessor heads, original paths,
Git blob IDs and SHA256 digests. Every retained file is checked against
those byte hashes. The original open-PR commits need not exist in a fresh
replay checkout; their source bytes are retained locally. The generic
provenance checker resolves the baseline catalogue and selected record in
Git, while the package checks retained predecessor bytes itself. Original
relative links inside the unchanged retained proof refer to its source
package. The present proof is self-contained about the implications used.
The retained notices preserve the earlier decoder lineage, including
joaqcoo's model. New work is Apache-2.0. Development and local checks used
substantial automated assistance.

## Open next questions

Before extending this census, identify another actual remaining profile
whose quotient normalization gives six independent affine vertices and
whose complete edge alphabet is still justified. That could reuse this
support budget for another decoder case. First pin the profile, check live
overlap and establish its support and quotient hypotheses. No such next
profile is established here. The active common-fourteen-cut investigation
of `2,3,4,6^8` is separate.
