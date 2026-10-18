# A phase-query bound for matched paired-log decoders

We prove that four independent matched P112 query swaps require at least
**555 single-array phase events** in the model below, even with shared
linear processing, COPY, CLEAR and private scratch. For one bank we obtain
139. We allow physical scalar mixing between different canonical frames.

Under the declared completed-log budget, we can afford at most 497 additional
rank-one calls at the comparison saving. The proposed matched primitive
therefore cannot close that budget in this alphabet. We leave the selected
multiplication exponent unchanged.

The new contribution combines an averaged nonzero-defect rank inequality,
a common Pauli-trivial tensor sector, and the exact P112 target calculation.
We build on eumemic's [PR288, Section 1.2](https://github.com/CrocSwap/integer-mult-bounds/pull/288)
and Ali Romman's [PR468](https://github.com/CrocSwap/integer-mult-bounds/pull/468)
for compact-WY/causal factorization, image and row spans, character
specialization and Sylvester rank inequalities. We do not claim those
ingredients as new.

## Model and claim boundary

Fix a payload dimension m and tensor length lambda. Each physical role
contains one array in `(C^(2^m))^tensor(lambda)`. An exact fixed straight-line
program may use:

- Constant complex linear maps on the **role coordinates**, tensored with
  the payload identity. We include COPY, CLEAR, zero-initialized scratch,
  discarded temporaries, and any number of restored dirty roles.
- Uniform tensor Paulis `P^tensor(lambda)` on individual roles.
- Paid application to one role of `G^tensor(lambda)`, where G is a product
  of the commuting directional phases

      C_q = (1+i)I/2 + (1-i)X_q/2.

Here X_q translates the m-bit address by q. The Fourier multiplier of C_q
is `i^(q dot u)`, with the binary dot product read as 0 or 1. We absorb
fixed scalar factors into the constant linear maps. A nontrivial phase
event has nonzero binary symmetric polar; Pauli-only events do not count.

The lower bound applies to programs that implement the target for all
sufficiently large tensor lengths. We use witnesses at arbitrarily large
multiples of four. A program and its constant coefficients may depend on
lambda; the argument applies at each such witness length.

We exclude data-dependent branching, nonlinear arithmetic, arbitrary
payload-coordinate linear maps, independently chosen per-layer Paulis,
and noncommuting payload adapters. We also exclude a new child interface
that acts on several roles as one oracle. A researcher proposing one must
specify its action and price before comparing costs.

