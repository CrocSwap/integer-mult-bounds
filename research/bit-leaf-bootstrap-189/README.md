# Bit leaf bootstrap: PR194 pricing, and the higher bit supplier

## Status (2026-10-09) — where this stands

The queue moved after this package was opened. Exact standing claims, taken from
the open pull requests (not from this package):

| PR | author | kappa | lever | notes |
| --- | --- | --- | --- | --- |
| #200 | chafreaky | **6.65046903615388e-4** (`166261725903847/25e16`) | new bit **and** complex supplier | With its own complex word *the complex branch binds*, so the headline equals #196. It also states that composed with #193/#194's complex word its bit supplier "would give about 6.769e-4, which I am preparing as a separate stacked composition". |
| #197 | evmckinney9 | **6.76080316519385e-4** (`135216063303877/2e17`) | packs #187 rank-4/rank-24 residuals; #193 complex | Its own body: +0.8398% packing gain over `0.000670450176035363`, 1.2957% above #194. **The highest standing kappa claim.** |
| #198 | sennemmi | **6.679123e-4** (`6679123/10^10`) | 102 lowered PR189 endpoint frames + the finite leaf wrapper | Draft. Explicitly "not claimed as the current public record" and "do not claim to beat #197". Credited here: "the finite depth-2 ordinary-leaf wrapper uses the PR185 recurrence **first applied to PR189 by PR199**". |
| #199 | this package | 6.678525e-4 (`267141/400000000`) | finite leaf bootstrap on PR194's inputs | Reproduces PR194's kappa exactly from PR194's own profiles; the wrapper is the only change. |

So on the record's own inputs this package's headline is **superseded**:

* by **#198**, which applies the same recurrence to a *descended* PR189 bit word
  (lower W ⇒ higher coarse saving), and states plainly that the recurrence and
  wrapper are "credited, not claimed as new work" to PR185 and this PR. This
  package is therefore the first published application of the PR185 bootstrap to
  PR189's bit word, not the current best;
* by **#197**, which raised the bit supplier itself (residual packing) rather
  than its pricing.

What this package still provides uniquely:

* an **exact reproduction harness** for a published record: it rebuilds PR194's
  kappa `1668581/2500000000` from PR194's own profiles through PR194's own
  `select()` and `assemble()` (depth 0 below *is* that reproduction), so any
  re-pricing delta is isolated to the leaf;
* the **maximality proofs** for the two W-lowering levers on PR189's bit word
  (terminal sinks 34 of 34; donor reuse 1760 of 3960 gauges) — see
  [bit-maximality.md](bit-maximality.md);
* a **supplier-agnostic pricing path**: [next_bit_composition.py](next_bit_composition.py)
  prices *any* certified bit profile with the same bootstrap against PR193's
  complex through PR194's unchanged assembly. Applying it today gives the
  highest kappa computed anywhere in this queue (next section).

## Beating the standing best: the composition #200 deferred, plus the bootstrap

#200 supplies a strictly stronger bit word — coarse saving
`677773948354561/10^18 = 6.77773948355e-4` against PR189's
`668298937775631/10^18 = 6.68298937775631e-4` — but publishes it with its own
complex word, where the complex branch binds, and explicitly leaves the stacked
composition "to be prepared separately". Pricing #200's certificate through
PR194's unchanged assembly against PR193's complex (`219037/312500000 =
7.009184e-4`) is exactly that deferred composition; the bootstrap then removes
the same slack below the coarse saving that it removed for PR189:

