# A finite rank compiler with one productive tensor grade

## Contract

A source word has true ambient rank `A`. At each positive integer column count it has the **same finite ordered list** of local instructions and paid requests. A productive role has its own arbitrary complete field. A paid request acts on its actual current owner, which may be an owned center. At a completed boundary, an explicit invertible adapter on the whole field identifies each target or request with a positive transform on specified coordinates and the identity on the other coordinates. The inverse adapter returns before the next dependent instruction. Positive transforms on disjoint axes compose to the transform on their union. Local storage, scalar operations, adapters and retirement have their source meanings and costs. [APPLICATION.md](APPLICATION.md) identifies these primitives in the two source alphabets.

Start with normalized target and paid boundaries. In the complex source a native endpoint can be `L C_s R` with distinct, two-sided factors. Apply the prescribed two factors in their source order, including their absolute phases. Only an extra placement that permutes coordinates or role rows is undone by its own inverse. Write `W_k` for the number of target roles of rank `k`, and count each occurrence of each positive paid rank `r` in chronological order. All ranks lie in `[1,A]`. Assume a nonempty paid list and at least one target of rank greater than one. Put

```text
T(s) = sum_k W_k k^s,        P(s) = sum_j r_j^s.
```

Fix `0<t<1`. A product grade is the integer product of the ranks on one target path. We permit a positive integer power of one source word, a subset of the slots of *one* product grade, specialization of all other source inputs to zero, and disjoint positive splits of every oversized paid request. Every paid position of the powered word is kept. The strict test for this intermediate word is `sum_i h_i^t < B K^t`, where the `B` retained slots have rank `K` and all split ranks `h_i<K`.

**Criterion.** This intermediate word exists if and only if, for every real `s` in `[t,1]`,

```text
log T(s) > ((1-s) log P(t) + (s-t) log P(1)) / (1-t).
```

Under this condition a finite compiler produces independent full-rank outputs with only rank-one paid calls. For each `z>t` there is a fixed `N` with `P_N / W_N < N^z`. The construction is effective for rational prices, or with computable prices and certified strict margins. For fixed source and fixed trial price its width and its number of pre-cover instruction records grow polynomially in the terminal rank `N`. In the five source applications below the common cuts also give a fixed polynomial degree as the trial price approaches the raw crossing. The criterion of necessity concerns the stated intermediate-word grammar. Changed native words, mixed retained grades, paid cancellations and other compilers can have different criteria.

## Construct the native product

Here and below the compiler manipulates a finite operation list at a fixed rank. There is no oracle for a recursive job or for a uniform compiled supplier.

Compose words `U,V` with true ambients `a,b`. In an `a b`-axis space put a separate `U` instance at multiplicity `k_j(V)` for each productive role `j` of `V`. Give each instance its own arbitrary input fields and owned banks. Complete the unused axes as spectators. Advance every instance to the *same* chronological paid position of rank `r` in `U`. The resulting owners are distinct, including when a local request uses an owned bank. The complete `V` word at multiplicity `r` acts on these owners. Its role `j` has precisely the requested `r k_j(V)` active axes. Apply the role-specific complete normalizers, execute `V`, undo the normalizers and resume each suspended instance. Both working windows fit because `a k_j(V)<=ab` and `b r<=ab`. Use fresh banks at each occurrence. The same argument works at any further positive integer lift. It gives targets `k_i(U) k_j(V)` and paid ranks `r_i(U) r_j(V)`. This is Cinna Davis's chronological product construction with explicit independent working ambients. [Product proof](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/pr4359-tensor-strictification/TENSOR.md)

For power `v` the true work window is `M=A^v`. A type has counts `n_k` with sum `v`, grade `K=product k^n_k`, and exactly `B=v! product W_k^n_k / product n_k!` distinct input slots. In particular `B K^s<=T(s)^v`. Keep those slots. Supply fresh owned zero fields for the other slots, run their instructions, and retire them after their completed outputs. Each discarded output is its own transform applied to zero. No issued request can be dropped, including a request on a bank that currently happens to be zero. This specialization uses distinct storage and preserves the original scalar word. It applies to all arbitrary values on the retained fields. Additional types with the same grade need not be credited.

## Proof of the criterion

Any split of `R` into positive pieces smaller than `K` has moment at least `R^t` by subadditivity, and at least `K^(t-1) R` by summing over its pieces. Thus success implies `BK^t>P(t)^v` and `BK>P(1)^v`. Interpolate the logarithms of these two strict inequalities. The line `log B+s log K` is below `v log T(s)` even if several types with grade `K` are used. This proves necessity.

