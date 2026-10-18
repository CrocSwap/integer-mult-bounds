# Fully charged favourable relaxation for a k-call shared centre window

**Scoped planning result for the `centre-path-sharing` card (construction reading).
No shared centre is constructed or admitted, and no new kappa is claimed.**

The card asks whether the 64-per-call centre path (eight rank-8 COPY/ERASE totals
through the private temporary) can be shared across calls or shrunk, and its
construction method asks for a fully charged favourable relaxation for sharing
one centre path across k calls, including restoration, hosting and precision.
This package supplies that relaxation for the one sharing pattern whose contract
is pinned: the shared-sink return window of
[centre-shared-return-guard](../centre-shared-return-guard/README.md)
(PR1708 forward fanout / PR1748 reverse phase lineage), generalised from two
panels to k panels. The three named costs are charged explicitly instead of
being left as free overhead, and the ceiling is computed with
`ceiling.ceiling(centre=...)` from [complex-local-word-ceiling](../complex-local-word-ceiling/ceiling.py).

## Conversion contract

The pinned contract's literal backward centre-phase bill is 16 rank-8 returns,
368 ADDs and 32 CLEARs for two literal phases, and 8 rank-8 returns, 360 ADDs
and 16 CLEARs for the two-call fused window (its `RESULT.json` counts; the
k = 1 and k = 2 formulas below reproduce all six numbers exactly). One fused
k-call window gathers k panels before one ascent per centre and writes the
shared sink once. The conversion to the ceiling model's mass units is:

| Macro or obligation | Charge |
| --- | --- |
| One rank-8 COPY/ERASE total | one rank-8 child, 8 mass units (ascent and erase inside) |
| One ADD | one rank-1 child |
| One scratch CLEAR | one rank-1 child (restoration of the private temporary) |
| Hosting of shared rows across the window | 0 mass, idle-axis-hosting lemma |
| Precision: k summed panels | `ceil(log2 k)` magnitude bits on 8 shared totals, each bit one rank-1 unit per total per window |

Per call, a literal phase pays 8 rank-8 + 184 ADD + 8 scratch CLEAR; a fused
k-call window pays `8/k` rank-8, `176 + 8/k` ADD and `8/k` scratch CLEAR per
call. The k = 2 row matches levers.py's ideal lever "shared by two calls
(copies and charge halved)", and the charged profile exceeds it slightly because
the ADD and scratch-CLEAR savings are credited too.

Restoration is the scratch CLEAR set (charged) plus the contracted zero scratch
endpoint; scratch dirt is not promised to return to its incoming value. Hosting
is charged zero mass on the idle-axis-hosting lemma, on the contract's
constraints: the shared rows, panels and scratch must be untouched across the
window (no source or panel mutation, observation or required canonical
checkpoint may intervene). Precision is charged at the derived bit count
(`additional_magnitude_bits_sufficient = 1` for k = 2 in the pinned guard;
`ceil(log2 k)` for k panels by envelope summation).

## Results: changed centre charge, copy profile and charged ceiling

All values exact; ceilings are certified brackets at grid `1e-12`; ratios are
against the baseline ceiling `0.001690054109...`. `kappa` uses the retained
planning transfer `kappa < a/(1+a)`.

| k | centre | copy children (rank-8/call) | restoration (scratch CLEAR/call) | hosting | precision (rank-1/call) | rank-1/call | gross ceiling | fully charged ceiling | kappa cap | ratio |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 64 | 8 | 8 | 0 | 0 | 2412 | 0.001690054110 | 0.001690054110 | 0.001687202646 | 1.000 |
| 2 | 32 | 4 | 4 | 0 | 4 | 2408 | 0.003217794406 | 0.003215381840 | 0.003205076296 | 1.903 |
| 4 | 16 | 2 | 2 | 0 | 4 | 2404 | 0.003984054054 | 0.003981062728 | 0.003965276713 | 2.356 |
| 8 | 8 | 1 | 1 | 0 | 3 | 2401 | 0.004367783311 | 0.004365321517 | 0.004346348309 | 2.583 |
| 16 | 4 | 1/2 | 1/2 | 0 | 2 | 2399 | 0.004559798056 | 0.004558083777 | 0.004537401919 | 2.697 |

