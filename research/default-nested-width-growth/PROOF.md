# Uniform width growth of the one old nested policy

**Result: the exact default raw-p7 nested widths have log B_N=Theta(N log N). Moreover their normalized logarithm has liminf at least log_5(420)>3, so it cannot converge to2.** This is a statement about the single policy `a_n=B_(n-1)` in the pinned `compile_counts`, not a new width policy, optimum or lower bound for compilers generally. No scientific execution, import, constructor, numerical program, checker or kernel was used. Source code/prose and old finite evidence were read, not rerun.

The fixed inputs are the canonical raw p7 dictionaries from `strictification.targets/paid`, not their tensor-power encodings or a new native census. They have minimum target5 with multiplicity420, maximum target m=121, total target multiplicity W=7688, total paid multiplicity P=55998, maximum paid48 and given rank surplus608. In particular P>W and all hypotheses of the default finite Flow laws hold. The original construction, source upper bound and empirical prefix checks retain their authorship.

## 1. Actual recurrence and its domain

The pinned canonical `verify.py`, Git blob `df9ca12ad0dae5437ed7d65688e962b9abda5af4`, SHA256 `9ae067eadf17ff9d97737805eb642a69375a5ff2ddb08988fef59aa0771f9b7c`, initializes every B_e=1. For integer n>=121 it obtains the complete `Flow(T,P,n).merged()` and, with `force_unit_replication=False`, assigns

`a_n=B_(n-1)`, `B_n=a_n*S_n`, `S_n=flow.source_count`.

Thus for every integer N>=121, with M=N-120,

`B_N=product_(n=121..N) S_n`.

This is actual source assignment, not a recurrence fitted to saved widths. Below121, including rank zero, B_e=1. Every S_n is a positive integer by the source-to-law result. Hence by induction all prior B_e divide B_(n-1), exactly as the code's whole-batch check requires; all recursive complement/exit ranks lie in0..n-1. A source of rank n has complement0. Its source multiplicity remains in S_n even though the zero-dimensional complementary subprogram has no paid leaves. Deleting such sources would change this policy and invalidate the product.

The other compiler guards do not impose an unproved eventual stopping rank. Their existing induction follows from the finite flow laws: base paid leaves equal e, base unit/column/slot counts are zero, and mirror rank balance gives `B_n*n-leaves_n=608*columns_n`. Nonnegative leaves and positive integer columns give `units_n<=columns_n<=B_n*n/608`. Source-count<=W*local_units and exit-count<=P*local_units imply the local slot allowance<=2(W+P)*local_units, and the same inequality propagates through the nonnegative lower-rank batch recurrence. This is the credited nested/slot argument, not a new slot identity; PR4476 supplies the sharper exact matched-slot accounting. Finally `sum_(d=0..G)P^d W^(G-d)<=(P+W)^G` and monotonicity of G bound all earlier S_n by the source's C_N, proving its final `largest_sources`/width envelope guards. The width recurrence is consequently well-defined at every finite N on these mathematical integer inputs, without a practical materialization claim. This is a statement about the code's specified exact-integer count recurrence under sufficient mathematical resources. It does not assert that a fixed Python host can allocate, serialize, or finish every finite N; memory, generation time, integer/byte serialization and physical execution remain separate.

## 2. A lower and upper factor for every rank

Put C=floor(n/121) and let G=G(n) be the default height. Since the minimum target is5,

`5^G<=C<5^(G+1)`, equivalently `121*5^G<=n<121*5^(G+1)`.

At the root, the degree-G column containing only target rank5 is present and has column5^G and weight420^G. `points` gives exactly this weight; the multinomial factor for a single repeated letter is1. Every one of those root units supplies all W target slots to initial demand. Initial root demands are external sources and the code only adds later sources, never cancels this initial histogram. Therefore, including G=0,

`S_n>=W*420^G`.

The full integer unit/source bounds, with **multiplicities rather than support sizes**, give

`S_n<=W*sum_(d=0..G) P^d*W^(G-d)`.

Since P>W, the exact sum equals `(P^(G+1)-W^(G+1))/(P-W)` and is at most `P^(G+1)/(P-W)`. Consequently

`W*420^G <= S_n <= (W*P/(P-W))*P^G`.

No physical/native premise is inferred from these integer inequalities. The upper bound improves the very loose source envelope for this analysis but is not a newly optimized compiler. The lower bound uses the root batch that this specific algorithm always retains; another policy or matching/replication scheme need not satisfy the resulting B_N product.

