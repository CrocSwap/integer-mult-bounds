# p104-certkit-pricekit-to-lean: PRICEKIT's exact κ of a word, turned into a Lean kernel certificate

**What it does.** `tools/certkit.py` takes a P104 word file priced under the #7113 caller, computes its invoice and κ
with PRICEKIT (`tools/pricekit.py`, exact rational invoice, κ by Decimal bisection), picks rationals lo < κ < hi
that share κ's first 10 significant digits, and emits Lean modules whose kernel check proves, for the word file itself:

```
Cert<N>.certified : Legal (pub caller7113) tr ∧ Rows ∧ Word caller7113 (exec tr) ∧ lo ≤ kword ∧ kword ≤ hi
```

with no hypotheses. Here `tr` is the kernel-replayed trace of the word file, `Rows` says its final rows are the #7113
target rows (packed reverse-mode row certificate over all 1501 public registers), and
`kword = sSup {κ ∈ [0,1) | ValidAt κ}`, where `ValidAt κ` is the word's Valid inequality on that trace:
caller(1−κ) + 17 · (MOVE prices at 1−κ) ≤ caller targets(1−κ) + 17 · (helper climbs at 1−κ).
`kword_root`, `valid_below` (Valid for κ ≤ lo) and `invalid_above` (not Valid for hi ≤ κ < 1) come with it.

**Results.** Every name in `lean/Check.lean` (34) has axioms within `[propext, Classical.choice, Quot.sound]`
(`CHECK-axioms.txt`). No `sorry`, `native_decide`, `axiom` or `extern`; finite facts use `decide +kernel`. No κ claim.