The k = 1 row is the selected word and reproduces the published baseline
ceiling exactly. The k = 2 fully charged ceiling is `a < 0.003215381840`,
`kappa < 0.003205076296`; charging restoration, hosting and precision moves the
gross ceiling by only 0.075 per cent. Rows k >= 4 use the derived k-panel
generalisation of the pinned two-panel contract, not a pinned construction.

## Break-even overhead at k = 2 (rank-1 children per call)

The named charges are not the binding constraint; how much *additional*
unmodelled overhead the window can absorb is. Two treatments, both sharp
(H passes the exact moment test at the threshold and H+1 fails):

| Treatment | keep full bit-limited gain (at T2) | at c_bit | any gain over selected |
| --- | ---: | ---: | ---: |
| overhead displaces idle mass (coverage identity kept) | 1650 (identity-feasible maximum) | 1650 (identity-feasible maximum) | 1650 (identity-feasible maximum) |
| overhead adds pure moment (predecessor treatment) | 31 | 31 | 32 |

Under the ceiling model's own accounting (extra children displace idle mass at
rank 51), consuming the *entire* idle remainder of 1650 rank-1 units per call
still leaves the ceiling above the complex-unbinding point
`T2 = 1733427039589844234749/(10^24 - 1)` and above the selected endpoint: the
break-even is capped by coverage-identity feasibility, not by cost. Under the
additive treatment of [centre-sharing-overhead-budget](../centre-sharing-overhead-budget/README.md)
(overhead as pure moment cost), at most 31 rank-1 children per call fit before
the full bit-limited gain is lost and 32 before any gain remains; their sharp
budgets on the identity profile are 4415/144 = 30.66 and 4591/144 = 31.88 per
call. The verifier recomputes both under its ideal-packing relaxation (30.98 and
32.19, ratios 1.010 and 1.010) and the residual difference is the ideal-packing
versus actual-histogram moment, not a shared term.

## Screen and what the relaxation decides

The card's first experiment screens the route on the levers.py scale: the ideal
shared-by-two ceiling ratio is 1.90 against the 1.10 stop threshold, so the
route survives the screen. The whole-bound gain is a different quantity: the bit
supplier binds at `c_bit = 0.001733427039589844234749`, so any mechanism whose
complex ceiling reaches that point gains at most the bit-limited
`kappa = 865213734911801/5*10^17 = 0.001730427469823602` (+3.4536 per cent over
the selected record). The fully charged k = 2 window clears that point with the
wide margins recorded above, so **for this pattern the cost side of sharing
(restoration, hosting, precision) is not the blocker**. The blockers are
eligibility and demand coupling, below.

## Scope and limits

- This is a favourable relaxation for one sharing pattern: a fused window whose
  k calls share sink rows, return operator and chart. It grants eligibility.
  [centre-shared-return-guard](../centre-shared-return-guard/README.md) supplies
  neither a full pair of fused local calls nor an eligible selected owner pair;
  [p112-batch-centre-floor](../p112-batch-centre-floor/README.md) proves that
  independent root-code demands cannot share at all (copied-pairing-rank bill
  `64k`), so the pattern needs genuinely coupled demands.
- The conversion contract (macro to rank-mass) is stated, not inherited: each
  scalar total pays one child at its pairing rank. Changing it changes the rows.
- Hosting is charged zero mass on the idle-axis-hosting lemma with its window
  constraints named; a window crossed by an observation or checkpoint cannot
  host, and then the per-use copy/erase returns (no saving).
- Precision is charged at the sufficient bit count for positive envelopes only.
  The pinned guard explicitly does not establish rounding-error, native guard,
  tape or global admission, and the fused primitives at width `mu+1` price at
  the invoice level (outside this mass model).
- The consumer and central readout are unchanged: the fused window writes the
  same endpoint rows as the separate phases (linearity of the shared-sink
  write), so the readout count is neither saved nor added.
