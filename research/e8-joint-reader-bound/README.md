# E8 star decoders: a joint-reader obstruction through 55 punctures

**Scoped negative result; no new kappa.** Deleting at most 55 of the 120 real
E8 root lines cannot improve the star copy-cost/live-port ratio `63/111`.
The new argument rules out simultaneously cheap readers by charging their
shared deletion set once. It extends Chi Zhao's [PR631](https://github.com/CrocSwap/integer-mult-bounds/pull/631)
exclusion through 35 deletions and Philipp's [PR875](https://github.com/CrocSwap/integer-mult-bounds/pull/875)
36-deletion equality classification.

Two distinct nonzero binary readers have a support union of at least 84
root lines. A surviving rational rank-five reader contains at most 20
lines, so two such readers need at least 44 shared deletions. This is a
compatibility bound, rather than another puncture search. Applying the
same inequality to all physical ranks gives:

| Deleted lines | Universal lower bound on star cost | Worst endpoint ratio |
|---|---:|---:|
| 36–43 | 53 | `53/84 > 63/111` |
| 44–51 | 45 | `45/76 > 63/111` |
| 52–55 | 44 | `44/68 > 63/111` |

These are lower bounds, **not claimed attainable costs**. Combining them
with the predecessor's smaller-puncture result gives the theorem through
55. The known nine-puncture construction still attains `63/111`. At 56
deletions the reader space can lose a dimension, and this note stops.

## Reproduce

From the repository root, Python 3.10+ and the standard library suffice:

```sh
python3 -I -B research/e8-joint-reader-bound/verify.py
```

Expected:

```text
PASS_E8_JOINT_READER: 256 flats; 511 readers; 130305 pairs; punctures 0..55; 6 rejection controls; no new kappa
```

The default run writes nothing and compares the entire rebuilt
[CERTIFICATE.json](CERTIFICATE.json). `--write /tmp/e8-joint.json` emits
a deterministic rebuilt receipt. Both new checkers preserve checks with
`-O`; the unmodified predecessor intentionally refuses optimized execution.

```sh
python3 -I -O -B research/e8-joint-reader-bound/independent_check.py
python3 -I -B research/e8-joint-reader-bound/test_package.py
```

The independent checker constructs all 240 signed roots before quotienting
by sign, uses Fraction RREF and direct span membership, and exhausts all
24,310 sorted nine-rank invoices at each of the 20 new puncture budgets.
It imports neither the primary verifier nor the predecessor implementation.
It checks the certificate's documented `independent_summary` only; source
pins, per-flat rows, threshold witnesses, the small-puncture inheritance,
and the rank-loss boundary have separate primary/predecessor coverage.

The package tests replay both implementations from a path containing spaces,
require byte-identical regeneration, reject a changed bound or capacity,
reject modified source bytes before overwriting an output, and replay the
retained predecessor with its geometry/parity/flat controls. See
[VALIDATION.md](VALIDATION.md) for actual results and limitations.

## Proof, scope, and handoff

[PROOF.md](PROOF.md) defines the model, states the inherited results,
proves the shared-deletion inequality, and explains why all standard
parabolic flats cover arbitrary root-spanned reader spaces. The finite
census supports that written coverage argument; it is not an enumeration
of all puncture subsets or a formal proof of multiplication.

The result concerns root-only E8 ports, fixed binary label readers,
independent input bits and additive star copy-rank costs. It does not
exclude general pairing-rank or nonlinear decoders, non-root ports,
changed geometry, helper savings, or 56+ punctures. No supplier, paid
recursive recurrence, improved assembly or new kappa is claimed. The
all-size/compiler, hosting, precision/tape and analytic obligations of
the selected construction remain inherited.

This contribution adds only this directory. The exact base is
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`; its selected conditional
kappa is `1661634653669567/10^18`, from PR799 with PR589 on PR555.
Existing generators, `upstream/`, and selected-frontier files are unchanged.
[SOURCES.json](SOURCES.json) pins retained predecessor bytes by commit,
SHA256 and Git blob, and records the inspected base context.
During final verification upstream advanced to `47481c89fd30a43f8f882eb4b391e89c29273fd0`,
which selects PR890 at conditional kappa `1661957774647029/10^18`.
This structural result is independent of that frontier change.

[CLAIM.json](CLAIM.json) records the OS-random seed **46**, three candidate
tasks, local claim, bounded domain and overlap review. No pinned sprint
coordination issue existed. There was no randomized search or timeout;
all stated finite domains were completed. PR875's stronger classification
at exactly 36 deletions remains useful and is not superseded by our
coarser cost bound there.

Prepared by **Ross Richardson (@RossRichardson)** with **substantial OpenAI
Codex assistance** in proof development, implementation, independent
checking and writing. See [NOTICE.md](NOTICE.md) for predecessor credit.
Apache-2.0; no independent human review is claimed.
