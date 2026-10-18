# Rational star observations recover a prescribed triangle

**Research note and scoped information theorem. No new kappa or physical
supplier.** Changing the observation field removes the binary triangle
obstruction in woklerx's [PR966](https://github.com/CrocSwap/integer-mult-bounds/pull/966).
It does not remove the cost of restricting the input family.

Let `G` be the graph on `2p` vertices with every edge except a fixed perfect
matching. Each retained edge has an arbitrary input value. The observation
at a vertex is the **sum**, in a field of characteristic other than two, of
its incident retained inputs. Fix three target edges forming a triangle.
Only nontarget edges may be deleted. A deletion removes that input from the
arbitrary source family, equivalently fixes it to zero; it is not a free
read and subtraction.

The exact minimum number of deletions for recovering all three target values is

```
p = 3:    5
p >= 4:   6p - 12.
```

This includes arbitrary nonlinear postprocessing of the same observations.
In characteristic two, recovery is impossible at every deletion budget.
There is no contradiction with PR966, whose theorem is explicitly binary.
The addition here is the changed-field criterion, the sharp paired-graph
optimization and its exceptional `p=3` construction. No literature-wide
priority is claimed for incidence-matrix or graph-code facts.

## Reproduce

From the repository root, offline, Python 3.10+ and the standard library:

```sh
python3 -I -B research/rational-triangle-seed48/verify.py
```

Expected final line:

```text
PASS_RATIONAL_TRIANGLE_S48 assignments=840693 graphs=512 deletions=5,12,18 restored_edges=35 omissions=172 no_new_kappa
```

[CERTIFICATE.json](CERTIFICATE.json) is compared to a freshly computed receipt.
`--emit` prints that receipt without changing files. `--certificate PATH`
checks another receipt and rejects any mismatch. Checks remain active under
`python3 -I -O -B`. There are no solver, network or predecessor-code imports.

The finite census visits all seven-class assignments for `p=3,4,5`, with
343, 16,807 and 823,543 assignments. It finds 7, 12 and 22 retained edges
respectively. These assignments cover the graph class established below;
they are not an independent proof of that reduction or the all-p theorem.
A separate exact rational row-space calculation checks **all 512 retained
graphs at p=3**, without the class reduction. It finds 97 recoverable graphs,
three with seven edges; an independent binary elimination finds none.
At each of the three optima, dropping any one raw vertex observation makes
recovery fail, giving another 18 adverse controls.
Both methods were written by the same AI-assisted contributor.

Local validation used CPython 3.14.8 on macOS 26.5.2 arm64, with and without
optimization and from outside the checkout. Three external receipt mutations
changed the deletion minimum, SCALE invoice and an integer count to a boolean;
all were rejected. The repository's `scripts/verify_selected_result.py` passed.
No supplier source changed, so the full frontier replay and historical suites
were not run. Hosted Linux CI and a formal theorem proof are not claimed.

The checker also restores each of 35 deleted edges in the three displayed
optimum fixtures and requires recovery to fail. It tests all source, output
and arbitrary dirty-helper basis columns of three explicit scalar words,
then omits each of their 172 instructions individually and requires failure.
Finite evidence supports the written proof; it is not formal verification.

## Proof

Matching automorphisms take any target triangle to vertices `a,b,c = 0,2,4`.
Write its edges in order `ab,ac,bc`. Let `H` be the retained graph and remove
the three target edges to form `J`.

### Recovery criterion

The targets are recoverable if and only if each component of `J` containing
a target vertex is bipartite and contains exactly one target vertex.
Components containing no target vertex are unrestricted.

For necessity, recovery of a linear coordinate from linear observations,
even by nonlinear postprocessing, requires that coordinate to vanish on
the observation kernel. Otherwise two inputs with identical observations
have different target values. By finite-dimensional row-space duality,
there must therefore be three linear decoder rows. Collect their
coefficients at each vertex in a vector `c_v` of length three.

The triangle equations force

