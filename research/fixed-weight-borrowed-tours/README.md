# Exact restored fixed-weight parity tours

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped mathematical proof with exact finite corroboration. For every n>=1
and 1<=k<=n, a borrowed arbitrary source row can visit every weight-k mask
of n unchanged source rows and return to its input with exactly

    2 binomial(n,k) + 2k - 2

source toggles. This is optimal among closed one-anchor schedules, even
with arbitrary intermediate masks and repeated visits. If the targets
number R, each requiring the anchor plus its designated source parity,
their complete cost is R plus this transition count. Every target is
written once and all source rows are restored. The k=0 cost is R.

For n=5, k=3 and one target per mask, the complete circuit costs **34 row
ADDs versus 40 direct ADDs**. The six-ADD reduction includes preparation
and restoration. At row width L these are 34L versus 40L bit XORs.
[PROOF.md](PROOF.md) gives the exact boundary, lower bound and constructor.
This is a local row-register result, with no new kappa or supplier admission.

## Predecessors and new scope

Cinna Davis / [PR2271](https://github.com/CrocSwap/integer-mult-bounds/pull/2271)
introduced the borrowed-source multi-mask interface and asked in Open next
question 2 for shortest tours through higher-dimensional mask families.
This result answers that question for every complete fixed-weight layer.
The application to k>=3 is the new contribution here. Nick Petalas /
[PR4899](https://github.com/CrocSwap/integer-mult-bounds/pull/4899) already
proves the k=2 case with unequal positive source prices; that specialization
is credited rather than claimed as new. The reflected Gray construction
and Hamming-distance tools are classical and are proved here for completeness.

Ali Romman / [PR5372](https://github.com/CrocSwap/integer-mult-bounds/pull/5372)
proves an all-nonempty-mask optimum with a paid clean-row contract. The
present masks all have one fixed weight, and the anchor is an arbitrary
borrowed source. No predecessor scientific verifier is imported or replayed.
The source question and original card are pinned as historical provenance
in [SOURCES.json](SOURCES.json); the standalone verifier has no live input
outside this six-file package.

The `bit-helper-contract` card changes scope from a selected G20 helper
trajectory to this explicit row-register side result. It supplies neither
a G20 target split nor a complete BIT moment. Native frames, physical
access, storage, tape movement, an actual caller and recursive charges
remain unknown. The selected PR6030 conditional kappa stays 0.003125804.
The source-binding baseline passed; its scientific cold replay was not run.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/fixed-weight-borrowed-tours/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/fixed-weight-borrowed-tours/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fixed-weight-borrowed-tours
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fixed-weight-borrowed-tours --check-source-history --check-modes
```

Another CPython 3.12 path may replace the displayed interpreter. The last
command requires committed package bytes and full Git history. Direct
verification also works in a Git-free export and writes no file. Its stdout
is a generated receipt bound to the SHA256 of all six package files.
Expected status is `PASS_FIXED_WEIGHT_BORROWED_TOURS_NO_NEW_KAPPA`.
Both registered modes use explicit guards that stay active under `-O`.

Exact evidence covers 90 layers and 8,190 required masks through n=12;
20 independent full-cube covering-walk optima through n=5; 132 complete
arbitrary-input circuits through n=8, with one to three targets per mask;
301,288 coefficient positions; 532 dirty-data cases, including 400
exhaustive one-bit states and 132 wide-row fixtures; and 132 inverse
executions. Eighteen rejection controls cover malformed domains, missing
masks, failed restoration, illegal gates, excess costs and an equal-length
semantic mutation. The 20 BFS runs discover 58,616 states in total, counting
each run's distinct state set separately. These finite checks corroborate
the written proof; they do not establish its unbounded quantifiers.

## Open next questions

1. Find a source-pinned caller that needs one complete fixed-weight parity
   layer at an aligned cut. Begin with the exact source and target demands,
   then price native frames, storage, references, routing and restoration.
   A caller is the missing link to a supplier consequence.
2. For a specified caller with unequal source prices and k>=3, determine
   its exact restored tariff. Begin with the small weighted covering-walk
   instance. The unweighted Gray listing is not asserted to be optimal
   for those prices. No physical price vector is supplied here.

The structured relevance, first steps and blockers are in [TASK.json](TASK.json).
Neither follow-on question is reserved by this contribution.

## Limits, overlap and implementation constraints

Base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361665)
preceded substantial work. Live open PRs, recent account contributions,
active Discussions, local target locks, main README terms and merged
fixed-weight/mask-tour searches were checked. Sparse local notes and
unpublished work limit overlap coverage; these searches do not establish
global literature priority. The package gives a self-contained proof.

The theorem requires exactly this one-anchor, one-write-per-target alphabet.
It is not an unrestricted CNOT minimum, a physical tape tariff, a native
implementation, supplier admission or a complete multiplication theorem.
Independent human and formal proof-kernel review are unclaimed. Lean,
Docker, full selected replay and all-size implementation checks were not run.

The verifier retains a deterministic constructor, an independent shortest-walk
oracle, full dirty coefficient-map checks and inverse execution.
Its eighteen functions are at most 38 physical lines. There is no subprocess,
network, dynamic code, callback dispatch or file-write path. Loops are bounded
by n<=12 for listings, n<=5 for BFS and n<=8 with multiplicity<=3 for circuits.
The BFS has at most 32,768 states, circuits at most 219 rows and 356 gates,
and receipts read six files with a 128-KiB limit each.

Power of Ten rule 3 deviation applies to `verify.py`: CPython allocates
managed integers and containers during execution. Fixed domains, explicit
state/circuit capacities and bounded receipt reads limit live collections;
this is not a fixed-allocation implementation. A fixed-allocation port
would be needed before embedded or real-time use. All remaining contracts
use explicit exceptions. Warning-strict normal and optimized replay plus
in-memory AST compilation provide the available interpreter diagnostics;
no external static analyzer or formal kernel was run.
