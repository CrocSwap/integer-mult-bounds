# Exact arbitrary-frame bridges

Prepared for Dugongue with substantial OpenAI Codex assistance. Apache-2.0.

Let U,V be arbitrary subspaces of F₂ⁿ, with the retained source's canonical frame operators C_U and C_V. They need not be nested. Then the operator C_U.adjoint().then(C_V) has exact Fourier rank

    r(U,V)=dim U+dim V−2 dim(U∩V).

It can therefore be implemented by one rank-r recursive Gaussian transform between two explicit monomial adapters, with all absolute phases retained. When r=0, only a monomial adapter is required. The finite exact Clifford lowering constructs and checks these adapters; this is a sufficient realization, not an assumption that arbitrary frame changes are free.

## Proof

Write Pauli exponents as (x,z)∈F₂ⁿ×F₂ⁿ and let L₀={(0,z)} denote the Z Lagrangian. We claim

    C_U(L₀)=L_U={(x,z):x∈U and x+z∈U⊥}.

For the coordinate r-plane E, this follows directly from each retained C gate sending a Z basis generator to the corresponding XZ generator on selected axes and fixing unselected Z generators. For a general basis of U, the canonical frame uses an invertible matrix G with GE=U and the monomial K=D_Q P_G, where Q=I+G⁻ᵀG⁻¹. Its symplectic action is

    (x,z) ↦ (Gx,G⁻ᵀz+QGx).

Consequently the new x coordinate is Gx and the sum of new x and z coordinates is G⁻ᵀ(x+z). This sends L_E precisely to L_U. The canonical-frame conjugation and the fact that K preserves L₀ prove the claim. The special zero and full-frame definitions satisfy the same formula.

Now L_U∩L_V is parametrized independently by x∈U∩V and y=x+z∈(U+V)⊥. Its dimension is

    dim(U∩V)+n−dim(U+V)
    =n−dim U−dim V+2 dim(U∩V).

The Fourier rank of a symplectic operator is the rank of its B block, equivalently n minus the intersection dimension of its image of L₀ with L₀. Each canonical frame is a conjugate of commuting selected-axis C gates, whose symplectic actions are involutions; hence C_U and C_U⁻¹ have the same symplectic action. Applying an invertible canonical-frame action transports the intersection calculation above to the relative operator, in either composition convention. Therefore its rank is exactly r(U,V).

The source's exact Clifford normal form factors any such relative operator into a right monomial, the r-axis Gaussian transform, and a left monomial. Its tableau and exact zero-state vector determine and check the absolute phase. Tensoring with identity spectator coordinates preserves the factorization and its active rank r. Taking f independent digit-column tensor copies gives active rank rf, as required by the retained all-fiber interface.

## Finite check

A separate checker evaluated 1,024 deterministic random pairs among the actual round-three frame registry. The Fourier rank read directly from each composed exact Clifford tableau matched the formula above in every case. The sample result is `RANK-FORMULA-SAMPLES.json`; it corroborates the proof and does not replace it.

This primitive permits nonnested contact proposals in the native model, provided every actual bridge and both its adapters are charged and its endpoint is checked. It does not by itself establish any improved paid invoice or κ. Productive helper credit must use the same actual relative-operator rank; a helper's input remains an arbitrary independent field.

## Attribution

The canonical-frame and exact Clifford implementations are retained repository sources, including Cinna Davis's native/helper interface, the transported warp-frame work, zxv's native framework, and all original compiler notices. This note gives an explicit arbitrary-frame rank proof and its sufficient native realization. No Lean verification or novelty priority for the general Clifford normal form is claimed.
