# Independent review of the fixed-root block-carrier model

Reviewer: OpenAI GPT-6 Astra Pro research subagent A, working for @CubeJerry.
Review date: 2026-11-07. The author's implementation was read to establish its
claim but was neither imported nor executed by the independent geometry replay.
This review does not change the frozen `research/noidle-root-defect` contribution.

## Verdict

**PASS for the stated fixed-root, sector-independent projector-carrier model.**
The independent eigenspace computation agrees with all **13,851** capacities
(171 intervals in each of 81 dense central mask cases). A separate exact audit
of all 13,851 dual inequalities, using those independently computed capacities
and the reviewer's previously written rational power bounds, proves every case
has negative complete moment at the actual headline `κ=0.00337180`. The weakest
certified upper bound is the central two-site mask `(8,9)`, strictly below
`−42.13044026865099`.

This eighty-one-case result is a **fixed-benchmark** obstruction. These dual
certificates alone do not rule out a hypothetical later positive moment interval
at a larger κ; such a global ceiling needs its own monotonicity argument.
The separate full-span concavity result may have a wider exponent domain.

The eighteen-dimensional quotient is an algebraic lead, not an admitted
productive caller. Raw compression of every native active rank-two projector
fails idempotence. A rank-one correction repairs each projector locally, so
this failure must not be presented as general quotient impossibility. The
repaired first two projectors have a rank-two commutator; a simultaneous
whole-target interface and its complete invoice remain unproved.

## 1. Bridge covariance

Write the coordinates as `A,f_0,...,f_8,h_0,...,h_8,E`. Define

\[
F=\sum f_j,\quad H=\sum h_j,\quad u=F+H,\quad v=A+F-H,
\]

\[
z=-A^*+\sum(-1)^j f_j^*-\sum(-1)^j h_j^*,\qquad
w=2A^*-\sum(-1)^j f_j^*+\sum(-1)^j h_j^*.
\]

Thus `zv=1`, `wu=0`, `zu=wv=0`, and `w+z=A*`. Multiplying the three thin
factors directly gives

\[
B=I-2P-2N,\qquad P=EE^*+vz,\quad N=uw.
\]

Here `P²=P`, `rank(P)=2`, `N²=0`, `rank(N)=1`, and `PN=NP=0`. Consequently

\[
(B-I)^2=4P,\quad B^2=I-4N,\quad(B+I)(B-I)^2=0.
\]

The minus eigenspace is `im(P)=span(E,v)`, of dimension two. The actual plus
eigenspace is `ker(P)∩ker(w)`, of dimension seventeen; its generalized eigenspace
has dimension eighteen. This distinguishes the Jordan direction from an
ordinary invariant carrier.

In the normalized fixed-root frame, the central bridge in the `S=+1` sector is
`I`, and in the `S=−1` sector is `B`. A sector-independent carrier projector
transported across it must satisfy

\[
J_{\rm after}=J_{\rm before},\qquad BJ_{\rm before}=J_{\rm before}B.
\]

The first identity follows from the plus sector, and the second follows from
the minus sector. This permits arbitrary changes of basis *inside* a carrier
plane but does not permit free movement of its projector between different
ordinary planes. A construction that changes the effective root, uses
sector-dependent carriers, or performs other restored work needs a separate
model and invoice.

## 2. Why actual eigenspaces suffice

For every full site,

\[
wx_i=\begin{cases}1&\text{left}\\-1&\text{right},\end{cases}
\qquad
 y_i u=\begin{cases}-1&\text{left}\\1&\text{right}.\end{cases}
\]

Every full query annihilates `span(E,v)` on both sides. An idle projector obeys
`Jx_i=0` and `y_iJ=0`. If it crosses the bridge, it commutes with `B`, hence with
its polynomial `N=(I−B²)/4`. Applying `JN=NJ` to any crossed full-query column
forces `Ju=0`, because `wx_i` is nonzero. Commutation then forces `wJ=0` as well.
Thus `JN=NJ=0`. Since `J` also commutes with `P=(B−I)²/4`, it splits into its
plus and minus parts, whose image and row spaces lie in the actual eigenspaces.
The generalized plus direction is not admissible merely because it is invariant.

For common mask `M` and interval of full sites `I`, define

\[
U_\lambda=\{f:(B-\lambda I)f=0,\ y_i f=0\ (i\in I),\ f_{M^c}=0\},
\]

\[
V_\lambda=\{g:g(B-\lambda I)=0,\ gx_i=0\ (i\in I),\ g_{M^c}=0\}.
\]

The maximum number of dual carrier directions in the interval is

\[
\operatorname{rank}(V_+U_+)+\operatorname{rank}(V_-U_-).
\]

