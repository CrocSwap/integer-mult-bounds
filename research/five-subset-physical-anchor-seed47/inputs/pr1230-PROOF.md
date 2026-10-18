# One common frame supports at most 36 signed entries

This is a finite structural theorem in the historical parity-side interface.
It does not establish a physical supplier or a multiplication exponent.

Let V=F2^9 with its standard dot product. Endpoint labels are distinct
weight-five vectors. A single nondegenerate separator U contains the source
labels S; U-perp contains the target labels T. Both sides contain a pair
with dot product one. Each incident residual must have an orthonormal basis.
The integer-normalized signed kernel is

    K(s,t) = Re(i^popcount(s&t)) = [1,0,-1,0][popcount(s&t) mod 4].

The matrix K on S×T must have rational rank one. This is stronger than
cross-orthogonality: the latter makes entries nonzero but need not make signs
factor. A common frame is stronger than independently completing every 2×2
rectangle, the question addressed by PR1173.

**Result.** In this class |S||T|≤36. A 6×6 block attains 36 with twelve legal
incident residuals. Among the explicit dirty-helper wrappers described below,
the maximum saving relative to one signed ADD per entry is twelve ADDs.
The area upper bound holds for both possible separator dimensions, four and
five. The finite enumerations explicitly cover dimension four; transposition
covers dimension five because K is symmetric.

## Reduction to the complete finite census

PR920 supplies the residual criterion: for a nondegenerate binary space X
and norm-one label x in X, the residual X∩x-perp is alternating exactly when
x equals the characteristic w_X, defined by w_X·v=v·v. It then has no
orthonormal basis unless it is zero. A degenerate pair of distinct norm-one
labels forces dimension at least four if both incident residuals are legal.
Applying this on both sides gives 4≤dim U≤5 at h=9. These are inherited
geometric facts, not new classification claims here. Every witness also has
its actual residual bases checked directly.

For dim U=4, select a degenerate source pair a,b from S. Its intersection has
odd size. Since the labels are distinct five-subsets of nine coordinates,
the only possibilities are one and three. Coordinate permutations reduce
them to (31,481) and (31,103), with masks in little-endian bit coordinates.
This reduction preserves dot products, weights, kernel signs and the full
residual interface. It does not claim the anchored counts are counts of
distinct labeled global frames.

The span E=<a,b> has dimension two. U4 containing E corresponds bijectively
to a two-plane in V/E, which has dimension seven. There are exactly
(127×126)/(3×2)=2667 such planes. The primary implementation forms all pairs
of nonzero quotient cosets and deduplicates their three-element plane sets.
The independent implementation constructs all rank-two RREF quotient planes.
Each orbit has 1643 singular and 1024 nondegenerate lifts. For each legal U,
all eligible labels are enumerated in U and U-perp, excluding characteristics.
No coordinate-frame restriction or sampled subspace is imposed.

Every source subset containing a,b is tested. For fixed S, nonzero target
columns belong to one signed rank-one block exactly when they agree up to a
common sign. Thus a maximal T is an entire normalized column class. Reject
classes lacking a degenerate target pair. Taking the entire class cannot
decrease area. It cannot decrease st−2(s+t), since s≥2. This is a complete
maximization, including nonsaturated subblocks. The independent program uses
literal 2×2-minor saturation instead of the primary column-pattern grouping.

The two programs agree on all 2048 nondegenerate-frame maximum records,
including their full endpoint counts and maximizing sizes. Their canonical
record digest is ac3520884ea295130595b20b4703217ed6838ba49dae1e4ca63412371803be7a.
The maximum area is 36; the maximum wrapper saving is twelve. Independently,
AM-GM gives st−2(s+t)≤st−4sqrt(st)≤12 for 4≤st≤36, confirming this saving
bound from the area theorem. The 6×6 witness attains equality. Some frames
have nine eligible targets: a simple six-by-six cardinality argument would
be false. The sign test is essential. Swapping S,T proves the same area and
symmetric scalar saving bounds for U5.

## Explicit common-frame block and complete scalar wrapper

The fixture extends PR1173's actual frame U=<31,481,3,40>. Its characteristic
is 40, and the complement characteristic is 471. Use

    S = [31,55,457,458,481,482], alpha = [1,1,-1,-1,-1,-1]
    T = [47,59,87,151,279,451], beta = [1,1,1,1,1,-1].

Every one of the 36 entries equals alpha_i beta_j. WITNESS.json records an
orthonormal basis for every incoming residual of dimension three and every
outgoing residual of dimension four. The independently chosen canonical
optimum in CENSUS.json is another checked attaining frame.

With immutable sources x_i, dirty accumulating outputs y_j and an arbitrary
dirty helper q, execute:

1. Six signed ADDs: q += sum alpha_i x_i.
2. Six signed ADDs: y_j += beta_j q.
3. Six inverse ADDs in reverse order: q -= sum alpha_i x_i.
4. Six old-value corrections: y_j -= beta_j q.

The final q equals its original value, sources are unchanged, and each
y_j gains sum K(s_i,t_j)x_i. Thus the complete word has 24 signed ADDs,
including restoration and dirty cancellation; the direct entry-by-entry
word has 36. This identity holds over any coefficient ring. The checker
compares all thirteen integer input columns, including dirty outputs and
helper dirt, and checks the literal inverse. Source columns alone miss the
omitted old-value correction, which is retained as a negative control.

## Geometric invoice and limits

For a caller already supplying the source-line frames, target-hyperplane
frames and the helper at U, all 24 incident transfers are nested. Their
residual ranks are twelve of rank three and twelve of rank four, mass 84.
Direct source-line to target-hyperplane transfers have rank seven, mass
36×7=252. No COPY, ERASE or clean-helper assumption appears in this scalar
word. These are conditional incident-edge invoices, not complete supplier
prices. They cannot be substituted into the selected recursive moment.

In particular, if one instead uses the zero-entrance dirty-role convention
in general-clifford-frames.tex, this helper needs a rank-four birth and a
rank-five Fourier tail (total nine), rather than free boundary changes.
Even that favorable local screen is only 84+9=93. It excludes still-unbuilt
caller/source access, exact phase and rank-zero adapters, the inherited
side-matrix factor 1/2, gather/scatter layout, copies needed by a larger DAG,
global restoration, recursive children/whole-owner hosting, precision/tape
and analytic transfer. None of those expenses is asserted to vanish.
The package stops at the finite geometry and integer-normalized macro;
it does not implement or claim that favorable supplier budget.

The selected E8 suppliers use different label units. Global label coverage,
compatible station choices across multiple nodes and actual compiled words
remain open. This local extension neither reopens the rejected unchanged
ParitySide DAG nor removes its common-span obstructions. It does not optimize
arbitrary nonnested transport, mixed weights, higher dimensions, multiple
stations or unrestricted decoders. The finite theorem is supported by a
complete bounded certificate with an explicit coverage argument, not a
formal proof of the full integer-multiplication theorem.
