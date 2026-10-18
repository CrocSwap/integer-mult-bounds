# Finite inverse and cold-dirt syndrome substitution

The two OpenAI sources are listed with exact source hashes in OPENAI-SOURCES.json. They were inspected as mathematical sources. No Lean execution or new Lean certificate is claimed.

## 1. Finite version-DAG expansion

Let v be the vector of all assigned register versions in a finite linear straight-line program, ordered chronologically. Every version has an equation using earlier versions and initial registers x. Thus v = N v + B x with N strictly triangular. If there are n versions then N^n = 0, and

v = (I + N + ... + N^(n-1)) B x.

Multiplying by I-N proves this identity; the two products telescope to I-N^n = I. Conversely these equations have a unique solution, by forward substitution. This remains true when mutable physical registers are reused: distinct versions, rather than register names, are the vertices. Every scalar coefficient remains exact.

This is the constructive specialization of OAI.OddKaplansky.FiniteMatrixInverse.series_mul and inverse_formula in Algebra/OddKaplansky/FiniteInverse.lean. We use the identity to derive actual register functionals at a chosen cut. It does not itself permit moving a gate or changing its frame.

## 2. Exact syndrome factorization

Let S: X -> Z be a linear map over a field and f: X -> K a linear functional. Then the following are equivalent:

- f vanishes on ker S;
- there is a functional a on Z with f = a S.

For sufficiency of the first condition, define a on im S by a(Sx)=f(x). This is well defined because two preimages differ by ker S. Extend a from a basis of im S to a basis of Z. Necessity follows by evaluation on ker S. Finite Gaussian elimination constructs the extension and checks the complete identity.

The relevant OpenAI source is Algebra/AuslanderReiten/Duality/LinearHomologyDuality.lean, particularly dualCyclesToDualHomology_kernel and its use of LinearMap.range_dualMap_eq_dualAnnihilator_ker. The present finite matrix statement is proved above independently; the larger homology theorem is not assumed as a circuit compiler.

## 3. Sufficient circuit replacement theorem

Partition initial coordinates into protected coordinates P and cold helper dirt D. Cold helpers have entrance frame zero. At a program cut let f be the current source value and g_j other available register values. Suppose exact version expansion proves

f - sum_j a_j g_j = q(D),

where q is an explicitly known linear functional of cold initial dirt only. Replace a background shear t += c f by the sequence t += c a_j g_j. The destination is excluded from all g_j. Every replacement coefficient is admitted by the native dyadic primitive contract, and its actual register-frame chains must be legal.

For every initial vector with D=0 the programs agree at this cut and therefore at every later point. Their full output difference is a linear function of D only. In particular the data map, action on initial targets, and responses to every warm helper are identical. This argument applies to any number of subsequent target deliveries.

Assume, as in the emitted program, that the background subsystem never reads target registers, that all changed background operations are invertible elementary gates, and that cleanup is regenerated as their literal reverse inverse. Background registers then return to their arbitrary initial values. Write the target action of the main program as A y + B x + C D after separating the protected coordinates. Its fixed initial target preconditioner is L=A^-1. Insert the explicit frame-zero target compensation -L C D after that preconditioner. Then the final target map is y+B x, with all cold dirt canceled. This compensation is sufficient only after checking its coefficients and that every referenced helper is indeed cold. The independent native auditor computes C from the entire changed main program; it does not trust a supplied compensation table.

The theorem has no free storage or routing assumption. The replacement gate sequence, changed cleanup, compensations, frame edges, exact Clifford phases, wrappers, full owner program and finite toll are separately charged by the enclosing verifier.

## Concrete application

On the pinned static44 plus PR534 frame-lift word, immediately before A[33], exact rational version expansion proves

value(z523) + value(z512) = initial(z512).

Register 512 is cold. The 324 protected columns are 112 original data columns and 212 warm helper columns. Therefore the operation z513 -= z523 at frame [480] can be replaced by z513 += z512 at the same frame. The difference is exactly one known cold initial coordinate, not an approximate or clean-only equality.

The frozen constructor checks this exact identity and all frame chains. Regenerated compensation has 9,756 additions instead of 9,760. Both oriented emitted programs have 22,107 events instead of 22,111. All 728 formal columns pass in both orientations, including arbitrary dirty helpers; 11 independent local mutation controls are rejected. All 2,929 directed phase edges and 23 residual adapter recipes are checked. The paid child profile is unchanged by this substitution, so it contributes a scalar-program simplification, not a new paid-rank saving.

## Positive paid-rank composition and attribution

The numerical paid-rank improvement in this lane comes from composing the previously proved static44 response presentation with PR534's supplied frame assignment. Matching unchanged scalar operations, the constructor transports desired frames and clips each lift to the exact common successor frame while processing events in reverse dependency order. Each chosen frame contains the old frame and lies below every next use. The existing coalescing realization therefore applies gate by gate; all register chains stay nested.

There are 477 changed frames. The local profile changes from

{1:2204, 2:728, 3:184, 4:280, 5:56, 6:56, 8:8}

to

{1:2284, 2:456, 3:488, 4:168, 5:56, 6:56, 8:8}.

The exact delta is 80 e1 - 272 e2 + 304 e3 - 112 e4. Rank mass and ordered helper widths remain unchanged. Its entropy gain is approximately 3.802467258994966 per invocation; the enclosing package uses exact moment bounds, not this approximation, for its final claim. PR534 supplies the new frame assignment, PR535 supplies the post-center rank-four construction, and the retained PR531/PR484 code supplies transport, response compilation and native audits. Earlier attribution and licenses are preserved in static44/NOTICE-upstream.md and the shared vendor tree.

The OpenAI-inspired syndrome rewrite is composed after these frame lifts. We do not attribute PR534's numerical gain to the two OpenAI lemmas.