## 3. Exact finite-N sandwich and floor sum

Let `H_N=sum_(n=121..N)G(n)`. Multiplication of the preceding per-rank factors gives the integer-form sandwich

`W^M*420^H_N <= B_N`,
`(P-W)^M*B_N <= (W*P)^M*P^H_N`.

Here P-W=48310>0, so no inequality reverses. There are no rounded logarithms, floating quantities or hidden denominators in this finite statement.

For g=G(N), count each threshold separately:

`H_N=sum_(j=1..g) #{n:121<=n<=N, n>=121*5^j}`

`=sum_(j=1..g)(N-121*5^j+1)`

`=g*(N+1)-121*(5^(g+1)-5)/4`.

The numerator divided by4 is integral because5 is1 modulo4. For121<=N<=604, g=0 and H_N=0; in fact every flow there has height zero, S_n=W exactly and `B_N=W^(N-120)`. At N=605 the formula gives H_N=1. At N=3024 it gives2420 and at N=3025 it gives2422, correctly adding a new rank of height2. These are hand-derived threshold checks, not executed width fixtures. They cover the floor cases without replacing floor(n/121) by n/121.

## 4. Uniform asymptotic consequence

The threshold bounds give

`g=log_5(N)+O(1)`.

Also `121*(5^(g+1)-5)/4<=5N/4`, so the exact formula implies

`H_N=N*log_5(N)+O(N)`.

For example the displayed subtraction is O(N), g*(N+1)-g*N is O(log N), and the bounded error in g contributes only O(N). Hence `H_N/(N*ln N)->1/ln5`.

Taking natural logarithms of the finite sandwich and dividing by N*ln N gives

`liminf_(N->infty) ln(B_N)/(N*ln N) >= ln420/ln5 = log_5(420)`,

`limsup_(N->infty) ln(B_N)/(N*ln N) <= ln55998/ln5 = log_5(55998)`.

The constant M*ln W and M*ln(WP/(P-W)) terms vanish after this normalization. Since `420>5^3=125`, the lower endpoint is strictly above3, and thus above2. The positive finite upper endpoint proves the two-sided growth assertion `ln B_N=Theta(N ln N)`, or `B_N=exp(Theta(N ln N))`. This does **not** prove that the normalized ratio has a limit or that either endpoint is sharp. The ratio is unchanged if both logarithms use any one other base; when the denominator also uses log_2(N), replacing log_2(B_N) by the integer bit length changes the normalized ratio by a vanishing error. If the denominator remains N*ln(N), conversion of the numerator to bits introduces the factor1/ln2; it is not a vanishing change.

## 5. Exact relation to prior finite evidence

The retained canonical PR4476 README, Git blob `c6db026010b7e2ec8a4063065c4d054401cfc9cd`, SHA256 `0563dd22edeba4ee82a5ac4a06d965ccb90edbb09bbe646c9f21497bd4789f76`, explicitly labels its scope finite ranks121..2000 plus a local3000 run. It reports normalized growth values1.094,1.756,1.965,2.033 and2.066 at500,1000,1500,2000 and3000, and offers the empirical interpretation “levelling off near 2.” This review does not recompute or dispute any of those finite values. In particular G(3000)=1, before the first height2 threshold3025. Such observations cannot imply a limiting constant2; the uniform root-batch lower bound rules that out for this one default policy.

PR4436 already proves the O(N log N) logarithmic upper envelope for nested divisible widths. PR4476 already independently checks finite width factors and proves an exact slot identity. The present additional implication is the uniform all-N root-batch lower bound and explicit H_N sandwich/asymptotic obstruction to a2 limit. It is not a new discovery of the old upper order and not a rejection of the previous finite check. Duplicate/priority assessment remains the coordinator's live-overlap process; this note claims no global priority.

Policies in PR4507/4586 use different chronological/replication constructions and are outside this lower bound. PR6612's homogeneous-gcd polynomial policy is different. A separated-floor statement such as PR5318 cannot simply be transferred to this raw overlap inventory, where paid max48 exceeds target min5. No lower bound for arbitrary valid replication choices, alternative compilers, selected suppliers, tensor lifts or multiplication follows from analyzing this product policy.

## Scope and credit

Only inert canonical text was read. The seven-source manifest now contains134,692 bytes, with the original six-source version preserved before adding PR4476 context. Actual compile_counts, source verify, Flow, saved outputs and native suites were not imported or executed. Prior S8 flow laws and S9 finite complete-output checks support different obligations and are not recounted as this result. The mathematical inventory is given; no native census, physical realization or analytic/formal admission occurs here. The original formal/certificate card gate remains unmet; no Lean/kernel theorem, full selected/all-five-assumption discharge, new kappa or frontier change is claimed.

