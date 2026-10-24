# Sharp commutator bound after a common block Schur deletion

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with finite corroboration. Deleting a common
invertible block of size d from two commuting matrices over any field produces
Schur complements whose commutator has rank at most 2d. An ordered factorization
also characterizes equality. The bound is sharp for every d, even for commuting
idempotents over F5. This answers open question 2 of Nick Petalas's merged
[PR #4278](https://github.com/CrocSwap/integer-mult-bounds/pull/4278).

The new step is the ordered block identity and its sharpness family. The scalar
criterion and its F5 example from #4278 are cited predecessors. This is original
successor work, not an audit of that package. No new kappa is claimed.

## Theorem

Let K be any field, let 1 <= d < n, and split two commuting n-by-n matrices
at the same first d coordinates:

```text
P = [[A,R],[C,D]],  Q = [[B,L],[E,F]],  PQ = QP = [[H,T],[W,J]],
S = D - C A^-1 R,  Z = F - E B^-1 L.
```

Assume A and B are invertible d-by-d blocks. They need not commute with each
other or with H. Define the following matrices in the displayed order:

```text
U = C A^-1 - E B^-1,         V = A^-1 R - B^-1 L,
X = W - E B^-1 H,           Y = T - H B^-1 L.
```

Then

```text
[S,Z] = SZ - ZS = X V - U Y = [X U] [ V ],
                                    [-Y ]
rank [S,Z] <= min(2d, n-d).
```

Here X and U have shape (n-d)-by-d, and V and Y have shape d-by-(n-d).
Moreover, rank [S,Z] = 2d exactly when [X U] has column rank 2d and [V; -Y]
has row rank 2d. Thus equality is impossible when n-d < 2d.

For idempotent inputs, S and Z are idempotents of ranks rank(P)-d and
rank(Q)-d. Nevertheless their commutator can attain rank 2d.

## Proof

The block equations from PQ=QP give, with no factor interchanges,

```text
DF = J - C L,             FD = J - E R,
D E = W - C B,            F C = W - E A,
R F = T - A L,            L D = T - B R,
R E = H - A B,            L C = H - B A.
```

Expand the first Schur product and substitute these equations:

```text
SZ = DF - D E B^-1 L - C A^-1 R F + C A^-1 R E B^-1 L
   = J - C L - (W-CB) B^-1 L - C A^-1 (T-AL)
       + C A^-1 (H-AB) B^-1 L
   = J - W B^-1 L - C A^-1 T + C A^-1 H B^-1 L.
```

Interchanging the two input matrices gives

```text
ZS = J - W A^-1 R - E B^-1 T + E B^-1 H A^-1 R.
```

Subtract the two expressions. Expanding the proposed factors gives exactly

```text
XV - UY = W(A^-1 R - B^-1 L) - (C A^-1 - E B^-1)T
           + C A^-1 H B^-1 L - E B^-1 H A^-1 R.
```

The two copies of E B^-1 H B^-1 L cancel without commuting any blocks.
This proves the identity. It factors through K^(2d), so the rank is at most
2d and also at most the output dimension n-d. If both rectangular factors
have rank 2d, the right factor surjects onto K^(2d) and the left factor is
injective there, so their product has rank 2d. Conversely a product of rank
2d forces both factors to have rank at least 2d, hence exactly 2d.

For the idempotence assertion, P^2=P gives

```text
D^2 = D-CR,  DC = C(I-A),  RD = (I-A)R,  RC = A(I-A).
```

Substitute these four identities into S^2. Since A commutes with I-A and
with A^-1, the result is S^2=D-C A^-1 R=S. Invertible block row and column
operations take P to diag(A,S), so rank(P)=d+rank(S). Apply the same argument
to Q. This step does not require P and Q to commute.

## Sharpness for every block size

Use the following scalar-pivot example from #4278, over F5:

```text
P0 = [[4,3,3], [3,4,3], [3,3,4]],
Q0 = [[4,4,3], [2,2,2], [0,0,1]].
```

As established there, these are commuting rank-two idempotents. Their Schur
complements have commutator

```text
K0 = [[4,2],[3,1]],  det(K0) = 3 in F5.
```

For any positive d, take P=P0 tensor I_d and Q=Q0 tensor I_d, with the first
d coordinates as the pivot block. The pivots are both 4 I_d and are invertible.
Block multiplication shows the Schur complements and their commutator are
the scalar counterparts tensored with I_d. In particular the commutator is
K0 tensor I_d, which is invertible in dimension 2d because its inverse is
K0^-1 tensor I_d. Its rank is 2d. The inputs are commuting rank-2d
idempotents in dimension 3d. This proves that no smaller universal bound
as a function of d is possible, including in the projector subclass.

## Evidence and reproduction

The self-contained [verify.py](verify.py) imports no predecessor executable.
It compares the ordered factorization with the directly multiplied Schur
commutator, computes both rectangular ranks, and tests idempotence and rank
drops in the projector cases. Its complete finite domains are:

- Every P in M4(F2), with Q=P^2 and a size-two pivot. Of 65,536 candidates,
  11,904 have both pivots invertible. Their commutator ranks are 0 in 10,392
  cases and 2 in 1,512 cases. In 4,032 admitted cases A and B do not commute.
- Every P in M3(F3), with Q=P^2 and a size-two pivot. Of 19,683 candidates,
  8,208 are admitted, all with zero commutator in their one-dimensional
  Schur space. In 5,184 admitted cases A and B do not commute.
- Every G in GL4(F2), conjugating the coordinate projectors with masks 7
  and 11. Among all 20,160 headers, 4,032 admit both size-two pivots. The
  Schur commutator has rank 0 in 2,304 cases and rank 1 in 1,728 cases.
  These are header occurrences, not distinct projector-pair counts.
- The tensor family at d=1,2,3,4 over F5, attaining commutator rank 2d.
- Four boundary controls reject a singular pivot, malformed shape, exceeded
  matrix capacity and noncommuting inputs. Four formula controls distinguish
  an incorrect order of H and B^-1, omitted H corrections, an incorrect plus
  sign and the false premise that admitted pivot blocks must commute.

The polynomial domains enumerate only the specified pairs (P,P^2), not all
commuting pairs. The finite checks corroborate the written universal proof.
The generated stdout receipt binds every package file by SHA256; no stored
or handwritten receipt is supplied, and the verifier writes no files.

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/block-schur-commutator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/block-schur-commutator/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/block-schur-commutator
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/block-schur-commutator --check-source-history
```

The scientific marker is `PASS_BLOCK_SCHUR_COMMUTATOR`. Another CPython 3.12
path may replace the local interpreter. VERIFY.json registers both scientific
modes with 120-second timeouts. Every check uses explicit exceptions and
remains active under -O. SOURCES.json pins historical provenance, including
the predecessor README; no external live input is required.

## Limits and code constraints

This is a field-algebra proof with finite corroboration, not a formal-kernel
result or a complete multiplication theorem. Independent human and formal
proof-kernel review are unclaimed. It treats one common deletion with both
pivot blocks invertible. It does not classify subsequent simultaneous orbits,
count passing complete headers, extend rank claims to rings, or provide a
producer, header selection/emission, dispatch, dirty return, stock, precision
or complete physical invoice. Those costs remain unknown. The selected
frontier is unchanged; selected cold replay, Lean and Docker were not run.

The verifier uses direct calls, no recursion, no subprocesses and no dynamic
code generation. All functions are below 60 physical lines. Matrices have at
most 12 rows and 12 columns; each exhaustive outer scan has at most 65,536
candidates, and the tensor scan has four cases. Gaussian elimination has at
most 12 pivot rounds. Its temporary augmented rows have at most 24 entries.
The file-hash receipt has at most eight files. Finite scan counters and ranks
are kept locally and invalid inputs raise explicit exceptions. Warnings are
errors in both registered modes; local AST syntax and function-size inspection
supplements execution. No external static analyzer is installed.

Power of Ten rule 3 deviation: CPython allocates tuples, integers and temporary
rows during arithmetic. The fixed matrix and scan capacities above bound live
state; matrices from exhaustive scans are discarded each iteration, retaining
only counters and the first witness. Both registered modes exercise those
bounds, and the capacity control rejects a 13-column matrix. A fixed-allocation
implementation would be a separate port if this verifier entered a long-lived
or native execution path.

## Open next questions

1. Can the changing Schur-pair state be classified by the ordered factors up
   to simultaneous conjugacy? A header-density recursion needs more than the
   rank bound. Start with size-two pivots and two rank-three projectors in
   dimension four. The present factors do not classify their orbit.
2. What is the sharp projector bound for fixed input ranks and a fixed field,
   especially F2? The F5 construction proves universal sharpness but does not
   give attainment in every field. Start with block-diagonal lifts of binary
   examples and compare rank restrictions on the two residual projectors.

## Credit and relation to the research bottleneck

Nick Petalas's #4278 supplies the scalar identity, the scalar F5 sharpness
example and the explicit block-pivot question. Nick Petalas's #4259 supplies
the laminar shared-header context, and #4228 supplies the single-projector
Schur framework. Cinna Davis's #4100 supplies the BIT request/complete-header
context. Those predecessors retain their credit; no predecessor file changes.

This is a side result with scope changed from `uniform-transfer-audit` to an
original open interface question. It bounds the noncommutativity created by a
wider elimination step, without assuming the pivot blocks commute. It closes
no actual-caller admission or all-size transfer obligation. This package starts
no further construction campaign and treats no unknown consumer cost as zero.
