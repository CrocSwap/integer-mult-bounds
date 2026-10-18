# Exact eight-stream boundary estimate

This is a sufficient norm theorem for the actual nine-call, nine-bridge controller. The current-source finite premises are checked in `CURRENT-RESULT.json`; the mathematical argument is given here. The release retains payload 2048. Neither this estimate nor the separate mixed-norm estimate changes the paid child profile or κ by itself.

## Statement and retained interfaces

Group each replica's 896 live physical families into eight streams of 112 families. Let N_a be a norm or seminorm on family a that is preserved by the actual family-local completed helper endpoints and frame charts. For stream j set z_j = (Σ_port N_(j,port)^2)^(1/2).

Assume the exact current native interfaces: a forward call has the unit-coefficient Y shear from X, its dual has the negative unit-coefficient X shear from Y, and no helper has a residual response into either data stream. Entry and exit charts are isometries for N_a. Distinct logical roles occupy distinct physical families in a complete invocation. Private work is cleared before use and returned to zero before reuse. The bridges and terminal corrections are the literal source routes.

Then, at every completed boundary of the actual source recipe,

    ||z(prefix)||₂ ≤ 10 ||z(input)||₂.

Arbitrary other replicas may interleave their calls. Arbitrary dirty live inputs and correlations are permitted. The conditions are sufficient interfaces, not an assumed unknown gadget: exact current endpoints, native phase recipes, static charts and family disjointness are source-bound in the accompanying classifier and retained full admission.

## Literal nonnegative majorant

A forward call on pair k gives z_(2k+1)' ≤ z_(2k+1) + z_(2k), leaving the other stream bounds unchanged. For the dual call, exchange the two indices. A signed bridge from pair s to pair t gives both bounds z_(2t+i)' ≤ z_(2t+i) + z_(2s+i), for i = 0, 1. Each follows first from the family triangle inequality, then from the Euclidean triangle inequality over ports. We discard signs only in this upper bound.

A helper borrowed from another replica undergoes a family-local completed isometry. It preserves N_a and hence the stream norm of its physical owner. Complete helper endpoints have no cross-family response, and the caller's active data families are disjoint from all its helpers. Thus omitted interleaved calls preserve the eight stream norms of the replica being considered.

Apply the updates in the source order. The final nonnegative product before the terminal signed exchanges is

```
P = [[2,1,2,0,0,0,0,0],
     [3,2,1,2,0,0,0,0],
     [2,1,3,1,2,0,0,0],
     [3,2,2,4,1,2,0,0],
     [0,0,1,1,3,1,2,0],
     [0,0,1,2,2,4,1,2],
     [0,0,0,0,1,1,3,1],
     [0,0,0,0,1,2,2,4]].
```

Every update adds nonnegative rows, so every earlier majorant P_j satisfies P_j ≤ P entrywise. The terminal signed exchanges only permute stream norms and preserve their Euclidean norm.

## Exact integer Schur certificate

Use positive integer vectors

```
u = [57,95,108,175,91,142,56,85],
v = [124,80,121,147,119,133,76,78].
10u - Pv    = [0,3,4,3,0,3,2,1],
10v - Pᵀu  = [100,95,94,97,101,95,98,100].
```

For each nonnegative z, weighted Cauchy–Schwarz gives

    (Σ_j P_ij z_j)²
      ≤ (Σ_j P_ij v_j)(Σ_j P_ij z_j² / v_j)
      ≤ 10 u_i Σ_j P_ij z_j² / v_j.

Summing in i and using Pᵀu ≤ 10v gives ||Pz||₂² ≤ 100 ||z||₂². For a general scalar vector, use |Px| ≤ P|x|. For every source prefix and nonnegative z, P_j z ≤ Pz, so the same bound holds. This proves the stated factor 10, which is less than 16 and therefore costs four whole amplification bits.

## Two legitimate applications

The Hilbert norm on all cover-indexed coordinates is one valid choice of N_a under ordinary family-local unitarity. That choice requires a full ambient-space conversion at input and does not justify payload 256.

`MIXED-FIBRE-PROOF.md` proves the stronger source-specific choice

    N_a = max_g ||f_(a,g)||₂,

where the inner norm is on the selected-bit address space and g is a separate cover label. Its validity needs the actual fibre-monomial operator classification, not generic unitarity. The current classifier binds all operators, exact endpoints and 1,365,984 owner roles, giving 121 actual magnitude bits or 179 bits with the retained local reserve. Denominator, total-mass, C0 and complete admission guards remain separate and unchanged.

## Sources and scope

The Schur test and norm inequalities are classical; the local tool selection comes from Pure Mathematics Atlas D031–D040. The specific source controller, completed endpoint and physical-owner interfaces come from the credited tensor-block lineage, including PR 471, PR 508, PR 537 and PR 2742. Current native supplier provenance includes PR 2802, Jeremy Kothe's PR 2833 dirt-entry rewrite, and the credited PR 2839 and PR 2848 derivatives. The endpoint replay is an unchanged excerpt from the earlier tensor-block certificate; its complete original source hash is recorded in `endpoint_contract.py`.

This is informal mathematics plus exact finite computation. No Lean process was used for this metric result, no new primitive was supplied, and no claim of global novelty or independent unconditional integer multiplication theorem is made.
