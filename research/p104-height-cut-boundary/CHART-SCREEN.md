# A small chart-family screen beyond the frozen height/flag separator

The frozen first result is in `RESULT.md` and `verify_relaxation.py`; this
second, independent construction does not change it. Both are pinned to
PR #7852 head `41beda1d6435760dc99e38bd7e65f36798aad212`.

**Result.** We can add all arbitrary-chart **base** cuts and two actual-label
paired chart cuts to the first relaxation without increasing its exact
minimum above `D + R = 28`. This does not prove that any larger selected
family, or the full model, has the same minimum. In particular an adaptive
third paired cut explicitly fails in this witness: each direction has 57
crossings against a required 104. No full-model counterexample is claimed.

The base directed cut at a set of charts S is

```
# banks (src in S, dst outside S) >= # fields (A in S, B outside S).
```

The construction supplies every one of these inequalities simultaneously:
it assigns **each field** a two-bank path `A -> C -> B`, where every pair of
successive subspaces is nested. On any S, a path whose start is in S and end
is outside must have at least one outgoing bank. Summing over all 400 fields
proves the cut for every possible S, not merely for the singleton checks.

For an x-field use `span(q) -> plane_x(q) -> top`; for a y-field use
`bottom -> plane_y(q) -> ker(q)`. Both intermediate charts have dimension
2. The construction chooses each y-plane among the x-plane family and
checks actual F₂ containment against the pinned P104 labels. The 96 D ports
carry both copies of each field, the other eight carry one. Two up/down
one-dimensional flag moves at each level 2..8 satisfy the extra 14 ascent
and 14 descent flag crossings. All 1022 directed HS height cuts hold, as do
the nine ascent and nine descent flag inequalities. There are 828 bank
occurrences; total ascent 3214, descent 14, field climb 3200, hence `R=14`
and `D+R=28`.

Let P1 contain all 104 actual port lines plus `top`; let P2 contain P1 plus
all x-path intermediate planes. In each P, all x-field endpoint pairs lie
inside and all y-field endpoint pairs lie outside. Thus the pinned
height-stop paired-cut argument demands at least 104 extra crossings in
each direction. The explicit witness has 214 bank crossings in each
direction and no crossing field endpoint pairs, for P1 and for P2. The
script checks these counts and the endpoint conditions directly. These two
paired cuts therefore do not strengthen the 28 lower bound in the named
relaxation; 28 remains optimal by the flag-cut lower bound already shown.

The full model requires those paired inequalities for *every* qualifying
chart predicate. To identify the missing constraint, the checker also
constructs a third predicate by putting each dimension-2 intermediate on
whichever side minimizes its x/y path crossings. It retains all 104 x
endpoint pairs inside and all y endpoint pairs outside, yet has only
`(out,in)=(57,57)` with no crossing fields. The required extras are 104 in
each direction; this predicate excludes the witness. The finding shows
that adding the third cut would rule out this particular witness, not that
the relaxation optimum with that cut must rise above 28.

Reproduce from this directory with `python3 -S verify_chart_paths.py`;
`verify_chart_paths.log` records the result. The checker verifies the six
source SHA-256 pins, path containment and dimensions, exact port/flag
bookkeeping, 314 distinct singleton base cuts, all height/flag cuts, both
selected paired cuts, and the failing adaptive control. The all-subsets
base-cut claim follows analytically from the individually checked paths.
No scalar output matrix, nonzero-minor proof, legal chronological execution,
price invoice, crossing, or Lean replay is supplied.
