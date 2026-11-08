# Independent nilpotent forward-action review

Prepared for **@CubeJerry** with separate source-aware OpenAI AI verification.
This is independent source/page and arithmetic reasoning, not human or
proof-assistant review. The algebraic lift and retained solver are inherited;
the reviewed contribution is their concrete fixed-tape forward composition.
**No new κ or discharged global multiplication assumption is asserted.**

## 1. Exact page commutation

Let F be a real rational n-by-n matrix, n≥1. Put target t_i=2i and source
s_j=2j+1, and define N[t_i,s_j]=−F_ij, with all other entries zero. The two
sets are disjoint. Every product of two entrywise-masked pieces of N vanishes.
Split N into strictly lower, diagonal and strictly upper block pieces
N_L,N_D,N_U. Assume the **exact source before rounding** satisfies
`|t_i−s_j|≤b` for nonzero F_ij, with dyadic block b. Then

\[
 L=I+N_L,\quad U=I+N_D+N_U,\quad LU=I+N.
\]

The factors have the adjacent-block support admitted by the retained
preparer. Lower inverse diagonal pages are I; upper ones are I−N_D.
This holds for singular, nonsymmetric or signed F: F is never inverted.

Let τ be truncation toward zero to h=2^−P and Fhat=τ(F). An N entry never lies
on the scalar diagonal, since an even target differs from an odd source.
The inverse-page formula is therefore affine on disjoint entries: exact scalar
ones stay ones, and each other nonzero coefficient is a signed F_ij. The
identities `τ(−x)=−τ(x)` and `τ(τ(x))=τ(x)` prove that pre-rounding F before
exact factor serialization produces **identical four rounded page banks**
to exact F followed by the preparer's rounding.

Identity padding adds no coupling. Simultaneously reversing rows and columns
is a permutation, commutes with τ, and preserves disjoint support even if it
exchanges parity labels. Thus the statement includes the retained **padded
upper reversal**, coupling banks, incomplete blocks and exact signed bits,
provided the common scalar width suffices.

Exact support must be checked first: a tiny off-band entry could round away
and make only the shortened path admissible. The producer rejects this case.
Floor rounding on negative coefficients would also break the equality.

## 2. Independent no-feedback semantics

Lift input x by y[t_i]=0 and y[s_i]=x_i. Every source row remains bit-exact:
coupling rows there vanish and diagonal rows are identity. A rounded target
value never enters any subsequent coupling source.

Partition row i's Fhat dot sum by whether its source block is lower than,
higher than, or equal to the target block. Call the three sums a_i,c_i,d_i.
The projected target is exactly

\[
 \tau\bigl(\tau(\tau(a_i)+c_i)+d_i\bigr).                 \tag{1}
\]

Absent updates truncate an already-grid value and do nothing. Equation(1)
is the independent oracle: **three disjoint complete dot sums**, rather than
a second implementation copied from the author's block-solver recurrence.

Let each logical complex input satisfy `|Re x_j|+|Im x_j|≤R`. Its components
are supplied as separate real columns; an unpaired final real column has
imaginary part zero. If s_i counts the nonzero exact F coefficients in row i,
source quantization contributes at most s_i R h. Three effective roundings
contribute at most 3h to each real component. Consequently

\[
 |\Re(\widehat{Fx}-Fx)_i|+|\Im(\widehat{Fx}-Fx)_i|
       \le (s_iR+6)2^{-P}.                                \tag{2}
\]

No number of blocks or inverse norm multiplies this bound. The exact target
is the original F product, not Fhat alone or F inverse. A separate finite
three-block example gives staged numerator 0 whereas one completed-dot
rounding gives 2, so the rounding semantics cannot be interchanged.

## 3. Range

Set ρ=||F||∞. Inward coefficient quantization cannot increase absolute entry
values. At every partial target stage, each coefficient has been used at most
once. Triangle inequality and the magnitude-decreasing property of truncation
bound each target state and completed target residual by ρR in component-l1
norm; source states stay bounded by R. No accumulated-rounding allowance is
needed for this **range** argument.

A common scalar carrier must cover `max(1,R,ρR,max_ij |Fhat_ij|)` strictly
below its positive signed limit. If this maximum is C≥1, the conservative
choice `w=P+2+ceil(log2 C)` suffices. Descriptor widths are separate. Exact
matrix returns still use `2w+log2 b+2` bits and SevenProduct's independently
proved internal U/V guards. The scalar-state bound cannot replace them.

