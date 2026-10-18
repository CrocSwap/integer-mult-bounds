# Joint numerical and count backing during native ADD

Freed numerical slots remain allocated while native ADD creates its countdown
tapes. This package proves a joint backing bound at those chronological cuts:

```text
joint cells <= K + N + max(C,H_C)

N = (max(H_R,L_R+max(J_R,6))+1)(b_R+2)
  + (max(H_I,L_I+J_I)+1)(b_I+2).
```

K counts all borrowed count backing, C is the native Counter maximum, and H_C
is callback count scratch released before return. H_R,H_I count already
allocated numerical slots, L_R,L_I count all entry live slots, and J_R,J_I
bound callback live-slot demands. The b values are digit widths. N includes
both numerical templates and erased slot arrays. [PROOF.md](PROOF.md) states
the exact source, canonical-entry, default-payload-factory, callback restoration
and no-capture hypotheses.

The complete modulus-five native ADD witness reaches **134 backing cells**,
although the largest simultaneous live-content bill is **114**. Warming the
same arenas before entry gives 536 backing cells with the same 114 live peak.
Erasure therefore does not justify a maximum of separate live-phase bills.
The formula is attained in these source fixtures; it is a conservative upper
bound for arbitrary callbacks satisfying the declared component contracts.

This joins the numerical and count categories of the released
[PR2916 handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/2916).
It does not repeat the existing callback/form liveness or Arena high-water
theorems. The entry boundary is `stream.add_pass` after extent preparation.
Other storage categories, preparation, actual selected callback admission,
physical placement/movement, total private A and recursive/outer reserve remain
outside this result. The selected frontier is unchanged; no new kappa is claimed.

## Evidence and reproduction

[RESULT.json](RESULT.json) records 41 complete unchanged-source ADD executions
and one additional successful capture counterexample. The fixtures cover all
25 basis inputs of the minimal fibre, nontrivial spectators, both suffix
branches, M=3,5,9, borrowed numerical residents, aliased count extents, warm
arenas and callback scratch in both categories. Every fixture checks the
complete output using an independent integer-address permutation, restored
borrowed bytes/ownership and source heads. The observer sums actual backing
array lengths and holds only weak references to count tapes.

Seven optimized test groups include a real 133-cell quota rejection paired
with the passing 134-cell run, warm history, borrowed residents, source
corruption, module/method restoration and typed receipt controls. Retaining
cleared callback count tapes gives correct ADD output but reaches 304 cells
against the released-case allowance of 216, so the no-capture premise is tested.

## Reproduce

From the repository root, with Python 3.12 and standard library only:

```sh
uv run --python 3.12 --no-project python -I -Werror -B \
  scripts/research_package.py --package research/selected-add-joint-backing
```

Direct `verify.py` compares a typed fixed receipt and writes nothing. Its
`--emit` option prints a fresh receipt. The registered replay also runs
`test_verify.py` under `-O`. [SOURCES.json](SOURCES.json) pins every consumed
source/proof input by Git blob and SHA256; all five executable source modules
authenticate before execution. Source compilation bypasses stale bytecode.

The quantified statement rests on the written source-lifetime argument, with
finite execution as corroboration. No complete selected GL64 payload, cold
supplier replay, capacity-prefix proof, arbitrary failure cleanup, formal kernel
or independent human proof is claimed. The separate read-only source review
checked the composition and its hypotheses. Hosted CI is a separate check.

## Engineering scope

Build the Lever led to the rerunnable joint census. Prove It Works led to
direct array measurements and complete ADD outputs. Test Behavior, Not
Implementation led to the insufficient quota and successful capture controls.
New functions are below 60 physical lines. Fixture extents are at most two,
payloads at most 1024 bits, arenas at most 64 slots and observed count inventories
at most 24 tapes. The observer rejects after 500,000 samples. Acceptance uses
errors that remain enabled under `-O`.

Power-of-ten deviations, rules 3/8/9: the Python checker dynamically allocates
host objects, compiles five authenticated predecessor modules under their fixed
import names and instruments fixed allocation/tape methods. Bounded fixtures,
explicit source inventories, private bytecode-free compilation, 120-second replay
timeouts and finally-based method/module restoration constrain these mechanisms.
The source-model array theorem does not assert fixed Python heap capacity.
Frozen predecessor loops remain unchanged and data-bounded by their admitted
word extents, finite fixture fibres and Euclidean descent. Revisit these
deviations when a physical compiler/allocator replaces the source-array model.
Ruff uses E4,E7,E9,F,I,UP,B,RUF diagnostics on new code; source snapshots are
not reformatted. [TASK.json](TASK.json) records the exact replay environment,
freshness and verification results.

## Open next questions

1. Join extent preparation and actual selected callback residents at the same
   entry boundary. Start from PR2912/2916 and the coefficient capacity-prefix
   result, then account for program/continuation backing without treating blank
   numerical slots as released. The missing caller inventory and other categories
   still block total private A.
2. Bind a complete backing ledger to the physical bank codec. Price slot and
   template placement, last-owner release, movement and erasure. This matters
   because a source-array bound alone does not establish a fixed-tape reserve;
   physical lowering and recursive/outer grants remain blockers.

Structured questions and feasible first steps are in [TASK.json](TASK.json).

## Credit

Nick Petalas, Apache-2.0. Jose Manuel/jmbarrancoml supplies the unchanged PR2697
implementation and retained source/control/hosting lineage. Its complete
[notice](../selected-adapter-caller-entry/vendor/NOTICE.md) is an unchanged pinned
input. Nick Petalas's PR2759 supplies primitive arithmetic scratch; PR2770/2778
and successors already establish callback/form liveness. Ross Richardson's
PR2825 supplies the caller numerical-envelope source export. PR2831 supplies
numerical retained-array history. Nick Petalas's PR2905/2912/2916 supply the
countdown, preparation and common-count-cut predecessors. This package adds
their numerical/count backing composition after preparation and the concrete
coexistence witnesses. No predecessor implementation is relabelled as new work.
