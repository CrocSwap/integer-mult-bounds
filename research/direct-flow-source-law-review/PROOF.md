# Independent source-to-law audit of the capped integer flow

**Verdict: conditional PASS for `Flow.points`, `units`, `demand` and default-height `merged` under the integer domain below.** The actual loops compute the complete finite path-labelled whole-job flow and its mirror histograms, with the stated support/count/rank-mass laws. No flow, source import, constructor, checker, numerical recurrence, compiler or kernel was executed. Inert-file authentication and direct inventory-data addition are reported separately. This is an external code-to-law review of source-claimed identities, not discovery of a new flow or native inventory census, and not the conditional analytic/onset/induction work of PR6723/6728/6729.

Reviewed exact canonical `flow.py` text,8,971 bytes, Git blob07175cd6... as supplied by the coordinator, SHA256 `460f0b0262d7b6880973f46240b3fff1e9f04601fa1d658dda18688b1e26575a`. The source's original proof/check exposure is acknowledged. No author result or floating `approximate_leaves` calculation is adopted. The fixed T/P inventory is a source-data premise; section10 binds its exact dictionary bytes and elementary sums without re-auditing native matrices.

## 1. Precise domain and notation

T and P are finite nonempty dictionaries of strictly positive integer multiplicities. All target keys k and paid keys r are integers, with k>=2 and r>=1. Let K be the sorted target keys, l=min K, m=max K, r_max=max supp(P), and assume integer n with `r_max<m<=n`. Set

`C=floor(n/m)>=1`, `W=sum_k T_k`, `Ptot=sum_r P_r`.

Use only constructor defaults `extra_height=0`, `height_base=None`, so the loop produces the unique G>=0 satisfying `l^G<=C<l^(G+1)`. This includes G=0. These are the requested mathematical entry assumptions; the Python constructor does not itself establish every key/n type or paid-key lower bound for arbitrary foreign objects. No broader input-validation theorem is claimed. Nondefault heights/bases are excluded.

For a nonnegative integer multiindex a of length |K|, write `|a|=sum_i a_i`, `c(a)=product_i k_i^a_i` and

`u_h(a)=h!/product_i(a_i!)*product_i T_(k_i)^a_i` when |a|=h.

All these weights are strictly positive integers on their degree. Different multiindices stay distinct even when their numerical column products coincide. The code matches on the full tuple b, not merely on its rank c(b); only final histograms aggregate equal numerical ranks.

## 2. What `points` and `units` compute

In `points(height,cap)`, a visit at coordinate i has remaining degree h minus the chosen prefix, partial product c, partial tuple a and weight

`product_(j<i) binom(h-sum_(t<j)a_t,a_j)*T_(k_j)^a_j`.

This invariant follows directly from each recursive call. At the final coordinate, remaining0 is exactly |a|=h and the product of binomial factors telescopes to h!/product a_i!. Every multiindex is visited once, so assignment `result[a]=weight` does not overwrite another copy of the same tuple. If a partial product exceeds cap, future nonnegative exponents cannot lower it; k_i>=2 also makes the current `count` loop strictly increasing in product, so `break` safely skips all larger counts. Thus it returns exactly `{a:u_h(a): |a|=h,c(a)<=cap}`. With cap<1 it returns empty; at height0 and cap>=1 it returns just the zero tuple with weight1.

Consequently, for actual d in0..G and positive integer rho,

`U_d(rho)={a:u_(G-d)(a): |a|=G-d, rho*c(a)<=C}`.

This is precisely `units(d,rho)`, because integer rho makes `c(a)<=C//rho` equivalent to the displayed inequality. The point height never goes negative in `merged`: child demand is called only at d<G. All floor reasoning below uses this integer equivalence rather than a continuous approximation.

## 3. Exact demand and capped Pascal inequality

`demand(d,rho)` gives each unit a exactly T_(k_i) target jobs at tuple b=a+e_i. Its count is therefore

`D_d(rho;b)=sum_(i:b_i>0, rho*c(b-e_i)<=C) T_(k_i)*u_(G-d)(b-e_i)`,

