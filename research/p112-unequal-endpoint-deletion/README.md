# Two P112 weight-seven profiles close with unequal endpoints

Nick Petalas. Apache-2.0.

Ten independent P112 pieces with code-intersection dimension at least six
cannot have either actual TWOSIDE `(b,t)=(6,4)` profile
`3,5^3,6^5,7` or `4^2,5^2,6^5,7`, over any characteristic-zero field.
[PROOF.md](PROOF.md) gives the complete scoped argument.

Deleting the last piece retains five code dimensions on nine independent
pieces. Three small pieces have support at most 28. The remaining six
endpoints have capacities `12,20,20,20,20,20`, so Nick Petalas/PR3169's
coordinate inequality requires `795<=784`, a contradiction of eleven.
The older incidence bound gives 812; replacing the unequal endpoints by
six twenties gives 816. Neither losing bound proves the exclusion.

The new result is this unequal-endpoint application and its source-bound
checks, not a new A5 inequality or geometry census. It follows the released
[PR3197 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19001119).
It does not close full C5, prove `C(P112)>=64`, admit a supplier or improve
kappa. The selected frontier stays unchanged. Evidence is author-checked,
not independent human or proof-kernel review; hosted CI is separate.

## Reproduce

Python 3.12 or later, standard library only. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-unequal-endpoint-replay"
mkdir -p "$RUN"
TMPDIR="$RUN" python3.12 -B scripts/research_package.py \
  --package research/p112-unequal-endpoint-deletion
```

The two bounded commands print `PASS_P112_UNEQUAL_ENDPOINT_DELETION` and
`Ran 12 tests ... OK`. They authenticate all four declared inputs, replay
all 4,097,782 inherited five/six-flats and all root planes, check 117,649
endpoint equality assignments, reproduce historical inclusion, and audit
every weight-certified four-piece quotient basis. A separate subset oracle
checks the two-flat cover minima; twelve behavioral groups include four
input mutations and strict/losing controls. [RESULT.json](RESULT.json) is
the expected mathematical receipt; [CHECKS.json](CHECKS.json) records checks.

No output is generated in the checkout. Direct replay is
`python3.12 -B research/p112-unequal-endpoint-deletion/verify.py` followed by
`test_verify.py` there. An optional `--output NEW_ABSOLUTE_EXTERNAL_PATH`
creates an exclusive external receipt. Git-free exports need this package
and exactly the four inputs listed in [VERIFY.json](VERIFY.json), preserving
their relative paths. The registered runner additionally validates Git
provenance and isolates bytecode caches. Direct execution assumes a trusted
Python runtime and import cache. [ENGINEERING.md](ENGINEERING.md) records
implementation bounds and verification limits.

## Sources and limits

Base main is `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[TASK.json](TASK.json) records the changed scope from formalization to the
live C5 handoff, success/stop test and remaining obligations.
[SOURCES.json](SOURCES.json) binds all live inputs at that base and records
exact predecessor heads. No frozen package is changed or copied.

DreamingOfClouds/PR3154 supplied the TWOSIDE filters and original reduction.
Nick Petalas/PR3169 supplied the coordinate inequality, with PR3164 and
PR3161/3162's retained root geometry. PR3197 supplied the dimension-deletion
application for a different ten-piece profile; PR3195 supplied the adjacent,
shorter deletion caller. The retained E8/P112 decoder lineage, including
joaqcoo's model, remains credited in the declared predecessor proof and
sources. Development and local checks used substantial automated assistance.

Both new profiles have excess `35<36` and occur among the 69 historical
`(6,4)` survivors. That number is not a current unresolved count. Their best
weight-only two-six-flat covers need sixteen paid cuts, beyond the earlier
fourteen-cut rule. Actual support overlaps and other profiles are not ruled
out by that comparison. The proof inherits the standard Weyl-chamber theorem
and original decoder reduction; no native, physical or full supplier replay
was run.

## Open next questions

Before another census, bind one actual still-open profile to its surviving
code dimension, support caps and current exclusions. First refresh
Discussion3156 and apply the existing deletion and cover rules. The blocker
is a missing current disposition, not another seed. This package does not
justify expanding a construction family. The structured question is in
[TASK.json](TASK.json).