## 4. Complete ceilings and retained history

Write c for the number of **real columns**, distinct from the radius R. Let

\[
 K_0=\lceil n/b\rceil,\quad K=\lceil2n/b\rceil,
 J=\lceil c/b\rceil.
\]

The input and projected output each contain J K_0 b² scalar words in the
retained batch-major ABI, including row and inactive-column padding. The
interleaved input and child output each contain J K b² words. Every child
batch uses K diagonal and K−1 coupling products in each of its two passes.
Thus the exact matrix-call count is

\[
 Q_b=2(2K-1)J,                                            \tag{3}
\]

with exactly `Q_b 7^log2 b` scalar leaves. No n/b or c/b approximation is
substituted for these ceilings. b=1 and partial rows/columns remain covered.
The four page banks themselves contain `2(2K−1)b²` scalar words.

The parent fills its entire interleaved stream, calls the retained child once
on all batches, then projects. Its live/backing space must therefore include
the **whole** J K b²w-bit interleaved input and child protected return, plus
the whole J K_0 b²w-bit parent output. This is not a per-batch O(nb w) bound
independent of c. Borrowed input/pages and preparation storage are additional.

Parent interleaving/projection scans and restoration are linear in these
stream extents, with encoded local counters charged. The unchanged child
receives the global column count c: its padding validation copies/compares
encoded column offsets, so generic accounting must retain their log c work
or an explicit caller premise absorbing it. B7's local-column-only invoice
does not transfer automatically to this different single-child interface.

Across repeated calls, sum the maximum visited extent of **each fixed role**
over its entire history, including erased parent buffers and inactive
arithmetic descendants. Source cache/rational preparation height and page
serialization stay in the separately paid setup bill. Clearing does not
deallocate historical tape backing.

## 5. Independent original source and completed finite review

For the current `Reference(61,3,2,1,3,32)`, the source checker reads **broad**
entries of the full original `[16,20)` window Q and inverts Q by pivoted
triangular elimination/back-substitution. Both inverse identities are checked.
It obtains F by inverting `(Q^-1)_{J,J}` for J=(0,3), independently of the
producer's A-inverse Schur calculation. Replacing broad Q with narrow Q gives
a different matrix and is explicitly distinguished. This is a finite exact
rational Reference claim, not an arbitrary-cap or ideal-Gaussian statement.

The independent observer matches actual physical packed outputs, zero
padding, hashes, matrix counts and scalar counts for all three retained runs:

| Case | Shape / grid | Matrix products | Scalar leaves | Original complex-l1 error |
|---|---|---:|---:|---:|
| Actual broad Schur | n=2, c=3, b=4, P=20, w=28 | 2 | 98 | approximately 1.08581024e−6 |
| Signed nongrid singular | n=3, c=3, b=4, P=8, w=16 | 6 | 294 | 1/128 |
| Same-owner short zero | n=1, c=1, b=1, P=4, w=8 | 6 | 6 | 0 |

The signed source is one third of the three-vertex path Laplacian. Its exact
rational rank is two. At the **chosen P=8**, truncation gives 85/256 times the
integer Laplacian and still has rank two; a nonzero two-by-two minor and its
constant nullvector certify this. This is not a general preservation claim:
at P=7 the rounded matrix has nonzero determinant and rank three. The primitive
needs neither exact nor rounded F to be invertible.

Separate finite controls distinguish negative floor rounding, the wrong
lift sign, nonzero target initialization, an exact tiny off-band entry that
would disappear on the grid, and one-shot instead of three-stage rounding.
These are external oracle controls; the physical fixture separately executes
alias, padding, pending-return and after-child truncation rejection controls.
All 2,788 owned roles are erased after the actual physical sequence, including
the larger-to-smaller reuse. This is not an independent implementation of
the scalar multiplier.

Reviewed source hashes:

* `action.py`: `c10d2daa72446d02326bf1f368f10fd1e6bb27c60477ccc16a288d1fb3d59688`.
* `pages.py`: `80d53c429af883507f817ec467f09de1a57ede342e244afbf83b753b31196a2c`.
* Independent oracle: `77b926bfdabcaac64516b13e50842958cc6db17f4a8ceae9b6879a9131548334`.

The package's final paper retains global-r buffers, global column-control
cost, full ceilings and separately paid source preparation. No blocking
mathematical or interface discrepancy remains in these reviewed versions.
