# Aligning common-point pair groups

The paired circuit can share more additions if its root pairs agree across
common-point groups. At the same `h=50`, this reduces side roles from 509,194
to **494,250** and supports the conditional saving

$$\kappa=17\cdot2^{-63}\approx1.8431436932\times10^{-18}.$$

This is 6.25% above the preceding `2^-59` headline. The unchanged dimension
and stopping recipe gives a minimum margin 6.1735% above its preceding exact
minimum. These are exponent comparisons, not measured practical speedups.

Artifacts: [certificate](../../certificates/aligned-paired-network.json),
[independent patch](../../patches/h50-aligned-paired.patch), and
[proof note](../../artifacts/aligned-paired-note.pdf).

The [focused review packet](aligned-paired-review.md) separates the finite
claim from its conditional consequence and identifies the rank, fixed-tape
recurrence and downstream obligations for independent review.

## Construction and frame transfer

Fix global pairs `{0,1}, {2,3}, ..., {48,49}`. For common point `i`, list all
points except `i` and `i^1` increasingly, then append `i^1`. Run the unchanged
49-point paired circuit in those coordinates. Its first 24 groups are now
complete global pairs, and its last group is the singleton partner of `i`.

The local weighted exclusion identity is invariant under this permutation:
edge inputs and pair outputs receive the same relabelling. Every contributing
triple still contains its common point and avoids the other two target points.
Each addition still has disjoint formal supports. Identify equal sums across
groups by the existing fixed-pair and union rule, retaining the first
decomposition. The exact local additions and outputs remain 9,813 and 1,176;
the global additions become **435,450**, with **55,200** merged additions and
58,800 partial outputs. Thus `R=435450+58800=494250`.

This changes the finite graph, not its reversible embedding or frame theorem.
Every retained source span has a common point and is positive definite under
the form `I-J/9`. Nested forward source spans and reverse orthogonal
complements therefore give the same nondegenerate frames, with no new rank
loss. The dirty-scratch restoration schedule and complete stage-1/stage-3
matching are unchanged. The [paired construction](paired-network.md) proves
these transfers for every such cancellation-free graph.

With `v=19600`, `N=v^3`, `m=125000` and central loss `L=3v^2h^2`, the counts are

$$W=2N+2v^2(R+h)=394839648000000,$$
$$s=Wm-N+2L=49354954232864000000,$$
$$D=Wm-s=1767136000000,\qquad\eta_b=23/642375000.$$

The absolute deficit is unchanged. The rational logarithm enclosure gives
`log(m)<11737/1000` and `eta_b>(305/10^11)*(11737/1000)`, so the bit saving
can increase from `296/10^11` to **`305/10^11`**. The original complex motif,
its saving `a_c=1/10^11`, and its coefficient-depth guard are unchanged.

## Downstream dependencies and strict target

Put `a=305/10^11`, `tau=1-a`, `sigma=1-a_c`, `beta=999/1000`,
`epsilon=199/1000`, `delta=1/10000`, `C1=2`, `c=beta*a`,
`lambda=1-(1+beta)*a^2/2`, and `lambda-prime=1-beta*a^2`.

Then `tau*(1+c/beta)=1-a^2<lambda<lambda-prime<1`,
`sigma<lambda`, and `sigma+beta*(1-sigma)<lambda-prime` by exact comparison.
The same stopping rule `e^1000<d^999`, stopped guard, Gaussian width
`alpha=ceil((32*d*b)^(1/4))`, and cutoff `b>=2^40` apply. In particular,
the guard and Gaussian exponents, prime intervals, setup and precision
conditions remain those in the paired dependency audit. Only `a`, the
derived layer choices, finite bit counts, and final target change.

All 30 strict constraints and seven margins pass, with

$$G=g_2=g_3=\epsilon\beta a^2
=\frac{739738521}{400000000000000000000000000}>17\cdot2^{-63}.$$

The fixed positive gap absorbs the retained logarithmic factors. The patch
updates the finite construction, both bit interfaces, layer choices and
assembly conclusion together, and applies independently to the unmodified
pinned source. This is complementary to parameter-only optimization: the
recipe is retained and the graph supplying its bit exponent changes.

## Verification boundary

Run `make verify`. Small tests independently expand every global support,
check both frame directions, test all dirty input basis vectors in forward
and reverse invocations, and exercise complete shared three-stage bank
exchange. A full-size regression expands the actual global DAG in 1,024-input
chunks, independently of the provenance checker, and compares every output
coefficient with incidence-star masks. Compiled frame inclusion, source hashes
and the independent patch are checked too.

The circuit was selected from bounded relabelling and ground-size screens;
no optimum for this family or a new dyadic `2^-58` target is claimed. The
scoped fixed-graph ceiling remains below `2^-58`. The complete upstream
multiplication theorem and retained analytic interfaces remain assumptions.

This refinement builds on Douglas Colkitt's paired construction and OpenAI's
pinned manuscript. It is not independent verification of the complete theorem.
