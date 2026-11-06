# Maximal resident-carrier span obstruction on the #6702 native word

**Result: no new native word or multiplication exponent.** On the exact native
word used by #6726, all **631** eligible single-helper transport intervals fail
a necessary response-span condition. The test allows arbitrarily many dyadic
injections into every other existing public or live owned field at the helper's
held frame, and leaves every final full-bank output entirely unconstrained.
Even this relaxation cannot preserve the required proper-frame outputs and
COPY-zero monitor. The obstruction is finite and source-bound.

The distinct contribution is the complete resident-response span and the
maximal chronological fusion window, rather than a one/two-compensator search
or a sampled frame neighborhood. It does not exclude changes to the held
source basis, additional carrier transports, removal of extra outside exports,
or coupled changes to multiple intervals. [PROOF.md](PROOF.md) states the
precise model, cut bounds, reduction argument, and exclusions.

## Exact result and calibration

| Replay input | Eligible intervals | Candidate cuts | Nominations |
| --- | ---: | ---: | ---: |
| #6702 native word used by #6726 | 631 | 2,387 | 0 |
| Earlier #6453 word | 634 | 2,413 | 2 |

The `cut_systems` receipt field counts candidate cuts. All 2,387 current-source
systems are solved. On the positive control, search stops at the first hit per
interval, so 2,413 is not a claim that every control system was solved.

There are 200 constrained final public rows and one actual COPY-zero monitor.
The largest current-source response rank is 23; 629 intervals have at least
one nonzero resident response. All 631 held source rows are nonzero modulo
65521, and all retained SCALE factors are modular units. Source validation
also replays the complete old-input map modulo 65521: 771 public input columns,
29 owned labels, and all 800 final rows on the current word.

On #6453, the identical algorithm recovers exactly the two event/injection
patterns in #6529's retained SPEC: helper 336, first/second events 8393/12924,
injection into owned 781 at cut 9048; and helper 368, events 8352/12893,
injection into owned 782 at cut 9101. Each returned modular coefficient is 1.
This calibration verifies the recorded pattern bindings; it does not
independently re-audit the predecessor's full-output cleanup. Those successful
constructions remain #6529's contribution.

A separate reviewer reproduced exclusion over 4,263 systems by adding cuts
immediately beside every threshold, and using unnormalized max-pivot cross
multiplication. That check reuses the reviewed response/residence generator;
it is an independent elimination and chronological-boundary cross-check, not
a second complete generator. Its separately retained review gives the code
and source hash.

The separately authored [forward review](FORWARD-REVIEW.md) independently
reconstructs the entire interval, residence and response system. All 33,455
forward residence segments match the primary reverse sweep. The retained
`FORWARD-REVIEW.json` contains 2,387 separating functionals; 24,012 direct dot
products check that each functional annihilates every allowed column and takes
value one on its required target. Three altered-inventory/target/witness
controls are rejected. This is a second implementation and review within the
same AI-assisted session, not external human or formal-kernel acceptance.

`review_forward.py` is a byte-exact copy of that review's `review.py`;
`FORWARD-REVIEW.json` is its current-source `PR6702-REVIEW.json`. The standalone
review also checked all 2,413 historical control cuts, with 35 successful
systems belonging to exactly the two known intervals. Its historical full
receipt remains in the original review commit recorded in `ORIGINS.json`.

## What is covered

Choose two consecutive forward MOVEs A -> B -> C of one actual public helper.
Between them, the helper may be rescaled but cannot receive any other write.
Delete every intermediate ADD export and replace the two MOVEs by A -> C.
The replacement MOVE can occur anywhere in the surrounding constant-up-to-scale
residence consistent with every retained A/C source read. Before the MOVE,
allow any finite set of ADD injections from the helper to other residents of A;
afterwards, allow the same at C. Recipient schedules and the remaining source
word stay fixed. Full-frame final outputs receive unrestricted free repair as
a relaxation; all proper-frame outputs and COPY-zero obligations remain.

The exact cut bounds and constant-response residence representatives reduce
this infinite-coefficient rewrite family to a finite collection of spans.
Failure over F_65521 excludes all exact dyadic solutions, since powers of 2
are invertible modulo 65521 and the held row remains nonzero. The result does
not cover arbitrary rational coefficients with a denominator divisible by
65521. No floating-point calculation decides exclusion.

The first exploratory helper-ID filter counted only 621 intervals. The final
replay identifies helpers by excluding the actual `live` and `live+112` role
sets, and includes the ten eligible intervals in unused main-register slots.
All source-wide claims and receipts use 631.

## Reproduce

The registered replay is `python -B scripts/research_package.py --package
research/p104-distributed-carrier-recoding`. Only Python's standard library is required. No network, toolkit, Git object
lookup, external solver, or optional numerical dependency is needed.

```sh
python -I -B research/p104-distributed-carrier-recoding/verify.py
python -I -O -B research/p104-distributed-carrier-recoding/verify.py
python -I -B research/p104-distributed-carrier-recoding/verify_forward.py
python -I -O -B research/p104-distributed-carrier-recoding/verify_forward.py
```

The verifier checks all pinned input bytes, reproduces both deterministic
receipts, binds both positive controls to the published SPEC, checks elementary
positive/negative span fixtures and source-corruption rejection, and verifies
that 65521 is prime. It uses explicit checks, so optimized Python retains all
validation. A primary verifier replay took approximately 2-3 seconds and 51 MB peak RSS
in this session. Direct replay is also available:

```sh
python -I -B research/p104-distributed-carrier-recoding/search.py \
  research/p104-distributed-carrier-recoding/inputs/PR6702-WORD.json.gz \
  /tmp/p104-current.json
```

`CURRENT.json` and `CONTROL.json` are deterministic receipts. `SOURCES.json` registers exact Git pins for both words, notices and the SPEC.
`ORIGINS.json` preserves the original source/archive-chain manifest used by the
standalone verifier.
The two words total 177,275 bytes. Archive-chain hashes explain how the current
word was extracted from the read-only #6726 package; archive access is not
needed for replay.

## Research implication

A profitable two-move fusion would ideally replace paid H_b + H_c by H_(b+c)
while preserving the target invoice. This package produces no nomination, so
it claims no complete invoice improvement, compiler theorem, all-size bound,
or change to the selected result. The five retained assumptions remain
untouched. Every ordinary instruction and any changed native obligation would
still need charging in an actual constructive successor.

## Open next questions

| Question and relevance | Feasible first step | Blocker |
| --- | --- | --- |
| Change the held source basis while preserving arbitrary old helper inputs; this escapes the fixed-row premise. | Derive one exact local rank-one basis correction and test all old input columns. | The basis correction must be realizable at actual resident frames and every paid stop must be charged. |
| Share a new paid carrier stop across several contacts; this escapes the fixed recipient schedule. | Nominate two contacts using the same added stop and compute their combined signed histogram before construction. | A one-contact saving can disappear after pricing the new stop; simultaneous endpoint/COPY legality must hold. |
| Couple intervals or delete additional A/C exports; this changes the error equations or chronological bounds. | Group intervals by their held old-input rows, then test exact combined errors and all retained reads. | Cross effects between edits can invalidate simple addition of isolated response columns. |

These are separate construction problems; increasing response sparsity or
trying more seeds inside the present model cannot evade the obstruction.

Prepared for Jerry Chen / **@CubeJerry**, with substantial OpenAI Codex
assistance and separately identified agent review. Apache-2.0. See
[NOTICE.txt](NOTICE.txt) for predecessor attribution and [TASK.md](TASK.md) for
the original question, overlap check, and stop criteria.
