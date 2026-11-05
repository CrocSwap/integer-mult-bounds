# Independent written review of Flow.merged

Verdict: **conditional PASS for the exact default integer flow and its symbolic conservation/support/unit bounds**. No peer derivation was read before sealing this note. I read only the pinned flow.py text, not a source checker, numerical recurrence result, finite census implementation or peer engine. No program/import/constructor/test/numerical or proof-kernel execution occurred. Metadata reads/hashes are not scientific runs.

Exact source text:8,971 bytes, Git blob `07175cd6e1f2c2367c2e78eca7f163fef18d301d`, SHA256 `460f0b0262d7b6880973f46240b3fff1e9f04601fa1d658dda18688b1e26575a`. The current task refers to PR6713's released analytic source, but actual fixed T/P profile bytes were not yet supplied to this reviewer. Therefore the review establishes the symbolic Delta formula below; the numeric specialization Delta608 must be separately bound to its exact dictionary bytes and arithmetic. Source authors already claim these identities; this is external review, not their discovery.

## Domain and exact lattice weights

Use finite nonempty target/paid dictionaries on positive integer ranks, target ranks k>=2 and paid ranks r>=1, positive integer multiplicities T_k,P_r. Put k0=min target, m=max target, rmax=max paid<m and integer n>=m. Fix the **default** height_base=k0 and extra_height=0. No dictionary mutation occurs during construction. Unsupported zero/negative/noninteger/bool/API inputs or arbitrary height overrides are not counterexamples to this fixed-domain theorem.

Let C=floor(n/m)>=1 and choose G so `k0^G<=C<k0^(G+1)`. For a nonnegative target exponent vector a, write `|a|=h`, `c(a)=prod k^a_k` and

`u_h(a)=h! * prod(T_k^a_k/a_k!)`.

The recursive binomial factors in points telescope to this multinomial integer. The early break in the count loop is sound because every target k>=2, so c grows monotonically with that count. At depth d and paid-product rho, the unit batch is exactly

`U(d,rho)={a: |a|=G-d, c(a)<=floor(C/rho)}`, with multiplicity u_(G-d)(a).

Nested integer division is exact: `floor(floor(n/m)/rho)=floor(n/(m*rho))`. This follows directly from Euclidean remainders and needs no real approximation or divisibility of n by m*rho. Unit rank rho*c(a) is at most C, including equality.

For |b|=h+1, demand is the truncated Pascal sum `D(b)=sum_i T_i*u_h(b-e_i)` over present predecessors. This is a sum of whole integer jobs, not fractional lending or a rounded multinomial coefficient.

## Parent supply versus child demand

Consider a nonterminal parent at depth d, paid rho and target degree h=G-d>=1, followed by paid rank r. Parent supply at b is u_h(b) if c(b)<=floor(C/rho), otherwise zero. Child demand at the same exponent vector uses degree h-1 units and cap floor(C/(rho*r)). The untruncated identity is

`sum_i T_i*u_(h-1)(b-e_i)=u_h(b)`.

Termwise it equals `(b_i/h)*u_h(b)`, but the code correctly evaluates integral multinomial terms rather than dividing u_h by h first. Since truncation deletes nonnegative terms, child demand never exceeds present parent supply. If demand exceeds supply, supply must therefore be absent/zero, exactly the source assertion. A zero parent batch or absent b does **not** imply zero child demand: smaller-degree units can reappear.

The code matches min(supply,demand) whole jobs at rank `e=rho*r*c(b)`, retaining positive supply differences as paid exits and positive demand differences as new sources. Multiplying each by the positive paid-path/round multiplicity preserves these identities.

## Support and strict endpoints

At initial root demand, sources have degree G+1, hence rank at least k0^(G+1)>C. Their predecessor unit has c(a)<=C and the extra target k<=m, so source rank<=m*C<=n.

For any later new source, absent parent supply means rho*c(b)>C. Since r>=1, e=rho*r*c(b)>C. A present child-demand term has c(b)/k_i<=floor(C/(rho*r)), so e<=k_i*C<=m*C<=n. Thus every source is an integer in(C,n], and in particular **m*source>n**. The default root batch contains the all-k0 vector, with positive multiplicity, so sources are nonempty for every n>=m.

Every nonterminal exit comes from a parent unit, hence e=r*rho*c(b)<=rmax*C. At terminal depth h=0, the only possible batch exponent is zero; each paid rank still creates exit e=rho*r. It satisfies the same bound because the terminal unit exists only if rho<=C. Consequently all paid exits are positive, satisfy m*e<=rmax*n and are strictly less than n since rmax<m.

For a premature boundary exit, a positive Pascal term is missing: for some i with b_i>0, `c(b)/k_i>floor(C/(rho*r))`. Integer arithmetic gives `rho*r*c(b)/k_i>=C+1`, so `m*e>k_i*n>=k0*n`. This proves the strict boundary inequality even when n is not divisible by m. No equality/floating endpoint may be substituted.

## Multiplicity, safe pruning and mirror order

At fixed depth, path_counts[rho] is the multiplicity of ordered paid words with product rho, including each rank's repetition count. Same depth/rho gives identical local batches and child demands. The code processes each edge's supply/demand difference **before** combining subsequent path counts. It does not globally pool excess jobs from different rounds to cover a later shortage. After missing inputs are supplied, every child runs its full prescribed units independently of the particular incoming subset, so its future histogram contribution depends only on depth/rho and can be combined linearly.

