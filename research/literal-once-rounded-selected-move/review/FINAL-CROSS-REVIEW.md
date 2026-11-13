# Cross-review: literal once-rounded selected MOVE

**Verdict: numerical argument and post-round fit pass under the cited Gaussian and frozen-core premises. No arithmetic counterexample found. The source-specific tariff is internally consistent as stated. This is a bounded proof/source review, not a fresh run of the emitted table or a proof of its inherited providers.**

Reviewed source versions at inspection:

- `worker-a/research/literal-once-rounded-selected-move/PROOF.md`, SHA-256 `5f068ccda93fe5c527d6a8374e4345232e6f19d6e691ee64cff5373395e8c07a`.
- `worker-a/research/literal-once-rounded-selected-move/rounded.py`, SHA-256 `760a20d8adc2c6d7c91a3f696d6127f928c805ada2449688ec92f221007702d3`.

## Numerical bound and signed-minimum input

Let `M=2^(w-1)` and `k=ceil(f/2)`. The componentwise bound `|x|<=M` includes the signed minimum `-M`. The ingress word is exactly `sign^(k+1) || original_w_bits || 0^k`, hence has width `W=w+2k+1` and value `2^k x`; for `x=-M` it represents `-2^(w+k-1)` without overflow. The phase monomials permute, swap, or negate components and preserve this magnitude bound.

For every actual prefix of `j<=f` central axes, the cited denominator premise gives integrality after scaling by `2^k`, since `ceil(j/2)<=k`. The cited component norm gives

`|prefix component| <= 2^ceil(j/2) 2^k M <= 2^(2k)M = 2^(W-2)`.

That is strictly inside signed W-bit range, so it also rules out negation of the widened minimum. The proof's local four-term numerator is bounded by `4*2^(W-2)=2^W`, which fits signed `W+2` bits; the completed quotient is bounded by the prefix result above. This supports the claimed stored-prefix and scratch widths, conditional on the cited core fact that each temporary numerator is the stated four-term sum.

## Once rounding and post-round fit

For `z` in the complete W-bit output, the high `n=W-k=w+k+1` bits represent `a=floor(z/2^k)` and the low bits are its Euclidean remainder `r`, including for negative `z`. The first discarded bit is one iff `r>=2^(k-1)`, exactly the condition for `floor(z/2^k+1/2)` to be `a+1`. The code scans all k discarded bits, increments the whole n-bit prefix when that bit is one, and accepts the all-one `-1` carry wrap as `-1+1=0`. The proof's core-output radius bounds `a` and `a+1` strictly inside signed n-bit range, so this modular implementation equals the integer result.

The fit loop is correctly indexed. Its first `read TMP` only selects the sign branch and does not move the head. With `MARGIN=k+1`, the loop then checks positions 0 through k, leaving TMP at k+1. The next stationary read checks the first retained sign bit at k+1, and the w-bit copy starts at that same position. Thus the code checks precisely the redundant sign extension and copies exactly w bits. No off-by-one defect remains.

The `w=2,k=1,z=-5` control is sharp for ordering: `a=-3` is out of range but the discarded half bit rounds it to `q=-2`, which fits. The code rounds first and checks fit afterward, so it preserves this legal result. The negative half-tie convention is also correct: `z=-1,k=1` gives zero (ties toward positive infinity), while `z=1,k=1` gives one.

The public write is after all component checks. A later overflow can leave staged OUTPUT bits, but does not modify public DATA; failure cleanup is explicitly outside the claim. Success commits only the complete staged array.

## Cost, history, and inherited ABI

The direct time arithmetic in §6 is consistent: `E_W<=E+2W<=E+2V_W` for positive packet dimensions, and the displayed core plus wrapper allowances are bounded by `2^26(fV_W+E+1)`. The history sum is also conservative: wrapper/private and public visited intervals are below `64(V_W+E+1)`, while the core allowance is at most `3072(V_W+E+1)`, totaling below both the proof's intermediate `3136` and declared `4096` coefficients. Erasure does not reduce `K_entry`; later calls retain prior backing. I accept the frozen core and helper tariffs as cited premises and did not independently recalculate their emitted transition tables.

The local port map is coherent: public ports are 0 and 1; `PRIVATE=2..24` has 23 wrapper roles; `(WH,WD,25..53)` is an injective 31-port core map; core halt is redirected to the local continuation; and the emitted alphabet is fixed to blank, `0`, `1`, and marker. `rounded.py` pins helper inputs and checks the core instruction-graph hash. Its initialization and retirement use the origin-1 marker guard. Consequently the theorem applies to that inherited local tape convention; it does not by itself refine to any native tape ABI that forbids motion/access at relative -1. Such a placement still needs a compatible primitive contract or a paid adapter.

The caller-level nonclaims remain material: this proves a source-specific leaf converter, not old-codec/strided source entry, selected caller placement, recursive tariff, or complete multiplication.
