# Proof and review boundary for paid clones on PR53 skip-prefix graphs

The pinned finite construction targets
T(n)=O(n*(log n)^(1-kappa)) with **kappa=141532521/3125000000000** and bit saving
**a_b=1132311451/25000000000000**. This is a **0.686876%** improvement over PR53. Fresh finite replay has
passed for both dimensions; the complete verification and source freeze
remain reproducible through the commands in the README. It inherits the mathematical
interfaces in [the copied/fixed proof](../copied-fixed/PROOF.md), pinned by
`SOURCE.json`; those interfaces remain conditional hypotheses, not results
proved merely by executing this directory's tests.

## The finite construction and its semantic invariant

Take a=23, b=25, m=575. Source lines are indexed by triples, with
v_h=binomial(h,3), rational address metric G_h=I-J/9, and bit payloads
over F2. Address-field and payload-field arithmetic remain distinct.

The base is the unchanged PR53 graph at commit
`3ffd4021995c959ac02d12920e0279ae97dd03c7`, by **Avi Eisenberg with
Anthropic Claude Opus 5.5 assistance**. `cloned_graph.py` imports its
pinned `research/skip-strips/skip_graph.py` and then replays the new paid
clone jobs. Its paired exclusion construction uses a skip-prefix layout
for every leave-one-out strip vector. If A_i and B_i are the usual prefix
and suffix sums, the ordinary side output omitting v_j is
A_(j-1)+B_(j+1). PR53 computes it as
A_(j-2)+(v_(j-1)+B_(j+1)), with the explicit boundary cases in its generator.
Associativity and the disjoint index ranges show this is exactly the same
indexed leave-one-out sum. The total and every omitted-point output retain
their exact scalar meanings.

