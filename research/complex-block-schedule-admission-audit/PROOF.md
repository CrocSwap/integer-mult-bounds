# Exact scope and mathematical checks

## 1. A sharp bound for the literal full cascade

Let V=(C^n)^W, and let X_s be the address permutation x -> x xor s. In each of the three source models,

    M = I + U/2,       (Uz)_k = X_(s_k) z_((k+1) mod W).

The source shift lists are (1,2,4) for W=3,n=16 and W=3,n=32, and (1,2,...,13) for W=13,n=16. U is a permutation, hence unitary. The triangle and reverse triangle inequalities give

    ||Mz|| <= (3/2)||z||,       ||Mz|| >= (1/2)||z||.

Thus M is invertible, ||M||<=3/2, ||M^-1||<=2 and cond_2(M)<=3. This is an endpoint norm ceiling, **not** a paid-call or κ ceiling.

Both inequalities are attained. The all-ones vector has Uv=v. For the lower extreme, take the address character h(x)=(-1)^(x_0) and block signs a_0=1, a_(k+1)=-(-1)^(s_k bit0) a_k. Because W is odd and the xor of all shifts has bit zero set (7,1,7 in the three cases), this recurrence closes around the cycle. Then z_k=a_k h satisfies Uz=-z. Hence Mv=(3/2)v and Mz=(1/2)z. Exact norms are 3/2 and inverse norm2, so the sharp condition number is3.

For both three-cycles the low signs are (1,1,-1). For the thirteen-cycle they are (1,1,-1,-1,1,1,-1,-1,1,1,-1,-1,1). These are literal integer witnesses on the actual finite address spaces; RESULT.json records them. The checker verifies the permutation bijection and both eigenvector equations independently, after comparing every source coupler to the specified permutation matrix. It also compares every entry of #4818's assembled 48-square and #4826's assembled 96-square matrices, and all 208 input columns of #4819's actual forward method.

The small loop norm 2^-W controls a Schur complement I +/- (product G_k) after elimination. Elimination/back substitution also acts on the full vector; its norms cannot be discarded. Therefore (1+2^-W)/(1-2^-W) is not a valid bound for cond(M). This refutes9/7 and8193/8191 as **full-cascade** bounds while preserving invertibility and the weaker bound16. No condition claim is made here for #4813's different observation model or for the overdetermined O_full matrices.

## 2. Explicit block-3 sector misuse witness

Use the exact operators in #4813 `verify_schedule.py:198-235`. They satisfy

    B = M0 C2 + 2 K a,       H K a = K/2.

For a plus-swap-sector input, C2 x = T A x; thus H(B-M0 T A)x=Kx. This implication requires Tx=x. For arbitrary input e_1, exact evaluation instead gives

    [H(B-M0 T A)-K]_(0,1) = -(1+i)/4.

The checker also verifies Te_1 != e_1. This is a counterexample to the hypothetical misuse of that conditional plus-sector rule on all inputs. It does not assert that the source states this conditional identity without its sector premise; the source admission gap is its absent complete shared-bank word. It is **not** a disproof of sector splitting with its copies, recombination, calls and storage charged, nor of another all-input decoder. #4813's test suite supplies known sector signs and forms ideal Kx+Ex observations directly. It does not emit a full shared-bank word that maintains those independent original inputs across overlapping ports. Dense Gaussian elimination followed by K on the recovered x is an algebraic recovery check; its operation price needs a separate admissible realization.

## 3. Positive block-5 check and remaining realization boundary

#4826's `verify_ports.py:149-168` defines F=C0(P+2Q)C0 and J=C4 C3 C2 N. It computes R=JF-2K but supplies no assertion that R has the claimed form M0 C4 C3 C2. This audit computes

    M0 = R (C4 C3 C2)^*,

checks one nonzero in every row and column, and checks M0(C4 C3 C2)=R exactly. This finite identity succeeds and should be retained. The test does not establish an all-width tensor identity or make the three calls in J include the two calls already needed for F.

The schedule constructor (`verify_schedule.py:155-216`) sets K=C4C3C2C1C0, picks G_k=X_(2^k)/2, sets E_k=KG_k, and inserts K,E_k into O_primary. The count s=9 is assigned independently. Full rank and exact recovery show that these **postulated observations** determine targets. They do not demonstrate three paid calls per port, ownership-safe chronological composition, a true raw inverse transpose, or priced physical implementation. #4818 and #4819 use the same distinction between assigned call counts and assembled target-containing observations. No universal impossibility of their call shapes is inferred.

The source tests also do not discharge arbitrary tensor width, field/phase lifting, control/movement/storage, finite precision at internal cuts, complete recursive profile, compiler reserve or outer transfer. The printed unit exponent formula cannot be imported as a complete integer multiplication κ until those obligations are bound to a real word. Passing a lower-bound capacity inequality only removes one necessary obstruction; it does not synthesize the word.
