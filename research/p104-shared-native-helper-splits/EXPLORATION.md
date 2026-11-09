# Scope of the causal and geometric searches

The accepted word is established by its exact witnesses, not by trusting a
search score. `SEARCH.json` records the finite domains, source payloads and
stopping rules. Floating-point signed moments select and order proposals. Exact
endpoint, physical, invoice and rational-interval checks decide acceptance.

## An endpoint reduction for new intermediate frames

Consider a helper whose boundary is the zero subspace to the full
dimension-$D$ space, and fix $0<t<1$. Suppose a cut uses $m\geq1$ contact-free
transport paths. The lower and upper endpoint dimensions of path $i$ are
$a_i,b_i$, with $0\leq a_i\leq b_i\leq D$. All paths must be coframed at an
intermediate subspace $F$, so

\[
 \bigvee_i A_i\subseteq F\subseteq\bigcap_i B_i.
\]

For $x=\dim F$, the complete signed gain from this one split is

\[
 G(x)=x^t+(D-x)^t-D^t
       -\sum_i\bigl((x-a_i)^t+(b_i-x)^t-c_i\bigr),
\]

where $c_i$ is the sum of the old path's paid rank powers. Both new legs are
charged; a zero leg is omitted. Every additional path costs its own pair of
legs. The old paid term is constant in $x$.

Let $h(x)=x^t$. On the open common dimension interval,
$h''(x)=t(t-1)x^{t-2}<0$. Since $x-a_i\leq x$ and
$b_i-x\leq D-x$, each one path gives

\[
 h''(x-a_i)+h''(b_i-x)\leq h''(x)+h''(D-x).
\]

Consequently $G''(x)\geq0$: one charged path already dominates the helper's
negative curvature, and further charged paths add nonnegative curvature.
Continuity extends convexity to endpoints, using $0^t=0$. The maximum on the
closed feasible dimension interval is therefore attained at an endpoint.
The join of the lower subspaces and the meet of the upper subspaces realize
those endpoint dimensions. When both are strictly between zero and $D$, a
new intermediate chart cannot beat both extrema in the complete rank bill.

This is a scoped reduction. It concerns full zero-to-$D$ helper boundaries,
fixed contact-free paths and their complete recursive rank charge. It does
not prove ordinary-cost feasibility or exact cut equations. If an extremum
is zero or $D$, a proper helper split still requires separate treatment of
the allowed integer dimensions. For a proper helper boundary, a paid path
may extend outside that boundary, and the curvature comparison need not hold.

## Bounded new-frame screen

The frozen 46-split checkpoint was used as an exploratory input. The first
screen used single-MOVE, rank-two contact-free paths. It enumerated 855 path
windows, 14,882 eligible overlapping pairs, 23 new pair-generated join/meet
geometries, 138 frame/cut regimes and 3,260 distinct two-to-four-path systems.
Its exact prefix and suffix kernel calculations found zero nonzero boundary
pairings. That is a finite obstruction for those systems, including their
rational kernel spans, not an impossibility theorem for other frames or words.

The mixed-rank extension used 2,178 single-MOVE windows of ranks two through
eight, 740,269 overlapping pairs and 916 favorable new pair-generated
geometries. The geometry cap of 2,048 and subsystem cap of 500,000 were not
reached. It checked 6,150 frame/cut regimes and 9,976 distinct two-to-four-path
systems. Twenty basis-pair witnesses had nonzero compatible pairings. Fifteen
were dominated by an already present frame. Five shared one cut whose
inherited basis-construction heuristic initially produced an illegal scalar.

The screen only forms geometry extrema from pairs of path windows. It does
not exhaust extrema first created by joins or meets of three or four paths,
longer transport windows, or all linear combinations of nonzero paired kernel
bases. It establishes no general optimality claim.

Floating-point screening does not certify inclusion of every possibly
positive geometry. The exact zero-pairing conclusion applies to the recorded
finite candidate list. Its complete domain and outcome can be rerun:

```sh
python3 -B research/p104-shared-native-helper-splits/construct.py --steps 46 /tmp/helper-word46.json.gz
python3 -B research/p104-shared-native-helper-splits/screens/rank_two.py --word /tmp/helper-word46.json.gz --output /tmp/helper-rank-two
python3 -B research/p104-shared-native-helper-splits/screens/mixed_ranks.py --word /tmp/helper-word46.json.gz --output /tmp/helper-mixed-ranks
```

The screens require the exact checkpoint46 payload and compare finite
coverage to `SEARCH.json`. Outputs go only to the specified directories.
The registered construction verifier needs no search.

## A constructive dyadic pivot correction

In the five remaining witnesses, the boundary direction has first nonzero
entry $-3/2$ at role 462. The historical algorithm chooses that entry and
attempts a SCALE by $-2/3$, outside the allowed dyadic-unit alphabet. The same
direction also contains legal unit coordinates, including $-1$ at role 565.
The new optional `dyadic-unit-v1` rule chooses an available dyadic unit before
normalizing the column. Every emitted operation and inverse is checked.
This is a constructive choice correction, not a relaxation of the alphabet.

At the exact cut 11,912 of the frozen 46-split input, roles 505 and 1,249 each
have a contact-free rank-three MOVE from frame 3 to frame 364. The intermediate
vectors are $a=e_{505}^T+e_{1249}^T$ and $b=e_{1249}$. Choosing the already
present rank-three frame 364 gives a better complete bill than the five new
rank-two charts: both original MOVEs are simply moved before the cut, without
changing a paid operator. The legal basis then yields the 47th independent
helper split, of ranks three and six. Subsequent searches reuse this optional
rule, always recomputing the exact cut equations on the changed word.

The final existing-frame pass can also be reproduced independently of the
committed final word. It enumerates 180 witness variants, processes all 145
unchanged-paid templates, and accepts three new cuts after checkpoint65:

```sh
python3 -B research/p104-shared-native-helper-splits/construct.py --steps 65 /tmp/helper-word65.json.gz
python3 -B research/p104-shared-native-helper-splits/discover.py /tmp/helper-word65.json.gz /tmp/helper-hits65.json --basis-rule dyadic-unit-v1 --saving .0035530
python3 -B research/p104-shared-native-helper-splits/retime_search.py --word /tmp/helper-word65.json.gz --hits /tmp/helper-hits65.json --output /tmp/helper-final-pass --prefix research/p104-shared-native-helper-splits/WITNESSES.json --prefix-steps 65 --max-new 40
```

The emitted `word-68.json.gz` has the committed scientific payload. The
Euclidean fallback used in an exploratory version admitted no extra variant,
so the portable reproduction uses only the published dyadic-unit rule.

The first 46 steps retain their historical basis rule, preserving their exact
payload hashes. Later witness entries name the new rule explicitly. Neither
rule claims to decide every dyadic-realizable basis; more general unimodular
row reduction could admit further witnesses and would require full accounting.

The causal basis mechanism is inherited from
CrocSwap/integer-mult-bounds#5599 and the witnessed retiming implementation
from CrocSwap/integer-mult-bounds#6805. This note and the new source-specific
instances are by @CubeJerry with substantial OpenAI assistance. Apache-2.0.
