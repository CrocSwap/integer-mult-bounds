# Chart-1 savings: parity, cheaper ingress and a conditional price

Each of the two one-export variants of the [#8036 chart-510 rewrite](https://github.com/CrocSwap/integer-mult-bounds/pull/8036) deletes one native rank-one MOVE. Neither is a valid supplier on the 630 independent public fields: its output map has rank **629**, and a specific output parity is zero on every possible input. Giving arbitrary additive changes to any combination of the other **2,802** MOVE payloads cannot restore the native output map while the remaining local instructions and final reads stay fixed.

A separate fixed-interface cut remains valid even if the chart-1 local decoder and all scalar payloads are freely recoded. Chart 1 starts with no public field. It has **505** independent prescribed final fields but, in either one-export variant, only **504** incoming scalar MOVEs. Those 504 messages cannot encode all 505 independent binary target bits. This cut keeps the remaining contact incidences and final public chart bindings; extra contacts, moved endpoints, extra initial side information, or a different public output contract are outside it.

The price of one rank shortening also motivates a separate fixed-history
screen. All **182** native chart-1 arrivals of rank greater than one need
information unavailable from the pooled histories of every cheaper chart and
chart 1 at the original clock. This does not rule out a changed producer or
changed destination demand.

At trial **κ = 0.00389046**, a hypothetical complete 36-call BIT invoice with one net rank-one paid deletion, no other tariff changes and the same productive inventory passes the stated 268-factor directed numerical test. This is a **conditional price**, not a legal rewrite. The two available one-export words fail the operator obligation, and an actual changed producer must also pay for physical routing, private owners, cleanup, the paired caller and the finite outer application. No new κ lower bound is claimed.

## Fixed-code parity

Let `M` be the original 630-field binary operator, which the replay verifies is an involution. Removing either native chart-510 export and installing its #8036 local readout gives `T = M + s r` over `F₂`. The source tape and ordered cocharted donor lists are embedded. The forward and independently implemented reverse checks agree on all 630×630 coefficients:

| Deleted native MOVE | Changed output rank | Weight of `r` | Weight of `s` | Surviving MOVEs |
|---|---:|---:|---:|---:|
| clock 10039, owner 2829, chart 510 → 1 | 629 | 29 | 12 | 2,802 |
| clock 10036, owner 2828, chart 510 → 1 | 629 | 18 | 7 | 2,802 |

For each, `ℓ = r M⁻¹ = r`, `ℓs = 1`, and `ℓT = 0`. For every remaining MOVE, let `d` be its exact downstream output sensitivity. Both the simultaneous forward-noise replay and the reverse interpreter check `ℓd = 0` for all 2,802 sites. Thus arbitrary, simultaneous, causal, even nonlinear choices of their scalar payload changes cannot alter this parity when the free local instructions, owner/endpoint schedule and final readout remain fixed. An additional terminal read of changed private history is not covered by that parity claim.

The original word and both changed words retain the same 3,433 private clears, all symbolically dirty on unrestricted inputs. The verifier includes a legal synthetic fault-and-repair control, a wrong-donor rejection, a corrupted-source rejection, and a residual oracle immediately before the first relevant reader. The oracle and external helper read are diagnostic controls: their delivery and cost are not supplied.

## Decoder-independent chart-1 cut

The 505 required fields at chart 1 consist of 111 first-rail outputs, 391 rank-eight helper outputs and three rank-four helper outputs. They are independent binary linear functions of the original public inputs. The native tape has exactly 505 incoming MOVEs to chart 1, with rank histogram `{1: 323, 2: 180, 4: 2}`, and no outgoing MOVEs. Either one-export variant has 504 arrivals and no initial public data at that chart.

Even if the retained scalar messages are arbitrary functions of the full input and preceding history, the transcript of 504 binary arrivals has at most `2^504` values. A deterministic cocharted decoder therefore cannot reproduce all `2^505` possible target tuples. The same argument applies by restricting arbitrary bank contents to constant binary fields. It does not price or prohibit an extra contact, a changed chart interface, prepositioned side information or a changed target domain.

## Cheaper existing chart-1 senders

The native 505 chart-1 arrivals include **180 rank-two and two rank-four**
contacts. For each, keep its original received field and clock. Grant free
retention of every earlier native chart-1 value and the whole preclock native
history of every existing sender with a cheaper nested contact to chart 1. The
receiver is even given the union of *all* those senders' histories for free.
The required original field is outside that union for all **182** arrivals.
This grants more information than choosing a single cheaper sender. It does
not include changed upstream producers, a changed receipt requirement or
additional retimed information.

The checker verifies all 300 relevant rational projector candidates and
**22,200** individual sender tests: 21,600 for the rank-two arrivals and 600
for the rank-four arrivals. Each exclusion has a checked dual input shift;
the original sender is an actual live positive control for every arrival.
At clock 6908, the required field is `e47 + e328`, and the shift
`e47 + e48 + e52 + e58` is invisible to chart 1 and every cheaper sender's
preclock native history but flips that field. The same checker independently
verifies the original 630-row forward and adjoint operators, all 3,433 dirty
clears, corrupted dual witnesses and a corrupted source. See
[SHORTER-INGRESS.json.gz](SHORTER-INGRESS.json.gz) for every case.

## A literal 326 → 531 → 1 diagnostic

At native clock 8075, field 2327 normally moves directly from chart 326 to
chart 1 at rank two. A literal diagnostic changes the earlier 326 → 531
payload at clock 8072 and sends a copy onward from 531 → 1 at clock 8075,
so the second contact has rank one and the original 2327 receipt is exact.
The resulting displaced field is owner 2326. Immediately before its first
reader at clock 10137 it is the **only** live owner with a wrong normalized
value; without repair, nine final public rows fail.

The missing value is the native XOR of owners 1857 and 2224 at the 326 source.
Its 27-input support is `3, 59, 60–72, 230, 359, 362, 365, 367, 372, 375,
378, 386, 388, 390, 522`. Granting that value as an oracle XOR into owner
2326 immediately before clock 10137 makes the entire live state, all 630 final
rows and all 3,433 private clear values equal to the native word. This is a
control, not a delivered or priced repair.

By clock 10141, chart 531 has only two original incoming contacts, at clocks
8072 and 8098, and no initial public field. Preserving receipt 2327 and both
original 531 → 1 exports at clocks 10138 and 10141 asks for three independent
binary forms. The two-arrival capacity is insufficient, even with arbitrary
recoding inside that stated interface. Extra or retimed receipts and changes to
the old export requirements remain open. The replay checks the exact rational
nesting of 326 ⊂ 531 ⊂ 1 as well as the literal state and oracle controls.
[RELAY.json](RELAY.json) records the complete residual and both reader checks.

## Conditional tariff at the trial

The paid counts below are for the entire 36-call binary caller. The numeric verifier rebuilds its binary histogram from the pinned graph and caller, and compares rational log/exp enclosures with an integer-root enclosure reader from #8036. The positive-supplier histogram and signed outer gates are the explicitly retained #8035 profile; this package does not rerun that positive supplier's physical source.

| Hypothetical change | Paid count | Rank sum | Raw surplus interval | 268-factor surplus interval |
|---|---:|---:|---|---|
| None | 104,904 | 285,600 | −0.132405116496822168 to −0.132405116496822167 | −0.000125133587380463 to −0.000125133587380462 |
| One net rank-one deletion | 104,903 | 285,599 | 0.867594883503177832 to 0.867594883503177833 | 0.000819561054648514 to 0.000819561054648515 |
| 36 net rank-one deletions | 104,868 | 285,564 | 35.867594883503177832 to 35.867594883503177833 | 0.033329702776022543 to 0.033329702776022544 |
| One rank-two charge shortened to rank one | 104,904 | 285,599 | 0.862208826193327056 to 0.862208826193327057 | 0.000814475257148468 to 0.000814475257148469 |

The same directed test passes for replacing one existing paid rank `r > 1`
by `r − 1` at each of the 13 ranks present in the complete caller inventory.
This hypothetical keeps the paid count and productive inventory fixed; it
does not identify a legal shortened contact. The smallest powered surplus in
the 13 examples is at least `0.000801304549856805`.

The numerical certificate also retains the positive 128-factor price, six staged rates, 21-bit ordinary and 10-bit positive debit, and **54 strict plus four functional** signed gates; its minimum strict/functional margin is `10⁻¹⁸`. The replay checks the previously priced 24-versus-25 fusion boundary as a control. Adding a rank-one payment, changing the productive inventory or changing the physical supplier invalidates the one-net-deletion invoice unless repriced.

## Reproduce

With Python 3.12 and the standard library:

```sh
python3.12 -I -B verify.py
```

The verifier authenticates the embedded sources and reference outputs, runs the forward noise certificate, the independent reverse audit, the chart-1 cut, the cheaper-sender screen, the literal relay diagnostic and the conditional directed price. It compares each deterministic result with its checked receipt without rewriting any source or receipt. `VERIFY.json` registers the same command. Base provenance is pinned to `e54523517d0f03e58352e647c403a5af3e525a57`; the external graph and its original source head are separately pinned in `SOURCES.json`.

## Open next questions

- Can an altered paid incidence or a delivered side observation recover the missing chart-1 information within the complete invoice? Start with a named source, destination, clock and displaced reader; this leaves the fixed-interface cut. The frozen-history screen does not cover changed producers or changed received values.
- Can a changed primitive word, including its private owner schedule and physical bank lifecycle, produce an actual one-net-rank-one saving? First emit and replay all 630 forward rows, their adjoints and the actual 36-call paid/productive inventories. A scalar or hypothetical price by itself does not answer this.

## Attribution

Ali Romman supplied the 111-port graph and physical supplier. ToikY nominated the chart-510 site, DreamingOfClouds supplied the #7852 toolkit, and Clear1nsight prepared #8036 and this follow-up with substantial OpenAI Codex assistance. The literal source's prior credits and Apache-2.0 license are retained in [PARENT-NOTICE](PARENT-NOTICE) and [LICENSE](LICENSE). The separate forward and reverse computational checks are author-side evidence; independent human scientific review remains open.