Credit zxv/PR4436 for the nested construction and upper envelope, Jacob Alan Sussman for the lockstep/multinomial lineage, Ryanson Jonathan/PR4476 for finite widths and exact slot accounting with its disclosed Claude assistance, the raw-p7 supplier/strictification authors and retained notices, and S8/S9 for the bounded precursor obligations. This proof review uses substantial OpenAI Codex assistance and does not claim independent human or proof-kernel acceptance.

## 6. Additional independent written controls (unexecuted)

1. **Keep historical floor layers.** At N605, true H is1. Replacing every earlier G(n) by final g=1 gives the false exponent M=485 and incorrectly treats484 G0 ranks as G1. Dropping the121 factor in thresholds likewise assigns nonzero height at n121 although the actual cap is1.
2. **Do not discard zero complements.** At n121, source121 has multiplicity224. Removing it from S changes7688 to7464 and breaks the exact default B121=W lower endpoint. B0=1 makes its recursive zero-rank batch legitimate; zero leaf work is not zero productive-array count.
3. **Do not lose root multiplicity.** The all-5 coefficient is420^G, not one word representative. The theorem is not generic over inventories with no such multiplicity: for valid T={2:1},P={1:1}, default S_n=1 and B_N=1, so a universal positive NlogN lower coefficient would be false.
4. **Do not divide by P-W in the equal case.** The same W=P=1 control has full unit upper sum G+1; a denominator0 formula is invalid. The raw profile avoids this only because55998>7688 is fixed and explicit.
5. **Do not replace the batching policy.** Setting a_n=1 changes the recurrence to B_n=S_n and does not satisfy this theorem. In the actual raw G0 range, such forced replication already fails at n126: source5 gives complement121, whose width is7688, and1 is not divisible by7688. This does not rule out other properly funded admissible batching policies; they are outside the theorem.
6. **Do not import separated-floor assumptions.** Raw paid rank48 exceeds minimum target5, so the rmax<kmin separation condition is absent. Source boundary exits and child fresh sources cannot be silently dropped to import a different separated model. The valid general condition here is rmax48<m121.

These controls are hand arguments, not source mutations or observed failures.


The code-review note also gives a legitimate short alternative-policy control: forced a=1 through n122 has B122=W, whereas the default has W^2. It later fails n126 divisibility and does not become a valid all-rank alternative. This is a written policy discriminator, not an execution receipt.


## 7. Exact expanded caller accounting, as supporting source binding

Use B_n,L_n,U_n,C_n,R_n for the actual widths/leaves/units/columns/slots arrays and u_n,c_n for the local flow unit/column counts. Below121, including0, B_e=1,L_e=e,U_e=C_e=R_e=0. Default a_n=B_(n-1). For every source rank s and exit rank e, the child rank is n-s or e, respectively; a_n is divisible by every earlier B_child. The actual code adds copies=count*(a_n//B_child) to each of the four record arrays, without deduplicating equal ranks.

Local rank mass gives sum_s s*S_s-sum_e e*E_e=608*c_n. Strong induction with L_child=B_child*childrank-608*C_child then gives
L_n=a_n*(n*S_n-608*c_n)-608*sum_children copies*C_child,
so B_n*n-L_n=608*C_n for the fully expanded counts. Positive whole local columns and nonnegative copies give U_n<=C_n<=B_n*n/608. The local slot allowance S_n+exit_count+(W+P)*u_n is at most2(W+P)*u_n, and the actual recursive child additions propagate R_n<=2(W+P)*U_n. The source already claims these accounting bounds; this is the explicit connection to its current loops, not a new slot identity or physical tariff.

Writing ell_n=L_n/B_n cancels replication and yields
ell_n=(sum_s S_s*ell_(n-s)+sum_e E_e*ell_e)/S_n.
Thus changes in a valid batching policy may change widths while preserving this normalized leaf recurrence. The width lower bound here is not a paid-leaf-saving obstruction.

At n121, the224 source jobs of rank121 have zero complements. They remain in source_count and B121=W while their complement leaf cost is zero. The exact symbolic endpoint is L121=121*W-608 and U121=C121=1. No native array, bank allocation, adapter implementation or paid ordinary-control price is inferred from these integer records.
