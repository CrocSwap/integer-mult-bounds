# Independent review of the complete four-site direct invoice

Worker B, prepared for @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. Source-aware AI review, not blind, human or proof-kernel review.

**Finding: no gap found in the declared direct-invoice exclusion.** I read
C's PROOF.md, verify_direct_bill.py, DIRECT-INVOICE-RESULT.json, the pinned
native pricing/caller sources and the inherited prefix/rank proof. I freshly
derived the normalization, endpoint shrinking, support relaxation, tail and
kappa monotonicity. An independently written multiplicity-vector enumeration
reproduces 267 inventories, nine deletion minima and six reflection classes.
Separate 60-digit Decimal diagnostics agree with the reported finite winner
and tail signs; those diagnostics are not the exact-arithmetic proof.
I did not rerun the 62,007,750-comparison source allocation search.

## Native, binary and root factors

Pairing 104 physical ports gives 52 copies of an eight-coordinate q=2 root.
It does not double the native invocation count. A native supplier acts on
two main roles per physical port, hence four roles per pair. Therefore a
rank-r_i full stage requires 52(r_i-4) additional whole idles. A sector of
dimension c_m contributes 52 c_m root targets. Dividing the physical bill
by 104 gives exactly the two factors of 1/2 in the root target/idle terms.

Four binary trees with F total leaves have F-4 internal nodes. Each node
has two independent auxiliary targets and two whole idles per physical port,
and one rank-one thin query. Its signed contribution is consequently
2[H(8u+1)-H(8u)]-1. The five-query root has four full sites and one thin
site, so the total thin count is F-3. The recurrence optimizes every binary
split recursively, not merely balanced shapes.

I independently summed the native table: helper rank mass minus paid rank
mass is -1720 per native invocation, or -215/13 per physical port. At k=0,
the root contributes 16F+3 after its thin query, and binary nodes contribute
F-4. Thus total physical surplus is

    104 [F(-215/13)+17F-1] = 48F-104,

as claimed. This checks all multiplicity factors against an independent
linear moment. Native main outputs are already represented by the caller,
so adding another credit for them would double-count.

For the reported relaxed winner (8,1,1,8), ranks (4,6,6,4), root targets
per physical port have ranks 145,73,73,17 and root idles are two rank-eight
requests. Its two eight-leaf trees have 14 internal nodes, giving 28 binary
idles per port. Together this is 30 whole idles, 15 thin queries and 18
native calls. The direct formula agrees with these independent counts.

## Legal endpoint shrinking and support reduction

The forced odd stage B supports query 0 on both sides and C supports query 4.
Since all four stages commute, AB and DC are commuting idempotents and retain
their endpoint query support. At site 0 support implies commutation with
I-2R_0; at site 4 the prefix is -I. Thus replacing A,D by AB,DC is legal
under the actual-prefix contract, and gives A<=B and D<=C.

Deleting one endpoint bit from one joint sector changes the target from
H(x+y) to H(x), with x>=1, y=8a_i>0, while saving idle H(y). For 0<1-k<1,
H(x+y)<H(x)+H(y), so the gap increases strictly. The coefficient 1/2
applies to both changes and does not alter the sign. The native suppliers,
binary trees and thin calls are unchanged. This is a valid upper relaxation.

Any three chosen query images and row spaces have dimensions 3q and 3q;
their skew-sign Gram has rank 2q. The union projector thus has rank at least
4q, equal to the ambient dimension. No sector of weight zero or one remains.
Together with the two containments, this leaves precisely masks
3,6,7,12,14,15. The endpoint cross Gram factors through AD and has rank q,
so c_15>=2. The rank floors, odd-pair inequality and two far-endpoint leakage
inequalities have the correct orientations and constants for q=2.

The finite necessary-condition set need not be geometrically realizable.
Deleting a bit while remaining in that set is still a valid objective
dominance step between relaxed inventories. Every such path terminates as
total rank decreases. Reflection reverses stages and allocations together;
the constraints and complete cost formula are invariant. The independent
count-vector enumeration confirms every stated inventory count.

## Finite evaluator and outward arithmetic

The positive integer compositions are enumerated exactly once: a,b,c>=1,
z=F-a-b-c>=1, for 4<=F<=127. Their count is binomial(127,4)=10,334,625.
Every six-class comparison is included. The dynamic program uses an upper
bound on both child values and on each positive H(8u+1), with a lower bound
on the negatively charged H(8u). Taking the maximum preserves its upper-bound
direction. No assumption that the recorded winner's geometry is feasible is
used in exclusion.

