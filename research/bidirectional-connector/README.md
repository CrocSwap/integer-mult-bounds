# Dirty-connector lower bounds and a signed zero-sum triangle

The primary results are **all-word one/two-root query lower bounds**, including
source-locality corrections and matching **4M/3M asymptotics**, and a **signed
triangle** with the F2 palette's source/read counts plus four transfers.
All children in the scalable constructions use physical root z0.
These are scoped exact query-model results, not a new multiplication exponent.

Secondary results are a 73-call F2 extension of Math PR1's five-source tariff
comparison, a minimum-read F2 compiler, a minimum-source n9 lower bound, and
signed fixed-port parent caches. The six-transfer witness/census and all-n
F2 two-call obstruction already occur in [Math PR1](https://github.com/conorholds/math/pull/1)
and [Math PR2](https://github.com/conorholds/math/pull/2); retained versions here
are supporting fixtures and independent cross-checks, not additional novelty.
Their predecessor packages remain the canonical Math accounts. Upstream
[PR2065](https://github.com/CrocSwap/integer-mult-bounds/pull/2065) independently
establishes the six-transfer endpoint; it is credited as a baseline here.
[PR2182](https://github.com/CrocSwap/integer-mult-bounds/pull/2182) contains the
separate fixed-port/two-root-boundary submission from the same contributor.
Neither endpoint nor the n>=6 two-call obstruction is a new claim of this package.

## Interface and paid scope

Let M=2^n-1. Source rows x_j, target rows y_m and roots z_p are distinct,
aligned length-L arrays, arbitrary dirty on entry. For every nonzero mask m:

```text
y_m += A_m sum_(j in m) B_j x_j; all x_j and roots restored.
```

Maps are arbitrary exact F2-linear or characteristic-zero linear maps,
possibly singular and noncommuting. The straight-line word is independent of
map entries/data. Calls are B(j,p): z_p+=B_j x_j and A(m,p): y_m+=A_m z_p;
the signed model also allows their additive inverses, not inverse matrices.
For two roots, U: z0+=z1 and V: z1+=z0, with signed inverses where applicable.
Sources are read-only and outputs unobserved until the whole batch completes.
All source, target and declared root rows are excluded from child scratch;
children preserve other rows and restore private work, frames and heads.
There are no free copies, resets, root rescaling/doubling, output borrowing,
combined queries or hidden persistent image caches. The cache section explicitly
changes the root stock and transfer alphabet.

Prices b,a,tau mean **fixed complete-call tariffs**, including access, recursive
leaves/inverses, updates, restoration, frames, heads and dispatch. Comparisons
require actual fixed prices or certified lower bounds for every comparator
orientation/port. Orientation maxima are candidate upper bounds, never
comparator lower bounds. In the limit claims a=1 and b~sqrt(2M); equal port
prices are an assumption, not an inferred property of a physical caller.

A transfer is a full-row pass with L updates plus actual routing/access costs.
Add H_word for costs outside the calls: extra root reservation, parking,
coefficient/input preparation, schedule generation/reads, counters, precision,
child-private work and tape/owner hosting. Different H_word values can erase a
query saving. No qualifying selected caller, contracting moment or kappa gain
is established. Exact arithmetic is not a floating-point error analysis.

## All-word lower bounds and the optimal 25% limit

Let k be the total B calls. Generic restoration forces k>=2n: a single
injection has a nonzero transported coefficient that invertible root transfers
cannot erase. Every target needs at least two A reads to cancel incoming dirt.
Necessity already follows from scalar identity maps and independent inputs;
these bounds concern words valid for every choice of maps.

With one root, signed dirt cancellation forces an even number of reads for
each target, and source closure makes k even. The closed source-prefix walk
has at most k distinct states. At most choose(k,2) nonzero masks can be served
with two reads; other masks require at least four. Hence every word costs:

```text
k*b + a*max(2M,4M-k(k-1)), k>=2n, k even.
```

With two roots write the state as G(d+Q), where G is the invertible scalar
root frame, d the incoming dirt and Q the two normalized source rows. Transfers
change G but not Q. Two reads cancelling dirt use one common functional l
(after accounting for signs), so their mask lies in the row space of Q_s-Q_t.
This has rank at most two. A rank-r subspace meets the binary mask cube in at
most 2^r points: project injectively onto r pivot coordinates. Including zero,
each prefix pair therefore supplies at most three nonzero masks. This works
in F2 and characteristic zero, even granting arbitrary scalar root frames free.
Closure repeats Q=0, so at most k distinct prefixes occur. Every two-root word
therefore costs at least:

```text
k*b + a*max(2M,3M-3*k(k-1)/2), k>=2n.
```

These are optimistic union bounds; repeated masks only strengthen them.
No two-call incidence or transfer-depth restriction is used. Before capacity
saturates at M, the price expression is concave in k; afterwards it increases.
[families.py](families.py) minimizes over the admissible interval endpoints
with integer/Fraction arithmetic, no finite cutoff or floating roots.

Let r_n be the first even k>=2n with k(k-1)>=2M and set
b_n=r_n-2+2n-1, a=1. Then b_n/sqrt(M)->sqrt(2). With x=k/sqrt(M), the
one-root lower expression tends to `sqrt(2)*x+max(2,4-x²)`, whose minimum is 4.
The two-root expression tends to `sqrt(2)*x+max(2,3-3*x²/2)`; its concave
branch endpoints are 3 and 2+2/sqrt(3)>3, followed by an increasing tail.
Thus the respective lower limits are 4M and 3M.

Four balanced one-root Gray blocks give (4+o(1))M reads and O(M^(1/4)) B
calls; signed references visit positive/negative cubes with opposite reader
signs. At the declared b_n their source cost is o(M). The three-block palettes
below give (3+o(1))M reads and O(M^(1/3)) B/transfer calls, again costing o(M).
Therefore **OPT_one/M->4 and OPT_two/M->3**, a matching **25% limiting
query-tariff saving**, in both fields. Any fixed finite transfer tariff is
compatible with these limits; overhead H_word is not assumed to vanish.
Characteristics such as three do not inherit the even-readout argument.

### Stronger source-locality correction

Index the k source cuts cyclically, identifying the final cut with the first.
For 0<=h<k/2 exactly k*h unordered cut pairs have cyclic distance at most h.
Their source differences touch at most h labels, even after frame normalization.
Together they can realize at most S(n,h)=sum_(i=1..h)choose(n,i) nonzero masks.
Each remaining pair contributes at most p masks, p=1 for one root, p=3 for two:

```text
P_p(n,k)=p*choose(k,2)-max_(0<=h<n)(p*k*h-S(n,h)), S(n,0)=0.
```

Every listed h is legal since k>=2n. Legal radii h>=n yield capacity at least
M and cannot strengthen the saturated bound. Replace paired capacity in the
preceding prices by P_1 or P_3:
`k*b+a*max(2M,4M-2P_1)` or `k*b+a*max(2M,3M-P_3)`.
The h=1 term removes repeated singleton slots. Repeated prefix states are safe.

Between intersections of deficit lines the unsaturated price remains concave;
after saturation it increases. `locality_lower_bound` checks both admissible
integer neighbors of every line intersection, the initial k and the saturation
boundary. Independent source-count enumeration checks this minimization on
small domains; actual closed walks check capacity. The 4M/3M limits persist.

## F2 palette and signed zero-sum triangle

Split sources into three nonempty blocks, q_i=2^(block size). Each block runs
one closed reflected Gray cycle. Every child uses z0, and z1 holds dirt only.
For F2 use normalized columns 10,01,11. At each nonzero vertex one U exposes
the second signature; a closing V changes/restores the companion dirt:

| Block | Entry dirt (z0,z1) | z0 signatures | After closure and V |
|---|---|---|---|
| P | (d0,d1) | d0,d0+d1 | (d0+d1,d0) |
| Q | (d0+d1,d0) | d0+d1,d1 | (d1,d0+d1) |
| R | (d1,d0+d1) | d1,d0 | (d0,d1) |

Pure targets read at zero and their block sum with matching dirt. Two-block
targets use the shared signature; three-block targets use 10,11,01, whose dirt
XOR is zero. Applying the same A_m gives exactly the requested source terms.
The invoice is B=sum(q_i), A=2M+product(q_i-1), T=B, two dirty roots.

For characteristic zero use `vP=(1,0), vQ=(0,1), vR=(-1,-1)`.
There is still one positive subset cube per block in normalized coordinates;
physically R uses inverse B/A calls. No division, rescaling or clean row occurs.

| Block | Entry dirt | z0 signatures | Read sign | Closing shears |
|---|---|---|---:|---|
| P | (d0,d1) | d0,d0-d1 | + | U+,U+,V-,U+ |
| Q | (d1,-d0) | d1,d1-d0 | + | U-,V+ |
| R | (d1,d1-d0) | d1,d0 | - | V+ |

At nonzero vertices U signs alternate, starting -, +, - respectively. Each
q_i-1 is odd, so every phase exits on its second signature. The table's closing
shears reach the next entry and finally restore (d0,d1). P/Q reads cancel
(d0-d1)+(d1-d0); P/R cancel d0-d0; Q/R cancel d1-d1. Three-block targets use
P at d0, Q at d1-d0 and inverse R at d1. Pure targets use an opposite-sign
anchor read at zero. The negative physical R sum and inverse A reader make
all requested source contributions positive, with no commutation assumption.

```text
B_signed=sum(q_i), A_signed=2M+product(q_i-1), T_signed=B_signed+4.
Two dirty roots; all A/B ports=0.
```

The replaced signed word used q0+2q1+2q2 B and q0+q1+2 transfers. The saving
is `(q1+q2)*b-(q2+2)*tau`; it weakly dominates that word when b>=tau. Equal
blocks give **40% fewer B calls**. At n=15, 160 B/66 transfers become
96 B/100 transfers, with the same 95,325 A calls.

Read counts are sharp in the declared one-active-block geometry: two prefixes
touch at most two blocks, so three-block masks need three reads, other masks
two. At that floor both signatures must be exposed at each nonzero vertex,
requiring B-3 switches. [certify_frames.py](certify_frames.py) checks all 384
phase-order/sign/entry cases with complete radius-eight SL2(Z) BFS and separate
literal radius-four halves, no height cutoff. All 144 endpoint distances agree;
minimum boundary cost is seven. Thus B+4 is optimal **within that fixed
triangle/one-switch-per-vertex geometry**, not over arbitrary programs.

Every forward parent coefficient has absolute value at most one; root/output
dirt l1 norm is at most two, and source terms enter outputs positively once.
For |d_p|<=D, |B_j x_j|<=beta_j and induced infinity norm alpha_m of A_m,
roots are bounded by `2D+max_block sum(beta_j)` and output prefixes by
`|y_m(initial)|+alpha_m*(2D+sum_selected beta_j)`. These are parent bounds;
child-private work, rounding and physical precision still need separate charges.
[verify_signed.py](verify_signed.py) checks every prefix for n3..12.

Exact signed examples with a=tau=1 and the locality lower bound:

| n | b | Every one-root word >= | Triangle | Guaranteed saving |
|---:|---:|---:|---:|---:|
| 9 | 49 | 2,638 | 2,569 | at least 2.61% |
| 15 | 285 | 138,778 | 122,785 | at least 11.52% |
| 18 | 759 | 1,074,672 | 920,257 | at least 14.36% |
| 30 | 46,399 | 4,297,747,752 | 3,360,623,617 | at least 21.80% |

n30 is formula arithmetic, not a materialized word. Explicit emission is capped
at n18; the inductive construction and bounds have no such mathematical cap.
[FRAME-RECEIPT.json](FRAME-RECEIPT.json), [SIGNED-RECEIPT.json](SIGNED-RECEIPT.json)
and [FAMILY-RECEIPT.json](FAMILY-RECEIPT.json) retain exact domains and invoices.

## Secondary: the F2 73-call extension of Math PR1

[Math PR1](https://github.com/conorholds/math/pull/1), package
[bidirectional-universal-five](https://github.com/conorholds/math/blob/623039e5f0c7a7fe090789c79ff7e722f5404e9b/integer-mult-bounds/research/bidirectional-universal-five/README.md),
already gives a six-transfer witness, the 51,900,912-assignment four-transfer
exclusion at 72 A/B calls, and the 72c+6s versus 74c comparison. The different
[CERTIFICATE.json](CERTIFICATE.json) word here is another achieving fixture,
not a new six-transfer result. This section adds only the **73-call exclusion**
needed to extend that comparison to arbitrary call counts.

At five sources/31 targets the generic operator floor is 72. Transfer counts
are even because U/V are odd permutations of the three binary root directions
and the final dirty frame is identity. At zero transfers every source/root
and target/root count is even, excluding 73 calls. The two-transfer possibilities
at 73 calls are one extra A read or one extra B call; [census.cpp](census.cpp)
exhausts both, without imposing even operator multiplicity:

| 73-call domain | Canonical source words | B/C interleavings | Restored assignments | Universal words |
|---|---:|---:|---:|---:|
| 10 B, one three-read target | 945 | 124,740 | 1,740,960 | 0 |
| 11 B, paired targets | 17,325 | 2,702,700 | 18,214,560 | 0 |

For the first domain at least 31 masks including zero must have paired reads;
the single missing nonzero mask is tested against all three dirty-signature
classes. The second domain uses one distinguished triple and four pairs;
11!/(3!*2^4*4!)=17,325. All restoring two-transfer words and physical port
assignments are covered. Literal replay follows normalized restoration filtering;
positive and failed three-read controls execute in every native run.

Thus 73 A/B calls require at least four transfers. For c>0,s>=0,
73c+4s is dominated by 72c+6s when s<=c/3 and by 74c when s>=c/3.
Words with >=74 operator calls cost at least 74c. Together with PR1's 72-call
exclusion and attaining words, this gives **min(74c,72c+6s)** at equal A/B
price c and transfer price s, allowing arbitrary counts. H_word is additional;
unequal-price schedules are not ordered by this theorem.

[PR1812](https://github.com/CrocSwap/integer-mult-bounds/pull/1812) explicitly
asked whether bidirectional transfers lower eight; the credited six-transfer
words answer that question. [Adam Gall PR1915](https://github.com/CrocSwap/integer-mult-bounds/pull/1915)
and [Arham Garg's connector-frame-73-exclusion](https://github.com/CrocSwap/integer-mult-bounds/tree/0fdd7d82/research/connector-frame-73-exclusion)
prove the framed **single-connector** 74-call bound. They are predecessors,
not exclusions in our changed two-root alphabet. The 74-call Richardson fixture
is replayed here as [ONE-ROOT74.json](references/ONE-ROOT74.json).
The 73-call native exclusion has one implementation; its independent written
case split does not constitute a second native enumeration.

### Inherited F2 incidence result: independent census only

[Math PR2](https://github.com/conorholds/math/pull/2), package
[scalable-dirty-connectors](https://github.com/conorholds/math/blob/623039e5f0c7a7fe090789c79ff7e722f5404e9b/integer-mult-bounds/research/scalable-dirty-connectors/README.md), already
proves F2 two roots cannot attain exactly two calls per source/output at n>=6,
using zero-map specialization for larger n. We adopt that simpler argument
rather than claim another all-n obstruction. The retained set/matching/Walsh
engines independently cross-check n5/n6: 945/10,395 source words, 14,175/322,245
two-color cases, 175/0 universal covers and maxima 32/59 including zero.
Three occupied source colors cannot cover a mask meeting all three classes.
These are supporting checks; the obstruction itself is credited to PR2.

## Secondary: minimum-read F2 walk compiler

[walk.py](walk.py) accepts a closed source word with two occurrences per label,
each having a fixed normalized color in {10,01,11}. At cut t its query vectors
are `(l,l*Q(t))` in F2^(n+2). A clean target is `(00,m)`. Exact BFS minimizes
reads for every requested target, with no four-read cutoff; optional requested
subsets preserve unrequested outputs. Emission is capped at n12.

For its **chosen** minimum-read decomposition, the deadline/frame DP considers
every placement at an available cut and every U/V path. States contain a frame
among the six GL2(F2) frames and delivered-generator bits; generators must be
served by their last available cut. Before a source call G*v_j=e0 is required,
so all A/B ports are z0; the final frame is identity. A 65,536-state overflow
raises an error, never a truncated-success claim.

**Transfer cost depends on the decomposition; equal-read alternatives are not
jointly optimized.** For source word `[2,0,1,2,1,0]`, colors `[1,2,1]`, this
compiler uses 14 reads/10 transfers, while the reviewer's literal program uses
14 reads/6 transfers through z0 and restores every dirty row. Both programs
and a missing-transfer failure are checked in [test_walk.py](test_walk.py).
The retained 32/50 transfer bills are not certified minima across decompositions;
the toy counterexample alone does not prove better words for those larger walks.

| n | B | A | Transfers | Query price (a=tau=1) | Every one-root >= | Guaranteed saving |
|---:|---:|---:|---:|---:|---:|---:|
| 9 | 18 | 1,404 | 32 | 2,318 at b=49 | 2,638 | at least 12.13% |
| 12 | 24 | 13,996 | 50 | 16,758 at b=113 | 18,564 | at least 9.72% |

[WALKS.json](WALKS.json) binds literal program hashes and invoices.
[search_walk.cpp](search_walk.cpp) is heuristic discovery, not a proof dependency:
19 three-color partitions at n9/n12, 200,000 proposals each, six relabelings,
114 generic-checked programs in [WALK-SWEEP.json](WALK-SWEEP.json). The n9 read
histogram is 143/354/14 targets using 2/3/4 reads. At n12 fourteen targets need
five reads; the search's optimistic four-read bill was rejected. No global
source-word optimum or impossibility follows from this bounded sweep.

### Within 2.98% at the minimum source-call count

Exactly two B_j calls force a fixed normalized color. Let d(t) bound nonzero
prefix differences of a closed twice-occurring t-label walk. Separate complete
engines give d(5)=30,d(6)=48; otherwise use min(2^t-1,P_1(t,2t)), d(0)=0.
At most three nonempty color classes occur; every partition is considered.

With one color, both two/three-read masks lie in one difference set, so
A>=4M-2d(n). With two sizes a,b, paired coverage P is at most
min(M,d(n)+d(a)+d(b)-n): singleton masks are counted twice. With three sizes
s_i it is at most min(M,sum_i d(n-s_i)-n); pairwise intersections contain
shared-class singletons and the three supports have no nonzero common mask.
For two/three classes, every <=3-read mask has each class component in its
class's difference set, since three-read dirt cancellation uses all three
functionals and each class appears twice. Thus at least
`2^n-product_i(d(s_i)+1)` targets require >=4 reads, giving
`A>=3M-P+2^n-product_i(d(s_i)+1)`.

All twelve n9 partitions imply A>=1369; at b=49 every exactly-18-B word costs
at least 2251 with transfers granted free. The actual 2318-cost word is within
67/2251<2.98% of that class's optimum, irrespective of decomposition improvement.
This does **not** bound programs buying additional B calls, subset batches,
or physical overhead. [WALK-BOUND.json](WALK-BOUND.json) records the full cases.

## Secondary: signed fixed-port parent cache

Reserve n+1 arbitrary dirty parent rows R=z0,C_j=z_(j+1), all excluded from
child scratch. Every operator call uses physical z0; the added paid operation
is T(dest,src,sign), a full-row ADD with distinct endpoints, one being z0.
No clean row, reset, source mutation or inverse matrix is supplied.

Let incoming R=d,C_j=c_j. A Hamiltonian cube path from zero visits every
nonempty mask once, maintains `R=d+sum_(j in m)c_j` by signed cache transfers,
and makes one negative A_m read per vertex. Opposite-parity endpoints admit
such a path: split on a differing bit, choose c neighboring the first endpoint
in its half, join recursively to c and from its cross-half neighbor to the
other endpoint. The halves are disjoint and the connecting edge differs in
one bit; the one-coordinate base is an edge. End at the full mask for odd n;
for even n end at full XOR bit0, then position at full with one extra transfer.
The full mask was already read in that even case.

At the full-sum invariant R=d+sum_j C_j, populate each cache by:

```text
C_j -= R; R += B_j x_j; C_j += R.
```

It changes C_j to c_j+B_j x_j and R by the same response, preserving the
invariant. A closed reflected Gray cycle starting at full now reads each
nonempty mask positively from `d+sum_(j in m)(c_j+B_j x_j)`.
The two A_m reads cancel the same arbitrary dirt and add the requested images.
At full, repeat the three-line update with inverse B_j to unpopulate caches,
then subtract all n restored C_j from R. Every source/root is restored.

```text
B=2n; A=2M; T=2M+1+[n even]+5n; roots=n+1; persistent rows=2n+M+1.
```

The old path takes M+[n even] transfers, the new cycle M+1, population/cleanup
4n, and final restoration n. The written induction holds for all n>=1;
explicit emission is capped at n18. Generic single-injection/reader dirt
arguments give every allowed root count the operator lower bound 2n*b+2M*a.
This construction attains both operator floors, paying its remaining transfers.

At a=1,b~sqrt(2M), its cost/M tends to 2+2*tau for fixed tau. At tau=1/4 the
limiting query savings are 37.5% versus one root and 16⅔% versus two. At
**tau=1/n²->0**, it matches the any-root 2M lower limit, giving 50%/33⅓% versus
the one/two-root optima. This last claim requires A to cost much more than a
full-row transfer; there is no proof that an actual caller has those prices.
The extra n-1 dirty rows versus two roots and all H_word charges still apply.
[CACHE-RECEIPT.json](CACHE-RECEIPT.json) retains the finite exact examples.

This is **not a better F2 cache invoice** than Math PR2's star: at n>=4 that
family uses n-3 roots and 8(2^(n-4)-1) transfers when its distinct source ports
are admitted. The additional cache scope here is signed characteristic zero,
all n>=1 and every operator call at z0. No priority for the operator floors,
Gray paths or dirty-cache cancellation is claimed.

Parent coefficients have absolute value <=1 but dirt l1 norm can reach n+1,
versus two for the triangle. With |d|,|c_j|<=D, roots are bounded by
`(n+1)D+sum_j beta_j`; output prefixes by
`|y_m(initial)|+alpha_m*((n+1)D+sum_selected beta_j)`.
[verify_cache.py](verify_cache.py) checks generic n1..12, every forward prefix,
683 paths, 1272 separate integer/F2 matrix cases, inverse/omission/sign/port
controls. No cache runtime benchmark or physical supplier admission was run.

## RAM checks of the tariff regime

[benchmark.py](benchmark.py) uses dense B and identity A, not a representative
integer-multiplication workload. Signed B traverses Theta(w²) coefficients;
identity A performs Theta(w) updates, so b/a grows with width by construction.
The signed crossover therefore tests this tariff regime, not independent
performance outside it. Width128 is the implementation cap and the only
positive signed point. F2 A is one big-integer XOR; its timings heavily reflect
Python instruction dispatch. Native tape/owner/precision costs are excluded.

Both B coefficient traversals execute, arbitrary private work is restored,
and separate direct forward/inverse checks precede timing. At n15 the comparator
screens all count-Pareto one-root partitions (24 F2,23 signed), then takes the
fastest of three finalists with nine fresh alternating samples. Data/maps match;
the candidate admits an extra dirty root. Input copying is timed (deep copies
for signed arrays); shared coefficient/input/program preparation is excluded.
Copying tends to shrink differences. Results are host-load-sensitive, without
confidence intervals or unrestricted-comparator optimality.

| Field | Width | Best reference blocks | Reference median | Palette median | Speedup | Time saved |
|---|---:|---|---:|---:|---:|---:|
| F2 | 64 | 7,8 | 12.342 ms | 11.445 ms | 1.08x | 7.27% |
| F2 | 128 | 3,3,4,5 | 14.772 ms | 12.253 ms | 1.21x | 17.05% |
| F2 | 256 | 3,4,4,4 | 17.484 ms | 15.659 ms | 1.12x | 10.44% |
| signed | 32 | 8,7 | 166.726 ms | 194.327 ms | 0.858x | -16.55% |
| signed | 64 | 8,7 | 380.732 ms | 405.463 ms | 0.939x | -6.50% |
| signed | 128 | 8,7 | 982.620 ms | 821.980 ms | 1.195x | 16.35% |

[BENCHMARKS.json](BENCHMARKS.json) retains every positive/negative measurement,
including superseded variants. [test_families.py](test_families.py) checks all
23 relevant function hashes and rejects altered measured source. These pins
bind shipped methods, not an authentication of timing data. No multiplication
runtime, floating-complex timing or cache-family speedup is claimed.
Within the one-root Gray-block reference family, n18 at b=800,a=tau=1
reduces tariff from 1,119,096 to 928,125 (17.06%); this is not an all-word
comparator lower bound.

## Retained caller screen

[screen_caller.py](screen_caller.py) extracts a source-bound interface included
in the selected manifest: eight distinct rank-eight centre charts, 112 signed
two-source targets, 224 additions, 24 patterns and a graph of two disjoint K4s.
Its retained forward word has eight private copies, sixteen clears and eight
centre descents. Those clean/owned buffers and sparse targets are a different
contract from our universal arbitrary-dirty-root batch. Complete chart, port,
recursive/head/stock and precision costs must be established before adoption.
This is **not a census of currently dispatched providers**, an endpoint/native
owner replay or a selected cold replay. [CALLER-SCREEN.json](CALLER-SCREEN.json)
records that scope; no supplier replacement or kappa follows.

## Reproduce and verification limits

All commands use Python's standard library; no package installation is needed.
From this Math repository root, set p to the package path below and run serially:

```sh
p=integer-mult-bounds/research/bidirectional-connector
python3 -I -O -B "$p/verify.py"
python3 -I -O -B "$p/independent_check.py"
python3 -B "$p/verify_families.py"
python3 -B "$p/certify_cost.py"
python3 -B "$p/verify_signed.py"
python3 -B "$p/verify_walk.py"
python3 -B "$p/verify_cache.py"
python3 -B "$p/screen_caller.py" --repo /path/to/pinned-upstream-checkout
```

For the official hook, copy the package into an isolated CrocSwap checkout at
research/bidirectional-connector and run:
`python3.12 -B scripts/research_package.py --package research/bidirectional-connector`.
[VERIFY.json](VERIFY.json) declares the eight commands and deadlines; walk replay
has a 120-second deadline for CI headroom, not a mathematical search cutoff.

Default `certify_cost.py` freshly runs the two Python n5/n6 engines and binds
the native receipt to census.cpp; it explicitly reports native **NOT_RUN**.
Fresh native enumeration requires `certify_cost.py --full`, Clang/GCC C++17.
On this host the installed compatible SDK was selected explicitly with
`--sdk /Library/Developer/CommandLineTools/SDKs/MacOSX15.2.sdk`, no global change.
The stored full replay covered 71,856,432 restored assignments, including
PR1's duplicated 72-call domain. The 73-call part has one native implementation.
No hosted-CI result is claimed. `make selected-record-check` checks source
integrity, not the complete multiplication theorem or selected cold replay.

Receipt writers use explicit --write-receipt; fresh native COST regeneration
also requires --full. `verify_families.py` runs 11 family, six original and
384 frame controls; `verify_walk.py` runs ten regressions. No weaker tests or
regenerated timing evidence replace the original records. The PR9 agent review
reported independent rectangular/degenerate-map, bound and native replays;
its scratch artifacts remain local-only, not independent human/formal review.

## Sources, status and attribution

Scientific inputs and selection remain pinned to original main
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, task connector-alphabet-change,
revision3/nonce4097e9f6a5c8e30cb7274114770e40f8. The refreshed canonical snapshot
is `0fdd7d82`; all mathematical inputs and the selected record still match.
Only the originating catalogue changed (now priority4), so its original pin
remains historical provenance. Refreshed guidance was read; review corrections
continue this task, without a reroll or touching frozen sources.

[SOURCES.json](SOURCES.json) records the byte-identical **merged PR1615** witness
(merged 2026-10-14 15:43:33Z), checked against refreshed main. It is replayed
as an eight-transfer comparator; its one-way native exclusion is not imported.
**PR1887 merged at 16:57:12Z**, and PR1915 at 17:06:51Z. PR1887's fixed-port
five-source two-projection/175-cover result is credited, not called pending or
concurrent. The distinct contributions here are the all-word priced bounds,
signed triangle and explicitly limited secondary extensions/cross-checks.

[TASK.json](TASK.json) preserves historical overlap searches and their limits,
plus the PR9 review response. Inspected nearby work includes PR1811,1707,1708,
1717,1719,1954,1968,1972,2045,2050,2060 and Discussion2053; their targets or
allowed resources differ. Historical no-match reports are not novelty proofs. A fresh canonical-main and
live-overlap checkpoint is recorded in TASK.json for this submission.
The scientific package and review corrections are archived in Math PR9/PR11.
The user has explicitly approved submission of this package for upstream
mathematical review. The selected frontier is unchanged.

## Open next questions

1. Bind one actual caller with expensive B, cheap A, offline targets and aligned
   paid root transfers. Charge extra stock, routing, precision/tape and all
   H_word terms; adopt only if the complete overhead fits the query saving.
2. Optimize across minimum-read decompositions at a fixed source walk, rather
   than only read placements, or bound cache transfers at positive prices.
   Establish a complete small state model before expanding synthesis; neither
   present routine claims an unrestricted transfer optimum.

## Credit and license

Prepared for conorholds with substantial OpenAI Codex assistance in
proofs, census, construction, both checkers, tests and writing; no subagents.
New material and the retained PR1615 certificate are Apache-2.0 under
[LICENSE](LICENSE). Retain Richardson PR943/934 for the universal prefix model,
read-only repair and Gray-block lineage; the six-source package by Douglas Colkitt and its
independent PR1215 audit for the preceding finite boundary; woklerx PR1438,
Gareth Davidson/bitplane PR1498, Cinna Davis Discussion1412 and Hanson Sun/bbMisk
PR1615 for the one-way root family; PR1767 for its complementary audit;
PR1812 for the bidirectional-transfer question; Adam Gall PR1915 and Arham
Garg's connector-frame-73-exclusion for the framed one-root 74-call bound;
and Cinna Davis PR1675, Charles Bethin PR1637 and Richardson PR944/1651 for
related signed bidirectional work. Retain martinxxx9 PR1088 and Hanson Sun
PR1526/1556 in the signed-query and paid-scaling lineage. Credit Cinna Davis's merged PR1887 for
fixed-port two-projection frames and the independently matching 175-cover
census. Adam Gall PR2065 is credited for the independent six-transfer endpoint.
Math PR1/PR2 are credited above for the six-transfer baseline and
all-n two-root incidence obstruction; neither is claimed as new here. No priority for Gray codes, elementary
compute/uncompute or dirty XOR cancellation is claimed. Retain shhxera/CubeJerry
PR889 and Chafik Boukhalfa PR628 in the dirty-commutator lineage. The selected
Rohan Arun/Jeremy Kothe construction and its cumulative credit remain unchanged.

All-size compiler, common-label/mutable-source realization, native owner and
whole-call hosting, precision/tape, exact recovery and outer analytic
obligations remain uninstantiated. Exact local identities and priced research
constructions are not a complete multiplication theorem.
