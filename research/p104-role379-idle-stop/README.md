# Conditional κ ≥ 0.0037170835567 from the role-379 contraction

Role 379 can go directly from chart 748 to chart 1072 on both pinned
words. The removed stop at chart 1065 has no use of role 379. The direct
rank-3 MOVE replaces ranks 2 and 1 with the same absolute operator,
public outputs, owned observations and productive targets.

The full finite #7658 candidate application supports the conservative
conditional bound **κ ≥ 0.0037170835567**, with safety probe
**0.00371708355677**. Its directed invoice crossing lies in
**[0.0037170835568, 0.0037170835569]**. The bound is 0.00000031655885
above #7658's published upper crossing. The #7636 edit has a directed
invoice crossing in **[0.0036810345257, 0.0036810345258]** under its
declared residual and 180-CLEAR contract.

| Pinned parent | Source events → candidate | Ordered CLEARs | Paid positions → candidate | Productive targets | Directed parent bracket | Directed candidate bracket |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| [#7636](https://github.com/CrocSwap/integer-mult-bounds/pull/7636) | 202,668 → 202,667 | 180 | 109,652 → 109,635 | 22,461 | [0.0036807241001, 0.0036807241002] | [0.0036810345257, 0.0036810345258] |
| [#7658](https://github.com/CrocSwap/integer-mult-bounds/pull/7658) | 150,010 → 150,009 | 234 | 108,598 → 108,581 | 22,461 | [0.00371676699784, 0.00371676699785] | [0.0037170835568, 0.0037170835569] |

For each comparison the paid delta is `{1: -17, 2: -17, 3: +17}`, the
targets are unchanged, and rank surplus stays at 1,424. The declared
signed invoices are retained in [the source bundle](retained/). The
replays recount native ranks from the two literal words in each case.
[The proof](PROOF.md) gives the transition identity and source clocks. [The independent review](REVIEW.md) describes the source-specific hypotheses behind the signed application.
[The discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19695810)
records the original bounded investigation.

## Registered replay

Both exact replays compare all 1,501 arbitrary-input public rows and
their end charts. They verify each original live-donor certificate in
both tapes. #7636 retains 1,049 ordered owned or COPY observations and
#7658 retains 1,317. For both cases the exact Gaussian checker compares
the two old transitions and the direct transition against their
canonical operators, then compares the two-step composition against the
direct transition. Each comparison covers 512 forward and 512 adjoint
columns with absolute phase. The wrong-phase control preserves the
signed Pauli tableau and is rejected by the column test.

The mutation checker also rejects a valid intervening SCALE, an
incorrect MOVE source, an omitted direct MOVE and a changed scalar.
The separate replay rejects an illegal chart, a legal sign change with
the same recursive invoice, and a self-referential CLEAR certificate.
It independently derives the full invoices using the declared caller
residuals and encloses their price crossings with rational logarithm and
exponential bounds. The construction uses the pinned 256-bit directed
invoice evaluator. On #7658 the published exact upper at 14 decimal
places is checked by the independent replay. The construction first
refused that upper at its 13-decimal grid guard and then used the
conservative upward tick 0.0037167669979.

| Case | Mutation and phase in original run | Separate exact replay in original run |
| --- | ---: | ---: |
| #7636 | 9.11 s / 103,088 KiB RSS | 104.30 s / 261,188 KiB RSS |
| #7658 | 14.44 s / 85,128 KiB RSS | 56.45 s / 244,204 KiB RSS |

The separate replay applies one CPU, 2 GiB address space and 240-second
CPU and wall limits per case. Each combined command is capped at
300 seconds. The third command reruns the #7658 signed application
under a 560-second caller deadline and a 600-second registered cap.

From the repository root on Linux with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/p104-role379-idle-stop
```

To replay an offline copy directly, run from this package's directory:

```sh
python3.12 -I -B verify.py 7636
python3.12 -I -B verify.py 7658
python3.12 -I -B application-evidence/signed-replay/replay.py --core . run --wall 560
```

The first two commands check the source bytes, reconstruct the mutated
words in private temporary directories, and compare both fresh checks
against the [retained receipts](evidence/). Generated gzip encoding
may vary across Python and zlib builds. Candidate comparisons authenticate
the exact decompressed bytes, while the independent replay binds the
actual gzip bytes it read on that run. The signed replay rebuilds the
#7658 candidate in a fresh temporary directory and compares its
deterministic application results with the retained signed receipt.

## #7658 finite application

The [application evidence](application-evidence/README.md) records the
separate, candidate-bound native, resource and signed caller runs. The
paired native audit checked both actual words with primes 998244353 and
1000000009, exact phase at the edited transitions, all 234 ordered
CLEARs and the retained native route inventory. It bound 2,952 exact
ascent groups to predecessor phase evidence and checked the other seven
fresh. The signed candidate run recomputed the 17-call #7113 caller, all
3,030 catalogue maps and 104 boundary pairs. A global-phase mutation
rejected in each of four catalogue slices. The aliased-main and
lower-crossing controls also rejected.

Both precision replays require the same native grid 225 × 2¹⁴, cover
24,277,036 coefficient and pre-product visits, and yield shared
context 2,064. The candidate's fixed-tape model binds ambient rank 145,
1,156 reserved native
banks, 83,895,232 scalar services and 25,147,082,048 elementary records
under the retained width and movement assumptions. Its ordinary model
totals 815,804,876 source units after charging all 51,034 native grid
conversions in addition to the inherited allowance. The outer gate
passed all 54 strict and four functional predicates. The effective BIT
subthreshold was checked as an algebraic inequality under the retained
BIT premise. The seven fixed-tape guard mutations rejected.

The registered signed command authenticates the native, CLEAR,
independent and grid/ordinary receipts. It reruns the transposed native
endpoint, the actual 17-call signed caller, all catalogue slices and
physical boundary checks, both directed price engines, the outer gate,
and the fixed-tape checks. The [application appendix](application-evidence/README.md)
gives separate reproduction commands for the paired two-prime native
run and rational/integer grid and tariff checks.

## Source and assumption boundary

The catalogue is provenance at base
`e54523517d0f03e58352e647c403a5af3e525a57`. The external parent sources
are vendored at the exact commits, paths, Git blob IDs and SHA-256
values in [SOURCE-PINS.json](SOURCE-PINS.json). The application
appendix binds its executable closure and exact receipts separately.
Git history verification for the catalogue belongs to the registered
launcher. Offline replay uses the bundled inputs and original notices.

| Parent | Exact head | SHA-256 of original decoded word | SHA-256 of candidate decoded word |
| --- | --- | --- | --- |
| #7636 | `7e68d8dd62d9a38c0f3c942262a7a85ca7125b75` | `98b8c12ece2f323a6ff5cac8c7ed2f78ba3835438ea56b16bd7d4698ec5ad5b2` | `9b5b66e93f91c9538525d8d7b1278e0f203058d5cd4e1351fa06f8315fdaa555` |
| #7658 | `0a0e71c34a5ee5a1b59a8fe7bc6abd35a4d3dd82` | `fa84fcdecb534700cd00dc81b74889f549a653daa2fb3658cb8142e1eeb9b9e6` | `f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669` |

The witnesses and bound carry #7620's five inherited assumptions:
native all-column provider, owned erasure, compiler, precision/tape
and analytic recovery. The ordinary and resource counts also carry the
same-tariff common-U assumption across the whole private extent,
including nonaliasing and return, and the retained W+26 temporary
format. The standalone price brackets use each parent's declared
#7113 residual. The application verifies the #7658 candidate's actual
signed invoice under those contracts.
The #7658 comparison preserves role 457's initial chart 281 and all 234
CLEARs, with 52 of 68 allocated labels used. The #7636 comparison preserves
its 180 CLEARs and 68 used labels.

On the #7658 candidate, clocks 100503 and 100504 move role 457 from
966 to 218, then apply `ADD 210,457,-1/2` in chart 218. The original
clocks are 100504 and 100505. In fixed-grid units, an even coordinate
can become odd after a one-tick perturbation. Exact same-grid halving
then fails. The all-width supplier needs a componentwise congruence
and range invariant at this boundary or a charged total rounded ADD
on all admitted states. The [proof](PROOF.md) records the obligation
alongside the finite exact-grid and norm-envelope checks.

For #7636 the unchanged literal ADD at old clock 150836 has coefficient
`23184221/921600`. Its numerator exceeds the historical 24-bit fixed-tape
guard on the #7636 source and its MOVE-only successor. A separate matched
compilation check splits it into consecutive same-chart ADDs with
coefficients `25` and `144221/921600`. The lowered pair passes the
24-bit guard and exact grid 54,675 × 2¹⁶, preserves all 180 CLEARs and
retains context 2,164 in the fresh native and caller envelopes. Each
lowering adds 544 modeled scalar services over the 17 invocations.
The charged ordinary-model totals are 868,475,092 and 868,458,092
respectively. Full native and signed application on the separately
hashed lowered pair remains open.

## Credit

DreamingOfClouds supplied both exact parent words and the initial
main-176 contact changes. #7630 E6 and #7658 E2 exposed the silent stop
on their respective lineages. The #7658 base also credits SYLforge's
#7637, Ali Romman's #7605 and Rohan Arun's signed #7113 caller. The full
lineage and retained code credits are in [NOTICE](NOTICE). Clear1nsight
prepared this package with substantial OpenAI Codex assistance. The
task scope is changed from a joint helper-basis/channel split to a
single paid native transition contraction on two exact words.

## Open next questions

- Independently review the exact #7658 candidate application and its
  inherited rounded-domain, common-U and W+26 contracts. Start with
  the exact-halving boundary and the private-field nonaliasing,
  return and scratch-movement schedule across all 234 lifetimes.
- For #7636, replay the actual native and signed callers on the
  separately hashed lowered pair with all 180 CLEARs and the
  charged scalar and precision envelope.
