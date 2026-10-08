# Bounded carried-signal exchanges on PR71

This experiment composes Alejandro's PR70 carried-signal exchange method
with Chafik Boukhalfa's PR71 split-pair graph, schedules and next-use scoring.
It uses Rohan Arun's PR67 actual-profile oracle and Dominik Scholz's PR68
pending live controls, with all earlier compiler/graph credits inherited.
The composition and this note were prepared with substantial OpenAI Codex
assistance. All licenses and notices in the preserved baseline apply.

The graph and original compiler bytes are unchanged. The selected maximum
cardinality carry matching is modified by at most three deterministic passes
of strictly improving single-edge exchanges. A chosen edge `(g,u,i)` says
that region g preserves input coordinate i for exactly the later use u.
Before insertion, the desired output basis plus retained input unit rows is
checked for linear independence. Every use remains assigned at most once;
every exchange removes and inserts one edge. Thus the original invertible
region completion and fresh-use obligations remain applicable. All carried
signals still belong to the original eligible-edge list; containment and
scheduled later use are unchanged.

For edge `(g,u,i)`, let p be the source region of input i and t the target
region of u. With H(a,b) the exact fixed-basis profile entropy between frames,
the discovery price is

    -H(g,t) + H(g,full) + H(zero,p) + H(p,t).

The expression compares one carried route with a fresh producer copy and
cleanup route, up to constants common to all edges. H uses integer midpoint
logarithm enclosure weights scaled by 10^30. This first-order price is only
a discovery heuristic: live clearing decisions, retirement dependencies
and higher moments are resolved by compiling the resulting full word and
screening its actual complete paid transition profile. It is not a claim of
weighted-matching optimality or monotonic improvement of the final bound.

The unmodified PR71 compiler still synthesizes every row transformation as
literal XORs; the dirty wrapper remains M,J,M^-1,V,M,J,M^-1,V. The compiler's
full input/dirty basis replay in both orientations is performed on every
candidate. Independent serialized replay is reported separately. Every
promotion, cleanup, copied center and endpoint is included by the inherited
word-to-profile extractor; arbitrary dirty scratch is never assumed zero.

`screen.py` reconstructs events from literal operations, computes every
fixed-I+J transition profile with the inherited CRT profiler, checks exact
rank mass, builds the full 575-dimensional paid child list, and applies
PR71's directed rational moment/assembly arithmetic. Exact adjacent-grid
controls and all 47 strict inequalities / seven margins are included.

These are finite conditional witnesses. Ordered affine residual compilation,
all-size recursion, scalar overhead, routing, prime selection, exact recovery,
and fixed-tape/analytic transfer remain inherited theorem assumptions.
Arithmetic cutoffs are not full operational thresholds.
