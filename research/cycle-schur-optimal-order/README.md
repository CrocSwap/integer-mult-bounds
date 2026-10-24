# Exact optimal ordering after a circular arc is eliminated

**Scoped proof with finite corroboration.** For a full negative circular band
of radius w, eliminate one nonempty proper arc and retain M vertices. The
exact minimum Schur half-bandwidth over simultaneous row/column orders is

    min(M-1, 2w).

The order `0, M-1, 1, M-2, ...` attains it. In the resulting support graph,
the minimum degree gives the matching lower bound. With M=9 and w=2, this
changes the inherited linear survivor bandwidth from eight to four. No
ordering reaches three. For arbitrary coefficients supported on the same
circular band and any invertible arc pivot, the same order gives the upper
bound; cancellations can reduce the optimum.

This answers the survivor-reordering question left open by James Reed /
jwr404's [PR #4289](https://github.com/CrocSwap/integer-mult-bounds/pull/4289).
The new contribution is an optimal linear order and its sharp constant.
The predecessor's sign/no-cancellation argument is a credited premise, not a
validation deliverable. [PROOF.md](PROOF.md) gives the complete all-size
argument and precise negative-host hypotheses. No predecessor executable is
imported or replayed. No literature-priority claim is made for path folding
or the elementary minimum-degree bandwidth bound.

## Evidence and reproduction

From the repository root, CPython 3.12, standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cycle-schur-optimal-order
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/cycle-schur-optimal-order/verify.py
```

On another checkout, substitute its Python 3.12 interpreter. Both registered
commands, warning-strict normal and optimized execution, emit
`PASS_CYCLE_SCHUR_OPTIMAL_ORDER`. Normal verification writes no files. Each
execution prints a generated receipt with SHA256 hashes of all six package
files. `verify.py --write-receipt NEW_PATH` additionally writes it to a new
external path and refuses overwrite. No hand-written receipt is committed.
The direct verifier is self-contained and works without Git or repository
inputs. Generic metadata/source-history checks require the pinned Git history.

The bounded checks enumerate:

- 4,656 graph/radius pairs through M=96, including 8,403,952 edge occurrences,
  checking the folded order and exact minimum-degree floor.
- All 362,879 vertex permutations for all 36 graph/radius pairs through M=8.
  This separate direct evaluator uses no folded-order or degree-bound pruning.
- 651 circular layouts through n=16, one representative for each radius and
  eliminated-arc length. Literal graph vertex elimination independently checks
  the new path-power-plus-end-clique support identification and folded order.
- Nine invalid-input rejections and four semantic controls for the old order,
  an incorrect `2w-1` cap, omitted clique fill, and saturation at M-1.

These are finite corroboration of the new theorem. No numeric matrix census,
predecessor reproduction, physical schedule, benchmark or full selected replay
is claimed. The all-size claim rests on the written proof. The selected
conditional kappa remains 0.00302015.

## Scope and source closure

The negative host is H=I-E with zero diagonal in E, strictly positive entries
at every circular distance from one through w, zero entries elsewhere, and
row sums less than one. This guarantees connected positive inverse fill and
prevents cancellation. Arbitrary invertible arc pivots need only the stated
support condition for the upper bound. Signed or missing couplings do not
inherit the sharp lower bound.

The original `uniform-transfer-audit` card is explicitly changed to this
ordering theorem, following another contributor's open question. It is a local
interface result, not an audit of #4100. Physical row and right-hand-side
permutations, routing, restoration, multiple arcs, inverse norms, precision,
tape access, compiler/hosting and complete supplier costs remain open. No
supplier admission, new kappa or complete multiplication theorem is supplied.
Independent human and formal proof-kernel review are unclaimed.

Base canonical main is `624de9dc66858af0945e5f8a0942488d62280d43`, priority
revision 7. [SOURCES.json](SOURCES.json) pins historical task/selected provenance
and the exact credited predecessor notes. No external executable or data input
is required by the new verifier. The selected-source metadata orientation
passed; it was not the selected scientific cold replay.

Entry overlap used live open PRs, this account's recent submissions, current
handoffs, local question locks, distinctive all-main README searches and merged
PR searches. The cached card scan reported sparse-note omissions. Arbitrary
diffs and unpublished work remain outside coverage; no-match searches do not
establish novelty. [The claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19134026)
preceded the substantive work. Research stops at this first proved result.

## Verification design

Build the Lever led to a rerunnable ordering and exhaustive optimum checker.
Prove It Works led to independent direct permutation evaluation and literal
circular graph elimination. Power of Ten bounds graph size at 96 vertices,
permutation enumeration at eight, and circular elimination at sixteen. Every
loop has a bound from those constants; functions remain below 60 lines;
rejection checks remain active under optimization. Python's managed allocation
is a documented deviation from fixed allocation: one graph has at most 4,560
edge tuples, the literal adjacency table has at most 256 booleans, and brute
orders are streamed. Package source files are fixed local inputs. Python's
allocator and standard-library internals are outside inspection. There is no
recursion, dynamic code generation, shared mutable state or native dependency.
Warning-strict Python and the repository metadata/publication checks are the
available diagnostics; no separate linter is installed in the supplied venv.

## Open next questions

Can the folded order be realized in one actual circular Gaussian boundary
solve within its complete paid routing allowance? First bind both permutation
directions, all right-hand sides and eventual restoration in a literal caller.
This matters because a smaller algebraic band does not pay for moving data.
No physical conversion or complete caller is constructed here.

Which multiple-arc elimination layouts retain an O(w) optimal linear bandwidth?
First specify a separation rule and derive the survivor support. This matters
because merged eliminated components can create larger cliques. The present
one-arc theorem does not decide that case. Structured versions of both questions
are in [TASK.json](TASK.json).

## Credit

This contribution is produced by Nick Petalas. James Reed / jwr404's #4289,
following #4286, supplies the circular-arc sign/support argument and the explicit
open reordering question. Cinna Davis's #4100 supplies the Gaussian boundary
motivation. unpaidmoon's #4373 and Ryanson Jonathan's #4407 address linear
separated carves and support fill; their `2w-1` constant has different
hypotheses. Their source files and credit lines are unchanged. Apache-2.0.
