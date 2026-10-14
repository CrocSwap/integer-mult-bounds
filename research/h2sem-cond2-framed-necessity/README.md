# H2-sem condition 2 is not necessary for the F4 framed endpoint

**Adversarial interface audit; no new κ.** Complements open
[PR1782](https://github.com/CrocSwap/integer-mult-bounds/pull/1782) (H2-sem
admission of the PR848 copy-path wraps; F4 recorded as a boundary probe) and
[PR1805](https://github.com/CrocSwap/integer-mult-bounds/pull/1805) (priced
those admitted wraps). This package answers PR1782's open question: on the
exact F4 target-feeding-helper wrap, is H2-sem condition 2 required for the
framed dirty endpoint?

## Result

For the seed-42 best pair `277 → 434` on the pinned selected R439 word:

| Check | F4 outcome |
| --- | --- |
| H2-sem condition 1 (zero-frame Y/H operands) | pass |
| H2-sem condition 2 (no target→helper/source) | **fail** |
| H2-sem condition 3 / semantic N = raw K | pass (661 columns) |
| Frames at D/A cut | equal to baseline |
| Framed sectional endpoint `(x,y,h)→(x,y+x,h)` | exact |
| Literal forward/reverse endpoint | exact |
| Virtual original-D splice (PR1194 bridge premise) | all H1–H5/U/J/K/C pass |
| Paid profile / rank mass | unchanged / **5129** |

**Claim:** on this instance, condition 2 is not necessary for the framed endpoint
substitution conclusion. F4 still fails the published H2-sem contract and the
inherited H1 flag; this is a necessity falsification, not an admission. No
general lemma dropping condition 2 for every wrap is claimed. Written argument:
[PROOF.md](PROOF.md).

### Exact costs (baseline → F4)

| Quantity | Baseline | F4 |
| --- | ---: | ---: |
| Whole-word ADDs | 24305 | 24374 (+69) |
| D ADDs / source reads | 18085 | 18154 (+69) |
| D gates | 111 | 113 |
| Rank mass | 5129 | 5129 |
| F / B | 49347 / 1113070 | 50535 / 2995586 |
| Local / nine-stage bits | 93 / 177 | 96 / 183 (guards still strict) |

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/h2sem-cond2-framed-necessity/verify.py
python3.12 -I -O -B research/h2sem-cond2-framed-necessity/verify.py
python3.12 scripts/research_package.py --package research/h2sem-cond2-framed-necessity
```

Expected:

```text
PASS_H2SEM_COND2_FRAMED_NECESSITY pair=277->434 cond2=false endpoint=exact profile_mass=5129 adds=24305->24374 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/h2sem-cond2-framed-necessity outcome=completed
```

`test_package.py` relocates the package and rejects a mutated source pin and a
mutated expected receipt. Full selected cold replay, Lean, and the multiplication
theorem were not rerun.

## Scope limits

No new kappa, frontier, native/hosted admission, or compiler/tape claim. Does
not re-price the PR848/PR1805 admitted wraps. Does not weaken PR1194's published
hypotheses; it only shows condition 2 is independent of the endpoint identity on
this F4 witness. Controls: unrestored feed and late restore each break condition 3;
the C1 helper-temp wrap on the same pair remains the admitted contrast.

## Open next questions

1. **Is there a general replacement for condition 2 that still implies the
   block-triangular step of PR1194?** Why it matters: a justified weakening would
   enlarge the admissible wrap class beyond helper-temp conjugations. First step:
   isolate the exact matrix identity H1 supplies in the W0 factorization and
   state a D-local substitute. Blocked by: need a proof that covers every
   zero-frame D, not one F4 witness.
2. **Do other target-feedback shapes preserve the endpoint while changing the
   paid profile?** Why it matters: only then could dropping condition 2 interact
   with κ. First step: enumerate short target-temp conjugations closed before
   each singleton target write. Blocked by: no favorable completed bill is known;
   F4 itself raises ADD count.

## Credit

Credit **Aaron Wang / navinor (PR1782)** for the F4 probe shape and the open
necessity question; **woklerx (PR1194)** for H2-sem and the chronological
bridge; **PR848** for the pair census and C1 contrast; **DreamingOfClouds
(PR589)** and **eumemic (PR555)** for the R439 word; **PR1805** for the priced
admitted-wrap companion (not consumed as code). Prepared by **Wentao Li**
([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review claimed.
