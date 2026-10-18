# Joint-width cuts for the T16 class relaxation

PR2169's class-level packing search can produce unrealizable pattern/flow
marginals even with its full per-call Hall and optional single-width
Gale-Ryser-style constraints. This package supplies an exact separator for
the additional necessary constraints

    sum(t in T,w in U) Y_tw <= sum_p X_p min(|T|,sum(w in U) p_w).

This is a standard capacity-counting principle applied to the pinned source,
not a new Hall theorem. Its useful distinction here is simultaneous width
and call subsets. An explicit example in the actual capacity-16, 224-bin
class 9 passes both existing families but violates the mixed constraint 4<=3.
Moving one helper to another call makes the same patterns legal. The new
constraint rejects an impossible flow without forbidding that pattern for
every later search.

[PROOF.md](PROOF.md) proves validity and exact separation by sorting call
loads. It explains the strictness witness, existing GR credit, and why the
reported eleven-quad-bin failure requires at least 11 outside helpers rather
than 4. That failure was already diagnosed by the producer; its missing c1
artifact is not replayed here. The reported 1002 relocation lower bound was
computed before the pattern ban and is neither refuted nor certified here.

## Reproduce and use

CPython 3.12, standard library, no optimizer or network:

```sh
python3.12 -I -B scripts/research_package.py --package research/t16-joint-width-realization-cuts
```

The registered suite checks both selected and PR2169 concrete maps, each
69120 helpers,32256 bins,144 classes and182652 sorted-prefix inequalities.
It exhausts 19683 small concrete schedules and 14989 direct-subset comparisons,
including 5928 violating balanced perturbations. It includes source, typed
receipt, source-format CLI and invalid-marginal controls. Default checks
never rewrite evidence; `--write-result` explicitly creates a missing receipt
and refuses overwrite.

To separate a new `mindiff_cls1.py` stage1 output:

```sh
python3.12 -I -B research/t16-joint-width-realization-cuts/verify.py --stage1 candidate.json --output new-cuts.json
```

The CLI accepts the retained `x,y,changed,bound` schema and uses that script's
**sorted physical-bin class numbering**. `changed` and `bound` are ignored
solver metadata. `glob.py` uses a different class enumeration; its output
must first be remapped by(capacity,allowed calls). The mathematical cuts
apply to either enumeration. `cuts.py` also exposes the pure per-class API.

Output gives the violated class, width subset, call subset, exact lhs/rhs,
and pattern coefficients. In a model, add coefficient
`min(len(calls),sum(pattern[w] for w in U))` for **every** pattern variable,
including patterns absent from the supplied sparse candidate. Never copy
only the listed nonzero-candidate pattern terms into a general model.
An empty cut list means no violation in this family; it is not a realization
certificate. Global demands, idle targets and physical audits remain with
the original pipeline. No solver bound is trusted by this command.

## Source and claim limits

Canonical main 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2, priority 4.
PR2169 source head 01b15aee27947d3319c8574464bdab80a00d2839. Six small relevant
source/data snapshots retain exact SHA256 and Git blob IDs. No predecessor
code executes. Four retained main inputs reconstruct actual phase ranks,
windows and active-pair exclusions. Their bytes authenticate before use.
This structural model reconstruction is not a fresh full native cold replay.

The scope is a stronger necessary relaxation, not a new owner map, measured
search speedup, packing optimum, physical supplier or new kappa. Pricing
both suppliers is not claimed because no paid profile changes. The original
selected-word packing ceiling still applies. Start baseline bindings passed.
Overlap searches included PR bodies and a timestamped 1197-record Discussion
snapshot; GraphQL rate limits prevented a complete fresh Discussion census.
Bounded live Curiosity Bot reading of PR2169 does not remove that limitation.

## Open next questions

1. Does adding these cuts reduce stage2 failures or improve bounded solver
   runs? Retain candidate files and compare identical solver settings; no
   performance claim follows from a stricter relaxation alone.
2. What colored-degree obstructions remain after every cut passes? Retain
   a counterexample from the source's exact bin-level realization rather
   than treating no-violation output as sufficient.

Structured handoffs and first steps are in [TASK.json](TASK.json).

## Credit

Philippe Van Velzen's PR2169 and its disclosed Claude assistance provide the
class model, Hall/GR constraints, existing failure diagnosis, heuristic ban,
candidate and search artifacts. The retained seed67 auditor and selected
owner construction, Douglas R.Colkitt and all upstream source authors retain
their attribution. Standard Hall/capacity counting is not claimed as new.
Prepared for ywz65 with substantial OpenAI Codex assistance, including a
separate AI review. Apache-2.0; predecessor snapshots are unchanged and the
repository license applies. No human or maintainer acceptance is claimed.