Pruning only rho>C is sound: positive paid ranks cannot decrease rho, all descendant caps are zero, and units plus demand remain empty. The code still computes current edge exits before dropping the future class. At terminal depth it iterates **all** paid ranks before any following-class test. C caps unit columns, not paid job ranks; exits above C must remain. Empty-batch pruning is not equivalent: descendants with smaller target degree can be nonempty while rho<=C.

The source literal routine explicitly returns the entire child and unmatched paid jobs before issuing the next parent paid position. Its histogram is therefore matched by the mathematical unbounded ordered mirror described above, without claiming simultaneous physical execution. The actual `literal(...,class_limit=200000)` method has an explicit finite class guard: do not claim it successfully returns for all n under that default cap. The all-n comparison is to the mathematical mirror, or conditional on the literal guard not firing, not a new execution result.

## Conservation and full unit bound

Let `Delta=sum_k k*T_k - sum_r r*P_r`. Every unit at scale rho*c(a) has target rank mass minus paid rank mass equal to Delta*rho*c(a). Every matched edge removes the same rank e with the same whole-job multiplicity from one target demand and one paid supply. Summing these exact cancellations leaves precisely sources minus paid exits. Thus

`mass(sources)-mass(exits)=Delta*column_mass`.

Here column_mass is the sum of actual unit scales with their multinomial/path multiplicities, exactly the code's columns accumulator. This identity does not require positive Delta; positivity for a chosen profile is an additional numeric specialization. Counter unary-plus removes zero entries only on this nonnegative construction, not an unpaid negative balance.

Write W=sum T_k and P=sum P_r. Total surviving paid-path multiplicity at depth d is at most P^d, and total capped unit coefficient at that depth is at most W^(G-d) by the multinomial theorem. Therefore

`units<=sum_(d=0..G) P^d*W^(G-d)`.

Each unit has W target jobs; unmatched sources are a subset of all target occurrences after cancellation, so `source_count<=W*units`. Also every unit scale<=C gives column_mass<=C*units. The finite sum is valid when P=W; replacing it by a formula dividing by P-W would need a separate equal case. No empirical n cutoff or integer inventory relaxation is needed for these symbolic statements.

## Written adversarial controls — none executed

1. **Empty parent, nonempty child.** T={2:1,4:1}, P={1:1,3:1}, n16 gives C4,G2. At depth1,rho3, degree1 batch is empty because floor(4/3)=1. Its paid-r1 child has a degree0 unit, whose demand creates sources6 and12. That subtree also has paid exits3 and9. Pruning the empty batch changes the prescribed mirror. Deleting an entire zero-incoming closed subtree can leave a mass identity self-consistent, so conservation alone does not certify faithful construction.
2. **Keep terminal rank48.** At n=m, C1,G0. Root units consist of one zero vector; source histogram is T and exit histogram is all of P. If P48>0, exit48 must remain even though48>C. Dropping it changes the conserved mass by48*P48 with column_mass still1. For a standalone valid example use T={2:1,49:1},P={1:1,48:1},n49: source mass51, exit mass49, Delta2. Dropping exit48 gives the wrong difference50.
3. **Do not divide before multiplying Pascal weights.** T={2:1},P={1:1},n8 gives C4,G2. Parent b=(2) has u_2=1 and true child demand1. Computing `(u_2//2)*b_1` instead yields0. The actual code uses binomial terms and has no such division.
4. **Do not erase multiplicity or multinomial order.** T={2:1,3:1} gives u_2(1,1)=2, not1. Treating paid P={1:2} as a set loses one paid round; at n=m=2,T={2:1}, true Delta0 and two exits1 balance source2, whereas one exit gives difference1.
5. **Do not use a single-level unit budget.** T={2:1},P={1:1},n8 has one unit at each of G+1=3 depths. W^G=1 is not the full count; the source sum gives3. Equal P/W is a real case, not a removable denominator.
6. **Do not replace per-round matching by a global pool.** Abstract two paid positions with supplies2,0 and demands1,1 have per-position matched total1 plus one exit/one fresh source. Pooling totals before min matches2 and hides both. This is a control against changing the model/chronology, not an asserted concrete source run or a native scheduling theorem.

## Limits and credit

I found no default-domain floor, support, conservation, multiplicity or pruning defect. This does not certify unsupported API inputs, arbitrary extra heights, mutation of cached dictionaries, large literal class budgets, numerical floating approximate_leaves, analytic root saving, actual finite census counts or a selected native/physical/paid supplier. The exploratory floating recurrence is explicitly outside acceptance. Fixed-profile Delta608 and its rank48 entry must be tied to exact source dictionaries; they are not inferred from this generic file. All five selected assumptions and kappa/frontier/adoption/merge remain unchanged.

Credit zxv and retained contributors for this whole-integer capped flow; Jacob Alan Sussman for the separated multinomial predecessor; the actual census/caller and analytic contributors retain their source claims. Earlier B11 PR6723/6728/6729 conditional local-limit/tilt/full-flow reviews are not recounted. This is source-aware OpenAI Codex-assisted written review, not a new conservation theorem, scientific execution or human/kernel acceptance.
