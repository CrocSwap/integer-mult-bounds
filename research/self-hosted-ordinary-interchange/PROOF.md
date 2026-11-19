# Width descent for cyclic ordinary interchange

A stopped word exposes ordinary swaps while it executes. Its public wrapper also produces an ordinary swap. Sections 1 through 4 close this loop for one word. Section 5 permits a finite cycle of different words and proves the bound for each entry. The selected and pending complete callers in [APPLICATION.md](APPLICATION.md) use that second result.

## 1. Statement

Fix a radix `q`, a finite stopped word, and a rational `0 < rho < 1`. At the public entry the input is an arbitrary bit array in address order

```
[P] [q^e] [G] [q^e] [S]
```

with positive complete spectator ranges. Its bit volume is `V=P G S q^(2e)`. The output sends address `(p,h,g,d,s)` to `(p,d,g,h,s)`. A record of fixed length for this call can put its bit index in the last range. All such bits return to their original record offsets. A caller with a borrowed input can keep the input and take a distinct output. It must consume the returned output before reusing the port. Width zero gives the identity.

Use the following **open** word interface. These are properties of the producer *when an unweighted ordinary move is an instruction that requests service*. They contain no runtime or space premise about the implementation of that instruction.

* The source's padded ordinary wrapper computes this permutation if each requested move returns its specified output. Each of its two reversed body calls restores its row at its own return. The scalar word, native endpoint, weights, ownership and stopping cases have their stated semantics on arbitrary complete arrays.
* A stopped node on `n` atoms of width `w` has a fixed profile of child volumes. For `n >= m`, the total bit volume of children with at most `r floor(n/m)` atoms is charged by the list `(r,c_r)`. Each corresponding group of calls has total volume at most `c_r` times the node volume. Groups are disjoint in this account, repetitions count, and `1 <= r < m`. Every child on a single active path has at most `1/L` times its parent's volume, with fixed `L>1`. Use the source's fresh rows at every invocation. The bound holds conditional on each allowed ancestor state. It includes bad-class children. Widths below `m` are stopped.
* The nonrecursive passes of a node cost at most `C V_node (1+n)`. At that node its unweighted ordinary requests have widths at most `Cw` and aggregate volume at most `C V_node`. Each returns before its consumer runs. Local private streams, split/return buffers and descriptors use bounded relative extents `C V_node`. Nonrecursive streams restore their permitted scratch. These requirements concern the actual passes, including prefix preparation and rewind. An unrestricted time bound on a black box does not establish the space condition.
* The outer stock has an effective bound `k <= C w (1+log(2e))` borrowed digits. One exterior row pad has bounded volume inflation. Opening or removing the padding, the three body shifts, the tail and the high-part exchange can be performed with total additional normalized cost `O(1+n+k+w)` using elementary moves. Finite constants can differ between these clauses.

Include parent parking in the nonrecursive work allowance. It suffices that each node makes at most `C(1+n)` full current-frame suspensions in total for stopped children and batched ordinary instructions. At a loop over many tiny old-prefix cubes the source can batch a fixed high-column operation over the complete old-prefix range as a spectator. A loop that scans the full parent again for every small cube would require a separate time proof.

Put `mu(z)=sum_r c_r (r/m)^z` and suppose `mu(1)<1`. If `sum c_r>1`, let `sigma` be the unique root of `mu(sigma)=1` in `(0,1)`. Otherwise set `sigma=0`. Put

```
t = max(sigma, 1-rho, rho).
```

One fixed finite-tape program per open word and `rho` uses elementary digit interchanges as its base. It computes the public service at all widths. For constants `C,d` of this program its time is at most `C V (1+e)^t log(2+e)^d`. Its visited backing is at most `K_entry+C V`. Thus the *same program* has bound `O(V (1+e)^z)` at every `z>t`. The constants in the latter bound may depend on `z`. Equivalently, any strict coarse saving `a` with `mu(1-a)<1` and `a<rho<1-a` gives the pure bound `O(V (1+e)^(1-a))`. No price is selected at runtime. The characteristic refers to the charged upper profile.

