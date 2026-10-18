# Fixed 26-puncture paired-normal completion

For PR1020's exact 26-line puncture and ordered normal pair (48, 0), this
package supplies a rational eight-term all-pairs decoder with separate COPY
cost **62**, profile **[6,8,8,8,8,8,8,8]**, versus the predecessor's **69**.
The puncture, cost-six first pair and prior 69 decoder are woklerx's work.

[proof.md](proof.md) gives the claimed matching lower bound for arbitrary
complex coefficients, without the F6 hypothesis, and a classification of
256 optimal classes up to residual paired rescaling and permutation.
Those universal conclusions depend on the written finite-reduction and
compatibility arguments; machine replay verifies their finite premises.
A separate GPT-6 Pro review reports corroboration of the minimum, the 256
classes and the attained branch bound 67. It independently recomputed the
511 kernels and 1,716 subsets, reconstructed the cost-62 witness and built
its own cost-67 witness. It did not audit the supplied programs or the prior
69 decoder. The full transferred review text was inspected; no repair was requested.
Its separate programs, certificates and logs have not been retrieved or
replayed locally.

The model fixes all eight terms, the exact first pair including its scaling,
all 8,836 ordered pairs of 94 live roots, the ordinary transpose identity,
and separate binary-rank charges on actual supports. It does not optimize
other punctures or designated pairs. Preparation, frames, restoration,
hosting and physical rank-shape costs are not priced; this is no paid-moment
or kappa improvement.

## Replay

Python 3.12, standard library only:

```sh
python3.12 scripts/research_package.py --package research/complex-paired26-completion
```

The registered hook runs both `verify.py` and the separately implemented
`audit.py` under `-I -O -B`, with a 30-second cap each. Direct commands from
this directory are `python3.12 -I -O -B verify.py` and
`python3.12 -I -O -B audit.py`. Success markers are
`PASS_FIXED_PAIRED26_MINIMUM_62` and `PASS_SEPARATE_FRACTION_AUDIT`.

The primary rebuilds and compares the entire certificate. Both programs
check the 511 functional ranks/kernels, 1,716 candidate seven-subsets, and
all 8,836 entries and actual-support charges for the prior 69, attaining 62,
sharp branch-67 and exact complex cost-63 examples. The 256 count is the
eligible basis-set census, not 256 full entrywise complex replays.
Fourteen primary rejection controls and two complex convention/compatibility
controls remain active under optimization.

Both programs were written in the same GPT-6 Pro research session; agreement
is not independently authored or human mathematical review. Local Codex
replay on CPython 3.12.14 passed normal and optimized runs, with a fresh
saved-certificate mutation rejected in both modes. [REPLAY.json](REPLAY.json)
records the environment, timings, controls and limits. [SOURCES.json](SOURCES.json)
pins the authenticated source bytes and immutable delivered artifacts.

## Priority checkpoint

This is a bounded result from the revision-2 `complex-masked-decoder`
assignment and [Discussion 1570](https://github.com/CrocSwap/integer-mult-bounds/discussions/1570),
changing the predecessor's at-most-25 punctures to one fixed 26-puncture
object. Revision 3 arrived while it was running. The result is retained as a
scoped algebraic checkpoint under that guidance; no favorable fully paid
rank-shape budget has been established. Historical assignment pins remain
historical. TASK.json records both checkpoints and the changed scope.

## Open next questions

Does this decoder admit a physical implementation whose fully charged
optimistic moment passes the current priority gate? First specify and price
preparation, frames, restoration and hosting, then test that bound before
network construction. The present COPY-only certificate supplies neither
that interface nor its invoice, so it cannot answer this question.

Prepared for Andrey Mas with substantial GPT-6 Pro research through ChatGPT
and Codex source coordination, mechanical verification and packaging.
See [ATTRIBUTION.md](ATTRIBUTION.md) for retained predecessor credit.
