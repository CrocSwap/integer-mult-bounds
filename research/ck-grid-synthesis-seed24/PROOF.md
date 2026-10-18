# Finite class, complete cost and inherited prefix bounds

The source and target are distinct and never written during preparation.
Private work may be arbitrarily dirty. For reduced `|q|=a/D`, where `D` is a
power of two, the searched word has one initial COPY, an arbitrary finite
preparation, one target ADD/SUB, and one final CLEAR. Preparation may use
unit source ADD/SUB, DOUBLE, HALF, NEGATE, COPY and CLEAR on work only, while
its coefficient remains in `D^-1 Z` and has absolute value at most `a`.
The unit macro's cheaper direct two-instruction lowering is outside this
mandatory-copy form and is retained.

Write `W=(x/D)S`. Every admissible preparation is exactly a walk on the full
integer vertex set `[-aD,aD]`, starting at `D` and ending at either `a` or `-a`.
The unit-cost transitions are `x+D`, `x-D`, `2x`, `-x`, `0`, `D`, and `x/2`
when `x` is even; only destinations in the vertex set are admitted. This
describes all words of arbitrary length in this class. Any repeated-state
cycle can be removed without increasing cost. The three instructions outside
the walk are all paid, giving complete cost `3+min(d(a),d(-a))`.

The construction uses breadth-first search from `D`. A separately implemented
synchronous Bellman recurrence rebuilds every label. Every edge `x -> y`
satisfies `d(y)<=d(x)+1`; telescoping from `d(D)=0` lower-bounds every path's
length by its endpoint label. Every noninitial vertex has an attaining
predecessor, and the submitted witness explicitly attains the lesser goal
label. These exact obligations prove optimality in the declared finite graph.
They do not prove optimality with extra registers, changed source/target,
multiple target updates, different initialization, a finer grid, a larger
envelope, macro reuse or physical tape instructions. The frozen inventory
from both CK programs is compared to all 103 certificate records.

After COPY, induction gives `W=(x/D)S` for arbitrary inputs. Adjusting the
target accumulation sign for the witness's terminal sign produces exactly
`T+qS`, with unchanged `S`; CLEAR leaves zero work. Testing all three formal
columns establishes the entire linear map, including dirty work and
correlated inputs. Applying the real-coefficient identity to each complex
component proves the same complex boundary map. Substitution at every
original macro boundary preserves subsequent states by induction. Paid
events, frames and recursive children are retained, rather than commuted or
omitted. The scalar projection does not execute physical frame operators.

The original binary preparation reaches `aS` before terminal halvings. Every
candidate prefix has `|W|<=a|S|`, so its work magnitude and row-L1 norm are
bounded by that original attained state. Source and target values before
and after the single update, initial private dirt and final zero also match
the original boundary values. This proves maximum-row/prefix domination;
it does not claim literal prefix containment or entrywise domination of
simultaneous transfer matrices. The verifier separately reconstructs the
original nonnegative Horner envelope from every event and matches the pinned
independent receipt: `920709848294` forward and
`146068000389976309073/32` backward, within the retained 192-bit allowance.
Candidate macro checks certify the local bound used in this substitution
argument, and complete sparse primitive replay certifies both endpoints.

For fractional depth, a prefix work coefficient is `x*s_j/D` for each source
row coefficient `s_j`. If `D>1`, reduced `a` is odd, so its denominator depth
is no larger than that of the original attained terminal coefficient
`a*s_j/D`. For `D=1` the multiplier is integral, so the original leading
source state already bounds its denominator depth. All other register states
are unchanged at boundaries. Thus these substitutions need no finer scalar
prefix grid than original/copy binary Horner. This is not a full physical
rounding, overflow, tape or compiler precision certificate.

The net saving against PR837 is a complete instruction recount, including
cost increases at some coefficients. It is not obtained by summing only
strict improvements. More source additions can replace shifts, and each is
charged; no physical memory-traffic or runtime inference follows. Paid ranks
and assembly choices stay fixed, so these finite circuits give no new kappa.
Inherited all-size and physical interfaces remain assumptions, and finite
graph/column verification is not a formal multiplication theorem proof.