The new placement makes successive prefix and side consumers have nested
covers, and provides further nested suffix continuations. These explain
why more carrier matches become available; all selected matches are still
checked individually. At the top level PR53 reverses the value list;
at deeper levels it uses PR48's support-based order and restores original
output indices. Its totals retain PR48's rules, and global common-point
orders retain RaD's alternating construction. This increment adds no new
schedule bits, point-order choices, source dimensions, or tensor basis.
The complete inherited skip-prefix argument is retained in
[PR53's proof](../skip-strips/PROOF.md), with its original attribution.

For a common core C and cover M, retain the original rational envelope
E(C,M)={x: supp(x) subset M, x_i=t for i in C, sum_i x_i=3t}. It has rank
|M|-|C| for an addition, with |C| in {1,2}, and lies in a nondegenerate
common-point hyperplane. Side outputs are orthogonal to their target
triple line; center envelopes have rank h-1. The inherited envelope
formula and exact bounded-minor certificate apply to every such core/cover
configuration; they do not depend on a particular summand order.

## Paid source-partition clones with original envelopes

The extra operation is a specialization of RaD / hipotures's PR51 paid
whole-chain cloning construction, developed with substantial OpenAI Codex
assistance. It is applied after the unchanged PR53 skip-prefix construction.
Every existing gate keeps its literal original envelope E(C,M), and each
clone receives exactly the original envelope of its parent gate.

Choose an addition x with at least two independent result-carrier chains.
Let f be the first use of one selected chain. Find two distinct previously
unused provider gates g1,g2, both earlier than f in the actual rank/node
chronology, and operands y,z consumed by these providers. Require exact
disjoint scalar supports supp(y) union supp(z)=supp(x), with empty
intersection, and require their core intersection and cover union to equal
x's original core and cover. Require E(g1) and E(g2) to lie in E(x).
Insert the paid addition x'=y+z immediately before f and redirect every
use of that complete continuation chain from x to x'. The original x
retains at least one other chain. No partial continuation chain is moved.

The new sum has exactly x's scalar form and original envelope. Its operand
frames fit E(x) because they fit their provider frames, which fit E(x).
All moved consumers previously contained E(x), so they still contain the
new producer's frame. Providers are earlier than the insertion point;
source operands retain their original producer identity in this conservative
specialization. The replay explicitly rejects a provider operand that was
itself redirected by another selected clone. Thus no circular source
substitution or unavailable earlier value is assumed. Disjoint job chains,
distinct unused provider capacities, and exact topological reconstruction
are checked before every resulting output is re-expanded in global source
coordinates.

Retain provider g1 at the first actual input use of x', and g2 at its
second. These are new, distinct uses; each provider capacity was unused.
Transport every old selected continuation together with its complete
chain. The two added continuations preserve their actual source operand,
are causal, and have nested original envelopes. Hence for each clone the
addition count rises by one, q is unchanged, and the legal retained-link
count rises by two: R=c+q-mu falls by exactly one. This is a charged new
scalar gate, not a free identification of two dirty carriers. The final
selected matching may be recomputed, but every selected use and the full
physical word must then pass the independent recount and compiler again.
The complete dirty-basis check supplies the semantic guarantee for arbitrary
old auxiliary contents; equal scalar supports alone would not supply it.

At h=23 the two rounds add 241+12=253 gates; at h=25 they add
340+13=353 gates. All **606 new gates** and **1,212 added retained links**
are accounted for. The final finite counts are:

| h | Additions c | Designated uses q | Matched links mu | Roles R |
|---|---:|---:|---:|---:|
| 23 | 40,582 | 5,336 | 13,225 | 32,693 |
| 25 | 53,828 | 6,925 | 17,697 | 43,056 |

The complete fixed I+J profiles are recomputed on these actual new DAGs and
selected matching uses. Their unmodified rank masses are 752,951 and
1,077,600; copied centers reduce them by 506 and 600 respectively. Every
source triple, center endpoint, common tensor basis, data-pair geometry,
paid endpoint correction, complex phase, and assembly interface remains
unchanged. The original-envelope projector and bounded-minor argument below
therefore apply directly. PR51's enlarged signed positive frames and negative
basis are not inputs to this construction.

## Actual role allocation, physical word, and finite gates

Let c_h be additions, q_h designated uses, and mu_h selected continuations.
The number of physical roles is R_h=c_h+q_h-mu_h and retained-center loss is
ell_h=h(h-1). A continuation is allowed only along the profiler's original
causal-order and nested-envelope relation, with no repeated donor or
recipient use. Selected matching edges are finite inputs. Search scores
and approximate matching objectives are not proof inputs.

For each h, `producer.py` must pass all of the following independent gates:

1. Rebuild the exact PR53 graph and replay the pinned integer clone-job files,
   verify every scalar output, and export the actual binary DAG.
2. Expand additions into dense global triple bitsets; check disjointness,
   exact common core and cover, nested operand envelopes, every designated
   output, and exactly h retained centers.
3. Validate the matching binary structure and injectivity in Python,
   independently recount every selected use, and then pass it to the C++
   profiler. C++ independently requires every edge to be admissible.
4. Reconstruct every actual transition's fixed I+J rational profile,
   compare modular ranks, and check the inherited exact minor bounds.
5. Compile every physical role trajectory from the exported DAG and selected
   uses; check terminal uniqueness, source and output coefficients, every
   frame containment, reverse-complement incidence, and copied rank mass.
6. Apply the full chronological XOR word to the complete formal basis of
   inputs, targets, and all dirty auxiliary roles. Both forward and reverse
   complementary orientations must produce the required shear and restore
   every auxiliary exactly. These are full finite linear checks, not random
   dirty-state tests.

Writing files with `--write` does not by itself certify them. After they
are frozen, ordinary replay compares every generated scalar/profile/timeline
record with its pin. Verification checks the source manifest before replay
and never regenerates it. The separate exact witness also checks that
all counts are nonnegative integers, original and fixed rank sums agree,
zero-width blocks are absent, and exactly h full center cleanup blocks
exist before the copied-center modification.

The scalar injection V, mixer L, and scatter J satisfy JLV=I. For an
arbitrary dirty auxiliary vector z, the word L,J,L^-1,V,L,J,L^-1,V
scatters JLz+JL(z+Vx)=x and restores z. The independently compiled
complete-basis test checks this finite word and its dual. The inherited
ordered-affine physical realization is still a separate mathematical
interface requiring review.

## Copied centers, fixed profiles, and complete cost

Retain the copied-center replacement in both orientations. For each center,
replace its original full h-block by a singleton while retaining the
transformed copy's charged profile. The rank-mass reduction is h-1 per
center, not twice h-1. Copy, read, erase, and parking passes remain paid.
The N separate rank-one endpoint corrections remain paid as well. These
are the same complete role streams used by the inherited fixed-tape
construction; this increment adds no independent row index or gather.

The explicit envelope projector formula and its rank-two/three/four
corrections are unchanged. The inherited exact CRT argument bounds every
minor numerator strictly below the selected modulus product and proves
denominator invertibility. A nonzero modular minor proves nonzero rational
rank; a supposedly nonzero minor vanishing modulo all selected primes
would contradict the strict numerator bound. This certifies ordered zeros
as well as nonzeros. Only consecutive increasing pivots form a contiguous
recursive child. No separated pivots are gathered.

The compatible tensor basis, all-weight geometry, physical offsets, and
data corner proof are inherited unchanged. The primary modular sweep
certifies 4,073,290 triple pairs; direct rational elimination recovers the
other ten with all 47 prescribed pivots and 346 required ordered zeros
per pair. Hence all N=4,073,300 data pairs have the profile
9 singletons +21+17+481. No pair is dropped. `base.data_corners()` replays
the exact finite data recovery; source hashes pin its proof interfaces.

Write B_a=v_b R_a, B_b=v_a R_b,
W=2N+B_a+B_b, and L=v_b ell_a+v_a ell_b=2,226,400. The complete child list is

| Class | Multiplicity | Recursive widths |
|---|---:|---|
| a auxiliary exterior | B_a | 23 and 529 |
| b auxiliary exterior | B_b | 25 and 525 |
| Every data macro | 2N | 9 singletons, 21, 17, 481 |
| a local internal | v_b | Complete copied fixed profile at h=23 |
| b local internal | v_a | Complete copied fixed profile at h=25 |
| a data growth | 2N | 1 and 21 |
| b data growth | 2N | 1 and 23 |
| Paid endpoint correction | N | 1 |

The weighted rank is s=Wm-N+L, so the rank deficit N-L=1,846,900 is
independent of the graph and clone choices. Every child width is at most 529<m.
For the pinned candidate R_23=32,693 and R_25=43,056, yielding
W=159,592,676 and s=91,763,941,800. The independent complete-dirty-basis
checks cover 36,235 basis vectors and 310,810 elementary operations at h=23,
and 47,656 basis vectors and 410,536 elementary operations at h=25, in both
orientations. Every selected carrier and fixed-profile transition is replayed.
Changing the graph and selected matching changes the role counts and full child histogram;
neither fewer roles alone nor a favorable floating-point score proves an
improved exponent.

## Exact objective and conditional assembly

For the complete multiplicities n_t, the bit recurrence's characteristic
is M(a_b)=sum_t n_t*t/(Wm)*exp(a_b*log(m/t)). The exact acceptance test is
M(a_b)<1. The integer-outward logarithm series and rational exponential
bounds are the pinned inherited arithmetic routines. The next bit grid
point must have a rigorous lower moment greater than one. The pinned PR53
child list, and any additional contemporaneous comparison list, must
also have lower moment greater than one at the newly claimed a_b. Thus
the improvement is a changed finite construction, not a relabeling of
the previous saving. These comparisons are scoped to the stored networks.

The complex network and its saving a_c=717/10^7 are unchanged, including
all copied-center inverse phases and paid corrections. The finite bridge
retains the full scalar charge G, semantic envelope 64(W_c+m_c+G+1)^3,
completed-child guard, halving degrees, and product-row stock. The balanced
assembly is the inherited physical layout, not an algebraic deletion of
prefix work. Its extra top-axis bits, common low-coordinate groups,
arbitrary-coordinate permutations and inverses, whole active/control/row/
spectator fields, FFT twiddle order, and bulk Gaussian passes remain paid.

The witness uses the same exact assembly parameter formulas and requires
all 47 strict inequalities and seven positive cost margins. It checks the
eventual cutoff conditions, including complete-row padding intervals,
prime setup and exact recovery, and rejects the next kappa grid point.
Only under the inherited analytic and fixed finite-alphabet multitape
interfaces does this yield T(n)=O(n*(log n)^(1-kappa)). Strict margins absorb
the fixed polylogarithms; the inherited fixed-machine extension handles
the bounded range below the eventual cutoff.

## Remaining mathematical review and credit

The ordered-affine partial-swap compiler, fixed-tape cost, copied-stream
parking, complete spectators, common ambient-basis transfer, balanced
positional layout, and semantic/bulk Gaussian/recovery interfaces remain
inherited dependencies. Finite replay supplies evidence for their concrete
inputs but does not prove the all-size machine theorem. No Lean build,
global search optimum, exact weighted-matching optimum, or measured
practical multiplication speedup is claimed.

This increment is by **Chafik Boukhalfa with OpenAI Codex assistance**.
The immediate skip-prefix graph is **Avi Eisenberg with Anthropic Claude
Opus 5.5 assistance, PR53**, building on **Chafik Boukhalfa with OpenAI
Codex assistance, PR43/46/48**. PR44's matching discovery and profiler,
and PR47's summand climbing, are also Rohan Arun with Anthropic Claude
assistance. Point-order and independent role-compiler work are **RaD /
hipotures, PR41**. The copied compiler retains **icekylinx** and **Dominik
Scholz** copyright and Apache-2.0 notices verbatim. The full predecessor
and analytic attribution chain, including James Chang, Zhihao Chen,
Aurel Prosz / Paureel, Swapnil Jain, eumemic, Douglas Colkitt, OpenAI,
David Harvey and Joris van der Hoeven, is retained in the linked inherited
proof and source files. Nothing in this new note supersedes those notices.
The contemporaneous PR50 benchmark is **Rohan Gupta / gupt1156 with
Antigravity assistance**, commit `5581d15c`. Its pinned child list is used
only for exact comparison, not as a construction component.

The paid source-partition / whole-chain clone construction is credited to
**RaD / hipotures, PR51**, with substantial **OpenAI Codex assistance**,
PR head `ee552125fb82c1664740fcc6c5eb97cad74d6bbd` and primary research
commit `6d74d1181a985b5b82debf3eb3e1a7fdbc869671`. This increment supplies
its conservative original-envelope specialization, integration with the
PR53 skip-prefix graphs, exact replay, and the resulting new complete child list.
