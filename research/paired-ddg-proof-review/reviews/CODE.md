# Independent proof-to-controller audit of PR6072

## Verdict, scope and exposure

PASS under the fixed nonadaptive-law and trusted-controller/bit-input contract stated below. No material discrepancy was found between the retained README's DDG proof and `make`, `census`, and `run` in `verify.py`. This is a separately written, source-aware AI audit of existing source claims, not a new sampler/count theorem, source-blind discovery, human review or formal-kernel acceptance.

Read only the byte-bound inert inputs README.md, verify.py and LICENSE from source9011bf83/canonical7c49 custody supplied by the coordinator. No source or new scientific program, constructor, census, import, compilation, test, numerical experiment or proof kernel was run. No peer draft was read before sealing this note. Source312-state/624-transition/702-byte figures and reported means are author-side certificates; the structural arguments below explain those claims without executing their catalogue. Actual numerical-join work in6096/6546 is known separate context, not a missing-global-coverage claim made by this audit.

The allowed law has genuine integer a,b in1..12, both fixed and known before this call reads any entropy. It starts in the one deterministic root control state, uses independent unbiased bits independent of those fixed parameters, and has no other initially random state or free entropy reservoir. The table must be the valid table returned for that parameter pair. The exact law is for one two-decision invocation, not a claim about adaptive rounding, entropy recycling across a sequence, inverse-service cleanup, worst-case latency, actual random-tape access cost or a native caller.

## 1. Product law and the exact unfinished-prefix invariant

`make` rejects bool as well as other non-int/out-of-range parameters by exact type checks. It defines the four positive weights in label order00,01,10,11 as

    ((13-a)(13-b), (13-a)b, a(13-b), ab).

Their sum is169. The source's marginal equalities associate label2/3 with first bit1 and label1/3 with second bit1. Their determinant equality, or direct division by169, gives precisely the product Bernoulli law. Correct marginal sums alone would not imply that product law. Every factor lies in1..12, so each weight is a nonzero unit modulo169 and is below169.

Let r_i(k) be the least positive residue of 2^k*w_i modulo169. Then

    n_k = sum_i r_i(k)/169
        = 2^k - sum_i floor(2^k*w_i/169).

The residue sum is a positive multiple of169, strictly below4*169, so n_k is1,2 or3. Initially r_i(0)=w_i and n_0=1. The next binary probability digit is

    d_i(k+1) = floor(2*r_i(k)/169),

which is0 or1, and residue doubling gives

    n_(k+1) = 2*n_k - sum_i d_i(k+1).

These are exactly `residues`, `counts` and `digits` in `make`. In particular a phase indexed by k must use residues at k to supply the digit at depth k+1; shifting it by one is not a harmless relabelling.

At depth k, index the n_k unfinished prefixes by j=0,...,n_k-1. The new child numbers x=2*j+bit are all distinct and range over0,...,2*n_k-1. Subtracting the four digits in output order first returns i exactly at the child number allocated to its one new leaf when d_i=1. Digits0 allocate no child. If no return occurs, the remaining index is x-sum_i d_i and ranges bijectively over0,...,n_(k+1)-1. The recurrence ensures no level is overfilled and no remaining index is missing.

Consequently the controller's labels are not just aggregate counts: each unresolved binary prefix maps to exactly one index and vice versa at every fixed depth. A label i is interpreted as its two output bits, so the complete four-output vector, not only its two marginals, is the checked object.

## 2. Period, phase155→0, and a structural explanation of312

The source checks the exact order156 numerically in its retained verifier. It also has a short written check. Modulo169, repeated squaring gives

    2^12 = 40,  2^13 = 80,  2^26 = -22,
    2^39 = 99,  2^78 = -1,  2^52 = -23.

Here equality denotes congruence. The fourth equality follows from(-22)*80 modulo169 and the fifth from99^2=9801=58*169-1. Thus2^156=1. For the prime divisors2,3,13 of156, the powers2^78,2^52,2^12 are all different from1, proving the order is156. This arithmetic was derived on paper, not obtained by running `pow` or the source.

All r_i and n_k therefore repeat with period156. More strongly, since every weight is a unit,

    r_i(k+78)=169-r_i(k),
    n_(k+78)=4-n_k.

Pairing the78 opposite phases proves

    sum_(k=0)^155 n_k = 78*4 = 312.

This gives a uniform structural reason for the source's already stated exhaustive312 count; it is not a newly discovered count or a new catalogue. It also shows that the hard-coded output base312 does not accidentally collide with an internal state for any allowed pair.

