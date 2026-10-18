# Quad17: exact 12-ADD minimum and a sharp reverse envelope

**Scoped negative result and exact finite audit; no new kappa.** Gareth
Davidson's retained PR952 R439 word already realizes frame283 / quad17 with
the minimum **12 positive ADDs** for its exact integer transfer on six labelled
registers. Its reverse positive matrix is exactly **the entrywise absolute
value of the inverse**. Thus it also attains the smallest valid reverse
endpoint envelope for every independent incoming coordinate budget.

This contribution certifies that boundary. The construction and its scalar
savings are credited to PR952, including its PR904/936 predecessors. No circuit
is changed or nominated here.

## Concrete object and result

Input: `research/r439-six-wire-boolean/candidate.json.gz`, PR952 head
`11d24706f06e95271804c9438869546724c67aab`. The contiguous block is
`A[854:866]`, at frame283, on registers **312, 355, 412, 429, 434, 490**.
In that order its integer transfer is

```text
T = [1 0 1 1 1 0]
    [0 1 0 1 1 1]
    [0 1 1 1 1 1]
    [1 1 1 3 2 1]
    [1 1 1 2 3 1]
    [1 0 1 1 1 1]

B = |T^-1| = [3 3 1 1 1 0]
             [3 3 0 1 1 1]
             [0 1 1 0 0 0]
             [1 1 0 1 0 0]
             [1 1 0 0 1 0]
             [1 0 0 0 0 1]
```

The fixed-transfer alphabet is `x_d += x_s`, with distinct register labels.
Repeated writes are allowed. There are no extra registers, subtractions or
free permutations in the gate minimum.

| Quantity | Exact result |
| --- | ---: |
| Minimum forward positive ADDs | 12, attained by PR952 |
| ADDs including mandatory literal inverse cleanup | 24 |
| Complete last-gate graph | 9,739 states / 43,454 edges |
| Complete first-gate graph | 9,739 states / 43,454 edges |
| Shortest ordered programs | 1,008,032 |
| Distinct shortest-program reverse positive matrices | 57 |
| Shortest programs attaining B | 767,232 |
| Entrywise Pareto-minimal reverse matrices | One: B |
| Maximum reverse row sum for a common budget | 9 |

The all-length gate minimum follows from complete finite graphs, without a
program-length cutoff. The reverse-envelope minimum has a separate algebraic
proof for **all exact realizations of this inverse**, rather than only shortest
positive programs: every universally valid independent-coordinate envelope
must dominate `|T^-1|`. See [PROOF.md](PROOF.md). The certificate lists all 57
shortest-program reverse matrices with exact path multiplicities.

## Reproduce

Python 3.12, the standard library and Git with the recorded base object:

```sh
python3 -I -B research/r439-quad17-seed17/verify.py
```

Expected final line:

```text
PASS_R439_QUAD17 minimum=12 shortest_programs=1008032 reverse_endpoints=57 sharp_absolute_inverse controls=8 no_new_kappa
```

The command checks immutable source SHA256 and Git blob pins; independently
extracts the integer map; exhausts the last-gate graph and the first-gate
graph; independently counts all reverse endpoints by row and column methods;
checks both inverse products and the literal signed cleanup; and compares
the complete result to `CERTIFICATE.json`. Eight controls must reject:
deleting a gate, swapping noncommuting gates, substituting a Boolean-equivalent
integer lift, falsifying the minimum, lowering the envelope below the inverse,
resource exhaustion in each search, and falsifying a path multiplicity.

The two implementations are algorithmically distinct and written by the same
AI-assisted contributor. They are not independent human review or formal Lean
verification. State caps are 100,000; reaching one fails as incomplete.
One complete exhaustion is the stopping rule. No random circuit search occurs.
Assignment seed **17** selects quad17; it is not used to alter the search domain.

Optional registered replay:

```sh
python3 -B scripts/research_package.py --package research/r439-quad17-seed17
```

`--write-certificate` regenerates only this package's certificate. The immutable
gzip source is hashed as committed; PR952's candidate receipt is checked using
canonical decoded JSON, as required by its original representation.

## Pins, overlap and scope

Exact base: **`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`**.
Its selected conditional saving is **0.001672660197076918**, PR1094, retaining
PR589/555 on the bit side. This audit's actual input is retained PR952, not a
new selected supplier. `SOURCES.json` pins every consumed external file and
the historical selection/catalogue as provenance.

The earlier frame267 (PR925), frame272 (PR1002) and frame281 exact-transfer
studies are credited predecessors. This target has entry sum **36**, unlike
the published frame267 and PR952 frame281 targets (58 and 42); those minima
cannot be transferred by relabelling. PR952's bounded synthesis supplied the
12-gate word but did not certify its optimum or enumerate this envelope class.
`OVERLAP.json` records live PR/discussion coverage and the overlap-tool limit.
No matching quad17/frame283 claim was found in the covered records; that is
not a proof of novelty.

No helper, frame schedule, COPY, source-access operation, restoration program
or recursive child is added. The existing local pair costs 12 forward ADDs
and 12 literal cleanup ADDs; the precise excluded optimization would have to
beat that pair or improve its independent-coordinate reverse envelope while
keeping the same integer transfer. The paid profile and decoder constant are
not modified or replayed. No new supplier exponent or kappa follows.

The result does not exclude other Boolean-equivalent integer lifts, signed
programs with fewer forward gates, extra workspaces, changed paid interfaces,
or estimates that exploit correlations in the full word. Native multistage
execution and a whole hosted invoice are not run for this local audit.
All-size/compiler, realization, hosting, precision/tape, analytic-transfer and
H1-H5 obligations of the complete multiplication construction remain inherited.

## Open next questions

Can a different Boolean-equivalent integer lift or larger paid register model
improve this block without worsening the complete supplier budget? First write
the alternate lift and its complete helper/frame/source-access/cleanup invoice,
then compare the global guard and original H1-H5 interface. No such alternate
candidate or hosted invoice is supplied here. Scalar reductions need a paid
moment or precision-charge change to affect kappa. Structured details are in
`TASK.json`.

## Attribution and license

Cinna Davis (`@1337isnot1337`), with substantial **OpenAI Codex assistance** in
selection, mathematics, code, verification and documentation. Apache-2.0.
Credit Gareth Davidson (`@bitplane`, PR952/904), Ross Richardson (PR936/925),
woklerx (frame272 PR1002 and frame281), Jeffrey Cox and mtpsl (earlier finite
factorization/guard methods), eumemic (R420/R439), DreamingOfClouds (puncture
and PR589 tuning), and the selected maintainer/PR1094 lineage. Source notices
remain at their pinned predecessor locations. No predecessor code is imported.
