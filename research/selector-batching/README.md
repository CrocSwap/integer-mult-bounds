# Selector batching of equal-rank complex children: the volume charge

**Scoped negative result; no new κ or supplier.** A pair of paid rank-2
children in the accepted #626 complex supplier suggests the replacement
`2 C_2 -> C_3 + C_1`. That unweighted profile appears to improve the moment.
The actual joined array has twice the volume: its profile in units of one
original stream is **`2 C_3 + 2 C_1`**. The tempting saving disappears.

This note supplies an exact circuit, arbitrary-dirty-padding restoration,
an all-size comparison of the inherited cost bounds, and an independently
implemented finite checker. It does not claim that batching is impossible
or that these bounds are lower bounds on actual execution time.

## Reproduce

From this repository, using Python 3.11 or later and only its standard library:

```sh
python3 -B research/selector-batching/verify.py
```

Expected first line:

```text
PASS_SELECTOR_BATCHING_IDENTITIES_AND_VOLUME_OBSTRUCTION
```

The command takes about three seconds on the contributor's macOS machine.
It checks every pinned source, reconstructs both native paid histograms and
the seed-selected pair, replays 34 complete finite operators against closed
Kronecker entries, rejects six operator and three invoice mutations, and
compares the entire result with [CERTIFICATE.json](CERTIFICATE.json).
There are 2,776 basis columns / 753,568 matrix entries, including 60 arbitrary
dirty-padding columns. Assertions are not used as admission predicates;
`python3 -I -O -B research/selector-batching/verify.py` also checks them.
`--output /path/to/new-receipt.json` optionally writes a fresh identical receipt.
The [local validation receipt](VALIDATION.json) records an optimized replay
from a relocated minimal checkout with a recompressed source, plus rejection
of a changed native source and a corrupted expected certificate. The selected
record's separate inventory/proof binding check also passed.

## Exact reference and task selection

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
At that base the maintainer-reviewed record is #626 with #543, conditional
`κ = 51110230636731/31250000000000000`. This note does not change that record.

The operating-system draw was **22**, assigning the complex-supplier track.
Three candidates were considered: more K-triangles, target-hosted face
delivery, and selector-axis batching. Pending #646 already measures the
eight-triangle construction; #651 investigates delivery rigidity. The third
scope was selected after inspecting 487 open PRs through #667, the review
ledger and the negative-result archive. No pinned coordination issue existed;
[CLAIM.json](CLAIM.json) records the local claim and stopping rule.

The even seed selects `jp8`; `22 mod 7` selects rank 2 from its sorted paid
ranks. Among the 32 consecutive equal-rank climb pairs feeding one addition,
pair 22 consists of these zero-based forward-program events:

```text
14512: ['climb', 'B', 159, 525, 526, 2]
14513: ['climb', 'B',  25, 524, 526, 2]
```

The following scalar adds register 25 into register 159. The stored native
`jp8` profile in each orientation is
`{1:2512, 2:400, 3:448, 4:160, 5:70, 6:8, 8:8}`. This is a pair of **paid
climbs**, not a pair of helper-width entries incorrectly added to the invoice.
The exact local program and SPEC are bound in [SOURCE-PINS.json](SOURCE-PINS.json).
The gzip input is pinned by its complete decompressed payload; container
headers are not mathematical evidence. These are retained native receipts,
not a new cold replay of the whole supplier.

The two residuals have different frame transitions. For the proposed cost
comparison we grant legal co-scheduling and their reduction to identical
coordinate normal forms, without charging extra frame wrappers or routing.
This is deliberately favorable to batching. No replacement of these events
in the actual scalar word is asserted to be legal or implemented.

## The literal operator

Use the repository's complex kernel

```text
C = ((1+i) I + (1-i) X)/2,       C_d = C tensor ... tensor C  (d factors).
```

`C_0 = I`. The pinned Clifford implementation and signed-child note use
this convention. For `n >= 1`, join `q = 2^s` lanes, each with `2^n`
active coordinates; additional spectator fibers are unchanged. The lane
index is the high `s` bits. The desired operation on all lanes is
`I_q tensor C_n`. The exact circuit is

```text
(C_s^-1 tensor I) C_(n+s) = I_q tensor C_n.
```

The full transform runs first, then the inverse selector. This follows
from the tensor-product identity `C_(n+s) = C_s tensor C_n`, so it holds
for every size and every input, not just the finite replays. The inverse
selector is itself a recursive complex operation. It can use the existing
forward-child convention `C_s^-1 = (-i)^s Z_S C_s Z_S`: one width-s child,
two address-sign passes, and the exact global phase. The checker executes
the conjugated Gaussian coefficients directly and checks both directions.

**Monomial routing alone cannot supply the inverse selector.** Every entry
of `C_(n+s)` is nonzero, whereas a row of `I_q tensor C_n` has only `2^n`
nonzeros. Invertible monomial pre/post maps preserve the number of nonzero
entries per row (up to row permutation). For `s > 0` these support counts
differ. This excludes a single dense tensor child with only permutations
and nonzero diagonal scalings around it, even if those maps mix lane and
data coordinates. It does not exclude a nonmonomial encoding or additional
arithmetic. The tensor factorization and support argument are the written
all-size arguments; the finite checker is not a formal proof of them.

### Arbitrarily dirty padding

For `k < q` useful lanes, the other `q-k` lanes cannot be assumed zero.
After the two operations above every padded lane also contains `C_n z`.
Apply `C_n^-1` on each unused lane to restore its arbitrary initial value.
The complete endpoint is then

```text
(I_k tensor C_n) direct-sum I_((q-k) 2^n).
```

