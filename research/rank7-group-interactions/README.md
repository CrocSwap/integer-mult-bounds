# Exact separation of PR2979's five frame-lowering groups

**Independent finite verification: all five groups change disjoint register
frame paths. Their local paid profiles and entrance-relative width inventories
add rank by rank for every one of the 32 group subsets, in both providers.**
This establishes local composability, not a complete physical invoice, supplier
admission, an improved κ, or the full multiplication theorem.

Base: `463113d675af7410ac91d53a4fed51ec6494eb9a`. Assignment seed **75** was
drawn with operating-system randomness, selecting independent verification.
The accepted conditional κ at this base is `0.001672660197076918` from #1094;
#2979's larger author claim remains separate. Its exact source head is
`be191346391661f4d35fc0d1508d0a6029572576`. The three consumed files are pinned
by SHA256 and Git blob in [SOURCES.json](SOURCES.json); the source construction,
earlier audits, task card and selected assembly are pinned as provenance.

## What this adds

Marius-Paul Dumitrean's #2979 reports five independent groups and pairwise
price additivity. Nick Petalas's #2993 already independently derives each
isolated rank-vector delta, all 16 V45 endpoint subsets, and the sum for the
whole stage. #3079 independently reconstructs the staged profiles. Those
results and the deltas below are credited predecessor work.

This check supplies a structural separation certificate and every mixed-group
case. It finds **92 affected registers, partitioned into disjoint sets of
26/17/17/16/16** for V45/A/B/C/D. Of each provider's **11,895** chronological
frame transitions (including zero-rank transitions), **366** depend on a group
and **11,529** are fixed. No
edge or register depends on two groups. The receipt records each register set,
all-edge digests, all 64 provider/subset profiles, and all 26 higher Boolean
finite differences per provider for each of the two inventories.

The checker uses intersections of orthogonal-character masks in F₂⁹. It imports
no producer, solver, previous auditor or predecessor arithmetic implementation.
This differs from the source's row reduction and the previous audits' explicit
primal-span closure. Both unchanged parent reports and the complete declared
stage-one report are reproduced as positive controls.
For a subspace U, the representation enumerates the characters vanishing on
every supplied generator. Nondegeneracy of the binary dot product gives
`dim(U)=9−log₂|Ann(U)|` and `U⊆V` iff `Ann(V)⊆Ann(U)`. Thus no numerical
rank tolerance or row-reduction pivot choice enters the check.

## Finite statement and proof

Let `G={V45,A,B,C,D}`. For `S⊆G`, apply precisely the gate-frame and helper-end
edits belonging to groups in S to the pinned parent. Group ownership of every
gate edit is derived from its unique containing rank-seven group space. All
139 old gate preimages and 22 old endpoints are checked. These are whole-group
choices; the partners are retained exactly as declared within each group.

Write `P(S)` for its vector of paid rank counts, including the fixed centre
COPY terms, and `I(S)` for the helper-width inventory relative to each helper's
actual entrance. Then

```text
P(S) = P(∅) + Σ[g∈S] (P({g}) − P(∅))
I(S) = I(∅) + Σ[g∈S] (I({g}) − I(∅)).
```

**Proof.** Every register has a fixed chronological list of gate, warp and
terminal-frame vertices. Stage one changes only vertex frame annotations,
each owned by one group. A charged climb is an edge between two adjacent
vertices; its child rank is their dimension difference. Fixed centre COPY
paths contribute fixed terms. The certificate shows that all changed vertices
on any one register belong to the same group. Consequently each register's
whole charged path, and every edge on that path, depends on at most one group.
Summing these disjoint contributions gives the first identity for every S.
The width is the terminal dimension minus the unchanged entrance dimension,
which gives the second identity. The checker verifies all warp/centre entry
equalities and monotone containments in all 32 settings, so these differences
are charged along legal paths under the inherited frame-accounting rules. ∎

