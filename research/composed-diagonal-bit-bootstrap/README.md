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

The model is checked against the three published values it can be checked on, all
to `1e-13` relative or better:

| row | model | published | source |
| --- | --- | --- | --- |
| PR187's word, unpacked | 6.70899981048782e-4 | 6.70899981048852e-4 | PR187's certificate |
| PR187's word, banked | 6.76537710350471e-4 | 6.76537710350481e-4 | PR197's **certified** packed word |
| PR200's word, unpacked | 6.77773948354529e-4 | 6.77773948354561e-4 | PR200's certificate |

The second row is the meaningful one: the model reproduces, from the unpacked
ledger alone, the value PR197 certified after building the banks.

Applied to this package's bit word, banking its 2,200 rank-60 exterior
corrections (132,000 of 1,483,712 rank mass, 8.90% of the child ledger) leaves
`W_per_vertex = 56402/3`, `D = 1936` and a ledger with no child above rank 22, and
gives

| | coarse saving | kappa ceiling |
| --- | --- | --- |
| this package's word, as certified | 6.77773948354529e-4 | 6.77314882e-4 |
| the same word, banked | 6.83528191056250e-4 | **6.83061299e-4** (**+0.8484%**) |

**This is a prediction, not a claim.** The bank construction on PR200's word is
not built here, and the package's `levers.json` records that status literally.
What the model does give is a falsifiable target for whoever builds it: over the
three copies, a bank allocation must reach a total stock of `56,402` roles with
the per-copy deficit unchanged at `1,936` and no rank-60 child remaining. The
other known lever is an order of magnitude smaller: PR198's endpoint-frame
descent bought `+0.0090%` of coarse saving on PR189's word.

## Cross-checks against published numbers

The harness is independent of the numbers it is asked to confirm, and this package
checks it twice against public statements:

* **depth 0 reproduces #200's own value** for this composition: `6.768823e-4`
  against its announced "about 6.769e-4". Since depth 0 is PR184's legacy wrapper
  applied to #200's certificate, agreement pins the whole pricing path (profile
  reading, `select()`, assembly, grid).
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
to reproduce its three published references and to keep its `MODELLED, NOT
CONSTRUCTED` status.

```bash
python3 -B research/composed-diagonal-bit-bootstrap/levers.py
```

prints the lever table on its own.

## Credits

Bit supplier: chafreaky (#200, with the #189/#196 lineage). Complex word and
assembly: icekylinx, GPT-6 Astra and ikeboy (#182/#184/#193/#194). Finite leaf
wrapper and its recurrence: rohanarun (#185). Paired-cube frame and balanced-prefix
construction: eumemic (#168 v4). Predecessor notices are retained in
[NOTICE.md](NOTICE.md). Apache-2.0.
