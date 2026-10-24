# A dyadic unit completion that stores the full current query

The selected eight target fields can store the exact current query R(X+Y).
The data encoding and its algebraic inverse use only dyadic coefficients.
The complete local word adds eight rank-one children to the accepted clean-J
forward word. Its cost is 212,826 real scalar primitives and native mass
5,530. It restores all 480 arbitrary helper contents in their original
complete job frames. All eight owned private fields end at zero.

This is a local component. Its selected Y outputs have FULL frames, while
its other Y outputs retain their inverse-line frames. No next controller
call, old-stage query, recursive hosting, or complete supplier is established.
The initial X line type is also unchanged.

## A general completion identity

Let V be the direct sum of coordinate spaces V_A and V_U. Let R:V->W and
K:W->V be linear maps over a ring. Suppose the restriction R_A:V_A->W is
invertible and the A part of K equals R_A^-1. Define

    L = R_A pi_A,       K_A = iota_A R_A^-1,
    R_U = R-L,         K_U = K-K_A,
    J = I-KR.

Then L K_A=I, L K_U=0, and R_U K_A=0. The two operators below are unit
triangular with respect to V_A and V_U:

    T = (I-K_U L)(I+K_A R_U),
    T^-1 = (I-K_A R_U)(I+K_U L).                    (1)

The two displayed products are inverses, since (K_U L)^2=(K_A R_U)^2=0.
Expansion gives

    T = I+K_A R_U-K_U R,
    pi_U T = pi_U J,
    L T = R,
    T-J = K_A(2R-L).                               (2)

Thus replacing only the A output rows of J gives an invertible encoding
whose A rows contain the full query R. There is no hypothesis on RK and
no need to invert I-RK. The ring only needs the coefficients already in R,
K, and R_A^-1. In particular, a dyadic minor and dyadic K give a dyadic unit
T, even when J has an odd nonunit eigenvalue.

For normalized coordinates (u,a)=(pi_U w,Lw), put B=R_U and D=K_U. Then

    f=a+Bu,
    T:(u,a) -> (u-Df,f).                           (3)

The inverse is u=u'+Df and a=f-Bu. In the actual construction BD=13I, so

    T^-1:(u',f) -> (u'+Df,-12f-Bu').                (4)

These equations account for every input coordinate. A query does not
replace or discard an arbitrary data value.

## The actual word

Use the actual R, K=R^T/4, RK=14I, and

    A=[0,7,20,27,36,46,57,111].

The selected minor satisfies R_A R_A^T=4I. Thus K restricted to A is
K_A=iota_A R_A^-1, as required by (1). Write L_A for L. For arbitrary
logical inputs l,v, apply these steps in order:

1. Apply I+K_A R_U to Y at its original I frame.
2. Apply I-K_U L_A to Y at the same I frame.
3. Run the complete accepted clean-J forward core.
4. Apply the positive line C_q to each selected Y field in A.
5. Add (T-J)X to these eight now-FULL target fields.

After step 3 the logical data is X=l, Y=Tv+Jl. By (2), the last scalar
correction is supported only on A and gives

    X_out=l,    Y_out=T(l+v),    L_A Y_out=R(l+v).   (5)

All 480 borrowed helper inputs are arbitrary. The old core acts on the
changed data with the same complete helper map and has no helper-to-data
coefficient. The new gates touch no helper. The eight private C fields are
owned. Their input values may be discarded. The prefix clears C0 before
each query and at its end; the retained core clears all eight private fields.

The decompressed payload `UNIT-QUERY-PROGRAM.json.gz` has SHA-256

    9cb744034b11ef515a9c429264199a03f02fd9c4cb408e6455021ce9c0802a9c.

It contains all 26,531 events: 944 prefix scalar events, the 25,155 old core
events, eight native line records, and 424 scalar suffix events. The old
core and the line records are byte-identical to the frozen PJ-query packet.
The line records include the exact intrinsic child and its two maps.

| Fields | Input frame | Output frame |
| --- | --- | --- |
| X_p | C_qp | F |
| Y_p, p in A | I | F |
| Y_p, p outside A | I | F C_qp^-1 |
| 480 helpers | Original input frames | Original complete job frames |
| C0 through C7 | Owned, arbitrary | Zero at I |

Here F is the complete local nine-axis transform. The prefix runs before
every retained event. The eight positive lines and the suffix run after
every retained event and before the enclosing owner view is restored. The
positive line cancels the old inverse line on the entire arbitrary Y field.
Each suffix ADD then reads FULL X and writes FULL Y. The inherited native
check proves the exact line phase; replacing the positive line with its
inverse would leave a nontrivial translation.

Relative to the unchanged old Y baseline F C_q^-1, the new output has code
C_A T, where C_A applies C_q only to A. It is not a uniformly typed T bank.
Equation (1) is an algebraic inverse; it does not permit cross-frame scalar
ADDs. An unchanged later B or F word is not admitted by this proof.

## Exact local cost and checks

Each triangular prefix factor uses C0 for eight serial queries. The first
factor reads only U and writes only A. The second reads only A and writes
only U. Thus updates within either factor cannot change its later query
inputs. Each factor has 448 unit ADDs, eight quarter SCALEs, and sixteen
CLEARs. Each costs 3,648 real primitives.

The matrix T-J has 424 nonzero coefficients, all +1 or -1, on the eight
selected target rows. Its literal suffix has cost 3,392 real primitives.

| Part | Real scalar primitives |
| --- | ---: |
| First triangular prefix | 3,648 |
| Second triangular prefix | 3,648 |
| Retained clean-J core | 202,138 |
| Selected FULL correction | 3,392 |
| Complete local word | 212,826 |

The native profile is {1:2420,2:418,3:432,4:142,5:82}, with mass 5,530.
The added work is eight rank-one children and sixteen child permutation
maps. No cover record, private field, or odd division is added. Recursive
child execution, hosting, address work, precision, and the complete stream
invoice remain outside this local count.

The producer checks all 712 input columns, all 480 arbitrary helper rows,
the eight cleared private rows, both inverse orders in (1), the exact query,
the support and coefficients of T-J, every new scalar frame, and the local
invoice. Four controls reject reversed prefix order, an omitted second
factor, an omitted suffix, and a missing initial C0 clear. The complete old
native chronology and the eight line kernels are inherited byte-for-byte
from `CURRENT-QUERY-PROGRAM.json.gz`; their phase proof is not rerun here.

Run:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/paired-package-review/upstream-followthrough-20261015/current-query-encoder/emit_unit_query.py --out /private/tmp/unit-query-replay
```

The first line is `PASS_UNIT_CURRENT_SUM_QUERY_712_COLUMNS`.
`UNIT-QUERY.json` gives the exact source pins, count, and controls.
Independent native and scalar review is separate from this producer check.

## Consequence for the reset decoder

At the current even-stage F_t input in the reset construction,

    l=J_s^-1 x_i-v_i,    v=v_i,    t=s+1.

Equation (5) gives R_t J_s^-1 x_i directly in eight completed fields. This
includes the arbitrary target term that the old source-only FULL reader
misses. It does not yet give R_s J_s^-1 x_i, retire the mixed code, or prove
a complete decoder within the 573-rank per-replica allowance.

The construction uses the accepted clean-J core, the actual orthogonal
minor used in the QQ16 work, and the coherent-port positive-line recipes.
The earlier PJ-query packet stays fixed. Research and verification used
OpenAI Codex under the user's direction. There is no kappa claim.
