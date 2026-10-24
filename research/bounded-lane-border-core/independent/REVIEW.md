# Independent review: finite lane boundary and filtered semantic grid

Yiyang (@Lyy-iiis), with substantial OpenAI Codex parallel-agent assistance.
Apache-2.0. Performed October 23, 2026 on CPython 3.14.5. This is a separate
agent's proof review and independently written exact checker, not independent
human review or proof-assistant verification. No new bound is established.

## Reviewed claims and evidence

The reviewer read the lane investigator's `PROOF.md` and the graded-grid
investigator's `README.md`, then checked the equations independently. The
checker here imports neither primary verifier. It uses its own rational dense
matrix operations, Gaussian elimination, and literal owned-boundary execution.

For each lane count L=1,...,5, payload width is two and payload entries do not
commute. The fixture's diagonal q=[[1,1],[1,2]] and comparison diagonal
r=[[1,0],[2,1]] do not commute; strictly lower payload blocks are independent
fixed-seed rational matrices. These are arbitrary invertible operator fixtures,
not physical canonical Gaussian fixtures. The symbolic identities apply to
both, but no full native source replay was performed here.

The checker verifies T(AC)=T(A)T(C), T(A)S=SA, and both E F=I and F E=I.
A columnwise interpreter separately rotates the actual input Y0 into an owned
boundary bank, inserts a blank terminal Y lane, executes the appropriate core,
applies the explicitly charged diagonal boundary map, routes outputs back and
clears the derived terminal field. It agrees with E and F on all 60 arbitrary
input columns across the five lane counts, in each orientation. The terminal
CLEAR is generally nonzero before clearing; it is not a reversed erasure and
is not credited as a productive output.

Four controls for each L>=2 reject treating a newly generated opposite
orientation as the actual inverse, dropping the paid boundary, inferring that
a positive-grade upper-right residue remains positive after R, and applying
the intertwining identity to a nontriangular input. Specifically S R=I-P0
exposes a nonzero degree-zero diagonal. All checks use explicit guards, remain
active under optimized Python and return identical normal/optimized output.

```
python3 -I -B check.py
python3 -I -O -B check.py
```

Both commands passed. `RESULT.txt` records the bounded cases and controls;
`RESULT-OPTIMIZED.txt` is byte-identical. The tests corroborate the written
operator identities; they are not their all-width proof.

## Algebra review

For lower-triangular block A and C, their leading principal compression is
multiplicative. The common diagonal of AC is a0 c0 in this exact order, so T
is multiplicative without commuting physical payloads. Also
S A P_last=0, R S=I-P_last and P0 S=0, proving T(A)S=SA. The lower-left
blocks of EF and FE then cancel exactly; no assumption of commutation between
A and its individual physical blocks is used. The equal-diagonal condition
ensures that E has the same two-payload Gaussian diagonal on every lane.

The owned-terminal implementation is an admissible finite linear-program
schema using role permutations, owned initialization/CLEAR and the named
operators. Its use of S/R is semantic notation, not permission to erase an
arbitrary independent input. At the ideal native specialization there are
112 boundary rank-17 jobs and 112 extra owned terminal fields. The extra
rank-one split count is therefore 112*17=1904. This verifies that arithmetic
and the local input/output ledger. A separately written rational atanh/Taylor
enclosure in `moment.py` independently proves 28.65 < Delta < 28.66 at
C=17/5000. Thus the L=66 margin is below -311/25 and the L=67 margin
is above 311/20, proving 67 is the least positive integer lane count for
this local invoice. Normal and optimized runs pass identically, recorded in
`MOMENT.txt`. This does not establish a recursive boundary-provider bill.

For the fresh factor d=D1D2, the inverse specialization requires the boundary
d^-1 q, not merely q. This still has rank 17. The author was asked to state
this explicitly rather than transfer the unmultiplied abstract a0 notation
silently to the native specialization.

## Filtered-grid theorem review

The theorem's substantial hypothesis is a fixed, compatible homogeneous
endpoint expansion, not endpoint triangularity alone. Its expansion contains
at most J terms, each at most Q child factors, with total positive child grade
at most the output grade. Both Q and J, all free height charges and H must
remain fixed as the actual recursion rank grows.

For l>=1 and f=floor(e/N)>=1 the induction bound is

    C_l(e) <= K*l*(f+1) + Q*c0*(f+1) + E.

Using f+1<=2f and E<=Ef shows that
K(N-1)>=2Q*c0+E suffices for C_l(e)<=K*l*(e+1). The finite elementary
base cases require their own maximum K. Summing homogeneous components adds
only ceil(log2(H+1)) to the row-norm height, giving the proposed Kstar.
The active-prefix recurrence has only one unfinished child; all earlier
children have completed semantic bounds. Thus Astar(N-1)>=2P*Kstar+g,
again enlarged for the base, yields linear temporary height. Denominator
heights and row-sum norms both obey the inequalities used in this proof.

