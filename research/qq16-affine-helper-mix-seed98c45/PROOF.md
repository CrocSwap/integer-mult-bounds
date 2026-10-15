# One mixed affine QQ16 helper cannot recover the lost input

## Statement and scope

Fix the source-bound QQ16 `F0/B1` pair, retained ordinary schedule, and
standard observations (selected outputs, completed-X descendants, and all five
forward-query histories). On a finite regular cover `G`, let
`B_s : Q^(96|G|) -> Q^(8|G|)` be the actual ordinary-source query operators
for `s=0,1,2`.

Allow exactly one additional eight-coordinate helper, immediately before
`F0`, with response

```text
H' = H + B0 X_U + (M lifted cover-wise) B2 X_U + c,
```

where `M` is any rational 8x8 matrix, `H` is an arbitrary but common dirty
pre-state, and `c` is any fixed 8-vector lifted identically at each cover
location. For every `M`, `H`, and `c`, the augmented observation map is
noninjective. More precisely,
`dim B2(ker[B0+M B2; B1]) >= 32|G|/7`. This is an information obstruction,
not a native cost or new `kappa` result.

## Pinned rank input

The exact three-query rank bound used here is the source-checked result in
[PR #2104](https://github.com/CrocSwap/integer-mult-bounds/pull/2104), head
`4bdc574da394a39f955e8cf4637075649c43a632`, exact base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Its `PROOF.md` SHA-256 is
`9c2ad4600d65dd3354db4bae5ac78d13fedf2da6e500224fafaeed596846c887`.
That proof pins the QQ16 source/certificate and checks, for each pair
`(0,1),(0,2),(1,2)`, that the 96 relative route labels are distinct and the
cross-Gram identity coefficient is `192 I_8`; it also checks the actual
ordinary column norms and Gram. The local source-specific verifier from that
exact PR head was run read-only against this base with Python 3.14. It printed
`PASS_QQ16_EXTRA_QUERY_RESIDUAL rank_stack>=144|G|/7 missing_A>=ceil(32|G|/7) no_new_kappa`.
At the last successful hosted-status check at 19:52Z, PR #2104 was open and
its checks were pending. A later status refresh hit the GitHub API rate limit,
so its current hosted status is unverified.

For `N=|G|`, those exact route facts imply

```text
B_s B_s* = 48 I_(8N),
tr((B_s B_s*)^2) = 18432 N,
tr(B_s B_t* B_t B_s*) = 1536 N  (s != t).
```
For `S=[B0;B1;B2]` and `K=S* S`,

```text
tr(K)   = 1152 N,
tr(K^2) = 64512 N,
rank(S) >= tr(K)^2/tr(K^2) = (144/7) N.                (1)
```
The rank bound is Cauchy--Schwarz on the nonzero eigenvalues of `K`. The
current package uses this exact predecessor lemma; it does not rederive the
route labels.

## All-matrix kernel argument

Let `A_M = B0 + (M lifted cover-wise) B2` and `T_M=[A_M;B1]`. Both query
blocks have `8N` rows, so `rank(T_M) <= 16N`. Appending `B2` recovers exactly
the row space of `S`, since

```text
A_M = B0 + M B2,       B0 = A_M - M B2,
row([A_M;B1;B2]) = row([B0;B1;B2]).
```
This holds for every rational `M`, including singular `M`. Therefore (1)
gives

```text
rank([T_M;B2]) - rank(T_M)
  >= (144/7)N - 16N = (32/7)N > 0.                     (2)
```
The left side is `dim B2(ker T_M)`. Rationality of all maps means the
rational nullspace spans the real nullspace. Thus some rational `h` satisfies

```text
B1 h = 0,       B0 h + M B2 h = 0,       B2 h != 0.   (3)
```
Clearing denominators preserves (3).

Use the same `H,c` for inputs `h` and `0`. Equation (3) makes their new
helper records equal. The affine offset and dirty pre-state cancel in the
difference.

## Existing selected-value witness

For any `h` satisfying (3), use the source-pinned QQ16 input compensation on
pair 0:

```text
X_U = h,                             Y_U = 0,
X_A = -P_(0,A) B0 h - P_(2,A) B2 h,  Y_A = -X_A,
X_T = P_(0,T) ell_(0,A) P_(2,A) B2 h, Y_T = -X_T.
```

The formulas are linear in `h`. The selected pair sums vanish; the ordered
`F0/B1` equations use only `B1h=0`, `B2h!=0`, and the pinned two-sided
selected-section identities. They leave a nonzero initial selected value
`X_(0,T)` but zero selected outputs, completed-X descendants and all five
forward histories, as detailed in
`research/joint-query/evidence/QQ16-SELECTED-WITNESS.md`. By (3), the mixed
affine helper also agrees with the zero input. No decoder from these
observations can restore every original selected input.

The zero-cost relaxation grants every potentially relevant expense for free:

| Expense | Favorable charge |
|---|---:|
| Source access and query arithmetic | 0 |
| Helper storage and output hosting | 0 |
| Helper update, inverse, and dirty-state restoration | 0 |
| Frame and address transitions | 0 |
| Local calls and recursive child operations | 0 |
| Recursive precision | 0 |

It still fails injectivity, so there is no implementable cost or moment gain
to invoice for this interface.

## Limits

The theorem allows all rational 8x8 mixers and fixed offsets on one helper.
It keeps the actual `F0/B1` maps, ordinary tail, observation set and source
cut fixed. It does not cover a second independent helper, an input-dependent
offset, another source field, a changed first pair or tail, or a later read of
other ordinary banks. `32|G|/7` is an information dimension, not a paid
recursive-child rank.

`verify.py` checks the rank/row-space corollary on exact rational controls and
checks the exact trace arithmetic. It does not replace the pinned route
verification of (1) or replay the full inherited native trajectory.
