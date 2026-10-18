# One P104 endpoint matching passes the relaxed dependency test

A four-edge alternating cycle in PR3013's matching repairs all 45 missing
dependencies in its optimistic graph. The resulting **single compatible perfect matching**
has all 4,992 required source-to-target dependencies in PR2996's optimistic
all-intermediate-completion graph. In fact, every target receives all 104 source
supports in that graph. This answers PR3013's matching-coherent handoff with an
explicit witness rather than the union of incompatible matchings.

This is a passing necessary test, not a correction program or a new kappa.
Matching coherence does not imply consistency of intermediate frames. Different
contacts in the graph can require incompatible choices in the same helper's
flag. Chronology, scalar coefficients, dirty restoration and the complete
physical/consumer bill are still missing. The reported stronger program-level
216/219/234 lifetime floors are not contradicted or replayed here.

## Exact delta and certificate

Use the same prescribed 208 departure and 208 arrival slots as PR2981, indexed
by `2*s+i` and `2*t+j`. All fixed covers and original X/Y data paths are unchanged.
The control is PR3013 at `504dc9a15f7a874a47564cdf3ae6857bbbc8d000`.
[CONTROL.json](CONTROL.json) is its byte-identical WITNESS.json, authenticated by
[SOURCES.json](SOURCES.json). The cycle is `(139,154,182,179)`, assigning each
departure the next departure's old arrival:

| Departure slot | Old arrival | New arrival |
|---:|---:|---:|
| 139 | 7 | 186 |
| 154 | 186 | 146 |
| 182 | 146 | 171 |
| 179 | 171 | 7 |

Every other assignment stays fixed. The checker reconstructs all prescribed
binary frames, verifies all 208 containment edges and the bijection, then checks
the literal cycle identity. [WITNESS.json](WITNESS.json) retains the cycle and the
complete new pairing. No solver is needed for replay.

The important new dimension-four contact is between helper slots 139 and 91.
Their departure planes have bases `[113,288]` and `[2,424]`. The dimension-four
space with basis `[113,288,2,424]` lies in both new arrival planes B186 and B8,
but not in helper 139's old arrival plane B7. The contact connects the old
`{83,91}` component to the large dimension-four component. The matching into
Y40 itself is unchanged: departure slots 17 and 83 still use arrivals 81 and 80.
Thus repairing the bottleneck need not change its immediate incoming edges.
The complete support computation, not this one contact alone, certifies that
no required dependency elsewhere is lost.

[RESULT.json](RESULT.json) records all 104 target masks, all missing-required
masks and the eight layer summaries for each of these calibrated cases:

| Matching | Helpers | Missing required dependencies |
|---|---:|---:|
| PR2981 published pairing | 208 | 3,095 |
| PR3013 control | 208 | 45, all at Y40 |
| This four-edge cycle | 208 | 0 |

The control's Y40 support is exactly `{X8,X41,X45}`. The new support is every
source at every target. There is no optimality or minimum-edit claim. A bounded
proposal experiment used six CP-SAT solves with matching-coherent cut clauses;
the sixth candidate passed the original, unmodified dependency test. Solver
output and search completeness are not premises of the certificate. The search
used CPython 3.12.15 and OR-Tools 9.15.6755 on Linux/WSL2 x86_64.

## What the graph proves

Retain PR2996's X-only monotone common-chart contract. X is immutable, Y is
unread, helpers have independent arbitrary dirty entrances, and scalar mixing
requires equal current frames. The correction may not read the original
channel's helpers or use additional storage; no descending transports are
allowed. At departure slot a and assigned arrival b,
write L for its source line, A for its dimension-two departure plane, B for its
dimension-seven arrival plane and H for its target hyperplane. The fixed frames
have dimensions 1, 2, 7 and 8. Intermediate frames range over `[A,B]` at each
dimension from three through six.

Two intervals `[A,B]` and `[C,D]` admit a common dimension-d frame exactly when

```
A <= D, C <= B, dim(A+C) <= d <= dim(B intersect D).
```

Any common frame contains A+C and lies in B intersect D. Conversely, extend a
basis of A+C inside that intersection to dimension d. This proves the test.
For fixed layers the interval is a singleton, with the same criterion.

Give each helper upward edges through dimensions one to eight. Give helpers
bidirectional contacts whenever the criterion permits a common frame. Inject
each source at every equal frame on its frozen data path, ignoring time. Read
each target at every equal frame on its path. Also allow direct equal-frame X/Y
contacts. Independent dirty coordinates carry no initial X coefficient.
Induction over any legal scalar program confines each X support to this graph:
transport advances along a helper, and equal-frame scalar operations can only
combine already reachable supports. A missing path would force a coefficient
to zero. A present path does not construct that coefficient.

The certificate establishes that one matching passes this necessary test. It
removes the need to pool the 2,309 possible matching edges to obtain complete
relaxed support, but it does not supply mutually consistent full flags. The
graph still grants each contact independently, free mixing, all source snapshots,
arbitrary interleaving and no dirty-restoration charge. This result neither
admits a supplier nor proves that 208 lifetimes can implement the correction.