A single outer scaling D_delta with integer nonnegative s and delta=2^-s
has inverse consisting of integer shifts, so it does not coarsen the incoming
grid. Exact dyadic evaluation on the common fine grid is justified by the
proved bound on every temporary linear map. The final nearest-grid recovery
works because the exact Gaussian output has a known dyadic mesh and the
defect is below one eighth of that mesh. The author was asked to require
s>=0 explicitly (or choose nonnegative input magnitude upper bounds), avoiding
an implicit delta<=1 assumption. The resulting bit bound is linear in the
requested input precision and e for fixed H; it is conditional on exact
primitive execution and is not a fixed-tape admission proof.

## Remaining limitations

The repeated E/F algebra replaces payload V by V direct-sum V. An iterated
formal identity is therefore not itself a fixed-role native recursive template.
The actual source must still supply coherent shears U(A), L(-A^-1), all helper
endpoints, fresh factors, monomial frames and owned-center behavior at the
same declared profile. Its full-word inverse alone does not establish that
shear structure; the checked S R leakage control explains why.

The exact diagonal boundary provider is another unresolved dependency. An
L-lane program run on a one-lane-supported input can still cost the entire
L-lane program. Counting 1904 ideal rank-one boundary jobs is not by itself a
uniform recursive price for those exact jobs. Pascal sources, exits,
complements, row stock, movement and outer BIT transfer were not checked.

The reviewer accepts the scoped symbolic algebra and conditional grid theorem
subject to the explicit assumptions above. No completed native recursive
supplier or bound improvement follows yet.

## Follow-up: independently declared truncated productive contract

The root investigator subsequently proposed removing Y0 from the declared
productive domain, keeping L arbitrary X fields and L-1 arbitrary Y fields
per main pair from the outset. This is a different interface, not deletion of
an input after crediting it. The reviewer independently checked it.

Write J for the inclusion of the first L-1 child lanes and P for their
projection, so C(A)=PAJ. For lower-triangular A, PA annihilates the last input
lane. Hence C(A)P=PA and C is multiplicative. The proposed maps

    Eminus = [[A,0],[P(I-B),C(B)]],
    Fminus = [[B,0],[P(B-I),C(A)]],  B=A^-1,

are actual two-sided inverses: their lower-left blocks cancel by precisely
C(A)P=PA. This derivation uses no commuting physical payloads.

The physical program embeds the L-1 declared Y inputs in the first L-1 query
lanes, initializes the terminal query lane to zero, applies the full core and
retains all X outputs and the first L-1 query Y outputs. It explicitly clears
the derived terminal Y field. Thus every declared arbitrary input remains
represented in the completed invertible endpoint. There is no undeclared
Y0 to recover, and no diagonal boundary Gaussian provider is needed.

The independent `truncated.py` verifies this literal program, both inverse
orders and the grade pattern on all 48 independent input columns per
orientation for L=2,3,4,5 with noncommuting two-dimensional payloads. It uses
only this reviewer's own rational matrix routines. Both ordinary and optimized
runs pass identically, recorded in `TRUNCATED.txt`. It also rejects silently
adding an unprocessed arbitrary Y0 to the claimed Gaussian target and using
a nominal opposite orientation instead of the actual inverse.

At the ideal native specialization, all 2L helper sets remain declared
arbitrary productive fields. The endpoint loses exactly 112 rank-17 target
jobs relative to the complete L-lane target list; no additional X job is
lost. Its local invoice is therefore

    target = L*T - 112 H17,   paid = L*P.

The separately written rational enclosure in `moment.py` proves
1885 < 112*17^(1-17/5000) < 1886, while 28.65 < Delta < 28.66 remains valid.
Consequently the L=65 margin is below -221/10 and L=66 is above 49/10.
Thus 66 is the least positive integer lane count for this truncated local
invoice at C=.0034. It has no extra exact diagonal boundary-provider calls.

Grade X_j is j, and grade Y_j is j for j=1,...,L-1. The cross-role output is
strictly positive grade, while C(B) preserves child grade. The endpoint's
grade-zero block has one V payload at lane zero and two at each later lane.
Thus it no longer belongs to the uniform-payload A_L family literally used
as its input. A fixed recursive graded-module realization and complete
matching are still required. Formal iteration must not silently multiply
role inventory, reinitialize existing productive fields, or call an arbitrary
full-word inverse a coherent native shear.

This follow-up removes the separate exact-boundary-provider dependency for
its explicitly reduced productive contract. It leaves the actual native
coherent-shear, fixed-role matching, physical cost and outer admission
obligations open. No full native source replay was performed here.

A further caution concerns the optional formal iteration on nonuniform grades.
For the isolated Eminus core, d'_h=d_h+d_(h-1) implies

    d_h(t)=sum_(j=0)^h binom(t,j) d_(h-j)(0).

With d_0(0)>0 and fixed H, the highest-grade population eventually dominates:
d_H(t)/sum_h d_h(t) tends to one. The total declared target dimension per
application is 2D-d_H, so its ratio to the previous D tends to one, while the
literal core still uses two child/inverse applications. Polynomial growth of
role count therefore does not by itself justify iterating the uniform L=66
moment. A complete supplier must track paid and productive profiles by grade
and bind any fresh sources, exits or rebalancing. This is an accounting caution
for this isolated formal iteration, not a theorem excluding a different full
native matching with its retained helpers.
