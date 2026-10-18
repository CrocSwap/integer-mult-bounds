# Exact selected-word idle-axis relaxation and a physical counterexample

**No improved κ.** This package proves the exact optimum of PR1324's structural
axis-assignment rule on the selected PR1094 inputs, then exhibits an exact
counterexample to physical admission of the attaining witness. The inherited
controller, invoice and assembly checks accept it; a check retaining all eight
physical data streams rejects it. PR1324 was closed for the same underlying
cross-family issue during this investigation; that prior finding is credited
below. The selected record is unchanged.

The 4,866 eligible rank-48 children form 1,792 replica/port groups. Their complete
assignment domain reduces to nine compatibility patterns. Attaining vectors
saturate every prefix bound and minimize the formal paid moment for **every
real `0<a<1`**. A separate integral max-flow/min-cut checker tests all 1,049
labelled rank vectors: 795 feasible, 254 infeasible. The optimum is over the
stated structural relaxation, which does not imply operator preservation.

| Selected-word domain | Formal native κ price | Meaning |
|---|---:|---|
| Original PR1094 | 0.001672660197076918 | Selected baseline |
| PR1252 disjoint pairs | 0.001672846574134982 | Predecessor overlay price; semantic concern applies |
| PR1276 disjoint stars | 0.001672987659462603 | Predecessor structural lead |
| **All declared simultaneous assignments** | **0.001673074238324615** | **Exact relaxation optimum; exhibited witness invalid** |
| PR1276 rank-only relaxation | 0.001673151843213755 | Unattainable under the declared structural rule |

Exactly 264 four-child groups improve formally on the star profile. The full
paid histogram of the relaxed optimum is

```
{1:349604, 2:60192, 3:62585, 4:20448, 5:11808, 7:7, 8:1152,
 39:264, 42:532, 45:765, 48:684, 51:2621}
```

Its mass is 1,041,408 and deficit 5,120 at `m=73,W=14336`. Both rational moment
engines price the complex endpoint as `0.001675878106811694717226`; the retained
bit endpoint is larger. The formal conservative κ is `0.001673074235472000`.
All endpoint signs and all 47 outer constraints are checked. These prices are
upper ceilings for any operator-preserving subdomain under the same hypotheses;
they are not new integer multiplication bounds.

## Why the attaining witness fails

At replica 0, port 0, cover identity and Fourier character `u=32`, the actual
selected schedule gives baseline `i*I_8`. The proposed assignment changes
`(Y0,Y0)` to `-1`, adds `-1-i` at `(Y1,Y0)`, and changes `(Y3,Y3)` to `1`.
An input on Y0 therefore leaks to Y1. A one-axis move, from child 8 to child 12,
also passes the structural rule and fails the physical test.

[stream_check.py](stream_check.py) uses exact Gaussian integers, the actual
emitted event order and all 30 relevant hosted helper occurrences, including
those on other replicas. It respects each factor's physical family. The
baseline passes 147 mode checks; the two invalid overlays are rejected.
These finite positive checks support the implementation, while one exact
failing mode establishes each counterexample.

The inherited flattened check combines different streams and treats address
translations as Fourier-label shifts. Under the source convention, address
translations instead have scalar Fourier multipliers. Its polynomial equality
is retained only as a reproducible demonstration of the missing implication.
[PROOF.md](PROOF.md) gives the full optimization proof and operator calculation.
We do not prove that every nontrivial assignment fails, or exclude another
physical assignment with the same optimum rank histogram.

## Reproduce

Python 3.12 or later, standard library only:

```sh
python3 -I -B research/selected1094-idle-reassignment/verify.py --full --work /tmp/idle-relaxation-new
python3 -I -B research/selected1094-idle-reassignment/test_package.py
python3 -I -B scripts/research_package.py --package research/selected1094-idle-reassignment
```

The output directory must be new. Every run checks the structural optimum,
independent flows, exact prices and the physical counterexample. `--full` also
reproduces legacy acceptance of the invalid witness with 15 controller, 69
assembly and 12 bit controls. The registered hook runs this full demonstration
and eight test groups. The final receipt explicitly says `admitted=false`.
Optimized `-O` is supported for the default run; the inherited full harness
requires assertions. The pricing subprocess always enables assertions.

