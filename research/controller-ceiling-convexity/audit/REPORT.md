# Independent audit of the PR5405 successor certificate

**Decision: PASS_SCOPED_FIXED_FAMILY_CEILING.** The reviewed v3 arithmetic and the two frozen analytic notes establish the necessary-moment obstruction for the exact family defined by PR5405 equation (1), at source head `314b56a6c0056c2358538f072c6fde9d365be44d`, throughout `0.00302728825 <= kappa < 1`. No missing mathematical implication was found within that stated family. The original optimized-mode acceptance defect and a source-representation discrepancy were found during review and resolved transparently before this decision.

This is a second mathematical/code review, independent of both the sole Astra theory worker and the numerical implementer. I read the source proof, both analytic notes, the numerical implementation and its remainder proofs, and the existing normal/optimized receipts. I did not execute the numerical checker, the author's DP or interval engine, a native/compiler/scientific replay, Lean, or a construction search. The metadata checks in `AUDIT-CHECKS.json` only inspect already retained JSON, AST and hashes. No public write or selected-result change occurred. New review material is confined to this directory.

## Exact reviewed objects and source binding

The exchange note has SHA256 `0e575a88d28db5aecc5ccf24504923a0508ff976d05f92e91e6d48408b7688ea`; the discrete-convexity note has SHA256 `bdad476f31b450e1ac4d1fd0d9530b43e33ebac48accc0956b38a9634b40a929`. Their frozen copies and original local files were preserved.

The final numerical directory is `outputs/controller5405-exact-successor-20261024/`. Reviewed final hashes:

| Object | SHA256 |
|---|---|
| `check_ceiling.py` | `8f443aa005f5c7c4e2286524e815074787cc109a06cc66e56f362f8cc7854b01` |
| `PROOF.md` | `b0aff27dd9203ef42e5b8898d6659819205f13c1d251ff043564fcab656bf7f4` |
| `receipts/arithmetic-v3.json` | `32d3adfc837ba4f66c899e7cb23adea441a3af48d96700f2e14e6c9f8b1c6729` |
| `receipts/arithmetic-v3-optimized.json` | `6d4b1c890bed07576ef4f76c47e27ce9effe903b7646f650f0092c03c69a6bda` |
| `FINAL-MANIFEST-v3.json` | `40a066e930adc821acf08fe6652f38626ef8c776ba111c8b7b8205ec2fa91841` |

I fetched `research/global-query-controller-ceiling/PROOF.md` independently through the GitHub connector from `aliromman/integer-mult-bounds` at the exact head. Its real Git blob is `5ad89d4ba1836d47798bdb856e3726c70a7b1922`, independently recomputed from the returned 10,029 bytes. Its SHA256 is `77dc9ce552be7dc9c9a32850c2f2cf0eff92cfe2e0a0e316db210a1667a8d32b`. The retained monitor proof is 10,030 bytes, SHA256 `5c82c9f1650b0ffb352f2aa7eaac3aa283754028e41cd85d1ee848af9d18cd37`, and equals the exact upstream bytes plus one LF. This is an exact representation bridge, not byte-identical upstream retention. There is no mathematical text change. Both the connector response and the bridge are retained here; the numerical owner also added an explicit bridge and exact upstream copy without altering the frozen monitor.

The six guidance files AGENTS, CONTRIBUTING, autoresearch, agent-procedure, current-priorities and research-family-status were checked through `git show` at canonical `1ec1119972c9aefe42525172d07b332fcff81cb4` in `swarm-provider-audit-sol-high-20261024/repository`. Their SHA256 values agree with the numerical worker's frozen guidance manifest. The task is an expressly assigned bounded audit; root owns fresh overlap, publication and repository packaging.

## Mathematical chain

1. **Actual equation and census: PASS within the source premise.** The local contribution is exactly `nL+112(2p+1-n)`. Each retained idle contributes the three terms specified in equation (1), with zero-rank paid idles omitted. Reading the right side from its outside endpoint reverses its pair order exactly as required by the suffix definition; the central bit belongs to neither side prefix. Setting `J=p+sum g` gives `E=224J+112+(L-112)n-224f(1+8n)`. Thus fixed-n comparisons genuinely cancel only fixed-n terms. This checks the invoice algebra; it does not independently derive the Laurent/native construction supplying equation (1).

