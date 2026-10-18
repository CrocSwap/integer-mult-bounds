# Conditional transcripts with paid prefix codes

Let the 60 ports be the Gaussian E8 lines of PR738. Each port t supplies an
independent uniform b_t-bit string X_t, with b_t a fixed nonnegative integer.
The receiver for t initially knows all X_u on lines orthogonal to t and does
not know X_t. Source and receiver roles are distinct.

A central encoder, optimistically given all inputs, chooses M=h(X). Distinct
header values have distinct words in a finite prefix-free binary code.
Every receiver and every payload encoder receives M. Header bits are charged
the pairing rank of the **declared full source and full reader spans**, namely 4.
This full public-observation contract is a premise, not an inference that all
possible implementations of a header must cost 4 per bit.

For each M=m there is a fixed finite ordered list of payloads. Payload j has
fixed supports A_j(m),R_j(m), codebook K_j(m), and value

    Y_j = f_j(m, X_(A_j(m))) in K_j(m).

Every K_j(m) is a finite prefix-free set of binary strings, including the empty
word only for a singleton codebook. Each reader receives the entire codeword.
All choices of list, order, supports, functions and codebooks are determined
by m and carry no further input-dependent metadata. Payloads do not relay
previous payloads. Arbitrary nonlinear joint decoding is allowed and must
recover every demand on every input. Declare

    c(R,A) = rank_Q(V_R V_A^transpose)/2,
    C(X) = 4 length(M) + sum_j c(R_j(M),A_j(M)) length(Y_j).

The bases V span representatives and their J-images. Additive per-bit pricing
and this geometry are explicit assumptions; encoding and decoding are free.

PR738 supplies 640 nonorthogonal cliques Q of size 12, each weight 1/192. Each
port lies in 128 cliques. For every support pair,

    sum_Q [Q meets R and A]/192 <= c(R,A).                 (G)

The full geometry replay covers all 2,579,856 nonempty flat pairs. Closing a
support preserves its pairing rank and only increases clique intersections,
so (G) covers arbitrary supports. For any individual nonorthogonal clique,
meeting both supports implies c(R,A)>=1: choose one line in each intersection;
their pairing is nonzero. These are retained geometric facts, not new results.

Fix any such Q and fix X outside Q. Given m, retain only payloads with both
supports meeting Q, in their m-determined order; call their tuple Z_Q. Then
(M,Z_Q) determines X_Q. Any omitted payload received by Q has sources disjoint
from Q and can be recomputed from m and the fixed outside inputs. All free
orthogonal side information is outside Q. Equal retained transcripts would
therefore give equal complete decoder inputs at every receiver in Q, forcing
equal X_Q. This does not assume linearity or conditional independence after M.

For every fixed m and outside assignment, each retained payload distribution
is supported on a subset of its declared prefix-free codebook. Thus

    H(Y_j | M=m, X_outside=u) <= E[length(Y_j) | m,u].

Indeed, Kraft K=sum_y 2^-length(y)<=1 and q_y=2^-length(y)/K give, by
nonnegativity of relative entropy, H(Y)<=E[length(Y)]+log2 K<=E[length(Y)].
Zero-probability codewords do not matter. This also proves H(M)<=E[length(M)].
Apply entropy subadditivity within each fixed branch, then average:

    B_Q = sum_(t in Q) b_t
       <= H(M | X_outside)
          + E[sum_j length(Y_j) [Q meets R_j(M) and A_j(M)]]. (1)

All variables have finite alphabets. Expectations use the original uniform
independent inputs. The payload count can vary between branches because the
branch is conditioned on before the sum.

Put B=sum_t b_t, L=E[length(M)], H=H(M), and P=C-4 length(M).
Multiply (1) by 1/192 and sum the 640 cliques. Use 128 incidences per port,
H(M|X_outside)<=H, and (G) on each realized branch with nonnegative lengths:

    (2/3)B <= (10/3)H + E[P].

Consequently

    E[C] >= (2/3)B + 4L -(10/3)H
         >= (2/3)(B+L).                                  (2)

For any one nonorthogonal clique, rank>=1 instead gives B_Q<=H+E[P], hence

    E[C] >= B_Q+4L-H >= B_Q+3L.                           (3)

Both (2) and (3) hold, so their maximum may be used. No integrality ceiling
follows merely because realized charges are integral. A constant header with
positive length has H=0, so the sharper entropy forms charge its full 4L;
an empty constant header gives L=H=0. A nonconstant prefix-free code has L>0
and incurs the strictly positive 2L/3 penalty. The theorem bounds the average,
and therefore the maximum cost; it does not bound each individual execution.

For uniform b-bit demands B=60b, charge is at least 40b+2L/3. Only with the
separate Dfc stage equation and a worst-case rational copy allowance at least
2 max_X C(X) does this give

    D/T <= (s-1)120b -2s(40b+2L/3)
        = 40b(s-3) -(4s/3)L.

No physical realization or all-size implication follows from this entropy
argument. The geometry and conditional-transcript/paid-header methods retain
their credit. New coverage is the Gaussian header gap and conditional
prefix-free payloads.