## 2. Produce the inputs and close the program

Choose `w=ceil(e^rho)` using integer powers and comparisons. Fix an entry cutoff large enough that the required stock fits with `k<e/2`, and all widths `u<=Cw` at inner ordinary sites satisfy `u<e`. The additional constant margin used in Section 3 can be included in this cutoff. It exists effectively from the finite constants and `rho<1`. For example bound the logarithm by a positive power smaller than `e^((1-rho)/2)` beyond a fixed threshold. Below the cutoff exchange each corresponding pair of digits using the elementary stream lemma. This costs `O(Ve)`, with bounded `e` here. The digit rule applies with all other coordinates present.

At a larger entry make the same row and body as the source. If `W(w)` is the fresh row divisor and `D` bounds the stopped depth for the original width, `W(w)^D` suffices for the selected word. Each coarse child takes its fresh factor from unused stock. Every smaller **ordinary** invocation performs its own borrow and restores it. The external stock factor for those ordinary invocations is one, by induction on `e`. Sequential moves reuse a restored row.

Use the high part of the first chunk as an existing preceding row. The second high part remains in the gap. Pad the first row once to a multiple of the required divisor, by a factor less than two. On the complete atom body perform the five chronological source operations

```
D <- D-H
F(H,D)
D <- D+H
F(H,D)
D <- H-D
```

where `F(H,D)=(C D,C H)` with atom reversal `C`. Thus the states after the two calls are respectively `(C(D-H),CH)` and `(D,D-H)`. The last operation gives `(D,H)`. Both reversed calls complete their own rows, including on the padding. Exchange any partial atom with elementary digit moves, restrict to the genuine rows and exchange the two high parts by `k` pairs of elementary digit swaps. The remainder can operate on its disjoint digits in the source wrapper's order. There is no recursive high-part call. Two equal address ranges of any positive cardinality `M` can enter by numerical padding of the two active ranges to the least `q^e >= M`, followed by restriction after the ordinary endpoint. This also gives the binary interface. The factor is below `q^2` for `M>1`. The same fixed radix is used for the entire inner computation.

At each open ordinary instruction suspend the current word and install a new ordinary entry on its smaller width and complete local stream as specified in Section 3. The new entry starts with the unit weight and its own row preparation. The parent evaluates its weighted coefficients and carries in its own scope. Its old numerical descriptor stays parked. No smaller root reads an unrelated long ancestor descriptor. The paid fallback reversals on `f` and `floor(f/2)` atoms are children of the same stopped tree. Passing these to the width-`O(w)` entry would be incorrect.

Termination and correctness follow by induction on the outer digit width, then on the stopped atom count within that entry. Each private lifetime has its source owner. The scheduler waits for each complete slab, merges and installs its entire output, and only then retires its private storage and resumes the parent. It can keep the borrowed input until the completed return. A correlated private centre is a valid input. The number of independent productive roles remains the source count. No centre, copy, duplicate fibre or dummy row earns credit.

## 3. Space when the ordinary instruction has the full payload

Shrinking width alone does not free space. For example an eight-digit radix-three call and a two-digit call can each have volume `3^16`. Give the second call prefix and gap cardinalities `3^6` each. Suspending a whole active root at each of a growing number of such edges would not prove a linear bound.

Let `V0` be the bit volume of the nearest enclosing **ordinary** root. There is a fixed `A>=1` such that each ordinary request at any coarse node of that root has volume `U<=A V0`. Indeed the body is padded once by a constant, a single coarse edge contracts by `1/L`, and the node has a fixed local expansion allowance. Choose an integer `J>=4A`.

