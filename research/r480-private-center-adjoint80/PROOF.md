# Adjoint erasure and the single-omission identity

This proof concerns the finite scalar macro projection over the rationals.
It does not interpret frame changes, native children or physical memory.
The specific instance has 712 coordinates, including eight arbitrary private centers.

## Reverse-mode rules

Let a column state `x` evolve by a scalar gate `x' = E x`.
For an output functional `lambda`, its value is `lambda^T x'`.
The corresponding input functional is `E^T lambda`.
Pulling a functional backward therefore uses the following rules.

| Gate | Pullback rule |
| --- | --- |
| `x_d <- x_d + q*x_s` | `lambda_s <- lambda_s + q*lambda_d` |
| `x_d <- q*x_d` | `lambda_d <- q*lambda_d` |
| `clear x_d` | `lambda_d <- 0` |
| `x_d <- x_s`, with `s != d` | Add old `lambda_d` to `lambda_s`, then set `lambda_d <- 0` |

COPY is not a swap. It overwrites the old target and preserves the source.
CLEAR and COPY are singular, so their pullbacks cannot assume invertibility.
The table follows by substituting each gate into `lambda^T x'`.

Start with one coordinate functional for each final output.
Apply the table in reverse program order.
The resulting 712 covectors give every entry of the complete transpose matrix.
Exact agreement on the coordinate basis establishes agreement on every rational input.
No clean-input assumption is used for the eight private coordinates.

For the intact forward word, the matrix fixes the 704 persistent coordinates
except `T_i <- T_i + S_i`, for `0 <= i < 112`.
For the intact backward word, it instead uses `S_i <- S_i - T_i`.
All eight private rows and columns equal zero.
Thus every helper retains its arbitrary initial value and every private input erases.
The instance checks these matrices exactly, with two different arithmetic implementations.
The persistent blocks are inverse transposes. The full matrices have rank 704
and nullity eight, so the full private-extended maps are not invertible.

## Rank-one deletion formula

Fix a gate at one site. Let `P` be the prefix before the gate.
Let `S` be the suffix after the gate.
The original matrix is `M = S E P`.
Deleting this gate gives `M' = S P`, so

```text
Delta = M' - M = S (I - E) P.
```

For CLEAR at target `d`, `E = I - e_d e_d^T`.
Consequently,

```text
Delta = (S e_d) (e_d^T P).
```

For COPY from `s` to `d`, with distinct coordinates,
`E = I - e_d e_d^T + e_d e_s^T`. Hence

```text
Delta = (S e_d) ((e_d^T - e_s^T) P).
```

Both formulas give `Delta = u v^T`.
The response `u` is a unit target state propagated forward through the suffix.
The sensitivity `v^T` is the stated functional pulled backward through the prefix.
An exact outer product has rank zero when either factor is zero.
Otherwise it has rank one over the rationals.

The primary checker computes every mutant's complete matrix separately.
It compares its difference from the intact matrix with this outer product.
The independent forward checker recomputes all mutant matrices with integer-dyadic rows.
It compares the same factors and every recorded witness.
The rank conclusion therefore uses exact equalities, not numerical rank thresholds.

## Detection and concrete scope

An omission is invisible on ordinary inputs precisely when every persistent
input column of `Delta` is zero. Private output rows remain part of this comparison.
The certificate contains eight such nonzero defects in the backward word.
Their sensitivities are exactly `e_Ck^T`, one for each private center.

For those eight sites, `Delta x = u_k x_Ck`.
All inputs with `x_Ck = 0` give the same result as the intact word.
The private unit input gives `Delta e_Ck = u_k != 0`.
Every private output remains zero, while 103–111 persistent outputs differ.
The full exact vectors appear in the certificate.

The 24 other nonzero defects affect an ordinary input column.
Each receives a unit input and an explicitly executed nonzero output difference.
The eight forward initial clears have zero response because a later COPY overwrites
the center before its contents can affect any final output.
This establishes scalar redundancy only.

The classification covers exactly 40 fixed sites in two frozen programs.
It makes no claim about multiple omissions, other gates, physical fault rates,
caller initialization guarantees or acceptance by a complete production verifier.
No discrepancy was found in the intact scalar word.
The rank-one formula is a finite linear-algebra identity, not a new multiplication theorem.
All inherited realization, hosting, precision/tape and analytic obligations remain.

Credit Sagar Thakrar's PR745 for the historical adjoint/private-input audit method.
New R480 evidence and implementation: @Scratch-net with substantial OpenAI Codex assistance.
Apache-2.0. No independent human review is claimed.
