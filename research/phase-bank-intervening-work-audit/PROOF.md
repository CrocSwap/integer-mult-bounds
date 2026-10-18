# Exact admission of intervening data work at an open Pauli bank

This is a source-bound interface audit, not a correction to an emitted
predecessor word. Gareth Davidson / bitplane's PR2850,
`a007c32f992195ad372806db38c9359dd49382ad`, supplies the physical open producer
and C/Q/phase primitives in `research/phase-accumulator-tensor-closure/model.py`.
Dugongue's PR2871, `894a3edbcd90fc379a277eb07a5ae2b706c7a8e1`,
`research/kappa-action-theory/volumes/02-physical.md`, supplies the sufficient
transport and invariant-block contracts P008 and P009. Its P095 supplies a
mutable-accumulator example preserving the controls. Those results retain
credit and are consistent with this audit.

The added result is necessity, including differently labelled consumers, and
its application in the predecessor's actual Fourier control frame. The proof
uses standard Pauli matrices and matrix blocks; these facts are not claimed as
new representation theory. Substantial OpenAI Codex assistance, including a
separately delegated derivation and review; no independent human review or
formal-kernel verification is claimed.

## 1. Contract and operator order

Let the finite data space have basis `|d>` and the bank have every basis state
`|c>`, `c in F2^r`. All amplitudes and all data/bank correlations are arbitrary.
For arbitrary functions `a(d), b(d) in F2^r`, define

```
Z(a)|c> = (-1)^(a dot c)|c>,     X(b)|c> = |c+b>,
W_d = X(b(d)) Z(a(d)).
```

A chronological W executes Z and then X. Let U be any complex
data matrix acting as `U tensor I_bank`; it need not be invertible. A second
consumer has functions `a'(e),b'(e)` in the same bank coordinates and executes
`W'_e=X(b'(e))Z(a'(e))`. The chronological sequence W, U, W' is the matrix

```
T = W' (U tensor I_bank) W.
```

There are exactly these two controlled Pauli words and the intervening
data-only U. No bank chart, prepared-state restriction, discarded lane,
additional bank correction, or arbitrary joint data/bank consumer is implicit.
In particular the data coordinates in this section are the coordinates in
which the controls are evaluated, not automatically physical array addresses.

## 2. Necessary and sufficient condition

**Theorem.** T equals `V tensor I_bank` for some data matrix V if and only if

```
U[e,d] != 0  implies  a'(e)=a(d) and b'(e)=b(d).                 (1)
```

When this holds, V is forced:

```
V = U D,       D[d,d]=(-1)^(a(d) dot b(d)).                     (2)
```

Thus even allowing an unspecified data-only endpoint does not relax (1).
Zero entries of U impose no condition; zero rows allow arbitrary consumer
labels there.

**Proof.** Acting on `|d,c>`, the first word contributes sign
`a(d) dot c` and changes the bank to `c+b(d)`. The second word, after the
U[e,d] branch, contributes sign `a'(e) dot (c+b(d))` and leaves bank
`c+b(d)+b'(e)`. Equivalently the (e,d) bank block of T is

```
U[e,d] (-1)^(a'(e) dot b(d))
       X(b(d)+b'(e)) Z(a(d)+a'(e)).                            (3)
```

For a nonzero entry U[e,d], this block is a nonzero scalar times an invertible
Pauli matrix. To be a scalar multiple of identity, its X label must vanish:
a nonzero translation sends every basis vector to a different bank address.
Its Z label must also vanish: if that label is nonzero, its values on `c=0`
and a suitable coordinate vector have opposite signs. Consequently (1) is
necessary. No cancellation between other data entries can change this block:
equality is required separately for every input d, output e and bank column.

Conversely (1) makes (3) equal to
`U[e,d] (-1)^(a(d) dot b(d)) I_bank`, proving (2) at every block. This proves
the endpoint on arbitrary complex joint inputs. QED.

**Unchanged consumer.** With `a'=a,b'=b`, condition (1) says exactly that U
is block diagonal under the partition by the pair `(a(d),b(d))`. This gives
necessity for P009's sufficient condition. In that case D commutes with U,
so P009's chronological wording “U followed by D” agrees with (2).

**Transported consumer.** If U is a data permutation R, its nonzero entries
are `e=R(d)`. Condition (1) becomes `a'(R(d))=a(d)` and
`b'(R(d))=b(d)`, recovering P008's transport premise. Its later R inverse
is a separate paid operation, not needed for the present bank-return test.

**Support test for choosing a consumer.** A consumer exists precisely when
all nonzero entries in each row of U come from input columns with the same
control pair. This pair then fixes the consumer labels on that row. In
particular, if a block of U is dense, all producer controls on the input side
of that block must be constant. Changing only the second labels cannot repair
a genuinely mixing dense block with nonconstant producer controls.

An additional *invertible data-only* operation after T cannot turn a failed
case into a bank-identity endpoint: if `(R tensor I) T=V tensor I`, then
`T=(R^-1 V) tensor I`, contradicting the theorem. This includes invertible
phase masks. Noninvertible projections and changed joint consumers are outside
that corollary.

## 3. The physical/Fourier frame must be stated