Our endpoint is four coherent copies of the matched query swap defined
below. We do **not** identify the complete mixed-chart inverse in
[PR1998](https://github.com/CrocSwap/integer-mult-bounds/pull/1998) with
this endpoint. The result rules out this proposed implementation strategy;
it does not settle every terminal decoder or integer multiplication algorithm.

## 1. A causal rank inequality with singular free maps

Consider a family of scalar-specialized programs indexed by chi. Replace
each phase query by identity and call the resulting baseline map M0. There
are k nontrivial events. At event j, let alpha_j be the query multiplier
minus one, so alpha_j is 0 or -2 in the real character sectors used below.

Unroll the constant linear computation. Let V_j map the genuine inputs
to event j's baseline read, and let U_j propagate an injection just after
event j to the declared outputs. Let H_ji propagate event i's injection to
event j's read, for i<j. Chronology makes H strictly lower triangular.
If q collects the actual prequery reads, then

    q = V x + H D_alpha q,
    M_chi - M0 = U D_alpha (I-H D_alpha)^-1 V.          (1)

The inverse is a finite triangular series. We need no inverse for a free
map. Clean ancillas add zero rows to the input embedding; discarded
temporaries disappear under output projection. COPY and CLEAR remain
constant linear operations, so (1) includes them.

Let S be the active events and t=|S|. Restricting (1) gives

    M_chi-M0 = U_S A_S V_S,

where A_S is triangular with diagonal -2 and therefore invertible. Define
d_image as the dimension of the span of the images of all target differences
M_chi-M0, and d_row as the analogous row-space dimension. Equation (1) gives
`rank U >= d_image` and `rank V >= d_row`. Deleting k-t columns or rows
reduces rank by at most k-t. Sylvester's inequality now gives

    rank(M_chi-M0) >= d_image+d_row-2k+t.              (2)

If each nontrivial event is active on half the characters, average (2):

    k >= (2/3)(d_image+d_row-R_average),              (3)

where R_average is the average target-difference rank. An upper bound on
R_average gives a valid lower bound in (3). We impose no restriction on
intersections among the event supports and no bound on scratch space.

PR288 already uses compact-WY factorization and both span directions for
a target-zero character argument. Here we retain the nonzero target rank,
average over characters, and extend the causal factorization to singular
free programs before applying it to the matched decoder.

## 2. Real characters in a common Pauli-trivial tensor sector

An unrestricted character average would miscount a free Pauli. For example,
a free X on one scalar role has nonzero differences in half the ordinary
Fourier characters. We instead construct a subspace on which **all** allowed
uniform tensor Paulis act as identity. Thus role-dependent free Paulis cause
no character-dependent free mixing in (1).

Modulo translations, the commuting phase group has binary symmetric polar

    C_q -> q q^T,

and the polars generate the full symmetric matrix space over F2. For a
linear functional L on that space, write

    L(q q^T) = sum_i a_i q_i + sum_(i<j) b_ij q_i q_j.

Choose a tuple of Fourier frequencies as follows. Include `e_i+e_j` once
for each b_ij=1. If degree_i counts those incidences, include
`(2a_i-degree_i) mod 4` copies of e_i. Pad with zero frequencies to a common
length lambda divisible by four. A length of at least

    binomial(m,2)+3m

suffices. Each coordinate count is even, so the total frequency XOR is zero.
The exact parity expansion modulo four gives

    C_q^tensor(lambda) -> (-1)^L(q q^T).

Uniform tensor X operations act as identity because that total XOR is zero.
Now sum the corresponding Fourier basis vector over all simultaneous
frequency translations by v in F2^m. This is a nonzero orbit sum, fixed by
every uniform tensor Z. If q dot v=1, the phase count changes from n to
lambda-n; since lambda is a multiple of four and n is even, its value modulo
four stays unchanged. Hence the orbit sum retains the desired phase character.

We obtain all real polar characters at the **same** tensor length, inside
one common Pauli-trivial subspace. Padding with four zero frequencies
extends the construction to arbitrarily large permitted lengths. Each
nonzero polar evaluates to -1 on exactly half these characters, as required
by (3). This includes higher-rank commuting phase children on one array:
after specialization they still change just one role coordinate.

We never expand `C_q^tensor(lambda)` as a two-term sum of uniform tensor
translations. That identity would be false for lambda>1.

## 3. Exact matched query target

Partition v data ports into r selected coordinates a and v-r ordinary
coordinates b. Introduce r independent log coordinates z, with each z_i
in the same hole gauge as a_i. For the pinned P112 minor,

    R'=[I B],  P'=(I,0)^T,  Z'=(-12I,B^T)^T,
    BB^T=13I,  v=112,  r=8.

The source is Ali Romman's unchanged `native-source-codes` loader and its
frozen archive. We use selected ports `[0,7,20,23,86,93,108,111]`.
The matrix B has 416 nonzeros, all +/-1/2, and no zero row or column.

The query swap sends

    Y'=(I-Z'R')Y+P'z,  z'=R'Y.

Writing beta=13, its constant role matrix is

    T(B) = [ beta I    (beta-1)B      I ]
           [ -B^T     I-B^T B        0 ]
           [ I        B              0 ].

In a real character sector the hole gauges are signs. Put
`D=diag(D_A,D_B,D_A)` and `B'=D_A B D_B`. The physical target is
`D T(B) D = T(B')`; its baseline is T(B). Put E=B'-B. Direct subtraction gives

    Delta = [ 0       (beta-1)E                  0 ]
            [ -E^T    -B^T E-E^T B'              0 ]
            [ 0       E                         0 ].

After removing dependent selected rows and zero log columns, the remaining
block reduces by invertible row and column additions to
`[[0,E],[-E^T,0]]`. Therefore

    rank Delta = 2 rank E <= 2r.                    (4)

We next prove `d_image=d_row=v`. Write P_q=q q^T. Distinct unordered pairs
of the 112 hole labels have distinct nonzero differences P_q+P_p. One can
check the 6,216 pairs directly. For a general justification, a dependence
among at most four distinct nonzero rank-one symmetric polars would give
`Q Q^T=0`; Sylvester's inequality forces rank Q<=2, which contains at most
three distinct nonzero binary vectors. The smaller cases follow as well.

For each nonzero B_ij, the Fourier coefficient of Delta at the unique
selected-ordinary pair character is

    B_ij [ ((beta-1)e_ai+e_zi)e_bj^T - e_bj e_ai^T ].

Its image spans `((beta-1)e_ai+e_zi,e_bj)`, and its row space spans
`(e_bj^T,e_ai^T)`. Fourier coefficients are linear combinations of the
character evaluations. Since B has no zero rows or columns, these
coefficients give v independent directions on each side. The block formula
also confines every image and row space to those respective v-dimensional
spaces. Thus the dimensions equal v.

Equations (3) and (4) yield

    k >= ceil(4(v-r)/3).

For P112 this is 139. For four independent banks, the dimensions add to
448 on each side and the rank upper bound becomes 64. Even if the program
shares scratch and mixes the four banks, it needs

    k >= ceil((2/3)(448+448-64)) = 555.              (5)

We claim a lower bound, not an optimal 555-event construction.

## 4. Coherent cover routes and price comparison

For the actual coherent port route D_s, `rho_s(p)q_p=q_p`. On the chosen
Pauli-trivial sector the payload translations disappear, while owner
reindexing is a constant permutation of expanded role coordinates. It
commutes with the diagonal hole signs, because the source owner
`d rho_s(p)` has normal `d q_p`. Hence a coherently routed target is a
constant conjugate of a direct sum of the preceding targets, with q replaced
by d q in each cover block.

The image and row dimensions scale by the cover size, as does the rank
bound. A uniform full-cover program therefore still needs at least 555
events per four-bank cover sweep. For a nonuniform program the average
lower bound is 554+2/3 events per cover element. Cross-owner constant linear
mixing does not change the argument. We require four such coherent target
endpoints; arbitrary products of different intermediate charts need a
separate analysis.

For the conditional completed-log model, take m=73, W=968, fixed profile

    {1:21204, 2:4500, 3:3744, 4:1170, 5:738, 8:16, 9:40,
     16:32, 17:16, 24:8, 32:16, 33:8, 40:8, 48:48, 49:8}

and idle mass 14,778. These are declared comparison inputs from the earlier
uniform-log investigation, not a new hosting certificate. We put the idle
mass at the allowed cap 51 to give a favorable lower moment. At

    a = 67018507072324140917/40000000000000000000000,

the unnormalized allowance lies strictly between 500.73765694042 and
500.73765694043. We can fit 497 additional rank-one calls; 498 fail.
The verifier encloses these inequalities with the pinned exact arithmetic
from Douglas Colkitt's `complex-local-word-ceiling` package.

Every ordinary single-array phase event has native rank at least one.
Higher-rank commuting children cost more than rank-one children at this
fixed width, so they cannot evade (5). A rank-additive batch of several
events also cannot fit: even its rank mass is at least 554+2/3 per cover,
above the allowance, and each rank unit has moment price at least one.
We make no claim for a new joint child interface with a different charge.
Sharing the decoder with already counted earlier work would also change
the stated appended-terminal comparison and requires a new full invoice.

## Reproduction and evidence

From the repository root, using Python 3.12 and its standard library:

```sh
python3.12 scripts/research_package.py --package research/paired-log-phase-query-bound
```

Direct optimized replay:

```sh
python3 -I -O -B research/paired-log-phase-query-bound/verify.py
```

We check 96 exact character maps from 12 constant linear programs containing
48 singular COPY/CLEAR steps, against an independent direct execution. We
exhaust 64 Pauli-trivial characters at tensor length 12, with 3,584 exact
phase checks. We reconstruct the actual source minor, check all 6,216 pair
characters, certify the two 112-dimensional spans and compare 57 exact
target differences with the block formula. Exact rational ranks of E and
modular lower certificates corroborate (4); the written block elimination
proves it for all characters. The generic average theorem and the general
tensor-sector construction are proofs, not extrapolations from these samples.

Controls cover omitted causal propagation, a nontrivial Pauli sector,
duplicated hole labels, unmatched log gauges, neutral events and understated
costs. Checks use exceptions and remain active under `-O`. We have not
formalized the proof in a proof assistant or audited the full multiplication
theorem.

## Open next questions

- Can noncommuting payload adapters yield a cheaper matched query swap?
  They can move between the character sectors used here. A researcher can
  start with one explicit address-linear adapter between two phase events,
  then check the tensor-valid endpoint and complete price. We have no such
  construction.
- Can a different terminal endpoint or shared earlier work close the
  paired-log controller? A researcher must derive its exact physical map
  and full invoice before applying this bound. The mixed-chart observation
  theorem alone does not specify an admitted native implementation.

## Attribution

Jose Manuel (@jmbarrancoml), with substantial OpenAI Codex assistance in
mathematics, implementation and prose. Mathematical collaborators checked
the causal expansion and target identities; the primary agent implemented
the replay. We have not obtained independent human review.

We credit eumemic (#288) and Ali Romman (#468) for the rank-factorization
and span methods; Ali Romman (#1862/#1969) for source codes and exact
phase/route conventions; Rohan Arun (#1931) for the local source-word
continuation; and Douglas Colkitt for interval arithmetic. Jeremy Diviney's
#836 addresses unitary or gauged mixing in a broader frame setting; our
arbitrary constant role-linear maps and restricted commuting-phase alphabet
give a different scope. We retain the original files and their notices.
