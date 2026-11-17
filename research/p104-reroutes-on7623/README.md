# CONDITIONAL κ = 0.0036667343458: seven stop edits and a joint hub re-settle on #7623 (premises: the same as #7623's)

**κ = 0.00366673434589504230429298346749029694192150…, ×1.00118271 (+0.118271%) over our
[#7623](https://github.com/CrocSwap/integer-mult-bounds/pull/7623)** (κ 0.0036624027915539817894…), and ×1.00027363 over
[#7627](https://github.com/CrocSwap/integer-mult-bounds/pull/7627) (κ ≥ 0.003665731276). The official `evaluate_recursive_power`
bracket (256 bits) is [0.0036667343458, 0.0036667343459]. The claim 0.0036667343458 is below the exact crossing 0.00366673434589504.

> **Premises: conditional on the same framework assumptions as #7623.** Those are exactly #7620's premises: its five framework
> assumptions (`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`) and its fixed allocation
> of 17·68 = 1,156 owned banks, with its CLEAR reading over #7623's **180 CLEARs**. This word adds no owned lifetime and no new kind
> of event. The 180 owned lifetimes (field, INIT chart, CLEAR chart), the 47 owned MOVEs, peak 50 and 68 labels are #7623's. The
> CLEAR *contents* do change (156 of 180), because the hub content they snapshot is re-derived. Each of the 180 CLEARs therefore carries its
> own exact certificate under #7620's `verify_certificates` rule (`data/clear-certificates.json`). If #7620's premises are refused,
> this word is void with #7620, #7621 and #7623.

## The edits

Base: #7623's word (`data/base-7623-word.json.gz`, 77,277 events). New word: `data/word.json.gz`, 208,738 events. Every edit is listed
in base-word coordinates in [data/edits.json](data/edits.json). That covers 23 deletions and 12 insertions on the interior events (every
MOVE/INIT/CLEAR, and every ADD/COPY/SCALE at a chart of dimension 1..8), plus `initial` for the two rebirths. Then come the re-derived hubs.

| id | register | kind | route #7623 → new | new ops |
|---|---|---|---|---|
| E1 | helper 457 | rebirth + swap canceller (TR1) | 3→281→966→218→127 ⇒ born at 281 | `242 += -1*457` @281 |
| E2 | helper 461 | rebirth + swap canceller (TR1) | 3→285→994→201→127 ⇒ born at 285 | `10 += -1*461` @285 |
| E3 | helper 382 | re-route at an existing co-presence | drops 24: 3→849→… | `553 += 1/2*383` @24 (replaces 4 ops) |
| E4 | helper 490 | re-route at an existing co-presence | drops 725: 594→883→… | `1427 += -1*296` @725 (replaces `490 += 296`) |
| E5 | X main 44 | re-route at an existing co-presence | drops 849: 495→127 | `382 += -1*816` @849 (replaces `382 += 44`) |
| E6 | Y main 176 | re-route (twin pickup) | drops 1065: 449→928 | `176 += -1/4*1000`, `176 += -1*236` @928 (replace `176 += -1/2*379` @1065) |
| E7 | Y2 main 902 | stop deletion, no new op | drops 595: 3→618 | none (4 donor deliveries deleted) |
| hub | {0} chart and V | joint exact re-settle | n/a | every ADD/SCALE at dim 0 and dim 9 re-derived |

**Why each kind is legal.**
- **TR1 swap canceller (E1, E2).** Helpers 457 and 461 were born at {0} and moved straight to their dim-3 first chart. Each is now
  born at that chart; its first MOVE is deleted. While its row is still exactly e_h, one canceller op `j += -1*h` runs at that chart,
  between registers that are both there. That is TR1's depth-1 swap: the token e_h now leaves on j. j = 242 is a {0}-born helper that
  ends at V, and j = 10 is a kept X main. Its content is settled by the V mix, so no paid stay carries the token. Each helper's target
  rank goes 9 → 6.
- **Re-route at an existing co-presence (E3–E6).** The register drops one interior stop with all its ops there, and its two MOVEs merge
  into one strictly ascending MOVE. The content the stop delivered is re-made by one or two new ADDs between registers that already
  share that chart at that moment in #7623's schedule. Each new op's legality is a chart check in the exact replay. For E5 the receiver
  382 ends at V, so the extra X content stays inside the V span and is absorbed by the V mix, and the {0} part by the {0} prefix. For E6
  the X content delivered to 176 is identical; the difference is {0} content plus two Y2 entries absorbed downstream.
- **Deletion with the hub re-settle (E7).** Main 902's stop at 595 is donor-only (it delivers to owned 1532 and to helpers 1479, 1255
  and 1495, which end at V). The four deliveries are deleted with no replacement. A positive control shows that the bare deletion
  on #7623 already leaves every final row unchanged, because the deliveries cancel downstream.
- **Joint hub re-settle.** Every ADD/SCALE at the {0} chart (the prefix among helpers born at {0}) and at the full chart V (the mix of
  registers ending at V) is solved jointly and exactly. The solution makes every final row equal #7623's and is factored into
  ADD/SCALE events with 5-smooth coefficients (61,251 → 192,723 such events).

Exactly the 7 edited registers change chains. Five new MOVE pairs appear, all strictly nested: (3,618), (3,849), (449,928), (495,127),
(594,883). Two leave: (24,849), (595,618).

## Price

Native paid delta per call {1:−2, 2:−3, 3:−5, 5:+1, 6:+2}; helper target delta per call {6:+2, 9:−2}. Over 17 calls: paid
{1:−34, 2:−51, 3:−85, 5:+17, 6:+34}, targets {6:+34, 9:−34}. Paid positions 110,145 → 110,026; rank surplus S = 1,424 unchanged.
Official tools (`price.py`):
- `compare_recursive_invoices` against #7623 gives `uniformly_better`, strictly negative for r^(1−C).
- `evaluate_recursive_power` (256 bits) gives `new_cost_lower` at C = 0.0036667343458, 0.0036624027915 (#7623) and
  0.003665731276 (#7627), and `new_cost_higher` at C = 0.0036667343459.

Ordinary bill (17 calls, the repository `independent.py` formula with its call count set to 17): 786,433,632 for #7623 → 867,014,040
for this word, below 10^9. The re-derived hubs triple the word length (77,277 → 208,738 events), and that is where the increase comes from.
Coefficients are 5-smooth. The replayed grid moves from #7623's (2-adic exponent 25, odd lcm 1,125, 40 numerator bits) to (20, 675, 34),
and non-dyadic literal events go from 5,903 to 12,312.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-reroutes-on7623
```
`VERIFY.json` registers six commands:
- `core`: words, interior edit list, exact replay and legality of both words, rows, end charts and owned data, routes, coefficients,
  invoice and κ.
- `certificates`: all 180 CLEAR certificates, with 2 rejecting controls.
- `controls`: 14 rejecting controls and 3 accepting.
- `columns1` and `columns2`: the affected-pair column tests.
- `price.py`.

**Affected pairs.** #7623's census is 964 pairs. This word changes 7 routes, and the census becomes **981 pairs**: +17, the old and new
route pairs of the changed registers that were not already counted, with none dropped and every new MOVE pair inside. `check.py` runs 512
forward and 512 adjoint Gaussian columns, signed Pauli action, absolute phase, exact ascent rank and a wrong-phase rejection on all 981
pairs, in two halves.

Independently of the package, the word passed our exact pricer, an independent exact row replay with chart legality, a replay modulo 2^89−1 and 2^107−1,
the repository's `independent.py` native audit (bad_inputs 0) and caller identity (bad_outputs [], 17 native calls), and an interval
gate on the κ bracket, with 6 rejecting controls.

## Conditional premises and what is not rerun

The claim carries exactly #7623's premises (above), over the same 180 CLEARs with new, individually certified contents, and the signed
#7113 caller and BIT premise of the base. This package does not rerun #7620's full native/signed 17-stage application, catalogue, outer
predicates or precision/tape counts. The header, end rows, owned lifetimes and labels are unchanged, but the coefficient grid and event
count are not (see Price), so the precision/tape figures quoted for #7620 do not carry over verbatim. No upstream maintainer has reviewed
the package.

## Credit

The base is our [#7623](https://github.com/CrocSwap/integer-mult-bounds/pull/7623) on [#7621](https://github.com/CrocSwap/integer-mult-bounds/pull/7621),
which uses SYLforge's loan + stationary-snapshot device ([#7616](https://github.com/CrocSwap/integer-mult-bounds/pull/7616),
[#7620](https://github.com/CrocSwap/integer-mult-bounds/pull/7620)). Signed caller: rohanarun's #7113. See [NOTICE](NOTICE).
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Open next questions

**The premises.** A ruling on #7620's inherited assumptions and its CLEAR reading (`owned_erasure`, clear-form-gap Q1) decides #7620,
#7621, #7623 and this word together. See [TASK.json](TASK.json).
