# Finite two-real packed parent at the actual PR5095 caller

This is one source-bound caller recipe and Python draft, not an executed construction or measured saving. It retains PR5095 head `e65f47db55b9a3779fbf7fe23e93a8a4c5eb3ce1`; the monitor authenticated its successor `467445ad61472f25e8b4d6757f838aceecf4fdec` as a README-only change, with all code/inputs/receipts/checks unchanged. The published actual hook is `Sandwich.run` in `research/physical-tensor-crt-sandwich-recovery/sandwich.py`, with inherited literal `Tensor.run` and `Converter.run_plan` owners. No rational-unitary proof/reference class or newer Core allocator is substituted.

`SOURCE-sandwich.py` is the unchanged inspected source snapshot. `packed_sandwich_DRAFT.py` keeps that owner's preflight, alias exclusion, complete private-owner inventory, child-return consumption, exact ingress/recovery/carries, strict production guard, failure cleanup and pending-output token, while replacing the two-forward/product segment by the recipe below. Only Python AST parsing has run. Imports, constructors, fixtures and factories have not run. An isolated implementation worktree and independent code/lifecycle review are still required before execution or publication.

## Exact typed recipe

Inputs remain five distinct borrowed tapes: two independently variable length-q radix-2^b digit streams, one catalogue, b and q. Require b,q>0, S<2^b, 2q-1≤S, p≥b+2. The independent operand dimension is2q real digit coordinates, not2q complex coordinates. Every borrowed source/cursor is restored as in the predecessor caller. Child owners transfer only from fresh, closed, lease-free disjoint constructors; occupied returned output rejects reuse until `consume()` performs its paid clear.

1. Execute the original ingress and forward CRT **separately for each input**. Retain exactly three total CRT calls, including inverse CRT after recovery. Both converted banks contain real exact p-grid quarter-disk data in the same original source-box order; the draft checks their imaginary components are zero.
2. Form one new owned complex bank h=u+i v by copying the two converted real components. Since each is below1/4, |h|<sqrt(2)/4<1/2, admitted by the existing Tensor entrance. Clear both consumed natural banks.
3. Call the actual complete `Tensor.run(packed,catalogue,rows)` once. Copy its return into the parent-owned H bank through the unchanged `child()` protocol, then clear/retire the child return. Clear the consumed packed bank. The actual call executes packed complex arithmetic; rounded linearity is never substituted.
4. Materialize a separate JH bank in the original source-box order, where J(j_1,...,j_D)=(-j_1 mod s_1,...,-j_D mod s_D). Preserve H. The source's frequency dilation R commutes with J; no R inverse is inserted.
5. Read H_j=(a+i b)/2^p and (JH)_j=(c+i d)/2^p. Form exact signed sums

       Araw=(a+c, b-d),    Braw=(b+d, c-a).

   These represent Atilde and Btilde on grid **p+1**, without split rounding. Use input word width (p+2)+1=p+3. Perform the four exact real products and two signed combinations of the usual complex product. The product numerator has scale2^(2p+2). Truncate each component **once by p+2 bits** to obtain a p-grid product. Applying shift p here is the required wrong-scale negative control. No divisibility or even-parity optimization is assumed.
6. Clear H and JH. Invoke the same actual Tensor with `opposite=True` on this product. Retain its complete entrance disk check: if a diagnostic reduced catalogue produces an unsafe product, reject and report it, rather than bypassing the boundary. Clear the consumed product bank.
7. Keep unchanged `recover()`, including both exact multiplications by S, shift2b+4, nearest p-grid rounding; then widened inverse CRT and carries. The exact ideal scale is S²2^(2b+4); the same Tensor gamma restoration is already inside each completed child and is not repeated.

The exact counterpart is H=T(u+i v), H#=conj(JH), A=(H+H#)/2=Tu, B=(H-H#)/(2i)=Tv, and Tplus(AB)=(u*v)/S². Every source coordinate and both components are retained. This is a scalar C^S product at the published parent cut, not the distinct inner polynomial-record product.

## Paid J routing and owned storage

The draft uses D explicit axis passes, with no free random access or host-side permutation. For an axis with shape `[prefix][s][suffix]`:

- copy the suffix group at coordinate0;
- move to the end of its s-1 remaining groups;
- copy those groups in reverse group order, preserving every bit inside each group;
- restore the source head to the block end and continue with the next prefix.

Each axis therefore performs precisely the coordinate map0→0 and j→s-j for j>0. In D dimensions, its composition is J. This differs from reversing the full bank or the complete record order. Odd source axes give one fixed point, the zero tuple; the routine writes that record once just like every other record.