2. **Pair exchanges: PASS.** With `delta(z)=f(z+1)-f(z)`, deleting 00 changes J by `-1+delta(8k)<=0`; exchanging 01 for 10 changes it by `f(8k+8)-f(8k)-f(8)<=0`. Splitting 11 into 10,10 changes it by `1+f(8k+16)-f(8k+9)-f(8)<0`: the seven-unit increment on `[8k+9,8k+16]` is at most the increment on `[9,16]`, strictly less than that on `[1,8]`. The added pair includes two new paid QUERY stages, represented by the +1 in J. All moves preserve n and later partial FULL counts. Replacing each original pair terminates and leaves only 10 pairs; no illicit fixed-p constraint is assumed.

3. **Unpaired transfers and small counts: PASS.** A QUERY side end with a first 10 pair can absorb its FULL bit while deleting that pair, changing J by `-1+delta(8)<0`. Any remaining QUERY endpoint lies on an empty side. A last donor 10 pair can then fill such an endpoint or the center, changing J by `-1+delta(8k)<0`; its removal affects no later donor count. A donor exists whenever `qL+qR=n-(l+r+c)>0`. Consequently n>=3 gives all three unpaired positions FULL, `qL+qR=n-3`, `p=n-2`; n<=2 gives p=1 with all n FULL bits unpaired. In particular n=0 is exactly E=112 for every original p, not an omitted logarithmic corner case.

4. **Balancing and attainment: PASS.** With FULL side ends, a q-pair side contributes `F(q)=-sum(k=2..q+1)delta(8k)`. Its increments `-delta(8(q+2))` strictly increase. A side-count imbalance at least two can be strictly improved by transferring the final pair to the shorter side. The balanced split is therefore attained and minimizes every fixed-n invoice over all allowed p, splits and masks. Reflected balanced masks agree; equality moves at zero FULL prefixes mean this does not establish uniqueness of the minimizing original mask.

5. **Strict discrete convexity and gate: PASS on every n>=0.** Put `A_n=f(8n+9)-f(8n+1)`. This strictly decreases. The first differences are `D_n=L-112-224A_n` for n=0,1,2, and `D_n=L+112-224A_n-224delta(8 floor((n+1)/2))` for n>=3. The first side correction is delta(16), repeated twice. The only junction has `D3-D2=224[1-delta(16)+A2-A3]>0`; later second differences are strictly positive because the A difference is strict and the delta correction nonnegative. The affine L term cancels. Hence `C18>0, D17<0, D18>0` prove `C_n>=C18>0` for all n>=0. Strict neighbor signs make 18 the unique minimizing FULL count. Neither the author's n>=96 tail nor its 10,290,000-state DP is a dependency of this successor implication.

6. **Directed arithmetic and remainder proofs: PASS by code/derivation review.** The new code uses integers on Q=2^256 and exact Fraction tails, with correct sign reversal for subtraction/integer scaling and reversed endpoints for positive reciprocals. The atanh-log truncation after 128 terms has the stated positive geometric remainder `2 z^(257)/(257(1-z^2))`; directed term recurrence encloses the finite sum. Range reduction gives z in `[0,1/3]`. The positive exponential Taylor sum through degree64 has remainder at most `Xhi^65/65!/(1-Xhi/66)`. Its recurrence rounds each multiplication/division outward; the reciprocal then bounds `r exp(-kappa log r)`. The r=0,1 values are exact. All finitely requested positive ranks are integers at most161, so the range `0<=kappa0 log r<1` is also analytically closed; the code checks its outward version explicitly. No floating value enters acceptance. The already executed v3 normal/optimized receipts have identical proof-relevant JSON and the same exact arithmetic endpoints as v2.

