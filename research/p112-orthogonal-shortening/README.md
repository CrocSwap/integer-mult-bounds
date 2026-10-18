# An analytic proof of the orthogonal A5 frame bound

[PROOF.md](PROOF.md) replaces the 2,025-frame census in concurrent
[PR3205](https://github.com/CrocSwap/integer-mult-bounds/pull/3205) with a
short Parseval argument. If c_j counts cost-j coordinates in an orthogonal
eight-root frame of an A5 simplex, then `2c_0+c_1>=2`. The inherited full
spectrum therefore leaves at least 122 endpoint incidences after the frame
and thirty further coordinates are deleted.

PR3205 already proves the support-thirty P112 shortening theorem. This
contribution gives an analytic proof of its root-frame step and does not
claim that shortening range as new. The inherited mixed-edge minimum 121,
root/D7 classification and A5 spectrum remain separate dependencies for
the shortening corollary. No new historical profile, supplier or kappa is claimed.

[RESULT.json](RESULT.json) retains the scalar and matrix receipts and an
attaining orthogonal frame. Checks cover 210 sorted integer evaluation
patterns, 165 formal frame-cost signatures, the A5 Gram matrix and literal
cut costs. They corroborate the proof without enumerating orthogonal frames.
At thirty-one cuts the witness reaches equality at 120, which is a failed
strict inequality, not a counterexample to a stronger shortening theorem.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root, put
all disposable outputs in one external session directory:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-orthogonal-replay"
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -W error -B \
  scripts/research_package.py --package research/p112-orthogonal-shortening
```

The registered replay runs both unchanged predecessor implementations,
the new analytic checks and twelve optimized behavioral groups. Its complete
input set is declared and pinned in [VERIFY.json](VERIFY.json) and
[SOURCES.json](SOURCES.json). The `-S` child commands exclude installed-site
module collisions; the runner supplies private bytecode caches.

Direct `verify.py` and `test_verify.py` runs check the new analytic argument and
authenticate inherited inputs. They do not execute the inherited mathematical
replays; use the registered command for that coverage. The mathematical
replay works in a Git-free export with all declared inputs. Metadata and
publication-byte checks additionally require Git. `verify.py --output NEW_PATH`
emits a receipt outside the checkout and refuses to overwrite a file.

## Open next questions

Can a similar variance argument replace the mixed root/D7 clique census?
First derive an invariant valid for all mixed vertices and test its proposed
bound against the retained minimum-121 witness. Root-only integer evaluations
cannot be assumed after introducing a D7 edge.

Can the actual small-piece supports exclude the thirty-one-cut equality
witness? Bind a caller before extending the search. The present arbitrary-cut
argument supplies neither such an exclusion nor an actual counterexample.

## Credit and verification limits

Nick Petalas contributes the analytic Parseval proof. Concurrent PR3205 at
`49d26a7604686aa77cf88d7280b2e313cb4882f6` retains priority for the
support-thirty theorem and its finite frame proof. No duplicate theorem
improvement is claimed.

Nick Petalas/PR3188 supplies the inherited six-vertex mixed-edge result and
A5 spectrum, building on PR3176 and the retained geometry. PR3203 supplies
the support-29 predecessor and handoff. DreamingOfClouds/PR3154 supplies
TWOSIDE and the original decoder reduction. The retained source notices keep
the E8/P112 and decoder lineage, including joaqcoo. Predecessor files are unchanged.

The standard Weyl-chamber theorem and inherited finite geometry remain
mathematical dependencies. Applying this lemma to the complete decoder floor
also requires the original reduction. New work is Apache-2.0. Development included
substantial automated assistance and internal review. Independent human
review, proof-kernel verification, hosted CI and complete supplier admission
are separate. See [CHECKS.json](CHECKS.json) and [ENGINEERING.md](ENGINEERING.md).
