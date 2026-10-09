# Composing the stronger bit supplier with the record's assembly

Under the retained interfaces of the pinned suppliers, this package prices PR200's
bit supplier with PR184's finite leaf bootstrap and PR193's complex word through
PR194's unchanged assembly:

$$\kappa = \frac{1693287}{2500000000} = 6.773148\cdot10^{-4},$$

**+0.1826%** over the standing claim (#197, `135216063303877/2e17 =
6.76080316519385e-4`) and **+0.0639%** over the value PR200 announces for this
same composition (`6768823/10e9 = 6.768823e-4`), which it says it is preparing as
separate work.

| PR | author | kappa | what it changed |
| --- | --- | --- | --- |
| #200 | chafreaky | 6.65046903615388e-4 | new bit **and** complex word; with its *own* complex word the complex branch binds and the headline equals #196. Its README: the bit supplier "would give about 6.769e-4" composed with #193/#194's complex — "which I am preparing as a separate stacked composition". |
| **#197** | evmckinney9 | **6.76080316519385e-4** | packed #187 rank-4/rank-24 residuals + #193 complex + the finite leaf. The standing claim. |
| #198 | sennemmi | 6.679123e-4 | 102 lowered #189 endpoint frames + the finite leaf; a draft that does not claim the record. |
| this | Maxime Fleury | **6.773148e-4** | #200's bit word + #193's complex + #185's finite leaf, on PR194's assembly. |

## Result

Exactly three things are inherited: the bit supplier's certificate (#200), the
complex supplier and the 47-constraint assembly (#193/#194), and the finite
ordinary-leaf wrapper's recurrence (#185). Nothing is re-derived; the one operation
is pricing.

| depth | bit leaf | kappa | vs #197 | vs the unbootstrapped composition |
| --- | --- | --- | --- | --- |
| 0 (PR184's legacy atom wrapper, = #200's announced value) | 6.77340866500955e-4 | 6768823/10000000000 = 6.768823e-4 | +0.1186% | — |
| 1 | 6.77773606501196e-4 | 1354629/2000000000 = 6.773145e-4 | +0.1825% | +0.0639% |
| 2, 3, 8 | 6.77773899999987e-4 | **1693287/2500000000 = 6.773148e-4** | **+0.1826%** | +0.0639% |

The bit profile priced here has `m = 72`, `W = 20634`, rank deficit 1936 and 34
terminal sinks; the complex saving is `219037/312500000 = 7.009184e-4`, so the bit
branch binds at every depth and the complex side is not a constraint.

## Why this is the last pricing room on this word

For a fixed bit word the assembly's `kappa` is capped by the word's own coarse
saving: `kappa <= C/(1+C)`. For #200's certificate `C = 6777739/10^10` and

$$C/(1+C) = 6.7731483368\cdot10^{-4},$$

so the claimed value sits **3.4e-11** below that ceiling — under a third of one
`10^-10` selection step. The finite-leaf recurrence

$$a_{n+1} = (1-C)\,C + C\,a_n = C - C^{\,n}(C-a_0)$$

recovers the whole `4.33e-7` of slack the legacy atom wrapper leaves below `C`, and
depths 2, 3 and 8 return the same grid value, so **no further leaf work can move
this number**. Both remaining levers reduce `W` on this word, and both are new
constructions on #200's graph rather than a recomposition:

* **endpoint-frame descent** — what #198 did on #189's word, worth +0.0090% of
  coarse saving there (`6.68298937775631e-4 -> 6.6835882709e-4`);
* **residual packing** — #197's mechanism, bound to #187's word, worth +0.8403% of
  coarse saving there (`6.70899981048852e-4 -> 6.76537710350481e-4`), the largest
  single bit-side gain in the queue.

Because the bit branch binds, complex-side work is worthless here until a bit
coarse saving passes the complex word's `7.009184e-4`.

## Where the next gain is, measured

The bit branch's coarse saving is the largest `a` whose paid moment is below 1,
and the row identity `m*W - sum_r n_r*r = D` means two words with the same `D`
differ only through the child ledger. `levers.py` solves that inequality exactly
over the rationals and models the one lever that has already been validated on a
word of this family: PR197's banking of the rank-60 exterior corrections, which
drops those entries from the ledger and leaves the stock at what the identity
requires.

The model is checked against the three published values it can be checked on, and
reproduces all three **exactly**: it prices with PR200's own enclosure module
(`references/pr200/interval_moment.py`, vendored byte-identically, the arithmetic
PR200's `bit/prove.py` uses) on the same `10^-18` grid, so the certified grid
points agree bit-for-bit rather than to a tolerance. Rows are taken over the
family's three copies, which keeps the stock integral and leaves the saving
unchanged.

| row | W | D | model = published | source |
| --- | --- | --- | --- | --- |
| PR187's word, unpacked | 63,324 | 5,808 | 167724995262213/250000000000000000 = 6.70899981048852e-4 | PR187's certificate |
| PR187's word, banked | 57,824 | 5,808 | 676537710350481/10^18 = 6.76537710350481e-4 | PR197's **certified** packed word |
| PR200's word, unpacked | 61,902 | 5,808 | 677773948354561/10^18 = 6.77773948354561e-4 | PR200's certificate |

The second row is the meaningful one: the model reproduces, from the unpacked
ledger alone, the exact value PR197 certified after building the banks — so on a
word of this family the accounting step is the whole of the gain, with nothing
left to a numerical accident.

Applied to this package's bit word, banking its 2,200 rank-60 exterior
corrections (132,000 of 1,483,712 rank mass, 8.90% of the child ledger) leaves
`W_per_vertex = 56402/3`, `D = 1936` and a ledger with no child above rank 22, and
gives

| | coarse saving | kappa ceiling |
| --- | --- | --- |
| this package's word, as certified | 677773948354561/10^18 = 6.77773948354561e-4 | 6.77314882e-4 |
| the same word, banked | 683528191056257/10^18 = 6.83528191056257e-4 | **6.83061299e-4** (**+0.8484%**) |

**This is a prediction, not a claim.** The bank construction on PR200's word is
not built here, and the package's `levers.json` records that status literally.
What the model does give is a falsifiable target for whoever builds it: over the
three copies, a bank allocation must reach a total stock of `56,402` roles with
the per-copy deficit unchanged at `1,936` and no rank-60 child remaining. That
target is sharp — the model's own three cross-checks say that hitting the
allocation is what buys the `0.8484%`, since on PR197's word the identical
accounting reproduced the certified value exactly. The other known lever is an
order of magnitude smaller: PR198's endpoint-frame descent bought `+0.0090%` of
coarse saving on PR189's word.

## The frontier moved, and this package priced the move first

This composition was priced at 15:33 UTC on 2026-10-09. Within the next half hour
the banked rows the lever model had predicted were built and opened as three PRs:

| PR | author | kappa | row |
| --- | --- | --- | --- |
| #205 | rohanarun | 683061299399923/10^18 = 6.83061299399923e-4 | PR200's word with its rank-60 exterior corrections banked |
| #206 | EcmaXp | 6830611/10^10 = 6.830611e-4 | the same row, PR186's entrance banks |
| #207 | Dugongue | 1366380910073/2e15 = 6.831904550365e-4 | the same row after 302 coordinated frame changes |

#205's coarse saving is `683528191056257/10^18` -- **the exact value the lever model above
predicted for the banked word** (`W_per_vertex = 56402/3`, deficit 1,936, no rank-60
child left), which #205 records in its own credits. So this package's composition is
superseded, and what it still supplies is the model that called the move and can price
the rows that followed it.

`audit.py` does that: it prices the queue's banked rows from byte-identical copies of
their authors' certificates and requires the result to appear *verbatim* in those
certificates.

| row | W | deficit | rank mass | children | model coarse saving |
| --- | --- | --- | --- | --- | --- |
| #205 packed diagonal bit | 56,402 | 5,808 | 4,055,136 | 877,638 | 683528191056257/10^18 |
| #206 entrance banks on #200 | 56,402 | 5,808 | 4,055,136 | 877,638 | 683528191056257/10^18 |
| #207 coordinated crossover | 56,402 | 5,808 | 4,055,136 | 879,231 | 136731504666219/2e17 |

Every one of the three is reproduced to the last digit, and every one is at its own
word's ceiling: with the bit branch binding there is no pricing room left in any of
them. What is left is the *ledger*. Per unit of rank mass a child of rank `r` costs
`(m/r)^a/(W m)`, which falls as `r` grows, so the cheapest integral ledger with the same
stock, deficit and mass packs it from the largest admissible child downwards. For the
frontier row that is 184,325 children instead of 879,231, and it would raise the coarse
saving by **76.6%**, from `6.8366e-4` to `1.2072e-3` (kappa ceiling `1.2057e-3`). No
schedule admits that ledger, so this is a **bound on the ledger term, not a
construction** -- but it is the whole of the remaining room, and it says the next move
is a frame or bank schedule whose residual dirt is packed in fewer, larger children,
not more packing of the same shapes.

## New ways to raise kappa, priced with the assembly's own formula

PR184's unchanged assembly takes `a = min(bit leaf, (1-1e-9)*C_complex - 1e-10)` and
returns `kappa = a/(1+a)` on the `10^-10` grid, so **the smaller branch is the whole
constraint** and a gain on the stronger side is worth nothing until the other side
catches up. Today the bit branch binds at `6.831904e-4`, while the complex side caps
at `7.004273e-4`: **+2.52% is available with no complex-side work at all**, as soon as
the bit word's coarse saving reaches `7.009184e-4` instead of `6.836575e-4`.

`targets.py` prices the ladder of moves that can get there. For a fixed stock and
deficit the coarse saving is `C = (1 - mass/(W m)) / L` with `L` the rank-mass-weighted
mean of `ln(m/r)`, so the lever is `L`: a ledger whose residual dirt sits in fewer,
larger children. Soaking every child of rank at or below a threshold into the largest
admissible child gives, on the queue's own two rows:

| soak | bit coarse saving | complex coarse saving | kappa | gain | binds |
| --- | --- | --- | --- | --- | --- |
| today | 136731504666219/2e17 | 350459221139329/5e17 | 6.831904e-4 | — | bit |
| bit only, rank-1 | 792978386838687/10^18 | — | 7.004273e-4 | +2.52% | complex |
| both, rank-1 | 792978386838687/10^18 | 814442339516203/10^18 | 7.923515e-4 | +15.98% | bit |
| both, rank-2 | 898167154125293/10^18 | 918515942111545/10^18 | 8.973611e-4 | +31.35% | bit |
| both, rank-3 | 981391149202381/10^18 | 1041436537175764/10^18 | 9.804289e-4 | +43.51% | bit |
| both, rank-4 | 1015042828910707/10^18 | 1112905588874264/10^18 | 1.014014e-3 | +48.42% | bit |
| both, rank-8 | 1096975618911405/10^18 | 1243672552482743/10^18 | 1.095774e-3 | +60.39% | bit |
| both, rank-16 | 1178908992537918/10^18 | 1367642974340202/10^18 | 1.177521e-3 | +72.36% | bit |
| cheapest ledgers | 1207154248293627/10^18 | 1391081382485139/10^18 | 1.205699e-3 | +76.48% | — |

The cheapest step is smaller than the table suggests. The bit word needs a coarse
saving of `7.009184e-4` to stop binding, and the cheapest 5.7% of its smallest
children already delivers it: `targets.py` bisects that population and reports that
**moving 57/1000 of the mass sitting in the bit word's rank-1 children into
rank-22 children takes the bit coarse saving to `7.009717e-4`**, past the complex
word, for `kappa = 7.004273e-4` (+2.52%). The whole rank-1 population (377,316
children, 9.3% of the rank mass) is worth +16% on its own, and the complex word's
own 87,534 rank-1 children (11% of its mass) do the same for its side,
`7.009184e-4` to `8.144423e-4` (+16.2%).

**What has to change is the child inventory, not the packing.** #207's bank proof
settles the packing side itself: its banks tile width 72 exactly with the word's two
residual families (`6 x rank-4 + 2 x rank-24`, or `3 x rank-24`), and it states that
the current word "has exactly the 4/24 residual families and both tile 72 exactly ...
there is no new LP improvement to add". The children the moment actually charges are
the word's own retained children -- internal, source, target, center, compensating
and terminal-substitution children -- and it is their inventory, set by the weighted
compilation and by the frame schedule, that holds the `L` above `ln(m/22)`.

**All of this is MODELLED, NOT CONSTRUCTED.** No ledger is built here: each rung is a
shape the assembly would price this way, computed from the queue's certified rows. The
calculator is checked two ways -- it equals PR184's own `assemble()` on the vendored
pair, and it reproduces #205's and #207's published kappa to within one grid step --
so a rung is a usable target rather than a guess, in the same way the lever model's
banked row was.

### The big rungs: absorbing whole families into the banks

Re-ranking children keeps the stock. The bank construction does something strictly
stronger: the dirt of an *absorbed* family leaves the ledger, so by the row identity
`W = (mass + D)/m` the stock falls with it, and the paid moment pays twice over. That is
exactly the mechanism #197 used on the rank-60 exterior corrections and #205 used to
reach this frontier, and it is the mechanism the audit's `76.6%` bound says the
remaining room is in.

`rungs.py` prices it for whole child families. Every combination of up to four families
of either word is screened across **all** ranks with this package's own ledger form
(`C = (1 - mass/(W m))/L`, the decomposition `targets.py` documents), the best of each
subset size is priced *exactly*, and the first search's window is kept alongside so that
nothing regresses.

A bank is a width-`m` coordinate-block partition, so a family set is a schedule only
when its blocks *tile* a bank. That gives two tiers, and the difference between them is
the whole story:

* **sound.** Every family's rank divides the bank width and its own volume is a whole
  number of banks, so the families can be banked one at a time with no block shape the
  word does not already use. #207's own schedule is this shape (`18 x rank-4`,
  `3 x rank-24`, and the mixed `6 x rank-4 + 2 x rank-24`).
* **volume only.** Only the total fills whole banks. This is exactly what the
  *certified* banks of #197/#205/#207 satisfy -- their absorbed rank 60 does not divide
  72 either -- but it is an upper bracket here: it needs the supplier to bank a family
  whose blocks are drawn from the construction's own residual shapes, which this package
  cannot verify.

On the two frontier words, only these families are sound: the bit word's ranks
**6, 8 and 18**, and the complex word's rank **11**.

| rung | new residual types | bit word absorbs | complex word absorbs | bit coarse saving | complex coarse saving | kappa | gain | binds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| today | 0 | -- | -- | 6.836575e-4 | 7.009184e-4 | 213497/312500000 = 6.831904e-4 | -- | bit |
| sound | **1** | rank 6: 1,008 banks | -- | 174621103751517/2.5e17 = 6.984844e-4 | -- | 54531/78125000 = 6.979968e-4 | **+2.17%** | bit |
| sound | 2 | ranks 6, 8: 1,824 banks | -- | 141899511517939/2e17 = 7.094975e-4 | -- | 7004273/10^10 = 7.004273e-4 | **+2.52%** | complex |
| sound | **3** | ranks 6, 8 | rank 11: 177 banks | 7.094975e-4 | 708793601534531/10^18 = 7.087936e-4 | 3541457/5e9 = 7.082914e-4 | **+3.67%** | complex |
| sound | 4 | ranks 6, 8, 18: 2,823 banks | rank 11 | 718242431279183/10^18 = 7.182424e-4 | 7.087936e-4 | 3541457/5e9 = 7.082914e-4 | +3.67% | complex |
| bracket | 1 | rank 22: 6,116 banks | -- | 728397865314023/10^18 = 7.283979e-4 | -- | 7.004273e-4 | +2.52% | complex |
| bracket | 3 | rank 22 | ranks 1, 8 | 7.283979e-4 | 9.174610e-4 | 7.278676e-4 | +6.54% | bit |
| bracket | 5 | ranks 1, 7, 21 | ranks 1, 8 | 1.052207e-3 | 9.174610e-4 | 9.166198e-4 | +34.17% | complex |
| bracket | 8 | ranks 1, 3, 13, 21 | ranks 1, 2, 3, 9 | 1.227995e-3 | 1.406861e-3 | 1.226488e-3 | +79.52% | bit |

Four readings matter:

* **one sound new residual type moves the record.** Absorbing the bit word's rank-6
  children alone, with the complex word untouched, takes the frontier from
  `6.831904e-4` to `6.979968e-4`, **+2.17%** -- and unlike the re-ranking rung it needs no
  cooperation from the complex side, because it lowers the stock instead of leaning on
  the other branch's ceiling.
* **two sound types reach the complex side's cap exactly.** Bank the bit word's ranks 6
  and 8 and its coarse saving passes `7.009184e-4`, so the pair prices at the unmoved
  complex side's own ceiling, `7.004273e-4` (**+2.52%**) -- the same number the re-ranking
  ladder reached, now with `W` down from `56,402` to `54,578`.
* **three sound types pass the cap, and it is the complex word that then binds.** Adding
  the complex word's single sound family (rank 11, 177 banks) takes the pair to
  **+3.67%**; the bit word's fourth family (rank 18) then buys nothing, because the
  complex side is binding again. The sound tier stops there: only ranks that tile the
  bank width are bankable one family at a time, and this word has three on the bit side
  and one on the complex side.
* **the volume bracket is where the big numbers live, and it is not the claim.** Ranking
  by volume alone (which is what the queue's certified banks actually did -- rank 60 does
  not divide 72) opens rungs at `+2.52%` for one type, `+6.54%` for three, `+34.17%` for
  five and `+79.52%` for eight. Whether those are schedules depends on the supplier's
  construction accepting a family whose blocks are not its own children, which is exactly
  the question its own "ready for future genuinely different residual types" leaves open:
  so the bracket is recorded as a bracket, and the claim is the sound tier.

Every schedule in the table also satisfies the checks the package can make on its own:
whole banks (`banks * m` equals the absorbed rank mass), the row identity after
absorption, the paid moment's adjacent-grid exclusion, and the assembly's own arithmetic.
`verify.py` re-derives the sound families of both words from the queue's certificate,
re-prices the first four sound rungs from that certificate without using `rungs.py`, and
requires each recorded kappa to follow from its own schedule.

**These are targets, and the physical side is not done here.** The chart and normalizer
conjugations, the F2 and defining-integer columns, the group-indexed role bookkeeping and
the per-bank prime witnesses are the supplier's harness, and `rungs.json` records that
status literally. What is proven here is the accounting: *if* a family of the frontier
word's children is absorbed into the banks the way #197 and #205 absorbed residuals,
*then* the frontier's own assembly returns the kappa in the table -- and `rungs.py` says
which families can be banked at all, which is a tiling condition no proposal can dodge.

## Cross-checks against published numbers

The harness is independent of the numbers it is asked to confirm, and this package
checks it twice against public statements:

* **depth 0 reproduces #200's own value** for this composition: `6.768823e-4`
  against its announced "about 6.769e-4", and against #202, which published that
  same composition at that same value. Since depth 0 is PR184's legacy wrapper
  applied to #200's certificate, agreement pins the whole pricing path (profile
  reading, `select()`, assembly, grid), and the whole of the improvement claimed
  here is the finite leaf the other PR does not apply.
* **PR184's grid legacy leaf agrees with #200's published atom wrapper**:
  `6.77340866500955e-4` versus `6.77340914792209e-4` from its documented
  `theta = 677340914792209011107/10^24` and `a_0 = 677773948354561/10^18`, a
  difference of `4.83e-11` that floors to the same grid value. The residual is the
  suppliers' own choice of wrapper precision, and it is recorded rather than
  smoothed over.

## Scope and limits

* The physical complex and bit words, their frames, sinks and paid moments are the
  suppliers' certified artifacts, vendored byte-identically and **priced, not
  rebuilt or replayed**. In particular #200's bit certificate is taken as its
  author's finite witness; this package does not re-run its checks.
* The wrapper is PR185's construction, not one built here.
* Conditional on PR184's finite bridge and closed-form acceptance arithmetic, and
  on the retained contracts of the pinned suppliers. The full multiplication
  theorem remains conditional; a finite certificate is not a proof of it.
* The improvement is small and lives on the `10^-10` selection grid, and it
  depends on an unmerged bit supplier (#200) and an unmerged complex/assembly line
  (#193/#194).
* This is not claimed as a new word, a new all-size hypothesis, or the public
  record: it is a composition, and it is superseded the moment a lower-`W` bit word
  appears.

## Reproduce

```bash
python3 -B research/composed-diagonal-bit-bootstrap/verify.py
```

`compose.py` performs the pricing; `verify.py` pins every byte against
`SOURCE.json`, reproduces `certificate.json` from the pins, re-checks the two
published cross-checks above, requires the claim to beat #197, requires it to sit
inside one grid step of the word's ceiling, re-derives the leaf tolls in closed
form, refuses three corruption controls, and re-runs the lever model, requiring it
to reproduce its three published references *exactly* and to keep its `MODELLED,
NOT CONSTRUCTED` status. The lever run takes about two seconds and the bank-absorption search about
thirty; the whole harness runs in roughly seventy seconds.

```bash
python3 -B research/composed-diagonal-bit-bootstrap/levers.py
```

prints the lever table on its own, and

```bash
python3 -B research/composed-diagonal-bit-bootstrap/audit.py
```

prints the queue audit against the banked rows the lever predicted, and

```bash
python3 -B research/composed-diagonal-bit-bootstrap/targets.py
```

prints the ladder of what each next ledger move on the two suppliers would be worth, and

```bash
python3 -B research/composed-diagonal-bit-bootstrap/rungs.py
```

prints the bank-absorption ladder: which whole child families of the frontier word can
be taken together, what the schedule is worth, and how many new residual types each rung
would need.

## Credits

Bit supplier: chafreaky (#200, with the #189/#196 lineage). Complex word and
assembly: icekylinx, GPT-6 Astra and ikeboy (#182/#184/#193/#194). Finite leaf
wrapper and its recurrence: rohanarun (#185). Paired-cube frame and balanced-prefix
construction: eumemic (#168 v4). Predecessor notices are retained in
[NOTICE.md](NOTICE.md). Apache-2.0.
