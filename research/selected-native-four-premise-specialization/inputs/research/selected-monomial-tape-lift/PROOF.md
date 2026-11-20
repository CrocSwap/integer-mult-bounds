# The f-column lift of the selected caller's monomials as a fixed record list

Scope: the physical half of `native_all_columns` for the selected #5413 caller, at the level
of records. PR #5442 closes the algebraic half (every identity of the caller lifts to every
column width `f`) and leaves open the tape realization of `g^(tensor f)` with spectators and
adapters at the retained tariff. `SPECIALIZATION.md` §2–§3 (the P1 specialization of #4610)
states the realization in writing: any nine-axis monomial has a recipe of at most 171
retained elementary movement/phase records, each a compact-control selected-bit addition or
a per-record phase, acting on all `f` columns with one fixed list of primitive types. This
package executes that recipe for the caller's actual monomials and routes.

## Setting

A field with `f` columns on `n` logical axes has addresses `X = (x_1, ..., x_f)`, `x_j` in
`F_2^n`, next to arbitrary spectator bits. The retained monomial convention
(`prune_native.monomial`) is `m = (G, b, Q, alpha, a)` acting on one column as

```
|x> -> i^(a + q(x)) |G x xor b>,   q(x) = sum_i alpha_i x_i + 2 sum_(i<j) Q_ij x_i x_j  (mod 4),
```

and its lift (SPECIALIZATION §3) as `|X> -> i^(a f + sum_j q(x_j)) |(G x_1 xor b, ..., G x_f xor b)>`.

Five record types, each acting on all `f` columns at once and on no spectator bit:

| record | action | retained primitive |
|---|---|---|
| `XROW(i,k)` | `x_{j,i} ^= x_{j,k}` for every column `j` | compact-control selected-bit addition, slots `k -> i` (movement-paid) |
| `NOT(i)` | `x_{j,i} ^= 1` for every column `j` | selected-bit translation (movement-paid) |
| `S(i)` | phase `i^(sum_j x_{j,i})` | unit-S phase record |
| `CZ(i,k)` | phase `(-1)^(sum_j x_{j,i} x_{j,k})` | controlled-sign phase record |
| `I` | phase `i^f` | global `i` record, lifted to `i^f` |

A row swap is three `XROW` records. `SWAP_BITS(i,k)` of the plan is a row swap.

## Lemma (record realization, uniform in f)

For every monomial `m` the list `R(m)` = [`alpha_i` copies of `S(i)` for each `i`; `CZ(i,k)` for
each `i<k` with `Q_ik = 1`; the reversed Gaussian-elimination list of `G` with swaps expanded
to three `XROW`; `NOT(i)` for each set bit of `b`; `a` copies of `I`] does not depend on `f`,
contains at most `96 + 9 + 27 + 36 + 3 = 171` records, and executes the lift of `m` exactly on
every address and every `f >= 1`, leaving every spectator bit unchanged.

*Proof.* Each record is the `f`-fold product of the same one-column operation, applied to
the columns independently (`XROW`, `NOT` act column by column; `S`, `CZ`, `I` add a phase that
is a sum over columns, with the global record contributing `f`). So the composition of the
list on `X` is the `f`-fold product of its composition on one column, and the phase is the
sum of the one-column phases plus `a f`. On one column: the phase records applied first on the
input address give `i^(q(x))` (the diagonal `Q` is carried by `alpha`, exactly as in the
convention); Gaussian elimination gives elementary matrices `E_1, ..., E_r` with
`E_r ... E_1 G = I`, hence `G = E_1 ... E_r` (each elementary matrix is an involution), and
applying `E_r` first and `E_1` last maps `x` to `G x`; the translations give `xor b`; the
global records give `i^a`. The bounds are those of SPECIALIZATION §2: at most 72 additions
and 8 swaps (24 records), 9 translations, 27 unit-S, 36 controlled-sign and 3 global
records. No record reads or writes a spectator bit. ∎

Cost. Each `XROW` or `NOT` record is one compact-control selected-bit addition on the ordered
pair of slots (`compact-control-movement.tex`, Proposition), costing `O(V((f log p)^tau + 1))`
on a fixed number of tapes in the domain `f <= p`, `A = O(p)`, `K / log p -> infinity`, with
the front/back control fields reserved as in `compact-control-layout.tex` ("the proposition
applies to every ordered pair of slots"). A phase record computes a fixed degree-two residue
from `O(f)` selected address bits per complete record and applies one of `{1, i, -1, -i}`
(SPECIALIZATION §2); it is absorbed by the record fiber. The domain `f <= p` is the actual
layer's own domain: `f <= e <= floor(b_in^epsilon)` and `p = 6 b_in` (SPECIALIZATION §3). The
tariff per record is inherited from the Proposition, not re-derived here.

## What is executed (`verify.py`)

- The 896 compiled port wrappers of `NORMALIZERS.json` (112 ports x 8 orientations/paths):
  the record list is executed on all 512 addresses at `f = 1` (and compared with the exact
  Clifford engine's basis action on one wrapper per path), on all 262,144 addresses at `f = 2`
  for two wrappers, and on 48 random addresses at `f = 2, 3, 4` for every wrapper, with random
  spectator bits. Every wrapper is within the §2 bound; the largest list has 107 records
  (69 movement, 38 phase).
- The body's own monomials, which are not port wrappers: all 1,072 `MONOMIAL` operations of
  `NEUTRAL-BACKWARD-v16c` (800 whole-job helper normalizers, 240 Z-map block maps, 16 paid C8 axis
  routes and 16 mode aliases) and the 8 `output_N` words of the #5402 provider's mode boundaries,
  which #5442's mode-output certificate binds (the 8 `input_K` words coincide with alias words).
  These are 283 distinct words. Each is read off the exact engine as a monomial `(G, b, Q, alpha, a)`
  on 46 basis states and certified to be the same group element (Pauli tableau and image of `|0>`);
  its record list is then executed on all 512 addresses at `f = 1` and on 48 random addresses at
  `f = 2, 3, 4`. The largest list has 76 records (60 movement), within the §2 bound.
- The central translation `X0` is one `NOT(0)` record. `C0` (cgate on axis 0) and `D`
  (Fourier on axes 1..8) are positive-rank Gaussians: in the retained framework they are paid
  children of the recursion (`FINITE-PRECOMPILATION.md` §1, "one ordinary positive rank-r f
  child on the actual owner's full stream"), not adapters, and no record list is claimed for them.
- The literal `pre_word` and `post_word` of all 119 targets of `WHOLECALLER-PLAN-v1`
  (32 main, 72 helper, 15 idle), 16,748 `SWAP_BITS` events in all, are executed as `XROW`
  records on 145-axis addresses at `f = 2`; each word realizes the declared `permutation` or
  `inverse_permutation` of its target with phase zero and spectators untouched. The 16
  central `X` corrections of negative `Q` powers are `NOT(0)` records.

## What is not claimed

The Proposition's proof (the four-update rotation scheme with dirty compact fields, its
overflow repair and the chunk-swap primitive) is not executed; the reservations of the control
fields for the 145-axis layout are taken from `compact-control-layout.tex` as written. No
numerical tariff, no new κ, no change to the selected record. The body monomials, including the
400 helper alias pairs of #5442, are executed separately above (an earlier version said they
were covered by the port-wrapper lists; none of them is a port wrapper). The forward body is not
replayed.
