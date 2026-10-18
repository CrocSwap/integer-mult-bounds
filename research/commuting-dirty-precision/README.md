# Smaller sufficient precision for the commuting dirty word

**Conditional precision audit; no new kappa.** This applies PR1278's commuting
interval lemma and PR1085's sharp prefix count to PR1054's actual
target-dependent rounded leaf contract. Both standalone word directions are
covered, including the positive preimage visited inside a negative leaf.

For n factors, put h=ceil(log2 n), C=h+2, and suppose every subset product
has norm at most G>=1. The prefix bound is B=CG and the interval bound is
L=C²G. For N paid leaves with source-only error bound `a u (X+1)`, initial
array bound D and grid unit u, the sufficient execution error becomes

    2 N L a u (B D+1),        provided N L a u <= 1/2.

This removes one factor G from generic two-prefix transport. The rounded
increment may still depend on the incoming target: its error bound applies
uniformly at the positive preimage. The internal reserve retains beta^-8,
including the inverse-preimage factor. [PROOF.md](PROOF.md) gives the complete
all-size substitution, explicit integer formulas, and unchanged cost bill.

For PR1054's prime-power preparation contract, the convenient coarse envelope
improves from `max(p,w_input)+m+18r³` to `max(p,w_input)+m+15r³` fractional
bits. It remains cubic and sufficient, not an optimum. Explicit formulas
are considerably tighter than this coarse envelope.

At p=128, m=20 and w_input=0:

| Radix | PR1054 fractional bits | New fractional bits | PR1054 signed integer bits | New signed integer bits | Paid leaves |
|---:|---:|---:|---:|---:|---:|
| 8 | 2,921 | 2,418 | 2,556 | 2,552 | 52 |
| 16 | 21,768 | 17,838 | 19,701 | 19,695 | 232 |
| 32 | 175,583 | 143,690 | 159,558 | 159,550 | 976 |
| 64 | 1,420,902 | **1,162,598** | 1,291,719 | **1,291,709** | 4,000 |

At radix 64 this saves 258,304 fractional bits. The six borrowed arrays,
516,499 factor-preparation bits and complete leaf/routing word are unchanged.
The radix-64 row is an exact budget comparison, **not an execution at those
million-bit widths**. PR1085's 1,162,523-bit example concerns PR905's different
leaf contract; the similar figures are not interchangeable.

## Reproduce and evidence

