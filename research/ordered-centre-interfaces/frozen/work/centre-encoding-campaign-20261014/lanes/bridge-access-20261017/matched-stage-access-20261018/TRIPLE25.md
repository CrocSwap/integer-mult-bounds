# The actual three-stage terminal in dimension 25

This supplement binds the five scalar code cuts of the one-pair
controller. It also gives a complete terminal recipe with profile
`{1:96, 2:64}`. Its rank mass is 224. The recipe does not save rank.
It does not combine the 48 mixed rows into 48 rank-two calls.

The controller source is
[ONE-PAIR.md](../../encoded-controller/one-pair-current-codes-20261018/ONE-PAIR.md).
Its program SHA-256 is
`f66186f2f67ea00eb8ae6447ec9cbddbdf410f141e61149871b0915e599845d7`.
The source proves the endpoint `(-y,T x)`, where `T=E2 E1 E0`.
After the retained raw terminal, the first output bank has code
`Q T Q^-1`. The second bank has no code. This supplement uses that
ordered endpoint. It does not replace it with the isolated two-call
endpoint in [MATCHED-STAGE-ACCESS.md](MATCHED-STAGE-ACCESS.md).

## The five scalar cuts

The emitted views act on the root nine coordinates and two fresh
eight-coordinate blocks. Each route and translation is the restriction
of the pinned DATA view. The exact cuts are:

| Operation | Bank | Global completed or hole level |
| --- | --- | --- |
| E0 after F0 | X | 0 |
| E1 before B1 | Y | 0 |
| E1 after B1 | X | 1 |
| E2 before F2 | Y | 1 |
| E1 inverse after F2 | X | 2 |

The checker verifies the full Z4 phase equation at all 560 port cuts.
It includes the route, translation, intrinsic line, and common exterior.
All ports in one code have the same frame in their specified view.
Thus each occurrence can use a scalar port circuit. The result does
not depend on a zero input or a zero borrowed field.

The scalar circuit is the independently produced
[FULL-GAUGE.json](../../independent-review-20261017/matched-full-gauge-20261018/FULL-GAUGE.json),
SHA-256
`ea8717a63861b7bc9acc2d8e8b0501503a928859042e453234a2fc0c65797f89`.
This supplement replays its forward and inverse words on all 112 input
columns. It verifies that the matrix is the actual matched48 plus
permutation64 response. The price is 2,396 real scalar primitives per
code. The largest row one-norm is four. Each routed application has a
conservative allowance of 224 monomial view calls. Those map calls are
not included in the scalar price.

## The complete raw triple

Let rho_(s,p) be the literal stage route, with rho_(0,p)=I. A path
`p <- j <- k <- r` in `E_a E_b E_c` has cover map

```text
A = rho_(a,p) rho_(a,j) rho_(b,j) rho_(b,k)
    rho_(c,k) rho_(c,r).
```

The two required stage orders are `(2,1,0)` for T and `(0,1,2)` for
T inverse. The inverse order is valid because each actual E_s is an
involution. The checker uses the full routed maps, not the local
identity E cubed = E.

In the common completed frame, the path in `Q T^(+/-1) Q^-1` is

```text
c X_delta C_a C_b^-1 P_A,
a = q_p,       b = A q_r,
c = E_pj E_jk E_kr.
```

Here X_delta is a uniform payload translation on every tensor copy.
The checker obtains delta from the difference of the full Fourier
phase polynomials before and after A. The serialized route and phase
are part of the program.

For each direction, the preferred response has 3,136 paths: 3,072 on
the 48 mixed ports and 64 on the permutation ports. All paths have
distinct, orthogonal line directions a,b. For fixed p,r, distinct
intermediate pairs give distinct complete cover maps. These facts are
checked on every path. The half-Hadamard64 alternative has 7,168 paths
per direction and is checked separately; it is not used in the emitted
mixed decoder.

The cover-map test does not collapse different owner paths into one
local matrix entry. For T, cancel the fixed left factor rho_(2,p).
The action on the second fresh block then recovers the root complement
chart of j. After that chart is removed, the remaining first-stage map
recovers k. The inverse word has the corresponding reversed recovery.
The literal checker compares all complete map columns.

