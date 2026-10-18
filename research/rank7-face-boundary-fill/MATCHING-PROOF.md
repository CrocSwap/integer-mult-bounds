# Exact boundary of a frozen-fill inverse-swap repair

Source: PR2979, commit `be191346391661f4d35fc0d1508d0a6029572576`.
Predecessor: PR2987, commit `02c3047a1e78e6e35e7573c12434ba26f6f9bd96`.
Both have separate attribution and remaining hypotheses. The predecessor's
necessary global condition `k >= 473` is an input, not a newly discovered cut.

## The changed construction choice

Keep the actual T37 call order, native provider dispatch, all 408 ordered helper
widths per call, and the source `k=1063` literal owner fill. Only perform the
following direct inverse move on two previously unused source bins:

```text
C=[8,8] at capacity16, D=[7,7,9,9] at capacity32
    -> C=[7,9], D=[7,8,8,9].
```

The two width-eight helper roles leave C. Choose one of D's two width-seven
roles and one of its two width-nine roles to move to C. Every role keeps its
original `(call,helper)` identity. Compact integer offsets are rebuilt within
the two bins. Each source bin participates in at most one move. This is the
**frozen-fill, disjoint, direct inverse-swap model**. Adaptive vacancy paths,
multi-bin cycles, changed source roles, and arbitrary new flows are outside it.

For a bin with source window `(L,U]`, every received role must have call time
`L < t <= U`. Its final occupants must have distinct call times. These are
necessary conditions for a direct move. In this source they are also sufficient:
all windows are disjoint from the active data family, and different child
windows naming one physical family have disjoint sets of legal call times.
Thus a received role cannot collide with a helper in a different child's bin
of the same physical family. Within a bin, distinct calls prevent collisions.
The independent checker proves these source invariants from the event schedule,
instead of assuming that separate bins always name separate families.

## The finite graph and exact optimum

Let C and D be the two vertex classes. The exact source has 1,386 C bins and
1,063 D bins. Join a pair precisely when at least one of the four possible
choices of D's displaced width-seven/width-nine roles satisfies all receiving
windows and distinct-call conditions above. Store one legal choice per edge.

The complete graph has **26,959 edges**. Its certificate contains:

* a matching with 123 edges, whose endpoints are all distinct; and
* a vertex cover consisting of seven C vertices and 116 D vertices.

The independent standard-library checker reconstructs every pair's eligibility,
checks that the stored graph contains exactly those pairs, validates each stored
role choice, and checks both certificates. Every matching edge needs a different
cover vertex, so every matching has at most `7+116=123` edges. The exhibited
matching attains that bound. This argument uses only the explicit finite graph;
it does not rely on a floating optimizer's infeasibility report.

Each inverse move reduces k by exactly one. Therefore the minimum k in this
restricted model is **`1063-123=940`**. Reaching `k=473` would require 590 direct
moves, which is impossible in this model. This is not a lower bound of 940 for
general chronological allocations. In particular, the predecessor's full
`473 <= k <= 1063` feasibility question is not decided by the matching bound.

## Literal realization and fully charged finite cost

The journal applies all 123 matching edges. Disjoint source bins and the source
family invariants make their local moves compose. The resulting literal fill
is nevertheless checked in full rather than accepted from that argument alone.
Every T37 helper role, ordered width, source window, integral mask, compact
prefix and physical-family exclusion is checked. The exact source interleaving
`(s,r,t) -> (s,r+37b,2t+b)`, `b in {0,1}`, gives a T74 fill and is also checked
in full against the source order and dispatch.

Every subset of the 123 journal entries also composes. Each entry changes
exactly its two distinct source bins: four roles change owner bins and offsets
are rebuilt within those bins. Distinct matching edges have disjoint bin and
role supports. Every receiving bin in a subset is
therefore either its valid frozen source state or its independently validated
exchanged state. The source family-window invariant excludes cross-child
same-call conflicts for every subset. Taking the first `1063-k` entries gives
an explicit chronological allocation for **every integer `940 <= k <= 1063`**.
This is a written finite-family construction from the certified journal, not
124 exhaustive full-geometry replays. Together with the predecessor's necessary
bound, it leaves `473 <= k <= 939` unresolved for general fills of this family.

The changing pattern multiplicities at `k=940` are:

| Capacity | Pattern | Count |
| --- | --- | ---: |
| 16 | `[8,8]` | 1,263 |
| 16 | `[7,9]` | 15,313 |
| 32 | `[7,8,8,9]` | 123 |
| 32 | `[7,7,9,9]` | 940 |

All other pattern counts are unchanged. Both bins in every direct move remain
full, with the same combined width inventory and capacity counts. Consequently
every residual rank count is unchanged. Together with the unchanged source
local profile this gives the complete T37 paid histogram

```text
{1:822840, 2:235098, 3:79734, 4:35964,
 5:6858, 8:2664, 48:14095}.
```

The T74 histogram is twice this vector. Hence the conditional recursive bill
`sum_r H[r] * tariff(r)` is exactly unchanged for every rank tariff, including
the inherited power tariff. This repairs placement without repaying the changed
native word's saving, but it improves neither the source profile nor its kappa.
The 408 helper names, eight centres, 91 private buffers and two guards remain
part of the source interface. The counts `896*T+509` are conditional namespace
counts, not a new physical-storage or machine-execution proof.

## Proof level and remaining implications

The maximum matching, complete graph coverage and literal geometry are finite
exact computations with explicit witnesses and rejecting controls. The
matching/cover bound and composition argument are written proofs for that
specified finite model, not formal-kernel proofs. The grouped-flow coloring
argument in `INDEPENDENT.md` describes a separate sufficient construction
interface; a time-limited search supplies no global impossibility theorem.

The native ordered widths and local paid profiles are source premises. Native
arbitrary-dirty-input arithmetic, phase/restoration, complete physical stock and
movement, precision/prefix/tape, consumer/outer admission and all-size/compiler
transfer remain separate. No supplier admission, selected-frontier update,
fractional-cap attainment or new kappa is claimed.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0. Credit
Dumitrean for PR2979's construction and face, Lu and the owner lineage for
flow/coloring, and all contributors retained in `NOTICE` and frozen sources.
