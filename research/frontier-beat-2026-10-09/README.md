# Ways to beat the frontier kappa, priced exactly (2026-10-09)

The frontier is PR207's coordinated crossover. This directory changes no pinned
artifact: it reproduces that certificate's two side savings and its kappa from the
certificate's own child ledgers with no floating point, then prices every way the
record's own composition can move the headline.

```
python3 -B beats.py           # ~95 s, writes beats.json
python3 -B beats.py --check   # re-runs and compares byte for byte
```

## The frontier, and why it is one number

The certificate states `a_bit`, `a_complex` and `kappa`, and `kappa` is
`floor(min(a_bit, a_complex)/(1 + min(...)))` on a `10^-16` grid. So the headline is
a function of **one** quantity: the smaller side saving. Reproduced here:

| quantity | value | how it is reproduced |
| --- | ---: | --- |
| `a_bit` | `136731504666219/2*10^17` = 6.83657523331095e-4 | to **sixteen significant digits** under the bit side's convention; the certificate's own fraction sits `1.4e-16` lower (`2.1e-13` relative) |
| `a_complex` | `700918443859411/10^18` = 7.00918443859411e-4 | **exact to the last digit** |
| `kappa` | `1366380910073/2*10^15` = 6.831904550365e-4 | **exact**, and the grid is discovered, not assumed |
| binding side | **bit** (6.8366e-4 vs 7.0092e-4) | |

The bit side carries 2.5% of unused complex budget above it, and nothing in the
composition can spend it.