with |b|=G-d+1. Counter addition retains every target label and all multinomial multiplicity. These are complete whole-job counts, not fractions or one representative per rank.

For h>=1, the untruncated Pascal identity is

`sum_(i:b_i>0) T_(k_i)*u_(h-1)(b-e_i)=u_h(b)`.

Indeed each summand equals `(b_i/h)*u_h(b)`, and sum b_i=h; equivalently this is the usual integer multinomial recurrence. Positivity of all T ensures that every available summand with b_i>0 is positive.

On a paid edge from(d,rho) to(d+1,rho*r), parent supply at b is either u_h(b) or zero, h=G-d. Child demand is a **subset** of the positive Pascal summands and is at most u_h(b), irrespective of the two cap domains. Hence when parent supply is positive, child demand cannot exceed it. When demand exceeds supply, the supply must be zero, proving the actual `need(supply==0,...)` branch for admissible data. No scalar classification, relaxed rank allocation or omitted job label is needed.

## 4. A complete finite labelled flow

Give each paid rank r its P_r distinct occurrence labels and each target rank k its T_k distinct labels. A path is an ordered sequence of paid occurrence labels of length d, with product rho. At that path place the entire unit batch U_d(rho), with u_h(a) distinct unit occurrences at each tuple a. Each unit has all W target jobs and all Ptot paid jobs. The multinomial weights may be labelled by target words of length h with the corresponding counts, so all multiplicities have a concrete finite interpretation.

There is one child batch per path/paid-letter extension, **not** one child batch per parent unit. At d=0 every demanded target job is an external source. At an internal paid extension, parent jobs at b and the child batch's target slots at b both have rank `e=(rho*r)*c(b)`. Match any fixed ordering of their labels for exactly min(supply,demand) whole jobs. Unmatched parent paid jobs are exits; unmatched child target jobs are sources. At d=G all paid jobs are exits. This is finite because both alphabets and G are finite. It is a whole-integer flow, not a partial/convex relaxation or an emitted physical traversal.

Let L_d(rho) count paid-labelled length-d paths with that product. Then `L_0(1)=1` and

`L_(d+1)(rho')=sum_(rho*r=rho') L_d(rho)*P_r`.

This is exactly the Counter update in `path_counts/following`. Unit/demand data depend only on d,rho, so paths with the same product can be merged by **adding** their multiplicity. They cannot be deduplicated. Each rank's `copies=paths*repetitions` multiplies all its matching/source/exit jobs. The batch is independently used at every paid label; consuming one paid round does not incorrectly subtract units from another round.

The initialization supplies exactly D_0(1). The degree-h union `set(batch)|set(child)` handles both kinds of missing support. Positive parent/absent child produces the full unmatched paid exit. Absent parent/present child produces the whole missing source demand. The nonnegative Counter updates implement the labelled construction exactly, and `+Counter` only discards zero entries; it hides no negative mass or cancellation. `matched_jobs` is the complete multiplicity of the integer min matches, not a rank-weighted sum.

## 5. Exactly which paths may be pruned

If rho>C, every nonnegative column product c(a)>=1 makes U_d(rho) empty, and D_d(rho) is empty too. Every future paid rank is at least1, so every descendant rho' remains>C. All jobs below that branch are empty. Dropping only such a descendant path is therefore safe. The code still computes its child demand and handles current parent paid jobs before pruning its future `following` entry.

An empty current batch with rho<=C is **not** a safe pruning condition: lowering the remaining degree may make later batches present. A hand-derived valid control is T={2:1,5:1}, P={1:1,4:1}, n=20. Here C=4,G=2. The path with first paid rank4 has rho4 at depth1: its degree-one units are empty since even the smallest product gives4*2>4. Nevertheless extending by paid rank1 gives rho4 at depth2, where degree-zero column1 is present; its demand is nonempty. The actual unconditional `following` update for new_rho<=C preserves this case. No execution was needed for this counterexample to the tempting stronger prune.

