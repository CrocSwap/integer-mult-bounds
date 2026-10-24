# Scoped one-parallel-bank ceiling for the source-restored involution

This is a separate read/derive corollary for the actual source-restored F in
PR4935 head `64c9f99693c92fb370096fb43dbc58a085b30e36`. It does not obstruct
the newly constructed physical raw dual or an eventual direct coded consumer.
Credit the parent for the projection/rank and determinant-lemma argument;
this agent independently checked the actual matrix, grades and intervals.

Let J={0,7,20,23,86,93,108,111} and D_J its diagonal selector. Exact source
checks give F²=I, diag(F)=12D_J and F_JJ=12I8. Write G=F−12D_J. The matrix
determinant lemma gives det(G)=det(F)det(I8−12F_JJ)=det(F)(−143)^8≠0;
symmetry of F is not assumed. The checker additionally verifies the two-sided
integer witness

    G(143F−12F D_J F)=(143F−12F D_J F)G=143I.

For the actual X entrance frames U_i, every nonzero off-diagonal F_ij has
Fourier grade2 for U_i U_j*. There are 5,824 such supported pairs, all directly
recomputed from the exact source Clifford library and checked by independent
binary row reduction. The pure diagonal12D_J is monomial. Thus

    pi2(U F U*)=U G U*,

which is invertible. Since F^-1=F, the source-restored forward uncoding
adapter is U F U*, with scalar exitF on the common-full X chart. The raw-dual
adapter has entrance bar(U) F^T bar(U)* and scalar exitF^T; its projected
matrix is likewise invertible. Fixed nonzero scalar rescaling preserves the
same projected-rank argument. No free ordinary implementation of those exit
matrices is asserted.

Here is the exact all-width algebra boundary. Fix a finite-phase one-column
Clifford group Gc on the declared address space and its central scalar subgroup
Z. Impose the actual scalar character z=ζ^f at width f; the resulting twisted
algebra A_f has one basis class per projective Clifford Gc/Z. Let H be the
full admitted monomial-Clifford subgroup and B_f its subgroup algebra. Fourier
grade is invariant under both left and right monomial multiplication, so
projection pi2 onto pure grade2 basis classes is a B_f-bimodule map. Phases
are retained, and no integral-domain or commuting-coefficient premise is used.

The projective algebra faithfully evaluates into columnwise tensor action for
all sufficiently large f. Indeed, choose nonproportional matrix representatives
v_t for the finitely many projective classes. For each t, a product of linear
forms vanishing on each other v_u but not v_t isolates v_t in homogeneous
degree |Gc/Z|−1. Multiply by a linear form nonzero at v_t to obtain an isolating
polynomial at every larger degree. Thus v_t^tensor(f) are linearly independent
at those widths, with their scalar character retained. An exact identity at
all positive widths must therefore hold in A_f at sufficiently large widths,
even with width-dependent owner scalar coefficients. No operator sum is
incorrectly tensor-powered.

Grant arbitrary rectangular B_f-valued owner pre/post controls L,R, zero
scratch, output selection, copies and a free identity bypass B0. A standalone
ONE parallel bank D of pure Gaussian-Clifford channels satisfies

    pi2(L D R+B0)=L pi2(D) R.

If the bank has r grade-two channels, its right-hand side has regular-module
rank at most r dim(A_f). All other pure grades project to zero; each grade-two
channel is a group unit. The required adapter projection has rank 112dim(A_f).
Consequently r≥112. This is the same restricted architecture ceiling even
though the scalar port matrix F is now an involution.

The explicitly UNREALIZED two-call grant 224H17+2H versus two copies of
P={1:2209,2:412,3:510,4:127,5:40} has margin
[150.262158203082210620506138658847,150.262158203082210620506138658848]
at C=.0030217758. Subtracting the necessary 112H2 gives
[−73.269156882594712940928576503039,−73.269156882594712940928576503038];
at C=.0034 it gives
[−80.401921647290247704383966403396,−80.401921647290247704383966403395].
All negative coefficient ranks are ≤5 and all positive ranks ≥7. Therefore
M(t)/5^t strictly increases in t=1−C, and negativity at the lower-C endpoint
excludes this stated bill over the entire interval. All 816 inherited helper
jobs are included exactly once. No productive Gaussian endpoint is supplied
by this price grant, and finite scalar/storage/precision/outer costs cannot
rescue its negative relaxation.

Scope excludes chronological multibank circuits, native absorption or
interleaving, source-prefix access, direct coded consumers, approximate/border
endpoints, nonlinear operations, non-Clifford monomial gates and arbitrary
noncolumnwise address controllers. The actual new raw-dual repair is not
such an uncoding adapter and remains a positive local interface result.
No caller, κ or universal producer ceiling follows.

Reproduce normal/O with `check_ceiling.py`. This is a source-specific finite
matrix/grade/interval verification supporting the written all-width proof,
not a formal proof-kernel certificate. Apache-2.0; substantial OpenAI Codex
assistance; upstream contributor credit is retained in REVIEW.md/SOURCES.json.
