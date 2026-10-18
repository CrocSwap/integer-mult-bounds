# Proof and exact scope

Work over F2. Write the 120 target registers as y and the 420 arbitrary helper
registers as s. The pinned D matrix K has 120 rows and 420 columns. Its original
implementation adds each nonzero coefficient separately, for |K| = 19,922 XORs.
All sources, targets and helpers are independent symbolic inputs; source rows
are not read by this replacement.

## Rooted-forest identity, including restoration

Fix a forest on the target vertices, orienting every component away from one
root. For a nonroot t with parent p(t), prepare `y_t <- y_t + y_p(t)` in decreasing
depth order. Since a parent has not yet been changed when its child executes,
the prepared target vector is Py, where row t of P is e_t+e_p(t) for nonroots
and e_t for roots. The product of these elementary transvections is invertible.
The reversed preparation stream is its inverse over F2.

At target t add `(K_t+K_p(t))s` for a nonroot, and `K_t s` for a root. This adds
PKs in the prepared basis. Apply the reversed preparation stream:

`P^-1 (Py + PKs) = y + Ks`.

Sources and helpers have not changed at any time in D. This identity holds for
arbitrary original y and s. In particular, preparation cannot be omitted merely
because the zero-target case seems correct. All gates act on existing frame-zero
target/helper registers. No descent, new frame, extra helper, source read, copy,
or recursive child is introduced. Both the preparation and its inverse are
included in the invoice.

Replacing D by this operator leaves the input to A identical to the original
word, on every input column. Thus the unchanged A/scatter/B/C program retains its
full dirty-restored endpoint. Its original literal H2 syntax and literal K
extractor are insufficient to recognize this implementation; the sufficient
semantic contract is the full D endpoint just proved. The rest of the scalar
interface is inherited without alteration. Same-frame target XOR operations
use the original common-label conditional realization.

## Exact optimal scalar cost within this class

A forest F implemented by the preceding recipe costs

`C(F) = sum_roots |K_t| + sum_nonroots (|K_t XOR K_p(t)| + 2)`.

The two units per forest edge are its preparation and restoration. This defines
the scoped class: one parent-difference helper row per target and no additional
factoring among those rows. More general target bases, helper bases, shared
helper expressions, cycles or arbitrary reversible circuits are outside it.

Add a vertex z with K_z = 0. Give each edge z--t weight |K_t| and each target
edge u--v weight |K_u XOR K_v|+2. Joining every component root to z maps a rooted
forest to a spanning tree of the 121-vertex graph, at identical cost. Conversely,
removing z from any spanning tree and orienting away from its neighbors gives a
rooted forest with the same invoice. Therefore the exact class minimum is the
minimum-spanning-tree weight.

`RECIPE.json:minimum_parents` specifies an attaining tree. The verifier checks
its connectivity and acyclicity and all 7,260 pair inequalities

`w(u,v) >= max { w(e) : e lies on the tree path u to v }`.

These inequalities are sufficient for minimality. To transform an arbitrary
spanning tree S into the proposed tree T, add an edge e of T absent from S and
consider its fundamental cut in T. The cycle in S+e contains an edge f of S not
in T crossing that cut. The T-path of f contains e, so the verified inequality
gives w(f) >= w(e). Replacing f by e does not increase cost and increases the
number of shared edges. Repeating reaches T. Thus no S costs less than T.
The verified sum is **14,921**, yielding the exact unconstrained saving ceiling
**19,922 - 14,921 = 5,001** within this recipe class. The separate Prim
implementation confirms the same integer minimum without using this certificate
checker or the nomination algorithm.

## Precision-limited submitted construction

The certificate above concerns scalar counts; it contains no precision premise.
The best reverse-bound tree among 256 nominated minimum-cost trees needs 106
payload bits under the inherited bound. This is a failed budget check on those
nominations, **not a proof that every optimum tree fails**.

Deleting eight target edges, making their children roots, gives the submitted
forest. Its 12 roots and 108 edges cost 14,922 helper XORs plus 216 target XORs,
or **15,138** total. No precision-constrained optimality is asserted. The
complete scalar stream costs **22,132**, a reduction of **4,784** from 26,916.

The actual exported stream is used to recompute both positive prefix envelopes:
initialize every local row bound to one; ADD replaces L_d by L_d+|c|L_s;
COPY opens a temporary with its source bound; ERASE closes it. Reverse traversal
interchanges COPY and ERASE. This is an entrywise triangle-inequality bound for
the signed lift, independently of F2 cancellations. The largest forward and
reverse bounds are respectively **144,651** and **9,640,706**. The inherited
local invoice is therefore

`64 * 144651^3 * 9640706^2 = 18003708514079901815901709480704 < 2^104`.

The unchanged C++ checker independently verifies this bound. The nominated
minimum-cost tree fails that same native budget check. Missing target restoration
fails the native full-column check at five, nine and eleven stages.

No gate outside D changes. All D gates remain at frame zero. Consequently every
frame transition, COPY and ERASE is identical to the source. Exact comparison of
the entire exported non-ADD subsequence checks this directly, including source
and helper endpoints. The paid histogram remains
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`, with rank mass **5,112**.

This proves a finite F2 circuit identity, a forest-class scalar floor, and the
stated local invoices. It does not prove a new κ, a precision-constrained
optimum, equality of the signed integer endpoint, or the uniform/physical/tape/
analytic hypotheses of integer multiplication. Global hosting and invoice
integration remain separate obligations; an increased local prefix must not
silently inherit an old global receipt.

Oscar Fennell, with substantial OpenAI Codex assistance; Apache-2.0. Predecessor
credit and exact source pins are in README.md and SOURCES.json.
