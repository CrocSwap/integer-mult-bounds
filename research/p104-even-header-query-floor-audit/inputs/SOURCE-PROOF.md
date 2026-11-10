# Conditional κ = 0.00330720 from two paid idle fragments

This complete construction raises conditional κ from **0.00330420** in [PR6716](https://github.com/CrocSwap/integer-mult-bounds/pull/6716) to **0.00330720**, an absolute increase of **0.00000300** (about **0.09079%**). It retains the five assumptions `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`. It does not claim an unconditional theorem or change the repository's selected frontier.

The native supplier is unchanged. Its pinned source and full replay are retained in the sibling `sources/pr6716/` and `fragment/RESULT.json`. Native and earlier caller authors retain their recorded credits. The two-pair root, paid fragmentation and new witnesses were developed with OpenAI Codex for [zxv](https://github.com/zxv).

## Actual caller

An eight-field shortest root uses nine nilpotent queries and six full sites, at indices **0,1,2,6,7,8**, with ranks **(2,4,4,4,4,2)**. Its two rank-four shared stage supports are `{0,1,6,7}` and `{0,2,4,5}`. Their active native queries are exactly `E01,-E10` in their respective common bases. Both remaining coordinates in each bank are genuine common idle directions. The exact integer root and every basis are in `ROOT.json`; `root_check.py` checks every independent stage and central character.

The child sizes are **(4,4,1,1,4,4)**. All 18 native invocations, 12 internal binary suppliers, 15 thin queries, all idles, arbitrary public inputs, owned lifetimes and phases are counted. Rotate the two idle banks by determinant-one matrices `[[2,-1],[1,0]]` and `[[-2,-1],[1,0]]`. In each bank, pay one idle direction separately on its two child bodies. The other direction retains its combined job.

The first equal-target group is fields 6,7. Its exact input column and row are `c=-2e6+e7`, `d=e7^T`. After the first paid fragment, the prefix has the dual identities `Pc=D_B a`, `bP=D_B d`, where `a=-e0+e2`, `b=-e1^T+e2^T`. Both pairings are one. The literal input matrix is `[[-2,-1],[1,0]]`; the cut basis is `ADD(0,2,1); ADD(2,1,-1); SWAP(2,6)`. Retire original field 6 and introduce fresh arbitrary field 32 only into the suffix. This replaces qBC by independent B and qC.

The second group is fields 4,5. Take `c=-e4+2e5`, `d=-e4^T`. Its prefix has `Pc=S D_D a`, `bP=S D_D d`, with `a=-e1+e2`, `b=-e0^T+e2^T`, and normalized central involution `S=λq^-1`. The input matrix is `[[-1,0],[2,-1]]`. The cut basis is `ADD(1,2,1); ADD(2,0,-1); SWAP(2,4); LAMBDA(4,-1)`. The final ordinary normalization turns the prefix into q^-1 D_D. Retire field 4 and introduce fresh field 33 to the inverse cut basis and suffix. The inverse ordinary normalization is paid and leaves a plain E output. This replaces qDE by independent qD and E.

All basis coefficients are legal dyadics; the listed scalar input matrices have determinant one. Every added field is arbitrary and untouched before its handoff. No stage factor occurs in an ordinary basis. The dual-pair retirement argument and general lemma are also explained in `../fragment/PROOF.md`.

## Complete economics and qualification

At this allocation, each changed target has rank 41 and is replaced by independent ranks 32 and 9. Each changed paid rank-40 idle is replaced by paid ranks 32 and 8. Therefore, relative to this same unfragmented root and allocation,

```
ΔT = 208(H32 + H9 - H41),
ΔP = 208(H32 + H8 - H40),
Δ(T-P) = 208((H9-H8)-(H41-H40)) > 0.
```

The last inequality follows from strictly decreasing increments of `H(r)=r^t`, for `0<t<1`. Comparison with PR6716 and the previously admitted 17-stage caller uses their complete signed invoices, including all changes in trees and native invocation counts; it is not inferred from this local inequality alone.

The final caller has **34 arbitrary independent inputs**, **606 instructions**, **13,670 productive fields**, **66,852 paid requests**, and rank-mass surplus **760**. Both coefficient engines check all **1,156 forward and 1,156 reverse entries**. The independent engine additionally verifies both actual prefix identities and rejects corruption of paid jobs, both handoffs, target credit and the second cut's phase normalizer.

The changed physical replay checks **7,488 contacts** and absolute output phases, all paid whole idles, ordinary λ normalizations, and fresh body axes. Two independent rational interval engines certify a raw crossing in **(0.0033072446848, 0.0033072446849)**. The finite certificate uses tested saving 0.003307205, claim 0.00330720, strictification power 1920 and cutoff/floor 11/12, explicit compiler threshold and all **54+4** outer inequalities. All ordinary work and scalar heights are recomputed from the new word. The once fully replayed native proof is reused byte-for-byte and hash-bound; its five framework assumptions remain conditional.

`RESULT.json` is the complete receipt, `INDEPENDENT.json` the independent algebra receipt, and `FROZEN.json` binds the reviewable files. `../two-fragment-replay.log` ends in `PASS_CONDITIONAL_KAPPA_00330720_TWO_PAID_FRAGMENTS`. Reproduce with `python3 -I -B verify.py` and `python3 -I -B independent.py`, retaining the pinned sibling sources and dependencies. The uniform compiler specifies an enormous finite multiplier; that word is not materialized.
