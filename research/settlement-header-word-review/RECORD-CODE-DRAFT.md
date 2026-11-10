# Source-aware audit of settlement and its anchored attaining word

## Verdict and scope

**Qualified PASS for the central h-Z slope-separation theorem, the actual zero-target partition/addition/witness path, and the anchored full-proper-minor implication. No material discrepancy was found.** The source already owns this theorem, its prices and witnesses. This note is an external written proof-to-code audit, not a new optimum, finite result or actual execution.

Exact source: SHIN09-git PR6712 head `03caa7f6cb5bd21c834024e9d81f6b43eb325b91`, `research/monomial-guard-settlement/`. The proof, algorithms and settlement implementation were exposed in the earlier bounded scout; this is not a fresh blind role. More source/caller text was read for this assignment. No current peer draft was read before sealing. No source/new scientific program, import, DP, enumeration, matching, literal-minor search, fault, NumPy/native operation or proof kernel was executed.

The selected path is `witness(...,target_value=None)`. The binary dummy branch, ternary scalar/envelope theorems, NP-completeness, orbit classifications and later claims were visible in source context but are **outside this audit**. The source's eight registered commands, multiple computational routes, twenty faults and extensive reported finite certificates remain source evidence; none is rerun, missing or newly established here.

Inspected exact source bindings:

| Path | Git blob |
| --- | --- |
| PROOF.md | `234bbba4812a8a5ca774679451ba17a8072d6b56` |
| ALGORITHM.md | `f855486175dd7c85c86fe410e85038636bed55aa` |
| settlement.py | `74df4fb3154fc62775850fcf54136a46faa33989` |
| source/finite.py | `b88d32f8ef386f3debd589d6eaf72d5501ab1132` |
| literal.py | `bef3d242ad16109eabf27a41cf0c34b47ad76c6d` |
| monomial.py | `3b68a6d1a59b8407f4b54706eeaad78dfa397e21` |
| example_check.py | `311863c06845ac005292e25c47338dc6cde83ad6` |
| certificates.py | `e753a14ac687c0d2826a0bb42db9999bdbc4d89f` |
| verify.py | `ddfade70fb213da5a493f6c244aef3943bc1a482` |

Only the relevant constructor/consumer predicates are accepted below; importing one of these files would pull additional source outside this narrow claim, and no import occurred here.

## 1. Exact model and arithmetic assumptions

Work in a finite field K with valid exact addition, multiplication, negation, inversion of nonzero elements and zero encoded by0. Let u in K^m be nonzero, b a row with b*u=1, and W a matrix of slope rows with W*u=0. The full affine guard family is `b+lambda W` for **every** lambda in K^d. Guards test every proper leading principal minor of the corank-one complements after the same coordinate header.

Permutations and invertible diagonal coordinate scalings are free. A paid step is an elementary row addition `R_i <- R_i+a R_j`, with i!=j and a!=0. Header dimension is fixed; known-input-dependent coefficient/word choice is allowed. This is a specified algebraic operation metric, not a universal circuit minimum, restored-input service or physical tariff.

Slope charges are labeled vectors y_i=u_i*W_:i, with total sum zero. Initially zero charges are discarded for the list defining h and Z; h is the number of nonzero charges, and Z is the maximum number of nonempty zero-sum blocks partitioning those h labels. For h=0, Z=0. Labels matter even if two vector values agree.

The abstract theorem works over any field satisfying these operations. The actual retained `Field` constructor implements only q in{2,3,4,5,7,8,9}, using prime-field or polynomial-basis lookup tables. It is not an all-prime-power constructor. This review reads that closure and relies on its valid-field arithmetic contract; it does not newly certify every arithmetic table/irreducible polynomial or advertise hostile field-object admission. Actual inputs must have equal vector widths, valid field labels and valid coordinate indices. Generic helper signatures do not independently validate every such shape/type condition.

## 2. Full guards force slope separation

For a prefix, let X be the scalar charge sum and Y its slope-vector sum. The determinant lemma makes the guard for parameter lambda equal to `1-X-lambda Y`. If Y!=0, the linear map lambda->lambda Y is onto K, so one parameter in the **complete** affine family makes the determinant zero. Hence passing every guard forces every proper Y prefix to vanish. The full slope sum also vanishes by W*u=0. Consecutive differences therefore force every coordinate charge y_i to vanish, including the final coordinate.

Conversely y_i=0 makes all slope prefixes vanish, but leaves the scalar prefix requirement X!=1. Separation alone is not the full unanchored guard condition. A named proper subfamily can also fail the necessity argument because it may omit the offending parameter. These are hypotheses of the exact price transfer, not optional interpretations.

The actual `flat_rows` enumerates all d-tuples of field parameters and combines each with b and the slope rows. `literal.identity_pass` forms the actual complements and tests orders1,...,m-1; `literal_orders` checks corresponding proper subsets along every labeled order. The full determinant is correctly excluded. No literal predicate or parameter enumeration was executed by this review.