[SOURCES.json](SOURCES.json) pins twelve live inputs, including the original
operator convention. [LEGACY-PATCHES.json](LEGACY-PATCHES.json) records all
scratch-only source adaptations. Original local/native and bit artifacts are
reused, not rebuilt. [EXPECTED.json](EXPECTED.json) binds the complete result;
[VALIDATION.md](VALIDATION.md) records commands, environments and receipts.
The proof is written, not Lean-checked. No selected-frontier or ancestry edits.

## Scope and overlap

One OS draw selected `incumbent-optimization / selected-packing`, nonce
`3dc042161f3eb4eb1e4768c6bbc6e12f`, scope key `2eb6f6918b10e182033b`, priority
revision 2. Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
[TASK.json](TASK.json) records the evidence-driven scope change from attempted
admission to exact relaxation plus obstruction; there was no new draw.
Submission: [PR 1387](https://github.com/CrocSwap/integer-mult-bounds/pull/1387).
Coordination: [Discussion 1339](https://github.com/CrocSwap/integer-mult-bounds/discussions/1339).
[OVERLAP.json](OVERLAP.json) records snapshots and exact predecessor heads.

PR1276 already solves disjoint stars and gives a broader rank-only ceiling.
This completes the intermediate simultaneous-assignment domain on the selected
word. Discussion1332/PR1343's single whole-helper relocation census, PR1129/1175's
fixed-inventory owner optimization and PR1240's wider ceiling have different
objects. The operator failure itself is not claimed as a new discovery:
PR1324's 2026-10-13 23:22:56 UTC closure comment already credits Rohan Arun for
identifying the cross-family problem. This package adds the selected-word
exact optimum, explicit matrices and reproducible acceptance/rejection checks.

The theorem excludes new axes or bases, relaxed dot-product restrictions,
changes to hosted children, owner maps, local words, schedules, replica counts
and outer recipes. The inherited all-size/compiler, common-label/mutable-source,
precision/tape, recovery, analytic transfer and bit H1–H5 assumptions are not
newly proved. Passing the legacy checks cannot repair the concrete obstruction.

## Open next questions

* **Optimize the operator-preserving subdomain.** Start with the nine-pattern
  structural bound and enforce the actual eight-stream matrix identities.
  The blocker is a complete symbolic equality criterion over all Fourier
  characters, rather than a flattened scalar product. This could determine
  whether any of the formal profile gain is realizable with the fixed schedule.
* **Add semantic rejection to the predecessor controller interface.** Use the
  one-axis witness as a regression and pin the intended data-stream contract.
  Broader integration requires agreement on the interface and complete source
  replay; this contribution supplies a local check and does not modify others'
  packages or promote a result.

## Credit and license

Gonzalo-Mier: [PR1252](https://github.com/CrocSwap/integer-mult-bounds/pull/1252),
head `1b9db2faf82b8866b0bb0164501c9a627c7dca9b`, pair mechanism and overlay protocol.
Guéorgui Maissouradze / PatatePatatePatate:
[PR1276](https://github.com/CrocSwap/integer-mult-bounds/pull/1276), head
`588425ebfc307dea3a94db9ba4bd4a3c74141b55`, star lead and rank-only ceiling.
Jeremy Kothe: [PR1324](https://github.com/CrocSwap/integer-mult-bounds/pull/1324),
head `43c19465dc7fd89b991612887c2cdb5ccf57925e`, simultaneous structural rule and
explicit withdrawal; its closure acknowledgment credits Rohan Arun
([PR1286](https://github.com/CrocSwap/integer-mult-bounds/pull/1286)).
Credit also Rohan Arun and Jeremy Kothe's selected PR1094 word/map; Josie
Elliston's owner audit; Hao Yan and the retained geometry/compiler/bit lineage;
Douglas Colkitt's review and PR1240 ceiling; and PR1255's scoped phase audit.
Original notices remain in the unmodified archives.

New work by Gareth Davidson (@bitplane), with substantial OpenAI Codex
assistance; Apache-2.0. No subagents, independent human review or literature
priority is claimed.
