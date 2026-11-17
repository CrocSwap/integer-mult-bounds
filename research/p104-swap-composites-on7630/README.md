# CONDITIONAL κ = 0.0036807241001: 22 swap-then-delete composites on #7630 (premises: the same as #7630's)

**κ = 0.0036807241001472786206795589800541716634…, ×1.00368972 over
[#7633](https://github.com/CrocSwap/integer-mult-bounds/pull/7633)** (κ ≥ 0.003667193194322). The base word is our
[#7630](https://github.com/CrocSwap/integer-mult-bounds/pull/7630) (κ 0.0036667343458950…). The official `evaluate_recursive_power`
bracket (256 bits) is [0.0036807241001, 0.0036807241002]. The claim 0.0036807241001 is below the exact crossing.

> **Premises: conditional on the same framework assumptions as #7630.** Those are exactly #7620's premises: its five framework
> assumptions (`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`) and its fixed allocation
> of 17·68 = 1,156 owned banks, with its CLEAR reading over the same **180 CLEARs**. This word adds no owned lifetime and no new kind
> of event: the owned INIT/CLEAR/MOVE sequence is #7630's. The CLEAR *contents* change (151 of 180), because the hub content they
> snapshot is re-derived, so each of the 180 CLEARs carries its own exact certificate under #7620's `verify_certificates` rule
> (`data/clear-certificates.json`). If #7620's premises are refused, this word is void with #7620, #7621, #7623 and #7630.

## The edits

Base: #7630's word (`data/base-7630-word.json.gz`, 208,738 events). New word: `data/word.json.gz`, 202,668 events. Every edit is listed
in base-word coordinates in [data/edits.json](data/edits.json): 22 composites C1–C22 on 44 helpers (521 interior deletions, 444 insertions),
then the re-derived hubs.

Each composite is two steps at one chart c:
1. **A SWAP-NULL relabel** of two helpers h1, h2 that are both born at {0} and both end at V. Exchanging their row trajectories after c is
   undone exactly by the hubs (the {0} prefix and the V mix), so on its own it changes no final row and no price. This is the swap law of
   our Lean package [#7634](https://github.com/CrocSwap/integer-mult-bounds/pull/7634) (`SwapNull`).
2. **Deletion of the recombined stay** at c. After the relabel, the two stays at c have new neighbours, and one of them is no longer needed.

Example C1 (helpers 396 and 564, swap chart 457): routes `396: 3→90→448→457→965→149→127`, `564: 3→457→895→127` become
`396: 3→90→448→457→895→127`, `564: 3→965→149→127`. Helper 564's stop at 457 disappears.

**Why the deletion is legal (the blank hand-off).** In every composite the receiver b is {0}-born and still *blank* when it reaches c
(its row is e_b plus {0}-chart content only). A co-resident register a either hands its content to b there (`b += a`) and then only
collects on its way to V, or has already spent its content and idles to V. Deleting b's stop without the relabel fails, because b's stop
carries that content flow. After the relabel, a carries its own content along b's old tail, and b, still blank, takes a's collector tail
straight from {0}: the copy `b += a` becomes a rename, and b's stop at c disappears. All 22 hits sit at charts of dimension 1–3.

**Joint hub re-settle.** As in #7630, every ADD/SCALE at the {0} chart and at V is then solved jointly and exactly so that all 1,569
final rows and end charts equal #7630's.

## Price

Native paid delta per call {2:−18, 3:−6, 4:−20, 6:+20, 7:+2}; helper targets unchanged. Over 17 calls: paid
{2:−306, 3:−102, 4:−340, 6:+340, 7:+34}. Paid positions 110,026 → 109,652; rank surplus S = 1,424 unchanged.
Ordinary bill (17 calls, the repository `independent.py` formula with its call count set to 17): 867,014,040 for #7630 → 859,783,396
for this word, below 10^9. Coefficients stay 5-smooth. The replayed grid moves from #7630's (2-adic exponent 20, odd lcm 675, 34 numerator
bits) to (16, 54,675, 29): the odd lcm grows. Non-dyadic literal events go from 12,312 to 11,737.
Official tools (`price.py`):
- `compare_recursive_invoices` against #7630 gives `uniformly_better`.
- `evaluate_recursive_power` (256 bits) gives `new_cost_lower` at C = 0.0036807241001 and `new_cost_higher` at C = 0.0036807241002.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-swap-composites-on7630
```
`VERIFY.json` registers eight commands:
- `core`: words, interior edit list, exact replay and legality of both words, rows, end charts and owned data, routes, coefficients,
  invoice and κ.
- `certificates`: all 180 CLEAR certificates, with 2 rejecting controls.
- `controls`: 14 rejecting controls and 2 accepting.
- `columns1` to `columns4`: the affected-pair column tests, in four parts.
- `price.py`.

**Affected pairs.** #7630's census is 981 pairs. The 44 changed helpers add 42 route pairs not already counted, so the census becomes
**1,023 pairs**, with none dropped. `check.py` runs 512 forward and 512 adjoint Gaussian columns, signed Pauli action, absolute phase,
exact ascent rank and a wrong-phase rejection on all of them.

Independently of the package, the word passed our exact pricer, an independent exact Fraction replay (all 1,569 rows equal #7630's,
no chart, ascent or ownership violation), a replay modulo 2^89−1 and 2^107−1, the repository's `independent.py` native audit
(bad_inputs 0) and caller identity (bad_outputs [], 17 native calls), and an interval gate on the κ bracket.

## Conditional premises and what is not rerun

The claim carries exactly #7630's premises (above), over the same 180 CLEARs with new, individually certified contents, and the signed
#7113 caller and BIT premise of the base. This package does not rerun #7620's full native/signed 17-stage application, catalogue, outer
predicates or precision/tape counts. No upstream maintainer has reviewed the package.

## Credit

The base is our [#7630](https://github.com/CrocSwap/integer-mult-bounds/pull/7630) on #7623 and #7621, which use SYLforge's loan +
stationary-snapshot device ([#7616](https://github.com/CrocSwap/integer-mult-bounds/pull/7616),
[#7620](https://github.com/CrocSwap/integer-mult-bounds/pull/7620)). Signed caller: rohanarun's #7113. See [NOTICE](NOTICE).
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Open next questions

- **More composites.** Only pure deletions after a single relabel were screened, and 35 further single hits conflict in the joint stack.
  Making non-blank receivers blank first (with a κ-null gauge) is untested.
- **The premises.** A ruling on #7620's inherited assumptions and its CLEAR reading decides #7620, #7621, #7623, #7630 and this word together.
