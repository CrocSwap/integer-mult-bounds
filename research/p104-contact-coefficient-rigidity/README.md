# Two-coefficient rigidity of native frame contractions

**No new κ.** On the exact P104 native word of #6824, none of its **1,466
single-contact frame visits** can be contracted by deleting the intervening
ADD and retuning at most one other existing scalar coefficient, even with
arbitrary invertible rational basis changes at both boundary hubs.

This is an **exhaustive, source-bound algebraic obstruction**. The coefficient
of the compensating ADD, COPY or SCALE ranges over all rational numbers;
there is no bounded coefficient search. The result leaves changed operands,
new scalar gates, three or more coefficient changes, and interior basis
changes open.

## Why this matters

Removing an intermediate contact could merge two paid frame transformations
of ranks `a,b` into one of rank `a+b`, a strict saving for the concave moment
used in the supplier invoice. PR #6835 characterizes boundary hub repairs
without changing that middle scalar program. This package changes the middle
program in a precisely defined class and proves that even arbitrary boundary
repairs cannot rescue those contractions. A useful new attempt must change
more than these two coefficients or use a different operation class.

The predecessor's hub-normal-form theorem, native word and conditional κ
claims remain credited to their authors. The new contribution is the complete
two-event perturbation filter and its exact source certificate, including the
otherwise easy-to-miss case where the compensator has zero original boundary
derivative.

## Result and evidence

| Exact quantity | Value |
|---|---:|
| Source public registers / scalar events | 772 / 15,072 |
| Single-contact visits / distinct deletable ADDs | 1,466 / 1,278 |
| Direction-compatible ordered pairs | 172 |
| Pairs with a zero original compensator derivative | 69 |
| Inconsistent rational boundary equations | 157 |
| Remaining candidate public maps, all singular | 15 |

Every possible deleted ADD has a nonzero effect on the boundary block that
zero/full hub changes preserve. The complete second-event filter leaves 172
pairs. For 157 the exact equation has no solution; for each of the other 15,
`CERTIFICATE.json` contains a nonzero rational null vector. The verifier
rebuilds each changed program and checks that vector against all 772 literal
public output rows.

`PROOF.md` gives the general perturbation identity, proves the filter is
complete, states the exact edit model, and explains why the certificate proves
the obstruction. Positive controls include both a repair by a second parallel
ADD and a repair by a compensator with zero original boundary derivative.
Negative controls reject a damaged source and damage to every one of the 15 actual null vectors. Both time orders of a zero-derivative compensator are tested, together with twelve identities involving nonzero owned overwrite and erasure.

A separately written `independent_audit.py` imports no primary or predecessor checker and reads no frozen certificate. It enumerates complete register traces, checks all ordered compensators, solves the full sparse boundary equations and applies Gaussian elimination to the changed 772-by-772 matrices. It reproduces every count and finds exact rank **771** in all 15 cases. A different agent also reviewed the proof and its hub-replacement premise. See `REVIEW.md` for the actual review boundaries.

## Exact sources and scope

The canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The selected conditional bound at
that base is **κ = 0.003125804**, from #6030. The newer #6833 caller proposes
κ = 0.00337180 and uses this #6824 native word; that pending proposal is not
substituted for the selected result.

The native source is #6824 at
`2a7ca44fbda3abaa4df355b183ed7d7478eef7c1`, canonical payload SHA-256
`d3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821`.
The committed export is retained byte-for-byte from #6835 at
`44316f3e6023a7f8c516360e22e9efd6f0fe48c5`. Both source identities, the
original path, Git blob, compressed-file hash and byte length are recorded in
`retained/SOURCE-PINS.json` and checked without network access.

Only the scalar necessary endpoint condition is needed for the obstruction.
COPY is even allowed to overwrite a nonzero owned coordinate during the
counterfactual calculation; this enlarges the candidate class and therefore
strengthens the impossibility result. Nonzero owned erasure is allowed. The
original source is checked with its strict COPY-zero rule and its frame
legality.

No complete caller, new invoice root, native chart compilation or outer
multiplication theorem is claimed. The selected result and the framework
assumptions `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`
and `analytic_recovery` remain unchanged. The sparse baseline inventory was
inspected; a complete selected-source closure was not materialized or replayed.

## Reproduce

Python 3.12, standard library only; no network, solver, predecessor import or
installed numerical library is needed.

```sh
python3 -I -B research/p104-contact-coefficient-rigidity/verify.py
python3 -I -O -B research/p104-contact-coefficient-rigidity/verify.py
python3 -I -O -B research/p104-contact-coefficient-rigidity/independent_audit.py \
  --word research/p104-contact-coefficient-rigidity/retained/WORD.json.gz
```

Expected marker: `PASS_P104_CONTACT_COEFFICIENT_RIGIDITY`, with
`compatible_pairs=172`, `inconsistent=157`, `literal_singular=15`.
The primary replay takes about 14 seconds locally; the independent full-matrix replay takes about 17 seconds. This timing is an
observation, not a performance claim. An optional `--output PATH` writes the
reconstructed certificate outside the package. The default command writes no
artifacts and compares against the frozen certificate.

The registered package command additionally validates its metadata and source
provenance. Full-history ancestry checking is separate and is not claimed for
this shallow checkout.

## Overlap

The bounded survey included canonical guidance, selected review, relevant
merged helper-split/rung-removal notes, all 789 open PR titles and bodies at
08:33 UTC on 2026-11-07, and targeted latest sources #6805, #6824 and #6835.
The archive's path inventory was read, not all 5,005 research directories.
Local notes and public Discussion views have partial coverage. This is not an
exhaustive novelty proof.

PR #6805 changes a main-register route before an independent helper split;
#6824 changes helper entrance frames and coordinated scalar delivery;
#6835 holds the middle word fixed while re-solving its boundary hubs. None is
replaced or contradicted by the present fixed-operands two-coefficient result.
The simultaneous gauge-invariance investigation concerns a fixed middle map
and is complementary.

## Open next questions

* **Three coefficient changes.** Does an exact triple remove one of the
  certified contacts? First derive a three-event boundary equation and an
  exhaustive support filter for one selected gate. The current result gives
  a lower bound on this edit count, not a three-event impossibility.
* **Interior basis changes.** Can a legal co-frame basis change remove a stop
  while changing operands? First identify one actual bank and its entry,
  exit and restoration costs. A local scalar identity alone is insufficient.

Structured questions and the reason for changing the original task-card scope
are in `TASK.json`.

## Credit

Jerry Chen / @CubeJerry, with substantial OpenAI assistance for research,
proof development, code and documentation. The native data and all earlier
construction results retain their original credit: DreamingOfClouds (#6824,
#6835, #6702); CubeJerry (#6805); Ali Romman (helper-basis and native-verifier
lineage); zxv (#6726); thu-nmrc (#6716); and themilkman216 (#968). See
`NOTICE`, `retained/NOTICE-pr6835.txt` and the Apache-2.0 `LICENSE`.