For sufficiency let `f=log T` and let `L` be the paid chord in the criterion. Choose a minimizer `u` of `f-L` on the closed interval, and put `eta=f(u)-L(u)>0`. The derivative of `f` is the mean of `log k` with weights `w_k=W_k k^u/T(u)`. Its second derivative is the variance of `log k`. At an interior minimizer the derivative matches the slope of the chord. At either endpoint its one-sided sign gives, for both `s=t,1`,

```text
f(u) + (s-u) f'(u) - L(s) >= eta.
```

Choose a modal term of the multinomial expansion of `(sum w_k)^v`. There are at most `(v+1)^d` terms, where `d` is the number of distinct target ranks. Its type gives `BK^u >= T(u)^v/(v+1)^d`. To see how close its rank is to the tangent, first take `floor(v w_k)` occurrences of each rank. Their priorities `w_k/j` are at least `1/v`. All next priorities are smaller. Pick the remaining, at most `d-1`, by the largest next priority. This maximizes `product w_k^n_k / n_k!`. Since the total deficit from the ideal allocation is at most `d`, the error in `log K - v f'(u)` has magnitude at most `d log(k_max/k_min)`. In particular `K` grows exponentially because `f'(u)>0`.

Consequently `BK^t/P(t)^v` and `BK/P(1)^v` both grow at least exponentially divided by a fixed polynomial in `v`. Set `J=floor(K/2)`. Split each paid product rank `R>J` into consecutive jobs of rank `J` and a final positive remainder if needed. Keep the entire original adapter around the split. For large ranks its charge is at most `2 R J^(t-1)`. The complete cost is therefore at most

```text
P(t)^v + 2 J^(t-1) P(1)^v.
```

As `J>=K/3`, the ratio of this expression to `BK^t` tends to zero. Choose a power giving a ratio `mu<=1/2`. For rational input prices there is an effective search without a real-valued tie oracle. Enumerate powers and types, split using integer ranks, and compare the finite sums by successively refined rational intervals until a strict success is found. Dovetail the comparisons so equality at one candidate cannot stall the search. The preceding proof guarantees termination. The explicit application certificate takes a shorter route.

The two endpoints alone cannot replace the interval condition. For `T(s)=70+256^s`, `P(s)=18·16^s` and `t=1/2` the endpoint comparisons are `86>72` and `326>288`. At `s=3/4` the target is 134 against the required 144. Necessity rules out every power and every single retained grade of this word.

Even strict raw moment advantage at *every* price can fail this grammar. Take `T(s)=2+256^s` and `P(s)=1+256^s`. At the midpoint the chord condition would require `66²>17·257`. It fails by 13. Conversely, an interior tangent can succeed when the trial-price tangent fails. For `T(s)=25+256^s`, `P(s)=8·16^s`, let `y=16^s`. Then `T(s)/y=25/y+y>=10>8` everywhere. The tangent at `t=1/2` misses the rank-one endpoint since `41^41·256^8<128^41`. At power 12 retain six slots of each rank on every target path. This type gives `K=16^12` and `B=binom(12,6)25^6`. Splitting each of the `8^12` paid requests in two gives `mu<1/2` by the integer test `8·8^24<B²`. These are tests of the rank grammar.

## Expand a job inside its original ambient

Fix an intermediate word with `B` targets of grade `K`, true window `M`, and split paid list `h_i<K`. Reserve the whole root space of `N>=2M` axes. A job specifies its owner, complete normalizer and `e` active axes. Its argument is the entire original field. It fixes every inactive coordinate at return, although its temporary scalar operations can use that coordinate. Each input needs `N` working axes once. Descendants inherit the same space.

For `e<K` pay for each axis of the requested job. Otherwise set `c=floor(e/K)`. On each complete owner put the requested axes first by an invertible adapter. Apply the word to its first `Kc` axes, using the first `Mc` axes as its working window. After the word returns, pay the `e-Kc` remaining axes on the same owner. Undo the adapter. Inputs with individual native charts get their own normalizers before they enter a common scalar instruction. A child of rank `h_i c` has a strictly smaller active rank and needs at most the parent's work window. No child allocates a missing tensor axis. No child discards the prefix, the remainder, or an external row.

Let `D(e)=0` below `K`, and otherwise `D(e)=1+D(h_max floor(e/K))`, with `h_max=0` for an empty paid list. It is nondecreasing. A batch divisible by `B^D(e)` splits into disjoint groups of `B` complete owners. Run their instances to the same paid position. Each group supplies exactly one paid owner at that position. Their count is divisible by `B^(D(e)-1)`. Recursively service this batch and return its fields, frames, sockets and role order before the next position. Correlated center values on distinct actual owners are permitted by arbitrary-input linearity. Clearing the denominator here consists entirely of taking an integer power of one width. Partial data from one field never count as two productive inputs.

