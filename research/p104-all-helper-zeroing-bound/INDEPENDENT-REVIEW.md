# Independent review: p104 all-helper zeroing bound

## Finding

The frozen package supports its stated fixed-word theorem. For the exact
#7481 native word, zeroing any subset of its 1,101 helper inputs and deleting
only MOVEs whose latent scalar rows become identically zero cannot increase
the complete signed moment for `0 <= kappa <= 1/2`, provided all other source
operations stay fixed. This is not a source/supplier change or a new kappa.

## Charging implication

Write `t = 1-kappa`, so `1/2 <= t <= 1` and the rank price is `f(r)=r^t`.
If a MOVE row becomes identically zero after the helper set `H` is zeroed,
every nonzero coefficient in that row must belong to `H`. The replay establishes
that each of the 468 helper-only MOVE rows has a nonzero coefficient at its
assigned helper, so every removable MOVE is charged to a helper in `H`.
The other 5,811 MOVE rows have a nonzero main-input coefficient; those inputs
remain arbitrary, so these MOVEs cannot be identically zero.

Each helper's lost productive credit is its target rank price `f(R)`: the exact
rational replay confirms that helper outputs are their own unit rows and no
helper coordinate leaks into main outputs. For 466 assigned helpers there is
one funded MOVE with rank `r <= R`, hence `f(r) <= f(R)`. The sole repeated
charge is helper 666, assigned to events 43186 and 43199. Both MOVEs have rank
1 and its target rank is 4. Therefore their total charge is
`2 f(1)=2 <= 4^t=f(4)` for every `t >= 1/2`, with equality at the square-root
endpoint. Summing over `h in H` bounds every removed native paid moment by the
productive helper credit lost. This reasoning holds for each invocation even
if the zeroed subset differs across the 17 independent native calls.
At the boundary, replacing the rank-four lost target by rank three fails the
double-charge inequality (`2^2 > 3`), so the exception is exactly accounted.

## Replay and invoice audit

One bounded run of the package verifier passed under Python 3.12.14 with
`-I -W error -B`. Its exact-rational and modular replays both cover 76,475
events, all 6,279 MOVEs, all 468 funded and 5,811 main-obstructed rows, and the
same paid histogram `{1:4001, 2:854, 3:827, 4:222, 5:344, 6:16, 7:10, 8:5}`.
Both reject changed source bytes. The rational replay also checks exact
helper endpoints, no helper leakage into main outputs, and assignment ranks.

The modular replay uses the prime 65,521. The proof checks primality by trial
divisors through 256, exceeding its square root, and checks every source
coefficient denominator is invertible modulo that prime. It finds a nonzero
residue for each assigned helper coefficient and a nonzero main coefficient
for each unfunded MOVE. A rational coefficient that were zero would reduce to
zero modulo this prime, so these residues independently certify nonzeroness.
No modular zero is used as proof of rational zero.

The verifier reconstructs the retained 17-call caller invoice, including
ordinary caller operations and all main targets: 22,461 productive fields,
110,519 paid jobs, and linear-rank surplus 1,424. The helper-zeroing bound
accounts for the helper-target loss and removable native MOVE savings inside
that existing invoice. It does not omit caller operations or charge the local
MOVE savings without the lost helper credit.

Targeted controls reject a duplicated MOVE, forged paid rank, forged target
rank, and omitted funded MOVE. An independent assignment pass confirmed 1,101
helpers, 468 unique funded events, 467 assigned helpers, 466 singletons, and
exactly the helper-666 rank-one/rank-one to rank-four double charge.

## Scope

The result is limited to the pinned #7481 word (`acee3236…fcc0a9`): helper
coordinates may be zeroed, and only newly identically-zero MOVE rows may be
removed; the other source operations, contacts, frames, productive boundaries,
and main-input contract stay fixed. The package says changed contacts and a
physical zero-frame implementation remain open. #7481 is expressly an
**unselected** comparator; its exponent is not admitted here. The selected
conditional value remains `363005817/100000000000` under the five inherited
assumptions.

## Receipt files

- `review.py` / `review-result.json`: independent source-rank and charging
  certificate checks.
- The replayed frozen package is at
  `cold-package/research/p104-all-helper-zeroing-bound/`.

## Later correlated-subspace extension

The earlier review above concerns the coordinate theorem. The later extension
in SUBSPACE-PROOF.md received a separate root implementation: it reconstructs
all assigned projected rows over F_65521 from the native word, checks direct-sum
rank additivity and all 612 subset funding inequalities, and rejects false
partitions and overpriced dependent rows. All 102 group ranks agree with the
independently authored exact-Q discovery. The lifting uses only nonzero minors
to lower-bound characteristic-zero rank; no modular zero is lifted. The exact
integer price envelope and annihilator-dimension argument were checked
separately. Final normal/optimized and portability receipts cover this extension.