For the request `[P'][q^u][G'][q^u][S']`, take the largest spectator length `M=max(P',G',S')`. Split it into `min(J,M)` consecutive intervals, with lengths differing by at most one. A stable scan sends each record to its interval. In prefix order the routing consists of a fixed number of nested counters over complete ranges. For each interval run the ordinary program with that spectator length. On return read the streams with the same interleaving counters. The interval offset needs no arithmetic inside the callee because an ordinary interchange leaves the spectator coordinate fixed. This also applies to gaps and to the bit index of an opaque record. No weighted word is asked to accept a sliced ancestor descriptor. The interval lengths sum to the original length. No padding, hashing or output credit is involved.

If `M>=J` each piece has at most `2U/J <= V0/2` bits. If `M<J`, the whole request has at most `J^3 q^(2u)` bits. The parent has at least `q^(2e)` bits. Enlarge the fixed base cutoff so that `J^3 q^(2C ceil(e^rho)) <= q^(2e)/2` above it. This proves the same contraction in both cases. No test against a distant parent's stack or high-water mark is needed in the tape program. The reference dispatcher checks this inequality on its small executable examples and can use elementary moves when it fails.

Split, merge, copy, rewind and erase all use `O_J(U)` steps and bit cells. Use one stream per interval and process the returned intervals serially. Sizes and indices are encoded integers. Within a scan a ripple counter has linear aggregate work including reset. Initial arithmetic on the fixed number of local range lengths costs a fixed polynomial in `log(2U)`, hence `O(U)`. Each deepest auxiliary sees precisely the complete stream it needs.

Use the delimited-segment dispatcher on a fixed number of tapes. A push parks the local registers, counters and finite return address, and opens a fresh segment above each active port. A pop first extracts the public output into a protected relay, clears the local coded extent, restores heads to the parent delimiters and installs the relay at the destination. Keep the parent inaccessible during the call. The fixed alphabet encodes virtual blanks separately from the physical delimiter. Local scans stop at the local origin. Repeated operations reuse those origins. These mechanics and their linear scan costs are supplied by the source segment construction. A node's local space allowance includes all queued slabs, outputs, and temporary copied state. Parking the current node once per one of its fixed ordinary sites costs `O(V_node)`. None of these costs is proportional to the sum of older parked frames.

Within an ordinary activation on `V_i` the active coarse frames occupy at most a constant times `V_i sum_{j>=0} L^(-j)`, including its padded root. Across ordinary activations `V_(i+1)<=V_i/2`. The two geometric sums bound the live head extents by a fixed multiple of `V0`. Reuse the vacated segment on the next sibling. On any one tape, the highest cell ever visited is bounded by the largest simultaneous extent from its reused origin. Sum over the fixed tapes, and add all pre-existing visited backing and entry head travel as `K_entry`. This proves the stated space bound even when erased material continues to count. It proves successful return, with the source entry-head convention.

## 4. Time including the repeated wrappers

Let `F(e)` be worst time per payload bit for the ordinary routine at width `e`, over the public shapes. For the moment hold its microcall bound `M(w)=1+sup_{u<=Cw}F(u)` as a symbol. Slab volumes sum to the original volume. Thus a node pays `O(V_node(n+M(w)))`, including administrative work. Sharding introduces no factor `J` on the **total recursive volume**. A fixed factor on setup is allowed.

The total normalized linear-in-rank charge is `O(n)` by `mu(1)<1` and induction. For the constant node charge, take the dominating tree with the listed positive edge weights `c_r` and child rank `r floor(n/m)`. If `mu(sigma)=1` and `b=sum c_r>1`, the sum of terminal weights times terminal rank to `sigma` is at most `n^sigma`. This follows by replacing one vertex by its children and using the floor. Positive terminal ranks give total leaf weight at most `n^sigma`. With internal weight `I` and leaf weight `E`, full expansion gives `E=1+(b-1)I`. All node weights therefore sum to `O(n^sigma)` even at equality. Grouped actual child ranks below the charged ones are dominated by the same increasing bound (or by the full upper tree). When `b<1` a geometric sum suffices. When `b=1` each depth has mass at most one and there are `O(log(2n))` levels. In this last case use any fixed `0<s<max(rho,1-rho)` as an upper exponent for the node count. This leaves the stated `t` unchanged. The empty body has no charge.

