# In-place availability of PR2443's two-cut QQ16 observations

**Negative result (scoped screen). No kappa claim, no supplier, no controller.**
[PR2443](https://github.com/CrocSwap/integer-mult-bounds/pull/2443) (starship-s,
head `545c05e17243c962b112b91e7f84b4c1a41de7b8`) decodes all pair-0 inputs of
the conserved `F0/B_1_2` pair from 224 observed port arrays at two cuts. It
grants the retention of those arrays and calls its F0 record transient. This
package checks which of them are still held by a live field at a decode point
of the pinned 19-event QQ16 recipe. It answers the logical-trace part of PR2443
open question 1 (native endpoint types stay open) and the storage term of open
question 2.

**What is already known and what is new.** That pair 0 cannot be recovered from
final-only records under the 19-event schedule is PR2346's obstruction
(alephnan, head `653520d7`: the final-only observation map loses at least
`ceil(8|G|/7)` dimensions of pair 0's selected input). The PR2376 scope map
(commdata2338, head `157143ab`) warns against assuming that a decoder granted
the B1 cut works from final records. The qualitative d18 failure below is
consistent with, and largely implied by, that work. This package quantifies it.
New here: exact per-array counts at both decode points, the d1 split (104 live,
120 overwritten by B1), the scalar-multiple and same-port-span relaxations,
the checked recomputation leads L1/L2 with an L2-variant decoder, and the
transfer of the counts to the price3 convention.

| item (cut) | arrays | live at d1 (after `B_1_2`) | live at d18 (after terminal) | first overwrite event |
|---|---:|---:|---:|---|
| `x1_A` (after F0) | 8 | 0 | 0 | 1 (`B_1_2`) |
| `x1_T` (after F0) | 8 | 0 | 0 | 1 (`B_1_2`) |
| `y1_A` (after F0) | 8 | 0 | 0 | 1 (`B_1_2`) |
| `y1_T` (after F0) | 8 | 0 | 0 | 1 (`B_1_2`) |
| `x1_S` (after F0) | 88 | 0 | 0 | 1 (`B_1_2`) |
| `y2_A` (after B1) | 8 | 8 (same field) | 0 | 3 (`F2`) |
| `C=x2_U` (after B1) | 96 | 96 (same field) | 0 | 2 (bridge `1->0`); 3 (`F2`) if pairs 1-3 are zero |
| **total copies needed** | 224 | **120** | **224** | |

"Live" means equal, as a linear map of all 896 initial port arrays, to some
field of the four bank pairs at that point. The zero entries also hold under
three relaxations. The array is not a nonzero scalar multiple of any live
field. It is not in the span of the two fields `X_(k,p)`, `Y_(k,p)` at any one
port of any pair. Neither statement changes if a cover map `M(g,delta)` is
applied (see "Model" below). The counts do not change if the terminal also
exchanges selected fields, or if pairs 1-3 start at zero.

Per owner per replica, the contract therefore needs these retained copies:

- **d1:** 120 copies (all F0-cut arrays), each held across one call (`B_1_2`),
  so 120 coordinate-calls.
- **d18:** all 224 copies. The 120 F0-cut arrays are held for 8 calls and the
  104 B1-cut arrays for 7 calls, so 1688 coordinate-calls.

### Comparison with the #2074 pricing (inherited, unreviewed)

philippeVV's four-bank finding (#2074; [fork](https://github.com/philippeVV/integer-mult-bounds)
commit `680d0997621a2cecfef2186ab143377658687825`, path
`research/joint-query-first-pair-catalogue/four-bank/`) says that with
`C = 0` the route "pays only for in-place or single-call storage". `price.py`
re-implements the `price3.py` convention (5F+4B QQ16 profile, rank-8 child
plus 8 mass per coordinate-call for centre-like storage, 72 mass per new live
family). It uses the pinned `ceiling.py`. Before transferring anything, it
reproduces three committed values of `price3.json` exactly: the selected
ceiling and the C=0 centre rows for 62 and 64 coordinates. The results are in
[PRICE.json](PRICE.json):

