# Execute complete literal CRT service and terminal retirement

**The unchanged current CRT producer and consumer now use one fixed 73-role
graph for arithmetic, lifecycle and terminal retirement.**
The old numerical/lifecycle providers and original Entry.close are blocked
for their replacement scopes. The three existing record owners are bound
once before execution; no role is rebound and no history is reset.

The graph preserves the public 70-role joined provider at
7a6334dceef9d03fb5b1aeec4269a2911c0112b4 as an unchanged prefix and appends
a 2,949-state terminal. The complete graph has **1,438,047 states** and hash
8616c06f340a18be2e947a6244ee58bbc6cddd7ea43994e8a1dcb6d87dc9855f.

## Complete source result

At P=7, left [(5,1)] and right [(7,2)], the exact original producer returns
lower=1, product=5 and output record (3,5), matching an independent CRT oracle.
After consumption, the terminal closes all owned physical histories.

| Evidence | Result |
|---|---:|
| ADD / COMPARE / DIVIDE / SUBTRACT | 82 / 63 / 14 / 6 |
| Same-handle additions | 63 |
| Total literal service calls | 2339 |
| Total literal instructions | 3,120,094 |
| Terminal instructions | 2977 |
| Positive replaced-provider calls | 0 |
| Remaining native symbol actions | 2050 |
| Complete physical owners / retained cells | 76 / 8991 |

All 76 capacities and touched intervals are recorded. The new fixture
explicitly supplies backed windows for every source primitive, including
the guide blank and three unequal record histories. No backing grows or
shrinks during the complete invocation.

## All-width terminal result

With u=P+n70+n71+n72, terminal cost is exactly **7u+2928** R/W/M/J/H
instructions. The per-op counts are R=848+2u, W=399+u, M=1680+2u,
J=2u and H=1. The physical stack guard precedes erasure and metadata
retirement comes last. Its decision uses the existing stack invariant,
without a host live/free set.

The old 70-owner binding cannot erase the three outside record markers.
Three additional fixed role labels suffice, using the existing owners.
PROOF.md and TERMINAL-PROOF.md distinguish that fixed-binding obstruction
from a general lower bound, and retain clean inactive tails and grants.

## Remaining work and invoice

The exact retained native action counts are 1011 on Words, 151 on the
guide, 782 on owned record ports and 106 on borrowed canonical inputs.
Their total is 2050. Pure higher control is still a separate premise;
source-function call diagnostics are not presented as physical prices.
The original 468 native Entry-close actions are now in the literal graph.

Higher controller/consumer lowering, grant construction and changing-Entry
attachment remain open. All five selected assumptions and kappa remain
unchanged. No complete multiplier or whole-caller physical tariff is claimed.

## Reproduction

CPython 3.12, standard library. From the repository root:

    python3 -B scripts/research_package.py --package research/complete-crt-terminal-service

The registered normal and optimized executions build the million-state
graph in memory. Budget approximately 550 MiB and one minute for both
full replays; ENVIRONMENT.json records measured costs. No giant generated
graph is committed. The 22-file authenticated source closure is 291,576 bytes.

For independent work, terminal.py exposes the small graph constructor and
relocation function; integration.py exposes the full prefix/suffix
constructor. Checkers can use a separate raw-array interpreter. See
COLD-FETCH.md for exact public-source acquisition without a full clone.

The included independent review uses its own character-array interpreter
and imports only compile_terminal. It checks 20 other fixtures at five
precisions through P=1024, both locally and after its own relocation:
40 executions and 247,208 instructions. Its full-history, per-op tariff,
missing-blank, returning-mutation and footprint controls pass normally and
under optimized Python. This reviews the terminal component; independent
review of the new complete integration remains a separate obligation.

## Files

- PROOF.md: source substitution, complete execution and residual invoice.
- TERMINAL-PROOF.md: uniform terminal proof, footprint obstruction and costs.
- integration.py / verify.py: fixed combined execution and full-source oracle.
- terminal.py / check_terminal.py: small all-width terminal and controls.
- RESULT.json / TERMINAL-RESULT.json: deterministic domains and receipts.
- SOURCE-PINS.json / SOURCES.json: exact copied closure and original provenance.
- NOTICE.md: predecessor credit and explicit limits.
- review/REVIEW.md: independent terminal scope, derivation and replay.

Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.

## Open next questions

1. Lower a retained consumer, Word predicate or record operation using the
   exact source call site and native action group recorded here.
2. Attach this complete provider across changing Entry widths while keeping
   every physical historical bound and its single terminal phase.
3. Supply the actual blank windows and initial framing at a common physical
   price; the explicitly granted fixture does not construct those grants.
