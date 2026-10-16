# P104 Y2 needs exactly 39 monotone acquisition lifetimes

The twelve late-access sources identified by [PR2460](https://github.com/CrocSwap/integer-mult-bounds/pull/2460)
can share three chronological acquisition paths. Together with 36 sources that
must be read at their initial lines, this gives **39 new dirty helper lifetimes**
for Y2, and a matching 39-source read-frame antichain proves optimality in the
X-only monotone relay model below. The exact word restores every dirty input.
It pays **351 boundary rank units and 174 scalar ADDs**.

This answers PR2460's explicit later-contained-frame handoff. Its 94-helper
three-target theorem assumes one capture per source at the initial line and
does not claim an unrestricted bound. Here the target set is Y2 alone; the new
mechanism is sequential acquisition of distinct source values after their
original frame expansions. Y0's 48-lifetime bound from PR2393 and Y0/Y1's
78-lifetime bound from PR2445 retain their stated domains and credit.

**No complete supplier or new kappa.** This is a written scoped lower bound and
an exact finite common-chart construction. Native phases/scalar-address maps,
global owners and idle children, physical precision/tape and all-size admission
are not supplied. Boundary progress is not recursive excess cost.

## Model and lower bound

Retain the entire PR1972 original word and all its frame paths. Original X
sources are immutable logical inputs. New helpers start with independent
arbitrary dirty values at ZERO and move only along nested increasing binary
frames. They may read original X values at their actual frames and mix with
each other by rational same-frame ADDs. They may add into Y2, but cannot read
targets or original G/Q/D/private registers, modify original registers other
than Y2 by those additions, allocate, discard, reset or descend. Coefficients
are input-independent. Arbitrary relay depth, cancellations, retiming and
multiple source reads are allowed. The original word never reads Y2, and Y2's
frames increase inside its endpoint hyperplane H2. Thus corrections do not
alter the old computation or feed back from the target.

Let S=I-G/2. Its Y2 row has 48 nonzero coefficients. Every such source must
have a causal path through a new helper to a Y2 addition; otherwise that
independent source coefficient cannot change from G/2 to identity. Along that
path, new-helper frames only increase, so the original-source read must occur
at a frame contained in H2. This remains true with arbitrary relays and
cancellation: expand the linear circuit coefficient into directed paths and
choose a nonzero contributing path.

The verifier enumerates every original-source frame interval contained in H2.
For **36** required sources, only the initial line is allowed: the first
expansion leaves H2 permanently. Add sources **3, 6, 15**. The allowable frame
families of these 39 sources are pairwise incomparable: no allowable frame
for one source is contained in an allowable frame for another. There are
741 source-pair checks, each comparing *all* allowed frame episodes, not just
the chosen read times. Therefore a monotone helper lifetime cannot perform the
necessary original-X reads for two of these sources. Each of the 39 sources
needs a distinct lifetime, even when all restoration and timing constraints
other than monotonicity are relaxed. Hence **at least 39** new lifetimes.

This is an arbitrary-length causal-path argument, not an exhaustive circuit
search. It does not imply 39 simultaneous physical registers or a global stock
lower bound. Original-helper reads, writable original storage, descending or
disposable helpers and target feedback change the premises.

## Attaining chronological word

The 36 forced sources each get one helper, captured at cut 0. The other twelve
sources use these three helpers, with cuts counting completed original events:

| Helper | Source reads at original cuts | Successive capture dimensions |
| --- | --- | --- |
| L0 | X3@502, X7@618, X20/X29@681, X0/X96@842 | 3, 4, 5, 6 |
| L1 | X6@559, X12@627 | 3, 4 |
| L2 | X15@541, X1/X24/X100@669 | 4, 5 |

Each listed frame is contained in the next and in H2. Its actual basis,
source coefficient and interval are in [CIRCUIT.json](CIRCUIT.json) and
[RESULT.json](RESULT.json). At each capture the helper adds S[2,s] Xs.
Its logical value is its original dirt plus the acquired partial correction.

At cut 0, Y2 subtracts each of the 39 original helper dirt values at ZERO.
At original cut 4058, each helper climbs to H2 and adds its accumulated value
to Y2. The initial dirt subtraction cancels exactly. Each helper then climbs
to FULL and subtracts every acquired S[2,s] Xs using the now-full original X
registers. Every helper returns to its independent initial logical value.
All original events remain present and in order; the original private-copy
lifetimes are unchanged.

The full 4,354-event word acts on 319 independent input columns. Y2 ends as
`y2+x2`; the other 103 targets retain `yt+(Gx)t/2`. All 104 sources, 72 original
dirty helpers and 39 added dirty helpers retain their logical inputs and
prescribed final frames. The check covers 101,761 endpoint coefficients.

| Added quantity | Exact value |
| --- | ---: |
| New dirty helper lifetimes | 39 |
| Original-X reads, including cleanup | 96 |
| Scalar ADDs | 174 |
| Nested transports | 122 |
| Dimension-gap profile | 80 H1 + H2 + 3 H3 + 2 H4 + 36 H7 |
| ZERO-to-FULL rank mass | 351 = 39 times 9 |
| Full original-plus-added rank mass | 2719 |

The rank mass is sharp if every lifetime must finish at FULL and nested
transports cost their dimension gaps: telescoping costs nine per lifetime.
The ADD count and histogram are not asserted optimal. Compared with 48
separate acquisition helpers for the same target, the lifetime and boundary
mass decrease by nine and 81; that comparison does not claim a favorable
complete recursive moment or inherit Y0's source geometry.

## Reproduce

Standard-library Python 3.12; default replay is read-only and Git-free. The
two external JSON inputs authenticate against [SOURCES.json](SOURCES.json).
No pending predecessor executable is imported.

```sh
python3.12 -I -O -B research/p104-y2-late-acquisition/verify.py --regenerate
python3.12 -I -O -B research/p104-y2-late-acquisition/independent.py
python3.12 scripts/research_package.py --package research/p104-y2-late-acquisition
```

The primary checker uses sparse Fraction rows and enumerated binary spaces;
the second independently uses dense quarter-integer rows and binary echelon
reduction. Both check the complete arbitrary-input endpoints and antichain.
Seven primary semantic controls reject missing dirt compensation, wrong
capture coefficient, wrong target, missing cleanup, a premature capture cut,
false rank billing and altered source-frame premises. Equivalent ADD frame
bases pass. The dense checker separately rejects compensation and cleanup
faults. Both direct checkers also pass in a Git-free source export, with all
11 exported files unchanged. A separate AI-assisted reviewer read the scoped
proof and reran the dense checker with no actionable issue; this is not
independent human review. `--regenerate` compares the entire parsed literal circuit.

The registered replay and baseline binding check passed locally on CPython
3.12.14; the direct primary replay also passed on 3.14.7. On this Windows host,
temporary regeneration required TEMP/TMP set to a writable workspace directory.
No selected cold replay, hosted-CI pass, human review or formal-kernel proof is
claimed. [TASK.json](TASK.json) states source freshness and limited Discussion
coverage: complete 693-open-PR metadata snapshot, visible required-board pages,
but the paginated Discussion API was rate-limited. This is not a novelty guarantee.

## Open next questions

Can these three paths replace the twelve Y2-exclusive captures inside the
three-target word of PR2460 without changing its other collector obligations?
Splice the exact captures into that word and replay all dirty inputs. Its old
94 lower bound has a changed premise and cannot simply be reused.

Can the 122 new transports receive native phase-correct lowering and an actual
owner/idle invoice? First compile their literal chart maps and scalar address
operations; only then price the globally hosted construction, precision and
all-size obligations. The original native channel does not automatically admit
the added transports. Structured questions and blockers are in TASK.json.

## Credit

Prepared for **ywz65**, with substantial OpenAI Codex assistance in derivation,
implementation, checking and exposition. Apache-2.0. Credit PR2460 for the
twelve-source exception and explicit late-acquisition handoff; Ross Richardson
/ PR2445 for the two-target sharing construction and acquisition proof;
commdata2338 / PR2393 for the one-target causal acquisition argument and dirty
compensation construction; Hiroki Kumazaki / PR2353 and Philippe Van Velzen
for the relay model and lifetime distinction; Rohan Arun / PR1972 for the
complete original word; Chafik Boukhalfa / PR1991 for its native realization;
Adam Gall / PR1940, Josie Elliston / PR1071, Ali Romman / PR1125 and the retained
PR968/717/446/595/620 geometry/compiler lineage. Frozen sources and selected
frontier records are unchanged. No independent human review is claimed.