## 3. Actual dual row update and conserved component charges

The source `add_row(field,u,rows,target,source,a)` rejects equal target/source or zero a. It updates

    u_i <- u_i+a*u_j,
    row_j <- row_j-a*row_i

for every supplied dual row, where i is target and j is source. Other u components and other row entries remain unchanged. It makes copies and uses each old target-row entry when updating that row's source entry. This is exactly u->T*u, row->row*T^-1 for T=I+a E_(i,j); it is not the opposite dual orientation.

For slope columns, only the two vector charges change:

    y_i <- y_i+a*u_j*W_:i,
    y_j <- y_j-a*u_j*W_:i.

Their sum is conserved. This identity does not require the transferred vector to equal either current whole charge in an arbitrary word. It applies even when initially zero-charge coordinates are used as helpers. All row pairings with u are preserved by the dual action, so the normalized affine family remains the same family under the accumulated header.

## 4. Lower bound includes free monomials and zero-charge helpers

A monomial matrix normalizes elementary transvections: conjugating one by a permutation/diagonal gives another valid transvection with relabeled distinct indices and a nonzero scalar. Therefore every allowed word can be rewritten with the same number of paid steps and all free monomials at the end. A diagonal cancels from each product u_i*W_:i; a permutation only relabels the charges. The zero-charge objective is invariant under this final monomial, although the full guard event itself is NOT invariant under arbitrary coordinate permutations.

For the remaining paid word, put an edge between the two fixed labels of every paid step, counting repeated operations in the total cost. By the preceding conservation identity, the sum of initial charges in each connected component equals the sum of final charges there. At a separated endpoint this is zero. Components containing initially active labels thus induce a partition of all active labels into nonempty zero-sum blocks. If there are C such components, C<=Z.

A component containing k active labels and any number of initially zero helpers has at least k vertices and needs at least k-1 connecting edges. Repeated edges or extra zero-helper vertices cannot lower that connectivity requirement. Summing over active components gives at least

    sum_components(k-1) = h-C >= h-Z

paid operations. Components containing only initially zero charges contribute no negative cost and can be ignored. This proves the advertised lower bound for arbitrary allowed successful words, not just for the attaining constructor. A full guard requires separation by Section2, so it shares this lower bound.

## 5. The actual DP finds Z, including its backtracking

`subset_sums` starts with the empty sum and, for each labeled value, appends the old subset sums plus that value. The right-hand list is built before extension, so its indices correspond to masks with the next label bit set. Under equal widths and field addition these are precisely all labeled subset sums, not merely value multisets.

For any ordering of a subset S, count its nonempty prefixes whose sum is zero. Maximizing this quantity obeys

    P(empty)=0,
    P(S)=1_(sum(S)=0)+max_(i in S) P(S without i).

The final element i has no influence on earlier prefixes, and the last prefix is zero exactly when the full subset sum is zero. This is the recurrence implemented by `score[mask]` and `last[mask]`, not a greedy choice of arbitrary zero blocks. Each predecessor mask is strictly smaller, so the numeric mask loop has already computed it.

For the selected full active list the total is zero. Any ordering's zero-prefix boundaries partition that list into zero-sum blocks, so its boundary count is at most Z. Conversely concatenate any zero-sum block partition in any within-block order; its block ends supply at least that many zero prefixes. Maximizing over orders therefore gives exactly Z.

Backtracking repeatedly removes the stored last bit. Starting with an end mask of zero total, whenever the remaining mask also has zero total, their nonempty set difference is a zero-sum block. The current end is then replaced by that remaining mask. Successive blocks are disjoint and cover the entire list by the final empty mask; the stored predecessor choices attain `score[-1]`. The source's final block-count equality checks this reconstruction association. It does not by itself replace the DP proof of maximality, supplied above. Empty input immediately returns the correct empty partition.

## 6. The attaining word has a legal nonzero donor at every step

For the selected zero-target path, `witness` filters to the initially nonzero vector charges and calls `partition`. There is no appended dummy. Each resulting block is nonempty, contains only real active labels, and has total zero. In each block the code chooses its last real label as donor/root j, then visits every other real i once.

An active vector charge implies u_i!=0. The donor u_j is nonzero initially and never changes: each addition targets i, not j. Distinct blocks use disjoint labels, and previous operations in the block change only the donor's dual column, not an unvisited target's u component. Thus at every visit both u_i and u_j are nonzero and

    a=-u_i/u_j

is a legal nonzero field coefficient. The actual table expression `mul[neg[u[i]]][inv[u[root]]]` implements this field quotient without ordinary-integer division or an inverse-of-zero call.