**A convention worth knowing.** The certificate prices its two sides *differently*:
the bit side includes PR200's rare-class fallback term, the complex side does not.
Each is reproduced exactly under its own convention here. The pinned ladder
(`rungs.json` in the supplier's package) prices *both* sides with the fallback, so
its numbers sit about `6e-10` relative below this package's; `beats.json` records
both conventions for every rung.

## Ranked ways to beat it

### 1. Bank a family on the bit word — the cheapest complete way

Banking means the family's children leave the ledger, the stock falls by the row
identity, and the paid moment pays less twice over. A family whose own blocks tile a
bank (`m % rank == 0`) and whose own volume is a whole number of banks needs no
block shape the word does not already use. **There are exactly three such families
on the bit word (6, 8, 18) and one on the complex word (11)**, and every
combination is priced here:

| absorb | new types | banks | kappa | gain |
| --- | ---: | ---: | ---: | ---: |
| bit **{6}** | 1 | 1008 | 6.979968750671e-4 | **+2.167%** |
| bit {8} | 1 | 816 | 6.937230027167e-4 | +1.542% |
| bit {18} | 1 | 999 | 6.912953180546e-4 | +1.186% |
| bit **{6,8}** | 2 | 1824 | 7.004275013051e-4 | **+2.523%** |
| bit {6,18} / {8,18} / {6,8,18} | 2–3 | 2007/1815/2823 | 7.004275013051e-4 | +2.523% |
| bit **{6,8} + complex {11}** | 3 | 2001 | 7.082915705907e-4 | **+3.674%** |
| bit {6,18} + complex {11} | 3 | 2184 | 7.06458935046e-4 | +3.406% |
| bit {8,18} + complex {11} | 3 | 1992 | 7.020811447888e-4 | +2.765% |
| bit {6} + complex {11} | 2 | 1185 | 6.979968750671e-4 | +2.167% |
| complex {11} alone | 1 | 177 | 6.831904550366e-4 | +0.000% |

Reading it:

* **+2.167% is the cheapest way to beat the frontier at all**: one new residual
  type, 1008 banks, the bit rank-6 family. The bit side is still binding
  afterwards, so the gain is the bit side's alone. [INSTANTIATE.md](INSTANTIATE.md)
  takes that rung apart: its block and bank schedule, and what the supplier's own
  bank proof already covers for it — the projector algebra is inherited, the
  per-copy allocation is integral, and the gap is an inventory (no pin enumerates
  the word's rank-6 children), not a piece of mathematics.
* **+2.523% is the first rung that makes the complex side binding** — the bit side
  clears the complex budget and the kappa becomes the complex cap. It agrees with
  #219's published rung 1 (`700427501305159/10^18`) on every digit the `10^-16`
  grid carries, so this rung is known and already claimed upstream.
* **+3.674% is the best rung that needs no new block shape** (bit {6,8} +
  complex {11}), and it is exactly the rung priced in the queue as the boundary:
  beyond it the complex word has nothing bankable on its own anymore. The two
  intermediate rows ({6,18} and {8,18} with complex {11}) sit between them, and
  every one of the 16 combinations is in `beats.json → strict_ladder`.
* Absorbing on the *non-binding* side is worth nothing: complex {11} alone moves
  the complex saving +1.12% and the headline by `+0.000%`.

### 2. The modelled tier — what the bank model pays, and what it assumes

The screen below treats an absorbed family's rank as free (only its volume must
fill whole banks), which is what #205/#206/#207 certified for rank 60 on width 72.
It runs over **every** family set of up to five families per word whose volume fills
whole banks — 3,512 admissible sets on the bit word, 991 on the complex word — and
decides each one with a single exact interval evaluation, no bisection and no
tolerance. The leaders of each family count are then priced exactly:

| families absorbed | best bit saving reached | best complex saving reached |
| ---: | ---: | ---: |
| 1 | `[22]` → 7.28397865314023e-4 (+6.54%) | `[11]` → 7.08793603125109e-4 (+1.12%) |
| 2 | `[19,21]` → 8.00024810534622e-4 (+17.02%) | `[1,8]` → 9.17460974044326e-4 (+30.89%) |
| 3 | `[1,7,21]` → 1.05220678470506e-3 (+53.91%) | `[1,2,18]` → 1.25531712077191e-3 (+79.10%) |
| 4 | `[1,3,13,21]` → 1.22799457745093e-3 (+79.62%) | `[1,2,3,9]` → 1.40686129974894e-3 (+100.72%) |
| 5 | `[1,3,13,21,22]` → 1.38023409118239e-3 (+101.89%) | `[1,2,3,4,19]` → 1.63407154980676e-3 (+133.13%) |

Each side's column is the leader of that family count by the exact screening key, priced
exactly; the bit side's rank-1 masses (9.3% of its ledger) and the complex side's rank-1
and rank-2 masses (11.0% and 10.0%) are the big movers, which is why the ladder is so
steep once the small families are gone.

### 2b. One family deeper: where the model tops out on each side

`beats.py --max-types 6` moves the screen one family further on both words (~157 s on
this machine, 1.7x the five-family screen; its artifact is `beats-six.json`). The
admissible space triples to 10,318 family
sets on the bit word and 2,725 on the complex one, and the ladder reads:

| families | best bit saving | best complex saving |
| ---: | ---: | ---: |
| 5 | `[1,3,13,21,22]` → 1.38023409118239e-3 (+101.89%) | `[1,2,3,4,19]` → 1.63407154980676e-3 (+133.13%) |
| **6** | **`[1,3,13,20,21,22]` → 1.52739614292328e-3 (+123.42%)** | **`[1,2,3,8,15,18]` → 2.30539885681005e-3 (+228.91%)** |

The two sides do not top out together: the six-family removals take 59.7% of the bit
ledger (33,599 banks) and 65.6% of the complex ledger (7,895 banks). Because the
headline is the *smaller* budget, the model's best pairing is bit six families with
complex four — `kappa = 1.5250667618335e-3` (**+123.23%**), 11 new residual types,
binding bit, removing 59.7% of the bit ledger and 33.8% of the complex one. The
complex side's extra hundred points are unspendable while the bit side is the lower
of the two.

This is the same model as the four-family ladder one family deeper, so section 2's
caveats apply unchanged — and the growth is a warning about the model rather than
evidence about the word: each step removes a larger share of the paid dirt, and the
savings climb faster than the removed share because dropping small children also
shrinks the log budget `L`.

Two facts fall out of the screen:

* **Nearly any bit-side absorption clears the complex side**: 3,502 of the 3,512
  admissible sets do. The bit word can be lifted past 7.0092e-4 in hundreds of ways
  — the family that has to move for a bigger headline is the *complex* one.
* **The best screened rung in this model is `+101.75%`**, at 9 new residual types:
  (the best of the leaders of each family count, priced exactly; the screen is
  exhaustive over sets of up to five families per word, but the global optimum over
  all sets is not established, so this is a leader, not a proven maximum)
  bit absorbs ranks {1, 3, 13, 21, 22} and complex absorbs {1, 2, 3, 9},
  `kappa = 1.3783316708213e-3`, binding bit, 33,261 banks. The pinned ladder's own
  best is `+79.5%` (`1.2264884e-3`, 8 types) — the same model capped at four
  families per word, so this is the pinned screen extended one family deep, not a
  different construction. The four-family bit rung reproduces the pinned
  `1.22799457745093e-3` to the last digit.

**What the modelled tier assumes** (re-derived in `beats.json → audit`):

1. **Every family left in the frontier word is retained dirt.** #207 banked the
   rank-60 *entrance exteriors*, and the frontier profile no longer carries them
   (bit maxchild 22, complex maxchild 20). So the exteriors are already spent, and
   every rung here removes *interior* children — the top rung removes **51.8% of
   the bit ledger and 33.8% of the complex ledger**.
2. **Each absorbed family needs a new residual type**, which the supplier's proof
   reserves for the future. The queue's own allocation records exactly this verdict
   for its single-family rung: *"needs the new residual type the supplier's proof
   reserves; not buildable with the construction as published."*
3. **The rank-free rule is certified precedent only for one exterior**, of one
   child per selected gauge, not for interior dirt.
4. The bank charts, the normalizers, the `F2` and defining-integer columns and the
   per-bank prime witnesses are the supplier's harness and are not built here.

So the modelled tier is a **priced upper bracket**, not a route. What it is good
for is the requirement side: it says which *family counts* each target demands, and
it shows the model's own curvature — one family buys +2.2% at the bottom of the
ladder and +6.5% at the top, because absorbing a larger family removes more rank
mass from a ledger of fixed size.

### 3. The routes that do not need a bank at all

* **A new bit word.** PR192 bounds the bit word *family*'s frame-layout ceiling at
  `7.010e-4`, and the sinks and reuse pairs on the current bit word are maximal
  (all 34 rank-21 sinks, all 1,760 pairs). A perfect new bit word therefore reaches
  `7.010e-4 > 7.0092e-4` — it clears the complex side and buys **+2.523%**, no
  better than the two-family bank rung, at the cost of a new word. Every bit-side
  PR in the queue is bounded the same way.
* **A new complex network.** This is where the headroom actually lives. The queue's
  own analysis of this complex word family (`m = 66`, deficit 1,320) puts the
  implied log budget `L1 = deficit/(m·W·kappa)` at about 2.27 and the
  mass-at-largest-child relaxation of the same `(m, W, s)` at a root near `9.8e-2`,
  roughly 150x the current saving; that is a different (relaxation) model, quoted
  rather than recomputed here, and it says the pinned complex *construction* is the
  wall, not its arithmetic.
* **Assembly and grid refinements — do not bother.** The assembly's loss is `a²`
  (4.7e-7, which is why `kappa ~ a/(1+a)`) plus the backoff; the grid is already
  `10^-16`; re-pricing at a finer grid, or tightening the `1e-9`/`1e-10` steps the
  older ladder carried, is worth less than `1e-4` relative here.

## What each gain needs, exactly

`beats.json → requirements`, for the smaller side saving the assembly has to see:

| target | needed side saving | over today's binding side |
| --- | ---: | ---: |
| beat the frontier by 0.1% | 6.84341648710e-4 | +0.100% |
| by 1% | 6.90498819211e-4 | +1.001% |
| by 5% | 7.17864938186e-4 | +5.004% |
| by 10% | 7.52074691816e-4 | +10.008% |
| by 25% | 8.54717987759e-4 | +25.021% |
| by 50% | 1.02583694557e-3 | +50.051% |
| `kappa = 2^-10` | 9.77517106549e-4 | +42.983% |
| `kappa = 1e-3` | 1.00100100100e-3 | +46.419% |

Within the bank model both sides clear all of these; that is a statement about the
model, not about the construction.

## Verification boundary

* Reproduced exactly from the certificate's own rows: `a_complex` to the last digit,
  `a_bit` to 16 significant digits (`1.4e-16` absolute, `2.1e-13` relative), and the
  certificate's `kappa` exactly, on a grid discovered by search rather than assumed.
* The ladder's zero point is the same frontier within one `10^-16` grid step, and
  every rung is priced by the supplier's own enclosure implementation
  (`references/pr200/interval_moment.py`, vendored; both pins are hashed against
  [SOURCE.json](SOURCE.json) at the top of every run, and the run fails on a mismatch).
* The four-family bit rung and the four-family complex rung reproduce the pinned
  ladder's values (`1.22799457745093e-3` and `1.406861298932255e-3`) exactly, in the
  paid-convention field `beats.json` records beside every rung.
* The six-family leaders were re-derived independently of the screening code: their
  absorbed rows were rebuilt from the certificate and re-priced, and their savings
  matched the artifact under both conventions, as did the best rung's kappa.
* [check_docs.py](check_docs.py) re-checks every number this README and
  `INSTANTIATE.md` quote against the three artifacts — 41 table numbers and 44
  required claims on the current revision — and fails if a value is altered or a
  claim disappears.
* [instantiate.py](instantiate.py) re-derives the bank schedule of the +2.167% rung
  from the same rows and turns the vendored bank proof into the checklist in
  [INSTANTIATE.md](INSTANTIATE.md).
* **Not claimed:** any bank construction, any new residual type, any replay of the
  physical words, any contributor verifier or upstream CI run. The rungs are priced
  targets; the gain on the *headline* is conditional on the bank harness the
  supplier's proof describes but does not instantiate.

## Reproduce

```sh
python3 -B beats.py                 # ~91 s, writes beats.json (five families per word)
python3 -B beats.py --check         # byte-for-byte comparison with it
python3 -B beats.py --max-types 6 --out beats-six.json          # ~157 s, one family deeper
python3 -B beats.py --max-types 6 --out beats-six.json --check  # ~157 s, same comparison
python3 -B instantiate.py           # ~2 s, writes instantiate.json
python3 -B instantiate.py --check
```

Every `--check` re-runs the whole screen and compares its text with the committed
artifact byte for byte, naming the file it compared: the two depths are checked
separately, and `--check` is the only way to tell the six-family artifact from the
five-family one. The six-family screen is the expensive one by 1.7x; `instantiate.py`
is seconds.