The two eigenspaces pair orthogonally. Within each, a rank-`c` bilinear pairing
allows `c` biorthogonal row/column pairs and hence a commuting rank-`c`
idempotent. This proves the isolated interval capacity. Simultaneous carriers
on overlapping intervals may have extra compatibility restrictions; ignoring
those restrictions only makes the author's cost relaxation more favorable.
For a one-sided interval, omit the eigenvalue constraints and use the rank of
the unconstrained row/column pairing.

This is the method implemented in `geometry.py`: direct nullspaces of explicit
plus and minus eigenvector equations, followed by pairing rank. It is different
from the author's cyclic-span rank formula.

## 3. Why the cyclic closure is a valid upper bound

Let `X` span the crossed full-query columns and all off-mask coordinate columns;
let `Y` span the corresponding full-query rows and off-mask coordinate rows.
From `JX=0`, `YJ=0`, and `JB=BJ`, necessarily

\[
J\,\operatorname{span}(X,BX,B^2X)=0,
\]

\[
\operatorname{span}(Y,YB,YB^2)J=0.
\]

Powers through two suffice by the bridge's degree-three polynomial. For these
closed spaces `X_c,Y_c`, the rank of a dual pairing between their annihilators is

\[
20-\dim X_c-\dim Y_c+\operatorname{rank}(Y_cX_c).
\]

This is an upper bound on any admissible carrier rank, irrespective of whether
a general nonsemisimple commutant would attain it. In the present source, the
separate eigenspace calculation above attains and verifies exactly the same
capacity for all 13,851 declared cases.

There is also a symbolic explanation of the difference from pointwise thin
annihilation. Every declared mask excludes `E`. The minus eigenspace can then
contribute only `vz`, whose image and row have support on all nineteen non-E
coordinates. Thus a crossing interval gains exactly one carrier when its
common mask is all nineteen coordinates, and no carrier otherwise. A plus
carrier has `Ju=Jv=JE=0` and `wJ=zJ=E*J=0`, and consequently kills all three
individual thin factors,
using `w+z=A*`. This accounts for the 2,025 changed interval capacities across
the eighty-one cases. In particular, the full dense interval has capacity one.

## 4. Quotient audit and its precise limitation

Let `R=I−P` project onto the eighteen-dimensional common active complement.
The bridge restricts there to `I−2uw`, a single rank-one query factor. This is
why eighteen full queries plus one thin query can close the quotient root.
It says nothing yet about productive stage targets.

For each original native active rank-two projector `Π_i`, put `Q_i=RΠ_iR`.
Direct algebra, independently replayed for all eighteen sites, gives

\[
Q_i^2-Q_i=c_iR_i,\qquad R_i=x_i y_i,
\]

where `c_i=(-1)^j` at left site `j` and `c_i=−(-1)^j` at right site `j`, with
`j=0,...,8` on each arm. Each `Q_i` has rank two, but each defect has rank one.
Therefore the raw compressed stage is not a projector.

This is **not a general impossibility result**: since `Q_iR_i=R_iQ_i=R_i` and
`R_i²=0`,

\[
\widetilde\Pi_i=Q_i-c_iR_i
\]

is a rank-two idempotent retaining the same query operator. All eighteen local
repairs were checked exactly. Their first pair has a rank-two commutator, so
these particular repairs do not form one common coordinate stage system.
A noncommuting productive output representation remains an open mechanism
requiring its own recursion and full cost accounting. No separate no-idle
theorem is needed for this package's claims.

## 5. Reproduction and exact coverage

The original independent review ran from a separate worktree. The packaged
equivalent commands are:

```sh
python3 -B research/p104-block-bridge-carriers/review/geometry.py
python3 -B research/p104-block-bridge-carriers/review/prices.py
```

The geometry checker contains its own exact matrix elimination and explicit
bridge formulas. It reads the author's frozen capacity report only as comparison
data, without importing author code. The comparison data are retained as `capacity-reference.json`. The original
full discovery report had SHA256
`9ef342039e29463ed1ef9afca70043d1e408b201c7325ad8769ad5c9f5e7ac58`;
the packaged fixture drops unrelated floating solver output. Source paths and
report handling were adapted by the author for standalone reproduction, while
the reviewer's geometry and arithmetic algorithms were retained.
`EXPECTED-GEOMETRY.json` records the full independently computed capacity table, all
projector defects and repairs, and the declared scope. `EXPECTED-PRICES.json`
records all eighty-one complete dual upper margins.

The dual audit uses the reviewer's previously completed source-authenticated
native profile and alternating-exponential rational arithmetic. It verifies
nonpositive inequality duals, every column dual constraint, all target degrees,
all eighteen native calls, three thin queries, 104 ports, and the complete dual
paid bound. It does not infer global infeasibility from a floating-point solver
or claim that the relaxed optimal schedules can all be physically realized.
