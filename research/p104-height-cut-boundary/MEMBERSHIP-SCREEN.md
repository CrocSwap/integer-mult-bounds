# P104 label-membership chart cuts at X = 28

Source pin, main accounting and first relaxation are in `RESULT.md`; the
base-cut/path extension is in `CHART-SCREEN.md`. This is a third, separate
construction at PR #7852 head `41beda1d6435760dc99e38bd7e65f36798aad212`.

For every pinned P104 port label `q`, include the directed paired cuts for
the natural chart predicate `P_q(C) := q ∈ C`. Since each label is nonzero
and self-odd, exactly one of the 104 designated x row/partner pairs has
both x endpoints inside P_q and both y endpoints outside: the pair for q.
The two directed `dir_extras` inequalities therefore each demand one extra
bank crossing for P_q, over its respective field crossings. These 104
predicates are fixed by the labels; they do not depend on the witness.

**Result:** Adding all 104 such paired cuts, in both directions, to the
previous screen still leaves an exact minimum `D+R=28`. The checker supplies
an integer witness with `D=14, R=14`, so the lower bound follows again from
the nine pinned flag cuts and is attained. The witness also keeps all
arbitrary-chart base cuts, all 1022 directed height cuts, all 18 directed
flag inequalities, and the two paired chart controls described in
`CHART-SCREEN.md`.

The 400 actual-label fields each use the nested two-bank path of the prior
screen, so all base chart cuts follow by path telescoping. Replace its 28
one-level flag moves by these four additional nested banks:

```
    b1 = span(flag[0], flag[8])
    b2 = span(flag[0], flag[8] xor flag[1])
    b1 -> top, top -> b1, b2 -> top, top -> b2.
```

Each 2↔9 movement has length seven and crosses flag cuts 2..8, preserving
the exact seven-times-two ascent/descent flag extras. The planes intersect
in `span(flag[0])`, which contains no P104 label. For each q, at least one
of b1/b2 omits q; its upward and downward edge then supplies the necessary
paired crossings of P_q. This does not assume the wall or either 56 half.

An explicit adaptive paired chart cut still fails: `(bank out, bank in,
field out, field in)=(45,45,0,0)` where the full model requires 104 extra
crossings in each direction. Thus this 804-bank object is **not** a full
banked graph and cannot refute the legal-word wall. The output transfer
matrix, all paired-cut conditions, bank chronology, and a legal word remain
unconstructed. Its value is to identify another collection of necessary
cut projections that, even together, do not imply 112.

Replay from this directory: `python3 -S verify_membership.py`. It checks
all paths, actual label/flag data and six source SHA-256 pins, the 1022
height cuts, the 18 flag inequalities, the 104 paired cuts and both extra
paired controls. Output is recorded in `verify_membership.log`. No Lean
build or repository/GitHub mutation was performed.
