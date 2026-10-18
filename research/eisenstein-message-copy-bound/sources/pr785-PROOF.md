# A counting extension of the Hurwitz copy floor

**Scoped result.** For the ten Hurwitz E8 lines, fixed-support, deterministic,
zero-error messages of arbitrary binary widths have minimum charge
`C = sum_t b_t`, when port t demands b_t independent bits and a q-bit message
with reader/source sets R,A is charged `q c(R,A)`. In particular, equal
block width b costs at least 10b quaternionic units, or 40b rational units.
Encoders and decoders may be nonlinear. No bound on the number of messages
is imposed, other than finiteness.

This extends the scalar-total argument of Douglas R. Colkitt's
[#703](https://github.com/CrocSwap/integer-mult-bounds/pull/703), at commit
`358383e2f1b0f292d4d6eb897c06fd8558a4f5e6`. The perfect-matching geometry,
pairing charge, transversal weights and scalar optimum are predecessor work.
The addition here is conditional transcript injectivity in place of binary
rank, together with nonlinear attaining examples and assumption controls.

## 1. Geometry and the pricing premise

Use the E8 roots in doubled coordinates: vectors in Q^8 with either two
entries in {2,-2} and the rest zero, or eight entries in {1,-1} and an even
number of minus signs. Regard Q^8 as H_Q^2 and take the spans of the four
left multiples 1,i,j,k of each root. These are ten four-dimensional rational
subspaces. Their orthogonality graph is five disjoint pairs; write mate(t)
for the unique orthogonal line. Any two distinct lines span Q^8.

For concatenated row bases V_R and V_A, set

    c(R,A) = rank_Q(V_R V_A^T) / 4.

The exact charge table is:

- 0 if a set is empty, or R and A are singletons at orthogonal mates;
- 1 otherwise if a nonempty set is a singleton;
- 2 if both sets have at least two elements.

Two spanning sets have rank-eight pairing. A singleton against a spanning
set has rank four. Nonorthogonal singletons have rank-four pairing; mates
have zero pairing. The verifier reconstructs all roots and line bases,
checks every singleton pairing and every two-line span over the integers,
then checks every support pair against the transversal inequality below.

**Explicit pricing premise:** a message of fixed width q_j, sent from source
set A_j to reader set R_j, is charged `q_j c(R_j,A_j)` quaternionic units.
Charges add over messages. Every transmitted bit is priced, even if the
encoder combines coordinates nonlinearly. This is the chosen block-message
model. It is **not** a derivation of nonlinear physical copy costs from
#446's scalar pairing-rank theorem. A supplier that shares physical work
between message coordinates more cheaply is outside this result.

## 2. Information model

There are independent inputs X_t ranging freely over {0,1}^{b_t}; b_t are
nonnegative integers. Message j has a fixed nonnegative integer width q_j
and is a deterministic function

    Y_j = f_j((X_a)_{a in A_j}) in {0,1}^{q_j}.

The supports, widths and functions do not depend on the input. Every reader
t in R_j receives the same full Y_j; it may process those bits arbitrarily.
Receiver t must reconstruct X_t for **every** input tuple, using its received
messages and free side information X_mate(t). The decoder may jointly use
all those messages and need not be linear. Granting the entire mate input
is an optimistic relaxation of orthogonal residual correction.

Source access, encoding, decoding and side-information preparation are free
in this model. There is no interactive relay, adaptive support, input
correlation, decoding error or additional nonorthogonal side information.
The theorem also covers a scalar fitting decoder from #703: each rank-one
total is one width-one message, and its mate contamination can be removed
using the granted side information. Fixed-support block-linear codes are
included as well, without requiring coordinatewise encoding.

## 3. Transcript injectivity

A transversal T chooses exactly one endpoint of each of the five mate
pairs. For this T define

    J_T = { j : R_j intersects T and A_j intersects T }.

Fix **any** assignment of all inputs outside T. The map

    X_T -> (Y_j)_{j in J_T}

is injective. To see this, suppose two different X_T assignments have the
same displayed transcript. Every message received by a receiver in T is
either in J_T or has A_j disjoint from T. Messages in the latter class are
identical because their source inputs were fixed. Every receiver's mate is
outside T, so all its side information is also identical. Its deterministic
decoder would therefore return the same X_t in both assignments, for all
t in T, contradicting the distinct X_T assignments.

Consequently, counting possible transcripts gives

    2^(sum_{t in T} b_t) <= 2^(sum_{j in J_T} q_j),
    sum_{t in T} b_t <= sum_j q_j a_T(R_j,A_j),                 (1)

where a_T is 1 exactly when both supports meet T. No probabilistic,
asymptotic or linearity assumption is used. The proof is for every finite
block width and every finite number of messages, not an extrapolation from
the truth tables used as controls.

## 4. Average over the 32 transversals

Each line lies in 16 transversals. For every R,A the predecessor inequality
is

    sum_T a_T(R,A) <= 16 c(R,A).                              (2)

If c=0 no transversal hits both supports. If c=1 a singleton support occurs
in only 16 transversals. If c=2 the total number of transversals is 32.
Thus (2) follows in all cases. Summing (1) and dividing by 16 gives

    sum_t b_t <= sum_j q_j (sum_T a_T(R_j,A_j))/16
              <= sum_j q_j c(R_j,A_j) = C.

The bound is sharp in the abstract model for arbitrary b_t: send X_t
directly from {t} to {t} with width b_t. This costs sum_t b_t. For equal
width b, another attaining code broadcasts the five mate-pair XORs in a
single 5b-bit message with all ports as sources and readers. Its charge is
`2 * 5b = 10b`. Apply any bijection of its 5b bits before transmission;
receivers invert it and recover their pair XOR using their mate input.
For example, the reversible update `z_2 ^= z_0 & z_1` makes the encoder
nonlinear and preserves both correctness and charge. The replay verifies
this example on all 1,024 inputs for ten one-bit ports, and a vector example
on all 256 inputs for four two-bit ports in the matching geometry.

## 5. Optimistic complete-budget screen

If, in addition, these b-fold ports satisfy the inherited Dfc stage
accounting with v=10, k=4b and cst=4C, then

    D/T = (s-1) * 40b - s * 4C <= -40b

for every positive integer s and b. Helpers, source access, frame changes,
copies beyond this lower bound, restoration and recursive children were
all granted zero additional expense in this screen. Any nonnegative charge
for them cannot repair its negative deficit. There is no positive supplier
saving to feed into an assembly, regardless of the other supplier.
Accordingly no circuit implementation or kappa optimization is attempted.
The algebraic inequality supplies the all-s conclusion; the receipt's
finite arithmetic examples are only error controls.

The use of Dfc and the conversion from message width to physical rank are
explicit additional assumptions. This note does not establish them for
nonlinear circuits. It does not bound interactive/adaptive codes, variable
length or average-cost communication, fractional physical sub-line copying,
correlated demands, other geometries or different stage accounting.

Prepared by Alexander Templeton (@azide0x37) with substantial OpenAI Codex
assistance in the proof extension, implementation, checks and writing.
This is a written mathematical argument with finite exact checks, not a
proof-assistant formalization or a verification of integer multiplication.
