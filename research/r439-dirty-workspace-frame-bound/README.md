# R439 B-block frame bound with arbitrary dirty workspace

**Scoped obstruction; no new κ or supplier adoption.** The ten pinned PR1062
phase-B maps force every one of their 114 original wires to exit at its
rank-four block frame, even with any finite number of independent dirty
auxiliary wires and arbitrary reversible nonlinear Boolean gates. The exact
minimum **original-wire block invoice** is

\[
93\,2^q+10\,3^q,\qquad 0<q=1-a<1,
\]

with 103 positive climbs and rank mass 216. The original words attain it.
Auxiliary frame work cannot reduce this bill. With fixed outside visits and
the **same caller width, role normalization and other charges**, neither can
it lower the complete frame moment. A new role count, hosting scheme, precision
charge or supplier contract needs separate pricing.

The new contribution is the dirty-workspace closure and reversible nonlinear
extension of the credited dual frame invariant, plus an exact ten-block
instantiation. It is **not** a new inverse-column argument or a new solution
of the original-wire B508/B509 exceptions:

- Arham Tahir's [PR1368](https://github.com/CrocSwap/integer-mult-bounds/pull/1368)
  supplies the forward-span obstruction, ten block interfaces and prefix test.
- Andrey Mas's [PR1511](https://github.com/CrocSwap/integer-mult-bounds/pull/1511),
  head f247c4e17b19e55c0db0ec8a1b660fd118adf014, proves the general XOR
  inverse-column invariant and closes B508.
- Ali Romman's [PR1128](https://github.com/CrocSwap/integer-mult-bounds/pull/1128),
  head df29b159239b79d7e451d6ddda826a73e0e50a67, already permits arbitrarily
  many restored dirty registers in its linear restoration/erasure boundary
  theorem. Its earlier-cut helper endpoints differ from these B-block maps.
  This package claims no priority for linear dirty-workspace bounds.
