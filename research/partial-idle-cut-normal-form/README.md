# Independent idle factors cannot beat the balanced path cut

Allowing every initial and terminal idle to select its native stage factors
independently does not improve the query-thinned path controller. For every
positive pair count p, exact scalar diagonalization forces a common cut, and
deleting the factors outside that cut improves every concave rank moment.
The balanced cut dominates all other cuts in this fixed native-stage pattern.

This is a scoped obstruction, not a higher kappa or a universal controller
ceiling. The current selected kappa remains 0.00302015. The theorem is
independent of the local helper/paid tariff, so substituting another tariff
does not reopen this idle-selection mechanism. Changed stage patterns,
topologies, boundary contracts and border exactification remain outside it.
The scalar boundaries act on the main roles; a new contract that mixes native
helper outputs into them is also outside this theorem.
The formal BIT group ring is covered too: coefficient comparison in the
one-generator algebra replaces differentiation, so imposing D_s²=1 in
characteristic two does not escape the proof. This says nothing about a
geometric quotient that changes native directions or their physical ranks.

The result targets a concrete larger mechanism: the predecessor selects
whole idle windows, whereas this model selects each available stage factor
inside each window separately. The source path has p-1 independent binary
choices for each of p+2 full stages. A proof, rather than a larger finite
packing search, closes that expanded family.

Read [PROOF.md](PROOF.md) for the precise hypotheses and all-p argument.
The individual stage projectors commute exactly when their consecutive
vertex intervals intersect. Pairwise intersection of intervals gives one
common cut. Concavity then prices every deleted factor with both its lost
target credit and its removed paid charge. No single-variable commutation
test is assumed sufficient for arbitrary multivariate correctness.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/partial-idle-cut-normal-form --check-only
python3 -B scripts/research_package.py --package research/partial-idle-cut-normal-form
```

Normal replay reads the committed receipt and writes no artifacts.
`python3 -B research/partial-idle-cut-normal-form/verify.py --write` explicitly
authors the receipt. Source bytes are bound in SOURCES.json. The verifier
extracts only three pure functions from the retained Laurent controller;
it does not import that controller's unrelated dependencies.

The exact finite controls bind seven source words, all 1,023 one-stage
subsets through p=7 on 7,422 integer interpolation nodes, 26,093 projector
pairs through p=6, and all 4,728 compatible families through p=4. Integer
capped-rank comparisons cover every discrete concave price for those
families. They include 23,974 deleted stage factors and the complete
selected p16 positive invoice: 10,928 targets, 64,620 paid calls, surplus 752.
The checker also covers 128 multistage recurrences at Q=2, 36 exact canonical-cut boundaries and 528 balanced-cut comparisons. The all-p conclusion comes from the written proof, not those finite counts.
Seven source BIT group-ring words and the complete BIT p16 invoice are
also checked. All 26,093 commutator cases are checked in characteristic
two as well. No full selected native/outer replay or formal kernel
verification is claimed.

## Attribution and overlap

Base: canonical main b58ad9ef4d4e861b0eaa5dba41742bdc072dca51. The 14:05 UTC
overlap snapshot covered 415 open PRs and 3,586 Discussion records with
complete reported pagination; local checkout note coverage was sparse.
Targeted terms found no independent partial-idle or interval-Helly proof;
this is not a novelty certificate. PR4623's no-idle border and PR4602's
large idle invoice motivate a different exact-interface question here.
PR4446's dynamic search covers every native/direct mask in its minimal-cut
family, and is credited rather than repeated. We prove domination for a
larger idle family with the query-thinned native-stage mask fixed.

Credit zxv's native/controller work; Cinna Davis's PR4440 query thinning,
PR4441/4447 frame changes and PR4470 joint-helper construction; Jacob Alan
Sussman's mixed-target compiler; and the retained Clifford, BIT, precision,
stock and outer contributors. No predecessor source or selected record is
changed. Prepared for Cinna Davis (1337isnot1337) with substantial OpenAI
Codex assistance; no subagents. New work is Apache-2.0.

## Open next questions

Change the controller topology and first prove an exact small Laurent
factorization; or close a paid chronological border-to-exact interface such
as the one left open in PR4623. Neither is established by this package.
The concrete relevance, first step and blockers are recorded in TASK.json.