The integer objective is exactly 208*10^12 times the per-port formula:
2F times the unnormalized native signed moment, 208 times binary-node credit,
104 times root targets minus idles, and -208*10^12 for the root thin query.
The direct general evaluator and the optimized six-mask evaluator have the
same coefficients and indices. The largest target index is below the allocated
1025 bound. Positive helper/target terms use upper endpoints; negative paid
terms use lower endpoints, including when the native net coefficient changes
sign at a rank.

For log, 36 terms cover odd exponents through 71 and the first omitted term
is z^73/73. Bounding every later denominator below by 73 gives the stated
geometric upper tail. Range reduction has 0<=z<=1/3. For exp, the first
omitted term is x^17/17!; all later successive ratios are at most x/18, giving
the stated upper tail. Inverting positive exp bounds reverses the endpoints
correctly. Floor/ceiling to 10^-12 preserves enclosure. Float values occur
only in display fields, not in the exact acceptance inequalities.

The separate Decimal calculation gives the winning direct gap approximately
-0.06504536315734695, below the exact outward upper certificate
-0.06504536308798077. Removing the thin-query debit makes the upper bound
positive; this is only a missing-cost detector, correctly not claimed as a
feasible winning construction.

## Infinite allocation tail

Every internal binary node has u>=2. Concavity of H makes
i(u)=H(8u+1)-H(8u) decreasing, so each node contributes at most
A=2[H(17)-H(16)]-1. Subadditivity of each root target gives
H(1+sum y_i)<=1+sum H(y_i). Summing all eight sectors and subtracting the
stage idle multiplicities cancels the r_i terms, leaving

    F ell +(F-4)A + 2 sum_i H(8a_i)+3.

Jensen on the four child sizes gives 2 sum H(8a_i)<=8H(2F). The resulting
B(F) is concave, with derivative ell+A+16(1-k)H(2F)/(2F). The code encloses
both B(128) and this derivative from above, and both upper bounds are
negative. Hence the tangent argument excludes every real F>=128, including
all remaining integer allocations. This is a proof of the tail, not a
heuristic finite search limit. Independent Decimal values were
-0.11896838183487055 and -0.04585210997713886, agreeing with the exact bounds.

## Monotonic extension in kappa

For the native derivative, a positive signed inventory coefficient produces
a negative derivative term, so its upper bound uses the lower H at the right
endpoint and lower log; a negative coefficient uses the upper H at the left
endpoint and upper log. The code uses exactly these signs. The resulting
uniform derivative upper bound is negative.

Each binary increment decreases with k because f_k(r)=r^(1-k) log r is
increasing in r>=1 for k<1. The maximum over finitely many tree contributions
is therefore decreasing, without assuming differentiability of the maximum.
For finite allocations, f_k(r)/r increases through r=1025 because
k log(1025)<1. It follows that f_k is superadditive on all root sums in this
range. Differentiating the root target-minus-idle term gives at most
-2 sum_i f_k(8a_i)<0. Thus every fixed finite allocation decreases with k.

For the infinite tail, F ell_k, (F-4)A_k and 8H_k(2F) each decrease with k
for F>=128. No large-F superadditivity assumption is used. Negativity at
0.00330720 therefore persists throughout the stated interval ending at .004.

## Scope and review limits

This exclusion gives ordinary work for free and tests a relaxed geometry,
which makes the upper bound more favorable. It remains scoped to the exact
native inventory, direct separately paid idles, binary suppliers, four fixed
root sites and eight independent inputs per pair. Cross-stage fusion,
retirements, different native schedules or additional productive outputs
would change the invoice and require a new proof. No such mechanism is
silently excluded. Source-byte pins identify the inherited scope but do not
by themselves establish physical supplier admission or discharge the five
retained framework assumptions.

The independent count and diagnostic numbers are in C-INDEPENDENT-CHECKS.json.
The complete finite allocation result remains C's exact program/receipt;
this review did not run a second full 62-million-comparison census. No new
kappa, independent human acceptance or proof-kernel certification is implied.

## Final lead review

The lead independently checked the pair normalization, exact binary-node recurrence, legal endpoint products, six-mask relaxation, outward rounding directions and concave tangent argument. The derivative bound uses f(r)/r increasing only in the explicitly bounded finite range; the infinite tail instead uses termwise monotonicity of its envelope. These scopes are correctly separated. No gap was found. The packaged proof differs from the reviewed worker proof only by renaming the custom source manifest to ORIGINS.json. Its evaluator has the same one-path rename; no numerical or combinatorial logic changed.