```
c_a = ( 1, 1,-1)/2
c_b = ( 1,-1, 1)/2
c_c = (-1, 1, 1)/2.
```

Every nontarget retained edge `uv` requires `c_u + c_v = 0`. Coefficients
alternate in sign along paths in `J`. An odd cycle forces them to zero
throughout its component, since two is invertible. None of the displayed
root vectors is zero, and no two are equal up to sign. Thus a component
meeting a target vertex is bipartite and cannot meet another target vertex.

Conversely, assign the displayed vector to each target vertex, extend it
with alternating signs across its bipartite component, and assign zero to
every other component. The resulting three coefficient rows cancel every
nontarget edge and extract exactly the three target coordinates. This proves
the criterion over every field of characteristic other than two.

For characteristic two, add a nonzero field element to all three triangle
inputs. Every vertex observation is unchanged and all three targets change.
This works regardless of which nontarget edges survive.

### Maximum retained edges

Let the three rooted bipartite components have sizes `s_1,s_2,s_3 >= 1`.
Combine all other vertices into a residual set of size `b`, so
`s_1+s_2+s_3+b=2p`. Grant every permitted edge inside that residual set.
There are no edges between these four sets except the three target edges.

A bipartite graph on `s` vertices has at most `h(s)=floor(s^2/4)` edges.
The residual set contains at least `max(0,b-p)` complete matched pairs,
so it has at most `f(b)=binom(b,2)-max(0,b-p)` edges. Consequently

```
|E(H)| <= 3 + h(s_1) + h(s_2) + h(s_3) + f(b)
       <= 3 + h(2p-b-2) + f(b).
```

For the second inequality, `h(1)=0` and the forward differences of `h`
are nondecreasing. Moving a vertex from a smaller rooted block of size
at least two to a largest rooted block cannot decrease the bound. Repeat
until the sizes are `2p-b-2,1,1`.

As an integer function of `b` on `0 <= b <= 2p-3`, both `h(2p-b-2)` and
`f(b)` are convex. For `f`, the forward difference is
`b - 1[b>=p]`, which is nondecreasing, including the repeated value at
the threshold. A convex sequence attains a maximum at an endpoint. Thus

```
|E(H)| <= max((p-1)^2 + 3, 2p^2 - 8p + 12).
```

The second endpoint minus the first is `(p-2)(p-4)`. At `p=3` the first
gives seven edges. At `p>=4` the second gives `2p^2-8p+12`. Subtracting
from `|E(G)|=2p(p-1)` proves the claimed deletion lower bounds.

### Attainment and explicit decoder

At `p>=4`, retain the target triangle and every edge induced on all other
vertices. Delete every edge between the two sets. There are
`3(2p-3)-3=6p-12` such edges, since three of the potential crossing edges
are forbidden matching edges. The criterion proves recovery.

At `p=3`, use matched pairs `01,23,45`, target triangle `02,04,24`, and
retain four further edges `03,05,13,15`. The rooted component of `J` at
vertex zero is `K_(2,2)` with sides `{0,1}` and `{3,5}`. The other two roots
are isolated. This retains seven of twelve edges and attains five deletions.

For this exceptional fixture, write vertex observations as `z_v` and set

```
S_a = z_0 + z_1 - z_3 - z_5,   S_b = z_2,   S_c = z_4.
x_ab = ( S_a + S_b - S_c)/2
x_ac = ( S_a - S_b + S_c)/2
x_bc = (-S_a + S_b + S_c)/2.
```

For the isolated-triangle fixture use `S_a=z_0, S_b=z_2, S_c=z_4` instead.
In each case internal nontarget contributions cancel exactly.

## Fully priced abstract scalar word

This section prices one explicit implementation, not a minimum-cost circuit
or a selected supplier. The scalar alphabet has unit-cost signed ADD and
unit-cost SCALE by two or one half. Sources are immutable and outputs and
helpers may start arbitrarily dirty. Each source access is a charged ADD.
There are no clean-zero assumptions, COPY instructions, frame changes or
recursive children in this abstract scalar model.

