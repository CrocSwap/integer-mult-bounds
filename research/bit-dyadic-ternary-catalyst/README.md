# Nine calls in a dyadic ternary model, even with dirty catalysts

**Result.** Three identical dimension-three interchanges need exactly nine
paid calls in the finite frame alphabet below, even with any finite number
of additional registers that contain arbitrary data and must be restored.
This is a scoped computer-assisted obstruction. It does not improve the
selected supplier or establish a lower bound for general rational frames,
nonabelian address actions, or integer multiplication.

The changed premise relative to the three-register result is genuine: the
scalar register space can have any finite dimension. The restriction that
makes this investigation finite is the explicit dyadic ternary frame
alphabet. All factor orders and repetitions in that alphabet are covered;
there is no bounded search over scalar projectors.

## Exact model and theorem

Let `R >= 3` be any finite register count. In the group algebra over
`F_2` of the additive group `M_3(Q)`, write `[A][B] = [A+B]`. A paid factor is

\[
 D_N([A])=I_R+([A]-1)N,
 \qquad N\in M_R(\mathbb F_2),\quad N^2=N,\quad\operatorname{rank}N=1.
\]

The frame alphabet is

\[
 \mathcal A=\{uv^T/2:
 u,v\in\{-1,0,1\}^3\setminus\{0\}\}.
\]

There are 26 nonzero ternary vectors. Two pairs give the same nonzero
outer product exactly when they differ by simultaneous negation, so the
alphabet has `26^2 / 2 = 338` frames. The required endpoint is

\[
 \prod_{j=1}^{k}D_{N_j}([A_j])
 =\operatorname{diag}([I_3],[I_3],[I_3],1,\ldots,1). \tag{1}
\]

Equality means equality of every formal group-algebra coefficient. In
particular, all incoming data in registers 4 through `R` are arbitrary,
all of those registers are restored, and they have no residual influence
on the three outputs. A clean-workspace-only identity is insufficient.
Arbitrary free address transformations between the factors are not part
of this alphabet.

**Theorem.** Equation (1) has no solution with `k <= 8`, for any finite
`R >= 3`. It has a solution with `k = 9` for every such `R`.

The lower bound uses exact finite enumeration of frame multisets and
explicit rational character witnesses. It does not enumerate the
projectors, limit the number of dirty registers, or assume a common
invariant subspace for those projectors.

## 1. Determinant and target-coefficient conditions

Scale every group exponent by two. This is an isomorphism of the additive
rational matrix group. Set `B_j = 2 A_j`, and set `T = 2 I_3`. Thus each
`B_j` is a rank-one matrix with entries in `{-1,0,1}`, and the three
nontrivial target entries are `[T]`.

A rank-one idempotent can be written `N = xy^T` with `y^T x = 1`. The
determinant lemma gives

\[
 \det D_N([B])=1+([B]-1)y^Tx=[B].
\]

Taking determinants of (1) therefore requires

\[
 \sum_{j=1}^k B_j=3T=6I_3. \tag{2}
\]

Next expand each factor as `(I_R-N_j) + [B_j]N_j`. A positional subset
`S` contributes the monomial `[sum_{j in S} B_j]` and an ordered scalar
matrix product: choose `N_j` at positions in `S` and `I_R-N_j` at the
other positions. Every nonempty such product has rank at most one,
because it contains a rank-one factor. The constant factors need not
have rank one; this does not change the product bound.

The coefficient of `[T]` on the right of (1) is

\[
 P=\operatorname{diag}(1,1,1,0,\ldots,0),
 \qquad\operatorname{rank}P=3.
\]

Consequently, there must be at least three **positional** subsets whose
frame sum is `T`. Repeated frame values occupy different positions and
are counted separately. Cancellations or zero subset products can only
make this necessary condition weaker. Its use does not depend on the
factor order or the register dimension.

## 2. Why the finite census is complete

A subset summing to `T` has at least three members: a sum of fewer than
three rank-one rational matrices cannot have rank three. By (2), its
complement sums to `2T = 4I_3`. Each diagonal entry of a frame is at most
one, so this complement has at least four members.

Thus `k <= 6` is impossible. For seven calls the only possible split is
`3 + 4`; for eight calls it is `3 + 5` or `4 + 4`. No other subset size
has been omitted.

A four-frame complement summing to `4I_3` has every diagonal entry of
every frame equal to one. Writing a frame as `uv^T` forces `u = v` with
all three entries in `{+1,-1}`. Up to simultaneous negation of `u` and `v`, there are
four possibilities:

\[
 H_{s,t}=(1,s,t)^T(1,s,t),\qquad s,t\in\{-1,1\}.
\]

The three off-diagonal sum equations and the equation for the total
number of frames force one copy of each `H_{s,t}`. Denote this unique
four-frame multiset by `H`.

