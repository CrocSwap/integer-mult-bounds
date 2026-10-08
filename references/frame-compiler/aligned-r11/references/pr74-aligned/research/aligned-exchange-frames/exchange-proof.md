# Paid carried-signal exchanges

## Scope and provenance

The selected producer uses Chafik Boukhalfa's pinned PR #84 indexed engine,
with up to three single-edge and three two-edge exchange passes. The local
invariant proof below applies at every accepted exchange and hence through
all passes. Our independently developed one-pass reference implementation
is retained as `exchange_policy.py`; it is not the selected runtime engine.
PR #70, by Alejandro Zarzuelo Urdiales, supplied the carried-signal exchange
method, and Dominik Scholz's PR #76 supplied integer profile-entropy pricing.
This composition and its independent reference work were prepared for
Thomas DiFiore with substantial OpenAI Codex assistance. All inherited
contributors, source notices and licenses remain credited.

This is a finite construction argument. The inherited all-size compiler,
analytic, fixed-tape, precision, routing, prime-selection and recovery
hypotheses remain assumptions. The search is bounded and makes no claim of
minimum cost or global optimality.

## Matching invariant

Each eligible edge has the form `(g,u,i)`: region `g` carries its input
coordinate `i` to use `u`. The inherited graph builder supplies the entire
eligible edge list. Each edge already satisfies the required signal identity,
chronology and frame containment. The exchange policy selects edges from
that list and does not add an eligibility rule.

For region `g`, let `O_g` be the span over F2 of its independent desired
output rows. Let `C_g` contain the selected input unit rows carried out of
that region. The matching invariants are:

1. The rows consisting of a basis of `O_g` followed by `C_g` are independent.
2. Every use `u` is assigned to at most one selected edge.
3. The total number of selected edges equals the initial matching cardinality.

The function `can(e,drop)` recomputes the local binary basis after excluding
`drop`, when present, and checks independence of the new edge's unit row.
Removing a selected row from another region also preserves independence.

## One-edge exchanges

Consider an unselected edge `e=(g,u,i)`.

If `u` is assigned to edge `f`, the policy checks that adding `e` is locally
independent after removing `f` when both edges belong to `g`. When `f` belongs
to another region, it checks independence against the unchanged selected
rows at `g`. Replacing `f` by `e` preserves the assigned use and cardinality.
The donor region either has a checked replacement or loses a row.

If `u` is unassigned, the policy finds a selected edge `f` in the same region
such that the replacement passes the same independence check. Removing `f`
frees its use, and adding `e` assigns the previously free use `u`. Cardinality
and use uniqueness are again preserved.

Each accepted replacement strictly lowers the fixed integer discovery cost.
The selected implementation makes three deterministic passes.

## Two-edge cycles

Suppose the matching contains

- `z=(g,u_z,i_z)`, and
- `f=(g',u_f,i_f)`, with `g != g'`.

The policy considers eligible unselected edges

- `e=(g,u_f,i_e)`, and
- `w=(g',u_z,i_w)`.

It checks `can(e,z)` and `can(w,f)`, and requires
`price(e)+price(w) < price(z)+price(f)`.
The two local checks concern different regions. Replacing `{z,f}` with
`{e,w}` therefore preserves local independence in both regions. Every other
region is unchanged. The set of assigned uses is exactly the same, and two
selected edges replace two selected edges. Thus all three invariants hold.

The implementation removes both old edges before inserting either new edge.
It asserts use uniqueness during insertion, then checks total cardinality
and every region's complete output-plus-carried-row independence at the end.
Each pass is deterministic, with explicit integer and edge-ID tie breaking.
The selected engine stops after at most three passes, or an unchanged pass.
Three-edge cycles are outside the selected policy.

## Discovery pricing and final coordinates

The discovery oracle receives each region's core and cover after applying
the selected pricing permutation in `selection.json`. A separately recorded
final permutation can subsequently relabel the compiled word; its complete
profiles are recomputed. The oracle's integer weights are retained
from PR #76: bounded rational logarithms define reproducible approximations
to `t log(t)`. The fixed oracle profile of each eligible transition supplies
its score. Prices remain fixed during the bounded matching passes.

These prices choose among eligible matchings. Acceptance of the construction
uses the complete physical word and its independently reconstructed paid
profile. An improvement of a discovery score alone is insufficient evidence
for an exponent improvement.

## Literal implementation and paid cost

After matching, the inherited compiler constructs independent output rows,
selected carried unit rows, and an independent completion to a full basis.
Its binary elimination synthesizes that invertible basis change as literal
XORs at the common frame. All selected carrying, frame growth, copied
outputs, clearing controls and cleanup are represented in the resulting
word. Changing the matching does not remove any of these charges.

The complete word is checked on all ordinary-input and arbitrary-dirty
basis vectors in both orientations. Its literal frame transitions determine
the exact fixed-basis recursive child multiset. Copied centers, endpoint
copies, data growth, data blocks and the inherited complex costs are included
by the complete recurrence checker. The exponent is accepted only after
exact moment bounds and the full assembly checks pass.

## A strict profile-dominance criterion

A useful sufficient condition can be stated without a discovery score.
At fixed physical width, replace `q` size-1 children by `n_t` size-`t`
children, where every `t>1`, `n_t>=0`, and `sum(t*n_t)=q`. The rank is
unchanged. For any positive saving `a`, the replaced contribution to the
characteristic changes from a factor proportional to `q` to
`sum(t*n_t/t^a)`, which is strictly smaller when at least one child is added.
All unchanged paid terms cancel in this comparison.

As a checked example on the fixed PR #82 graphs at commit
`3410b940aa26e5876202152dfa7c4f66451ee22c`, the additional two-edge pass produced:

| Axis | Size-1 children removed | Larger children added |
| --- | ---: | --- |
| h23 | 147 | 63 of size 2; 7 of size 3 |
| h25 | 216 | 56 of size 2; 12 of size 3; 2 of size 7; 6 of size 9 |

Both ranks and role counts were unchanged, and both complete words passed
independent dirty replay and exact profiles. This establishes strict moment
improvement for every positive saving for that experiment. The selected
aligned graphs have their own separately checked complete costs.