- CubeJerry's [PR1535](https://github.com/CrocSwap/integer-mult-bounds/pull/1535),
  head 274dc01bbe537da6b3173fd8da2512860b5e0626, and the credited independent
  [PR1576](https://github.com/CrocSwap/integer-mult-bounds/pull/1576), head
  7fdf558a8e4bcf9e98642e9ba688bc66b6629e86, already close B509.
  Cinna Davis's later [PR1778](https://github.com/CrocSwap/integer-mult-bounds/pull/1778),
  head 84f0d0b8565dccc7418183c3ad2c6ea0552e3856, corroborates B508.

## Exact scope and proof

Fix one block's invertible binary map M, named original wires, entry frames
S_i and rank-four frame F. The original inputs and every auxiliary input
range over the **full Cartesian product** of bits. There are no promised
zeros or correlated inputs. A finite straight-line circuit consists of local
bijections on fixed sets of wires; all operands, including read-only controls,
are promoted to one common containing rational frame. Frames grow by inclusion
and stay inside F during the replacement. No reset, erasure, special
COPY/ERASE interface, frame descent or uncharged external read is allowed.

Every original output must equal Mx for every auxiliary input z. For the lower
bound we even permit an arbitrary auxiliary output G(x,z), provided the complete
circuit remains reversible. This is a relaxation of a restored-workspace caller,
not permission to discard information. Actual restoration, holding and delivery
costs remain charged.

**Semantic dual invariant.** Let T_t be the bijection from all initial values
to current values, and let E_i(t) be wire i's current frame. Define essential
dependence in the usual full-domain sense: changing just one input coordinate
can change the indicated output. Then

\[
E_i(t)\supseteq S_i+
 \sum_{j:\,(T_t)_i\text{ depends on }x_j}S_j+
 \sum_{j:\,(T_t^{-1})_j\text{ depends on }y_i}S_j. \tag{1}
\]

This is PR1511's row/inverse-column invariant with semantic dependence in place
of linear coefficients. Initially it holds for the identity map. Frame-only
promotions preserve it. At a local bijection g on operand set K,
\(T_{t+1}=g\circ T_t\) and \(T_{t+1}^{-1}=T_t^{-1}\circ g^{-1}\).

A new forward component on K can only depend on the union of the old forward
dependencies on K. If a new inverse component depends on coordinate i in K,
that inverse component previously depended on at least one coordinate in K:
substitution by g inverse introduces no variables outside K. The old invariant
places every associated S_j in at least one old operand frame, hence in the
common new frame of **every** operand. Coordinates outside K gain no forward
or inverse dependencies. Monotonicity retains each own S_i. This proves (1)
by induction for every finite circuit, including nonlinear reversible gates.
The same reasoning works over any finite common alphabet; the instances here
are Boolean. Finite checks below support, but do not replace, this proof.

**Dirty-workspace closure.** The endpoint is a bijection
\(T(x,z)=(Mx,G(x,z))\). For every output pair (y,w), its inverse has original
coordinates **exactly** \(x=M^{-1}y\), independently of w. Thus original
forward dependencies are the rows of M and original inverse dependencies are
the columns of M inverse, irrespective of the number, mixing or final values
of the auxiliary wires. Additional inverse dependencies from recovered
auxiliary values can only strengthen (1). Consequently every original exit
must contain

\[
L_i=S_i+\sum_{j:M_{ij}=1}S_j+\sum_{j:(M^{-1})_{ji}=1}S_j. \tag{2}
\]

The certificate verifies \(L_i=F\) for all 114 original wires. Since replacement
frames stay inside F, each exit equals F. The full-product and reversibility
hypotheses are essential to the inverse step.

| Frame | Original wires | Minimum positive block climbs |
|---|---:|---|
| 506 | 10 | 5H2 + 3H3 |
| 507 | 10 | 3H2 + 3H3 |
| 519, 520, 521, 522, 523, 524 | 12 each | 12H2 each |
| 508 | 11 | 6H2 + 2H3 |
| 509 | 11 | 7H2 + 2H3 |
| **Total** | **114** | **93H2 + 10H3** |

Here H_r denotes one paid rank-r child. The original-wire conclusions and
instance constants are predecessor evidence, recomputed here.
Forward dependencies alone force 112 exits. For source 19 in B508, the inverse
support is [19,35,66,89,97,466], with wire 466 initially on F508. For source 22
in B509 it is [17,22,33,38,77,87,468]; wires 17 and 468 start on F509.

**Complete frame accounting in this fixed interface.** A wire entering at rank
e must accumulate rank increments d_k summing to 4-e. For 0<q<1,

\[
\sum_k d_k^q\ge(\sum_k d_k)^q=(4-e)^q. \tag{3}
\]

For positive total D, divide by D^q and use t^q >= t on [0,1].
Equality holds for a single positive climb; two positive increments make it
strict. The baseline uses that single climb on every original wire. All
original exits equal the baseline exits, so the unchanged continuation has
exactly its old frame charges and scalar boundary.

Dedicated additional workspace contributes nonnegative frame charges. For a
borrowed existing wire unused by the baseline during the replacement, keep its
outside frame visits fixed. New promotions between its old entry E and next
fixed visit H must lie between E and H; otherwise the fixed continuation is
illegal. They merely split the baseline jump dim(H)-dim(E), so (3) shows their
complete contribution through H cannot decrease. Apply this between consecutive
fixed outside visits. If there is no later fixed visit, the baseline holds E
and added promotions again have nonnegative cost.

Thus the whole frame invoice is bounded below by the baseline, with the same
normalizing factor \(64^{-q}/W\). This comparison does not increase W to obtain
an allowance for extra workspace. If added roles change W, the host layout or
other charges, no normalized supplier-moment conclusion follows from this
package. Simultaneous replacements require the pinned original entry contracts
at every block; using an earlier block to change a later entry is a
cross-boundary mechanism outside the result.

## Replay and finite evidence

Python 3.12, standard library only:

~~~sh
python3.12 -I -B scripts/research_package.py --package research/r439-dirty-workspace-frame-bound
~~~

The registered commands run both checkers and tests with -I -O -B.
Expected markers are PASS_R439_DIRTY_WORKSPACE_FRAME_BOUND,
PASS_R439_DIRTY_WORKSPACE_ORACLE, seven passing test groups, and
PASS_REGISTERED_RESEARCH_PACKAGE.

[verify.py](verify.py) reconstructs the ten maps and actual entry labels from
the pinned PR589 and PR1062 candidate words. It uses binary elimination and
rational row reduction. It compares the previously published block data only
after reconstruction. All 661 ordered frame paths agree between the two words:
ADDs 24,305 -> 11,500, with unchanged local profile
{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}, rank mass 5,129 and nine rank-seven
COPY charges. It checks the literal cleanup shape; it does not replay the
entire word's scalar map.

[oracle.py](oracle.py) imports no primary or predecessor code. It:

- replays 61,440 complete Boolean block inputs across the two source words;
  obtains inverse tables by permutation inversion and essential dependencies
  by paired inputs;
- checks all 228 rational-span witnesses with integer Gram determinants
  (all are 64), using a separate integer elimination for entry and support ranks;
- checks 122,880 dirty-workspace inputs for ten nonlinear auxiliary echoes and
  their garbage-output relaxations; the extra zero-dimensional auxiliary
  pays one rank-four climb per block;
- checks all 8! three-bit prefix bijections followed by each of six CNOT or
  three Toffoli gates: 362,880 forward/inverse dependency steps;
- checks all 1,536 three-bit bijections with one or two prescribed original
  coordinates and arbitrary invertible workspace fibers.

Both implementations were written in this same assisted session; this is
implementation separation, not independent human review.

Seven test groups include six actual on-disk certificate corruptions rejected
by **both** engines, actual source-byte corruption, optimized execution from a
relocated package and source tree with no file writes, and semantic controls.
Destination-only promotion violates the inverse obligation. Frame descent
violates the retained own label. A clean-only auxiliary copy passes when its
incoming bit is zero but fails for arbitrary dirt. A Toffoli fixes zero and
every one-hot input while failing an identity contract on other inputs.
Resetting an auxiliary destroys the required bijection. These controls make the
hypotheses visible; none is a counterexample to the stated theorem.

## Limits, next question and credit

The exact base is 0b1cccf86e2f5132ed286a26ef0a681a495740ea; source Git blobs and
SHA-256 values are in [SOURCES.json](SOURCES.json). The selected record remains
the conditional PR1094 result, κ=0.001672660197076918, with the complex side
binding. PR1062's H2/K adoption gap remains separate. This package is not a
complete selected cold replay, a physical COPY/ERASE or native multistage
replay, a replacement supplier contract, a formal proof-assistant result,
a precision/tape proof, or a new multiplication theorem. It establishes no
scalar gate optimum or impossibility outside its frame/interface model.

## Open next questions

Can a particular cross-block interval change one original entry frame enough
to lower its complete invoice? This matters because dirty workspace alone
cannot change the pinned frame exits. First select a specific interval that
changes donor 466 before B508, or donor 17/468 before B509; recompute both
directions' essential dependencies and price every new entry, exit and outside
visit before synthesis. The blocker is a source-bound interval with a favorable
full budget. More resynthesis within the closed interface is not proposed.
Clean/correlated inputs, nonreversible gates or a different COPY contract require
separate proofs and full costs. Structured questions are in [TASK.json](TASK.json).

Additional related work: the incorporated
[fixed-prefix cleanup bound](../bit-cleanup-frame-obstruction/README.md) already
allows nonlinear gates and scratch for its forward-dependency argument.
Jose Manuel's [PR1757](https://github.com/CrocSwap/integer-mult-bounds/pull/1757),
head 78a1810e44bf08f845252cfe4c785ccc967c07a2, proves a different nonlinear
common-flag cut bound. Neither is claimed anew here. This package concerns
the dual essential-dependency condition at these fixed B-block boundaries,
without a common-flag premise.

Credit the above predecessors and Aaron Wang (PR1015), Ross Richardson
(PR923), Sagar Thakrar (PR1062), Sricharan Vagvala (PR967), Gareth Davidson
(PR915/926), DreamingOfClouds (PR589), eumemic (PR555/543), and the retained
frame/compiler lineage. Prepared by Ross Richardson with substantial OpenAI
Codex assistance; no subagents or independent human review. Apache-2.0.
[Discussion 1795](https://github.com/CrocSwap/integer-mult-bounds/discussions/1795)
records coordination.
