# Independent transport audit and an alternate complete pivot for P104 type (4,4)

## Exact claim

Let `L` be PR1212's type-(4,4) representative P104 unit: delete
`FRAME0` and, in PR1212's original 120-line numbering, the second frame

    {2,3,16,17,46,47,52,53}.

PR1212 §10 used the pivot `{4,5,14,15,48,49,50,51}` for this unit. The
live frame

    F = {12,13,22,23,30,31,36,37}

(which is also PR1212's published pivot for its type-(2,2,2,2) unit)
has 24 complete four-line classes relative to `F`, with a complete class
in **all 14** D4 blocks. Every one of the 24 classes satisfies all 12
group-witness conditions of PR1212 Lemma 5, and for every ordered pair
of complete classes whose blocks meet in two pivot lines, each line of
one is orthogonal to exactly the two sign-rule rows of the other, as
Lemma 6 uses. The
two-term and diagonal necessary zero-pattern conditions at this pivot
refute every supported zero. Consequently PR1212's original Lemmas 5–7
apply directly to this representative: every rank-at-most-eight solution
of its E-graph system is diagonal-gauge equivalent to `2G_L`.

The `FRAME0` stabilizer is transitive on the 28 second-frame units of
type `(4,4)`, so the same conclusion transports to all 28. This is an
**alternate proof** of the type-(4,4) result already established by
Josie Elliston's PR1389, which kept PR1212's chosen 12-block pivot and
supplied a new path-gluing lemma (6′) for it. It also corrects PR1212 §10's
explanatory remark that, for type (4,4), "other pivots give all 14
blocks a live class but leave eight classes incomplete": of the 801 live
pivots, PR1212's has 12 covered blocks, and **24** others have no
incomplete class and all 14 blocks covered. No new
COPY floor or κ is claimed.

## Orbit and transport check

`verify.py` separately generates the 240 scaled E8 roots (the
`(±2,±2,0^6)` and even-sign `(±1)^8` families), quotients antipodal
roots to 120 lines, and recomputes the integer Gram matrix. Its line
ordering is different from PR1212's; `source_numbering` is used only to
translate the displayed witness to PR1212's published indices.

Root reflections act as signed permutations on chosen line
representatives. For every generated stabilizer map `π` and signs
`s_i`, the checker verifies all 120² identities

    G_{π(i),π(j)} = s_i s_j G_{i,j}.

Thus the binary pairing `N=(G+1) mod 2` is unchanged by the line
permutation. For rank-eight E-graph matrices, a simultaneous line
permutation transports the diagonal and orthogonal-zero equations,
rank, and term supports. The sign diagonal converts the transported
Gram matrix back to `G`, and is absorbed by the diagonal gauge.
Consequently the **signed** root action is compatible with the gauge
conclusion and the **sign-free** pairing ranks are compatible with COPY
cost. The program checks nonconstant gauge examples entrywise; the
general transport is the algebraic identity above.

An independent 8-clique enumeration gives 2,025 frames. Root-reflection
BFS reaches all of them from `FRAME0`. Among the 1260 frames disjoint
from `FRAME0`, the 204 distinct one- or two-reflection permutations
fixing `FRAME0` generate exactly three orbits of sizes 28, 336 and 896,
classified by class-hit types `(4,4)`, `(2,2,2,2)` and `(1^8)`.
The 112 live lines form one orbit. Hence a representative statement
for the 28-orbit transports to every unit in it. The checker also
places PR717's named P104 unit in the 896-orbit and independently
checks PR1212's type-(2,2,2,2) representative/pivot profile.

## Four finite inputs at the alternate pivot

The type-(4,4) unit is PR1212's own representative: `verify.py`
translates PR1212's published line numbers into its independent line
order (`source_numbering`), checks that the deleted frame has hit type
(4,4), and records both numberings in `RESULT.json`. It examines every
live pivot frame, not only PR1212's first minimizing pivot (PR1212's
`best_pivot` stops at the first frame with no incomplete class).
The displayed `F` is the smallest all-block complete pivot in the
independent order, and the verifier requires it to translate to
`{12,13,22,23,30,31,36,37}`. Of the 801 live
frames, **25** have no incomplete class: one covers 12 blocks and 24
cover all 14. At the displayed `F` the checker obtains:

