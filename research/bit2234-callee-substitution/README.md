# Completed-callee substitution at the selected BIT leaves and headers

This is a **conditional compiler-interface proof and finite endpoint audit**.
At the two ordinary-interchange APIs in Jose Manuel's
[PR2234](https://github.com/CrocSwap/integer-mult-bounds/pull/2234), a completed
binary interchange of saving `a` can replace a whole radix-`q` field exchange
with cost `O(V u^(1-a))`. Only the exchanged fields are padded, their joint
volume grows by less than four, and padding closes before the next operation
in the original ring. Prefix, gap and suffix fields are never padded.

Applying the substitution to **both** weighted leaves and reversed header
ADDs changes their width toll from `w` to `w^(1-a)`. Under the remaining
PR2234 physical and moment contracts, the source stopped recurrence then has
local toll `C V(n+w^(1-a))`. This supplies one specific implementation premise
of [Adam Gall's PR2087](https://github.com/CrocSwap/integer-mult-bounds/pull/2087)
conditional time lift. Improving leaves alone does not justify removing
PR2234's header `O(Vw)` toll.

The conditional second-round ordinary saving at the unchanged coarse point
`c=17/10000` is `c(1-c)+c[c(1-c)] = 1699995087/10^12`.
This is an instantiation of the inherited bootstrap formula, **not** a new
selected supplier or multiplication exponent. It remains below the selected
BIT rate. The contribution is the concrete substitution and its proof
obligations, not another evaluation of that formula.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

## Exact scope and sources

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The claim is in [Discussion #2209](https://github.com/CrocSwap/integer-mult-bounds/discussions/2209#discussioncomment-18942787).
The card and refinement are in [TASK.json](TASK.json).

The implementation predecessor is PR2234 head
`d047ef86fbc5b1614d3d8e2b8d3441413beab73f`, specifically `leaf.py`,
`header_streams.py`, `low_update` in `vendor/qadic_streams.py`, and
`PROOF.md` sections 4–8. PR2087 head
`b5ffc48e3dd5c92f591bdb4fabafa2c8e8b33970` is a contextual proof predecessor.
[SOURCES.json](SOURCES.json) binds exact Git blobs and SHA256 values of unchanged
copies. No pending branch must be checked out to replay this package.

The two-field adapter lemma works for every integer `q>=2`. The source
dyadic headers require odd `q`; the whole-node and second-round corollaries
retain the source's fixed prime `q>2^80`. Small `q=3,5` fixtures test local
identities, not the large-prime fallback fraction.

The following are **assumptions**, not conclusions from the finite tests:

1. For fixed `0<=a<1`, the earlier binary algorithm `B_a` is completed at
   **every** positive binary width `E`, with cost at most `C_b V E^(1-a)`.
   It exchanges two ordered complete `2^E` ranges while preserving arbitrary
   complete prefix, intervening and suffix fields, and arbitrary correlated
   Boolean payload. Its constant is uniform in their cardinalities and
   contents. Its endpoint is an ordinary exchange, not a reversed exchange
   or merely a clean return.
2. `B_a` restores borrowed row/spectator coordinates, caller parking and head
   positions, and clears local work. It requires no reserve from the caller:
   internal borrowing is part of its completed contract. The fixed-tape
   parking/locality contract remains in force.
3. Retained ordered shifts, fixed dyadic scales, signs, selectors and
   coefficient preparation have their stated uniform stream costs. For
   the whole-node corollary retain PR2234's causal generated expressions,
   complete high packets, chronological endpoint/hosting argument, fresh
   stock, proper child descent, uniform preparation amortization and moments.

These hypotheses explicitly include nonbinary spectator cardinalities.
A theorem only for binary-complete spectators needs an additional adapter.
Padding every ancestor field is not part of this result. The instantiated
`B_a` from PR2234 is itself pending mathematical review.

## Two-field substitution lemma

Fix integer radix `q>=2`, integer `u>=1` and positive integers `P,G,S`.
An input stream has lexicographic shape

```
[P] x [Q] x [G] x [Q] x [S],    Q=q^u,    V=P Q^2 G S.
```

`S` may include all following spectators and the payload block length.
Put `E=ceil(log2 Q)` and `L=2^E`. Pad the two `[Q]` fields separately to
`[L]`: scan the enlarged lexicographic shape, copying the next genuine
payload exactly when both field coordinates are below `Q`, and writing an
owned zero otherwise. Call `B_a` **once on the entire padded stream** with
the same `P,G,S`. At its completed return, restrict to those inequalities.

**Endpoint.** Let `J` exchange the two fields. The genuine rectangle
`R={x<Q,y<Q}` and its complement are invariant under `J`. Thus
`J pad = pad J_Q` and `restrict J pad = J_Q`. Every genuine bit appears once
with prefix/gap/suffix coordinates unchanged. The complement contains only
owned zeros again at return, even if intermediate operations mix genuine
and padded positions. Its removal loses no payload. The old algorithm's
complete return contract, restriction and scratch erasure give the same
head, row and parking boundary. For `u=0` the fields are singletons: the
adapter is identity and invokes no zero-width instance of the old theorem.

**Uniform bill.** `Q<=L<2Q`, so `V<=V'=P L^2 G S<4V`. With
`b_q=ceil(log2 q)` one has `E<=b_q u`. For `p=1-a` in `(0,1]`,

```
C_b V' E^p <= 4 C_b b_q^p V u^p <= 4 C_b b_q V u^p.
```

Padding/restriction use sequential scans of `V` and `V'` and a fixed number
of tapes. Preparing `q^u`, bit length and loop bounds costs a fixed polynomial
in `u` for fixed `q`; minimum active volume `q^(2u)` absorbs this with a
uniform finite coefficient. Binary ripple counters advance incrementally;
unrelated spectator counters are not reread per item. Under the retained
charged-scan model, absorb this work as `C_pad V`. Because `u^p>=1`, the
whole cost is at most `(4 C_b b_q+C_pad) V u^p`, with constants independent
of `u,P,G,S`. This written bound is not inferred from Python timings.

The adapter closes padding for **each exchange** and does not change the
coefficient ring. At `q=3`, `D<-D+H` on `(H,D)=(1,2)` gives target `0`
modulo 3 but `3` modulo the padded size 4. Keeping padding live across that
original-ring ADD is an invalid shortcut.

## Binding the two source APIs

`adapter.py` supplies the two-field wrapper and a completed slow binary
reference callee using four sequential buckets per digit position.
`verify.py` compares its full permutation with a separate address oracle.
Distinct symbolic tokens certify arbitrary Boolean payload for these
value-oblivious permutations; tokens are not an expanded physical alphabet
claimed for the machine.

**Weighted stopped leaf.** `leaf.py:execute_leaf` has, for each of its
`n<64` reversed pairs, the exact chronological word

```
J, L(a_i), J, L(-a_i^-1), J, L(a_i), J, sign_D,
```

where `L(t)` updates the later field by `D<-D+tH` in `Z/q^w`.
For frozen unit `a_i` this sends `(H,D)` to `(a_i D,a_i^-1 H)`:
just before the final sign the pair is `(a_i D,-a_i^-1 H)`.
The unit may depend on earlier frozen ancestors, but not either changing
field. The reversed pairs are disjoint and compose to
`F_A(H,D)=(A C_n D,C_n A^-1 H)`.

The successor uses four whole-field calls at `u=w`, three retained shifts
and one sign per pair. Its cost is a fixed multiple of `Vw^p`, uniformly
for `0<=n<64`; a peeled leaf of at most 63 pairs has the same bound.
Its returned coordinates and private work match the original leaf.
The original `4nw` digit-swap meter is specific to its elementary backend;
it is not silently disabled. A separate successor checks `4n` completed
calls and their padded volumes/widths. The verifier authenticates and
checks the source operation sequence, then checks the successor endpoint.

**Fixed dyadic headers.** `header_streams.py:add` uses `ordinary_fields`
before and after the forward update when the fields are reversed, at
`u=w-1`. At `w=1` the high fields disappear and no call is made. Otherwise
preceding complete high coordinates enter `P`, intervening fields enter
`G`, and trailing coordinates enter `S`; neither call is split by a high
matrix value. Each costs `O(V(w-1)^p)<=O(Vw^p)`.

The unchanged middle operations scale, rotate and inverse-scale in
`Z/q^(w-1)` with the original carry. For `c=A/B` and new low target `y0'`,
the carry is `(B y0+A x0-B y0')/q`; the high target is
`B^-1(B y_high+A x_high+carry)`. This is the original full-ring update.
The fixed coefficient alphabet is `+-1/4,+-1/2,+-1,+-2,+-4`, so the number
of monotone scale pieces is bounded independently of `w`. Other fixed
header operations retain their `O(V)` charge. Each fixed route consequently
costs `O(Vw^p)`.

The header replay executes the **unchanged source bodies** of `add`, its
scale/rotate helpers and `low_update`, replacing only `ordinary_fields`.
Hashes are checked before extracting these function definitions. The
symbolic tape interpreter checks append/read positions, consumed inputs
and scratch erasure; it is not a full transition-table audit. Callback
return flags state obligations: a flag cannot prove an arbitrary callee's
parking trace.

## Conditional node and second-round consequence

Retain the source caller and its uniform cost decomposition. There are
`O(n)` ordered atom passes, a fixed number of header routes, one peeled
leaf and a fixed number of selections/parking operations. The two changed
sites cost `O(Vw^p)`; other charges remain `O(Vn)` or `O(V)`. Hence one
width-independent `C` gives `C V(n+w^p)`, including preparation and parking.
No coarse recursive children are added: the **earlier completed** algorithm
is included in the local toll. Its own borrowing does not consume the
current caller's reserve, by its full restoration contract.

Retain PR2234's exact profile, fallback maximum and inequalities
`mu_1<199/200`, `mu_(1-c)<9999/10000`. The same proper-width induction gives

```
T(n,w) <= 200 C n + 10000 C n^(1-c) w^p,    n>=1.
```

The linear margin pays `Cn`; the power margin pays
`C n^(1-c) w^p >= Cw^p`. At a leaf `n^(1-c)>=1` pays the leaf bound.
The fallback maximum is bounded by the increasing comparison function,
without assuming actual `T` is monotone. `n=0` is identity. This is inherited
recurrence algebra from PR2234/PR2087 and PR2289/2295. The fractional moment
is not independently recertified here.

For the next round take `a=c(1-c)`, keep `w=ceil(e^c)` and the original-width
reserve `K(w)^D(e)`. A completed old callee needs no extra parent-stock
factor. The borrowing/fit argument and two-call ordinary wrapper apply
under the retained row-restoration contract. With `n<=e/w`,
`e^c<=w<=2e^c` and `0<a<c`,

```
n^(1-c) w^(1-a) <= e^(1-c) w^(c-a)
                     <= 2 e^(1-c+c(c-a)).
```

The linear term has exponent `1-c`. Even retaining elementary
outside-recursion remainder/high-part exchanges costs only
`O(V e^c(1+log e))`, strictly below the displayed main exponent. The source
finite-small-width fallback is absorbed into a constant. Final fixed-radix
binary padding has its original fixed factor. The conditional saving is

```
a_2 = c-c^2+c a = c(1-c^2) = 1699995087/1000000000000.
```

Constants may depend on the fixed earlier stage and fixed `q`, not current
width, cutoff, spectator contents or ancestor stack. This does not identify
the fourteen selected stage coefficients or admit the full construction.

## Reproduce and evidence boundary

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B research/bit2234-callee-substitution/verify.py
python3 scripts/research_package.py --package research/bit2234-callee-substitution --check-only
python3 scripts/research_package.py --package research/bit2234-callee-substitution
```

The direct replay prints `PASS_BIT2234_CALLEE_SUBSTITUTION` and checks:

- 40 whole-field cases at `q=3,5`, `u=0..3` and five distinct
  prefix/gap/suffix shapes, retaining every address in each case; also all
  512 Boolean payloads at `Q=3`, through a callback accepting only bits;
- seven full weighted leaves, including the empty leaf, two-pair reversal,
  nonconstant frozen ancestor units, nontrivial gaps and trailing payload;
- 1,480 source header ADD executions, both orientations and all ten dyadic
  coefficients. All low classes are checked at `w=1,2`; at `w=3` the low
  pairs `(0,0),(1,q-1),(q-1,1)` are used, with every high coordinate;
- exact source call inventory, integer padding bounds, conditional rational
  exponent arithmetic and 16 semantic/receipt control cases.

Controls reject a clean identity substituted for a swap, wrong
head/cleanup/parking declarations, changed spectators,
payload leakage into dummy positions, incomplete inputs, nonunit weights,
wrong inverse or omitted sign, omitted return exchange or carry, duplicate
JSON keys and boolean/integer drift. The wrong-modulus witness explicitly
invalidates padding across an original-ring ADD. Source/receipt corruption
controls also exercise the public CLI. [RESULT.json](RESULT.json) records
exact counts and permutation digests.

The all-width statement rests on the written argument and named hypotheses.
The executable binary reference has elementary cost, not the faster pending
rate. We have not run the full GL64 selected payload, full supplier cold
replay, actual fast old callee, finite-alphabet compiler or Lean proof.
Physical preparation, dispatch, chronological hosting, analytic transfer
and the full multiplication theorem remain open here. No independent
human review or hosted CI success is claimed.

## Open next questions

1. Can an actual faster completed callee replace `binary_reference` with the
   stated spectator, restoration and parking contract? First join one
   nonadjacent field exchange to that caller with arbitrary dirty spectators
   and source-bound cleanup checks. PR2364 supplies generic joined packets; its Discussion #2319 follow-up on
   physical prefix decoding is complementary. Earlier caller review and a
   completed faster backend remain prerequisites.
2. Can this substitution be instantiated at a sharper retained moment point
   and the selected fixed stages? First bind the changed stopping exponent,
   preparation domain, reserve and previous completed algorithm together.
   The first-round caller review and actual stage coefficients still block
   selected admission.

## Credit

Jose Manuel / PR2234 supplies the implementation and source contracts.
Adam Gall / PR2087 supplies the conditional time lift. The source527 weighted
factorization, selected PR589/555 lineage, earlier normalizers, descriptors,
fixed routes and parking remain credited in [NOTICE.md](NOTICE.md) and the
unchanged source notice. The generic bootstrap formula, factorization and
existing moment are not claimed as new. PR2289/2295, PR2310, this account's
PR2332, PR2324/2343 and PR2364 have distinct scopes. PR2364 at
`b9293bb14d40f8e820ce5efd99939278e5871c56` executes generic joined packets;
Discussion #2319's current prefix/coefficient-site follow-up explicitly
excludes this leaf/header bootstrap audit. No replay of PR2364 is claimed.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0. No independent human or proof-assistant review is claimed.
