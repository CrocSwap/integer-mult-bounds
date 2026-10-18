# P112 orthogonal rank demands outside full frames

**Finite census, counterexamples and a necessary-condition guard. No new κ.**

Checking every subset of every eight-root live frame misses **35,232**
orthogonal sets in the pinned P112 geometry. Two explicit nine-term support
layouts of binary pairing-rank cost **63** pass all **227,696** frame-contained
demands but each fails six of the omitted demands. Thus neither is a decoder,
regardless of its real or complex coefficients.

The reusable guard in [cliques.py](cliques.py) enumerates all **262,928** nonempty
cliques directly from the live orthogonality graph. It does not assume that a
partial orthogonal set extends to an eight-root live frame.

| Set size | All orthogonal sets | Outside every full live frame |
|---|---:|---:|
| 1 | 112 | 0 |
| 2 | 3,304 | 0 |
| 3 | 31,024 | 1,792 |
| 4 | 94,892 | 17,024 |
| 5 | 82,656 | 12,096 |
| 6 | 39,088 | 3,808 |
| 7 | 10,592 | 512 |
| 8 | 1,260 | 0 |

Here “outside” means not contained in a full live frame; it does not mean that
the set is inclusion-maximal. All orthogonal pairs do extend, so pair checks
alone cannot expose this domain gap.

## Exact obstruction and scope

For an orthogonal set Q, the required decoder restriction is a nonsingular
diagonal matrix, of rank |Q|. Each term whose two support factors both meet Q
can contribute rank at most one; every other term contributes zero. Therefore
at least |Q| terms must meet Q on both factors. This remains necessary after
independent whole-term transposes, arbitrary coefficients or further zero trims.

For example, **Q = {29,38,58,65,79}** consists of five mutually orthogonal
live roots. In either saved cost-63 layout only four terms meet Q on both
factors. Rank at most four cannot equal the required rank five. This Q is
contained in no full live frame. [CERTIFICATE.json](CERTIFICATE.json) records
all six failed sets for each layout and the incident term indices.

[CANDIDATES.json](CANDIDATES.json) encodes a term as `[a,b,cut_hex]`, with
support `(S[a] minus cut, S[b])`. `S[2α]` is the live nonorthogonality star of
root α; `S[2α+1]` also removes α. The binary pairing matrix is
`B[i,j] = (1 + <root_i,root_j>/4) mod 2`. Literal restricted ranks, rather than
the advertised costs, determine the invoice. Each example has four rank-eight,
four rank-six and one rank-seven factors, totaling 63.

The samples arose from global support searches, intermediate rank-five
two-code cuts and local repairs. The discovery search is not part of this
package and no search completeness is claimed. Every claimed finite fact
about the saved examples is reconstructed by the verifier without a solver.

This extends the explicitly scoped frame relaxation of
[Cinna Davis's PR1347](https://github.com/CrocSwap/integer-mult-bounds/pull/1347).
It does **not** identify an error in that PR's stated frame bound. It shows
why upgrading a full-frame test to all of its subsets still does not supply
every orthogonal rank demand. Passing the complete guard would remain only
a necessary condition: coefficient identities and physical accounting are
separate obligations. No universal COPY floor, supplier admission, moment
improvement, multiplication theorem or Lean proof is claimed.

## Reproduce and use

Standard library only, tested with Python 3.12.3. From repository root:

```sh
python3 -I -B research/p112-unextendable-cliques/verify.py
python3 scripts/research_package.py --package research/p112-unextendable-cliques
```

Expected: `PASS_P112_COMPLETE_ORTHOGONAL_CLIQUE_AUDIT`, then the registered
package pass. `--write-certificate` explicitly regenerates the canonical JSON;
the normal replay is read-only. No external proof-relevant files are imported.

For a search, load the pinned model, call `geometry(model)` and
`all_orthogonal_sets(model['live'], gram)`, then call
`require_rank_demands([(left_mask,right_mask), ...], complete_cliques)`.
`rank_violations` returns witnesses for constraint separation. Supply the
complete clique list; `frame_subsets` is retained only for the regression.

Verification compares bitset and set-based complete clique enumerations,
reconstructs the E8 root set separately, and compares two binary elimination
orders. It checks the known cost-64 coordinate decoder's exact factorization
on all 12,544 entries and five failure controls, including the two false
cost-63 fixtures. The separate implementations share the same AI-assisted
author; this is not independent human review or formal verification.

## Open next questions

1. Can a masked decoder with at least nine terms survive all 262,928 demands
   at cost below 64? This remains relevant to the complex-side inventory.
   Start by feeding these missing clique constraints into a bounded support
   search. A successful support cover still needs exact coefficients and a
   fully charged physical realization.
2. Can a smaller demand family give equivalent rejection power for a specified
   support alphabet? Start from the stored failing cliques and prove any
   proposed dominance reduction. Inclusion of vertex sets alone does not make
   the corresponding rank-demand inequalities redundant.

[TASK.json](TASK.json) records these questions and the scope change from
decoder construction to an adversarial audit. [SOURCES.json](SOURCES.json)
pins the base/card provenance; [PREDECESSORS.json](PREDECESSORS.json) pins
the verbatim geometry and its upstream path. Later frontier changes do not
alter this fixed geometric question.

## Credit

Jeremy Diviney, with substantial OpenAI Codex assistance in search, checker
design, exact verification and writing. New work is Apache-2.0.

The geometry and C/N support conventions are retained from Cinna Davis
(@1337isnot1337), PR1347 at `64fd5f9e91961dedc16118fcc7ad71ee82efe28f`, and
its PR1323 lineage. Earlier contributions include Navinor/PR1226,
David Arias/PR1236, Hanson Sun/PR1242, DreamingOfClouds/PR717 and the retained
E8/frame-pair sources. [PR1226-NOTICE.md](PR1226-NOTICE.md) preserves the
upstream notice. No predecessor executable is imported or modified.