## Reproduce and evidence

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-coherent-support-witness
```

The registered replay runs both algorithms and the behavioral controls. Direct
optimized checks also work from a read-only, Git-free source export:

```sh
python3 -I -O -Werror -B research/p104-coherent-support-witness/verify.py
python3 -I -O -Werror -B research/p104-coherent-support-witness/verify.py --literal
python3 -I -O -Werror -B research/p104-coherent-support-witness/test_verify.py
```

The success marker is `PASS_P104_COHERENT_SUPPORT`, with
`changed_pairs=4 required=4992 missing=0 no_new_kappa`. Add `--emit` to either
verifier mode to regenerate the complete receipt on stdout.

The primary algorithm uses exact subspace cardinalities and layer-component
support propagation. The second enumerates all 374 quotient subspaces between
each departure and arrival plane, indexes literal common frames, and runs a
separate directed BFS from each source. Their complete contact relations and
receipts agree. They share parsing, prescribed-frame reconstruction and Gram
arithmetic, so this is not two independent complete supplier audits. The 120
positive E8 lines and 104 ordered retained roots reconstruct I-G/2 over the
rationals; its 4,992 nonzero entries bind to the ordered data endpoints.

Controls cover both actual CLIs, the 3,095/45-missing predecessors, exact edits,
schema/bijection failures, exhaustive interval contacts in F2^3, forward versus
backward relay timing, source and control corruption, false receipt fields,
duplicate keys, a contact-dropping mutant, the new bridge, and a read-only
Git-free export. Explicit acceptance checks remain active with `-O`.

Local registered CPython 3.12.15 replay and optimized CPython 3.13.5 checks pass
on Linux/WSL2. Ruff and warnings-as-errors source compilation cover all three
Python files. No native/global/outer replay, complete physical invoice,
all-size theorem, independent human review, formal-kernel proof or hosted-CI
conclusion is claimed. The selected record and frozen predecessor inputs remain
unchanged. Exact sources, scope and freshness are in SOURCES.json and TASK.json.

## Open next questions

Can a stronger contact-consistency or chronological test reject or realize this
named passing matching? Start with the dimension-four component, requiring all
contacts involving a helper to agree on its single frame at that dimension.
Then check the whole nested flag and time order rather than independent pairwise
contacts. This matters because support completeness in the relaxed graph is
strictly weaker than the correction identity. Coefficients, arbitrary dirty
restoration and the full consumer bill remain blockers. The reported stronger
lifetime floors must remain part of that assessment.

Family decision: finish this matching witness and stop. The favorable necessary
test is not a reason to expand into scalar/native synthesis or another matching
census. No missing implementation cost is set to zero. The structured handoff is
in TASK.json and the canonical investigation is [discussion #2245][thread].

## Credit and engineering notes

Nick Petalas. Apache-2.0. This extends Nick Petalas/PR3013's matching-coherent
handoff, PR2996's interval dependency test and PR2981/2920/2909/2896's fixed
covers. Bitmap/path primitives and the quotient-frame oracle are adapted from
PR3013 with that attribution retained in the source. New here are the passing
four-edge cycle, the bridge certificate and the separate per-source BFS replay.
Credit Arham Tahir/PR2997 for the complementary fixed-full-flag audit, Adam
Gall/PR2090 and Jeremy Diviney/PR2113 for information-flow work, Sudarsh
Chaturvedi/PR2924 and Sagar Thakrar for the lifetime-floor handoff, Hiroki
Kumazaki/PR2889/2353, ywz65/PR2614, Arham Tahir/PR2675/2682 and Philippe Van
Velzen for the monotone, endpoint, budget and relay lineage. Retain Rohan
Arun/PR1972, Chafik Boukhalfa/PR1991, Adam Gall/PR1940, Josie Elliston/PR1071,
Ali Romman/PR1125 and their geometry/native/compiler predecessors.

Build the Lever changed the deliverable to a search-free certificate and replay.
Prove It Works required literal contact enumeration, a separate directed BFS and
rejecting controls instead of relying on the solver's nomination.

Power of Ten inspection covers the three new Python files. Functions fit within
60 physical lines. Loops are bounded by 4,058 input events, 104 endpoints, 208
helpers, eight layers, 512 binary points or 374 quotient subspaces. Each BFS
visits at most 1,664 nodes per source. The F2^3 contact control enumerates 16
subspaces. Inputs are capped at 2 MB; child processes have 25-second timeouts.
Source authentication precedes mathematical processing. Tests, Ruff and
warnings-as-errors compilation supply local diagnostics without changing shared
configuration.

Rule 3 deviation: Python allocates managed objects during verification. Fixed
input domains bound all collections; a literal layer has at most `208*155`
frame entries with 208-bit host masks. A resident service would need preallocated
storage and a separate resource audit. Rules 8/9 deviation: fixed package-local
files are loaded with runpy, and JSON has a duplicate-key hook. There is no
arbitrary plugin or executable predecessor dependency. The source-export and
mutant controls exercise these fixed targets. A plugin service would need a
static interface and separate authority audit. No subagent review capability
was available; the checks above are local algorithmic controls, not independent
human review.

[thread]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18979257