| convention | max coordinate-calls/replica with any positive saving | max still beating the selected ceiling | census demand d1 / d18 |
|---|---:|---:|---|
| C=0, centre-like copy | 111 | 71 | 120 / 1688: no saving at either (L2 variant: 32) |
| C=0, new live family | 12 | 8 | 120 / 1688: no saving at either |
| C=64, centre-like copy | 39 | 0 | none beats selected |
| C=64, new live family | 4 | 0 | none beats selected |

The literal PR2443 contract needs copies at both decode points. At the
favourable d1 point the copies are single-call storage, which philippeVV's
qualitative condition allows. The failure is quantitative: 120 coordinate-calls
exceed the C=0 centre-like break-even of 111 (any saving) and 71 (beat the
selected ceiling). **Under this convention the literal contract exceeds the C=0
centre-like break-even even though its d1 storage is single-call.** By a
dimension count this is also the floor for PR2443's d1 read set: the 104 live
reads (`y2_A`, `C`) leave 120 of the 224 pair-0 input dimensions, so any linear
record that a decoder confined to those reads can use must retain at least 120
coordinates per owner across B1.

Three limits on this conclusion:

- *Copy kind.* price3 also has a `line` kind (an in-place write that adds no
  new live data). It is not used here because a retained copy is new live data:
  the census shows that no live field holds it. If copies were priced as `line`
  writes, this screen would not reject them.
- *Pair 0 only.* PR2443 recovers pair 0 only. #2074 Theorem B's 62 is the
  four-bank total (four banks at `77N/5` each, rounded up); the inherited
  per-bank floor is `ceil(77N/5)`, 16 per owner at that normalisation. A complete controller must also repair
  banks 1-3, which also lose a query by Theorem A, so the pair-0 demand counted
  here is a favourable lower bound on a full controller's storage.
- *Literal contract only.* Lead L2 (below) gives a variant that needs only 32
  coordinate-calls at d1, below both C=0 break-evens. So this negative result is
  specific to PR2443's literal read set and is not evidence against a
  compressed contract.

This screens one contract under one inherited, unreviewed price convention. It
is not an impossibility theorem for QQ16 controllers. Note also that the
convention gives a free controller (zero retention) +179.5% over the selected
ceiling at C=0 and +0.28% at C=64 (PRICE.json rows `zero_retention`), so the
C=0/C=64 choice dominates every storage figure here.

### Recomputation leads (not in-place availability)

Two exact identities follow from CONSERVED-QQ16 (1) and (3). The checker also
verifies both in the model.

- **L1.** F0, B1 and F2 conserve the 16 selected pair sums `X_V+Y_V=x_V+y_V`.
  Nothing writes them afterwards, so they are live two-field sums at d1 and at
  d18 (identity selected terminal). PR2443's last step `y_V=x1_V+y1_V-x_V`
  only needs these sums.
- **L2.** At d1, `x1_U = X2_U + Y2_U - K_(1,U) ell_(1,T) x1_T`. The driver
  `ell_(1,T) x1_T` is computable from the retained `x1_T` record, so the 88
  `x1_S` copies can be replaced by a same-port read of `Y2_U` (`X2_U = C` is
  already read). The checker runs PR2443's decoder with these `x1_U` forms and
  recovers all 224 pair-0 inputs from the 32 retained F0 selected arrays
  (`x1_A, x1_T, y1_A, y1_T`) plus the live post-B1 reads `y2_A`, `C`, `Y2_U`
  (RESULT.json `leads.L2_variant_d1`). Its storage demand is 32
  coordinate-calls. Under the inherited C=0 centre-like convention that is
  storage-only +99.56% over the selected ceiling (PRICE.json row
  `d1_L2_variant`); reads, their legality, chart maps and restoration are not
  priced, so this is a lead, not a bound. L1 cannot replace `y1_A`/`y1_T`,
  because the decoder queries them separately. Because `B_1_2` is invertible,
  a decoder that may read the whole post-B1 state of pair 0 needs no copy at
  all at d1. PR2443 excludes `y2_U` from its reads, so both are different
  contracts.