7. **Full saving interval: PASS by a separate whole-invoice argument.** Delete 00 pairs at the t under consideration, preserving a no-greater invoice and n. For n>=1 normalize the fixed reduced invoice by 8^t. Its QUERY coefficient is `112(2p+1-n)>=0`; the main target base is `n+1/8>1`. Every reduced side summand is `h^t+e-(h+e+1/8)^t`. For h>=1 its t derivative is negative since `z^t log z` increases on z>=1. When h=0 reduction forces e=1 and gives `1-(9/8)^t`, also strictly decreasing. In `L/8^t`, the only positive derivative term is less than `7 log(8/7)<1`; the negative rank-one term alone has magnitude greater than `2193 log8/8>274`. All remaining derivative terms are nonpositive. Thus the normalized reduced whole invoice strictly decreases with t. Positivity at t0 persists for `0<t<=t0`, and unreduced invoices dominate their reductions at the same t. The n=0 branch E=112 completes the claimed interval `kappa0<=kappa<1`; discrete convexity alone would not do so.

The certified endpoint signs retained by the numerical worker are:

```
C18 > 0.000000014914967918767741908079
D17 < -0.271338621904872494155700553536
D18 > 0.022748156490424972863108432493
```

These displayed bounds are exact decimal rationals. Finer integer/Q endpoints are in the receipts. My metadata inspection checked those recorded exact endpoint signs, equality of normal/optimized mathematical fields, and the recorded 456 symbolic mask/split checks, 11 canonical checks and five rejection controls. It did not re-evaluate powers.

## Resolved review findings and trust boundary

**Optimized acceptance defect resolved in v3.** In reviewed v2 code SHA256 `3352d5c6dd0da6e988efcab7b6a8cfd5ff85655390bef472523e7022db431cd9`, the three-sign gate, coefficient equalities, domain guards and control checks were assertions and would vanish under `python -O`. I notified root and the numerical owner. V3 replaces every assertion with explicit require/raise; AST inspection finds no Assert node. The direct normal and optimized executions retain every acceptance predicate and agree in all proof-relevant output. Earlier code/receipts are preserved as earlier versions; their normal-mode numeric endpoints remain valid, while they must not be represented as optimized acceptance evidence.

The source +LF discrepancy is resolved by the explicit exact-byte bridge above and in the numerical v3 packet. No frozen input was repaired silently.

The checker and manifests are trusted Python/source artifacts, not a formal-kernel certificate or a self-authenticating adversarial verifier. A source file and its self-reported digest are not independent authority; this audit's external fixed hashes and the package worker's separate Git-origin/export checks supply that boundary. The arithmetic engine's correctness is justified by the directed-rounding/remainder review, not by interval overlap checks alone. Small symbolic controls check indexing and mutations; the all-n claims rest on the analytic proof. Broader publication and package integrity remain root/package-worker gates.

## Remaining implications and next questions

There is **no remaining blocker for this scoped mathematical ceiling**. Broader claims would still lack an independently repeated derivation of the autonomous P/H profile and equation (1) from all claimed native/physical programs, the complete source construction and its five framework assumptions, physical legality of arbitrary masks, compiler/supplier admission and any complete multiplication theorem. This audit does not validate PR5398 by comparison and does not establish the exact supremum in the tiny gap below kappa0. It establishes no physical/global optimum, new kappa, native-query lower bound, or transfer to changed/coupled PR5402 outputs.

The next useful step is the isolated package's exact-source, export and final claim review. No further arithmetic is needed to finish this audit. Reopen the mathematical decision for a concrete counterexample or changed source/formula; reopen construction work only with an explicitly changed provider/consumer, stage-rank, graph or idle-law premise and a complete bill.

Credit Ali Romman for PR5405's family, invoice and original unbounded proof/DP; Cinna Davis for the paired path/query controller; Cao Yifan, zxv, Chris R/Clear1nsight, Dugongue, Jacob Alan Sussman and the retained native/helper/compiler/analytic contributors. Root proposed the exchange and discrete-convexity conjectures, and the sole Astra worker supplied the two frozen theory notes. The numerical worker supplied the independent rational engine and executed receipts. This separate review was prepared with substantial OpenAI Codex assistance, under Apache-2.0 for new material. It is not an independent human or formal-kernel review.
