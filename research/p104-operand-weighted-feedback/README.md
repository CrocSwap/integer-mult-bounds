# Operand-weighted feedback for the completed P104 word

For the exact completed forward word in [PR2166](https://github.com/CrocSwap/integer-mult-bounds/pull/2166),
the same completed-instruction error contract admits **27 uniform guard bits**,
improving its sufficient 39-bit estimate. For requested accuracy b >= 3,
**26 guard bits suffice**. The word, its native rank mass 6,782, and its
unfavorable fixed-profile cost screen are unchanged.

The improvement comes from retaining each instruction's ideal operand norm
before accumulating its error. Multiplying the largest ideal state anywhere
by the largest defect amplification anywhere is unnecessarily coarse for
this word. This is a conditional precision implication, not an implementation
of rounded children, a physical precision minimum, or a new supplier or κ.

## Exact source and result

Nick Petalas's PR2166 is pinned at
`a655734277aa5f2ad74bcba29e093f6dd3b84a68`. Five unchanged files, including
the complete word, source verifier and original receipt, are retained with
SHA-256 and Git blob pins in [REFERENCES.json](REFERENCES.json). It supplies
the signed coefficient model, completed-output contract, all-cut constants
and unitary-chart interpretation. Jose Manuel's PR2139 supplies the completed
construction; Adam Gall's PR2096 supplies the preceding stability framework.

The unchanged word has 844 initial roles, 34,333 instructions and 32,722
defect sites. It has 34,334 instruction boundaries including the initial one.
All initial register Hilbert norms are at most B. The norm throughout is the
maximum of register Hilbert norms, not addresswise maximum norm.

| Quantity | Exact value |
|---|---:|
| Source ideal all-cut row norm P | 131,072 |
| Source weighted defect coefficient K | 2,134,050 |
| New operand-weighted defect coefficient J | 66,657,328 |
| Old uniform threshold K(P+1) | 279,716,335,650 |
| New uniform threshold J+K | 68,791,378 |
| Sufficient uniform guard, old / new | 39 / 27 |

J first peaks after zero-based event 33373, at source register 93. The peak's
ideal input row is `-65536*(input86+input93)`. Input86 is an arbitrary dirty
helper, so dropping it would invalidate the result. The full 29-defect peak
row and each of its new weights are recorded in [RESULT.json](RESULT.json).

## Operand weights and feedback theorem

Write the exact ideal state at a cut as `z_r = sum_s L_rs input_s`, and put
`p_r = sum_s |L_rs|`. Thus `||z_r|| <= B*p_r`. At each defect site j define
the weights from the **pre-instruction ideal rows**:

| Exact operation | Ideal operand weight a_j | Error weight w_j |
|---|---|---|
| Unitary native transport of r | p_r | 1 |
| `dst += c*src` | p_dst + |c| p_src | 1+|c| |
| `dst *= c` | |c| p_dst | |c| |

Owned resets and monomial/frame annotations remain exact as in the source.
The source's relative contract bounds the completed operation's output
defect by u times its actual operand expression in the second column,
with actual Hilbert norms replacing the p values. A native child's internal
implementation must establish that contract separately.

Let C_(t,r),j be the exact signed coefficient transporting site j's logical
defect to register r at boundary t, including effects of later resets. Define

`J = max_(t,r) sum_j |C_(t,r),j| a_j`,

`K = max_(t,r) sum_j |C_(t,r),j| w_j`.

K is exactly the source's retained weighted coefficient; the new replay
checks that its w vector agrees entry for entry. Let E be the maximum actual
minus ideal register error over **every included boundary**. At each site,
the triangle inequality for its perturbed operands gives

`||eta_j|| <= u*(B*a_j + w_j*E)`.

Unitary source charts preserve each physical defect's Hilbert norm. The
exact linear superposition formula and triangle inequality at every boundary
therefore give

`E <= u*(J*B + K*E)`.

If uK < 1, rearrangement proves

**`E <= B*u*J / (1-u*K)`**.

This is an a priori finite-execution bound: E includes the earlier operands
used to bound every defect, and no independence or absence of feedback is
assumed for actual defects. Signed coefficients are retained until the final
weighted sums; a positive-majorant recurrence through the entire word is
not substituted for them.

For integer b >= 0 and u <= 2^(-b-g), a sufficient condition for
`E <= B*2^-b` is

**`2^g >= J + 2^-b*K`, with `2^(b+g) > K`.**

For all b >= 0 the right side is at most J+K=68,791,378 < 2^27.
For b >= 3 it is at most J+K/8=66,924,084.25 < 2^26. The strict
feedback condition also holds. Conversely J+K/4=67,190,840.5 > 2^26,
and J > 2^25. Thus this particular sufficient inequality yields the exact
piecewise integer allowance 27 for b=0,1,2 and 26 for b>=3.
Failure of its smaller allowance is **not** a lower bound on physical
precision or a claim that another analysis cannot improve it.

The new synthetic weighted-defect coefficient J is attained by assigning
each independent defect the sign of the peak covector and magnitude a_j.
The checker executes that injection literally. This only proves sharpness
for the independent defect budget `||eta_j|| <= a_j`; the ideal-row maxima
need not be attained by one actual trajectory, and that injection is not
claimed to satisfy the state-relative rounding contract. No sharpness of
the nonlinear feedback bound is asserted.

## Verification and its limits

The replay authenticates all five original files before importing source
code. It first regenerates and compares the **complete original receipt**,
including P, A=1,394,705, K, the old 39-bit guard, signed peak witnesses,
endpoint error maxima, all-cut stream hash and paid profile. The old estimate
remains correct; it is being refined, not reported as a bug.

A new Fraction-based ideal-row pass computes every a_j before its instruction
and independently checks all 844 final input rows. The new weighted forward
pass reuses the authenticated source's integer-row machinery with a different
weight vector. Every changed row's weighted sum is directly recomputed to
check the cache. This reuse is credited and is not described as an independent
implementation. All changed rows at all boundaries are visited; unchanged
rows preserve the previously checked bound.

A separately written sparse Fraction reverse covector agrees on every signed
coefficient of the J peak and six endpoint rows spanning source, target,
helper and private roles. These are seven reverse checks, not an independent
reverse audit of every boundary. The complete forward scan supplies that
coverage. An independent literal scalar injection attains J for the synthetic
weighted-defect model described above.

Six semantic controls show why pre-operation norms, both addition operands,
absolute coefficient magnitudes, escaped private defects, relative feedback,
and native sites with zero ideal value must be retained. The real source has
no zero-ideal-weight defect site; the latter is an explicit small contract
control rather than an additional source finding. Export controls exercise
source and typed-receipt corruption and actual weight-code mutations under
optimized Python.

From the repository root, standard-library Python 3.12:

```sh
python3 -I -B scripts/research_package.py --package research/p104-operand-weighted-feedback
python3 -I -B scripts/research_package.py --package research/p104-operand-weighted-feedback --check-only
```

The mathematical replay prints `PASS_P104_OPERAND_WEIGHTED_FEEDBACK`.
The complete registered replay and all five export test groups passed on
CPython 3.12.14; the optimized primary replay also passed on CPython 3.14.5.
The registered command also runs the artifact tests. Default replay is
read-only and checks the full typed receipt; explicit `--write NEW_PATH`
creates a new file exclusively. The mathematical export needs only this
package, no Git or network. Metadata/source pin success is not mathematical
acceptance.

The fixed word is accepted as the source's exported native/logical stream;
this package does not re-run its upstream producer, every Clifford recipe,
or the selected cold replay. Physical adapters must retain the source's
exact/unitary assumptions. Approximate borrowed restoration is bounded by E;
it is not promoted to exact restoration of rounded state. Exact private
discard remains part of the source contract. Internal rounding, actual
operator implementation and reserve/precision charges remain open.

## Family decision, overlap and next consumer

Scientific base is current main
`c3c94c2ea2ebcd5d69d1e51b5fe8a36bf79819f5`, priority revision 5. The fresh
recursive-interface selection and binding baseline are in TASK.json. The
scope is changed to this concrete precision-interface refinement after an
output-slice candidate was retired as duplicate of PR2709; that candidate
was not published or counted. Coordination is on
[PR2166](https://github.com/CrocSwap/integer-mult-bounds/pull/2166#issuecomment-6199131728).

PR2670 independently audits a different QQ16 word and tightens its integer
guard using the original K(P+1) inequality. PR2654 studies a different P104
relay word; PR2549 concerns a private-macro dual. They retain their priority
and do not supply this exact word's operand-weighted J or feedback estimate.
Cached open-PR and Discussion coverage, live source head and current-main
review checks are recorded with their limitations. No-match searches are
not novelty certificates.

**Decision: narrow.** Proved here: the conditional feedback implication,
source-bound all-cut J and its integer allowance. Constructively supplied:
exact forward, reverse and synthetic-witness checks. Unknown: actual rounded
rank-1 through rank-7 child contract, internal range, physical tape/hosting,
global precision charges and all-size supplier admission. Unknown costs are
not zero. The native rank mass and unfavorable fixed-profile cost screen are
retained; no selected precision invoice is reduced.

## Open next questions

Can an actual rounded native child meet the same completed-output Hilbert
contract at u <= 2^(-b-27), or 2^(-b-26) for b>=3? Begin with one declared
rounding convention and bind its local defect and magnitude bounds to the
exact operand expression above. Stop further guard arithmetic for this word
until that implementation or a materially sharper feedback model is supplied.

## Credit

Prepared for ywz65 with substantial OpenAI Codex assistance. Credit Nick
Petalas / PR2166 for the exact exported precision model and arithmetic;
Jose Manuel / PR2139 for the completed construction; Adam Gall / PR2096 for
the Hilbert-defect framework; Arham Tahir / PR2670 for the distinct QQ16
threshold audit; and the Rohan Arun, Chafik Boukhalfa, Ali Romman, Josie
Elliston and selected Hamming/compiler lineage retained in source/NOTICE.md.
Standard perturbation and triangle-inequality arguments are not claimed as
new general mathematics. New code and retained material are Apache-2.0.
No human review, proof-assistant or hosted-CI pass is claimed.