So the census prices the literal contract; at d1 that equals the information
floor for its read set, and only extra reads lower it.

## Model, exactness and scope

- **Maps:** CONSERVED-QQ16 equations (1) and (3). The checker binds them to the
  packet's `F_contract`/`B_contract` strings. Pins: `R`, `K=R^T/4`, the
  A/T/U96 sets and the Grams (U:48, A:4, T:4).
- **Recipe:** the literal 19-event `GLOBAL-TEMPLATE.json.gz` recipe (archive
  member sha256 `a179dad8...`). Its local pairs are `0,0,0,1,1,2,2,3,3`.
- **Bridges and terminal:** semantics follow PR2346 section 1 (alephnan, head
  `653520d7`). A bridge does `X_j,U += c X_i,U; Y_i,U -= c Y_j,U`. The
  terminal does `(X_U,Y_U) -> (Y_U,-X_U)`; the selected terminal is identity or
  the same exchange (variant).
- **Exactness:** every field is an exact rational linear form in the 896
  initial port arrays of four pairs. The executable instance is the
  owner/payload-constant subspace, where every cover map
  `M(g,delta)f(d,z)=f(d*g, z XOR d*delta)` is the identity. Any actual
  equality, even up to a scalar or a cover map, restricts to an equality
  there. So every "not live" entry is an exact counterexample for the actual
  routed maps. The only "live" entries are the post-B1 arrays at d1, where no
  event intervenes. The support argument proves them, and every survival claim
  is checked against the symbolic write sets.
- **Consistency check:** in this model, PR2443's ordered decoder recovers all
  224 pair-0 inputs exactly, including `C=-y_U` and the two-sided `R_J`
  inverse. This was implemented independently; no predecessor code is imported.
  It runs on the payload-constant subspace only, so it does not validate
  payload-sensitive charts: ywz65's PR2456 (head `665ba8d7`) shows that
  payload-constant fixtures miss the logical-D vs physical-A chart fault. The
  "not live" direction of the census is unaffected, since a restriction of an
  actual equality is still an equality.
- **Not covered:** physical idle cover sweeps, terminal Y translations,
  bank padding and phase adapters. These are invertible frame changes in the
  inherited logical convention. They cannot make an overwritten logical value
  live again. Also not covered: native read legality, read and chart-map cost,
  cleanup, hosting, precision, and other contracts or schedules.

## Negative controls (all must be rejected or change the receipt)

Controls 1 and 4 are claim rejections (a false statement is tested against
the computed states). Controls 2, 3, 5 and 6 mutate the pipeline.

1. Claiming `x1_A` survives B1 in place is rejected.
2. Dropping F2 (event 3) changes the d18 census to 216 copies. Eight arrays
   are then live in place, and 104 are scalar multiples of live fields.
3. Dropping B1 (event 1) changes the d1 census to 0 copies.
4. Claiming `C=+y_U` is rejected.
5. A corrupted centre coefficient fails the Gram/source checks.
6. A wrong sign of the future logger `E_t` breaks PR2443's decoder.

A wrong `11a -> 12a` coefficient in the backward `Y_T` output was also tried.
It does **not** break the decoder, because PR2443 never reads `y2_T`. That
mutation was therefore not used as a control.

## Reproduce

From the repository root (stdlib only; about 65 s and 50 s on one core):

```sh
python3 -I -B research/qq16-cut-retention-census/verify.py
python3 -I -B research/qq16-cut-retention-census/price.py
```