At terminal depth the code handles **every** paid rank before any following-path test. A terminal parent rho<=C may have rho*r>C and still has real paid exits. For example T={2:1,5:1}, P={4:1}, n=5 gives C=1,G=0, parent rho1 and required terminal exit4; pruning that exit because4>C would be wrong. The implementation's terminal `continue` retains it. Terminal paid ranks are not conditioned to resemble target keys or fall below the column cap.

## 6. Source support and the exact floor boundaries

At root, every demanded b has degree G+1. Its rank s=c(b) is at least l^(G+1)>C. It comes from a unit a with c(a)<=C and one target key k<=m, so s<=mC<=n.

For a nonroot missing source, child demand at b is positive but parent supply is zero. Degree and positive multinomial weights show that parent absence means `rho*c(b)>C`, not a hidden zero coefficient. Thus its source rank `s=(rho*r)*c(b)>C` because r>=1. A positive child demand term comes from a=b-e_i with `(rho*r)*c(a)<=C`, whence s<=k_i*C<=mC<=n.

Every external source therefore has integer `C+1<=s<=n`. Since `n<m(C+1)`, all satisfy the stronger source condition `n<m*s`, without assuming n divisible by m. The sources are nonempty: choose the degree-G column using only the minimum target l; its column l^G<=C and positive weight guarantees at least one root unit, hence positive root demand. This proves both actual source guards. When n=m, C=1,G=0 still works; sources may have rank exactly n. A claim that all n-s are strictly positive would be false.

For fixed T/P, the actual point/unit/demand/path construction depends on n only through C=floor(n/m). Thus the histograms, G, units and column mass are identical throughout each integer bucket mC<=n<m(C+1); the returned n field changes, and mirror complements n-s change accordingly. Every support inequality above was proved for the entire bucket, not only its left endpoint or an assumed multiple of m.

## 7. All paid exits and premature boundary exits

Any exit originates as a paid job of a present unit, so with its parent column a,

`1<=e=r*rho*c(a)<=r_max*C`.

Therefore `m*e<=r_max*m*C<=r_max*n` and e<n because r_max<m. In particular every paid exit is a positive integer strictly smaller than the parent n, including all terminal ranks. These bounds do not require a successful child to exist.

For a **premature** unmatched exit at d<G, positive parent supply u_h(b) exceeds its truncated child demand. The full Pascal identity then has a missing positive term for some i with b_i>0, so

`t=(rho*r)*c(b-e_i)>C`.

Integer t is at least C+1, and e=k_i*t. Hence `m*e>=m*k_i*(C+1)>k_i*n>=l*n`. This proves the strict boundary-exit guard, including edges whose child product exceeds C entirely. Terminal exits need not satisfy this stronger inequality and are correctly excluded from `boundary_exits`.

## 8. Conservation, complete counts and mirror law

For one unit at path rho/column a, let its scalar column mass be rho*c(a). Its complete target rank mass is that number times sum_k k*T_k; its paid rank mass is that number times sum_r r*P_r. Define

`Delta=sum_k k*T_k - sum_r r*P_r`.

Summing over every labelled unit, an internal match cancels the same whole rank e on its paid and target sides. Only external sources/exits remain. Thus, writing S_s and E_e for the final histograms,

`sum_s s*S_s - sum_e e*E_e = Delta*sum_(d,paths,a) u_(G-d)(a)*rho*c(a)`.

The right-hand sum is exactly `column_mass`: the code multiplies by path multiplicity and every multinomial unit count. Its `units` likewise counts all whole units. No positivity of Delta is needed for this identity for arbitrary inventories. A pinned concrete inventory with Delta=608 specializes it to608*column_mass; this proof does not compute or admit that native census.

At depth d, omitting the cap only increases the nonnegative unit count. There are Ptot^d paid-labelled paths and total unconstrained multinomial weight W^(G-d), so

`units<=sum_(d=0..G) Ptot^d * W^(G-d)`.

Each actual unit has W target jobs, and every source is an unmatched one of those jobs, giving `source_count=sum_s S_s<=W*units`. These are full multiplicity bounds, not counts of distinct ranks/classes. All code counters remain integers; `columns` is positive because the root has a present positive unit.

