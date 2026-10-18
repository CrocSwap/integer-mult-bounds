# Analytic A2 rank-six support capacity

For every full E8 large A2 projective fiber A and every ambient binary
space V of dimension at most six,

```
|R intersect V| + |A intersect V| <=32.
V not contained in span(A) implies the stronger bound30.
```

PR3262 already proved32 by a finite support-space census. This package
replaces that proof dependency by a signed quadratic argument. It derives
the entire127-hyperplane table analytically, proves exactly27 equality
spaces for every A, and characterizes equality by a balanced affine
five-section avoiding the fiber's unique missing root. A literal16-label
rank-six witness attains32 on the actual fixed P112.

[PROOF.md](PROOF.md) is self-contained after the finite quadratic binding.
The new replay authenticates the existing geometry before execution and
checks all3360 fibers from all1120 A2 planes. A separate dense rational
reconstruction checks the roots, labels, canonical127 hyperplanes and
exact witness. [RESULT.json](RESULT.json) stores the read-only receipt.
This is a scoped support lemma, with no new shortening threshold, actual
caller, full C5, physical supplier, kappa or selected-frontier claim.

## Reproduce

Python3.12 or later and the standard library suffice. From the repository:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/e8-a2-analytic-rank6
```

The direct scripts are `verify.py`, `independent.py` and
`python -O test_verify.py` in this directory. Use `-W error -B` and a fresh
private `PYTHONPYCACHEPREFIX`, or run a source-only Git-free export. All
normal replays compare the committed receipt without regenerating it.
The registered runner isolates bytecode. Fifteen controls reject malformed
or reclassified source manifests, actual changed source/proof bytes,
symlinked input and invalid binary spaces. Actual wrong-sign and rank-seven
counterexamples show why those hypotheses cannot be dropped. The
missing-root condition is checked against the16/15 hyperplane class.

The registered metadata resolves only canonical-main objects. Exact
predecessor proof bytes are retained under vendor with their original
commit, path, blob and SHA256 in SOURCES.json. Custom authentication binds
the full fixed inventory, schemas and usages and checks those bytes before
any geometry runs. Fresh CI needs no pending-PR Git objects. Authentication
is source provenance, not mathematical approval.

## Open next questions

Can these equality supports satisfy one actual caller's coefficient and
single-common-cut equations simultaneously? Pin a specific caller before
applying the lemma. This package does not answer realizability or improve
a threshold. The separate mixed5/5/6 cut40 investigation owns that question.

Is outside-span30 sharp on the fixed P112? Start with one actual ambient
six-space and reconcile its root and singleton supports. No sharpness or
automatic construction round follows here. TASK.json records the relevance,
first steps and blockers for both questions.

## Credit and limits

Credit Nick Petalas/PR3262 for the original32/table, PR3280/3269 for the
signed quadratic method, David Arias's retained quadratic model,
DreamingOfClouds/PR3154 and the E8/P112 lineage including joaqcoo. Worker3
suggested making the outside-span and equality conditions explicit during
scope coordination. The retained predecessor proofs are unchanged.

This result has written mathematics, finite exact binding and an internal
read-only computational peer check. It is not independent human or
proof-kernel approval. Historical global flat censuses, normalization of
arbitrary code planes, selected cold replay, Lean and Docker are unrun.
No physical, restoration, consumer or all-size supplier cost is admitted.
The exact implemented bounds and review receipt determine the scope.

## Bounded implementation decisions

Power of Ten rules1,2,4,5,6,7,9 hold through iterative binary elimination,
bounded root/fiber inventories, short functions, explicit `require` checks,
local state and checked returns. Ambient9-bit inputs cap spans at512;
there are7140 root pairs,1120 planes,3360 fibers and127 corroborating
canonical hyperplanes. File reads are capped at100KB. Every replay has a
120-second timeout. Source and control failures propagate as exceptions.

Rule3 deviation: Python's managed runtime allocates during arithmetic.
Scope is this finite standard-library replay. The enforced finite domains
bound retained data to3360 fibers of27 labels, at most512 points per span,
and at most512 input rows. Allocation inside Python/Fraction is not
instrumented. A native fixed-buffer implementation would be needed if
this became a constrained production verifier.

Rule8 deviation: the pinned geometry is authenticated before `runpy.run_path` reads its
source directly, without import bytecode lookup. The checkout must stay
stable between authentication and execution. One fixed path, fixed complete
manifest hash and exact Git-blob/SHA256 checks bound the target. No fetched
or generated code is executed. Source-drift/symlink controls exercise the
boundary. Follow-up for a reusable loader belongs in shared tooling, not a
new dependency here. Function callbacks are limited to the inherited
integer dot product and bounded test calls, a rule9 deviation from a
literal ban on indirect calls. Their finite targets are explicit.

Rule10 uses warnings-as-errors, Ruff and formatting on the new Python
files, registered replay and optimized controls. The pinned source remains
unchanged; its unused historical census functions are neither called nor
reformatted. Any future code change must rerun the same relevant checks.
