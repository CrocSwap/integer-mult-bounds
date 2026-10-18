# Physical C5 floors do not add through unrestricted termwise charging

Even granting cost 20 on all 23 physical C5s, a nonnegative weighted sum of
those floors with uniform termwise complete-plane rank charging cannot prove
a real global floor of 26 or an integer floor of 27. Its numerical floor is
at most 180/7. Uniform weights are limited to 4140/193 and cannot prove an
integer floor of 23.

This answers one proof-method question in PR3281's global-charging handoff.
It is not a global decoder lower or upper bound, an optimal charging
certificate, a supplier or a new kappa. Frozen inputs and the selected result
are unchanged.

[PROOF.md](PROOF.md) states the method and its limits. One full-support
rectangle costs nine globally but costs seven, eight or nine on each restricted
C5. The 23 restricted ranks sum to 193. Any valid termwise normalizer must
pay that overlap. The proof covers arbitrary nonnegative real weights.
Finite weight tests only corroborate its algebra.

A complete 114-term identity fit includes this rectangle as a cancelling
+J,-J pair. It costs 242 and is deliberately inefficient. It shows that the
rectangle can occur in a correct signed asymmetric fit, not that it occurs
in an optimal or cancellation-free fit.

## Evidence and reproduction

From the repository root, using standard-library CPython 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/c5-global-charging-ceiling
```

Direct commands also work from a Git-free committed package export:

```sh
python3.12 -Werror -I -B research/c5-global-charging-ceiling/verify.py
python3.12 -Werror -I -B research/c5-global-charging-ceiling/independent.py
python3.12 -Werror -I -O -B research/c5-global-charging-ceiling/test_verify.py
```

The primary reconstructs all 23 cycles with a bounded path census and packed
binary elimination, then compares the required RESULT.json. The separate
implementation checks all 3,819,816 five-subsets using dense elimination. It
also multiplies the two explicit scalar factor matrices and checks all 12,544
entries. It imports neither the primary nor predecessor code.

Nine behavioral groups check 1,330 finite weight vectors, integer seams,
complete-plane tariffs, both live inputs against both checkers, a wrong
cancellation sign, malformed domains, receipt corruption, missing receipts,
changed manifest pins and exclusive output creation. Default replay writes
nothing. `verify.py --emit-to NEW_PATH` creates a separate receipt and refuses
to overwrite an existing file.

[SOURCES.json](SOURCES.json) pins the only two live scientific inputs. Both
are already on canonical main `463113d675af7410ac91d53a4fed51ec6494eb9a`.
No pending PR Git object, solver or predecessor executable is needed.
TASK.json records the changed scope, priority revision 6 and overlap.
[CHECKS.json](CHECKS.json) records environments and unrun obligations.
The local cost20 papers motivate this audit but are not independently
admitted here. No selected cold replay, Lean, Docker, native program,
physical invoice or all-size theorem is supplied.

## Open next questions

1. Can simultaneous scalar coefficient or trace constraints across overlapping
   C5s give a stronger fit-level charge? Start with an explicit inequality
   relating different terms. The separate local floors omit that information.
2. Can optimal decompositions be restricted without losing signed asymmetric
   candidates? Prove a cost-preserving reduction before excluding cancelling
   pairs. The appended-pair fixture only certifies unrestricted admissibility.

The family decision is narrow and stop. Weight optimization or another local
cost20 replay alone does not justify a dependent construction round.

## Credit and implementation limits

Tekalign/PR2782 retained the physical inputs and quarter-weight experiment.
Cinna Davis/PR1825 supplied the matching; Adam Gall/PR1889 supplied the strict
mask. Sagar Thakrar/PR2484 and PR3256 supplied the core and arbitrary-term
weighted-rank/trace method. Nick Petalas/PR3248, PR3268, PR3271 and PR3279
supplied the asymmetric and residual follow-ups. Krzysztof Wójt/PR3281 supplied
the rational-separation proof and global-charging handoff. Retain Arham
Tahir/PR2879, PR3232, ctoth, Philippe Van Velzen and the E8/P112 lineage credited
by the unchanged predecessors. This contribution adds the aggregation ceiling,
not those local floors. Nick Petalas. Apache-2.0.

This is bounded research verification, not a fixed-memory tape algorithm.
Power-of-Ten rule 3 has a managed-Python deviation. Integers, JSON objects,
matrices and fixtures allocate dynamically. Authenticated compressed inputs
are capped at 32 KiB, decompressed data at 1 MiB, matrices at 112 rows/columns,
labels at nine bits, path storage at 200,000 entries and test subprocesses at
60 seconds. The separate census has exactly 3,819,816 iterations. Temporary
fixtures have scoped cleanup. Reassess these limits before changing sources.
Standard unittest dispatch and one fixed local-module load are the bounded
rule 9 deviation. No predecessor executable or dynamic plugin is loaded.