`states` is ordered first by phase and then node, so its first state is(0,0) and has ID0. Every state ID is in0..311. At phase155, any surviving child has phase156 reduced to0 and node index in0..n_156-1. Since n_156=n_0=1, that index is exactly0. Thus the literal `(phase+1)%PERIOD` transition is the correct return to the unique root, not a free restart or a discarded residual branch. Reaching it has consumed156 actual bits. Before that wrap, every continuing transition advances one phase. Reusing the root at different depths does not merge different unresolved prefixes at the same depth; the invariant above retains their one-to-one correspondence.

There are two entries per312 internal states, hence624 transitions. The four output targets are312..315, so all targets fit in9 bits. A fixed packed transition payload therefore contains624*9=5616bits=702bytes. This is a logical packed-table calculation. The Python tuple/list representation does not itself occupy702bytes, and this does not include table selection, dispatch, parameters, random tape or a physical local-access implementation.

## 3. `census` and `run` implement the same chronological tree

`census` first validates the312-by2 table shape and genuine integer targets0..315. It starts only state0 with multiplicity1. When a prefix has already returned, multiplying `done` by2 counts both extensions to the next fixed depth; it does not charge those unused suffix bits to the stopped sampler. For active prefixes, both table branches contribute to the next active state or the designated output. Thus `done[i]` is the number of length-k binary strings whose sampler has completed at or before k with label i, not merely the number of leaves first terminating at k.

The digit recurrence gives, at every depth,

    done_i(k)=2*done_i(k-1)+d_i(k)
             =floor(2^k*w_i/169).

The total completed and unfinished counts exhaust2^k. The controller index argument gives multiplicity1 at every active state and exactly n_k such states. These are the quantities tested in `census`. Its finite312-depth checks corroborate the periodic construction but are not, by themselves, a universal-depth proof; the phase/index invariant supplies that bridge.

`run` starts the same ID0, uses exactly one input bit to select one table entry, returns the corresponding output immediately if it is312..315 and otherwise advances to the designated internal ID. Its `used` counter is the number of consumed bits, not an implementation-transition tariff. The eight-bit enumeration in source `main` exhausts256 tapes per parameter pair; early outputs are repeated over all unused suffix completions, exactly matching the completed-prefix convention in `census`. This audit did not rerun that enumeration.

The low-level `run` does not validate arbitrary table/bit inputs. Its source caller uses valid `make` tables and finite tuples from `product((0,1),repeat=8)`. Python bool or negative integers may act as sequence indices, and malformed values may raise non-ValueError exceptions; no defensive arbitrary-input API or hostile-packet guarantee is claimed. The probability theorem requires literal unbiased0/1 bits and a valid fixed table. `census` similarly receives its weights and positive depth from the trusted source path. These caller qualifications are not sampler counterexamples or reasons to modify the source in this review.

## 4. Exact all-depth law, stopping and expectation

At depth k the unfinished probability is n_k/2^k<=3/2^k. It tends to zero, proving almost-sure termination. For each output, completed mass tends to w_i/169; hence the actual full joint output law is exactly the stated independent product, including arbitrary nonzero a,b in the domain. This is not an inference from finite eight-bit frequencies.

For a nonnegative integer bit count T with at least one bit consumed,

    E[T]=sum_(k>=0) Pr(T>k)
        =sum_(k>=0) n_k/2^k.

Partitioning k into periods156 gives exactly the source's displayed rational expression. A return to root after156 bits is a surviving branch of probability2^-156 and costs those bits; the geometric denominator does not grant a new free seed or erase that work.

The source's coarse uniform inequalities also have a short structural justification. Since n_k>=1 and n_78=4-n_0=3, the expectation is strictly larger than sum_(k>=0)2^-k=2. Since n_0=1, n_1<=2 and n_k<=3 for k>=2,

    E[T] <= 1+2/2+sum_(k>=2)3/2^k = 7/2.

The inequality is strict, for example because n_156=1 rather than3 in the bounded tail. These arguments explain the existing source bound; they do not replace the unexecuted source's exact min/max or `(1,1)` rational certificate with a newly computed one. The claimed `(1,1)` mean and its9/4 comparison remain credited to the retained source certificate rather than a fresh arithmetic replay here.

At every finite depth n_k>=1, so there is positive probability of consuming more bits. This is an unbounded stopping sampler implemented by a finite control graph, not a finite draw cap or worst-case latency theorem. A finite `run` test may return None on tape exhaustion; that is unresolved sampling, not a fifth output that can be silently coerced to00.

## 5. Expected-bit optimality association