The PR2850 producer is `P(u,v)=X(v)Z(u)` on its bank **in Fourier labels**
u,v of physical data addresses x,y. It is not W controlled by the physical
addresses themselves. Let F be the ordinary Walsh matrix on those data axes;
its inverse includes the exact power-of-two scale. The source's dyadic
`h_word` is a scalar multiple of F with a literal inverse, which gives the
same conjugation. A physical data operation U_phys must therefore be tested
using

```
U_control = F U_phys F^-1.
```

For one axis, with `S=diag(1,i)`, `Z=diag(1,-1)` and X the swap,

```
C = [[(1+i)/2, (1-i)/2], [(1-i)/2, (1+i)/2]],
F C F^-1 = S,           F S F^-1 = C,
F X F^-1 = Z,           F Z F^-1 = X.
```

These are exact 2-by-2 multiplications. The source's physical Q has Fourier
matrix `diag((-1)^(u dot v))` by its kernel definition. It follows that:

| Physical data work inside the interval | Matrix in the control frame | Unchanged consumer |
| --- | --- | --- |
| C on data x or y axes | Diagonal phases in u or v | Admitted |
| Q on the data x,y axes | Diagonal `(-1)^(u dot v)` | Admitted |
| Physical translation X on x | Diagonal `(-1)^u` | Admitted |
| Physical Z on x | Permutation `u -> u+1` | Rejected; transported labels can repair it |
| Physical S on x | Dense C on u | Rejected; merely relabelling the second consumer cannot repair it |

Other data spectator axes can be included by tensor identity. These statements
do not license moving a gate onto the bank or changing a whole joint caller.
In particular **physical C/Q are positive controls, not counterexamples**.
Applying a dense-matrix argument to them in their physical basis while treating
u,v as their coordinates would give an incorrect conclusion.

## 4. Exact smallest source-bound witness and repair

Take f=1, with physical address bits `(x,y,c)` numbered `(0,1,2)` as in
`model.py`. Let

```
P = accumulator_word(1, half=True),
Q = q_word((0,), (1,)),
S_x = phase((0,), 1),       Z_x = phase((0,), 2),
Z_c = phase((2,), 2).
```

The predecessor proves `P^2=Q tensor I_bank`. The interposition tested here
is new: chronological P, U, P, with intended endpoint chronological Q, U
(the matrix UQ). It is not a word asserted valid by PR2850 or P009.

For U=S_x, the physical input basis column `(x,y,c)=(0,0,0)` has output
coefficient `1/2` at `(1,0,0)` under P,S_x,P, whereas Q,S_x gives `i/2`.
For U=Z_x the same coefficients are `1/2` and `-1/2`. Every value is an
exact Gaussian rational.

The stronger residual identity shows why returning bank addresses is
insufficient. Write T_x for the physical XOR `x <- x+c`. The rest of P acts
only on y and c and commutes with S_x and Z_x. Hence

```
P^-1 S_x P = T_x S_x T_x = diag(i^(x xor c)),
P S_x P = Q diag(i^(x xor c)),
P Z_x P = Q diag((-1)^(x+c)).                                  (4)
```

The bank coordinate returns in (4), but the data operator depends on its
incoming value. For S_x, bank lane c=0 sees Q S_x and lane c=1 sees
`i Q S_x^-1`; these differ. For Z_x there is an unwanted Z_bank factor.
This rules out a single V tensor I, including on arbitrary dirty correlated
bank input, rather than merely showing that one target phase was mischosen.

For Z_x, the control-frame permutation sends `(u,v)` to `(u+1,v)`.
Choose second labels `a'(u',v')=u'+1`, `b'(u',v')=v'`. This is realized by
inserting Z_c **before** the second P: its bank matrix is
`P(u',v') Z_c = X(v') Z(u'+1)`. The theorem gives the exact repair

```
chronological P, Z_x, Z_c, P  =  chronological Q, Z_x.           (5)
```

Z_c cannot be commuted to an arbitrary other position without justification.
It is an additional full-array phase instruction, with whatever native and
movement tariff the caller requires; this proof supplies no favorable bill.
For S_x, each output control row receives both values of u with nonzero C
coefficients, so (1) would demand its one consumer label equal both 0 and 1.
No choice of second Pauli label functions alone can provide that repair.
Additional joint operations remain outside this restricted impossibility.

## 5. Evidence and limits

The written proof above is all-parameter within the specified two-word Pauli
interface. Finite exact matrix checks and unchanged-source execution
corroborate it, including full physical basis columns, admitted C/Q/translation
interpositions, rejected S/Z interpositions and the correctly ordered Z repair.
Their concrete domains and counts are reported by the checkers and summarized
in README.md; they do not prove the universal claim by exhaustion.

The contribution does not alter the selected construction, identify a fault
in the existing PR2850 program, strengthen PR2872's different fixed-label
paired-schedule theorem, or claim a new exponent. It does not classify arbitrary
encoded or joint consumers, general bank operations, noninvertible cleanup,
prepared-state endpoints, all-size physical implementations, precision,
movement, native tariffs or supplier admission. These are additional contracts
and costs. This audit stops at a usable exact acceptance criterion and the
basis-correct source examples; it does not justify another construction round
without a complete changed caller and its charged budget.