- No new kappa, supplier admission or eligible pair is claimed; the selected
  record is unchanged. Fractional child counts are allowed by the relaxation,
  as in the incumbent ceiling model.

## Reproduce

Standard library only, from the repository root (Python 3.12):

```sh
python3 -I -B research/centre-shared-kcall-charged-seed615415/verify.py
python3 scripts/research_package.py --package research/centre-shared-kcall-charged-seed615415 --check-only
```

Expected first output: `PASS_CENTRE_SHARED_KCALL_CHARGED k2_charged_ceiling 0.003215381840 k2_ratio 1.902532 H_bit_displace 1650 H_bit_additive 31 H_any_additive 32 no_new_kappa`.
`verify.py --write` regenerates `RESULT.json`; the normal run requires the
committed file to equal the recomputation byte for byte. Controls (each enforced,
not advisory):

- the k = 1 and k = 2 conversion formulas reproduce the pinned separate bill
  (16/368/32) and fused bill (8/360/16) exactly, and the precision bit count
  matches the pinned guard;
- the k = 1 profile equals the selected word and reproduces the published
  baseline ceiling to the grid;
- one extra rank-1 child lowers the k = 2 charged ceiling, and a doubled
  precision charge lowers it again;
- every break-even is sharp, or explicitly capped by identity feasibility;
- the additive identity-profile budgets stay within a factor of two of
  centre-sharing-overhead-budget (measured 1.010 and 1.010).

## Open next questions

- **Is any selected call pair eligible for a fused window?** Trace one candidate
  pair through the selected owner map and call schedule: shared post-A sink
  rows, identical return operator and chart, and an uninterrupted window with no
  intervening observation or checkpoint. *Why it matters:* the relaxation shows
  cost is not the blocker for this pattern; eligibility is. *First step:*
  extract the backward centre-phase invocations of two calls that share sink
  rows from the selected replay schedule. *Blocked by:* the owner map and
  schedule are not in this package; the guard leaves this open explicitly.
- **Which selected call pairs have coupled rather than independent demands?**
  *Why it matters:* the `64k` copied-pairing-rank floor of p112-batch-centre-floor
  blocks sharing for independent root-code demands; only coupled (shared-sink)
  demands can use this pattern. *First step:* classify the 144 calls of the
  selected record by shared sink rows and return operator. *Blocked by:* a
  machine-readable demand-coupling table for the selected record.
- **Does the fused primitive tariff fit the scalar guard?** The guard prices
  fused primitives at `mu+1`; centre-sharing-overhead-budget leaves about
  654,144 extra macros per call of primitive headroom, and the fused window adds
  none (it removes 32 macros per two calls). *Why it matters:* it would close
  the invoice-level obligation the mass model cannot see. *First step:*
  instantiate the two-panel fused bill under the selected invoice formulas.
  *Blocked by:* the actual tariffs and precision headroom are uninstantiated.

## Credit

The sharing constructions are 1337isnot1337's PR1708 (forward fanout) and
ToikY's PR1748 (reverse phase). The pinned two-panel contract, its exact bill
and its one-magnitude-bit precision guard are ToikY's
[centre-shared-return-guard](../centre-shared-return-guard/README.md); its
`RESULT.json` counts are used unchanged as a pinned input. The packing-ceiling
model, the lever table and the coverage identity are Douglas Colkitt's
[complex-local-word-ceiling](../complex-local-word-ceiling/README.md) and
PR1012. The additive overhead budgets and the bit endpoint are
[centre-sharing-overhead-budget](../centre-sharing-overhead-budget/README.md)
(prepared for rtyu193-rgb). The hosting lemma is
[idle-axis-hosting](../idle-axis-hosting/PROOF.md). The `64k` floor for
independent demands is [p112-batch-centre-floor](../p112-batch-centre-floor/README.md).
Prepared by Aaron Wang with help from opencode (substantial AI assistance; no
model named; no independent human review claimed). Apache-2.0.