Any exact decision procedure under the same fixed-law/unbiased-bit/no-free-initial-entropy contract unfolds into a binary decision tree. At fixed depth k, completed output-i mass is an integer multiple of2^-k and cannot exceed w_i/169, since all future output masses are nonnegative. Thus it has at most floor(2^k*w_i/169) completed prefixes for that output and has unfinished probability at least n_k/2^k. Summing nonnegative tail terms lower-bounds its expected number of consumed bits by the source's value, whether or not its expectation is finite.

The literal source controller saturates every one of those depthwise bounds by Sections1–4. It is therefore optimal for exactly that joint law and objective. This does not prove optimal physical runtime/storage/table-access cost, require optimal standalone trees to be executed separately, or rule out different amortized contracts with entropy carried between calls. Correct independence of the two decisions is a property of the four masses, not independence from the random tape consumed to obtain them.

## 6. Written adversarial controls — all UNEXECUTED

1. **Phase off by one.** Derive current digits from residues at phase+1 instead of phase. For a=b=1, the root's weights are144,12,12,1. The true first two depth digit vectors both allocate one00 child, whereas phase2's vector allocates none. The altered construction misses the second-depth00 prefix10 and fails the exact prefix invariant. This is a hand trace, not a recorded mutation run.
2. **Root revisit is not free.** Returning00 rather than continuing at the surviving phase156 root forces termination by156. The real unresolved probability there is2^-156 and a finite capped tree cannot realize the positive non-dyadic output masses exactly. Likewise resetting every unresolved transition to root erases phase and can make all outputs00 rather than the product law.
3. **Node indexing.** Replacing `2*node+bit` by `node+bit` merges the children of neighboring indices. A phase with multiple unfinished nodes exists (n_78=3), so the unique-prefix/index invariant fails. Retaining only one unfinished node or allocating `range(n+1)` likewise loses or invents states; the output-ID base312 cannot merely be kept while changing that count.
4. **Labels, including unequal parameters.** Swapping01 and10 may be invisible at a=b. For the allowed a=1,b=2 the weights are132,24,11,2; the swap exchanges unequal middle masses and their required marginals. A control suite checking label order should include unequal parameters rather than only the symmetric example. The source catalogue does include unequal pairs, but it was not run here.
5. **Marginals with wrong joint law.** At a=b=1, reuse a single Bernoulli1/13 flag for both decisions. Both marginals remain1/13 but the11mass is1/13 rather than1/169. This is the source's stated false-independence contrast. Its final constant inequality checks that arithmetic contrast, not an executed correlated sampler. The full four-output census is the substantive gate that would discriminate an actual changed table implementing the wrong law.
6. **Initial entropy.** Starting with an already randomly selected output (or a secretly random initial controller state) can consume fewer newly charged bits. That changes the contract: it gives free initial entropy. All root/optimality claims require the one fixed initial state and charge every consumed fair bit.
7. **Adaptive second probability.** Choosing b from the first returned decision makes the second conditional law depend on that result. A single table constructed from a fixed b does not certify such a caller, even if each separately selected b lies in1..12. The source explicitly excludes that application.
8. **Finite tape versus completion.** Treating `run(...,bits)` returning None as an ordinary output or claiming finite control implies bounded draws changes the exact law/latency contract. The source's n_k>=1 and positive survival after one period directly contradict the proposed cap.
9. **Malformed bits / trusted helper.** An input-API claim accepting arbitrary integers as bits would be unsupported: `-1` is a valid Python row index and2 is out of bounds. This is outside the valid0/1 source path, not an alleged source theorem defect. A future external packet interface would need its own typed validation and failure contract.

## Remaining obligations and credit

No code correction is requested. The audited construction, current-row output labels and phase wrap implement the written law on the valid fixed table/bit domain. The uniform312 explanation and bounds above are structural written corroboration of source claims, not independently executed census results or priority claims.

Actual service integration still needs a caller that exposes both nonadaptive residue probabilities before either result is consumed, exact parameter/table selection, physical table and random-bit movement, output ownership, stopping-record retention, reversible/dirty-state cleanup and a complete cost/error budget. No such caller or full supplier is established by a logical entropy reduction. Existing separate6096/6546 numerical joins are not displaced or declared absent. All selected native/caller/compiler/tape/analytic and outer obligations, and the selected frontier, retain their status.

Credit zxv6072's catalogue, source verifier and claims; JoyboyBrian5069/5037 inverse-service lineage; Nick Petalas6026 stochastic-prefix context; the retained original notices/license. Dyadic distribution-generation trees and depthwise expected-bit optimality are classical, and their ownership is not reassigned by this review. Substantial OpenAI Codex assistance produced this external source-aware written note; no human or formal acceptance is implied.
