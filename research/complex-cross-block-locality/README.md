# Cross-block mixing retains the fixed late-interface moment floor

**Scoped negative result; no new kappa.** Allowing all twelve late complex
blocks to mix their helpers does not reduce their complete helper-growth
moment under the retained fixed-port, monotone-frame contract. This closes
one specific exclusion in Ali Romman's [PR1429](https://github.com/CrocSwap/integer-mult-bounds/pull/1429).
It does not exclude new source versions, earlier output access, extra helpers,
frame descents or changed centres.

For every `0 < s < 1`, the exact minimum for the 96 helpers is

```
328 + 56*2^s + 28*3^s + 20*4^s.
```

The original selected local word attains this value, from the declared late
entries through completion of every helper to rank nine. Arbitrary finite
rational helper programs,
input reassignment and repeated fixed-port reads are permitted. Source and
target interfaces, centre paths and the exterior program are held fixed;
all extra charges are nonnegative. The result concerns recursive rank cost,
not a global scalar-operation optimum or a new multiplication theorem.

## What is new

PR1429 already establishes the per-block floor. Its proof explicitly leaves
cross-block communication outside scope. Here the exact source geometry
confines each high dirty input to its original eight input slots even when
low helpers migrate. Every rank-seven cancellation frame is also confined
to one block and can reach at most one of all 48 outputs. These global
premises let the carrier and retirement arguments survive arbitrary mixing
of the 96 helpers. The [proof](PROOF.md) supplies the all-length argument.

The actual word admits a common boundary before B index 1054 after
deferring 144 commuting correction ADDs. Its 192 source/helper coordinates
are independent. A separate modular replay supplies full-rank witnesses
over two checked primes, so the argument does not assume independence of
arbitrarily chosen asynchronous snapshots.

| Finite evidence | Completed coverage |
| --- | ---: |
| Block support cases, rational ranks and binary spans | 3060 |
| Distinct input-frame pairs | 4560 |
| Foreign high-frame/input tests | 1056 |
| Input-frame/target-entry tests | 4608 |
| Rank-seven cancellation frames | 24 |
| Literal scalar input columns across the twelve blocks | 240 |
| Joint boundary rank, independently checked modulo two primes | 192 |
| Primary semantic rejection controls / independent boundary controls | 10 / 2 |

The primary checker uses rational elimination and binary pivot bases. The
separate implementation imports none of it and uses integer Gram minors,
explicit subspace sets, single-column scalar execution and modular prefix
replay. Both implementations were written by the same AI-assisted author;
this is algorithmic crosschecking, not independent human review. The finite
checks establish the proof's source premises, not a formal theorem about
every possible multiplication algorithm.

## Reproduce

From the repository root, Python 3.12 and its standard library:

```sh
python3.12 scripts/research_package.py --package research/complex-cross-block-locality
```

Expected final line:

```
PASS_REGISTERED_RESEARCH_PACKAGE research/complex-cross-block-locality outcome=negative-result
```

The command checks exact Git/SHA256 source pins, both deterministic receipts,
semantic controls, and package corruption/relocation checks. Direct replays
work with Python 3.10 or later, including optimized execution:

```sh
python3 -I -O -B research/complex-cross-block-locality/verify.py
python3 -I -O -B research/complex-cross-block-locality/independent.py
```

Default replay is read-only. `--record` explicitly regenerates only this
package's receipt. It does not regenerate any predecessor artifact.
The generic registered replay needs the pinned base Git object. Direct
replay also works in a minimal source export containing this package and
the one declared archive. The decompressed canonical word is authenticated
separately from its immutable source archive.

## Scope, sources and assignment

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. At that base, the selected
conditional kappa is `0.001672660197076918`, with the complex supplier
binding. Its certificate, actual construction and review were followed;
the baseline source-binding check was run, not the full cold replay.

The runtime input is the canonical local word in
`research/community-frontier1042-audit/selected-replay.tar.gz`, still used
by the selected PR1094 owner map. Its decompressed SHA256 is
`4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c`.
[SOURCES.json](SOURCES.json) pins the exact base, archive, predecessor head
and consulted proof/extractor. No pending implementation is imported at
runtime. The block extractor is adapted from PR1429 with attribution.

OS assignment seed **33** selected the complex track. The three candidates
were deeper decoder punctures, coefficient-work sharing, and joint late-block
mixing. Nearby work made the first two poor choices. Pair 33 of the sorted
66 block pairs, bases 624/656, was the pilot; the new localization property
then supported the full twelve-block statement. This is an enlarged
interface class, not another random search in a closed scalar neighborhood.
[TASK.json](TASK.json) records the bounded experiment, overlap limits and
[coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1492).

The selected frontier, frozen predecessors and `upstream/` are unchanged.
All-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape, exact recovery, analytic transfer and bit H1-H5 assumptions
remain inherited. A full selected cold replay, native/global admission,
hosted CI and proof-assistant verification are not claimed.

## Open next questions

An additional source version or an earlier target entry can break the
antichain or global output wall. A useful next experiment would specify
one actual earlier target frame or later source value, then recheck the
global premises and charge its complete preparation/continuation cost.
No such replacement interface or favorable complete budget is supplied
here. The precise question and blocker are in [TASK.json](TASK.json).

## Attribution and license

Credit **Ali Romman** for PR1429's fixed-block statement, extractor,
carrier-count proof and retirement argument. Its inspected head is
`591582004d82302268da3b264a6ba5edec1521de`; its pending status is retained.
The joint boundary, global confinement argument and cross-block extension
are this contribution. PR1429's additional PR1319 provider coverage is
not claimed here.

Credit **Jeremy Kothe** for the mutable-leaver/local supplier lineage,
**Rohan Arun** for the k8 slots and PR1094 owner exchanges, **Hao Yan** for
the controller, and **icekylinx**, **Chafik Boukhalfa**, **Jonathan Capalbo**
and the retained source-notice contributors for the underlying construction.
The retained bit supplier is **DreamingOfClouds**' PR589 on **eumemic**'s
PR555. All original archives and notices remain intact.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex**
assistance in derivation, code, proof, checks and writing. New material
is Apache-2.0 under the repository license.