This is an exact finite certificate plus a written implication, not a
proof-assistant theorem. In particular, the profile identity holds for **any
additive per-rank tariff**, without dependence on the search's integer price
rounding, a saving parameter, numerical root evaluation or surrogate break-even.

The already known isolated deltas are reproduced:

| Group | Paid-profile delta (`Hᵣ` = one rank-r child) | Width-inventory delta (`Iᵣ` = one width-r helper) |
| --- | --- | --- |
| V45 | `−2H₁+10H₂+6H₃−10H₄` | `4I₇−4I₈` |
| A | `−H₁+20H₂−14H₃+2H₄−2H₅` | `4I₆−3I₇−I₈` |
| B | `−H₁+20H₂−14H₃+2H₄−2H₅` | `4I₆−3I₇−I₈` |
| C | `20H₂−14H₃+2H₄−2H₅` | `4I₆−4I₇` |
| D | `20H₂−14H₃+2H₄−2H₅` | `4I₆−4I₇` |

## Reproduce and challenge the check

From the repository root, Python 3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/rank7-group-interactions
```

Expected: `PASS_RANK7_GROUP_INTERACTIONS`, five passing test methods, and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Direct read-only receipt comparison:

```sh
python3 -B research/rank7-group-interactions/verify.py
```

The primary replay takes about 1.3 seconds on the session's CPython 3.12.14
Linux host; this is a reproducibility estimate, not a performance improvement.
`--emit` outputs recomputed deterministic JSON without replacing the receipt.

Controls reject stale preimages, duplicated/omitted edits, a corrupted endpoint,
triple-only and full-set receipt changes, and nonmonotone paths. A small valid
two-group shared-register example has mixed difference `2H₁−H₂`, although all
four profiles have equal rank mass: rank mass alone cannot certify additivity.
The separation guard rejects it. A second fixture distinguishes disjoint
edges from the stronger disjoint-register statement. An explicit primal-span
oracle checks all 67 subspaces of F₂⁴ and all 4,489 containments against the
annihilator implementation. An optimized, isolated, Git-free export reproduces
the receipt from read-only files, then rejects corrupted source bytes.

## Scope and remaining costs

Only the local frame paths and entrance-relative inventories of **stage one**
are certified. Scalar and native operators, global phases, cleanup zero return,
physical owner embeddings, idle profiles, stock, precision/tape, both supplier
caps and outer/all-size transfer are outside this check. The source's frame
accounting is an explicit inherited cost model. A width inventory alone is not
an independently valid allocation or a proof that each subset improves a
complete recursive moment.

In particular, this does not contradict #3014's fixed-parent allocation
obstruction. No fixed parent or final allocation is silently assigned to these
32 variants, and no private buffer is removed from a complete invoice. Active
group-A native, peer-private return and V45 final-allocation audits were read
and excluded from this scope. It does not start another lowering census.

## Open next questions

Can one named subset's independently checked paths be joined to a legal
physical allocation and complete idle bill? Test the actual owner capacities
and chronology before evaluating its full moment. Wider endpoints from omitted
groups may require repacking. See [TASK.json](TASK.json) for the precise next
step and blockers, and the active allocation audits before taking that work.

## Credit and license

Marius-Paul Dumitrean / Dugongue supplied #2979 and #2942's construction and
literal words. Jeremy Kothe supplied the frame/cleanup lineage and #2957;
Mason Hale / #2917 and Jeremy Diviney / #2908 supplied the paired-extraction
lineage. Nick Petalas / #2993 and Gonzalo-Mier / #3079 supplied the earlier
independent isolated/staged frame evidence. Ross Richardson's #2987 and
Nick Petalas / #3014 supplied separate allocation evidence. Their original
notices retain the full geometry, native, compiler and ownership attribution.
No earlier delta or construction is claimed as new here.

Prepared for Charan (@theon199) with substantial OpenAI Codex assistance in
research, implementation, verification and writing. No independent human review
is claimed. Apache-2.0, following the repository license.