For `b>1` put `s=sigma`; for `b<1` put `s=0`. With the above choice for `b=1`, the stopped bound is `O(n+n^s M(w))` per bit for positive `n`. Account for both reversed calls, the one root pad, three lower shifts, high exchange, tail and format conversion. The complete large-root inequality has a fixed `K` with

```
F(e) <= K [1 + e^(1-rho) + e^rho log(2+e)
             + e^((1-rho)s) (1 + sup_(u<=C ceil(e^rho)) F(u))].
```

Choose `H(E)=max_{0<=v<=E} F(v)/(1+v)^t`. Since `s<=t`, dividing the last term by `(1+e)^t` leaves a bounded factor: its power difference is `(1-rho)(s-t)<=0`. All large-root arguments of `H` are at most `D E^rho` for fixed `D`. Increasing a constant for bounded widths gives

```
H(E) <= K' log(2+E) + K' H(D E^rho).
```

For any fixed `lambda` strictly between `rho` and one, `log(2+D E^rho)/log(2+E)<=lambda` eventually. Choose an integer `d>=2` with `K' lambda^d<1/2`. Induction bounds `H(E)` by a constant times `log(2+E)^d`. This charges the repeated wrapper, routing and padding constants over an unbounded number of ordinary roots. Any strictly larger power absorbs this logarithm. The source can specialize to one numeric price after this proof, without changing the algorithm.

The logarithm cannot in general be removed from this argument. Take an abstract two-leaf tree of quarter-rank children, with two complete bodies at every square-root scale. For `e_j=e_(j-1)^2` with all widths powers of four, the equality recurrence `U(e_j)=2 sqrt(e_j/e_(j-1)) U(e_(j-1))` multiplies `U(e_j)/sqrt(e_j)` by two per level. This is a counterexample to dropping a constant at the characteristic. It makes no lower-bound claim about a physical multiplier.

## 5. Cycles, different atom widths and unfunded entries

Take a finite cycle of words indexed by `i`. Each has the public ordinary endpoint and the open semantic, parking and space contracts above. Word `i` uses its own `rho_i`, ambient dimension, cover and row divisor. Fix one eligible radix for the catalogue. At every smaller ordinary instruction of word `i` run word `i+1` cyclically. Same-width weighted coarse children still use the parent's stopped word. A new ordinary activation receives only its two active ranges and complete spectators, starts at unit weight and creates its own stock. Use common finite bounds for sharding, frames and the elementary cutoff. Each tag fits in finite control. Width induction simultaneously proves all endpoints and the two geometric volume sums still bound the backing.

The following version allows a coarse profile to have `mu_i(1)>=1`. Assume `b_i=sum_r c_(i,r)>1` and write `sigma_i>0` for the unique root of `mu_i(sigma_i)=1`. This root may be greater than or equal to one. The leaf-mass argument of Section 4 still gives `O(n^sigma_i)` for the constant toll. At each depth the sum of weights times the current rank to `max(1,sigma_i)` is at most the initial rank to that power. There are `O(log(2n))` depths, because every coarse child rank decreases by a fixed ratio. Thus all nonrecursive linear tolls cost at most `O(n^max(1,sigma_i) log(2n))`. A strict moment at a slightly larger exponent also gives these upper bounds there.

Let the cycle length be `h` and solve

```
d_i = (1-rho_i) sigma_i + rho_i d_(i+1).
```

Substituting once around the cycle gives a unique solution. The coefficient of `d_i` on the right becomes the product of the `rho_j`, strictly below one. If every `d_i` dominates `rho_i` and `(1-rho_i)max(1,sigma_i)`, the closed program at entry `i` costs `O(V (1+e)^d_i log(2+e)^D)` for a fixed finite `D`. Divide the equation in Section 4 by the *entry-specific* power. The exponent for its ordinary service is `(1-rho_i)sigma_i + rho_i d_(i+1)-d_i=0`. The additional logarithm on the nonrecursive charge contributes to the additive logarithmic term. Take the maximum normalized function over the finite tags and choose a log-width contraction strictly between `max rho_i` and one. This proves the estimate as in Section 4. One can use `n<=e/w` directly even when the new service is faster than the local word. For any real `z`, `w^z<=2^max(z,0) e^(rho_i z)` since `e^rho_i<=w<=2e^rho_i`.

