# Restored dirty-carrier delivery for the P104 32-chain schedule

**Draft partial construction. No new kappa or admitted P104 supplier.**

PR1940 supplies a chronological 32-chain delivery schedule but assumes exact
query copies and leaves dirty-copy formation/restoration open. This package
implements its delivery with **32 arbitrary dirty width-nine carriers**,
one reusable private query-copy slot, and eight supplied query parents.
All dirty carrier inputs are preserved through their required endpoint
transports. No dirty carrier is cleared or treated as zero.

The construction uses ordinary dirty-input cancellation: before targets leave
frame zero, subtract each assigned carrier's input from them. Populate the
carrier with its query at the singleton survivor frame, deliver along the
pinned chains, then remove the query at full frame using its parent. The
novel claim is this concrete frame-compatible wrapper for the pinned P104
fixture, not the general cancellation trick or the 32-chain theorem.

## Boundary and exact invoice

Eight independent query parents enter at their gather hyperplanes Q_k of
rank eight and exit at full rank nine. The 104 arbitrary targets enter at
frame zero and exit at their rank-eight hyperplanes H_t. All 32 carriers
enter at zero and exit at full rank nine. In normalized chart coordinates:

```
Q_k -> Q_k
Y_t -> Y_t + sum_k D[t,k] Q_k
H_i -> H_i
```

Physical carrier output is the required full-frame transform of its input,
not an untransformed physical identity. The supplied query values need not
be clean or independent of actual future source data, but their formation
and compatibility with a full supplier are outside this package.

| Contribution | Paid profile | Rank mass |
|---|---|---:|
| Eight private query drops | 8 H7 | 56 |
| Query-parent completion | 8 H1 | 8 |
| Dirty carriers, complete lifetimes | 117 H1 + 17 H2 + 19 H3 + 20 H4 | 288 |
| Target lifetimes | 416 H1 + 12 H2 + 24 H3 + 32 H4 + 24 H5 + 12 H6 | 832 |
| Total | 541 H1 + 29 H2 + 43 H3 + 52 H4 + 24 H5 + 12 H6 + 8 H7 | 1184 |

The boundary coverage mass is 8 + 288 + 832 = 1128; the excess is exactly
**COPY56**. There are 896 signed scalar additions (416 precompensations,
32 query injections, 416 deliveries, 32 cleanups), eight private copies,
eight private zero initializations and eight private erasures. The exact
normalized prefix l1 bound is seven relative to the supplied boundary inputs.
Scalar actions, chart adapters, routing and physical memory are not free;
only their counts, not a full compiler allowance, are given here.

PR1940's 24 extra supplied arrays are not a comparator with the same
boundary. Here all 32 delivery arrays are dirty live carriers, while the
eight query parents are retained separately. The parent streams must be
available unchanged in normalized coordinates until full-frame cleanup.
The new carrier demand is **{9: 32}**, not {9: 24}. These are candidate
residual lifetimes; no owner assignment has been proved.

## Evidence and reproduction

```
python3 -I -O -B research/p104-restored-dirty-delivery/verify.py
```

Standard library only; default replay is read-only. Local CPython 3.14.8
checks passed; Python 3.12 and hosted CI are separate until actually run.
The producer checks all 144 arbitrary boundary input columns and exact
binary subspace inclusions. Eight meaningful corruptions are rejected.
A separately written checker uses freely noncommuting invertible chart
symbols, reproduces all endpoint identities and rejects a wrong global
phase. It does not import the producer or upstream geometry checker.
This proves cancellation conditional on the declared chart realization;
it is not a concrete Gaussian/Clifford compiler replay.

The raw predecessor inputs are pinned in UPSTREAM.json and used at runtime;
SOURCES.json pins the research catalogue and selected record as provenance.
The frozen schedule is credited unchanged. Verification does not modify
selected-result.json, the incumbent supplier, or predecessor packages.

## Remaining admission obligations

No complete P104 gather/side-correction word is supplied. In particular,
targets cannot silently revisit smaller frames after the staged delivery.
No claim that these 32 width-nine lifetimes fit the global owner windows,
that the complete moment improves, or that the bit supplier supports a new
kappa is made. Concrete phase normalization, adapters, hosting, precision,
tape and inherited all-size analytic obligations remain. Finite checks are
not independent human review or a formal multiplication theorem.

## Open next questions

1. Build a complete P104 gather and side-correction word around this wrapper;
   first check every target contact against its evolving frame. This is the
   immediate blocker to a full supplier profile.
2. Price and host the resulting residuals, including all 32 width-nine
   carriers, in chronological owner windows. This determines whether COPY56
   survives as an actual moment gain.
3. Extend the native emitter and replay concrete Gaussian charts, including
   adapter/global-phase mutation controls. Free chart algebra does not
   establish that compiler implementation.

Structured versions are in TASK.json. This draft remains partial until the
full construction and relevant admission checks exist.

## Attribution and overlap

Adam Gall / PR1940, exact head
`a9b7dfe2809092a9a4c90784d12bb60061e995e8`: the unchanged 32-chain chronological
witness and its replay code. Josie Elliston / PR1071: the exact P104 fixture,
bi-frame decoder and survivor geometry. Ali Romman / PR1125: the prior
32-path lower bound. Their original assistance notices and earlier lineage
are retained in NOTICE.md and the vendored input code.

General dirty cancellation is standard and is not claimed new; PR673's
dirty-echo work and the inherited helper/cleanup constructions are adjacent
precedents. The targeted overlap search included P104/dirty and dirty/delivery
PR bodies plus recent Discussion metadata; it is not a novelty guarantee.

Prepared by Rohan Arun with substantial OpenAI Codex assistance.
Apache-2.0. No independent human or formal-kernel review is claimed.

## Low-rank channel extension

The package now also constructs and verifies the complete `G/2` channel, including gathering and restoration of all 72 dirty helpers, with COPY56. See [LOWRANK-PROOF.md](LOWRANK-PROOF.md). The `I-G/2` side correction and full supplier are still missing; there is no new kappa. The same verify.py entrypoint checks both constructions.