| word | PRICEKIT κ (#7113 caller) | Lean bracket [lo, hi] | headline |
|---|---|---|---|
| t7669 (#7669's word, replayed) | .00372142604386357… | [.00372142604386, .00372142604387] | `CertT7669.certified` (+ `UniUniversal.Crossing .w7113 lo`) |
| w_s4 (own test word) | .00366673434589504… | [.00366673434589, .00366673434590] | `CertWs4.certified` |

The two words differ in shape (t7669: 152,023 trace events in 96-bit slots; w_s4: 210,240 events in 128-bit slots with
25-bit coefficients), so the gate is PRICEKIT vs Lean agreeing to 10 significant digits on two independent words.

**Pieces.**
- Generic core `CertKit.kroot_bracket` (`Nov15/CertKitCore.lean`): for ANY invoice cs (pairs (c, r), r ≥ 1),
  F cs t = Σ c · r^(1−t); positivity on [0, lo] and negativity on [hi, ∞) give lo ≤ kroot cs ≤ hi,
  F (kroot cs) = 0 and every root of F on [0, ∞) in (lo, hi). The piece checks use certified enclosures of log m
  (telescoped series) and exp (Taylor bound with halving), dyadic rounding at 2^−128, chained by `decide +kernel`.
  `Cert<N>Num.bracket` is this for the word's PRICEKIT invoice; this part works for any PRICEKIT invoice.
- Link `Cert<N>.FW_eq`: the replayed trace's own invoice (MOVE |Δdim| histogram via `fold_paid`, helper-climb
  histogram) equals F cs, so `kword = kroot cs`.
- Caller (`CertCaller7113*`, made by `tools/callerfacts.py`): the caller block's T/P histograms and the call count
  (17) are derived in the kernel from the caller file's events; `CertCaller7113Link.kwordT_bracket` /
  `kwordW_bracket` restate both brackets with the caller sums taken over the raw caller items.

## Usage
Check this package (Python 3, standard library):
```
python3 -I -B verify.py     # CI command, about 30 s, no Lean
./verify.sh                 # verify.py + tools/regen.py + lean/check.sh (Lean build and axiom audit)
```
For Lean: `cd lean && lake exe cache get` (Mathlib rev pinned in `lakefile.toml` / `lake-manifest.json`, toolchain
v4.33.0-rc1). The 340 largest generated data modules (68 MB of event chunks, row checkpoints and segments) are not
stored; `tools/regen.py` rebuilds them from `data/` byte-identical to the sha256 pins in `REGEN.json` (about 80 s for
t7669, 330 s for w_s4). `lean/check.sh` then builds `build-order.txt` one file at a time with an RSS guard and runs
`#print axioms` on `Check.lean`.

Certify another word (same shape, see Scope), one command after the chain generator:
```
python3 tools/gen_chain.py WORD.json.gz TAG          # kernel-replayable trace modules UniInhabit<TAG>*
python3 tools/certkit.py WORD.json.gz --name N --chain TAG --rows gen --build
```
This prices the word, writes `Cert<N>Tab/Part*/Num`, `Cert<N>`, the row certificate `UniRows<TAG>A*` and
`Cert<N>Rows` (headline `Cert<N>.certified`) into `lean/Nov15/`, and builds them through `lean/tools/runlean.sh`.
Without `--chain`, only the invoice bracket `Cert<N>Num.bracket` is emitted. Generated Lean headers keep the tool
paths of the authors' tree (`toolkit/certkit/…`, `Nov15/unigen/…`); here those tools are `tools/` and `tools/unigen/`.

**Measured (one core, Apple M3 Pro).** PRICEKIT and the Python certificate: about 7 s per word (67–68 pieces on each
side). Bracket + link modules: 100–125 s per word, peak ≤ 3.0 GB. t7669 headline with its existing rows: 111 s.
w_s4 rows chain (85 segments, 128-bit): about 41 min, peak 3.27 GB. Caller modules: about 40 s. Loading the whole
closure for `Check.lean`: 29 s, peak 3.34 GB. A clean build of the full 703-module closure was not timed as one run.

## What `verify.py` checks
File pins (`MANIFEST.sha256`); `REGEN.json` is exactly the closure minus the stored modules; token bans outside
comments; `build-order.txt` is topological and equals the `All.lean` import closure (regenerated modules through their
pinned imports); every `Check.lean` name is declared; both headline statements are hypothesis-free with the stated
conclusion; `CHECK-axioms.txt` within the three standard axioms; toolchain and Mathlib pins. Python side: PRICEKIT
reprices both words, the bracket is re-chosen and the piece certificate re-checked exactly, and
`Cert<N>Tab/Part*/Num` and `Cert<N>` are regenerated byte-identical to the stored files; the caller modules are
regenerated from `data/7113_CALLER.json`.

## Scope and caveats
- Words: the trace template is the #7113 caller's word shape: 1501 public registers, 104 ports with the same D-port
  layout (1101 helpers), 68 owned fields, MOVE ranks < 10. Another caller needs its own link template; the invoice
  bracket alone works for any PRICEKIT invoice.
- What `kword` is: the sup of κ ∈ [0,1) at which the trace's Valid inequality holds, for the concrete trace that the
  word file encodes (`tools/regen.py` rebuilds the replayed data from the word file). MOVEs pay `paid[|dim new − dim
  old|]` whether or not they are owned (the repo verifier's rule); owned MOVEs (46 in t7669, 47 in w_s4) are priced so.
- Caller: the caller histograms are derived in Lean from the caller items; what remains outside the kernel is the
  Python JSON-to-Nat encoding (round-trip checked) and the pricing rules themselves (the repo's caller invoice rules with
  #7113's IDLE_ODD), which are taken as given, not derived from SPEC.
- `Legal` is the trace model's legality (replay, ownership nesting, frames). It does not restrict the coefficient
  alphabet: t7669 keeps #7669's odd-denominator coefficients.
- w_s4 has one COPY (into a register just INIT'd to 0); the trace encodes it as SCALE 0 then ADD. COPY, ADD and SCALE
  are not invoiced, so this does not move κ.
- `UniUniversal.Crossing .w7113 lo` is proved for t7669 only (its fold D/R tables exist); w_s4 has the bracket headline.
- The closure includes, unchanged, the earlier P104 Lean library that the crossing statements import (decoder-wall,
  banked-banner and `UniUniversal` modules, as in #7796); it is shipped for self-containment.

## Open next questions
- Another caller: the word-level link is written for the #7113 caller (17 calls, its port layout). First step: run
  `tools/callerfacts.py` on the other caller file and swap the derived constants into the link template.
- `Crossing .w7113 lo` for w_s4 (and for any new word): needs the fold D/R tables that `UniWordChain` builds for t7669 only.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