The checker includes `k=3, q=4` and propagates every initial padding column.
Omitting restoration leaves the useful outputs correct but corrupts padding;
its negative control specifically fails on a dirty input column. No clean
workspace assumption is hidden in the correct operator.

## Complete recursive bill and all-size comparison

Let `V` be one original lane's volume, including its spectator fibers.
Use the same inherited normalized child cost bound `A V d^sigma`, with
`0 < sigma < 1`, for every call. The volume factor is essential: a routine
acting on the joined array sees **`qV`**, not `V`.

| Operation | Width | Volume in units of V |
|---|---:|---:|
| Original k independent children | n | k |
| Joined tensor child | n+s | q |
| Inverse selector child | s | q |
| Restore dirty padding | n | q-k |

Thus the literal proposal substitutes the recursive budget

```text
B_original = A V k n^sigma
B_joined   = A V [q (n+s)^sigma + q s^sigma + (q-k) n^sigma] + E.
```

`E` denotes nonnegative gather/scatter and source-access work, coordinate
and frame changes, sign/phase passes, coefficient temporaries and their
restoration, and descriptor/precision work. The joined operation needs
`q` full lane volumes, including `q-k` padded ones. The finite circuit uses
no other logical lane; it is not a fixed-tape implementation or a new
proof of the inherited realization contract. We grant all work in `E`
for free here. The recursive bill alone already rejects the hypothesis,
so implementing or estimating those costs more closely cannot rescue this
particular bound comparison. For a constant-size selector one may instead
use direct butterflies; granting the entire selector operation for free
is even more favorable and gives the same conclusion.

Indeed `q >= k`, `s > 0` and `sigma > 0` imply

```text
q (n+s)^sigma > k n^sigma.
```

Even the joined child alone exceeds the original numerical budget under
the same cost model. This is an inequality between available upper-bound
expressions, **not** a lower bound on the optimal cost of either operator.

Two scaling regimes must be distinguished:

1. **A fixed number of streams.** For the selected pair, `k=q=2`, `s=1`
   and `n=2f`. The ratio is
   `(1+1/(2f))^sigma + (1/(2f))^sigma > 1`, tending to 1 as `f` grows.
   The leading moment contribution stays `2 * 2^sigma`. It does not become
   `3^sigma + 1`. A finite positive overhead must not be described as a
   strictly larger leading exponent; the asymptotic leading budget ties.
2. **A selector slot scaled with f.** To obtain the ranks `3f` and `f`
   literally, one needs `s=f` selector bits, hence `q=2^f` lanes. Keeping
   only two useful lanes introduces `2^f-2` dirty padded lanes. Already
   the joined-child ratio is `2^(f-1) (3/2)^sigma > 1`; restoration adds
   further work. Ignoring that growing volume is not a uniform compiler.

The fixed-lane argument also applies group by group to any partition into
equal-width batches. It does not cover fusing genuinely consecutive
operators on the same stream, changing the scalar network or owner map,
or a different recursion algorithm with independently proved costs.

### The false gain at the current supplier exponent

Use the source-bound complex endpoint
`b = 65528268492323474503/40000000000000000000000`, `sigma = 1-b`.
At `f=1`, the ratios to the original two calls are:

| Accounting | Ratio (rounded for display) |
|---|---:|
| Incorrect unweighted `C_3 + C_1` | 0.999786029497691095 |
| Complete volume-weighted `2 C_3 + 2 C_1` | 1.999572058995382190 |
| Joined child alone; inverse selector and all other work free | 1.499003977340941911 |

The wrong profile preserves the apparent rank mass (`3+1 = 2+2`) and
therefore looks particularly plausible. The real volume-weighted mass is
`2*3 + 2*1 = 8`, versus 4 originally. The displayed decimals are backed by
exact rational enclosures in the certificate, using atanh/Taylor remainder
bounds. Square-root probes independently check the enclosure routine by
squaring its endpoints. No floating-point search or solver claim is used.

## Coverage, controls and limits

The finite domain is all columns in both directions for `n=1..6, s=1..2,
k=2^s`; `n=1..4, s=2, k=3`; and `n=8, s=1, k=2`. The deterministic stopping
rule is completion of these 34 cases, the rational fixed-lane screens
`f in {1,2,4,8,16,32,128,1024}`, and slot-scaled screens `f=1..8`.
The infinite-size comparison comes from the displayed inequalities,
not from extrapolating these finite cases.

Negative controls remove the selector, use its wrong direction, act on
the wrong axis, change the global phase or normalization, omit dirty
restoration, omit joined volume, omit selector cost, and omit restoration
cost. The first six retain concrete failing matrix entries. The operator
engine uses Gaussian integer butterfly updates; its reference computes
each Kronecker entry as a product of `(1+i)` and `(1-i)`, independently.
No supplier verifier is changed, imported, or weakened.

This note adds a current-source-bound counterexample to unweighted
cross-stream batching, a padding repair, and a uniform scaling diagnosis.
The historical [sparse fusion audit](../../docs/research/sparse-fusion-audit.md)
already rejects partitioning one active-position set into separately charged
batches. The [signed whole-residual construction](../../notes/batched-complex-rows.tex)
instead combines tensor factors **within the same array volume** and is
unaffected. PR451's split-residual obstruction and PR665's spectral-dilation
experiment concern different interfaces. No claim of priority for the
elementary tensor identity or linear-volume accounting is made.

Local validation does not include a full supplier replay, repository-wide
`make verify`, Linux CI or Lean. The focused Linux workflow reports its status
separately on the PR. This package supplies no new owner assignment, tape
realization, precision/recovery theorem or improved multiplication exponent.
See [NOTICE.md](NOTICE.md) for attribution and assistance disclosure.