Expected last lines: `PASS_NEGATIVE_CONTROLS 6`, `PASS_QQ16_CUT_RETENTION_CENSUS`,
then `PASS_QQ16_CUT_RETENTION_PRICE_TRANSFER`. Each script recomputes its JSON
and requires it to equal the committed [RESULT.json](RESULT.json) (receipt
`8c57f8f5...`) and [PRICE.json](PRICE.json). Per-array rows are in
[CENSUS-ROWS.json](CENSUS-ROWS.json); verify.py also requires them to equal
the recomputed rows. Registered replay:
`python3.12 scripts/research_package.py --package research/qq16-cut-retention-census`.
The checks were run with Python 3.14.4, since 3.12 was not installed locally.

Base commit `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Input pins are in
[SOURCES.json](SOURCES.json). External, read-only pins: PR2443 `545c05e1`,
PR2346 `653520d7`, PR2174 `f79470a7`, and philippeVV `price3.py` sha256
`1c2ca9a4...` (philippeVV/integer-mult-bounds commit
`680d0997621a2cecfef2186ab143377658687825`,
`research/joint-query-first-pair-catalogue/four-bank/`). price3 is not
vendored; its three reproduction values are hard-coded in `price.py`.

## Open next questions

1. **What is the smallest retained record for a final-only (d18) decode with
   PR2443's read set plus legal final reads?**
   - *Why it matters:* the literal contract needs 1688 coordinate-calls, while
     the C=0 break-even is 71. For pair 0 alone the inherited Theorem B floor
     is `ceil(77N/5)` per bank, 16 at the normalisation where 62 is the
     four-bank total, and a full
     controller must also repair banks 1-3.
   - *First step:* carry the L2 variant (32 retained arrays plus a `Y2_U`
     read) through F2..F8 and the terminal with this census code.
   - *Blocker:* the legal native read types for former-Y endpoints and
     `X+Y` sums.
2. **Can a controller use the d1 decode point at all?**
   - *Why it matters:* the demand there is 120 for the literal contract, 32
     for the L2 variant, and 0 with full post-B1 reads, since `B_1_2` is
     invertible. But a mid-schedule decode must restore what it reads before
     F2.
   - *First step:* price the CONSERVED-QQ16 inverse of B (`H_s`, `E_t`) as
     reads plus restoration.
   - *Blocker:* no priced read of `y2_U`/`X2_T` at the completed-X type.
     ywz65's PR2468 (head `baa90ee8`, opened 11:49Z,
     `research/qq16-future-x-query`) constructs a native local read of
     `C=x2_U` at the post-B1 frame with restoration and leaves retained
     observations open; this package defers to it for the read and supplies
     the retention count it leaves open.
3. **Which centre charge applies to QQ16, C=0 or C=64?** This is the
   maintainers' open question in #2074. Under C=64 no positive retention
   budget beats the selected ceiling; even a free controller gains only +0.28%.

## Credit

The observation contract and decoder are from PR2443 (starship-s). The local
maps, packet and cover semantics are from Ali Romman (PR1969,
`research/joint-query`). The bridge/terminal semantics and the 19-event
binding are from alephnan (PR2346). The two-query recovery contract is from
commdata2338 (PR2174; also PR2153, PR2376). The unread basis and 88-port
threshold are from Gareth Davidson / bitplane (PR2432). The C=64 screen and
the `y2_A` pricing are from 1337isnot1337 (PR2079, PR2197). Theorem B and the
price3 convention are from Philippe Van Velzen (#2074, fork `680d0997`). The
trace method is from Ross Richardson (PR2104). The ceiling model is
`research/complex-local-word-ceiling`. The final-only obstruction is
alephnan's PR2346, and the contract scope map is commdata2338's PR2376
(`157143ab`). Concurrent work: ywz65's PR2456 (head `665ba8d7`) audits
PR2443's operators with payload-sensitive fixtures, and ywz65's PR2468 (head
`baa90ee8`) constructs the native `C` read of open question 2. ToikY's PR2416 (head
`f2c93e76`) prices native retention of A-copy data at the `B_1_2[:80]` cut
(24 native lines vs 16) in a different cost model; it is not combined here.

Prepared by thakrarsagar with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5). No independent human review is claimed.
Apache-2.0.
