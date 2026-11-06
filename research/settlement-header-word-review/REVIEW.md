# Settlement price and its actual attaining header

## Result and exact scope

Qualified written PASS: SHIN09-git [PR6712](https://github.com/CrocSwap/integer-mult-bounds/pull/6712), head `03caa7f6cb5bd21c834024e9d81f6b43eb325b91`, already proves the central h−Z slope-settlement price. This external review binds its lower bound, subset-DP/backtracking and actual `witness(..., target_value=None)` row word to the anchored complete-affine-family proper-minor endpoint. No material discrepancy was found on that domain; no code change is requested.

This is a new source-bound review, not a new theorem, optimum, witness execution, count or physical tariff. The source owns h−Z, its original eight commands, multiple routes, twenty faults and all reported finite outcomes. None was executed here. The binary dummy target branch, ternary scalar/envelope/extra-step claims, NP-completeness, orbit classifications and later sections are outside this review, including where retained source context exposes their text.

`PROOF.md` blob `234bbba4812a8a5ca774679451ba17a8072d6b56`, `ALGORITHM.md` `f855486175dd7c85c86fe410e85038636bed55aa` and `settlement.py` `74df4fb3154fc62775850fcf54136a46faa33989` are the central inputs. The exact additional consumer/arithmetic texts and source custody are listed in SOURCE-PINS.json. Python files are inert `.py.txt`; this subset is not a runnable original suite. Remote source custody is checked separately from canonical-main provenance; no pending foreign object is represented as a main ancestor.

## Model and quantified endpoint

Let K be a field, u a fixed-dimensional column, b a row with bu=1, and W a matrix with Wu=0. The guard family contains **every** row b+λW, λ∈K^d. A header transforms u→Tu and each dual row r→rT⁻¹. Permutations and invertible diagonal matrices are free; every transvection T=I+aEᵢⱼ with i≠j, a≠0 costs one. Input-dependent choice is allowed. This is a coordinate-header metric; original coordinates need not be restored. No restricted instruction alphabet, coefficient bit cost, physical gate realization or free general linear mixing is inferred.

Define labeled vector charges yᵢ=uᵢW_:ᵢ, active set A={i:yᵢ≠0}, h=|A|. Their total is zero. Let Z be the largest number of nonempty zero-sum blocks in a partition of A. For h=0 set Z=0. Equal charge values retain distinct labels.

For any proper prefix put X=Σbᵢuᵢ and Y=ΣuᵢW_:ᵢ over that prefix. Its rank-one-complement determinant is 1−X−λY. If Y≠0, the scalar map λ↦λY is surjective, so some member of the **complete** family fails that minor. Passing every member at every proper prefix forces all such Y to zero. Consecutive differences, together with total Wu=0, force every individual yᵢ=0. The failing λ may depend on the prefix; a common failing parameter is unnecessary.

Thus successful full-family headers must settle the slope charges. The converse also needs scalar prefixes to avoid one; settlement alone is insufficient. The attaining full-guard statement below uses a scalar anchor and makes all proper determinants exactly one.

## Lower bound against every allowed word

For the paid step i←i+a·j, the actual dual update is W_:ⱼ←W_:ⱼ−aW_:ᵢ while uᵢ←uᵢ+auⱼ. Hence

    yᵢ′ = yᵢ + auⱼW_:ᵢ,
    yⱼ′ = yⱼ − auⱼW_:ᵢ.

Only two charges change and their vector sum is conserved. This holds for initially zero-charge helpers too; a helper can acquire charge and cannot simply be discarded from a lower-bound proof.

Monomial matrices normalize transvections. Move free operations to the end by conjugation, preserving paid length and legal nonzero coefficients, or equivalently track labeled strands through free permutations. Diagonal factors leave each charge unchanged and terminal permutations only relabel the settled objective. This normalization is for charge settlement, not a claim that arbitrary permutations preserve the guard event.

Draw an undirected edge for each paid step between its tracked labels. At a settled endpoint, each connected component's initial charge sum is zero. Components containing active labels induce C nonempty zero-sum blocks partitioning A, so C≤Z. A component containing k active labels and any zero helpers needs at least k−1 edges. Counting all paid edges, including repetitions or ineffective operations, gives

    L ≥ Σ(k−1) = h−C ≥ h−Z.

Components with no initially active label contribute no negative cost. This covers intermediate cancellation/creation and all allowed words, including ones using the scalar anchor. A heuristic that each step removes at most one active charge would not suffice: a step can remove two opposite charges.

## Why the actual subset recurrence and backtracking attain Z

`subset_sums` doubles the old list by adding the next labeled vector. Under equal widths and exact valid field labels, numeric indices are the intended bitmask sums. `partition` rejects a nonzero total and uses

    D(∅)=0,
    D(S)=maxᵢ∈S D(S\{i}) + [Σᵢ∈S yᵢ=0].

This maximizes the number of nonempty zero cumulative prefixes along an ordering of S, by choosing its last label. Every predecessor mask is numerically smaller. At full A, cut an ordering at all zero-prefix boundaries: those cuts form nonempty zero-sum blocks covering A. Conversely concatenate a maximum zero-sum partition; its block ends are zero prefixes. Therefore D(A)=Z.

The stored `last[mask]` is an actual maximizing removed bit. Backtracking starts with zero-total `end=A`; whenever the nested remaining mask has zero total, `end ^ mask` is a nonempty zero-sum set difference, then `end` becomes that remaining mask. Successive differences are disjoint and cover A upon reaching empty. Their number is D(A); the source checks that association. Empty input returns the empty partition. Repeated vector values are never deduplicated. The check alone does not establish maximality; the preceding recurrence interpretation does.

No DP value or finite partition was computed by this review. Exponential state space is not a scalability endorsement.

## Legal attaining word and the literal code orientation

In each optimal block choose its final real label j as collector. Initially active yⱼ implies uⱼ≠0. For every other i in that block use a=−uᵢ/uⱼ and target i, source j. Unvisited uᵢ retains its initial nonzero value and uⱼ never changes; disjoint blocks cannot affect it. Thus every coefficient is legal and nonzero, even if the collector's **charge** cancels before the final transfer. Each step sets uᵢ to zero and transfers its entire current charge into j. At the end the collector charge is the original block sum, zero. This uses |block|−1 steps per block, hence h−Z total.

`add_row` first copies u and each row. It rejects target==source or zero a, sets `u[target] += a*u[source]`, then sets each copied `row[source] -= a*row[target]`. Distinct indices mean the target entry used for that dual update is its old value. The expression `mul[neg[u[i]]][inv[u[root]]]` is precisely the field quotient above; no ordinary-integer division or inverse of zero is needed. The zero-target witness filters active labels, partitions them without a dummy, records the tuples, applies this update, and checks no remaining nonzero charges and gate count h−number_of_blocks.

Its returned dictionary contains gate tuples/certificate metadata, **not** transformed u and dual rows. Replaying these tuples on all original rows is a separate consumer obligation; storing the dictionary alone does not execute a header.

## Anchored full proper-minor bridge and existing consumer

Assume b is supported at c, u_c b_c=1 and W_:c=0. Then c is inactive and the attaining word never touches it. Every target/donor is outside c, so both corresponding b entries stay zero under the inverse-dual update. The anchor's b, u and slope column are preserved. After slope settlement, a free permutation puts c last. All proper scalar prefixes are zero and all proper slope prefixes are zero, so every original full-family proper determinant is one. The lower bound allowed arbitrary words, including use of c; the attaining word avoids it. No unanchored price theorem follows.

There is already a real source consumer. `example_check.collect()` obtains the anchored slope-only gates. `example_check.example()` replays them through `add_row` on BOTH b and w, calls `flat_rows` to enumerate the complete parameter family, and compares a positive `literal_orders` result against `passing_permutations`. `literal_orders` builds actual complements and principal submatrices for every proper size 1,...,m−1 along labeled orders; it excludes the full corank-one determinant. `certificates.constructions()` merely retaining witness dictionaries is a different use. The finite replay and lower-depth search already belong to the source; neither ran here. The uniform argument above supplies the all-input implication, conditional on the model, rather than extrapolating from those examples.

## Code domain and written weakening controls

The retained exact `Field` implements q∈{2,3,4,5,7,8,9}. The abstract field theorem is broader; this review does not certify every arithmetic table/irreducible polynomial or claim an all-prime-power code constructor. Field validity, equal row/vector widths, valid labels and coordinate indices are premises. Generic helpers do not independently admit arbitrary malformed/hostile packets.

The sealed abstract/code roles contain eight and nine overlapping **UNEXECUTED** weakening controls, not seventeen experiments. They challenge the coupled inverse sign/orientation, zero helpers, free-monomial normalization, legal coefficient alphabet, collector component vs charge, labeled optimal DP vs greedy blocks, complete parameters, scalar anchor, every proper prefix and generated valid-input domain.

Two explicit hand controls delimit the endpoint. Over F₃, u=(1,1,1), W=(1,−1,0), b=(0,0,1): the singleton λ=0 passes identity proper prefixes despite nonzero slope charges; the complete family supplies the failing parameter. Over F₂, u=(1,1,1,0), b=(1,1,1,0), W=(0,0,0,1): bu=1, Wu=0, h=0, yet three scalar ones cannot avoid a proper prefix sum of one under free monomials. Thus unanchored guard success is not implied by zero slope cost. These are changed-premise mathematical deductions, not observed source failures or new field searches.

## Review process, credit and obligations

The coordinator read the prior scout/source body and had informal preclaim algebraic reasoning. The code role had earlier source proof/code/later-section exposure. The target-known abstract role sealed before current6712 proof/code/peer reading; historical context is not excluded. First drafts and seals are retained unchanged, followed by a source/peer cross and an exact-version assembled review. AI role separation supplies inspectable arguments, not blind discovery, human independence or proof-kernel acceptance. No scientific source import, DP, field computation, constructor, matrix/minor search, census, mutant or kernel ran.

The original formal-interface task card is retained with explicit CHANGED written-review scope; its formal/kernel gate remains unmet. Reviewers can inspect this argument against exact inert texts and sealed roles without a replay hook. There is no scientific VERIFY registration and no claim of replaying the source's eight commands. Hosted repository-helper CI is reported separately if run.

SHIN09-git6712 retains the law, prices, original witnesses and subsequent classifications, with its disclosed Codex assistance. Credit6710 finite-field/context work, ToikY's distinct binary/all-field pair and prior header work, Nick Petalas's marginal/pair/header predecessors, all original NOTICE/license contributors and classical determinant, row-operation, connected-component/debt-clearing/zero-sum partition methods. This review was produced by ToikY with substantial OpenAI Codex assistance and separate abstract/code/metadata/byte roles; no predecessor endorsement is asserted.

Actual physical header selection, coefficient implementation, placement/movement, restoration/inverse, tape/precision, stock/owner cleanup, sampling, native/all-column supplier, compiler and full tariff remain open. All five selected framework assumptions remain in their prior state. No κ/frontier/adoption change, merge, physical multiplication result, new numerical optimum or reservation of follow-on work follows.
