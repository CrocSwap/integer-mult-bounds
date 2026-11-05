# Direct mixed flow and explicit compiler size: a partial research checkpoint

**Publication authorized by the user on October 21, 2026.** This is a partial
compiler/resource checkpoint; the direct exponent gate remains open.

The target is a structural successor to
[PR4433](https://github.com/CrocSwap/integer-mult-bounds/pull/4433): remove the
tensor/padding step needed by overlapping ranks and control the complete
finite compiler's size. The user requested a significance target twice the
previous contribution. That is an ambitious scope target, not a numerical
measurement or a claim that it has been achieved.

Two results are established under the source native-word hypotheses:

1. A **finite chronological integer flow** works when paid ranks overlap
   target ranks, provided `max paid < ambient`. It retains and pays every
   unmatched job as an exit. All recursive ranks decrease. This gives a
   finite uniform compiler, **without a proved near-root saving**.
2. Choosing **nested divisible widths** gives `B_N <= exp(O(N log N))`.
   Exact rank-one accounting also bounds raw instances, owned centers,
   routing slots and the source finite-constant envelopes. This batching
   choice preserves the normalized leaf cost and therefore applies to the
   already supported PR4433 supplier.

The main exponent target remains open. Exact compilation at rank 1,000 on
the raw p7 profile fails the desired saving. That finite failure is not an
asymptotic obstruction, and it does not invalidate PR4433's separated recipe.
No new κ, selected frontier, native admission or physical runtime is claimed.

## 1. Source boundary and decision

The starting point is Jacob Alan Sussman's multinomial lockstep construction,
retained by PR4359. Its separated proof requires `r_max < k_min` so every
parent output is consumed. PR4416 and PR4433 instead repair the raw p7
overlap by chronological products, paid completion and splitting.

Retain the four native hypotheses of
[FINITE-PRECOMPILATION.md](vendor/FINITE-PRECOMPILATION.md): a correct
all-column arbitrary-input word, disjoint splitting with complete spectators,
permitted and priced whole-job adapters, and finite-program closure with
owned initialization/erasure. Equal rank alone does not supply an adapter.
Changed finite combinatorics do not independently admit those hypotheses.

**Continue, with two separate gates.** The finite-flow gate is now proved and
checked. The exponent gate requires a new uniform estimate on the complete
complement-plus-exit recurrence. Do not expand a search solely because a
moment root is favorable. The size theorem is useful independently, since
the predecessor leaves productive width and owned-instance counts implicit.

| Obligation | Evidence / remaining work |
| --- | --- |
| Integer matching with overlapping ranks | Proved below; literal and merged replays agree |
| Chronological return and strictly smaller exits | Proved under `r_max < m`; no cross-round matching |
| Source complements and full uniform output | Source integer-batch induction, with nested divisible widths |
| Direct near-root saving | **Open**; rank 1,000 fails; no global conclusion |
| Productive width, rank-one leaves, raw instances, owned centers | Explicit bounds below, with exact finite controls |
| Routing slots, encoded records and source finite-constant envelopes | Counted below in the stated grammar; physical implementations retain their own tariffs |
| Native all-column, physical, analytic, precision and recovery premises | Inherited; no full replay or new admission |

## 2. Partially matched integer lockstep flow

Let positive integer target multiplicities be W_k, chronological paid rounds
have ranks r_j, and let

```
2 <= k_min <= m=max(k),   1 <= r_max < m.
```

The paid word may have `r_max >= k_min`. At a fixed integer top rank n>=m,
put

```
c(a) = product_k k^a_k,
u(a) = multinomial(|a|;a) product_k W_k^a_k,
R(rho) = {a : m*rho*c(a) <= n},
G = floor(log_(k_min)(floor(n/m))).
```

For every paid-round path s of length d<=G with multiplier rho_s, instantiate
u(a) units at column rho_s*c(a), for every point a in R(rho_s) of degree
G−d. This is the source class construction. For a parent class with
multiplier rho, its rank-r round supplies u(b) jobs at point b when b is
present. The child demand at that point is

```
D(b) = sum over eligible (b−e_k) of W_k*u(b−e_k).
```

The complete Pascal sum is u(b). Therefore:

- If the parent point b exists, `0 <= D(b) <= u(b)`. Route D(b) of the
  **whole** issued jobs to the child. Complete the remaining u(b)−D(b)
  jobs as paid exits, at their actual rank `e=r*rho*c(b)`.
- If the parent point is absent, supply the child demand with new distinct
  top input arrays. These are source jobs, not copies of issued data.
- At depth G, every point has degree zero; all paid jobs are exits.

No fractional jobs, cloned productive inputs or uncharged discarded requests
are introduced. Within each point, choose a fixed enumeration of parent
jobs and target slots and match their first D(b) elements. The rest have
explicit endpoints and remain on their actual owners.

### Sources and exits

At the root, every demanded point has degree G+1, so it is outside R(1).
Its rank s is in `(n/m,n]`. A non-root source has no parent point, hence
`m*rho_parent*c(b)>n`; its rank is `r*rho_parent*c(b)>r*n/m>=n/m`.
Its eligible child target ensures s<=n. Thus every source is a positive
job in `(n/m,n]`.

Every exit belongs to an actual parent unit, so

```
e <= r_max*n/m < n.
```

This holds for the new premature exits as well as leaf exits. A premature
exit has at least one omitted Pascal term, with
`m*r*rho*c(b)/k > n`; consequently `e > k_min*n/m`. These are large exits
near the upper boundary. They cannot be assigned the old bound
`r_max*(n/m)^theta` with theta<1. That lost estimate is the exponent issue.

### Chronology and arbitrary inputs

Run all scalar steps of a class in their specified order. At paid position
j, issue that position for every unit, partition its whole issued jobs into
matched and unmatched slots, finish all unmatched exits and the entire child
class, restore adapters, and only then resume position j+1. The child takes
incoming jobs from this one parent round plus its new top sources. It never
waits for a later round of a suspended parent. The finite class depth is G;
all complement and exit calls have rank below n, so their uniform programs
are already available by strong induction.

Distinct slots in one class have distinct physical fields. Routing fewer
parent slots than the original full-Pascal construction preserves this
property. Arbitrary-input native correctness permits correlated values,
including current owned-center contents; it does not permit field aliasing
or extra productive credit. Each unit has its own owned identities and
retains them until its word clears them. These requirements are unchanged.

### Exact potential and count identities

Let S_s and E_e be integer source and exit inventories, U the unit count,
and Qcol the sum of the units' positive integer column multiplicities.
Cancellation of matched jobs gives, exactly at rank one,

```
sum_s S_s*s − sum_e E_e*e = Delta * Qcol,
Delta = sum_k W_k*k − sum_j r_j.
```

At any real exponent t, the corresponding identity is

```
sum_s S_s*s^t − sum_e E_e*e^t
    = (T_t−P_t) * sum_units column^t.
```

Thus a favorable raw t-moment survives as a superpotential. It does **not**
by itself pay the source complements. Writing W=sum W_k and P=number of
paid rounds, complete untruncated layer counts give

```
U <= sum_(d=0..G) P^d W^(G−d) <= (W+P+1)^(G+1),
S := sum_s S_s <= W*U,
sum_e E_e <= P*U.
```

The source package's separated case is unchanged: no premature exits occur.
The verifier compares it with the byte-identical predecessor literal replay.

## 3. Nested divisible widths and complete count bounds

Use the ordinary base B_n=1, P_n=n below m, with B_0=1 and P_0=0. For n>=m
choose the replication factor and productive width

```
a_n = B_(n−1),    B_n = a_n*S_n.
```

Every earlier width B_e divides B_(n−1), by induction. Therefore every
source-complement batch and exit batch is an integer number of smaller
uniform programs. This is a concrete choice within the source compiler's
existing denominator-clearing freedom; no optimum is claimed. Its previous
option to use an LCM is retained as predecessor context.

As in the source compiler, each of the a_n*S_n original arrays first gets
its disjoint complementary job, then its one source job through the flow.
All exits are completed by smaller uniform programs. The result is a full
rank-n transform on every original array. Owned storage is excluded from B_n.

The normalized leaf count satisfies the **same exact recurrence** for any
valid replication choice:

```
L(n) = (1/S_n) * [sum_s S_s L(n−s) + sum_e E_e L(e)].
```

Changing the replication factors changes width and total counts equally.
It does not spend supplier saving or alter any outer parameter.

For a fixed final N and h=G(N), all n<=N satisfy

```
S_n <= C_N := W*(W+P+1)^(h+1),
B_N = product_(n=m..N) S_n <= C_N^N.
```

Since h=O(log N), **log B_N=O(N log N)** for a fixed mixed rule. Repeatedly
multiplying all previous widths is unnecessary. This bounds one explicit
realization; the original compiler did not require that inefficient choice.

If Delta>0, telescope rank-one mass over the fully expanded uniform program:

```
B_N*N − P_N = Delta * Qcol_N,
U_N <= Qcol_N <= B_N*N/Delta.
```

All raw columns are positive integers, which gives the middle inequality.
Thus paid leaves and raw instances have the same `exp(O(N log N))` bound.
With one owned center per raw unit, the center count is at most U_N. A rule
with O_local distinct owned banks per invocation instead gets O_local*U_N.
Extra router scratch must be counted separately.

### Routing and word description

Count one routing slot for every source, every exit, every unit target slot
and every unit paid position. At one flow its count is at most
`2*(W+P)*U`. The same bound telescopes over all recursive calls, because
each call contributes its own local unit instances. Exact compilation checks
this identity alongside widths and leaves.

In the macro grammar that records a whole-job adapter, inverse adapter or
whole-field move as one record, a slot can be handled with at most sixteen
records: up to two whole-job conjugations and their inverses, park/load/
return/reorder moves, and explicit scratch initialization and erasure.
Allocate separate owned scratch for those moves when needed; no zero-cost
routing or free copying is assumed. Let A bound the fixed unit's complete
nonrecursive record count, owned operations and scalar coefficient heights.
The final weighted record allowance satisfies the conservative bound

```
R_bar <= A*U_N + 32*(W+P)*U_N + P_N
      <= (A+32*(W+P)+1)*B_N*N,  for Delta>=1.
```

R_bar bounds both the macro count and the sum of scalar-height and native
record allowances. Every owned bank has an explicit initialization record,
so total allocated owned banks can also be bounded by R_bar; the sharper
raw-center bound remains separate. This is a **description/record bound**,
not a new tariff for executing a
general matrix or permutation. A Gaussian monomial adapter's dense binary
address matrix and quadratic phase have O(N^2) descriptor bits. Explicit role indices add O(log B_N)
bits. Thus an encoding of this finite word still has
`exp(O(N log N))` bits for a fixed unit and its finite coefficient alphabet.
If physical expansion of one adapter needs F(N) native records, multiply
the routing term by its actual F(N). That physical implementation, coefficient
heights and tape costs remain separately priced native obligations. They
are not set to zero by the macro bound.

## 4. Applying the size result to PR4433

The new nested widths may be used in the separated compiler of PR4433.
Its normalized L(n), ambient N, uniform saving and outer ledger remain
unchanged. Therefore this application does not need the still-open direct
exponent lemma.

With `v=150`, `H=349300000000`, `N=2^H`, the completed mixed rule has

```
W = 7688^150 < 2^1950,
P <= 131115^150 + 7688^150*15^150 < 2^2701,
W+P+1 < 2^2702.
```

The bound on P counts every original and completion call by its positive
rank mass; splitting preserves that mass. Since k_min>=2, h<=H. Set

```
D = 1950 + 2702*(H+1) = 943808600004652.
```

There is consequently a realization of the same proposed conditional
κ=0.00268647 supplier satisfying

```
B_N < 2^(D * 2^H),
P_N < B_N * 2^H.
```

More finely, after expanding every product, padding, split and compiler call
back to the raw p7 word, that word has surplus 608. Product/completion/split
boundaries cancel, so

```
B_N*N − P_N = 608 * sum_raw_p7_instances column,
U_raw <= (B_N*N − P_N)/608.
```

This is also an explicit bound on raw p7 center banks under the safe
one-center-per-instance allocation. These are large upper bounds, not
emitted words, smallest widths or practical precision estimates. They replace
one implicit part of the source finite-constant prescription. The native
adapter bodies, analytic transfer and physical costs retain their original
conditions; a closed bound for the source's finite-constant prescription is
given next, without a new physical runtime or exact-recovery threshold.

### A closed envelope for the source finite constants

The exported THREE-base native word has exactly 22,633 records in each
orientation. Source-bound counting retains all 15 copies, the literal p7
controller, scalar allowance 2,490,856, every productive/paid/contact/helper/
idle slot, and all routing and owned operations. A raw macro allowance is

```
A_raw = 15*8*(decompressed native JSON bytes)
      + 8*(literal controller JSON bytes)
      + 32*(2490856 + all declared slots + 15*22633) < 2^40.
```

The payload-bit terms overcount the coefficient literals and full local
descriptors, including both orientations. The 32-per-slot term overcounts
whole-job normalizers and inverses, field movements, initialization and
erasure. It is a bound on the declared source word in this grammar, not
independent verification of its functional correctness or physical tariffs.

For the chronological v-fold product, its number of raw p7 invocations is

```
U_v = sum_(i=0..v−1) 7688^(v−1−i)*55998^i < 2^2392.
```

At every product level retain the whole-job matching wrappers. A conservative
product allowance is

```
A_product <= (2^40 + 32*v*(7688+55998+1))*U_v + 32*v*55998^v.
```

Add 32 records for every final paid call, completion role and original paid
position. Counting paid calls by their rank mass gives

```
A_completed <= A_product
    + 32*(131115^v + 7688^v*15^v + 7688^v + 55998^v).
```

A dense local binary map/quadratic phase and role index fit in
`64*(121^v)^2` bits per such record. The verifier checks the integer bound
`A_completed * 64*(121^v)^2 < 2^5000`. Thus **A=2^5000** is a valid weighted
record/description allowance for this fixed completed unit. It includes all
source coefficients and owned operations, with a large deliberate overcount.
No instruction list of the completed product is emitted.

Since `A+32*(W+P)+1 < 2^5001`, use the envelope

```
R_bar < 2^(D*2^H + H + 5001).
```

Apply the existing source finite-constant prescription to the **newly expanded
word**. With Z=B_N+owned banks, G its scalar coefficient envelope, and P_N
its rank-one leaves, we have `Z<=2*R_bar`, `G<=8*R_bar`, `P_N<=R_bar` and
`N<=R_bar`. Therefore

```
E = 64*(Z+N+P_N+G+1)^3
  < 2^(3*D*2^H + 3*H + 15021),
B_constant = P_N+E,
C0 = 32*N*B_constant^2
   < 2^(6*D*2^H + 7*H + 30049)
   < 2^(8*D*2^H).
```

The last comparison uses `2^H>=H+1` and an exact polynomial integer check
on D and H. These are explicit, very loose upper bounds for the inherited
semantic precision/stock constants, conditional on that source prescription
and its admitted native record implementations. The exact numerical outer
input threshold, prime exclusions and physical tape costs remain separate.

## 5. Exact finite checks and the open exponent gate

The verifier uses no floating-point acceptance tests. It checks:

- Nine literal/merged flows at ranks 20, 40 and 80: a separated control,
  strict overlap `{2:1,5:1} <- {1:2,4:1}`, and Sussman's open equality
  example `{2:4,3:1} <- {1:6,2:2}`. Every whole input and exit agrees.
- The separated control agrees with the unchanged Sussman literal replay.
- Complete nested-width compilations through rank 100 on both overlap
  examples, checking every recursive batch, routing count and rank identity.
- Raw p7 through rank 1,000: **880 exact nonbase compilations**. B_1000 has
  17,504 bits; the saved receipt binds all large computed integers by their
  unsigned big-endian hashes, avoiding enormous decimal dumps.
- Removing premature exits violates mass conservation. Removing batch
  replication fails integer divisibility. Allowing a paid rank equal to
  the ambient rank is rejected because strict rank descent is unavailable.

For raw p7 at rank 1,000, exact arithmetic gives

```
L(1000) > 990 > 1000^(1−0.00268647).
```

The second comparison is elementary and exact: `ln(2)>2/3` from its first
atanh term and `1000>2^9` give `ln(1000)>6`. Then
`1000^κ > 1+6κ > 100/99`. No log approximation is used in this rejection.
This checks one finite failure and keeps it distinct from the infinite-rank
question.

The missing lemma is a uniform bound on the **whole** recurrence. For some
fixed p and sufficiently large n, one would need, for example,

```
sum_e E_e e^t (1+log2(e))^p
 + sum_s S_s (n−s)^t (1+log2(n−s))^p
 <= S_n n^t (1+log2(n))^p,
```

with zero-rank terms defined separately and a correctly funded base range.
The premature exits have rank proportional to n. Their logarithmic factors
cannot use the old fixed theta<1 power contraction. A raw moment advantage
alone does not prove this inequality.

Exploratory `approximate_leaves` in flow.py evaluates the recurrence in
floating point and is deliberately excluded from verification. A bounded
run through 20,000 ranks found saving about 0.000827 for the default height;
varying the height did not approach 0.00268647 there. This is local search
evidence, not a lower bound or a reason to enlarge the same scan. A better
boundary estimate or a changed flow is the next research obligation.

## 6. Reproduction and provenance

Python 3.12, standard library only:

```sh
python3.12 -B research/direct-mixed-flow/verify.py
python3.12 -B scripts/research_package.py --package research/direct-mixed-flow --check-only
python3.12 -B scripts/research_package.py --package research/direct-mixed-flow
```

Use `verify.py --out /absolute/new/result.json` for a fresh receipt.
[RESULT.json](RESULT.json) contains exact flows, integer compilation hashes,
symbolic size bounds and negative controls. `flow.py` is the new algorithm;
the verifier independently compares its merged and literal traversal outputs.
Those are two internal implementations, not an independent mathematical review.

Canonical base is `12fa8c5c844be21bfefb38a19503fbd867a11244`, priority revision
7. SOURCES.json pins orientation metadata. VENDOR.json separately binds eleven
unchanged exports by commit, full path, Git blob and SHA256. Their bytes and
notices are preserved; direct replay needs no foreign Git objects. The source
theorem and earlier finite compiler remain attributed hypotheses, not new work.

Local validation used Python 3.12.8 on macOS arm64. The registered replay,
metadata/pin check and committed-byte preflight passed. A separate Git-free
copy passed with `python3.12 -I -O -B verify.py`; changed-native-source and
changed-receipt controls both rejected. Replay uses exact integer arithmetic
and source hashes, with no network or foreign Git objects. The repository is
shallow, so a full source-history preflight was not attempted. No Lean, Docker,
full native/all-column admission, physical adapter expansion or historical
suite was run. Independent mathematical acceptance remains open.

The overlap refresh at 18:48 UTC covered 538 open PR bodies and 3,280
discussion/comment records, with complete reported pagination. Specific
searches for direct overlapping-rank compilers, Pascal matching and nested
widths found no matching public item in that scope; this is not a novelty
certificate. Existing PR4433 supplies the fixed-rank application, and the
source theorem explicitly leaves the unseparated exponent open. No Discussion
claim or PR has been posted for this partial checkpoint.

## Open next questions

1. **Close or refute the direct exponent gate for this capped flow.** Start
   with a proved bound on premature-exit potential relative to the actual
   complement capacity. This decides whether the flow can replace the
   tensor/padding layer. A larger rank scan is not a uniform proof.
2. **Independently admit the physical expansions and precision prescription.**
   Audit the conservative A allowance against the actual native caller and
   bind every adapter's physical implementation, row movements and recovery
   exclusions. The encoded constants above use the inherited semantics;
   description size is not a physical execution tariff.
3. **Tighten the constructive width.** The nested product is an explicit
   upper bound, not an optimized LCM. A useful next step would control prime
   valuations of the actual source counts; another arbitrary batching choice
   would not by itself establish a smaller physical supplier.

Prepared by zxv with substantial OpenAI Codex assistance in research, code
and writing. No subagents or independent human mathematical review were
used. New material is Apache-2.0. The integer lockstep/Pascal construction
and original open unseparated question are Jacob Alan Sussman's work, retained
at upstream `wht-power-saving-lean` commit
`563b4e6e913625637f36ba7869bf5fcd0dd4975a`; its LICENSE and NOTICE are included.
PR4359 supplies the native finite-precompilation bridge and p7 predecessor
lineage. PR4416's p7 product/padding is @1337isnot1337's work. PR4433 supplies
the unchanged sufficient rank. Their original contributor credit remains
in the authenticated exports.
