# Leading-section conditioning controls all completed downsets

Prepared for Brian (`JoyboyBrian`) with substantial OpenAI Codex assistance.
Apache-2.0.

This independent audit proves a stronger completed-call norm bound than the
one retained in `rational-unitary-fft/FULL-PROOF.md` §§2–4. It applies to every
complex matrix whose original leading sections meet the stated inverse bound,
and to every binary tree of contiguous intervals, balanced or unbalanced.
The key observation is that every descendant's scalar unit-LDU factors are
principal restrictions of **one global factorization**. This avoids charging
the Schur descendant's larger direct norm again in every scalar row bound.

[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202#discussioncomment-19131470).
This answers the norm implication explicitly left inherited by
[PR #4755](https://github.com/CrocSwap/integer-mult-bounds/pull/4755).
It does not extend that package's physical-fragment proof or claim a new
FFT/generator, rounded execution, physical cost, selected κ or complete
multiplication theorem.

## Theorem

Let `T` be any complex `N×N` matrix, `N>=1`, with

```
Λ,Q >= 1,   ||T||₂ <= Λ,   ||T[0:k,0:k]^-1||₂ <= Q  (1<=k<=N).
```

All leading sections must be invertible. Bounds smaller than one may be
normalized upward before applying the theorem. No Toeplitz, Hermitian,
positivity, near-identity, dyadic-dimension or balanced-tree premise is used.
Let an arbitrary binary contiguous interval tree recursively execute the
upper block shear, its two children in parallel, then the lower block shear;
a singleton executes its scalar pivot. Children may be legally interleaved.
An atom is one complete shear or scalar, not a primitive gate inside it.

Write `χ=ΛQ`, `U₀=Λ+Λ²Q`, and `W=1+sqrt(N-1)χ`. For every downset `I`
of the resulting atomic dependency DAG, its chronological endpoint product
`P(I)` satisfies

```
||P(I)||₂      <= Q U₀² W³,
||P(I)^-1||₂ <= Q³ U₀² W³
                  <= 32 N^(3/2) χ^8.
```

The common bound improves the predecessor's sufficient
`256 N³ χ^12` at the same ideal completed-call boundary. This is a sufficient
bound, not a sharp constant. A remaining suffix is `T P(I)^-1`, so its direct
bound needs the additional endpoint factor `Λ`; its inverse similarly needs
`Q`. No unit-endpoint suffix assumption is made.

## 1. One global unit-LDU factorization and its row/column bounds

The nonzero leading determinants give the unique factorization `T=L D U`,
where `L,U` are respectively unit lower/upper triangular and `D` is nonsingular
diagonal. Let `T_k=T[0:k,0:k]`. For `1<=k<N`, the last row of
`T_k^-1 T[0:k,k:N]` equals the tail `U[k-1,k:N]`: substitute the leading
LDU factors; the last row of unit-upper `U_k^-1` is the last coordinate row.
Its Euclidean length is at most `QΛ=χ`.

Dually, the last column of `T[k:N,0:k] T_k^-1` equals
`L[k:N,k-1]`: the last column of unit-lower `L_k^-1` is the last coordinate
column. Its length is at most `χ`. These are ordinary complex matrix
products and inverses. There is no conjugation of the row/column solve.
Both off-diagonal Frobenius norms are consequently at most
`sqrt(N-1)χ`. The triangle inequality with the identity gives

```
||L||₂, ||U||₂ <= W.
```

This uses the **original** leading solves. Replacing `Λ` here with a generic
Schur-descendant bound would lose the improvement.

For pivot `d_k`, the scalar Schur formula gives `|d_k|<=U₀`, using the
norms of restrictions of `T` and of `T[k-1]^-1`; for the first pivot use
`|d_1|<=Λ<=U₀`. The last diagonal entry of `T_k^-1` is `d_k^-1`, so
`|d_k^-1|<=Q`. Therefore

```
||D||₂ <= U₀,   ||D^-1||₂ <= Q,
L^-1 = D U T^-1,   U^-1 = T^-1 L D,
||L^-1||₂, ||U^-1||₂ <= V := Q U₀ W.
```

The exact order in these inverse identities is essential. Since `Q,U₀>=1`,
`V>=W>=1`, so identity blocks fit every direct-sum estimate below.

## 2. Every contiguous Schur descendant uses restrictions of the same factors

For `J=[a,b)`, define `M_J=T_b/T_a`, with `T_0` the empty prefix. Block
elimination of `T_b=L_b D_b U_b` at position `a` gives

```
M_J = L[J,J] D[J,J] U[J,J].
```

The lower-right trailing block after eliminating a leading block has exactly
these factors. Uniqueness of scalar unit-LDU proves the claim; it is not an
assumption that a Schur complement is itself Toeplitz. The Schur quotient
identity then shows that any binary split at `c` produces children
`M_[a,c)` and `M_[c,b)`. All required pivots remain nonzero.

A principal restriction contracts the spectral norm. Moreover, for a
**contiguous interval** `J`,

```
L[J,J]^-1 = L^-1[J,J],   U[J,J]^-1 = U^-1[J,J].
```

For example the entry equation for a triangular product at indices `i,j`
uses only summation indices between `i` and `j`; these all remain in `J`.
Thus restricting the global inverse gives the identity product on `J`.
The same assertion need not hold for a principal set with holes, which is
why interval ownership is a hypothesis. All descendant unit factors and
inverses are now uniformly bounded by `W` and `V`, without a depth multiplier.

At a split, write the node matrix as `[[A,B],[C,E]]`. Define
`K=A^-1 B`, `H=C A^-1`, upper atom `R=[[I,K],[0,I]]`, and lower atom
`B_low=[[I,0],[H,I]]`. Ordinary transpose may implement the right solve
`H=(A.T^-1 C.T).T`; conjugate transpose without matching conjugation changes
complex coefficients. The block endpoint identity is

```
M_J = B_low diag(M_left,M_right) R.
```

Uniqueness also gives

```
L_J = B_low diag(L_left,L_right),
D_J = diag(D_left,D_right),
U_J = diag(U_left,U_right) R.
```

These identities require no equal child sizes.

## 3. The completed-downset factorization, with order retained

For a downset `I`, let `C(I)` be the disjoint maximal fully completed subtrees.
Define `L_C` as the direct sum of their full unit-lower factors and identity
on other coordinates. Define `D_I` to contain a pivot exactly when that leaf
has completed, and one otherwise. Define an upper frontier `F(I)` by stopping
at any internal node whose upper atom is absent from `I`, descending otherwise,
and retaining all singleton leaves. Its intervals partition the coordinates.
Let `U_F` be the direct sum of the full unit-upper factors of those intervals.
Then

```
P(I) = L_C D_I U_F^-1 U.
```

Proof: recursively define partial lower, diagonal and upper factors. An empty
subtree has three identity factors. A completed leaf has `(1,d_k,1)`. An
internal node whose upper atom is present has

```
L_partial = B_low^ε diag(L_left_partial,L_right_partial),
D_partial = diag(D_left_partial,D_right_partial),
U_partial = diag(U_left_partial,U_right_partial) R,
```

where `ε=1` only if the lower atom is present. In that case both children
are completely finished. Multiplying in this order gives the executed node
product by induction, without commuting any overlapping factors. The lower
recursion is precisely `L_C`; the diagonal recursion is `D_I`.
For the upper factor, induction on frontier nodes gives
`U = U_F U_partial`, hence `U_partial=U_F^-1 U`, with the inverse on the
left. A legal interleaving changes only products on disjoint child supports,
which commute. Thus the factorization holds for every downset, independent
of how a linearization reached it and independent of the tree's depth.

Now `||L_C||<=W`, `||L_C^-1||<=V`, `||D_I||<=U₀`,
`||D_I^-1||<=Q`, `||U_F||<=W`, `||U_F^-1||<=V`. The four-factor product
and its correctly reversed inverse give

```
||P(I)|| <= W U₀ V W = Q U₀² W³,
||P(I)^-1|| <= V W Q V = Q³ U₀² W³.
```

Finally `U₀<=2Λ²Q`, `Q³U₀²<=4Λ⁴Q⁵<=4χ⁵`, and
`W<=2sqrt(N)χ`; this proves the common `32 N^(3/2)χ^8` bound. For `N=1`,
`W=1` and the two downsets are identity and the one pivot. The same proof
and estimates hold without invoking a nonexistent split.

## Scope, evidence and reproduction

This theorem concerns complete ideal calls. It neither improves the current
factory's explicit allocation automatically nor bounds unfinished generator
fragments. The existing physical-cut, perturbation, rank and rounding arguments
would need a separate audited substitution before any implementation precision
change. No source compiler or frozen proof is modified.

The oracle implements its own matrix product, Gauss–Jordan inverse, scalar
LDU elimination, Schur quotient, interval trees, all downsets of each selected
tree, and frontier products. It shares only the retained exact Gaussian-rational
scalar representation. No predecessor verifier is imported. Exact nonsymmetric,
non-Toeplitz complex examples cover `N=1`, both `N=3` trees, all five `N=4`
trees, and three asymmetric/balanced `N=5` choices: 11 trees and 398 downsets.
Eight cuts have both nontrivial completed lower factors and a nontrivial upper
frontier. Each state checks the forward and correctly reversed inverse formula,
original leading solves, descendant restrictions and a conservative rational
norm envelope against the squared common bound. The proof above supplies the
universal theorem; finite checks are not substituted for it.

An AST selection executes the original `full_plan` and `parallel` functions
on one complex size-four matrix, with independent whole-shear/scalar callbacks.
Its ten ideal atoms reproduce the matrix exactly. This binds the source's
block schedule and ordinary right-solve direction, but does not execute actual
FFT/generator fragments or the Full factory.

Five controls discriminate a wrong frontier factor order, a singular first
leading section despite an invertible whole matrix, a noncontiguous triangular
inverse restriction, use of only the whole-matrix inverse bound, and replacing
ordinary transpose by an unmatched complex adjoint in the right solve.
The whole-inverse-only control uses `[[1/64,1],[1,0]]`: both endpoint norms
are below two while its upper factor has an entry 64.

Base `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7. The
physical-cut predecessor #4755 has head
`653289c67733e1b0feb24ddac796003ebb827e55`. The same-ρ near-identity theorem
#4209 has head `ccc33bfde8baadef7979fac81e28c0a6f6f278c4`; it does not
supply the present general leading-section hypothesis. The fresh round search
covered 299 open PRs, 3721 Discussion records and 6319 local notes with complete
inventories. Live #4202 and the relevant predecessor heads were checked.
Search coverage is not a novelty certificate. All source bytes are pinned in
`SOURCES.json`; every live input is declared in `VERIFY.json`.

```
python3 scripts/research_package.py --package research/leading-section-downset-audit --check-only
python3.12 scripts/research_package.py --package research/leading-section-downset-audit
python3 -B scripts/check_research_commit.py --package research/leading-section-downset-audit --check-source-history
```

The registered normal and optimized commands use Python 3.12 and the standard
library only. Run the last preflight after committing. An official export can
be integrity-checked and `verify.py` run directly without Git. No full historical
suite, Lean, Docker, normalized/raw Gaussian execution or multiplication replay
is claimed. Author-process agent review is not independent human/formal
acceptance.

## Open next questions

Can the sharper completed-call envelope be substituted into the actual Full
allocation while preserving every downstream coefficient, child, physical-cut
and data-grid inequality? First make a dependency ledger for each occurrence
of the old envelope in `full.allocation`, including its third power in the
operator defect and the generator/scalar fragment allowance. Merely changing
a constant in the factory would not prove its rounded caller contract.

## Attribution

Jose Manuel supplied the original global scalar-LDU/frontier argument and
polynomial completed-downset bound in `FULL-PROOF.md`, last changed at
`7ab1bc8973cc9e606053c65f094ca3abc4a42fee`; #4205 retains it at final head
`78c72e563173f3822fcb4efed9ceeccf05630258`. Vlado supplied the recursive
scheduler. Classical block elimination, Schur quotient, triangular inverse
and Frobenius inequalities underlie this proof. The new scoped contribution
is the independent restriction-based sharpening and arbitrary interval-tree
extension. #4209's near-identity Schur-majorant theorem has different premises;
#4755's physical trace audit intentionally leaves the norm hypothesis open.
