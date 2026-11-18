# Separate basis audit of the helper restrictions

**Scoped exact audit; no new kappa.** All 33 helper restrictions from
PR #7713 pass a separate rational basis calculation. It checks all
67 receiver relations on independent entrances, retains all 400 main
fields and 1,068 surviving helpers, and debits every surrendered
productive target. Both final endpoint orientations pass.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[verify.py](verify.py), [SOURCE-PINS.json](SOURCE-PINS.json) and
[CREDITS.md](CREDITS.md). The construction and gain belong to the
source authors. This package supplies new checking evidence.

Helper 264 removes paid ranks two, four and three for one rank-nine
target. The first transposed case, helper 559, is step 13 after twelve
forward restrictions. It removes ranks three and six for one rank-nine
target. The complete caller removes 1,072 paid jobs and 528 productive
jobs. Both rank masses fall by 3,200; the surplus stays 1,328.

## Reproduce

Use CPython 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/helper-quotient-basis-audit
```

Both registered normal and optimized commands print:

```text
PASS_HELPER_QUOTIENT_BASIS_AUDIT 67 33 1468
```

The standalone command is `python3.12 -I -W error -B verify.py`
from this package. No Git, source constructor, network, installed
dependency or generated file is needed. Each replay is bounded at
120 seconds. SOURCE-PINS.json authenticates retained bytes; RESULT.json
records the deterministic result.

All 1,501 parent rows and all 1,468 final rows in both orientations
are checked. Receiver checks evaluate only required ancestors.
Coefficient products total 9,280,471 for the parent, 116,794 for
receiver identities, 9,657,314 for final forward rows and 7,948,543
for final transposed rows. Controls reject 67 changed receiver
coefficients, 33 changed entrance pivots, 33 missing target debits
and one wrong orientation.

The parent is a source-constructor export. The source proof and code
were read before this separate implementation. The audit is not blind
or human review. It does not independently reconstruct the raw word
or earlier cuts. Physical phases, owned storage, scalar arithmetic,
compiler and numerical kappa crossing are outside the check. All five
selected assumptions remain open. No full selected replay, predecessor
suite, Lean, Docker or formal-kernel check was run.

## Coordination and scope

The canonical [audit claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19711966)
takes the source PR's explicit request. This is a refined
`supplier-boundary-audit` at priority revision 8, based on canonical
main `e54523517d0f03e58352e647c403a5af3e525a57`.
The selected record is unchanged. The contextual catalogue is older
than that record; the current selected binding check passes.
Live open PRs, Discussions, source references and the closed cache
were checked. Sparse local and unpublished work remain coverage limits.
No construction search, two-constraint extension or peer PR edit is made.

## Open next questions

A separate physical or compiler audit must select one implication
at this exact graph and check live claims first. Normalized equality
does not prove signed native phases, owned reset behavior, precision
bounds or a materialized full multiplier. The [task record](TASK.json)
states this boundary and first step. No follow-up is reserved.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. Source attribution and supplier notices are retained.
