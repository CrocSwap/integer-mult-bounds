# Independent adversarial review of default nested-width growth

Verdict: **conditional PASS for the fixed raw-p7 default nested policy and the stated all-N bounds**. No peer/code-author draft was read before this note. I read canonical flow.py and verify.py's actual compile_counts source as inert text, the pinned raw profile, and the exact PR4476 README context. No source/own program, import, constructor, numerical experiment, test, compilation or kernel ran. File reads and metadata hashes are not scientific execution.

Source bindings: verify.py SHA256 `9ae067eadf17ff9d97737805eb642a69375a5ff2ddb08988fef59aa0771f9b7c`; flow.py `460f0b0262d7b6880973f46240b3fff1e9f04601fa1d658dda18688b1e26575a`; raw p7 RESULT `9b814be97e3b45fcc28eafa8a65694897a7387f71a14d44796c6aadf303d7fab`; PR4476 README `0563dd22edeba4ee82a5ac4a06d965ccb90edbb09bbe646c9f21497bd4789f76`. Source custody is canonical main7c49 for the actual code/data. Earlier source-aware S8/S9 exposure is retained; this is not source-unexposed discovery or native-census acceptance.

## 1. Which width policy is actually proved

The function initializes widths[e]=1 for all base ranks e<121, including0. Under the default `force_unit_replication=False`, its actual assignment is

`a_n=B_(n-1), B_n=a_n*S_n` for n>=121,

where S_n is the **full** Flow.merged source_count. Therefore for integer N>=121,

`B_N=product_(n=121..N) S_n`.

This is an exact recurrence property, not a normalized leaf-cost claim or a statement about every possible compiler. The copy loop separately checks a_n divisible by every required smaller width B_e; nested products make that true inductively. Source rank n may produce e=0: widths[0]=1 and its source occurrence still belongs in S_n. The zero leaf/record base at rank0 does not delete the original array or reduce productive width.

## 2. Fixed source-count lower bound

Retain the default integer-flow laws and fixed raw profile as premises: min target5 has multiplicity420, maximum target121, W=7688, paid count P=55998, and Delta608. These are the authenticated raw dictionaries, not a completed tensor rule.

At height G(n), the all-5 target word has column5^G<=floor(n/121), so it is present in the root unit batch. Its coefficient is exactly420^G, including G0's empty word. Each such unit has all W target job occurrences. The source initialization adds every root demand occurrence, and later sources only add nonnegative counts. Collisions in numerical rank aggregate counts; they do not deduplicate arrays. Hence

`S_n>=W*420^G(n)`.

This uses an actual present root batch, not the unsafe inference that every paid descendant batch is present. It also does not omit fresh child sources or assume separation of paid/target ranks.

## 3. Complete upper bound

The source's full unit bound gives

`S_n<=W*sum_(d=0..G) P^d*W^(G-d)`.

Here P-W=48310>0. Therefore the exact sum is `(P^(G+1)-W^(G+1))/(P-W)`, and

`S_n < (W*P/(P-W))*P^G`.

Using <= instead of < is harmless for the requested product envelope. This bound counts every paid depth and all source multiplicity. No division by P-W is asserted for a generic equal-P/W profile.

Write M=N-120 and H_N=sum_(n=121..N)G(n). Multiplying positive inequalities yields, for every integer N>=121,

`W^M*420^H_N <= B_N`,

`(P-W)^M*B_N <= (W*P)^M*P^H_N`.

All quantities in these two bounds are integers. No rounded logarithm, fractional replication or assumption that n is a multiple of121 appears.

## 4. Exact floor layers and asymptotics

Default G(n) is the largest j>=0 such that121*5^j<=n. For g=G(N), count its layers exactly:

`H_N=sum_(j=1..g)(N-121*5^j+1)`

`=g*(N+1)-121*(5^(g+1)-5)/4`.

The division is exact because every5^j is congruent1 modulo4. The endpoint values are

| N | g | H_N |
|---:|---:|---:|
|121|0|0|
|604|0|0|
|605|1|1|
|3024|1|2420|
|3025|2|2422|

