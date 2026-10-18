# Three coordinate swaps: arbitrary dirty workspace costs nine calls

This is a computer-assisted theorem in the exact formal register model of
commdata2338's PR1414 and PR1491. The written rank-compression argument is the
arbitrary-register step. The 35 checked CNF/DRUP certificates are an essential
finite premise. Neither part is a multiplication theorem or an unconditional
lower bound for bit circuits.

## Model and claim

Let `G=GL_2(F2)`, `R=F2[G]`, and

```
a = [[1,1],[0,1]], b = [[1,0],[1,1]], s = aba = bab = [[0,1],[1,0]].
```

Registers are arbitrary R-module inputs. For any finite register count r,
allow free scalar `GL_r(F2)` changes and paid units

```
D_N(g) = I + ([g]+1) N,  g in {a,b},
N = u v^T over F2,  v^T u = 1.
```

Each paid occurrence costs one; inverses are paid. There are no other free
address operations, copies, erasures, overwrites or clean allocations. With
`P=diag(I_t,0)`, t active coordinate swaps request the complete formal map

```
T_t = I + ([s]+1) P.
```

Every one of the remaining r−t registers starts arbitrarily dirty and is
returned identically; all original dirty coordinates have the stated map.
Equality is in `M_r(R)`, not only the natural 2r-dimensional representation.

**Theorem.** For every finite r≥3, three active swaps require exactly **nine**
paid calls, even with arbitrary free scalar mixing and restored dirty extras.

The attaining word needs only the three active registers. The lower bound
uses a stronger free-scalar relaxation than a physical supplier may admit.
The complete paid bill is nine including undo work; no free source access,
frame conversion or coefficient preparation is asserted for a physical
implementation. This closes the arbitrary-workspace three-target question
left by PR1414 and the exactly-three-register certificate PR1491.

## 1. Normalize scalar work and use sign parity

As in PR1414, move scalar basis changes to the right; they conjugate each N
and preserve its rank-one idempotence. The augmentation `[g] -> 1` sends every
paid unit and T_t to I, so the final scalar factor must be I. All free mixing
is therefore represented by the choices of u,v in the paid factors.

The sign map `G=S3 -> C2`, with characteristic-two algebra
`F2[C2]=F2[epsilon]/(epsilon^2)`, sends each paid factor to `I+epsilon N` and
T_t to `I+epsilon P`. Therefore `sum N_i=P`. Since `trace N_i=v_i^T u_i=1`,

```
number of paid calls = t modulo 2.
```

For t=3 a word shorter than nine has odd length at most seven.

## 2. General role-compression lemma

**Lemma.** Any q-call word for T_t has an equivalent q-call word on at most
q−t registers, retaining t active swaps and restored dirty extras. Moreover
the number of a calls and the number of b calls are each at least t.

Let U_a be the span of the image vectors u_i of a-labeled calls, and U_b the
span for b-labeled calls. Apply the natural address representation of G to
2r coordinates, ordered by their two address components. The paid factors
become block shears

```
a: [[I,N],[0,I]],     b: [[I,0],[N,I]].
```

The target is

```
[[I+P, P], [P, I+P]].
```

Follow chronological left multiplication. Only a calls change the top block
row, and each change has output image contained in the corresponding line
span(u_i). The top-right block initially vanishes and ends at P. Thus
`im P <= U_a`. Likewise the bottom-left block gives `im P <= U_b`. This is a
necessary consequence of a formal word, with no claim that this address
representation is faithful.

If n_a and n_b are the two label counts, then

```
n_a >= t, n_b >= t,
dim(U_a+U_b) <= dim U_a+dim U_b−t <= n_a+n_b−t = q−t.
```

Set C=U_a+U_b. Every image vector u_i belongs to C, so each projector N_i
preserves C. Its restriction still has rank one and is idempotent:
`u_i in C` and `v_i^T u_i=1`, so `v_i|C` is nonzero. Also P preserves C because
`im P <= C`. Restrict the complete formal identity to C. Since P is an
idempotent of rank t on C, choose a scalar basis

```
C = im P direct-sum (C intersect ker P).
```