The complete finite mirror histogram can now be stated without making an analytic or native-admission inference. Let a=sum_s S_s>0. For each external source occurrence of rank s, append its complement rank n-s. Keep all exit occurrences. Thus for0<=j<n,

`M_j=E_j+S_(n-j)`, with absent indices interpreted as zero.

All entries are nonnegative integers, and all positive paid mirror ranks are below n. If s=n there is a zero-rank complement: it may be omitted from positive-rank mass bookkeeping, but **its source occurrence must remain in a**. The full target side has a copies of rank n, and

`n*a - sum_(j=0..n-1) j*M_j = Delta*column_mass`.

For fixed Delta608 this is exactly608*column_mass. Equivalently, any permitted downstream cost functional has the formal source-complement/exit expression `sum_s S_s*f(n-s)+sum_e E_e*f(e)` with full source multiplicity a; using that expression as a physical recursion rule needs the separately retained interface/supplier premises. Rank-zero complements do not make those premises free. A labelled matching can be chosen at every edge, but `merged` does not itself emit native scheduling, ordinary control work or a physical traversal.

## 9. G=0, scope and remaining obligations

When G=0, U_0(1) is exactly the zero column once; root demand is the original target inventory and terminal exits are the entire paid inventory. Units=column_mass=1, source_count=W, bound=1, and conservation reduces exactly to the definition of Delta. Boundary exits are empty. The same source/exit/mirror floor arguments cover this case, including n=m and possible zero-rank complements. There is no missing lower-rank leaf or artificial boundary restriction.

The argument establishes the finite code-to-law implication only on the stated integer/default-height domain. It does not certify arbitrary malformed inputs, nondefault heights, a runtime class-limit promise for `literal`, floating `approximate_leaves`, a new native T/P census, actual side-port coupling, paid scheduling/ordinary control price, physical stock/compiler/tape/precision, analytic (H)/tilt/local-limit assumptions, all-rank induction/onset, final multiplication or any selected all-five-assumption discharge. Earlier PR6723/6728/6729 conditional analytic results are distinct. No frontier, kappa or paid-profile change follows.

Credit zxv/source flow and its author checks; Jacob Alan Sussman's separated multinomial construction; the retained lockstep/whole-integer matching/flow and mirror predecessors; and all original notices for the actual fixed inventory/supplier lineage. The missing implication checked here is an external source-aware proof that these loops retain the exact finite jobs and bounds, not a new flow discovery. This work uses substantial OpenAI Codex assistance and is not human or proof-kernel acceptance.


## 10. Exact pinned raw-p7 inventory specialization

The canonical source README already claims the finite construction, chronology, rank-one identity, count bounds and nested compiler width. This audit adds an external check of the actual loops implementing the finite default-domain statement. It does not claim the source theorem or native census as a new discovery. The actual reviewed source custody is canonical main7c49, with the exact blob/SHA above. PR6713 is related analytic context, not the source origin of this canonical file. Earlier review-note shorthand referring to its context is interpreted accordingly.

The pinned original inventory is inputs/p7-RESULT.json.txt, canonical path research/direct-mixed-flow/vendor/p7-RESULT.json, Git blob ebb30a9b3b94fb159a316350f7da57bde4a30c25 and SHA256 9b814be97e3b45fcc28eafa8a65694897a7387f71a14d44796c6aadf303d7fab. Use strictification.targets and strictification.paid, the raw dictionaries; do not substitute the enormous completed/tensor rule described elsewhere in that source artifact.

Targets: {5:420,6:270,7:840,8:1395,9:3195,25:448,41:448,57:448,121:224}.
Paid: {1:37305,2:10695,3:3360,4:1530,5:300,8:1464,16:448,32:448,48:448}.

Direct addition of these pinned integer entries gives W=7688, Ptot=55998, target rank mass131723, paid rank mass131115 and Delta=608, with minimum target5, maximum target121 and maximum paid48. These elementary data sums were checked while preparing the binding; no original or independently implemented flow/census/recurrence checker ran. Every PASS/native/strictification status stored in the original RESULT remains an inherited source assertion, not re-executed evidence.