For a pure power, start from any finite strict tests `s_i=1-a_i>0` with `mu_i(s_i)<1`. Solve the displayed equations with `s_i` in place of `sigma_i`. Require strict slack over the two nonrecursive exponents at every entry. Continuity gives a common `epsilon>0` by which all tests can be decreased while preserving their strict moments and both guards. Decreasing every `s_i` by epsilon decreases every solution by epsilon. Use the node-mass bound at the reduced strict tests and absorb the logarithm into this power gap. **Only the coupled bounds must be sublinear.** An individual open word can have a nonpositive coarse saving.

For two entries, put `r=rho_A`, `s=rho_B` and let `a,b` be the strict covered savings. Their pure ordinary savings are

```
x = ((1-r)a + r(1-s)b)/(1-rs)
y = ((1-s)b + s(1-r)a)/(1-rs).
```

For fixed characteristic tariffs, elementary truncation at `j` levels replaces the next ordinary exponent by one. When the nonrecursive guards do not bind and `d_(i+j)<1`, the resulting positive difference in the propagated exponent is `(product of the first j width powers)(1-d_(i+j))`. This compares certified recurrences. An already completed, faster backend or a different tariff can give a better price at a single prescribed target.

A concrete neutral entry illustrates what the individual moment restriction excluded. Splitting one ordinary interchange into two half-width swaps on the same complete array gives normalized coefficient `c_1=2, m=2`, hence `mu(1)=1`. In the direct version partition each active field into consecutive pieces of width `u=ceil(e^r)` and one shorter remainder. Send each corresponding pair to the other entry. At most `1+e/u` requests carry the **full** bit volume. They act on disjoint digit pairs and preserve all remaining coordinates. Use the same spectator sharding before each request. Parking and stitching cost `O(V(1+e/u))`. This word has no high exchange, cover, weighted normalizer or row borrow. `block_word` implements it.

The direct inequality is `F_A(e)<=K(1+e/u)(1+sup_(j<=u)F_B(j))`. Its only additive power is `1-r`. It has no `e^r` guard and its coarse tariff is exactly neutral. The companion word can call this entry at *every* ordinary site. With `r=9999/10000`, `s=1/250` and the independent pending `b`, the pure savings are `r(1-s)b/(1-rs)` and `(1-s)b/(1-rs)`. To obtain a pure power, increase **only** the strictly funded B trial by a small positive delta. Both solved savings increase by positive multiples of delta and the actual additive guards remain strict. This absorbs the logarithm without asking for any strict moment from A. Both entries fund the pending complete caller. All saving here comes from the funded word. Moving the chunks in the neutral entry still costs time at full volume.

In fact the strict funded test at `b` permits one *fixed* power-split program for every price through `b`. Choose `b1>b` so close that its moment and companion guards remain strict. Take rational `b/((1-s)b1+s b)<r<1`. Then `b<x(r,b1)<y(r,b1)<b1`, and `x<r`. This single choice funds the original `b`. The following construction also preserves the exact characteristic. It makes no tuning choice for an individual price.

## 6. Inserting an entry without any loss of funded exponent

Start with any cycle covered by the preceding width recurrence. Replace any of its ordinary edges by a finite chain of the following words. Fix an integer `k>=2` for each inserted word. Its public input has width `e`. At `e>=2` partition both fields in order into pieces of width at most `u=ceil(e/k)`. Call the successor on each corresponding pair, including the final shorter pair. There are at most `k` calls. Each call has the entire bit volume. Width zero or one can use the elementary case. Every original cycle must still contain a word with a subpower bound on its smaller ordinary widths.