| depth | bit leaf | kappa | vs #197 | vs this package |
| --- | --- | --- | --- | --- |
| 0 (legacy atom wrapper, = #200's own "about 6.769e-4") | 6.77340866500955e-4 | 6768823/10000000000 = 6.768823e-4 | +0.1186% | +1.3521% |
| 1 | 6.77773606501196e-4 | 1354629/2000000000 = 6.773145e-4 | +0.1825% | +1.4168% |
| 2, 3 | 6.77773899999865e-4 | **1693287/2500000000 = 6.773148e-4** | **+0.1826%** | +1.4168% |

**This is the highest computed kappa in the queue**: +0.1826% over the standing
claim #197, and +0.0639% over the depth-0 row that #200 has announced but not yet
published. The depth-0 row is an independent cross-check of the harness: #200's
own announcement says the stacked composition "would give about 6.769e-4", and
this harness returns 6.768823e-4 from that supplier's certificate. The bit side
still binds at every depth (6.7777e-4 < 7.0092e-4).

**Pricing headroom is now exhausted.** For a fixed bit word the assembly caps
`kappa` at `C/(1+C)`; for #200's certificate `C = 6777739/10^10` gives
`C/(1+C) = 6.7731483368e-4`, and the depth-2/3 rows sit 3.4e-11 below it. So no
further pricing change can move this number: the only remaining levers reduce
`W` on #200's word. Both known ways to do that are new work on that graph, not
a recomposition:

* **endpoint-frame descent** — #198 did this on PR189's word and gained
  `+0.0090%` of coarse saving (`6.68298937775631e-4 -> 6.6835882709e-4`);
* **residual packing** — #197's mechanism is bound to PR187's word and was worth
  `+0.8403%` of coarse saving there (`6.70899981048852e-4 -> 6.76537710350481e-4`),
  the largest single bit-side gain in the queue (`+0.8398%` on kappa).

Because the bit branch binds, improving the complex side is worthless until the
bit coarse saving exceeds the complex's `7.009184e-4`.

Reproduce:

```bash
python3 -B research/bit-leaf-bootstrap-189/verify.py
```

which re-prices the vendored PR200 certificate, requires the result to beat #197,
and requires the depth-0 row to equal `6768823/10^10`.

Caveat, stated plainly: #200's bit word is that author's certified artifact,
vendored here and priced — not rebuilt or replayed. The wrapper is a *pricing*
change whose physical realization is PR185's construction, not one built here.

## Result claimed here: PR194's inputs

**kappa = 267141/400000000 = 6.6785250e-4**, against PR194's
1668581/2500000000 = 6.674324e-4 (+0.0629%). One thing changes in the record: the
ordinary leaf that prices the binding bit supplier. The complex supplier (PR193
as carried by PR194), the bit word (PR189), its terminal sinks, its reuse pairs,
the finite bridge and the 47-constraint balanced assembly are PR194's, unchanged.

| quantity | PR194 (record) | this composition |
| --- | --- | --- |
| complex saving | 7.009184e-4 | 7.009184e-4 (unchanged, PR193) |
| bit coarse saving `C` | 6.68298937775631e-4 | 6.68298937775631e-4 (unchanged, PR189) |
| bit ordinary leaf | 384599/10^10 = 3.84599e-5 (legacy) | 6.68298899999874e-4 (bootstrapped) |
| bit effective saving | 6.67878244234e-4 | 6.68298899999874e-4 |
| **kappa** | 1668581/2500000000 = 6.674324e-4 | **267141/400000000 = 6.6785250e-4** |

### Why it moves kappa

PR194's assembly sets `a = min(bit_effective, (1-1e-9)*complex_saving - 1e-10)`
and `kappa = a/(1+a)`; the bit side binds. PR184's `select()` prices that side as
`effective = (1-atom)*C + atom*OLD` with `OLD = 384599/10^10`, which holds the
effective value 4.207e-7 below `C`. PR185's finite acyclic wrapper

    a_{n+1} = (1-C)*C + C*a_n = C - C^n (C - a_0)

recovers it; three levels give `C` to within 1.3e-15. Details and per-depth rows:
[certificate.json](certificate.json).

### Searched and rejected

Both W-lowering levers on PR189's bit word are maximal
([bit-maximality.md](bit-maximality.md)): `word.py::row()` gives
`W = 2*v + (R - pairs)` at fixed rank deficit, and

* **terminal sinks: 34 of 34.** 474 per-root-admissible roots enumerated; the
  shipped 34 reproduce the frozen profile bit-for-bit and each of the 440 rank-23
  extras is rejected by the exact target chronology of `terminal.py::prove`;
* **donor reuse: 1760 of 3960 gauges.** All 2200 unpaired gauges carry rank-20
  entrance birth frames and no donor end frame among all 8628 is contained in
  any of them (`word.py::exact_frames` eligibility).

A frame-layout search on the same word was started and abandoned: re-choosing
operation frames only moves kappa when chain gaps are re-nested, and #198
published a deterministic endpoint-frame descent that does this properly (it
lowers W to `1670897/2500000000` coarse). The remaining big lever is the one
#197 used — residual packing, bound to PR187's word (`packing.py` +
`--bit-root`); carrying it onto #200's new bit graph is new work, not a
recomposition. Note that #198's own descent route and #200's stronger supplier
are *independent*: a descent on #200's word would start from the higher coarse
saving.

## Reproduce

```bash
python3 -B research/bit-leaf-bootstrap-189/verify.py
```

pins every input and package file by SHA-256 ([SOURCE.json](SOURCE.json)),
reproduces PR194's kappa exactly, re-checks 47 strict constraints and 7 margins
at every depth, re-prices the vendored PR200 supplier, and requires the result to
beat #197.

## Verification boundary

* Reproduced here: PR194's kappa from PR194's own profiles through its own
  `select()`/`assemble()`; the wrapper recurrence, its closed form and the strict
  tolls `a_0 < a_n < C < 1 - a_n`; 47 strict constraints and 7 margins per depth;
  the PR200 composition.
* Inherited pinned inputs, not replayed: PR168 v4 `fd25adb7`, and the
  #182/#184/#189/#193/#194/#200 packages. The wrapper's physical realization is
  PR185's claimed construction, not one built here; #200's bit word is its
  author's certified artifact, vendored and priced, not rebuilt.
* Conditional on #183's closed-form acceptance ceiling, #184's finite bridge, and
  the retained contracts of those inputs. Gains are small and live on the
  10^-10 selection grid.

## Stacking

Inputs are vendored byte-identical from the open PRs named above, so this package
runs on its own branch; the PRs' own changes are not claimed here. See
[NOTICE.md](NOTICE.md).