Let `A` gather the active vertex-star observations into helpers, and let
`B` be the displayed decoder. Use the exact echo

```
H += A X;   D += B H;   H -= A X;   D -= B H.
```

Each `BH` update scales every active helper by one half, performs the
signed output ADDs, and scales those helpers back by two. The whole word
returns `H` unchanged and sends `D` to `D+BA X` for every initial helper
and output value. Source inputs, including ignored residual inputs, are
unchanged. `verify.py` emits and executes every instruction on every basis
column, including all dirty columns.

| Fixture | Dirty helpers | Source ADDs | Output ADDs | SCALEs | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Five-deletion `p=3` optimum | 6 | 28 | 36 | 24 | 88 |
| Isolated triangle, every `p>=4` | 3 | 12 | 18 | 12 | 42 |

The rational rank of `A` is six in the `p=3` fixture and three in the
isolated fixture. The six-helper word intentionally preserves the supplied
vertex-star interface; it does not claim optimal compression or optimal
scalar cost. Direct access to the three target inputs would need only three
ADDs in this alphabet. This word therefore provides no scalar speedup.

The five-deletion exception also has a real information tradeoff. All six
raw vertex observations are needed, while the six-deletion isolated triangle
at `p=3` needs only three. In the exceptional fixture the retained graph is
connected and contains the triangle. A dependence among its vertex rows
would alternate signs along every edge; the triangle forces zero at its
vertices, then connectedness forces zero everywhere. Thus all six rows are
independent and the displayed decoder rows are unique. Each uses all six
observations with nonzero coefficients. Dropping an observation fails;
offering a precomputed linear combination changes the gather interface.

Changing a bit/XOR observation into a rational sum is a changed contract.
The information theorem grants those rational observations and the punctured
source family. A physical multiplication supplier would still need a useful
geometry, paid source restriction or correction, copied-information ranks in
that geometry, frame realization, precision and storage bounds, recursive
children and whole-call hosting. No such supplier is constructed here.
The selected assembly is complex-binding; this result does not change either
supplier budget or its kappa. The inherited all-size/compiler, common-label,
mutable-source, precision/tape, bit H1-H5 and analytic obligations remain open.

## Provenance and open next questions

Base `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`; OS seed **48**, structural
decoder track. [CLAIM.md](CLAIM.md) records candidates, bounded coverage and
coordination. [SOURCES.json](SOURCES.json) pins the predecessor and selected
construction context with SHA256 and Git blob IDs. Selected conditional
kappa at this base is `836330098538459/500000000000000000`, from PR1094.
The selected record, supplier sources and `upstream/` are unchanged.

Credit **woklerx, PR966**, for the prescribed binary triple problem and its
explicit characteristic-two scope; **Sam Sung / the-missionary-company,
PR669**, for the target hierarchy; **Joel Pulikkan / GamingPuzzled, PR231**,
and **icekylinx/eumemic** for the proper-star and paired-port lineage.
The binary comparison uses the locally integrated PR966 proof at the exact
base, with original PR head `7eaf5665ac246310293fda06a3cf245fe72f6012`.
No pending PR is assumed as a mathematical theorem dependency.

**Open next questions**

- Can a native complex geometry realize these rational observations more
  cheaply than direct target access? First derive a complete invoice for
  one existing geometry, including the deleted-input correction. The current
  blocker is that this graph incidence model supplies no physical copy ranks.
- Can the three needed combinations of the six observations be gathered
  cheaply in a native geometry? First price one gather for each displayed
  `S_a,S_b,S_c` and its restoration. Preserving all six observations cannot
  use fewer than six scalar dimensions, since their rational rank is six;
  a smaller interface must explicitly discard unneeded information.

Prepared by **Sagar Thakrar (@thakrarsagar)** with substantial **OpenAI Codex
assistance** in mathematics, implementation, checking and writing. No
independent human review or proof-assistant verification is claimed.
Apache-2.0 under the repository license.