Python 3.12, standard library only, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/commuting-dirty-precision
```

Expected: `PASS_COMMUTING_DIRTY_PRECISION`, six passing package tests,
`PASS_COMMUTING_DIRTY_PRECISION_PACKAGE`, then `PASS_REGISTERED_RESEARCH_PACKAGE`.
The standalone `python3 -I -O -B research/commuting-dirty-precision/test_package.py`
also works from a source export with this complete package.

The exact deterministic [certificate](CERTIFICATE.json) contains:

- 5,220 uniform prime-power budget certificates through radix 512, independently
  recounted phi/leaf counts and checked integer exponent inequalities; 216
  generic rational budget checks, including incoming-grid domination.
- Literal PR1054/PR628 recursive dispatcher comparisons in both signs at every
  n=1..33 and n=63,64,65,127,128,129. The numerical leaf body is instrumented;
  split, signs, wiring and scratch reuse come from the pinned source AST.
- 20 stable rational factor fixtures at n=2,3,4,7,8; two cyclic geometries and
  two shared unit gauges. All 80 signed rounded words are actually executed,
  with odd lowest input bits, a finite-geometric ideal oracle, exact source
  and scratch restoration, complete positive/negative inverse cancellation,
  literal data-access counts and full internal/routing bounds.
- Each fixture's forward paid-operation census also matches the old finer-grid
  execution on the same incoming data. This compares every counted read,
  write, product, powering product, division, node, leaf and tape move; it does
  not equate rounded numerical answers on different grids.
- Eight mathematical/admission controls, including PR1244's seven-factor
  noncommuting interval obstruction (the latter is
  a credited inherited witness, not a new counterexample). The rounded tests
  additionally demonstrate actual target dependence. Five actual package
  corruptions fail, including missing proof, source/receipt drift, a deleted
  interval G and a deleted inverse-preimage guard. Relocated read-only inputs
  replay with isolated optimized Python.

The direct oracle and budget checker are separate implementations. They are
AI-assisted and are not independent human reviews. Written predecessor lemmas
supply the quantified all-size proof; these finite checks support the source
binding and arithmetic. [VALIDATION.json](VALIDATION.json) records performed
and omitted checks. No selected supplier cold replay or hosted CI is claimed.

## Pins, overlap and scope

Base: `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`. OS seed **64**, adversarial
audit under the original user track mapping. [TASK.json](TASK.json) records
scope and stopping rule. The initial three candidates were a sharp interval
coefficient bound, this rounded-contract substitution, and sign-asymmetric
connector prices. This chosen task is explicitly left open by PR1278.
The [claim and result discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/1283)
records its narrow boundary.

Pinned pending predecessors:

| PR | Contributor | Exact head | Retained obligation |
|---|---|---|---|
| [#1054](https://github.com/CrocSwap/integer-mult-bounds/pull/1054) | Ali Romman | `6bc675be1554b3a3be771147f21f9dc2c6dae50a` | Rounded word, admission, nonlinear leaf error, inverse preimage, preparation and complete cost |
| [#1085](https://github.com/CrocSwap/integer-mult-bounds/pull/1085) | Hanson Sun | `82b99c7d12dac009d35636562df4c6c91e885409` | Sharp C=h+2 prefix coefficient lemma |
| [#1278](https://github.com/CrocSwap/integer-mult-bounds/pull/1278) | Charles Bethin | `06b8c006891ae78abe24b30d2fe9d8c188deafe8` | All-size squarefree interval lemma with shared deeper scratch |

These are dependency pins, not a claim of maintainer acceptance. Each consumed
source byte is recorded in [VENDOR-PINS.json](VENDOR-PINS.json). The small
vendored subset serves this audit's proof and actual executions; frozen
predecessor packages are not modified. Existing generic precision bounds stay
valid. PR1244's noncommuting obstruction and PR1135's nonadditive borrowing
obstruction are not removed. We retain the original reserved-depth allocation.
Concurrent [PR1294](https://github.com/CrocSwap/integer-mult-bounds/pull/1294)
by Philipp / mightyOil (`03025ca1d51091a9525203000e77dacccfa6a70d`) supplies
universal local algebra certificates for PR1278. That is complementary; no
PR1294 implementation or stronger local-hypothesis claim is consumed here.

Only this package is added. The selected PR1094 record, upstream sources,
source-access/restoration charges, paid rank profiles and all-size/compiler,
physical hosting, fast scalar arithmetic, supplied factorizer and analytic
interfaces remain unchanged. No new supplier, optimal precision, measured
speedup, full transform, or multiplication theorem is asserted.

## Open next questions

A sharp two-cut coefficient recurrence could improve the remaining logarithmic
constant. Start from PR1278's six phase cases; an all-size proof is needed,
not merely more finite maxima. This audit deliberately uses C².

To use this at a complete supplier caller, bind one caller and regenerate its
native/physical invoice with the smaller width. Preparation, source routing,
compiler and analytic interfaces are the blockers. A local sufficient width
does not itself change the selected moment. Structured next steps are in TASK.json.

Prepared for **Philipp (@mightyOil)** with substantial **OpenAI Codex / GPT-6
Astra assistance** in mathematics, code, verification and writing. Apache-2.0.
Credit PR1054/985/621 (Ali Romman), PR1085/1244 (Hanson Sun), PR1278 (Charles
Bethin), PR628/862/905 (Chafik Boukhalfa), PR877 (Gareth Davidson), PR663
(0xkilgore), and the retained lineage. [NOTICE.md](NOTICE.md) preserves scope.
