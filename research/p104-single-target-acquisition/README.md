# Exact acquisition minima for all 104 individual P104 targets

In the fixed-source-path, X-only monotone-helper model of PR2393 and PR2496,
the minimum number of new dirty helper lifetimes needed to correct **one**
P104 target has the following complete distribution:

| Minimum lifetimes | Number of targets |
| ---: | ---: |
| 37 | 1 |
| 38 | 4 |
| 39 | 5 |
| 40 | 12 |
| 41 | 2 |
| 47 | 24 |
| 48 | 56 |

Each of the 104 entries has a matching all-allowed-frame antichain lower
certificate and a chronological, dirty-restored upper construction. The table
extends the credited results **Y0 = 48** ([PR2393](https://github.com/CrocSwap/integer-mult-bounds/pull/2393))
and **Y2 = 39** ([PR2496](https://github.com/CrocSwap/integer-mult-bounds/pull/2496));
those two entries are controls, not new minimum claims. The complete target
lists and proof are in [PROOF.md](PROOF.md). [CERTIFICATE.json](CERTIFICATE.json)
gives every source witness, capture cut and frame basis.

The new minimum occurs at **Y53**, which needs exactly **37** helpers: 36
initial-line acquisitions plus one carrier that acquires twelve sources at
cuts 0, 542, 711 and 830. Its word adds **170 scalar ADDs**, **114 nested
transports**, and **333 boundary rank units**, with profile
`76 H1 + H2 + H3 + 36 H7`. All helpers finish at FULL with their initial
logical values restored. The other 103 targets retain the original G/2 updates.

This is a scoped proof and finite construction table, **not a complete supplier
or a new kappa**. These are separate single-target optima. Their sum, 4,762,
is not a lower bound for a shared multi-target network. In particular, the
1,031-lifetime relay-v2 construction and the multi-target sharing results do
not contradict this table. Helper lifetimes are not simultaneous physical
stock; dimension-gap rank mass is not recursive excess cost.

## What is checked

The primary verifier reconstructs the 104 roots, their ordinary Gram matrix,
and all source-frame episodes from the two unchanged main-branch inputs. It
checks 112,600 frame-pair comparisons in the lower witnesses. For every target
it expands the compact capture paths into an explicit word inserted among all
4,058 original events, then checks every coefficient over all `280 + L_t`
independent inputs, all frame transitions, eight private-copy lifetimes,
restoration and the complete added local invoice. The 104 endpoints contain
11,039,672 coefficients, including zeros.

A separately written checker uses enumerated subspaces, the full 240-root
construction, and dense scaled-integer rows instead of echelon frames and
sparse rational rows. It replays all 104 full original words with their
corrections and agrees on every endpoint. Both implementations were written
in the same AI-assisted session; this is not independent human review.

Eight rejecting controls cover repeated or comparable lower witnesses,
premature late captures, missing captures, missing dirty compensation, a
wrong capture coefficient, missing cleanup and undercharged transport. Each
must fail at its intended semantic predicate. An equivalent-basis presentation
passes. Behavioral tests also check source and receipt integrity, Git-free
read-only replay, exclusive output and independent-checker mutations.

## Reproduce

CPython 3.12, standard library only; tested with 3.12.3. Default replays are
read-only, Git-free and network-free. The package runner also authenticates
Git provenance. Exact input hashes and predecessor heads are in
[SOURCES.json](SOURCES.json).

```sh
python3 -I -B scripts/research_package.py --package research/p104-single-target-acquisition
```

The registered replay, including both complete arithmetic implementations,
regeneration and the five behavioral groups, passed locally. Allow about one
minute for this small standard-library replay; timing is not part of the certificate.
The primary line is:

```text
PASS_P104_SINGLE_TARGET_ACQUISITION targets=104 min=37 max=48 matched=104 controls=8 no_new_kappa
```

The second checker reports
`PASS_P104_SINGLE_TARGET_DENSE targets=104 coefficients=11039672`.
Direct checks and complete certificate regeneration:

```sh
python3 -I -O -B research/p104-single-target-acquisition/verify.py --regenerate
python3 -I -O -B research/p104-single-target-acquisition/independent.py
python3 -I -B research/p104-single-target-acquisition/test_verify.py
```

To inspect one literal insertion word, choose a new output file:

```sh
python3 -I -B research/p104-single-target-acquisition/verify.py --emit-target 53 --out y53-word.json
```

Cuts count completed original events; insertions at cut `c` run before original
event `c`. The emitter refuses to overwrite an existing file. The finite search
in `build.py` is reproducible but is not imported by either checker. Optimality
comes from matched certificates and the causal proof, not from trusting search
exhaustiveness. The individual profiles and ADD counts are in
[RESULT.json](RESULT.json); only lifetime count and its nine-per-lifetime
boundary-rank corollary are claimed optimal.

## Scope and relation to other work

Original X registers are immutable logical sources on their retained frame
paths. New helpers start with independent arbitrary dirt in ZERO and move only
up nested frames; extra operations are same-frame rational additions from X
to a helper, between helpers, and from a helper into the single chosen target.
Targets and original G/Q/D/private registers cannot be read by the correction;
original registers cannot be repurposed, and no new allocation, erasure, reset
or descending transport is allowed. The lower bound permits arbitrary helper
relays, repeated reads, cancellation and retiming within this model. Each upper
word uses no helper-to-helper relays and retains every original event.

Philippe Van Velzen's [window-bill finding in Discussion2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18949693)
already identified the 48 targets with later-contained-frame access. This
contribution classifies their exact single-target minima and supplies complete
matching certificates. PR2504's isolated Y2-exclusive group, PR2521's cross-group
three-target construction and PR2548's pooled collectors have different target
sets and sharing contracts. PR2594 audits a joint relay word's growth. None of
those joint constructions is reverified or priced here. PR2604 audits an
arrival-shape pricing premise; PR2614 justifies a joint departure floor and
composes relay-v2. Those are also distinct from the individual minima. The claim is in
[Discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18953046).

Native phases, intrinsic physical lowering, scalar/address costs, a global
owner/idle/residual bill, backward orientation, physical precision/tape,
all-size admission and the inherited private-copy disposal contract remain
open. No selected-frontier cold replay or formal-kernel proof was run.

The final upstream checkpoint is revision 5, main
`b4560d9e7216f72b73c5aa940ac099c05e33ccf9`. Its family expansion gate was read;
the scientific inputs and selected record are unchanged. This completed local
module is retained without starting another dependent construction round. Its
original revision-4 task/source provenance remains pinned in TASK/SOURCES.
Any follow-up below first needs a joint consumer and complete budget, including
unknown physical and hosting costs.

## Open next questions

Can Y53's twelve-source chain be used in a named two-target correction without
losing its advantage to collector separation and dirty restoration? Start by
intersecting its actual capture frames with one other target's endpoint and
checking the two demand rows at the common frames. The blocker is joint demand
rank and causal routing; the single-target count alone does not price sharing.

Can the source-family antichains be combined with a joint output-rank inequality
to obtain a useful multi-target lower bound? Start with exactly two targets and
a capacity certificate that explicitly permits a helper to serve both. Adding
the entries of this table is invalid. These questions and their blockers are
also recorded in [TASK.json](TASK.json).

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0. Credit ywz65 / PR2496 for the all-allowed-frame antichain argument
and Y2 chronological acquisition construction, and PR2460 for its late-access
handoff; this account's PR2393 for the Y0 source-acquisition argument and dirty
compensation construction; Ross Richardson / PR2445 for two-target sharing;
Hiroki Kumazaki / PR2353 for the monotone relay model; and Philippe Van Velzen
for the global reachability-window finding and shared relay constructions.
Rohan Arun / PR1972 supplies the original word; Chafik Boukhalfa / PR1991 its
native realization; Adam Gall / PR1940 the schedule; Josie Elliston / PR1071,
Ali Romman / PR1125 and the retained PR968/717/446/595/620 lineage supply the
fixture and geometry. No predecessor executable is copied or imported.
