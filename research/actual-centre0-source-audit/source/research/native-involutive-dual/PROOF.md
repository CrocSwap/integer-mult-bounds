# Sufficient construction and its scope

## 1. Fixed source and inherited forward code

The decompressed source SHA-256 is cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd. It has 112 X fields, 112 Y fields and 408 independent helpers. The canonical source has X exits in the common full frame T and Y exits in hyperplanes V_i. The backward convention uses entrywise-conjugated frames. Neither an adjoint nor an unchanged forward frame may silently replace that convention.

Retain the exact 8 by 112 matrix R, K = R^T/4, and the eight supported rows S = {0,7,20,23,86,93,108,111}. Let P equal K on S and vanish elsewhere. The source facts are RK = 14 I and RP = I. Put U = K - 12 P, A = I - KR, and F = I - UR = A + 12 PR. Then RU = 2 I and F² = I. All coefficients are dyadic. The forward F-shear and its eight supported repairs are predecessor results, freshly replayed here, not a new involution theorem.

The helper-clean backward producer from #4929 has normalized endpoint X -> X - A^T Y, with Y and every helper unchanged. Its physical outer frames are the conjugates specified by the source. The backward source is an inherited all-width premise with source-bound finite corroboration.

## 2. Actual backward repair

For each i in S, initialize the owned scratch C at the conjugate hyperplane frame bar(V_i), copy the current Y_i into C, apply the exact transport bar(T) bar(V_i)^(-1), and add

    -(F_ij - A_ij) C

to every X_j with a nonzero coefficient. Finally clear C. X exits all share bar(T), so every ADD uses a common physical frame. The compiled transport has Gaussian rank 1, checked with its absolute phase. The scratch is owned; no helper or other arbitrary input is cleared, overwritten, or credited as an extra productive field.

In normalized coordinates this adds -12 (PR)^T Y to X and leaves Y unchanged. The result is therefore X -> X - F^T Y. Each selected Y_i is copied before its scratch is erased, and the original Y_i never changes. All 408 helpers retain their inherited autonomous endpoints. The repair tail has 8 owned COPY operations, 424 scalar ADDs, 16 owned CLEARs and 8 rank 1 calls, for 456 literal events. Ordinary scalar, copy, routing and erasure work is retained. The full literal profile is 2,209 rank 1, 412 rank 2, 510 rank 3, 127 rank 4 and 40 rank 5 calls.

This is the normalized raw inverse transpose of the forward shear. For unitary outer frames, (T S U^(-1))^(-T) = bar(T) S^(-T) bar(U)^(-1), which explains the conjugate-frame convention. The repair is constructed at the actual backward exit; it is not obtained by prefixing the forward repair with mismatched frames. F is not symmetric, so the backward coefficient must be F^T.

The separate sparse Gaussian-integer evaluator checks all 512 basis columns of each of the eight raising circuits, including global phase. Target frame circuits remain bound by the main constructor and frozen equality check. This is a separately implemented finite evaluator, not an independent human or proof-kernel audit.

## 3. Dyadic code implementation

For F on a common chart, compute t = R x in eight owned temporaries, then x <- x - U t. For F^T compute t = U^T x and then x <- x - R^T t. Each factor has 448 nonzero entries, so either program uses 896 ADDs and eight initialized/cleared temporaries. The program reads all original x values before modifying x. RU = 2 I proves both transformations are their own inverses. Thus their inverses use the same program, with no odd division.

Let K_i be the retained real signed-permutation normalizers of #4933. Define C = diag(K_i)^(-1) F diag(K_i). Its transpose is obtained by substituting F^T because K_i is real orthogonal. The checker replays all 112 normalizers and their incoming/outgoing factors with exact phases, independently of a symmetry assumption about F. Both C and C^T commute with the full Gaussian DQ, since every K_i does and scalar owner mixing commutes with its identical diagonal action. Both are involutions.

At a forward stage use C_s from F; at a backward stage use C_s from F^T. The phase-correct physical forms are

    diag(D_s,D_s) L(C_s Q^(-1))       (forward),
    diag(D_s,D_s) U(-Q C_s)          (backward).

The literal monomial wrappers are retained in NORMALIZERS.json and checked again against the source frames. Each local recoding applies the K_i maps, its eight-mode scalar program, and their inverses. This costs 224 monomial passes as well as the scalar work. Backward raw-dual conversion uses the inherited X-only Q² convention; no Y-only substitution is made.

## 4. Complete typed caller, with unresolved terminal recovery

Apply the universal local and paid-IDLE gauge identities and the noncommuting controller identity of #4933 to these stage codes. They require [C_s,D_s Q] = 0 and commutation with other stages' fresh D_t; they do not require [C_s,Q] = 0 or commutation between different codes. For an involution the backward inverse code is the same code, so all 194 inserted evaluations and the 97 optional positive-half output inverses are dyadic. Backward stages use the transpose code, not an incorrectly symmetric F.

The retained scalar bridges, signed swaps, boundaries, IDLEs and thin queries are unchanged in the recipe. The exact outputs are Q^(-1) B_i D_i on 16 negative banks and B_i D_i Q on 16 positive banks, with every ordered B_i emitted. Applying the emitted inverse word on positive banks gives ordinary Gaussian jobs there. It does not decode negative banks, since B_i need not commute with Q. The 3,584 main inputs and 7,344 helper inputs remain independent. No helper is credited twice.

The full recursive difference from the original caller is -144 rank 8 +144 rank 1. Compared with #4933's rational coded caller this deliberately pays 144 additional rank 1 requests to obtain involutive dyadic codes. It is not claimed to dominate that caller's paid moment, or to improve κ. The complete compiler cannot count the remaining negative coded banks as Gaussian targets without a new theorem or a paid decoder.

## 5. Width, precision and limitations

For each positive digit-column multiplicity, lift every native frame and monomial circuit columnwise. A scalar phase i^gamma lifts as i^(f gamma); it is not held fixed when f changes. The one-column operator identities then tensor by composition. The owner code is implemented by its scalar program at that width; no tensor power of a sum or of the entire owner matrix is assumed. The inherited free-group scalar/warp identity evaluates at the consistent lifted operators and preserves arbitrary helpers.

All new coefficients are fixed dyadic rationals, and all frame maps are unitary. In the maximum of fiber Euclidean norms, an ADD with coefficient a has norm at most 1+|a|. Multiplying these factors gives a finite bound for every rounding suffix of each fixed recipe; COPY and CLEAR obey their owned-field contracts. This supplies a finite precision propagation bound, not a fully implemented fixed-tape rounding protocol, compiler reserve or outer recovery theorem. The exact backward prefix bound 258 is not substituted for a suffix bound.

The evidence is a source-bound finite exact construction plus the written all-width assembly under retained native assumptions. No full multiplier, independent human review, Lean theorem or selected-frontier update follows.