Consequently the proved finite code law specializes, for every integer n>=121 under the default entry premises, to source mass minus exit mass=608*column_mass and to the full complement mirror law of section8. It does not derive the native census from matrices, establish chronological adapter/owner correctness or admit the selected P104 supplier.

As a written endpoint control, for121<=n<=604, cap lies in1..4 and G=0. Therefore sources=T, exits=P, units=column_mass=1, source_count7688, matched_jobs0 and boundary_exits empty. In particular paid rank48 must be retained even when cap=1. These are hand-derived consequences of G=0, not a new measured fixture.

## 11. Integration qualifications and independent written controls

Do not mutate the object inventories or exposed cached dictionaries during this claim; the source API does not make those objects immutable. Integer keys exclude zero/negative/nonintegral foreign data; paid keys are >=1. This is a theorem on the explicit domain, not an arbitrary-input validator or a request to harden its API. The mathematical unbounded path mirror is distinct from the actual literal method's default200000 class guard: no all-n successful literal invocation is promised.

The complete cancellation can also be stated at every individual rank, or for any test function f on the finite support:
sum_s S_s f(s)-sum_e E_e f(e)=sum_units weight*(sum_k T_k f(kz)-sum_r P_r f(rz)).
This follows by cancelling the same matched whole rank before aggregation. For f=1 it gives source_count-exit_count=(W-Ptot)*units; for f(x)=x it gives the displayed rank-one law. No scalar mass flag alone authenticates a complete output histogram.

The following independently sealed adversarial controls are written and UNEXECUTED:
1. **Empty parent, nonempty child.** T={2:1,4:1}, P={1:1,3:1}, n16 gives C4,G2. At depth1,rho3, degree1 batch is empty because floor(4/3)=1. Its paid-r1 child has a degree0 unit, whose demand creates sources6 and12. That subtree also has paid exits3 and9. Pruning the empty batch changes the prescribed mirror. Deleting an entire zero-incoming closed subtree can leave a mass identity self-consistent, so conservation alone does not certify faithful construction.
2. **Keep terminal rank48.** At n=m, C1,G0. Root units consist of one zero vector; source histogram is T and exit histogram is all of P. If P48>0, exit48 must remain even though48>C. Dropping it changes the conserved mass by48*P48 with column_mass still1. For a standalone valid example use T={2:1,49:1},P={1:1,48:1},n49: source mass51, exit mass49, Delta2. Dropping exit48 gives the wrong difference50.
3. **Do not divide before multiplying Pascal weights.** T={2:1},P={1:1},n8 gives C4,G2. Parent b=(2) has u_2=1 and true child demand1. Computing `(u_2//2)*b_1` instead yields0. The actual code uses binomial terms and has no such division.
4. **Do not erase multiplicity or multinomial order.** T={2:1,3:1} gives u_2(1,1)=2, not1. Treating paid P={1:2} as a set loses one paid round; at n=m=2,T={2:1}, true Delta0 and two exits1 balance source2, whereas one exit gives difference1.
5. **Do not use a single-level unit budget.** T={2:1},P={1:1},n8 has one unit at each of G+1=3 depths. W^G=1 is not the full count; the source sum gives3. Equal P/W is a real case, not a removable denominator.
6. **Do not replace per-round matching by a global pool.** Abstract two paid positions with supplies2,0 and demands1,1 have per-position matched total1 plus one exit/one fresh source. Pooling totals before min matches2 and hides both. This is a control against changing the model/chronology, not an asserted concrete source run or a native scheduling theorem.


The empty-parent control is especially important: deleting a closed zero-incoming subtree can alter every required histogram while leaving a reduced source/exit/column mass identity internally self-consistent. A later finite audit must compare complete histograms and counts, not merely the surplus flag. No follow-up execution is reserved by this written package.

The original formal-interface-lemma task card's formalized certificate/proof-assistant and complete-interface acceptance gate remains unmet. Its scope was explicitly narrowed to source-aware written review. All five selected assumptions and the frontier remain unchanged. Source authors retain the finite construction/theorem, native inventory and compiler/analytic claims; this package adds external code-to-law review only.
