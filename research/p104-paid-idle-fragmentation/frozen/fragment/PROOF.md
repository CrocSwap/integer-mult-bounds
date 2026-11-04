# Paid idle fragmentation creates a productive retirement

The complete changed construction proves conditional **κ = 0.00330500**, an increase of **0.00000080** over the independently replayed conditional 0.00330420 in [PR6716](https://github.com/CrocSwap/integer-mult-bounds/pull/6716). It retains exactly the five assumptions `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`. It does not assert an unconditional integer-multiplication bound or change the repository's selected frontier.

The source is PR6716 commit `a467457692bc9e11113d9b2e2e34ea8ffb553b58`. Its complete 45-file manifest is preserved in `../sources/pr6716/LOCAL-PINS.json`. Native source and earlier caller work keep their credits in those files. This additional construction was developed with OpenAI Codex for [zxv](https://github.com/zxv).

## The new operation and its full bill

The root has two common idle directions across B and C. Each originally pays one rank-40 whole Gaussian job. Rotate that two-dimensional bank by the literal dyadic determinant-one matrix `[[1/2,-2],[1/2,0]]`. Pay rank 16 on its first direction after B, and rank 24 on that same direction after C. Its other direction retains its original rank-40 job. Thus the extra job is paid, and the complete endpoint before retirement is unchanged.

The equal BC-target group is fields 6 and 7. Take column `c = -e6/8 + 45e7/16` and row `d = 37e6^T + 2e7^T`. Their pairing is one. At the actual cut after the new paid B idle, the prefix P satisfies

```
P c = D_B a,       b P = D_B d,
a = -e0/16 + e2,   b = -16e1^T + e2^T,   b a = 1.
```

The literal input matrix on fields 6,7 is `[[-1/8,-2],[45/16,37]]`, with determinant one. Its first column is c and the corresponding inverse row is d. The cut basis is `ADD(0,2,1/16); ADD(2,1,-16); SWAP(2,6)`. It sends a to e6 and its pivot row is b. The emitter uses only dyadic ADDs, dyadic-unit SCALEs and SWAPs; no odd denominator or unpaid stage factor occurs.

Consequently the transformed prefix is a direct sum of D_B on field 6 and its complement. Park field 6 at that cut and introduce a fresh arbitrary field 34 to the inverse cut basis and remaining suffix. The fresh field is untouched before the handoff. This gives two independent outputs, D_B (rank 16) and q D_C (rank 25), in place of one q D_B D_C output (rank 41). All other inputs remain arbitrary. The previous D retirement is then performed with an additional fresh field 35 and is independently checked to survive.

More generally, if an invertible prefix P has unit dual pairs `(c,d)` and `(a,b)` with `Pc=ma`, `bP=md`, ordinary bases split P as `m ⊕ K`. If the complete target on the associated equal-target group is t, its complementary suffix splits as `t/m ⊕ L`. The actual implementation never applies an inverse of m: the original field stops at the cut, while a new independent field traverses the suffix. This is why both outputs earn independent target credit.

## Strict gain

Writing `H_r = r^(1-κ)`, the complete changes are

```
ΔT = 104(H16 + H25 - H41),
ΔP = 104(H16 + H24 - H40).
```

The signed gain is therefore `104((H25-H24)-(H41-H40))`, strictly positive for every exponent between zero and one because the increments of a strictly concave power decrease. The rank-mass surplus remains 760. There are 13,878 productive fields and 67,060 paid requests; every acquired and consumed helper remains charged.

## Qualification

`RESULT.json` records the complete unchanged native source replay, all 800 native columns, all owned lifetimes, 7,488 physical contacts with absolute phases, both interval engines, finite strictification, uniform compiler, fresh ordinary envelope and all 54+4 outer predicates. It proves the raw crossing lies between 0.0033050256038 and 0.0033050256039. The stated claim leaves a positive compiler and transfer gap.

The literal caller has 36 arbitrary independent inputs, 18 distinct fresh native stages and 610 instructions. Both the author engine and the separately written Fraction/Gaussian Laurent engine check every forward and reverse coefficient. `INDEPENDENT.json` additionally checks the prefix row and column identities and rejects corruption of paid calls, bases, handoffs and target credit. `../fragment-full-replay.log` ends in `PASS_CONDITIONAL_KAPPA_00330500_PAID_FRAGMENT_RETIREMENT`.

Reproduce the independent algebra with `python3 -I -B independent.py`. The complete source replay is `python3 -I -B verify.py`; the sibling pinned source directory must be retained. A uniform multiplier is specified by the inherited compiler certificate, not materialized at its enormous threshold.