| PR1212 input | Exact finite check |
|---|---|
| (I1), complete classes | 24 classes of four live lines; no incomplete class |
| (I2), zero exclusion | independently encoded CNF and RUP proof below |
| (I3), group witnesses | each class × six pivot pairs × two signs has a live witness: 288 checks |
| (I4), gluing | 14 covered blocks; 56 triples each in one block; 24 Hadamard classes; 1,952 ordered cross-class sign-rule checks (488 class pairs × 4 lines) |

The new zero-pattern CNF uses one Boolean variable for nonzeroness of
each `a_if` and `b_if` with `i∈L\F` and `f∈T_i` (768 main variables),
plus 384 product variables. For each ordered orthogonal pair `i,j`
whose pivot supports meet in `{f,h}`, the exact equation
`a_if b_jf + a_ih b_jh = 0` implies

    (a_if != 0 and b_jf != 0) iff (a_ih != 0 and b_jh != 0).

There are 3904 such equations, each encoded by four CNF clauses.
Each of the 96 diagonal equations `a_i·b_i=16` implies that at least
one of its four products is nonzero; a product variable is made
equivalent to the conjunction of the corresponding two main variables.
Finally one clause requires at least one main variable to be zero.
The CNF has 1,152 variables and 16,865 clauses. These conditions are
necessary for every characteristic-zero solution of PR1212's pivot
equations; the CNF discards other restrictions, so refuting it is sound.

The submitted `proof-alt-p104-44.drup` was generated using Lingeling in
the shared search venv; **the verifier does not import or trust the
solver**. Its stdlib checker replays 2,501 RUP additions, including
the empty clause; three deletions are ignored, which only strengthens
the active database of previously verified consequences. The CNF digest
is `552f868d0bc24a3371e211b5a5881d959e82ff35c4a7690eb59784e48f18789c`;
the proof (115,599 bytes) digest is
`a0b967b30f0a7a8d2ea1cfcb7e17babc4d2d8a3adcd7d09f633fb5106bfc5117`.
As a separate review cross-check, not part of the package, PR1212's own
`build_zero_cnf` with the two-term and diagonal families at this unit and
pivot is also unsatisfiable with `some zero` (and satisfiable without it),
while at PR1212's chosen pivot it is satisfiable, as PR1212 Lemma 8 records.
Controls reject a Gram-sign change, a corrupted transport permutation,
the proof with the `some zero` clause omitted, an injected non-RUP
unit, and a missing empty line.

With (I1)–(I4), the *written* Lemmas 5–7 of PR1212 apply at `F`:
complete-class ratio relations yield the Hadamard-scaled form; the
all-block condition glues the column scalings; and the pivot
factorization yields `K=D(2G_L)D^{-1}`. This package checks the new
finite premises and cites those written lemmas; it does not formalize
them in Lean or claim an independent proof of their universal algebra.
PR1497 separately audits Lemmas 5–6.

## Section 8 cost bridge and limits

PR1212 §8's bridge is algebraic. If eight costly terms factor a
rank-eight E-graph matrix `K=XY^T`, then the pivot forces `rank X =
rank Y = 8`. Gauge rigidity gives `K = D R(2I)R^T D^{-1}`; full column
rank of `R` gives unique invertible matrices `A,B` with

    X = DRA,   Y = D^{-1}RB,   AB^T = 2I.

The diagonal factors are nowhere zero, so each term has the same row
and source supports as the exact all-pairs decoder `(RA,RB)`. Its binary
pairing ranks therefore match term by term. PR968's all-pairs theorem
then gives the eight-term real COPY floor `72-p` for `p<=16` in the
relevant P120/P112/P104 cases: 72, 64 and 56 respectively (at `p=16`
use its general bound (a), not the `p<=15` bound (b)). This step is a
reduction to PR968's cited hyperplane-flat classification and finite
checker, not a new proof of that classification. PR1212 states its
cost corollary for real coefficients. Its rank-eight gauge algebra
extends to characteristic-zero fields, while a complex COPY floor
requires the separate complex extension; this package makes no new
complex cost claim.

The audit concerns exact E-graph equations, eight costly terms and
the fixed E8 P104 geometry. It does not settle nine or more costly
terms, all-size multiplication, physical delivery or the selected
frontier. PR1389's broader type-(4,4) proof remains credited; this
alternate route supplies a shorter set of algebraic dependencies and
an independently replayable finite certificate at a new pivot.
