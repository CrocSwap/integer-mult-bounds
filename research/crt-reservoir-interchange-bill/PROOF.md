# The #4174 reservoir exchange as ordinary H-bit interchange calls

**Scoped counting proof, conditional on BIT.md's ordinary-interchange
theorem as stated. No new κ.** The selected conditional exponent stays
60403/20000000.

**Attribution of the parts.** Parts (i)–(ii) are this package's
contribution: the placement as ordinary calls and its call count. Parts
(iii)–(iv) were first obtained by James Reed in pending PR #4942
(`research/crt-interchange-width-threshold`, head
`32fa3600a0e739d47dca98fdeb3abceda073f9f2`). #4942 also proves that every
width above the threshold is recursive, which is not needed here. Sections
4–5 below are an independent recomputation and agree with #4942. Part (v)
and Remark 4 are additional checks of this package.

## 0. What CRT.md bills, and which callee it means

CRT.md (#4100, Cinna Davis) prices its reservoir and switch gadget with
"an already completed ordinary interchange", costing `O(V h^(1-a))`. The
same file says this interchange "is supplied by BIT.md". BIT.md's statement
is the following. A fixed finite-tape machine

> exchanges two complete equal e-bit binary address fields, with arbitrary
> complete preceding, intervening and following fields, in O(V e^(1-a2))
> time and O(V) visited space.

It "preserves its borrowed input, returns a distinct owned output, fixes
every spectator, erases its work and returns its heads". Its constants
depend on `q = 2^89 - 1` and the fixed source, not on `e` or the payload.
Here `a = a2 = c(1-c^2)` with `c = 8667/5000000`, so `a2 < 1/500`.

BIT.md §4 builds that machine as a wrapper:

1. Embed each `2^e` binary field into `q^E` with `E = ceil(log_q 2^e)`.
   This multiplies the volume by less than `q^2`.
2. At the root, set `w = ceil(E^c)`. Compute `stock = K(w)^{D(E)}` and the
   least `k` with `q^k >= stock`. Here
   `K(w) = 269241600 N q^{4096(w-1)}`, `N = |GL_64(F_q)|`, and
   `D(n) = 0` for `n < 64`, otherwise `D(n) = 1 + D(42 floor(n/64))`.
3. If `2k >= E`, or the body width `n = floor((E-k)/w)` is below 64,
   run the elementary algorithm. That is BIT.md §3's stage `a = 0`,
   "elementary q-digit swaps", which costs `O(V E)`. Otherwise run the
   body word.

**Reading used here.** The "original radix width `e`" of BIT.md §4 is the
radix width `E` of the embedded field, and `w` and `D` are evaluated at
that root call. Remark 4 below gives a bound that does not depend on the
exact `D`.

CRT.md §3 sets `G = 64(ell + ceil(log2(p+2)))`, `r_max = floor(L/(100G))`
and `H = r_max G`. It moves three borrowed `H`-bit fields "using a fixed
number of paid equal-H interchanges" and undoes them at the end of the
batch. PR #4174 (Hiroki KUMAZAKI) constructs these fields. Its PROOF.md
§4 gives destinations `U = [0,H)`, `T = [H,2H)`, `B = [L-H,L)` and
sources `S_0, S_1, S_2` inside the unused interval. All six blocks are
pairwise disjoint. It also states the invoice "at most six width-`H`
ordinary exchanges per batch" and leaves the callee open.

`V` denotes the payload volume, that is `2^L` addresses times the record
length.

## 1. Proposition

Let `(p, ell, widths)` be any layout accepted by the #4174 `Layout`
constructor. Let `π` be any of its plans, with placement `P`. Put
`a = a2`.

**(i) Calls.** For `k = 0, 1, 2`, let `X_k` exchange `S_k` with the `k`th
destination (`U`, `T`, `B`), bit for bit in order. Then
`P = X_0 X_1 X_2` in every order of the factors, and `P^{-1} = P`. Each
`X_k` is one BIT.md call with `e = H`. Its spectators are the other
`L - 2H` address bits and the record. So placement plus restoration is
exactly **six ordinary calls of width `H`**. No other payload action is
needed. Recomputing positions touches only the #4174 descriptor, which
has at most `d + 12` fragments.

**(ii) Bill.** Assume BIT.md's theorem as stated, with constant `C_BIT`.
Placement plus restoration then costs at most

```
6 C_BIT V H^{1-a} + 6 c_own V,
```

where `c_own V` charges for using the owned output in place of the
borrowed input (one copy and one erase). This is CRT.md's
`O(V H^{1-a} + V)` with multiplicity 6 per batch. With #4174's bound of
25,600 batches per synchronized switch layer, a layer pays at most 153,600
such calls.

**(iii) Branch at the actual width (#4942; recomputed).** For `1 <= H < 89·2^88`, the wrapper
runs at `E(H) = floor(H/89) + 1`. It takes the elementary branch for every
`H < H* = 27,706,412`, and the body branch at `H = H*`. Since
`H <= L/100`, every accepted layout with `L < 2,770,641,200` runs all six
calls on the elementary branch. So do the twelve width-`H` shuttles of
CRT.md §4. In particular:

| layout | `H` | `E` | `w` | `D(E)` | `k` | branch |
|---|---|---|---|---|---|---|
| minimal, `p = 1310720`, `ell = 21`, widths 20 | 10752 | 121 | 2 | 1 | 8193 | elementary |
| #4174 production, `p = 9240576`, `ell = 24` | 15360 | 173 | 2 | 2 | 16385 | elementary |
| first body width | 27706412 | 311309 | 2 | 19 | 155654 | body |

**(iv) The elementary branch meets the bill (agrees with #4942).** For `1 <= H < H*`,
`E(H) <= H^{1-a}`. So each elementary call costs at most
`C_0 q^2 V H^{1-a}` plus the `O(q^2 V)` embedding. Here `C_0` is the
per-digit constant of stage `a = 0`. On this range `H^{a} < 2^{1/20}`,
so the saving `H^{-a}` is numerically absent.

**(v) Padding at the actual width.** The literal BIT.md call embeds both
`H`-bit fields into `q^E`. This multiplies the volume by
`(q^E/2^H)^2`, which lies in `(2^{33}, 2^{34})` at the minimal layout
and in `(2^{73}, 2^{74})` at the production layout. So the `q^2` factor
in (iv) is mostly realized, not slack. A direct binary exchange, made of
`H` single-bit swaps, would avoid the padding. That routine is not
BIT.md's machine, and its fixed-tape cost is not proved here.

**Answer to #4938's open question.** Yes. One #4174 three-field exchange
is three ordinary width-`H` calls, and its restoration is the same three
calls. Their cost fits `O(V H^{1-a} + V)` with multiplicity 6. At the
minimal layout, and at every layout with `L < 2,770,641,200`, the bill is
met by BIT.md's elementary fallback alone. The body word and the
`a2` saving play no part there.

## 2. Proof of (i)

By #4174 PROOF.md §4, `S_0, S_1, S_2, U, T, B` are pairwise disjoint
intervals of length `H`. `P` maps bit `S_k[0] + t` to `D_k[0] + t` and
back, for `0 <= t < H`, and fixes every other bit. Define `X_k` as the
same translation on the single pair `(S_k, D_k)`. The `X_k` have disjoint
supports, so they commute. Each is an involution, and their product is
`P`. Hence `P^{-1} = P = X_0 X_1 X_2` in any order.

Fix `k`. The bits outside `S_k ∪ D_k` form at most three contiguous
spectator fields: before, between and after the pair. The other four
blocks lie inside these fields. `D_k` precedes `S_k` when `k = 0, 1`,
since `S_k ⊂ [2H, L-H)`, and follows it when `k = 2`. An exchange of two
fields is symmetric. So `X_k` is exactly the operation in BIT.md's
statement, with `e = H` and "arbitrary complete preceding, intervening
and following fields". The record payload is carried with its address.
The call fixes every spectator, so it moves the record at address `x` to
`X_k(x)` for every `x`. This includes invalid padded addresses and dirty
borrowed values. Three calls realize `P`, and three more realize
`P^{-1}`. The endpoint is the identity on every address.

The transported controls `f'_i = f_i ∘ P^{-1}` and the split-axis
descriptors are #4174 PROOF.md §5. They are metadata, not payload
actions. ∎

## 3. Proof of (ii)

By (i) and BIT.md, the six calls cost at most `6 C_BIT V H^{1-a}`. BIT.md
returns a distinct owned output and preserves its borrowed input. To keep
a fixed inventory, the caller copies the output back and erases it, or
swaps tape roles and erases the old input. Either costs at most
`c_own V`. The batch bound is #4174's. ∎

## 4. Proof of (iii), recomputing #4942

**Lemma R (radix width).** For `1 <= H < 89·2^88`, the least `E` with
`q^E >= 2^H` is `floor(H/89) + 1`.

*Proof.* `q^E < 2^{89E}`. By Bernoulli, `q^E = 2^{89E}(1-2^{-89})^E >=
2^{89E}(1 - E 2^{-89}) >= 2^{89E-1}` when `E <= 2^88`. So `q^E >= 2^H`
holds if `H <= 89E - 1` and fails if `H >= 89E`. The least such `E` is
`ceil((H+1)/89) = floor(H/89) + 1`. ∎

**Lemma W.** For `2 <= E < 2^576`, `w = ceil(E^c) = 2`.

*Proof.* `E^c > 1`. Also `E^{8667} < 2^{576·8667} = 2^{4992192} <=
2^{5000000}`, so `E^c <= 2`. ∎

**Lemma S (stock digits).** If `w = 2` and `D >= 1`, then
`k = 8192 D + j(D)`, where `j(D)` is the least `j` with
`q^j >= 269241600^D`. The values are
`j = 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 6` for
`D = 1, …, 19`.

*Proof.* `N = ∏_{i<64}(q^64 - q^i) = q^{4096} ν` with
`ν = ∏(1 - q^{i-64})`. Then `1 - 2/q < 1 - Σ_{m>=1} q^{-m} <= ν < 1`.
So `K(2)^D = q^{8192 D}(269241600 ν)^D`. Let `j*` be the least `j` with
`q^j >= 269241600^D`. Then `q^{j*} > (269241600 ν)^D`. For the listed `D`,
the exact integer check `q^{j*-1+D} < (269241600 (q-2))^D` gives
`q^{j*-1} < (269241600 (1-2/q))^D < (269241600 ν)^D`. So `j(D) = j*`. ∎

**Lemma B (branch).** `D(E) = 0` exactly for `E < 64`, and then `k = 0`
and `n = floor(E/w) < 64`, so the branch is elementary. For `D >= 1`,
`D` is constant on blocks `[T_D, T_{D+1})`:

| D | block | `2k` |
|---|---|---|
| 1 | 64–127 | 16386 |
| 2 | 128–255 | 32770 |
| 3 | 256–447 | 49154 |
| … | … | … |
| 17 | 114496–174527 | 278540 |
| 18 | 174528–265983 | 294924 |
| 19 | 265984–405311 | 311308 |

For `D <= 18`, each block ends below `2k(D)`, so `2k >= E` and the branch
is elementary. In block 19 the branch is elementary iff
`E <= 311308`. At `E = 311309`, `2k = 311308 < E` and
`n = floor((311309 - 155654)/2) = 77827 >= 64`, so the branch is body.
The verifier evaluates all `E <= 311309` directly. ∎

By Lemma R, `E(H) <= 311308` iff `floor(H/89) <= 311307`, that is
`H <= 27,706,411`. Finally, `r_max <= L/(100G)` gives `H <= L/100`. So
`L < 2,770,641,200` forces `H < H*`. The CRT.md §4 shuttles exchange the
`t` field `[H,2H)` with the back field `[L-H,L)`. They are also width-`H`
ordinary calls, so the same branch applies. The two table rows follow
from Lemmas R, W, S and the definition of `D`. ∎

**Remark 4 (robust to the reading of `D`).** For `64 <= E <= 16386`,
any reading with stock at least `K(w)` and `w >= 2` gives
`k >= 8193`, so `2k >= 16386 >= E`. So `H <= 1,458,353` is elementary
whatever `D` is, provided `D >= 1`. Both table layouts are far below.

## 5. Proof of (iv), recomputing #4942

If `H < 89`, then `E = 1 <= H^{1-a}`. If `89 <= H < H*`, then
`E <= H/89 + 1 <= 2H/89`. Also `H* < 2^25` and `a < 1/500`, so
`H^{a} < 2^{1/20}`. Since `2^{1/20} < 89/2`, we get
`E H^{a} <= (2H/89)(89/2) = H`. In both cases `E <= H^{1-a}`.

Stage `a = 0` exchanges two `E`-digit fields with `E` single-digit swaps
on the embedded volume `V' < q^2 V`. Each swap costs `C_0 V'`. So one call
costs at most `C_0 q^2 V E <= C_0 q^2 V H^{1-a}`, plus the embedding and
its restriction, which are `O(q^2 V)`. ∎

## 5a. Proof of (v)

By Lemma R, `E = floor(H/89) + 1`. At `H = 10752`, `E = 121` and
`89E - H = 17`. The exact integer check
`2^{33 + 2·10752} < q^{242} < 2^{34 + 2·10752}` gives the first range. At
`H = 15360`, `E = 173` and `89E - H = 37`. The same check with exponents
73 and 74 gives the second range. ∎

## 6. Not proved here

- BIT.md's theorem, including stage `a = 0`, its constant `C_0` and its
  fixed-tape realization. AUDIT.md in #4100 records that its physical
  suites are not all passing. This package uses the statement as written.
- The fixed-tape cost of the binary-to-radix embedding. BIT.md states it.
- The rest of the CRT.md §4 gadget: the guard scan, the sparse sort and
  reinsertion, the last-`K` branch, and #4377's evaluator model.
- Whether `D` is meant at the radix width `E`. Remark 4 covers the two
  table layouts under any `D >= 1`.
- That every width above `H*` is recursive. #4942 proves it; it is not
  used here.
- Any κ change or selected-frontier change.

## 7. Verification

`verify.py` checks the following:

- Input pins and the quoted phrases.
- **A.** On two `Placement` fixtures with dirty payloads, three literal
  field-exchange calls realize `P` in all six orders, and the same three
  calls restore every record.
- **B.** Every plan on the minimal layout (131,072 plans, 786,432 calls)
  and on the production layout (104,864 plans, 629,184 calls) satisfies
  the hypotheses of (i).
- **C.** The exact `N = |GL_64(F_q)|` bounds, the `j(D)` table, the branch
  at every `E <= 311309`, Lemma R on `H < 3000` and the table widths,
  and the `H*` edge.
- **D.** The inequality of (iv).
- **E.** The two padding ranges of (v).

Its rejection controls are: a dropped restoration call, a bit-reversing
exchange, a source overlapping `T`, the body branch one digit or one bit
early, the stock without `269241600 N`, `D(173) = 1`, `N >= q^{4096}`,
`j(D)` dropped, and padding below `2^{33}` or `2^{73}`. Each must fail. The finite checks corroborate the
written argument; they do not replace it.