Thus B_N=W^(N-120) exactly throughout121<=N<=604. A floor-layer transition adds the current G(N), not one whole historical block at the new height. In particular G3000=1, and the next layer begins only at3025.

Since g=log_5 N+O(1) and the subtracted geometric term is O(N),

`H_N=N*log_5 N+O(N)`.

Taking natural logarithms of the product bounds, the M-dependent constant factors contribute only O(N). Consequently

`liminf log(B_N)/(N*log N) >= log_5(420) > 3`,

`limsup log(B_N)/(N*log N) <= log_5(55998)`.

The strict >3 follows from420>5^3, with no decimal log calculation. Both constants are fixed and finite, so `log B_N=Theta(N log N)` and `B_N=exp(Theta(N log N))` for this policy. The inequalities do **not** prove the ratio converges, identify its exact coefficient or claim either endpoint is attained.

## 5. Explicit written controls — unexecuted

1. **Keep historical floor layers.** At N605, true H is1. Replacing every earlier G(n) by final g=1 gives the false exponent M=485 and incorrectly treats484 G0 ranks as G1. Dropping the121 factor in thresholds likewise assigns nonzero height at n121 although the actual cap is1.
2. **Do not discard zero complements.** At n121, source121 has multiplicity224. Removing it from S changes7688 to7464 and breaks the exact default B121=W lower endpoint. B0=1 makes its recursive zero-rank batch legitimate; zero leaf work is not zero productive-array count.
3. **Do not lose root multiplicity.** The all-5 coefficient is420^G, not one word representative. The theorem is not generic over inventories with no such multiplicity: for valid T={2:1},P={1:1}, default S_n=1 and B_N=1, so a universal positive NlogN lower coefficient would be false.
4. **Do not divide by P-W in the equal case.** The same W=P=1 control has full unit upper sum G+1; a denominator0 formula is invalid. The raw profile avoids this only because55998>7688 is fixed and explicit.
5. **Do not replace the batching policy.** Setting a_n=1 changes the recurrence to B_n=S_n and does not satisfy this theorem. In the actual raw G0 range, such forced replication already fails at n126: source5 gives complement121, whose width is7688, and1 is not divisible by7688. This does not rule out other properly funded admissible batching policies; they are outside the theorem.
6. **Do not import separated-floor assumptions.** Raw paid rank48 exceeds minimum target5, so the rmax<kmin separation condition is absent. Source boundary exits and child fresh sources cannot be silently dropped to import a different separated model. The valid general condition here is rmax48<m121.

These controls are hand arguments, not source mutations or observed failures.

## 6. Prior finite observations, significance and limits

PR4476's exact README describes finite checks through2000 and a local3000 observation of `log B/(N log N)` near2, calling it levelling off near2. This review does not re-run or dispute any listed finite values, nor review its full implementation. Those ranks are still at G<=1. A proposed **asymptotic limit2 for exactly this same default canonical policy** is excluded by the proved liminf>3, but a finite plateau is not a claimed limit and is not contradicted. No limit-existence or optimality assertion is made.

The source already supplies the construction, upper exp(O(NlogN)) size bounds and rank-one/compiler count identities. Those retain zxv's/source credit. The additional narrow conclusion is the fixed-policy uniform lower/product/floor analysis and its asymptotic coefficient bracket. Ryanson Jonathan/PR4476 retains its independent finite/slot checks and observations; Jacob Alan Sussman retains the lockstep/multinomial predecessor; all raw inventory/native/compiler authors retain their methods. Other separated, chronological-subexponential or homogeneous-polynomial constructions must be assessed under their own exact policies and are not lower-bounded by this proof.

This is source-aware OpenAI Codex-assisted written review, not a full compiler/word execution, new native census, normalized leaf-saving obstruction, proof-assistant certificate, full paid/physical invoice or selected supplier admission. Changing replication may leave a normalized leaf recurrence unchanged while changing these widths; this theorem does not lower-bound that recurrence or the optimal possible width. Native all-column, ownership/stock, compiler/tape/precision, analytic/outer and all five selected assumptions remain. No kappa/frontier/adoption/merge follows.