Each distinct two-line path has four nonzero address entries per copy.
Thus a path has support 4^f at tensor width f. This rules out a fixed
number of scalar and monomial passes for the specified raw operator.
It is not a lower bound on the number of children in a joint decoder.
In particular, it does not rule out shared native work between paths
or fields.

## Literal rank-two calls on the 64 permutation ports

Each permutation output has exactly one path. Its coefficient is -1,
and the 64 source ports form a permutation. The cover maps are
orthogonal and invertible. This gives a field and cover bijection;
it does not need a copy of an input bank.

For each path, the program constructs an orthogonal 25 by 25 matrix G
whose first two columns are a and b. It constructs G by orthogonal
transvections, records every transvection, and checks both inverse
orders. In the stated coordinate convention,

```text
C_b^-1 = X_b C_b,
C_a C_b = P_G H2 P_G^-1.
```

Consequently the exact inverse path is

```text
-X_(delta+b) P_G H2 P_G^-1 P_A.
```

This is one positive rank-two child between two monomial views. The
right view includes the source field and cover map. The left view
includes the translation delta+b. The complex sign can be applied
separately. The program records both full basis matrices and the full
translation. It verifies all constant, linear, and quadratic phase
coefficients. The construction applies on each tensor copy, so it
holds at arbitrary tensor width.

The 64 records are a literal native factorization of these 64 rows.
They do not rely on a claim that all rank-two path sums use one child.

## The exact two-pass contract on the other 48 ports

The 48-port set is invariant under every E_s. It has no read from the
64-port set. Apply this sequence to the 48 fields:

1. Apply C_q^-1 on each field.
2. Apply the restricted E2 inverse, E1 inverse, and E0 inverse codes,
   in that chronological order, through the final FULL views.
3. Apply C_q on each field.

This is precisely `Q T^-1 Q^-1` on that invariant set. The program
emits all 96 rank-one recipes. An inverse line uses one positive child
and the translation q. Every recipe includes an orthogonal basis,
its inverse, and its phase check.

The restricted scalar circuit has 256 events: 168 complex ADDs and
88 complex SCALEs. Its price is 1,564 real scalar primitives per stage.
The checker replays both orders on all 112 columns, with the other
64 fields fixed. Its largest row one-norm is four.

The complete terminal invoice in this packet is:

| Item | Count or price |
| --- | --- |
| Rank-one children | 96 |
| Rank-two children | 64 |
| Total native rank | 224 |
| Three restricted scalar codes | 4,692 real primitives |
| 64 complex signs | 128 real primitives |
| Total scalar primitives outside children | 4,820 |
| Restricted scalar code views | 288 |
| Rank-one child wrappers | 192 |
| Rank-two child wrappers | 128 |
| Top-level owned or private fields | 0 |

The 608 map calls have not been converted to a finite real-operation
or precision invoice here. The inherited signed terminal remains a
separate part of the controller. The basis wrappers and cover maps
can use the existing monomial map interface. Recursive child hosting
must still be bound to these particular recipes.

The fallback is 224 rank-one children with three full scalar codes.
The mixed profile has the same rank mass, but a different positive
moment. It must not be replaced by `{2:112}` in an invoice.

## Verification and limits

Run:

```text
python3 -I -B check_triple25.py
PASS_MATCHED_TRIPLE25_AND_FIVE_CUTS
```

Repeat with `-O`. The program and receipt must be byte-identical.
The checker verifies 560 cut equations, both complete raw triple
directions, the full and restricted scalar codes, and 52,160 native
phase coefficient equations. The source pins are in the payload and
receipt. `TRIPLE25-FREEZE.json` preserves this supplement independently
of the earlier stage-access freeze.

This result is an exact decoder implementation at the stated cuts.
It does not prove a lower native cost, a complete recursive supplier
invoice, or a kappa improvement. A joint decoder for the 48 mixed
fields, or a changed code placement, remains an open opportunity.

The work uses the controller lane's ordered endpoint, the independent
review lane's scalar gauge, the history lane's permutation64 word,
and the pinned DATA phase calculations. OpenAI Codex assisted the work.
No PR, commit, or push was made. Before a future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
