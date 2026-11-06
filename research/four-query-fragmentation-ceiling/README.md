# Four-query fragments: exact attainment and complete grammar ceiling

Jerry Chen / @CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.

**No new κ.** This package closes the equal-orientation four-query question
left open in `research/binary-full-bank-retirement` (#6764). An exact word
exists, and its two retired auxiliary inputs can produce a positive local
gain at extreme asymmetry. Nevertheless, any mixture of these words with
the ordinary binary words cannot improve the retained #6726 complete
construction over the stated parameter ranges.

## Precise results

1. Over `Z[S,L,R]/(S^2-1)`, a 13-operation word sends six arbitrary independent
   inputs to `LR(X+SY), LR Y, SL A, SL B, R E, R F`. It uses two atomic native
   children, two additional thin queries, four paid body idles and five
   integer ordinary gates. Its source-normalized complex expansion has
   21 events, followed by two ordinary auxiliary target normalizers
   (23 events including those normalizers). It attains the four-query lower bound **under the precise
   positive-body, atomic-support hypotheses of #6764**.
2. For `H(r)=r^(1-κ)` and `i(n)=H(sn+1)-H(sn)`, the complete new-node excess
   is `2i(a)-2`; the local change is `2[i(a)-i(a+b)]-1`. Both fresh targets
   and their paid idles are counted before cancellation. Exact positive
   controls retain a local gain at `F=2^400`.
3. Fix the native leaves and formal six-child root of #6726. Every positive
   six-child allocation and every mixture of ordinary/four-query binary
   trees obey the following raw upper ceilings:

| Source | Raw ceiling | Uniform interval audited |
|---|---:|---|
| Complex | 0.0033072446849 | κ in [0.0033, 0.004] |
| BIT | 0.0037667234776 | κ in [0.0037, 0.004] |

The finite maximum occurs at 18 leaves for each source. Every replacement
loses below 50 leaves, while a concave bound excludes every size at least
50, including the regime where a replacement can pay locally. These are
source-relative raw ceilings, not new feasible or admitted values. The
qualified values proposed in #6726 remain 0.00330720 and 0.00376669;
canonical selected κ remains 0.003125804 at the pinned base.

## Proof and evidence

- [CONSTRUCTION.md](CONSTRUCTION.md): exact word, arbitrary-input proof,
  source `q^4=1` phases and full local invoice.
- [ECONOMICS.md](ECONOMICS.md): complete root formula, mixed-tree envelope,
  finite dominance and all-size tail proof.
- [CONSTRUCTION-REVIEW.md](CONSTRUCTION-REVIEW.md): separate hand derivation,
  reverse-oracle inspection and exact application of the inherited lower bound.
- [INTERFACE-REVIEW.md](INTERFACE-REVIEW.md): independent target-type and
  source-wrapper compatibility check; fresh plain-R outputs skip the old
  blanket auxiliary normalizer.
- [ECONOMIC-REVIEW.md](ECONOMIC-REVIEW.md): independent proof review and
  six Decimal-85 numerical corroborations. The rational enclosures remain
  the exact sign certificates.
- `construct.py` checks all 36 formal coefficients and separately represented
  Gaussian rational source coefficients. `reverse_check.py` uses reverse
  output-functionals, a different implementation and a separately derived
  plane word. The wrapper binds the literal gate lists.
- `economics.py` independently reconstructs native tariffs, the root's
  symbolic six-child signature and both complete target/paid histograms.
  It reuses only the byte-pinned rational power-enclosure engine.

## Reproduce

From repository root, using Python 3.12 and the standard library:

```bash
python3 -B scripts/research_package.py --package research/four-query-fragmentation-ceiling
```

Expected package marker: `PASS_FOUR_QUERY_FRAGMENTATION_CEILING`; expected
registered-run marker: `PASS_REGISTERED_RESEARCH_PACKAGE`. The direct command is
`python3 -I -B research/four-query-fragmentation-ceiling/verify.py`.
Normal and optimized Python produce identical receipts. Default replay
does not write files. Explicit `economics.py --write` regenerates its receipt.

Negative controls reject all 13 literal-gate omissions, all eight source
phase reversals, eight independently implemented reverse/invoice mutations,
and three economic invoice omissions. A scope control confirms that making
the extra thin query free would invalidate the economic envelope. Details
and exact pins are in `VALIDATION.json`, `SOURCES.json`, `PINS.json` and
`ORIGINS.json`.

## Scope and inherited obligations

This is a formal atomic-supplier construction and a complete scalar cost
obstruction for a fixed recursive grammar. The economic upper bound grants
ordinary work for free, so additional physical routing costs cannot turn its
negative margins positive. It is not a new native physical circuit or a
complete compiler, ownership, precision-tape or analytic-recovery result.
The five inherited assumptions remain `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, and `analytic_recovery`.

The three-query lower bound is inherited, with its hypotheses, from the
retained `frozen/THREE-QUERY-OBSTRUCTION.md` at #6764. The present replay proves
four-query attainment, not an unrestricted optimality theorem. Complex
source-opcode phases are checked; the BIT economic result grants the same
formal node without claiming a separately compiled BIT realization.
Changed native leaves, changed root signatures, packed-query discounts,
shared billed jobs and nonlocal coupled retirements are outside this claim.

## Provenance and credit

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Source #6726: `435bbe91fb28cb1d7a569ca70c6c4e9eb302d486`.
Prior #6764: `1153341fb288bd4cd3c9eba490b6dec4e2e6d43c`.

The source lineage includes Cinna Davis and Ali Romman's native/caller work,
#6348 and #6398, thu-nmrc's root in #6716, and zxv's complete paid-fragment
construction, allocation tail and rational interval implementation in
#6726. Predecessor notices and licenses are retained under `frozen/`.
This combines a new literal construction with an independently developed
complete budget argument and separate reverse verification. AI assistance
is substantial; these are author-side checks, not human acceptance or
formal-kernel verification.

## Open next questions

- Can a changed root or coupled retirement system alter the complete
  envelope? Specify independent productive targets and every paid job
  before extending the search; this proof fixes the six-child root.
- Can physically justified query sharing reduce the extra unit charge?
  The free-query control shows why this could matter, but no such
  implementation or discount is established here.
- Can a new native leaf improve the complete signed native moment enough
  to reopen this grammar? A local improvement must be reassembled with
  the exact root and all inherited costs.
