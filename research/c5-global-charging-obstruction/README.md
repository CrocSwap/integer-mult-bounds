# A ceiling for direct global charging of the physical C5 floors

Even granting cost 20 on every one of the 23 physical C5s, a universal fixed
nonnegative weighted sum of their restricted tariffs can certify a raw global
cost bound of at most **180/7**, less than 26. Final integer rounding can yield
at most 26. This is a necessary ceiling on one proof method, with no claim that
the ceiling is attainable. It is not a bound on the actual decoder optimum.

The all-support term costs 9 globally. Its C5 restrictions cost 7 on four cycles,
8 on six and 9 on thirteen. Consequently every universally dominated positive
weight vector has sum at most 9/7. The unweighted local sum would charge 193
against 9 for that one term. [PROOF.md](PROOF.md) supplies the argument and two
complete exact strict fits containing the term. Neither fit is a cheaper decoder.
[RESULT.json](RESULT.json) lists every actual cycle and rank.

This answers the direct restriction part of the global-charging handoff after
[PR3281](https://github.com/CrocSwap/integer-mult-bounds/pull/3281) and
[PR3279](https://github.com/CrocSwap/integer-mult-bounds/pull/3279).
All local 20 theorems are granted, not replayed or claimed anew. Native programs,
suppliers, selected results and kappa are unchanged. Signed or coefficient-sensitive
completed-fit arguments remain outside the theorem.

## Reproduce

Python 3.12+, standard library. From the repository root:

```sh
python3.12 -I -W error -B scripts/research_package.py --package research/c5-global-charging-obstruction
```

The three direct export commands are:

```sh
python3.12 -I -W error -B research/c5-global-charging-obstruction/verify.py
python3.12 -I -W error -B research/c5-global-charging-obstruction/independent_check.py
python3.12 -I -O -W error -B research/c5-global-charging-obstruction/test_package.py
```

Expected primary output starts `PASS_C5_GLOBAL_CHARGING` with ceiling 180/7.
The independent checker uses dense binary elimination, iterative chordless paths
and a different signed Gram identity extension. The primary checker uses packed
elimination, neighbor-set cycle construction and an asymmetric identity extension.
They share only input authentication. Seven controls cover admissibility, the
invalid unweighted sum, false large raw certificate objectives, malformed ranks,
source reclassification/inventory changes, digest corruption and actual input
corruption. Checks remain enabled under optimization.

Both scientific inputs are canonical-main files already retained by PR2782.
SOURCES.json binds the exact four-path inventory and input/provenance roles,
SHA256 and Git blobs. The registered runner checks historical task/selected
provenance. Direct Git-free replay authenticates both live scientific inputs;
it does not independently authenticate historical Git provenance. No pending-PR
Git objects or predecessor executable modules are needed. The local 20 proofs
are cited context and are not mathematical inputs to the ceiling theorem.

## Evidence and engineering limits

CHECKS.json records actual replay, committed export and environment evidence.
The reviewed scientific files remain stable when a separate peer receipt is added.
Internal computational review is not human or proof-kernel approval. No selected
cold replay, Lean, Docker or full supplier audit is run for this implication.

Separate Before Serializing Shared State led to a worker-owned package, cache
and branch, with short OS locks only for shared Git metadata and reservation.
Prove It Works led to the actual committed read-only Git-free export and explicit
identity extensions. Power of Ten inspection uses no recursion and functions
below 60 lines. Loops are bounded by 112 labels, 56 planes, five-vertex paths and a
100,000 path cap; source reads and decompression are bounded at 2 MB. Python's dynamic
allocation is a documented managed-runtime deviation, limited by those domains.
The separately parsed authenticated compressed payload has the same pinned finite
size. Source errors propagate, temporary controls use scoped cleanup and no
assertions disappear under optimization. The current fixed inputs determine all
numeric results; runtime measurements are not part of the claim.

## Open next questions

Can a coefficient-sensitive completed-fit charging inequality escape the
individual-term obstruction? This matters because fixed positive restriction
aggregation cannot prove a large global floor. First state one explicit
cancellation identity and test it on both strict identity extensions in PROOF.md.
No such inequality, cheap decoder or complete physical consumer is supplied here.
[TASK.json](TASK.json) retains the question and exact scope change. This session
stops after the scoped obstruction; no dependent construction round is reserved.

## Sources and credit

Base 463113d675af7410ac91d53a4fed51ec6494eb9a, priority revision 6.
The immediate source heads are PR3281 a3a7306c15c7da541e4b586fdb642e2855fc2956
and PR3279 67c1360a7a6e81bcac515c698d56656454340b10. They motivate the question
and receive credit without an executable dependency. Credit Krzysztof Wojt,
thakrarsagar/PR3256/3232, Nick Petalas/PR3268/3279, Tekalign/PR2782,
Arham Tahir/PR2879, Sagar Thakrar/PR2484, Cinna Davis/PR1825, Adam Gall/PR1889,
ctoth, Philippe Van Velzen and the retained E8/P112 supplier/geometry lineage.
The original local floors are predecessor results. Apache-2.0.
