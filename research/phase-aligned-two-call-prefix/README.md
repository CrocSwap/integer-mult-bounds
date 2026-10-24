# A target-compatible phase repair of the two-image block-3 prefix

This package gives a necessary-condition obstruction for one proposed beginning of a five-array, fourteen-call unit, and an explicit phase repair that removes that obstruction. It does **not** give a completed unit or a new multiplication exponent.

The starting construction is [lee-phys's PR #4688](https://github.com/CrocSwap/integer-mult-bounds/pull/4688), frozen at `264c4b3cb13c82d171de352ecf60486dfb8d2bd4`. That work proves that its two-call prefix is invertible at every digit width and gains the full 80 per call in eight block-3 hook cuts. We retain its exact rank engine unchanged, with its complete calibration and controls. Jacob Sussman's [PR #4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628), head `ee4fd87f064017c23e5a86fc1dcfe0a5237caed3`, supplies the engine model and hook lower bound. Neither predecessor claimed that hook equality itself guaranteed a completion.

## The missing target-alignment condition

Let `𝓥=C^8`, with addresses `x=x0+2*x1+4*x2`. Write

- `C_j = ((1+i)/2) I + ((1-i)/2) X_j`, where `X_j` flips bit `j`;
- `C=C_0` and `K=C_2 C_1 C_0`;
- `U`: CNOT from bit 0 to bit 2;
- `V`: swap bits 0 and 1.

Every letter acts by its tensor power at digit width `f`; a sum is implemented by mixing registers **after** the individual tensor powers.

At width five, use `H=𝓥 tensor exterior^4(𝓥)`, of dimension 560, and the eight coordinate subspaces `N_b` of #4688. If `q_b:H->H/N_b`, the target has rank 224 and any one paid rank-one call adds at most 80 quotient rows. The two prefixes are

```
F_old,f = C_f (U_f + 2 V_f) C_f,
F_new,f = C_f (P_f + 2 Q_f) C_f,
S e_x   = i^popcount(x) e_x,
P       = S U S,
Q       = S V S.
```

All factors in `P,Q` are admitted free letters. `S` is the product of the three one-coordinate S phases. Both prefixes use exactly two paid rank-one calls and one zero scratch register, with the same copy/mix/erase schedule as #4688 (replace its `U,V` branches by `P,Q`, and restore the retained first output using `Q^{-1}`). The second prefix contains genuine phase letters, not just Pauli signs.

The exact ranks are:

| Cuts `b` | `rank(q F_old)` | `rank([q K; q F_old])` | `rank(q F_new)` | `rank([q K; q F_new])` |
|---|---:|---:|---:|---:|
| 3, 6, 7 | 160 | **280** | 160 | **224** |
| 2, 8, 9, 12, 13 | 160 | 224 | 160 | 224 |

All restrictions have domain `N_b`. These are ranks over `Q(i)`, calculated by exact Gaussian integer elimination. As in the predecessor, the implementation replaces each `C` by `I-iX` to remove a nonzero scalar. The two branches have equal paid-word length, so their common scalar cancels consistently in every pencil; independent nonzero scaling of target rows also preserves every joint rank. The second column of joint ranks is the extra test; measuring only the rank of the prefix does not detect the first prefix's misalignment.

### Why the original literal beginning needs at least fifteen calls

Fix the target rowspace `T` on all five independent inputs, and let `E` be the rowspace of the current stacked quotient observations. Define the remaining target deficit

```
d_T(E) = dim(T+E) - dim(E).
```

A free operation sends `E` into a subspace of itself, so it cannot decrease this deficit. For a paid call, retain the previous quotient rows conceptually: modulo those rows, at most `rank(q C|N)=80` new independent rows can appear. Consequently a paid call decreases `d_T` by at most 80. This argument permits arbitrary scratch, singular mixing and erasure.

Suppose the **first two paid calls** are exactly the original #4688 prefix on one fresh independent input, and the other four inputs have not received paid work. For cut 3, the current rowspace has rank 160 and its union with the five target rowspaces has rank `280+4*224=1176`. Thus the deficit is **1016**, exceeding the capacity `12*80=960` of the twelve remaining calls. At least thirteen further calls are needed, for at least fifteen total. Keeping the first output `C_f y` does not help: #4688 already certifies `rank([q C; q F_old])=rank(q F_old)=160`.

The same calculation for `W` fresh inputs gives the total lower bound `ceil((224*W+56)/80)` for this literal beginning. For example, six inputs would need at least eighteen calls, so it cannot begin a six-in-seventeen unit either.

This is not an obstruction to an arbitrarily pre-encoded or later occurrence of the same word, nor a lower bound excluding five in fourteen generally. It is a statement about this literal two-call beginning on one fresh input. The original prefix's invertibility and full local gains remain valid.

For the repaired prefix, the corresponding deficit is `64+4*224=960`. It passes this necessary test exactly. This equality does not supply a continuation.

## An exact all-width inverse

Both `U,V` are involutions. The relative monomial is

```
R=P^{-1}Q = S^{-1} U^{-1} V S,
R^4=I,
(I+2R)(I-2R+4R^2-8R^3)=-15I.
```

The same identity holds for `R_f=R^{tensor f}` at every positive `f`. Since `P_f+2Q_f=P_f(I+2R_f)`, the free middle operator is invertible with a fixed rational inverse. The two outside calls are invertible too. Thus clearing the retained first output loses no input information. No inverse has to be executed by the forward prefix.

There is also no width-dependent conditioning loss: all outside factors are unitary and the eigenvalues of `R_f` are fourth roots of unity. The singular values of the prefix therefore belong to `{1,sqrt(5),3}`, with both extremes present for every positive width. Its Euclidean condition number is exactly 3. The original prefix has this same property; it is not a unique benefit of the repair and is not a full outer precision theorem.

## The natural higher-width hook tests also pass

The result is stronger than a width-five numerical coincidence. Put

```
A=C P C,  B=C Q C,
A5=rho(A), B5=rho(B), K5=rho(K),
rho(g)=g tensor exterior^4(g).
```

The checker proves, separately for each of the eight cuts:

1. `rank([q K5; q A5])=rank([q K5; q B5])=224`. Equivalently, each branch separately annihilates `ker(q K5)` after applying `q`.
2. All four pencil matrices `q(A5+2 lambda B5)|N`, for `lambda=1,-1,i,-i`, have rank **160**.

For `r` additional digit columns, use the invariant space `H tensor 𝓥^{tensor r}` and the kept subspace `N_b tensor 𝓥^{tensor r}`. The relative single-column matrix `A^{-1}B=C^{-1}RC` has fourth power one and eigenvalue multiplicities `4,2,1,1`. Multiplying by an invertible matrix in the additional columns reduces the quotient prefix to the direct sum of the four pencil evaluations, with the multiplicities of `(A^{-1}B)^{tensor r}`. Its rank is therefore exactly

```
160 * 8^r.
```

The branchwise kernel inclusions tensor with the additional columns, so the joint target-prefix rank is exactly `224*8^r`. This proves zero alignment defect and two maximal call gains for **all these lifted cuts**, at every `r>=0`. In particular the width-six ranks are 1280 for the prefix and 1792 for the target and joint state.

This does not claim that every possible higher-width certificate passes, that all output end conditions hold, or that a multi-input completion exists.

## A concrete residual interface for further work

The repaired prefix also has an explicit all-width relation to the target. With Hermitian Paulis `Y_j=i X_j Z_j`, put

```
a=Y0 Z1,  W=Z0 Z2,  J=Z1 V C2,
M=X1 V CNOT(2->0) Z1 S2 CZ02.
```

`J` uses one paid call and `M` is entirely free. The independent standard-library checker `verify_residual.py` multiplies actual 8-by-8 matrices over Gaussian rationals and verifies the two **word** identities

```
J W C0 P C0 = M C2,
J W C0 Q C0 = K a.
```

Tensorize these identities separately and then add the second with coefficient 2. For every positive digit width,

```
J_f W_f F_new,f = M_f C2_f + 2 K_f a_f.
```

Thus the remaining contamination is exactly a free image of one paid call, rather than an unspecified operator. This gives a precise cross-input cancellation problem. The formula itself is not a saving: directly computing both terms is insufficient to deliver five independent targets in fourteen calls.

The same checker verifies four actual free projector sectors, generated on input by the commuting Hermitian Paulis `a=Y0 Z1` and `b=Y2`. At width `f`, set `e(alpha,beta)=(I+alpha*a_f)(I+beta*b_f)/4`. The prefix transports this projector to `e(epsilon*alpha,epsilon*beta)`, where `epsilon=(-1)^f`. These projectors can pack pieces of distinct independent inputs and separate them after the two-call prefix, but the other pieces must also be preserved and eventually processed. This is a feasible interface, not a complete unit.

## Reproduction

Only the Python standard library is required. No network, solver, floating point rank, or source checkout is used.

```sh
python3 -B verify.py --check RESULT.json
python3 -O -B verify.py --check RESULT.json
```

The checker authenticates the unchanged #4688 engine and README, runs that predecessor's complete calibration and seven controls, computes the new Gaussian ranks, verifies the four-point pencils and the actual monomial inverse, and checks the exact deficit arithmetic. It also invokes the independent Gaussian-rational residual checker, including its wrong-phase and wrong-coefficient controls. Regenerate the deterministic report with `python3 -B verify.py --out RESULT.json`.

The frozen predecessor engine is retained under `vendor/pr4688`; its provenance and hashes are in `PINNED-SOURCES.json` and `NOTICE.md`. No Lean proof or human review is claimed.

The registered repository replay is:

```sh
python3 scripts/research_package.py --package research/phase-aligned-two-call-prefix
```

## Open next questions

1. Complete the repaired prefix to five independent transforms in fourteen calls. Start with the explicit residual identity and the four Pauli sectors, preserving every complementary input piece and restored scratch. A literal all-width continuation and its complete paid bill remain missing.
2. Test other width-six invariant subspaces and output end conditions. The proof above covers every natural `H tensor V^r` hook lift; it does not cover every invariant of the engine game.

The structured questions, scope change and current-priority provenance are recorded in `TASK.json`. The selected frontier is unchanged.

## Attribution and review scope

Prepared by Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance in parallel research, implementation and independent agent review. New work is Apache-2.0. Credit lee-phys's #4688 for the original two-image construction, rank engine and controls; Jacob Sussman's #4628 and its retained sources for the model and lower bound; and the predecessors credited in the unchanged source README. The new result is the target-deficit analysis, explicit phase repair, lifted-hook proof and residual interface. No independent human review or full multiplication-theorem verification is claimed.

`SOURCES.json` authenticates the vendored files through their first preservation commit on this branch; their Git blob IDs are also checked equal to the files at the original #4688 head. The original commit, paths and SHA256 hashes are recorded separately in `PINNED-SOURCES.json`. No predecessor branch is merged or modified.