The addition makes u_i zero. Its dual update adds that target's whole current charge to the donor charge. Repeating leaves all visited charges zero and the donor charge equal to the initial block sum, hence zero. A block of size k uses k-1 gates. Summed over Z blocks this is h-Z, meeting Section4's lower bound. Labels initially of zero charge remain untouched by this construction.

The source final charge and gate-count checks associate the generated internal result with the partition. Its returned dictionary contains gate tuples and certificate metadata, **not** the transformed u/rows. A caller must replay those gates on the original complete data if it wants an actual header result; merely storing the dictionary is not that replay. The all-input word argument establishes the implication without claiming that this review ran a witness.

## 7. Anchored carrier makes this the full proper-minor price

Assume b is supported at a single carrier c, u_c*b_c=1 and W_:c=0. Its slope charge is zero, so c is not an active label and the attaining word never uses it as target or donor. On every gate both targeted noncarrier b entries are zero; the dual update keeps them zero. Hence b remains supported at c, u_c is unchanged, and the carrier remains normalized. Its slope column also remains zero.

After settlement all coordinate slope charges vanish. A free final permutation placing c last makes every proper scalar prefix zero, so every original affine guard has determinant one at every proper prefix. This proves the all-input anchored attaining implication. It is a coordinate-header operation: u and other dual coordinates may change, and no restoration of the original input vector or physical caller frame is asserted.

There is a real source consumer for this bridge. In `example_check.collect`, the anchored examples obtain gates from the slope-only witness. `example_check.example` then replays each gate via `add_row` on BOTH b and w, constructs the complete flat rows, and requires a positive literal order count agreeing with the subset order counter. This is distinct from `certificates.constructions`, whose anchored entries just store witness dictionaries. The source's replay already exists; it was not performed by this review, and its finite examples do not replace the all-input argument above.

## 8. Written weakening controls — all UNEXECUTED

1. **Wrong dual orientation/sign.** Updating the target entry of a row instead of the source entry, or using+a there, need not implement T^-1 and destroys the displayed two-charge conservation. A gate name alone does not establish the inverse-dual action.
2. **A donor that changes.** If the accumulator were also targeted by the settlement step or an earlier block, its u component could become zero and the displayed division would be illegal. The actual disjoint-block/source-only donor invariant is required.
3. **Drop free-monomial normalization.** Applying a fixed-label component argument while arbitrary free permutations are interleaved needs justification. Monomial conjugation supplies that normal form; arbitrary extra free linear mixing would not.
4. **Ignore zero-charge helpers in a lower bound.** They can have nonzero u or dual columns and participate in transfers. The component graph must include their labels; the bound then survives because adding vertices cannot reduce k-1 required connections among k active labels.
5. **Use any greedy zero-sum subset.** A locally found block need not maximize the eventual block count. The DP optimizes all labeled orders and backtracks an attaining partition; counting one partition proves an upper word, not its minimality.
6. **Retain only a named proper affine subfamily.** A nonzero slope prefix might not hit one for any retained parameter. The separation necessity uses the complete parameter family; applying its lower bound to an arbitrary smaller list would change the theorem.
7. **Use an unanchored scalar row.** Zero slopes alone do not ensure all scalar prefixes avoid one. The anchored carrier, its untouched support and final carrier-last permutation are the extra full-guard argument. An arbitrary free permutation can fail it.
8. **Skip the last proper prefix or check only zero charges.** The actual predicate is all orders1 throughm-1, never just a first pivot or the full determinant. Word metadata or a separation summary does not itself execute this predicate; replay on b+W and the actual complement checks are the source's separate route.
9. **Treat helper signatures as hostile packet validation.** Malformed widths/labels/negative indices, an unsupported Field constructor input or an altered target_value branch are not admitted by the stated generated path. A field representation or physical gate alphabet change requires its own proof; no all-q code-constructor or arbitrary circuit minimum is inferred.

These are proof challenges to weakened claims or operations, not source defects, new observations or seventeen experiments when combined with a peer's overlapping list. Source extensive controls retain their own provenance.

## Conclusion, credit and remaining scope

The central proof, recurrence/backtracking and actual dual word are consistent. The active partition supplies both a lower bound against every allowed word and a legal attaining sequence; the anchored carrier supplies the separate all-proper-minor endpoint. No source code change is requested.

SHIN09-git6712 retains the finite-field guard realization, exact prices, witnesses, sharp ternary and other package results. Classical debt-clearing/zero-sum partition methods and subspace/header predecessors keep their attribution;6710 and ToikY/Nick Petalas complete-header work are not repriced by this note. The imported exact arithmetic retains its original source/license and known supported domain. Substantial Codex/source-aware review exposure is disclosed.

No new DP result, witness execution, matrix/raw/orbit census, field-law table certification, binary dummy/ternary envelope/NP result, restored physical input/output service, movement/precision/selection/return invoice, native supplier, human/formal acceptance, kappa, selected-frontier or adoption change follows from this audit. All selected framework assumptions remain in their prior state.