The restricted endpoint is exactly t swaps plus identity on the other
`dim C−t` dirty registers. All restricted paid units are members of the same
alphabet. No clean scratch is introduced. This proves the lemma for arbitrary
finite r and arbitrary R-module inputs.

## 3. Seven calls reduce to 35 normalized four-register patterns

The label-count part of the lemma gives at least six calls for t=3; parity
leaves only seven below nine. At seven, the label counts are (3,4) or (4,3),
and the compressed register count is at most four.

Conjugating address maps by s exchanges a and b while preserving the target
s. Hence assume three a calls and four b calls. Because the three a image
vectors span im P, they are linearly independent and constitute a basis of
that three-dimensional active space. A single scalar basis change, chosen
inside im P and extended on `C intersect ker P`, sends these vectors, in their
word order, to e0,e1,e2. It leaves P unchanged. If dim C=3, append a fourth
identity register with arbitrary dirty input and zero coupling.

Consequently every seven-call arbitrary-workspace counterexample has a
four-register representative with the three a image vectors fixed at
e0,e1,e2. All v vectors remain arbitrary subject to `v^T u=1`; every b factor
has all four-bit u,v choices. The fourth register must be returned identically.
There are exactly `binomial(7,3)=35` a/b label patterns. These reductions do
not identify patterns by an unproved cyclic, time or symmetry quotient.

## 4. Exact finite encoding and certificate check

`cnf.py` independently realizes G as permutations of the three nonzero
binary address vectors. For each label pattern it builds a Boolean formula
for all source u,v bits and all formal coefficients of the four-register
product. The three normalized a image vectors are constants. Every projector
has the exact `v^T u=1` constraint. All 96 output coefficient bits (six group
labels times sixteen matrix entries) are constrained to T_3, including the
fourth dirty register and every possible leakage coefficient.

For chronological left multiplication, if S_h is the scalar matrix at group
label h, define `w_h,j = sum_k v_k S_h,k,j`. A g call updates

```
S'_h,i,j = S_h,i,j + u_i (w_h,j + w_(g*h),j).
```

Here g is an involution. XOR and AND use Tseitin clauses with both directions
of equivalence, not one-way implications. Every choice of admissible u,v has
exactly its induced state extension; satisfiability is equivalent to the
normalized word's existence. The original clauses have no heuristic cuts.

All 35 formulas are UNSAT. The supplied `CERTIFICATES.json.gz` contains the
literal clauses and proof records. `verify.py` rebuilds every formula and
requires exact equality. It checks each added proof clause by unit propagation
under the negation of that clause, using only the original clauses and earlier
validated additions. Deletion records are ignored; every retained clause is
already a consequence of the original formula, so retaining it is sound.
Every certificate must derive the empty clause. No SAT solver is used by this
replay. The proof-producing run used python-sat 1.8.dev24 / Glucose3; the
separate Boolean right-product encoding used Z3 4.13.4.0 and also returned
35 UNSAT results without timeout. That independent run is corroboration;
the checked RUP certificates supply the finite premise.

The checker tests its watched propagation against a separate slow implementation
on all two-variable clause sets and all consistent literal assumptions, and
rejects invalid and incomplete proofs. Exact Tseitin truth-table controls and
a satisfying assignment for the full nine-call construction guard encoding
vacuity. Natural-representation-only equality is explicitly rejected as an
insufficient endpoint test.

Combining all 35 exclusions with Sections 1–3 eliminates every word shorter
than nine on any finite dirty workspace. This is a computer-assisted scoped
theorem; neither the written argument nor the checker is verified in Lean.

## 5. Nine calls attain the entire dirty boundary

For any scalar idempotent N, direct expansion gives
`D_N(g) D_N(h) = D_N(gh)`. Apply b,a,b to each of the three distinct coordinate
projectors E00,E11,E22. Since `bab=s`, each active register undergoes exactly
its required swap; all other registers remain identity. There are nine paid
calls, no scratch registers, no scalar basis changes and no omitted restoration.
The literal formal word and its faithful 24-column regular representation
are checked in the replay. This proves the upper bound and finishes the theorem.
