# A block-solve envelope for completed elimination downsets

This contribution is produced by Nick Petalas. Apache-2.0.

**Claim type: scoped all-size proof, with exact finite corroboration.**
At the ideal completed-shear/scalar boundary of recursive block elimination,
the common spectral-norm envelope improves from Brian's proposed
`32 N^(3/2) (ΛQ)^8` in [PR #4788](https://github.com/CrocSwap/integer-mult-bounds/pull/4788)
to **`2 sqrt(N) (ΛQ)^2`**. The new proof bounds whole block rows and inverse
block columns through original leading solves. It does not modify a compiler
or rounded allocation. There is no new κ or selected-frontier claim.

## Theorem and boundary

Let `T` be a complex `N×N` matrix, `N>=1`, such that

```
Λ,Q >= 1,   ||T||₂ <= Λ,   ||T_k^-1||₂ <= Q  for 1<=k<=N,
T_k = T[0:k,0:k].
```

Every leading section is invertible. Put `χ=ΛQ` and `S=Λ+Λ²Q`.
Choose any binary tree of contiguous coordinate intervals. At `[a,b)` split
at `s`, the reference matrix is the Schur descendant `T_b/T_a`, with the
empty-prefix convention. Execute the upper shear, both children in any
legal interleaving, then the lower shear. A leaf executes its scalar pivot.
Atoms are complete ideal shears and scalars, including identity atoms.

For every downset of this atomic dependency order, let `P` be its endpoint
product. Form a partition by stopping at a fully finished subtree or a
subtree none of whose atoms has executed, and otherwise descending. Label
its intervals finished or untouched. If their counts are `c` and `u`, then

```
||P||₂²      <= c S² + u(1+χ²),
||P^-1||₂² <= c Q² + u(1+χ²).
```

The partition has `1<=c+u<=N`. Since `S>=1+χ>=sqrt(1+χ²)` and
`Q<=χ`, this implies

```
||P||₂      <= sqrt(N) (Λ+Λ²Q),
||P^-1||₂ <= sqrt(N(1+χ²)),
```

and the common envelope `2 sqrt(N) χ²`. Neither Toeplitz structure,
positivity, equal splits nor a balanced tree is required. The theorem
concerns complete calls. Cuts inside a generator/FFT call, rounded arithmetic,
storage, native cost and the complete multiplication theorem are outside scope.

## Proof

### 1. Retain the global factorization and its order

Write the unique scalar unit-LDU factorization as `T=L D U`. For an interval
`J=[a,b)`, write `M_J=T_b/T_a` and `U_J=U[J,J]`. The identities
`M_J=L[J,J] D[J,J] U_J` and the completed-downset/frontier factorization
are inherited from Jose Manuel's `rational-unitary-fft/FULL-PROOF.md`,
sections 2 and 4, and Brian's PR #4788, sections 2 and 3, head
`ddd98e28b1d6a674b1d6b93c5d7de8a9f9c86eec`.
The latter includes arbitrary contiguous interval trees. They are cited
inputs, not results audited here.

Let `B` be the finished/untouched partition. Define

```
U_B = direct_sum over J in B of U_J,
E_B = direct_sum over J in B of (M_J if finished, I_J if untouched).
```

The inherited factorization gives, in this order,

```
P = E_B U_B^-1 U,                 (1)
P^-1 = U^-1 U_B E_B^-1.           (2)
```

Indeed the usual upper frontier stops at untouched internal nodes and has
singleton leaves inside finished nodes. Replacing those singletons within a
finished `J` by `U_J` changes its left factor from `L_J D_J` to
`M_J=L_J D_J U_J`; the new right factor `U_J^-1` cancels that change.
Untouched blocks already have left factor identity and upper block `U_J`.
This gives (1) without commuting overlapping factors. Incomparable atoms
have disjoint intervals, so all legal linearizations give the same product.
Equivalently, contract each finished or untouched node to one block. At an
open internal node its lower atom is absent, so its product is
`diag(P_left,P_right) R`. Substituting the child formulas and
`U_node=diag(U_left,U_right) R` proves (1) inductively for every interval
tree. The two stopping cases are respectively `P=M_J` and `P=I_J`.

### 2. Bound forward block rows

For a finished `J=[a,b)`, equation (1) gives

```
P[J,:a] = 0,
P[J,a:N] = T[J,a:N] - T[J,:a] T_a^-1 T[:a,a:N].       (3)
```

Eliminate the leading `a` rows of `T=LDU` and restrict the resulting
rectangular Schur row to `J`. Each restriction of `T` has norm at most `Λ`.
Thus this whole block row has norm at most `S`. At `a=0` the second term
is absent and `Λ<=S` suffices.

For an untouched `J`, its row is `U_J^-1 U[J,:]`. It is zero before `a`,
identity on `J`, and has tail

```
K_J = (T_b^-1 T[:b,b:N])[a:b,:].                      (4)
```

To see this, cancel `L_b D_b` in `T_b^-1 T[:b,b:N]`. The last block rows
of the result are `U_J^-1 U[J,b:N]`. Hence `||K_J||<=QΛ=χ`.
The row `[I_J K_J]` has squared norm `1+||K_J||²<=1+χ²` by its Gram
product. For any `x`, sum the squared norms of the disjoint block-row
outputs of `Px`. This proves `||P||²<=cS²+u(1+χ²)`.

### 3. Bound inverse block columns

For every interval `J=[a,b)`, triangular block inversion gives

```
(U^-1[:,J] U_J)[0:b,:] = [-T_a^-1 T[:a,J]; I_J],     (5)
(U^-1[:,J] U_J)[b:N,:] = 0.
```

At `a=0` the top block is empty. For the top identity, invert the upper
`2×2` blocks on `[:a,J]` and use
`T_a^-1 T[:a,J]=U[:a,:a]^-1 U[:a,J]`.

An untouched block column in (2) equals (5). Its norm is at most
`sqrt(1+χ²)`, using the original leading solve at `a`, or is one if `a=0`.
For a finished block, multiply (5) on the right by `M_J^-1`.
The ordinary block inverse formula identifies the result as

```
P^-1[0:b,J] = T_b^-1[:,a:b],
P^-1[b:N,J] = 0.                                      (6)
```

Its whole block-column norm is at most `Q`. This avoids multiplying
separate bounds for the two factors in (5).

For disjoint input blocks, `P^-1 x=sum_J C_J x_J`. The triangle and
Cauchy-Schwarz inequalities give

```
||sum_J C_J x_J|| <= sum_J ||C_J|| ||x_J||
                 <= sqrt(sum_J ||C_J||²) ||x||.
```

This proves the inverse inequality. Empty downsets, finished roots,
singletons and zero-width tails are included. Finally
`S=Λ(1+χ)<=2Λχ<=2χ²` proves the common envelope.

## Exact evidence and reproduction

`verify.py` is a self-contained standard-library checker. It constructs
literal upper/child/lower atomic programs and checks all binary contiguous
interval trees through five leaves and every downset of each tree, for one
real and one nonreal rational fixture per size. Complex matrices use faithful
interleaved rational realification. No predecessor verifier or unmerged Git
object is imported.

For each downset it computes `P` by literal atomic multiplication and its
inverse by exact elimination, then checks (1), (3), (4), (5) and (6).
Exact rational positive-semidefinite tests certify block norms and both
assembled squared bounds. The printed receipt enumerates its checks and
binds them to hashes of the package files. Checks use explicit exceptions
and remain enabled under `-O`. Rejection controls cover wrong factor order,
omitted finished endpoints, wrong inverse signs, invalid partitions, invalid
spectral certificates and using only the whole-matrix inverse premise.
The complete finite replay passes 46 trees, 2,380 downsets, 9,520 matrix
identities, 9,372 partition blocks and 23,504 downset spectral certificates.
Eleven control groups pass, including 2,244 wrong-order, 2,160 omitted-endpoint
and 1,940 inverse-sign distinguishing states. These are finite coverage counts,
not claims about every complex matrix.

From the worktree root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/downset-block-solve-bound/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/downset-block-solve-bound/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/downset-block-solve-bound
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/downset-block-solve-bound --check-source-history
```

The last command follows committing. The universal claim rests on the written
proof. A selected-baseline metadata control passed; the selected construction
was not replayed. Independent human and formal proof-kernel review are unclaimed.

Checker resource limits: Python/Fraction arithmetic allocates managed objects.
The checker fixes at most five logical coordinates and ten real coordinates,
at most 16 tree shapes per size, and at most 256 downsets per tree. Loop
bounds follow these capacities or fixed package-file inventories. No recursion,
dynamic imports, code evaluation, subprocesses or external runtime dependencies are used.
The three negative-control callbacks have fixed local targets and no retained
state. AST syntax validation and warning-strict execution supplement the replay;
no unavailable standalone lint or type-check pass is claimed. A future
parameterized checker must add input/bit-size limits before lifting these
fixed-fixture resource bounds.

## Open next questions

1. Can this envelope replace the old one in the complete rounded Full factory?
   First list every old-envelope dependency and prove the new allocation
   inequalities. Unfinished generator fragments and scalar/data grids retain
   their own obligations. No factory substitution is supplied here.
2. Is square-root growth in the number of frontier blocks necessary when
   `Λ,Q` stay bounded? Seek an explicit growing family or a bound exploiting
   shared block-solve geometry. No asymptotic sharpness claim is made.

## Attribution and overlap

Credit Brian (JoyboyBrian), PR #4788, for global-factor restrictions,
arbitrary interval trees and the previous `32 N^(3/2)χ^8` envelope;
Jose Manuel (jmbarrancoml), PR #4205, for the original scalar-LDU/frontier
proof and polynomial Full-recursion envelope; and Vlado Vojdanovski,
PR #1673, for the recursive compiler. Classical Schur and block inverse
identities are background. The new step is the mixed finished/untouched
partition and direct original-leading-solve block norm estimate. Predecessor
credit and disclosures remain unchanged in their own packages.

The task changes `uniform-transfer-audit` into a new precision-interface
inequality. Brian's open package studies the same quantity and is the
nearest predecessor. Triangular parity-prefix/suffix and dirty FFT gate-cut
packages use different schedules and boundaries; this does not extend their
exact constants or audit their results.

Canonical base is `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133325)
records the scope. Main README searches, merged PR searches, live open PR
bodies, recent handoffs and local reservations were checked. Those searches
do not cover unpublished investigations or every historical diff.
Provenance pins are in `SOURCES.json`; runtime needs only this package.
The overlap helper covered 367 open PRs and 3,821 Discussion records at its
21:46–21:47 UTC snapshot. Its sparse local inventory covered 115 of 6,319
HEAD notes; separate `git grep` searched all main package READMEs for the
distinctive terms. No complete local-note inventory or novelty certificate
is claimed. A canonical refresh after the first replay retained the same base.
