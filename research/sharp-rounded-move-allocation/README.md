# Smaller lifted records for a once-rounded complete MOVE

This contribution was produced by Nick Petalas.

Scoped written proof with exact finite corroboration. Under the retained
complete-MOVE provider premises of CubeJerry's
[PR #6996](https://github.com/CrocSwap/integer-mult-bounds/pull/6996), put
g=r f and k=ceil(g/2). A paid k-bit lift and component width

    w = h + 2ceil(g/2) + 1

suffice for every exact Gaussian prefix and both serial monomials. Drop k
bits once, after the exit. The rounded mathematical map, absolute phase,
final overflow test and actual-input error contract are preserved.
The source domain is #6996's retained #6030 raw catalogue. Mapping this
allocation to the selected #7000 caller remains open.

The previous width is h+g+ceil((g+1)/2)+1. The new allocation saves s+1 bits
when g=2s and s bits when g=2s+1. At g=8 it saves five bits per real
component. At h=2 and 4096 complete records with one complex coefficient,
the widened coded field falls from 417792 to 294912 bits. This is an exact
size calculation, not a physical execution or total runtime claim.

The new result is the complete-MOVE allocation substitution and its changed
record bill. The sharp Gaussian denominator and real row-norm facts are
credited prior work. [PROOF.md](PROOF.md) distinguishes the new step, cited
premises, descriptor changes and every retained cost. No new kappa or
supplier admission is claimed. The physical provider is unchanged; its
Count/Tape substitution and whole-MOVE trace remain unimplemented here.

## Evidence and reproduction

Use CPython 3.12 and its standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/sharp-rounded-move-allocation/verify.py --emit
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/sharp-rounded-move-allocation/verify.py --emit
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sharp-rounded-move-allocation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sharp-rounded-move-allocation --check-source-history
```

Other machines may substitute their CPython 3.12 path. Expected scientific
marker: `PASS_SHARP_ROUNDED_MOVE_ALLOCATION`. `--emit` prints a computed
receipt bound to all package files and the four cited input hashes; no
replay artifact is written into the checkout.

The exact reference checks 32768 allocations, of which 32640 strictly
reduce width; 131584 complete small input cases and all 1050624 output
components; 320 larger boundary cases; 4064 signed codec round trips;
31320 drop/range cases; and eight invalid-allocation, eight insufficient-lift
and one negative-exit rounding-order controls. Dense literal tensor
multiplication is independent of the butterfly implementation. The small
census has 943834 fitting and 106790 overflowing components. Every final
range rejection is checked against the exact rounded component.

The reference covers at most eight active axes and 257-bit data in its
large endpoint fixtures. The allocation API permits h and f through 4096.
The universal claim rests on the written argument and cited lemmas, not
extrapolation from these finite checks. No predecessor scientific program
is imported or run.

## Credit and limits

Credit CubeJerry's #6996 complete rounded source contract and #6989 variable
codec; Alejandro Zarzuelo Urdiales's #45 Gaussian parity/tensor work; Jose
Manuel / jmbarrancoml's #3091 physical Gaussian leaf and fused arithmetic;
Nick Petalas's #2772/#3089 prefix applications; and the monomial, cutoff,
codec, tape and native contributors retained in those sources. Exact
unchanged files are pinned in [SOURCES.json](SOURCES.json). Their original
credit lines remain unchanged. No literature-priority claim is made for the
Gaussian identities.

The complex-new-helper-inventory card is changed to a local precision/storage
side result. It adds no productive target or paid rank saving. All fixed
roles, staging, repetitions, source/control work, restoration and historical
backing remain charged. Full numerical physical execution, the selected
#7000 caller mapping, global precision/stock and every remaining framework
assumption are outside this result. Independent human and formal proof-kernel
review are unclaimed.

## Open next questions

- Implement the literal Count/Tape allocation substitution and execute a full
  admitted nine-block packet. Start with one source triple and include both
  protected stages and cleanup. The reference is not a physical supplier.
- Bind the new record length to one actual caller and recompute its complete
  long-record, control and history bounds. Source placement and a complete
  caller invoice remain blockers.

Structured questions are in [TASK.json](TASK.json). The claim is recorded in
[handoff #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19540627).

## Implementation bounds

All new functions are below 60 physical lines. There is no recursion,
subprocess, dynamic evaluation or runtime source import from a predecessor.
Loops are bounded by h<=4096, f<=4096, r<=8, reference g<=8, the fixed census
or at most sixteen manifest/package files. Explicit require checks remain
active under optimized Python. The registered normal and optimized commands
use isolated Python imports, warnings as errors and a 120-second limit.

Power-of-Ten rule 3 has a managed-runtime deviation in model.py and verify.py.
CPython allocates tuples and arbitrary-precision integers during execution.
Endpoint vectors have at most 256 complex coordinates, reference public
widths are capped at 4096 bits, and the scalar codec census has h<=8 and
lift<=4. Large endpoint fixtures use at most 257 input bits. The allocation
API performs only bounded-size integer arithmetic. These limits
bound live data, without claiming a fixed allocator or hardware bound. A
fixed-buffer implementation belongs to the physical follow-up. Warning-strict
normal/optimized checks and in-memory syntax compilation are the diagnostics
for this standard-library reference. No repository-wide tool configuration
is changed.

Apache-2.0, under the repository license.
