# Fixed-support nonlinear messages on the Eisenstein E8 lines

This note extends Jonathan Lam's [PR798](https://github.com/CrocSwap/integer-mult-bounds/pull/798)
scalar Eisenstein certificate to finite messages that may mix payload bits
nonlinearly. It uses Alexander Templeton's conditional-transcript argument
from [PR785](https://github.com/CrocSwap/integer-mult-bounds/pull/785), which
treats a different, Hurwitz geometry. Neither method is claimed as new here.
The new result is their composition on the Eisenstein geometry, including
unequal demands, a concentration bound, and explicit nonlinear controls.

## Statement and model

Let the 40 ports be the Eisenstein E8 lines specified below. Port t holds an
independent input X_t ranging freely over all b_t-bit strings, where b_t is a
nonnegative integer. There are finitely many messages. Message j has fixed
source and reader sets A_j,R_j, fixed integer width q_j >= 0, and value

    Y_j = f_j((X_a)_(a in A_j)) in {0,1}^{q_j}.

Every reader in R_j receives the same complete Y_j. Receiver t must recover
X_t on **every** input tuple, using all its received messages and the full
inputs of ports orthogonal to t. Functions and joint decoders may be
nonlinear. Supports, widths and functions are fixed before the input is
chosen. Granting full orthogonal inputs as free side information is an
optimistic model of residual correction.

For line sets R,A, let V_R,V_A be rational row bases of their spans and set

    c(R,A) = rank_Q(V_R V_A^T)/2,
    C = sum_j q_j c(R_j,A_j).

**The charge is a premise of this message model:** every transmitted bit
pays its support pairing rank, and charges add over messages. PR446's
scalar copy-tree interpretation does not establish this pricing for
arbitrary nonlinear physical circuits. Sharing physical work between bits
more cheaply would be outside the result.

Write Q for any clique of pairwise nonorthogonal lines, including singletons.
The following bound holds for all finite widths and message counts:

    C >= max( ceil(11 sum_t b_t / 20), max_Q sum_(t in Q) b_t ).       (1)

In particular, if every port demands b bits, **C >= 22b Eisenstein rank
units**, or **44b rational rank units**. This is a lower bound, not the
optimum decoder cost. Direct messages give the abstract upper bound 40b.

This model excludes adaptive/interactive supports, correlated inputs,
errors, variable-length or average-cost messages, rational sub-line
supports, and additional nonorthogonal side information. It includes
fixed-support block-linear codes, coordinate mixing, arbitrary nonlinear
encoding and joint decoding. It does not assert that every physical
vector-valued circuit has the declared additive charge.

## Exact geometric premise (predecessor work, replayed independently)

Use the 240 doubled E8 roots: two nonzero coordinates in {2,-2}, or eight
coordinates in {1,-1} with an even number of minus signs. Each has norm
squared eight. The root order and four mutually orthogonal A2 pairs in the
certificate match the `standard_e8`/`a2_rotation` object in Joel Pulikkan /
GamingPuzzled's archived PR620. For a root a, its reflection is

    s_a(x) = x - (x dot a) a / 4.

Let J be the product of s_a s_b over the four pairs. The checker reconstructs
J and verifies J^2+J+I=0, J^T J=I, and preservation of every root. The six-root
orbits under ±J are exactly the roots in their rational two-dimensional
spans. They define 40 K-lines for K=Q(omega), in K-dimension four. The
certificate uses `rotation4 = 4J` to keep integer coordinates.

Every line-generated space is J-invariant. So is the kernel of its pairing
with another such space: orthogonality of J gives invariance of X_A^perp.
Domain and kernel therefore have even rational dimension. Thus c is an
integer, independent of the chosen row bases. Pairing rank need not equal
either support's dimension.

The scalar certificate in PR798 assigns weight 1/40 to each of the 40
singletons, and 1/960 to each of the 2,880 seven-line nonorthogonal cliques.
Call these weights lambda_Q. Its geometric inequality is

    sum_Q lambda_Q [Q meets R and A] <= c(R,A).                      (2)

Our implementation imports no predecessor executable code. It reconstructs
the geometry and checks the following integer form of (2) on every pair
of flats F,G:

    24 |F intersect G| + H_7(F,G) <= 960 c(F,G).                     (3)

Here H_7 counts seven-line cliques meeting both flats. The exact census is
772 flats and 298,378 unordered pairs including empty supports. Symmetry
covers both orders. All 30,880 one-line extensions remain in the flat list.
Flats are generated from the empty span by adjoining a line and taking
closure. Every flat has a line basis, so induction on basis size proves
completeness. Closing arbitrary supports preserves their spans and pairing
rank and can only increase clique-hit indicators. Hence (3) proves (2) for
all support pairs, not just the enumerated flat masks.

Every port lies in exactly 504 seven-line cliques, as checked literally for
each of the 40 ports. Its total weight is therefore

    sum_(Q contains t) lambda_Q = 1/40 + 504/960 = 11/20.            (4)

The flat census by (K-rank, cardinality) is

    (0,0):1; (1,1):40; (2,2):240; (2,4):90;
    (3,5):360; (3,12):40; (4,40):1.

The geometric inequality and its scalar application belong to PR798.
This note does not claim a new optimality theorem for clique weights; that
PR also gives a separate dual certificate, which is not needed here.

## Conditional transcript proof for arbitrary widths

Fix a nonorthogonal clique Q and **any** assignment of all inputs outside
Q. Let J_Q be the messages whose source and reader sets both meet Q. Then

    X_Q -> (Y_j)_(j in J_Q)

is injective. If two assignments of X_Q had the same displayed transcript,
each receiver in Q would have the same received messages: omitted messages
have all sources outside Q, so their values were fixed. Each receiver's
orthogonal side information is also outside Q, since distinct vertices of
Q are nonorthogonal. Every deterministic receiver would return the same
X_t in both assignments, contradicting their difference.

Counting input tuples and possible fixed-width transcripts now gives

    sum_(t in Q) b_t <= sum_j q_j [Q meets R_j and A_j].             (5)

This is the argument from PR785, applied to general nonorthogonal cliques.
It uses no linearity and holds for every finite width by proof, rather than
by extrapolating the truth-table controls.

Multiply (5) by lambda_Q, sum over Q, and apply (2) and (4):

    (11/20) sum_t b_t
      <= sum_j q_j sum_Q lambda_Q [Q meets R_j and A_j]
      <= sum_j q_j c(R_j,A_j) = C.

Integrality of q_j and c gives the ceiling in (1).

For the other part of (1), if a clique meets both supports, choose a line
from each intersection. They are either the same nonzero line or two
nonorthogonal lines. The corresponding Gram block is nonzero. Evenness of
pairing rank gives c(R,A) >= 1. Thus (5) directly yields
C >= sum_(t in Q) b_t for every Q. Since b_t >= 0, the largest such demand
sum occurs on an inclusion-maximal clique. The checker enumerates all
2,970 maximal cliques, including the 90 of size four that are not contained
in seven-line cliques.

The concentration term matters: demands supported on a seven-line clique
give C >= sum_t b_t, whereas (11/20) times their total alone is weaker.
No claim is made that (1) is the strongest inequality for every demand vector.

## Nonlinear examples and assumption controls

The seed-41 control chooses an exact partition into ten orthogonal
four-frames. For the first three frames, let z_0,z_1,z_2 be their input
parities. Broadcast to those 12 ports the three-bit message

    (z_0, z_1, z_2 XOR (z_0 AND z_1)).

Receivers invert the last Boolean update. A receiver knows its other three
frame inputs as orthogonal side information, so its frame parity recovers
its own bit. The source and reader spans are full K-rank four, giving
charge 3*4=12. Its mixed Boolean derivative is nonzero, so this encoding is
nonlinear. The verifier exhausts all 4,096 inputs, all 12 receivers and
303,104 conditional transcripts from 74 distinct projections of the
weighted cliques. Adding 28 direct one-bit messages gives a cost-40 code
on all 40 ports. This product extension is justified algebraically; the
checker does not claim to enumerate 2^40 inputs. Independent repetitions
give cost 40b for arbitrary equal b, without claiming optimality.

A second control uses demands 0,1,2,3 on one orthogonal four-frame, sending
each active bit-plane parity only to the ports with that bit. It checks all
64 inputs and 192 transcripts, with charge six and bound four. Inactive
and unequal-width ports are thus exercised explicitly.

Two boundary examples show why the premises cannot be dropped:

- Charging the three-bit nonlinear message just once would cost four,
  below the certified integer bound seven for its 12 active inputs. It is
  the per-bit charge, not a scalar copy theorem, that prevents this.
- Seven pairwise nonorthogonal ports could all recover from one parity
  if each were given the other six inputs for free. Their joint span has
  K-rank four, giving charge four versus the clique demand seven. This
  code is correct on all 128 inputs, but violates the side-information
  premise. The verifier accepts its decoding and rejects its admission.

Twelve rejection controls cover understated widths, undeclared sources,
dropped message bits, constant messages, a missing nonlinear inverse,
illegal side information, underpriced width, a non-clique, the rational
rank conversion, excessive geometric weights, omitted singleton weights
and negative demands. These test mathematical failure modes.

## Optimistic cost screen and remaining obligations

Only if the physical implementation obeys the message pricing and the
inherited Dfc accounting may one substitute v=40, rational port rank 2b,
and cst=2C. Then

    D/T = (s-1)*80b - s*2C <= b*(36s-80).

At three stages the upper deficit is **28b**, which is positive. This
result does **not** exclude a three-stage supplier. The nonlinear cost-40b
example has deficit -80b for every stage count and supplies no saving.
Helpers, source access, encoding, decoding, frame changes, further copies,
restoration and recursive children have all been granted zero additional
expense in this optimistic screen. Any achieved supplier must price them;
none is constructed here. The other supplier and outer assembly are not
replaced or repriced, and no new kappa follows.

This contribution changes no selected record or supplier. All-size realization,
compiler, hosting, precision, tape and analytic obligations are inherited
and unresolved by this finite result. The transcript argument is a written
proof; the geometry has exhaustive finite premises. Neither is a
proof-assistant formalization of integer multiplication.

Prepared by Michael Fischler (@shiftybitshiftr) with substantial OpenAI Codex
assistance in proof development, implementation, verification and writing.
Apache-2.0. See SOURCES.json and NOTICE.md for predecessor pins and credit.
