# Rank-two residual completion

Every binary symplectic partial map with residual-form rank two has a
completion within one turn of the displacement-plus-nullity lower bound.
For every nonalternating residual form, the exact count is **2r-2**.
An explicit radical-lift test also attains that count for alternating forms.
All axes stay in the given ambient space. Fixed spectators remain prescribed.

The [proof](PROOF.md) gives the reduction and its limits. The alternating
closed case is not classified: exact examples attain either endpoint.
The API in [completion.py](completion.py) returns an interval when necessary.
It does not silently assert optimality. The generic interval [6,7] in the
last fixture has a separate six-turn optimum certificate.

This resolves part of [PR6494's open higher-rank question](https://github.com/CrocSwap/integer-mult-bounds/pull/6494).
It gives a constructive budget for candidate native label completions.
It is a formal unsigned turn tariff, not a Gaussian paid-rank or physical
cost theorem. No actual supplier or new kappa is claimed.

## Replay and evidence

```sh
python3.12 -B scripts/research_package.py --package research/rank-two-residual-completion
```

The standalone command is `python3.12 -W error -B verify.py` from this
directory, and again with `-O`. Python 3.12 and its standard library are
enough. [RESULT.json](RESULT.json) is recomputed and compared. The replay
needs no Git, network, pending branch or external package.

All 7,644 rank-two forms in dimensions three and four have explicit partial
isometry embeddings. A separate bit-pairing and matrix interpreter checks
the whole returned symplectic matrix. There are7,108 exact small-group
partial-map distances,64 larger conjugated inputs,30,282 prescribed
spectators,8,066 literal words in the four-turn exclusion,120 omitted
turns,11 malformed inputs and three source-corruption controls. The
retained kernel and source proofs are checked before use. The written
argument is the all-size proof; this finite corpus is corroboration.

The base is canonical main7c49fe32c55de02c2c873655c804b16e4c3fef0a,
priority8, selected6030. The selected binding example passed. The live
source handoff, open PRs and Discussions were checked before the claim.
The 01:51Z cache covered463 open PRs and6,456 Discussion records; main
source searches supplement the sparse local inventory. This is no novelty
guarantee for unpublished work or arbitrary nested diffs.

## Open next questions

* Classify the alternating closed case. The six- and five-turn fixtures
  show that the radical-lift test has no converse. Start with the induced
  action on radical lifts and minimal Wall-form extensions; test both
  fixtures before asserting a criterion.
* Bind one optimal word to an actual signed native contact. Include fixed
  spectators, a phase anchor, all monomial passes, owner restoration and
  the complete signed bill. A label-word saving alone cannot change kappa.

Precision, stock, tape, compiler, outer admission and all five selected
assumptions remain. Independent human and proof-kernel acceptance are
unclaimed. Lean, Docker and the full selected replay were not run.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents.
Nick Petalas / PR6494 supplies the retained rank-one kernel and proof;
Krzysztof Wojt / PR5097 supplies the lower bound and zero-form reduction;
Nick Petalas / PR5085 supplies the residual form and low-turn cutoff.
Brian / JoyboyBrian / PR5051 supplies signed compatibility. Credit also
David Ganz / Dugongue / PR4841, Cao Yifan / intqwq, Cinna Davis, zxv,
Jacob Alan Sussman and the retained native/compiler lineage. Wall forms,
symplectic elimination and Callan's binary exceptions are established
mathematics. This package makes no literature-priority claim. Apache-2.0.