For a five-frame complement, each diagonal is a sum of five numbers in
`{-1,0,1}` equal to four. Its terms are four ones and one zero. Hence all
five frames have nonnegative diagonals, and their total trace is twelve.
This is a necessary restriction, not a symmetry assumption. There are
145 frames with nonnegative diagonals. Exhaustive exact enumeration on
that set finds all five-frame complements.

The verifier generates the alphabet from the vector definition, uses
integer matrix sums, and enumerates multisets with replacement. Its
decomposition counts are:

| Exact sum | Number of frames | Number of multisets |
|---|---:|---:|
| `T` | 3 | 8 |
| `T` | 4 | 473 |
| `2T` | 4 | 1, namely `H` |
| `2T` | 5 | 24 |

For seven calls, union each three-frame decomposition of `T` with `H`.
This gives eight candidate multisets; each has exactly one positional
subset summing to `T`, so all eight fail the coefficient-rank condition.

For eight calls, take the union of the `3 + 5` candidates and the
`4 + H` candidates and deduplicate equal full multisets. There are 665.
These are all eight-frame multisets satisfying (2) and admitting at
least one target subset. They are not asserted to be all multisets
satisfying (2) alone; a multiset without a target subset already fails
(1).

| Positional subsets summing to `T` | Eight-frame multisets |
|---:|---:|
| 1 | 579 |
| 2 | 80 |
| 4 | 6 |

The first 659 are excluded by rank. The remaining six are excluded below.
The certificate retains the decompositions, candidates, subset counts,
and exact witnesses; the verifier regenerates the census rather than
accepting these displayed counts as a proof.

## 3. A parity character excludes each survivor

Here is one representative, written using `e_1,e_2,e_3`:

\[
 \{- (e_1+e_2)(e_1+e_2)^T,
 H_{-1,-1},
 (e_1-e_2)(e_1-e_2)^T,
 H_{-1,1},
 H_{1,-1},H_{1,-1},H_{1,1},H_{1,1}\}. \tag{3}
\]

Its six full-sign frames and two sparse frames have total `6I_3`.
For a matrix `B = (b_ij)`, define the rational linear functional

\[
 \ell(B)=\frac{-b_{11}-b_{12}-b_{13}+b_{23}+2b_{33}}2.
\]

On the eight listed frames its values are, in the displayed order,

\[
 (1,2,0,0,0,0,0,0),\qquad \ell(T)=1. \tag{4}
\]

The six surviving multisets form the orbit of (3) under simultaneous
signed coordinate permutations `B -> P B P^T`; the finite orbit has six
elements. The certificate also supplies and checks a direct rational
functional for every survivor, so the exclusion need not rely on an
unchecked symmetry reduction.

The domain of the character matters. Let `L` be the additive subgroup
generated by the paid frames of the particular word. A surviving word
has a subset summing to `T`, so `T` already belongs to `L`. All values
of `ell` on the generators are integers, so `ell` maps `L` to `Z`.
Reduction modulo two therefore defines a well-defined homomorphism

\[
 L\longrightarrow C_2,\qquad B\longmapsto g^{\ell(B)\bmod2}.
\]

Restrict the asserted identity first to `F_2[L]`, then apply the induced
group-algebra map to `F_2[C_2]`. We do **not** claim a nontrivial
homomorphism from the full divisible group `M_3(Q)` to `C_2`.

By (4), seven paid factors map to the identity and one maps to

\[
 I_R+(g-1)N.
\]

The target maps to `diag(g,g,g,1,...,1)`. Comparing coefficients of the
formal basis element `g` gives `N = P`, contradicting ranks one and
three. The order of the eight factors is immaterial after this map.
Although `F_2[C_2]` has zero divisors, the argument only compares its
two formal coefficients; it does not take matrix rank over that ring
or assume it has a fraction field.

This excludes the six remaining frame multisets for every finite `R`.

## 4. An alphabet-valid nine-call identity

Let

\[
 B_1=\begin{pmatrix}0&-1&-1\\0&1&1\\0&1&1\end{pmatrix},\quad
 B_2=\begin{pmatrix}1&0&1\\-1&0&-1\\1&0&1\end{pmatrix},\quad
 B_3=\begin{pmatrix}1&1&0\\1&1&0\\-1&-1&0\end{pmatrix}.
\]

Each is an outer product of nonzero ternary vectors and
`B_1+B_2+B_3 = 2I_3`. Thus `A_i=B_i/2` belongs to the stated alphabet
and `A_1+A_2+A_3=I_3`. For each of the three active scalar coordinate
projectors `E_ww`, apply the three factors with these frames. Their
product is `D_{E_ww}([I_3])`. The nine factors together give (1), while
every additional register is untouched. This is a formal identity,
not a test at one finite address size.

## Paid budget and scope of the negative result

The proposed eight-call mechanism had the optimistic recursive bill

