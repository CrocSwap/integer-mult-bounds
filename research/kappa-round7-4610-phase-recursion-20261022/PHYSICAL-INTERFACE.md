# Charged grouped-phase and selected-position interfaces

Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.

This is a written extension of the retained compact-control primitive. Lean
checks its address algebra and separate phase identities. The all-size tape
argument below inherits the retained chunk-swap and record-paid rotation
theorems. It is not a complete Lean machine or multiplication proof.

## Input and workspace contract

Use the actual retained lexicographic layout, not a gathered q digit. An
active group has e selected bits at common offset rho in e consecutive K-bit
chunks, possibly spanning the fixed number m of original slots. All other
address bits are spectators. The group lies after two complete front fields
and before a complete back field. Each available field has H=dG bits, with
e<=d and `G=4 ceil(log2 p)+6`. Split off at most `(e-1)G` bits from each
field; remaining bits are spectators. Empty lists are elementary cases.

The global reservations, whole-row splits, and restoration before children
are the exact contracts in the frozen
[layout source](../kappa-round6-query-normalizer-20261022/layout-audit/sources/notes/compact-control-layout.tex#L18-L54).
In particular these are complete ranges of existing address coordinates,
with arbitrary contents, rather than independent zero scratch coordinates.

Let M records of R bits have volume V=MR. Assume A=ceil(log2(2V))=O(p),
K/log p tends to infinity, and R exceeds every fixed power of p. These are
the original long-record and compact-field hypotheses. The primitive below
uses a fixed number of tapes and no additional productive field.

## Parallel selected-position addition

Specify n pairs `(s_i,t_i)` of selected source and target positions. Targets
are distinct; no source is a target. Sources may repeat. A fixed recipe
generates the positions in polynomial time in A. The intended address map is

```
x[t_i] ^= x[s_i]  for every i,
all other address bits retained.
```

Here "selected" retains the strict **same-rho, distinct K-bit chunk**
condition above. It does not mean arbitrary adjacent bit positions. The
runtime finite model rejects structural violations. For example positions
`[0,1]` and sources `[2,3]` at K=6 have overlapping guard windows and are
outside this contract, even when two separately evaluated guard inequalities
hold. The parent audit supplied this useful negative control; admitting it
would corrupt a dirty t field.

`ParallelControls.lean` proves its involution for arbitrary index type,
including repeated controls. Treat the entire active group as one binary
target field Y. This does not permute its records or gather its bits. A
selected target position j owns the K-bit segment `[rho+jK,rho+(j+1)K)`.
Distinct target segments are disjoint and contain no selected source bit.
If the highest selected bit is a target, omit that one pair initially and
execute it by the elementary two-bit XOR after repair; its source cannot be
another target. All remaining segments fit in Y, even for rho=K-1.

Carve n radix-B digits, B=2^G, from each dirty front field u,t and the back
field b. For fixed controls z_i in front, execute the retained four-step
dirty identity simultaneously on the target segments v_i and digits t_i:

```
v_i += 2 z_i t_i
t_i += parity(v_i)
v_i += z_i(1-2 t_i)
t_i -= parity(v_i) xor z_i.
```

The two changes to Y are modular rotations by the appropriate sums shifted
to target positions. For each change to t, swap t with the back field,
rotate that back field by the packed target parities, and swap back. This
costs four compact swaps and four rotations. Each rotation is independent
of its target. Back-field original contents return after each swap pair.

For the general source positions, including interleaving sources and targets
inside Y, first execute that identity with the old parities of u. Then swap
u to the back, rotate by

```
sum_i x[s_i] B^i,
```

and swap back. Repeat the identity with the new u parities, and undo the
packed source load by the same two swaps and inverse rotation. On the good
set no u digit overflows, so its parity changes by exactly x[s_i]. Each
completed target identity changes only target parities. In particular it
preserves source bits, including during the later unload. The two target
identities therefore compose to the desired simultaneous additions and
restore u,t,b. The complete word has **twelve compact swaps and ten modular
rotations**, including loading and unloading.

This generalizes the earlier/later-source proof in the frozen
[movement source, lines 46-80](../kappa-round6-query-normalizer-20261022/layout-audit/sources/notes/compact-control-movement.tex#L46-L80).
It does not use an offset depending on the binary field while that field
is being rotated: target offsets use u,t, and loads rotate only the back.

## Offset work, bad addresses and exact repair

Packed control generation is charged. Its recipe scans at most e positions,
extracts their bits from O(A)-bit controls, and forms O(A)-bit shifted sums
using ordinary binary arithmetic. It takes a fixed polynomial in A, with a
fixed number of arithmetic work tapes. A repeated pivot uses
`z sum_i B^i` and is not a free broadcast. No growing descriptor is scanned
once per payload bit. The retained record-paid rotation lemma charges
`O(V+M A^C)` for some fixed C, absorbed by R being superpolynomial.

Exclude u/t digits equal to B-1 and require `2B<=g_i<2^(K-1)-2B` in each
target segment initially written `2g_i+a_i`. These tests do not depend on
the selected target parity or any source bit. The ideal addition preserves
them. Complete ranges give

```
delta <= min(1,2n 2^(-G)+8n 2^(G-K)).
```

On good addresses every compact load stays within its digit, the conservative
guard prevents wide-segment carries, and the four-step identity is exact.
On all addresses the actual word S is a bijection, since every swap and
target-independent modular rotation is bijective. Agreement with the ideal
map T off the bad set, and preservation of that set by T, imply preservation
by S. Repair `T S^-1` only on bad records. Inverse offsets are evaluated with
their current inverse controls, including exact cyclic arithmetic on bad
addresses. Stable binary radix repair costs
`O(V+M A^3+delta M A(R+A))`. This is the same proof and full charge as the
retained [movement source, lines 82-158](../kappa-round6-query-normalizer-20261022/layout-audit/sources/notes/compact-control-movement.tex#L82-L158).
For the stated G and eventual `K>=G+4 ceil(log2 p)+10`,
`delta<=5/(128p^3)` and repair costs O(V). All compact fields and physical
field order return. The omitted highest pair costs O(V).

The nG-bit chunk swaps remain paid by the retained arbitrary-width primitive.
The complete cost is

```
O(V((e log p)^tau+1)).
```

It is not O(V). The generic polynomial-time position recipe is a new
semantic extension of the compact-operation alphabet; it is not claimed
as an old metadata operation.

## Gathering selected axes without a transpose

For any fixed polynomial-time permutation recipe on the e selected positions,
write each permutation cycle as `c_j -> c_(j+1)`. The two cycle reversals

```
A(c_j)=c_(-j mod L),       B(c_j)=c_(1-j mod L)
```

are involutions and `B A` is that cycle. Each is a disjoint matching of swaps.
Three parallel additions perform all swaps in one matching. Thus six charged
parallel additions implement the complete selected-bit permutation. The
ordinary unselected chunk bits are retained; no growing matrix transpose
is declared elementary. A periodic fixed-block gather has a fixed formula.
Its cycle leader, length and position can alternatively be computed by at
most polynomially many iterations of that formula, using a fixed number
of O(A)-bit counters. This recipe construction is included in the record-paid
offset work. It requires no variable-size table supplied as a free descriptor.

Any fixed binary basis change on m*ell block coordinates, repeated over the
column blocks, uses a constant number of such selected additions for fixed
m,ell. Its inverse has the same charge. It follows that a fixed blockwise
Clifford lowering recipe may gather all its Fourier axes into one contiguous
selected-axis job, rather than paying one separate Gaussian child per block.

The exact native embedding is important. Local block coordinate `(h,j)`,
with `0<=h<m`, `0<=j<ell`, in block b of an original slot length f, is the
physical selected position

```
rho + (h*f + ell*b + j)*K.
```

Thus adjacent *local* Clifford indices still occupy distinct physical K-bit
chunks. Every blockwise basis change and every gather swaps only these
same-rho positions. No step compresses them into adjacent bits before using
the compact primitive. This embedding, rather than a general overlapping-
window claim, is the witness needed by the native recipe.

## A paid grouped phase job

Partition f selected q-coordinates into r disjoint full blocks of fixed
length ell. Write `P_j` for the translation complementing the q bits in block
j. Within each block, fan out an extreme pivot to all other q bits. Their
parallel composition L is admitted above. Then

```
L (product_j S(P_j)) L^-1 = C on the r pivot bits.
```

After the charged selected-axis gather, the middle operation is **one paid
ordinary Gaussian job of rank r**, with arbitrary coefficient input. This
gives `b(V,r)+O(V((f log p)^tau+1))` under the retained Gaussian job contract.
It does not give f independent phase gates for free. Owned coefficient
streams required by the existing Gaussian provider retain their original
stock/restoration invoice and earn no output credit here.

For commuting involutions A,B, the exact split is

```
S(A)S(B)=S(AB) CZ(A,B),
CZ(A,B)=(I+A+B-AB)/2.
```

On their joint negative eigenspace the interaction contributes -1. The
`GroupedPhase.lean` sector theorem records this debt. A binary split that
discards this interaction does not implement the tensor phase.

## Actual native frame type and all-f residue handling

The canonical inherited frame circuit is
`K.adjoint().then(C_[0,r)).then(K)`, where K includes a quadratic diagonal
phase as well as a binary permutation; see pinned
`clifford_exact.py:120-127`. Since `.then` executes its argument after the
preceding circuit, this is `F=K C_[0,r) K^-1` in ordinary left matrix action.
Its square is
a Hermitian Pauli, generally with both X and Z parts. Define

```
Phi(F)=S(F^2)F = ((1+i)/2)F+((1-i)/2)F^3.
```

It is an involution because F^4=I. It is not necessarily a real matrix in
the physical address basis. The pure-X formula `M=B B^T` alone is therefore
not an admission of its actual relative operator. An exact block recipe
executes K^-1 first, the r*ell coordinate C gates, one C on their combined
Pauli direction, and K last, with K repeated over ell columns. Native warp operators include their
actual diagonal corrections. Every mixed-frame warp must be lowered and
charged if its Fourier rank becomes positive.
This is the finite-block operator definition used by the exact compiler;
runtime does not execute all those coordinate gates and then add an unpriced
S. It lowers the complete relative block operator and executes the one paid
Gaussian job of its resulting rank, with its complete monomial normalizers.

At a shared scalar contact choose either F or Phi(F) consistently for every
operand. A shared invertible linear encoding commutes with the scalar ADD;
`RankGate.lean` proves this local equality and the generic two-edge gauge
telescoping law. All intermediate encodings cancel. Arbitrary helper inputs
remain arbitrary, but their resulting complete relative endpoints must be
lowered independently. Owned zero remains zero under an invertible encoding;
owned clearing still requires the original proven zero endpoint.

No recursive dimension padding is used. Write `f=ell*r+t`, `0<=t<ell`.
Use the chosen new frame on r full blocks and the original frame on t
leftover columns. If a one-block paid relative has exact lowered rank d',
and its original one-column rank is d, the full exact Gaussian width is

```
d' r + d t.
```

Likewise a newly broken warp of one-block rank w' costs `w' r`, and helper
and main targets receive their actual affine widths. Fixed blockwise
monomial normalizers and the charged gather combine these into a single
ordinary Gaussian job. Backward jobs use complex conjugation of the complete
new forward recipe; silently substituting Phi(F^-1) is invalid.

This defines a finite residue-class family of affine-width ordinary jobs,
with no factor-2^t volume expansion at every recursive level. A positive
census would still require a strict whole-job contraction and a concrete
cutoff paying all bounded affine offsets, scalar/route constants, owned
stock and precision. This package does not assume that such a census is
positive. Fixed main/adapter/owned endpoints must retain their actual types.

## Concrete next local palette

The binary choice F/Phi(F) uses only the zero mask and the full active mask.
A finite extension has a direct phase-exact definition. For an active-chart
mask v supported on the first k coordinates of the actual K chart, put

```
P_v=K X_v K^-1,
A_v=S(P_v)F=K C_v C_[0,k) K^-1.
```

All these coordinate C gates commute. Consequently
`A_v^2=K X_(ones_k xor v) K^-1`; A_v is symplectically involutive, although
the complete operator need not be an involution. In its active chart its
Fourier block is `I_k+v v^T`. For even weight v this block squares to the
identity and has rank k. For odd weight it has kernel exactly span(v), with
v nonzero, and rank k-1 by rank-nullity. `ActivePalette.lean` proves the
generic characteristic-two square, projection, exact kernel and nonzero
direction statements. The rank-nullity translation is a written standard
finite-dimensional corollary, not a formalized native operator theorem.

For a unit vector v=e_i the full operator identity is particularly simple:

```
A_(e_i)=K X_i C_[0,k)\{i} K^-1.
```

The Pauli factor is retained, including its conjugated phase. The supplied
`active_palette.py` constructs these literal canonical-chart operators and
compares their complete tableaus and zero-state phases with the independently
cancelled unit recipe. The bounded palette
`{0, first active unit, last active unit, all active}` has at most four
distinct states per scalar component. It is a candidate menu, not an invoice.
It may overlap earlier frame choices; no novelty follows solely from a new
mask label. Even-mask changes with fixed rowspace must also be compared with
the existing symmetric-phase rigidity result before repeating that search.

At ell=1 these are columnwise finite-dimensional Clifford frames. A complete
relative of rank d' repeats on f columns and costs one ordinary Gaussian
job of width d'f, with exact monomial normalizers. There is no residue or
padding complication in that case. Every shared scalar component chooses
one state, every warp is priced with its actual native body, and helpers
keep their complete independent endpoints. This makes the four-state ell=1
palette the smallest concrete next test if the binary weighted price fails.
