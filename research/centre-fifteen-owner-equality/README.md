# Cubic structure and a signed defect at fifteen owners

**Scoped written proof with finite exact corroboration. No new kappa.**
Every graph attaining Sagar Thakrar's PR3291 fifteen-owner abstract floor is
cubic on fifteen vertices per side. Its six-cycles are vertex disjoint, and
it cannot have exactly one six-cycle. This contribution is produced by
Nick Petalas.

The new structural identity, over the integers, is

    C C^T C = 4C + J + P - Q,
    (P-Q) C^T = C (P-Q)^T.

C is the incidence matrix. P and Q are partial permutation matrices on the
vertices lying on six-cycles. P matches opposite vertices on each cycle;
Q matches vertices on different cycles. If there are t six-cycles, their
active sets have size 3t. Thus t is either zero or one of 2,3,4,5.
[PROOF.md](PROOF.md) gives the universal argument and exact hypotheses.

This is a new restriction on the equality search left by PR3291 and
Matarener's PR3656. Their floor, geometry, source extraction and coset
certificate are cited without replay or audit. We do not classify every
equality graph or prove that the six-cycle-free example is unique.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/centre-fifteen-owner-equality/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/centre-fifteen-owner-equality/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/centre-fifteen-owner-equality
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/centre-fifteen-owner-equality --check-source-history
```

Substitute an installed CPython 3.12 path elsewhere. The direct verifier is
read-only and prints a generated receipt bound to every package file by
SHA256, followed by `PASS_CENTRE_FIFTEEN_OWNER_EQUALITY`.

The bounded corroboration visits all 531,441 local path profiles in
{0,1,2}^12, including the 133 profiles admitted by the path-sum/cycle cap;
checks the twelve possible noncubic root degrees; and checks the integer
defect on the duad/perfect-matching graph. All 720 eligible two-edge switches
of that graph are tested. Exactly 360 are four-cycle-free and all 360 fail
the six-cycle cap. Independent intersection and literal-walk cycle counters
agree on their complete cycle sets. This is a bounded control family, not
an enumeration of all fifteen-owner graphs or evidence that the remaining
cycle counts are impossible. No nonzero-defect equality graph is supplied;
nonzero local profiles are checked independently of graph realization.

Controls reject malformed equality boundaries and local path profiles, and
a cubic C4-free fifteen-by-fifteen cyclic graph specifically at the six-cycle
capacity gate. Literal matrix multiplication supplies a separate path-count
check. Normal and optimized commands retain every check.

## Connection and limits

The original `centre-path-sharing` card is changed to a structural side
question in the retained one-to-one block-repair model. The theorem assumes
the abstract minimum-degree, C4-free and cycle-cap conditions. It does not
recompute the routes or prove those conditions for another supplier.

For a route-labelled equality search, the cubic restriction removes larger
degrees, and the P/Q identity supplies necessary equations before checking
route labels and scalar coefficients. These obligations remain open. No
physical acquisition, dirty restoration, frame conversion, hosting, precision,
stock, recursive invoice, all-size compiler, admitted supplier or complete
multiplication theorem is supplied. The selected frontier remains unchanged.
Independent human and formal proof-kernel review are unclaimed. No selected
cold replay, Lean or Docker run is part of this result.

The historical card control fails with `KeyError: 'complex_profile'` against
the selected schema. The current `research_selected_baseline.py` binding
control passes. These are orientation observations, not scientific premises.

The checker has no recursion, subprocesses, network or write paths. Graphs
are bounded to 32 vertices per side; actual cycle checks use cubic graphs
with fifteen vertices per side. Walks have exactly five expansion rounds.
The largest local profile domain is 3^12, processed one tuple at a time.
Functions stay below sixty physical lines. Python allocates managed objects;
fixed allocation is not claimed. These fixed domains and the registered
120-second command bounds are the compensating limits. Raw-pointer and
preprocessor rules have no direct Python counterpart. Warning-strict normal
and optimized execution and AST inspection provide diagnostics; no project
static type checker is configured for this isolated standard-library file.

## Open next questions

1. Can an equality graph have two through five six-cycles? Use the cubic
   fifteen-by-fifteen boundary and signed partial permutations first. This
   would decide whether a route search may restrict to girth eight. No such
   exclusion or witness is supplied here.
2. Can a graph satisfying this stronger boundary carry the actual routes
   and scalar coefficient equations? Begin with one equality incidence and
   retain every route relation. The route-labelled CSP and a favorable full
   physical budget remain blockers to a supplier construction.

The structured questions are also in [TASK.json](TASK.json).

## Credit

Sagar Thakrar #3291 supplies the local path-counting inequality and sharp
fifteen-owner theorem. Matarener #3656 supplies the coset construction and
minimum-support question. Retain dcharb78 #3147, Ross Richardson #3071,
Gonzalo Mier #3097, Sudarsh Chaturvedi #3168, Aaron Wang/navinor, ywz65 and
the selected source lineage for the block-repair model and route conditions.
The duad/perfect-matching geometry and ordinary graph path counting are
classical; no literature-priority claim is made for them. Only the equality
reduction, signed defect and its consequences are new in this package.
Predecessor files and notices remain unchanged. Apache-2.0.