At the root partition the `N` active axes into consecutive tiles of capacity `K floor(N/M)`, with a final shorter tile. Use one fixed batch of `W_N=B^D(capacity)` arbitrary fields for *all* tiles in sequence. Each field receives exactly one full rank-`N` job. Every tile uses at most `N` axes. Only the root pays for multiple tiles. The reference implementation emits normalized native instructions and rank-one leaves in this order. [Schedule](schedule.py)

Let `F(e)` denote leaf count per input within one tile. For `e<K` it equals `e`. At all higher ranks the exact recurrence is

```text
F(e) = (e mod K) + (1/B) sum_i F(h_i floor(e/K)).
```

Its solution satisfies `F(e)<=2 K^(1-t) e^t`. In the induction the tail costs at most `K^(1-t) e^t`. The children use at most `2 K^(1-t) mu e^t`. The number of tiles is at most `3M/K`. Concavity over their actual lengths, which sum to `N`, gives

```text
P_N / W_N <= 2 (3M)^(1-t) N^t.
```

Choosing `N=2^H` with `H(z-t)>1+(1-t)(2+v ceil(log2 A))` and `N>=2M` suffices. All productive credit belongs to those `W_N` independent inputs. A single public root has no divisibility assumption beyond the separately reserved physical row stock in the outer algorithm.

## A polynomial bound for the actual sources

The five checked profiles allow `J=8^v` and `K>=16^v`. For a trial saving `p=1-t`, [funding.py](funding.py) uses 275-bit lower bounds `a_k` on `W_k k^t` in a common dyadic unit. Let `S` be their sum in real units. It checks `S>P(t)`, `S·8^p>P(1)`, and computes a modal type for the rational weights `a_k/sum a_k`. The previous type bound applies with `S` in place of `T(t)`. A directed log sum verifies its actual grade. For `v=2^j` it certifies `v·min(1-P(t)/S, log(S·8^p/P(1))) >= d(j+1)+3`. Hence the split paid-to-productive ratio is at most `3/8`. The code also verifies the cutoff margin and `f'(1-p_max)>log 16` at `p_max=1/250` (historical p7 uses `3/1000`). By convexity the cutoff remains valid throughout the price interval whenever the raw moment is strict. A finer arithmetic grid can be required arbitrarily near equality. The finite witness stores the exact type counts without expanding its factorials.

Every paid rank descends by a factor of at least `2^v`. At level `j>=0` an actual native call requires `16^v<=N 2^(-jv)`. Thus `D<=floor(log2(N)/v)` with no extra level or price-dependent width factor. If `B0=sum W_k` and `Q0` is the raw paid count, then `B<=B0^v` and **`W_N<=N^ceil(log2 B0)<=N^16`**. This also holds for smaller roots run sequentially. The bound is in the final uniform rank, before the binary cover.

Here is a conservative expanded instruction bound. The number of paid children of a macro is at most `(A Q0)^v`, even if every paid product were split to individual axes. Thus visits at all levels per root tile per initial owner are bounded by `(1+(A Q0)^v)^D<=N^ceil(log2(2 A Q0))<=N^27` (for `D=0`, one base visit). Replicas grouped into one call only reduce this bound. A native product uses `sum_{i=0}^{v-1} B0^(v-1-i) Q0^i` raw occurrences. At each product boundary charge both complete matchers for each routed role. Counting the levels, bindings and terminals gives at most a source-dependent constant times `(v+1)(B0+Q0+A Q0+2)^v` local records per macro, including specialization, paid slices and retirement. For example, each contraction matches at most `B0^v Q0^v` only in a naive cross-product enumeration. The chronological product instead has at most `v(B0+Q0)^v` such bindings: a routed role at an internal product boundary is specified by a target prefix, one paid position and a paid or target suffix of total length at most `v`. Equivalently, adjoining one outer factor starts `B0^i` raw instances, adds at most `2Q0 B0^i` whole-job matchers at that boundary, and invokes `Q0` copies of the existing inner product. Summing this recurrence gives the stated bound. Each raw occurrence contributes its own full fixed raw-record allowance.

For these profiles `B0+Q0+A Q0+2<2^27`, `A>=2^6` and `N>=A^v`. The macro bill is `O_source(N^6)`. There are at most `N` root tiles. Even charging another factor `N` at every visit for rank-one peeling, the fully expanded instruction and reserved-bank occurrence counts are **`O_source(N^51)`**. The degree and multiplicative primitive allowance can be taken independent of the trial price within the checked family. This is a logical record count. It does not price one physical field as one bit, bound the cardinality of the binary cover by a polynomial, or establish the bit size of every rational matrix. [APPLICATION.md](APPLICATION.md) pays the complete physical volumes, descriptors, prime exclusions and primitive thresholds after fixing the word.
