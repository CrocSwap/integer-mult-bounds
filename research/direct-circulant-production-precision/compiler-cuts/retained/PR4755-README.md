# Independent physical-cut audit of the full Toeplitz schedule

Prepared for Brian (`JoyboyBrian`) with substantial OpenAI Codex assistance.
Apache-2.0.

This package independently audits the **physical-cut factorization** in
[`FULL-PROOF.md`, §5](../rational-unitary-fft/FULL-PROOF.md). It proves the
trace identity for arbitrary legal atom schedules and strengthens its explicit
coverage to a cut after any subset of a matching gate layer. It binds that
argument to the retained scheduler, including asymmetric parallel children and
zero-duration identity calls. The result is an algebraic audit, not a new
conditioning estimate or a complete multiplication theorem.

Canonical investigation:
[Discussion #4202](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202#discussioncomment-19130763).
The starting handoff was the [independent universal-proof follow-up](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19076672).

## Exact claim and hypotheses

Fix a finite atom DAG. Each atom has a fixed wire support and an ordered
microprogram of invertible complex-linear gates supported on those wires.
Every program layer is a matching: its gates have disjoint supports. The
scheduler preserves each atom's local gate order; an atom starts only after
all predecessor atoms finish. Incomparable atoms have disjoint supports.
The endpoint of an atom with no layers is the identity. No numerical accuracy,
Toeplitz structure, positivity, real-coefficient assumption, or common child
length is required for the identities below.

The retained recursive DAG has an upper shear before both child programs,
each child internally ordered by the same rule, then a lower shear after both
children. Leaves have one scalar atom. Its incomparable atoms lie in disjoint
logical intervals, regardless of the physical names of their wires. This
establishes the support hypothesis by the first branch where their ancestral
paths differ. Calls on a common ancestor path are comparable.

Consider a physical cut after all layers before layer `k` and any subset of
layer `k`. Assign atoms using their source timestamps, before selecting that
subset:

* `I` contains atoms with `stop <= k`;
* `A` contains atoms with `start <= k < stop`;
* all other atoms remain unstarted.

An active fragment may consequently be empty or already contain the entire
atom's last matching layer. This convention avoids changing the atomic
partial order as disjoint gates in one layer are selected. A zero-duration
identity at source time `k` belongs to `I`, contributes no fragment, and still
satisfies all DAG dependencies. Its timestamp cannot be reassigned according
to an arbitrary display order of atoms. The final cut uses `k = depth`.

Both `I` and `I ∪ A` are downsets: every predecessor of a completed or active
atom is completed. Active atoms are incomparable, hence their supports are
disjoint. For each active atom `a`, write its stored endpoint as
`Â_a = T_a F_a`, where `F_a` is the executed fragment and `T_a` the unexecuted
fragment. Within a partial matching layer, selected gates can be moved before
unselected gates because those gates commute. Thus these are legitimate local
prefix/suffix operators in a suitable linearization of that layer.

Let `Q̂(I)` be the product of completed stored endpoints in any topological
order. Let `R̂` be the product of unstarted endpoints in a topological order
after `I ∪ A`. Products act on column vectors, so the latest gate multiplies
on the left. Then the **exact** physical operators obey

```
C_prefix = F Q̂(I),       C_suffix = R̂ T,
F = ⊕_{a ∈ A} F_a ⊕ I,  T = ⊕_{a ∈ A} T_a ⊕ I.
```

Here the final identity block acts on unused wires. This includes arbitrary
interleavings of independent child programs, not just the one zip-by-layer
schedule used in the executable fixtures.

## Proof by legal adjacent swaps

Regard the physical gate sequence as a word tagged by atom ownership. To
collect the executed part of an active atom after all completed atoms, move
its gates rightward in chronological order past completed-atom gates that
occur later. Such a completed atom cannot be a predecessor (it would have
finished before the active atom started) or a successor (it could not yet
have completed). It is incomparable, so its entire support is disjoint from
the active atom's support. Every required adjacent swap therefore commutes.
Distinct active fragments also commute. No same-atom gates are reversed.
The remaining executed gates are precisely whole completed atoms; any
interleavings of those atoms can be collected into a topological endpoint
product by the same disjoint-support swaps. This proves `C_prefix = F Q̂(I)`.

For the suffix, move each active tail earlier in chronological order past
any preceding unstarted-atom gate. That other atom cannot be a predecessor
of the active atom (all predecessors are in `I`) or a successor (a successor
cannot start before the tail ends), hence again is incomparable. Collecting
the active tails first and the whole remaining atoms afterward yields
`C_suffix = R̂ T`. The argument uses only bilinearity of matrix multiplication
and disjoint support, and is valid over the complex numbers without conjugate
transposes. Inversion gives, in the essential reversed order,

```
C_prefix^-1 = Q̂(I)^-1 F^-1,
C_suffix^-1 = T^-1 R̂^-1.
```

The proof also explains why simply swapping overlapping factors, or treating
a completed atom as active according to a count of its emitted gates, is not
a valid substitute for the source schedule and DAG.

## What the identity does and does not imply for norms

For the Euclidean operator norm, a direct sum contributes the maximum norm
of its blocks. Thus, **if** all completed/remaining endpoint products and
all relevant local fragments and inverse fragments have stated bounds, the
four physical prefix/suffix bounds follow by multiplication of one endpoint
bound and one maximum fragment bound. There is no factor for the number of
active atoms and no assumption that sibling macro boundaries align.

The polynomial completed-downset estimate `256 N^3 (ΛQ)^12`, perturbation
budget, generator/scalar fragment bounds, and rounded execution theorem are
already supplied by the predecessor. They are not proved anew here. In
particular, extending the *algebraic* identity to a partial matching layer
does not silently extend a child's *numerical* bound if that child bound was
proved only at complete layer boundaries. Establishing the matching-layer
fragment norm contract is a separate open obligation. No selected κ, width,
physical delivery tariff, or accepted frontier changes.

## Executable source binding and independent controls

`verify.py` executes the unchanged AST definitions `full_plan`, `parallel`,
and `inverse` from Vlado's retained `check_circuits.py`, plus `Plan` and
`Full.parallel` from the rational implementation. Its synthetic callbacks use
independent exact Gaussian-rational matrix multiplication and elimination,
noncommuting microsteps, unequal atom lengths, and reversed physical wire
order. They are structural tests, not substitutes for the actual FFT.

One additional `N=2` complex Toeplitz fixture invokes the actual `Full` factory
and its actual rational primitive gates. The oracle reads atom timestamps,
local plans and supports, then independently constructs predecessors and
multiplies both sides of both identities at every enumerated cut. It does
not import `frontier.py` or any predecessor verifier. The pure exact scalar
representation is shared; the matrix multiplication, elimination, cut
classification, ownership checks and factorization comparisons are local.
All live source dependencies, including this single actual factory's closure,
are pinned in `SOURCES.json` and declared in `VERIFY.json`.

The five bounded fixtures cover **191 cuts**, including **64 proper partial
matching-layer cuts**, complex scalars, a zero-shear identity tree, simultaneous
nonempty fragments, unequal siblings and one actual source factory. Four
controls reject a shifted atom timestamp, a delayed zero-duration predecessor,
an incorrect prefix multiplication order, and an incorrect inverse order.
Finite coverage tests implementation binding; the quantified theorem is the
trace argument above. Python `-O` is registered separately and no audit check
uses `assert`.

## Sources, overlap and reproduction

The base is `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51` (priority revision 7).
The full compiler/proof last changed at
`7ab1bc8973cc9e606053c65f094ca3abc4a42fee`; archive PR #4253 preserves the
original #4205 head `78c72e563173f3822fcb4efed9ceeccf05630258`.
Credit Jose Manuel for the rational compiler and physical-cut claim, Vlado
for the recursive scheduler, and the cited retained interval/Stein producers
for the actual primitive factory. ToikY's #4209 same-ρ Schur audit and #4220
scalar Gaussian audit are distinct predecessors. The #4731/#4737 parity
macro-cut bounds do not cover this full Toeplitz physical fragment interface.

The shared fresh overlap snapshot contained 506 open PRs, 3650 discussion
records and 5860 local notes at 2026-10-22 18:50 UTC. Focused terms were
physical cut, active fragment, full Toeplitz and uniform cap; live #4202 was
also read. The active tensor/raw-H work is excluded. Coverage is an overlap
check, not a novelty proof or independent scientific acceptance.

```
python3 scripts/research_package.py --package research/full-toeplitz-cut-audit --check-only
python3.12 scripts/research_package.py --package research/full-toeplitz-cut-audit
python3 -B scripts/check_research_commit.py --package research/full-toeplitz-cut-audit --check-source-history
```

The registered replay runs normal and optimized Python 3.12, standard library
only. The final command must be run after committing the package. No full FFT
historical suite, Lean build, Docker run or complete multiplication replay is
claimed.

## Open next questions

Can each actual generator/FFT child's existing four fragment bounds be extended
to **arbitrary subsets of a matching layer**, with its stated constants? First
inspect the elementary matching gates and prove the direct-sum bound for the
unfinished layer before composing the preceding local prefix. This matters
only if an application actually needs sublayer physical cuts; the present
algebraic strengthening does not establish that numerical contract. The
required child norm argument, not a larger finite census, is the next step.
