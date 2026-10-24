# Bounded inspection of the source/flag checker supplement

**PASS for its stated finite scope.** Reviewed check_source_and_flag.py SHA256
`025ba8f3f63fa4f4d7155a32f0f51de210693f6b425b047312d5f232e96fdc5f`
and its saved SOURCE-FLAG-CHECK.json. The packager separately reports exact
normal/optimized replay and receipt equality. This reviewer inspected code
and source contracts without rerunning the checker or source algorithm.

The checker uses standard-library integer/Fraction operations and explicit
RuntimeError checks, with no assertions disabled by optimization and no dynamic
source imports, subprocesses, solver, native emitter or network access. It
authenticates the five retained source files before checking the literal112
owner inventory, zero diagonal,52 nonzeros per row/column, distinct literal q
directions, correct G ROW convention, orthogonality and the exact A polynomial.
This is finite source-structure evidence, not an all-width theorem replay.

Its17-axis flag example is correctly embedded: q=0, U=1..8, W=9..16, w=9.
Q and D3 are upper-right symmetric binary symplectic shears; CZ(q,w) is a
lower-left symmetric shear. Their composition K=D3 CZ D3^-1 is therefore
symplectic and invertible. The code uses column images consistently for these
maps and row matrices consistently for the source G data. Basis-inclusion
tests establish equality of the known full-dimensional Lagrangians here.

The example correctly has CZ in H0 but transported K in Ht, with central X
image e_q+e_w. K preserves L0,Lw,Lqw and fails to preserve Lq; its Q conjugate
is nonmonomial. This is a valid concrete rejection of Ht=H0 and of replacing
the quotient-central condition by R_k e_q=e_q. The small loop over noncentral
U vectors corroborates that particular example's quotient behavior, not the
universal flag lemma for arbitrary K.

The controls test a nonzero A diagonal, duplicated port direction, corrupted
orthogonal source row, untransported-H0 substitution and erased central shift.
No portability or source/control gap was found within this bounded scope.
The file correctly excludes absolute-phase checking, all-width theorem replay,
t0 search, native/compiler execution and supplier admission from its claim.

This supplement may be packaged unchanged with those limits. It does not
replace the written support/separation proof. No original proof/review bytes
were edited. Credit the source author and packager; substantial OpenAI Codex
assistance. Local independent inspection only.