**Insertion theorem.** The modified cycle has the original characteristic upper exponent at each original entry, with a possibly different fixed logarithmic power. Each new entry has the exponent of the next original entry. The same fixed programs give every strict pure power supplied by the original proof. The elementary width cutoff and code are independent of which of those exponents a reader wants to use.

For a piece of length `v` starting at position `j`, the literal port spectators are `P q^j, G q^(e-v), S q^(e-j-v)`. The two middle fields being swapped each have cardinality `q^v`. The swaps act on disjoint digit pairs. Their product gives the whole required transposition on arbitrary input. Exactly `V` independent positions pass through each one. Send the previous result into the next request. The open driver charges at most `k` full traversals, split and merge passes, and suspensions. It restores each borrowed input and returns the entire final stream before the parent resumes. It creates no cover or row stock. This is the literal producer `fixed_block_word(k)` in the implementation.

Here `u` is of order `e`. The smaller-width proof remains well founded. Each proper block has `G q^(e-v)>=2`. For the largest spectator of length `M`, if `2<=M<J`, splitting it into singletons gives each new call volume at most `V/2`. For `M>=J`, the earlier bound gives at most `2V/J<=V/2`. Thus both the geometry of suspended frames and the stable, bit-exact return hold even on odd widths and arbitrary suffix records. Simultaneous stock can be summed just over the original entries. An intervening block only reduces the next width. With the common elementary cutoff each active powered transition still takes width to at most half. Unused stock and visited backing obey the same asymptotic bounds as before.

For a chain of such entries let `K` be the product of their fixed block counts. The total volume reaching the next original word is at most `K V`, including every physical shard. Each intervening split, copy, park, merge and rewind costs a fixed multiple of its current volume. The split-shard volumes sum to the request volume. Iterating the ceilings gives maximum successor width `ceil(e/K)`. Allowing elementary termination on the way only adds a fixed per-bit cost. Consequently

```
F_inserted(e) <= C_K (1 + sup_(v<=ceil(e/K)) F_next(v)).
```

Substitute this bound into the preceding original word's recurrence **before** applying the induction in Section 4 or 5. The coefficient changes by a finite constant. Its next original width is still at most `C' ceil(e^rho)` with the same original `rho<1`. The local additive exponents and recursive exponent equation are unchanged. The normalized maximum over original tags again contracts in log width. It absorbs the modified constants into one fixed power of the logarithm. Each intervening entry satisfies its promised bound by the displayed inequality. The same derivation preserves strict pure powers, with constants permitted to depend on the chosen price. It needs no power slack or stock at an inserted entry. A cycle of neutral halving words alone illustrates the need for a funded core: on powers of two the elementary-base leaf mass doubles at each halving and is proportional to `e`.

In particular a single powered word B and a two-block public entry have the same characteristic upper exponent at **both** entries. Each admits the full strict covered saving of B if it meets B's own two additive guards. Every small ordinary call made inside B goes back to the block entry. Neither the block count nor the machine changes as the reader ranges over all the admissible strict prices of this fixed B. A logarithmic factor can still occur at moment equality.

The same proof permits at most a fixed number of proper, positive contiguous pieces of unequal lengths, if their layout is produced within the paid linear allowance. Their total volume charge is still bounded by that count times `V`, and each proper block exposes a spectator digit. Use `e-1` in place of `ceil(e/K)`; the adjacent powered leg supplies the log-width contraction. This observation does not extend the price to an unbounded number of uncharged pieces.

## 7. Scope of the implementation

`interchange.py` implements the ordinary effects, sequential digit buckets, ragged split, protected return through separate results and smaller-width dispatch in Python. `check_streams.py` executes the actual five-operation wrapper around a small sequential reversed body, weighted four-swap leaves and a high-matrix column permutation. Its sequential body has no asserted saving. The tape simulation and time theorem above apply to a funded open word under its stated local contracts. The Python interpreter and its stack are reference machinery. The selected astronomical native template remains specified by its finite compiler. The selected source binding and numerical consequences are in [APPLICATION.md](APPLICATION.md).