Let w=p+2 component bits and B=2Sw full-bank bits. On an axis of size s, the explicit source-head movement inside the routing loop is B(5-4/s); output appends are B. Add full cursor rewinds, clearing consumed intermediate banks, Count/axis descriptor scans and encoded products—none is free. Thus the direct loop movement is at most5DB plus DB writes, followed by O(DB) reset/cleanup traffic and O(D²) encoded shape operations. H is retained separately; at most two alternating route banks are live during a pass. Fused product then needs H, final JH and its output; it does not store A/B arrays.

The largest new stage holds three O(B)-bit banks, besides unchanged child/catalogue/word backing. Packing also peaks at two natural inputs plus one packed output. The existing fixed128-role parent pool is retained, but its adequacy and every error cleanup path remain to be checked with the actual Tape cohort; no new resident Tape is allocated during run.

There are no newly introduced borrowed dirty helper arrays at the parent. All inherited child private/dirty-state restoration remains in the unchanged complete Tensor/Converter contracts. The proposal cannot count correlated or discarded helper targets as extra work.

## Complete finite bill relative to the source caller

| Item | Original5095 | Packed recipe |
|---|---:|---:|
| Complete Tensor calls | 2 forward +1 opposite | 1 packed forward +1 opposite |
| Complete CRT conversions | 2 forward +1 inverse | same3 |
| Coordinate complex products | S | S |
| Real word products at the nonlinear cut | 4S at input width w | 4S at width w+1 |
| Exact split additions/subtractions | none | 4S |
| Product-combination additions/subtractions | 2S | same2S |
| Final product component truncations | 2S, shift p | 2S, shift p+2 |
| Recovery real word products | 2S at retained widened width | same2S |
| New packing traffic | none | reads4S components, checks2S zeros, writes2S components |
| Frequency-negation routing | none | all D paid passes above |
| Complete child setup and catalogue traffic | all retained | all retained for each actual call; common preparation paid separately |

No total wall-clock or primitive-cost saving is asserted. One complete Tensor invocation is removed, but widened word products,4S split operations, packing, routing, rewinds, cleanup and their metadata remain charged. The word bound is the retained constructive DigitWordProduct/WordProduct bound, not a Gaussian rank reward. Core's two scalar channels do not supply any recursive saving. The coefficient of a finite outer caller can improve only after the entire actual bill is compared; κ is unchanged by this call-count observation alone.

## Error and recovery contract

The elementary proof in `notes/real-packing-5095-fit.md` (SHA256 `3b48e1790472a686ac1d7a50673b90fb2f456b5c72d35a85e5f96dbd54febf62`) has independent conditional PASS in `outputs/real-packing-independent-review-20261023/REVIEW.md` (SHA256 `6b4c95aee5c222a9168159e77a45b007a4a48c1e9d201de4258e0bdcce0326be`). Under the unchanged production-page/complete-Tensor premises, epsilon=E2^gamma2^-p, E=Dp²+6M+22+2D, the original guard C(3epsilon+2*2^-p)<1/2, C=S²2^(2b+4), suffices. Exact split maps have real-linear norm≤1; product error<2epsilon; one final component truncation adds<2*2^-p; opposite Tensor adds epsilon. Correlated split errors are allowed.

This conditional proof does not admit the existing reduced5x7 catalogue. Raising p at that geometry never repairs its production period/halo premises. A staged diagnostic must retain `require_recovery=False` and report its recovered bits and true product separately. The normal entry must reject the reduced catalogue.

## Pre-execution decision and scope

No factory execution is authorized by this packet. The smallest cheap proposed step is the source's existing `--suite leaves`, plus one source-cohort physical Tape/arithmetic test of the new paid J route and widened fused product, with supplied approximation data clearly labelled as such. It does not claim either complete Tensor has run. A separately budgeted staged packed-forward/opposite diagnostic would be the first complete-call binding; its exact catalogue must be prepared or authenticated from a reusable source cache first.

The source author's earlier Mac full export run took372.34s; the later Ubuntu/Python3.12.15 optimized full invocation timed out at600s. Optional fixture preparation alone is reported at~251s. These observations are not interchangeable runtime guarantees. This packet therefore schedules no full baseline replay or new production factory merely for orientation. `FIXTURE-PLAN.md` declares parameters, probes, source-cache prerequisites and a bounded first execution proposal for root's decision.

Credit standard two-real FFT packing prior art; JoyboyBrian's actual5095 parent and separate Core allocator; Jose Manuel/jmbarrancoml Tensor3935; Tekalign/tekuuu CRT4024; Mason Hale's recovery predecessor; all retained Gaussian/native/router/word/analytic contributors; Astra's source-bound error deduction and the independent reviewer. Substantial OpenAI Codex assistance. No public write, push, κ claim or frontier modification.
