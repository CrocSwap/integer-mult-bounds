# R439 frame 267: 21 ADDs become 12, with an exact class minimum

**Finite bit-supplier construction; no new kappa.** Replace PR589's complete
six-register phase-A frame-267 circuit and its literal reverse cleanup.
The local word saves **18 ADDs: 24,305 -> 24,287**. The new circuit preserves
its complete positive integer transfer and attains the **12-ADD minimum for
that fixed six-wire integer transfer**, including repeated destination writes.
The reverse positive matrix is entrywise no larger.

Research base: **`91a2094f2e022930069e8cfdc810a3ea1b81cd09`**. Its selected
certificate is PR799 with PR589 on PR555, conditional
**kappa = 0.001661634653669567**, complex-bound. We followed the selected
record to its actual assembly and maintainer review. Older supplier README
frontiers are historical. This package changes no selected source or pointer.

## Reproduce

Python 3.11+ and the standard library suffice:

```sh
python3 -I -B research/r439-frame267-seed01/verify.py
```

Expected final line:

```
PASS_R439_FRAME267 gates=21->12 native_adds=24305->24287 columns=661 rank_mass=5129 controls=8
```

This recomputes both minimum certificates, validates every recipe metadata
field, checks the full exact integer matrices and 64 local Boolean inputs,
runs the unchanged owning E8/frame/interface checker on all 661 symbolic
dirty-input columns, exports both words, and independently interprets every
native record. It checks all fields of `CERTIFICATE.json` and rejects eight
mathematical controls. `--output /absolute/new/directory` preserves both words
and their records; an existing output directory is refused. Default replay
uses temporary outputs and changes no repository files. `--write-certificate`
is explicit regeneration of this package's certificate only.

For the fresh native legality and 5/9/11-stage replay (C++17 and Boost):

```sh
BOOST_INCLUDE=/path/to/boost python3 -I -B research/r439-frame267-seed01/native.py
python3 -I -B research/r439-frame267-seed01/test_package.py -v
```

The native command compiles each unchanged checker once, replays both words,
checks **883 / 1,327 / 1,549 formal columns**, rejects all **96 omitted-bridge
controls**, and compares all proof-relevant receipt fields. Only elapsed time
and the temporary input path are normalized. Both words retain the paid rank
profile, nine copies, 439 helpers, and 93-bit payload under the 104-bit cap.
`NATIVE-CERTIFICATE.json` retains the receipts; `VALIDATION.md` records execution
and the repository-wide check separately. Gzip container bytes are not used
as regenerated mathematical equality: the verifier binds canonical decoded
words and actual exported record bytes.

## Exact scope and evidence

See [PROOF.md](PROOF.md) for the graph argument, literal circuit, complete local
cost and inherited assumptions. `search.py` exhausts 416,508 states / 2,366,680
edges. The separately written flat-matrix breadth-first checker fully expands
depths 0 through 11 and first reaches identity at depth 12. This establishes a
minimum only for this fixed positive integer matrix and six ordered wires.
It does not establish unrestricted XOR optimality, a new exponent, or the
full multiplication theorem. No global hosted invoice or outer assembly is
newly certified.

Controls drop a circuit gate, reverse an operand, insert an F2-neutral but
positively expensive pair, drop cleanup, keep a scalar-valid but nonliteral
old cleanup, lower the frame illegally, omit dirty compensation, and drop an
exported ADD. Stale cleanup is explicitly scalar-valid and rejected by H4.
The package tests additionally exercise source/certificate corruption, invalid
gates, minimum under/overclaims, preserved existing outputs, and optimized
Python in a minimal offline directory whose path contains spaces.

## Assignment, prior work and overlap

The first OS-random draw was **01** (bit supplier). It selects quad 1 among
60 six-register phase-A frames. `CLAIM.json` records three considered tasks,
the narrow scope, timing, first capped experiment and completed coverage.
GitHub returned no pinned coordination issue, so the claim is local.

**Gareth Davidson's PR904** (head `883a0bdf7792693e57c16be660824b57aacfbe05`)
contains two disjoint four-wire substitutions inside this same frame, saving
two A ADDs (21 -> 19). This full-frame witness saves nine (21 -> 12), **seven
more in A and fourteen more including cleanup on this frame**. The source-bound
comparison is recorded in `OVERLAP.json`; no combined whole-word saving with
PR904 is claimed. Our method exhausts a different full-six-wire positive
factorization class, rather than sampling additional small windows.

**mtpsl's PR691** supplies the related integer-transfer/reverse-domination
argument for historical R420 quad 13; this package adapts its finite word and
record verifier with credit. **Hao Yan's PR823** treats historical R480 quad 1,
a different matrix. **Sagar Thakrar's PR728 / Ryan Haines' PR792** concern R439
mini-nodes, not this frame. **PR886** closes fixed-word frame-only improvement;
this result changes the gate sequence while preserving frame paths. **PR848**
records the old H2 barrier for D sharing; D is untouched here. **PR915** changes
D under a semantic boundary; those changes and savings are not composed here.

Credit remains with eumemic (PR543/555), DreamingOfClouds (PR545/589/510), Dylan
Crow (exporter/native lineage), Zhihao Chen (scalar interface), DaysSky (hosting),
and all retained predecessors. The native wrapper adapts Ali Romman's PR688
wrapper from current main. Source hashes and Git blobs are in `SOURCES.json`;
see `NOTICE.md` for detailed attribution.

Prepared by **Ross Richardson (@RossRichardson)** with substantial **OpenAI
Codex assistance** in research, code, proof analysis and verification. One AI
agent performed the work; no independent human review is claimed. Apache-2.0.