\[
 M_8(a)=\frac{8}{3}(1/3)^{1-a}=\frac89\,3^a.
\]

It would have had room for a positive saving if all required recursive
calls, including frame changes and restoration, fitted within those
eight calls. The theorem rules out that core identity in this alphabet.
The nine-call minimum instead has

\[
 M_9(a)=3^a\ge1\quad(a\ge0),
\]

with equality only at zero saving. Additional nonnegative hosting,
transport, or restoration charges cannot repair this failed budget.
The normalization uses the three requested interchanges: restored
spectators do not become extra completed output roles. The calculation
does not assume that their physical storage or access is free.

This rejects the stated mechanism, even under its favorable bill. It
does not bound quarter-denominator frames, larger vector entries,
different target frames, nonabelian operations, or a different recursive
contract. There is no new kappa or selected-frontier claim.

## Reproduction and evidence

From the repository root:

```sh
python3 -I -O -B research/bit-dyadic-ternary-catalyst/verify.py
python3 -I -B research/bit-dyadic-ternary-catalyst/independent.py
python3.12 -X utf8 -B scripts/research_package.py --package research/bit-dyadic-ternary-catalyst
```

The default command is read-only. It regenerates the finite census,
checks the stored certificate, verifies all character evaluations and
the nine-call witness, and runs deliberate failure controls. Explicit
`--write` regenerates this package's `CERTIFICATE.json`.

The independent implementation uses ordered depth-first enumeration with
coordinate bounds, rather than the primary meet-in-the-middle census. It
compares every decomposition and candidate multiset, reconstructs the six
characters independently, and verifies positional subset counts again using
binomial multiplicities. It refuses `-O`, which would disable its assertions.
Both implementations use Python 3.12 and the standard library only.
Local validation used CPython 3.12.14 on Windows. The registered replay and
source bindings passed; the primary verifier rejected eight deliberately
corrupted certificates and the independent checker rejected two.

The proof uses exact integer and rational arithmetic. Numerical moment
estimates, finite cyclic-address simulations, and a full selected-supplier
cold replay are not acceptance evidence for this local theorem. The
selected construction and its inherited obligations are unchanged.

## Predecessors and contribution

- [Ali Romman's PR #468](https://github.com/CrocSwap/integer-mult-bounds/pull/468),
  retained in `research/bit-three-register-lower-bound/README.md`, proves
  the unrestricted-rational-frame nine-call lower bound for its specified
  three-register model. It explicitly leaves additional registers outside
  its scope.
- That work builds on eumemic's [PR #288](https://github.com/CrocSwap/integer-mult-bounds/pull/288),
  pinned at `475a088b5862f75f0b10596cfd6842d19531a5ec`, and huxint's
  [PR #203](https://github.com/CrocSwap/integer-mult-bounds/pull/203), pinned
  at `d2873e20750d0949d2ad75cbc4cd82b5b1a74e84`.
- woklerx's [PR #1456](https://github.com/CrocSwap/integer-mult-bounds/pull/1456)
  already investigates arbitrary-register obstructions with at most one
  rational frame relation, at head
  `83b6ad2ace819a96128131a3600ee914a66dd0dd`. This package does not claim that restriction,
  the general projection method, or parity characters as new techniques.
- Cinna Davis's [PR #1541](https://github.com/CrocSwap/integer-mult-bounds/pull/1541)
  (head `194724d87505ec2517fdca1c1884da12398f4c33`) concerns a different
  finite nonabelian group model. This package retains
  additive rational matrix exponents.

The contribution here is the complete 338-frame dyadic ternary census,
its arbitrary-register exclusion, and exact reproducible witnesses for
the six surviving multisets. Coordination is recorded in
[discussion #1594](https://github.com/CrocSwap/integer-mult-bounds/discussions/1594).
Prepared for Tuafo with substantial OpenAI Codex assistance: GPT-6 Astra
at maximum reasoning for derivation, separate implementations and proof
review, with root integration. Separate AI checks are not independent human
review or proof-assistant formalization. Apache-2.0.

## Open next questions

1. **Can a larger explicit dyadic alphabet escape the obstruction?** A
   feasible first step is to add frames `uv^T/4` to the present alphabet,
   or allow a bounded larger vector alphabet, then derive the determinant
   and coefficient-rank restrictions,
   and price the complete favorable bill before any census. The blocker is
   that the present `3 + 5` / `4 + 4` reduction and six-survivor list no
   longer apply automatically. Merely changing the denominator need not
   create a feasible identity.
2. **Is there an alphabet-independent extra-register obstruction at eight
   calls?** The present character witnesses suggest a precise question but
   do not prove it. A first step is to classify which frame-relation
   lattices admit a character seeing fewer than three paid factors while
   seeing all three targets. Rational frames outside this finite alphabet
   are the blocker; the known at-most-one-relation scope must be credited
   rather than repeated.
