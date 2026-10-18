# Fixed co-star decoder obstruction from nine E8 roots

**One exact structural obstruction; no decoder or kappa claim.** The rational
masked P112 candidate with normal groups `[0,1,56,87]` and capacities `[3,2,2,2]`
is impossible, even with coefficient zeros, repeated terms and unequal left
and right factors. Both factors of each term must lie in its group's co-star.

The [proof](PROOF.md) uses six roots exclusive to a two-term group. Their crown
orthogonality pattern forces the factors on each side into two distinct lines.
Three further roots then lose that group's contribution and would require
`4I3` from only two remaining terms. The contradiction is rank 3 versus rank 2.
This addresses a fixed changed decoder mechanism, not a packing or cost audit.

## Reproduce

Python **3.10 or later**, standard library only. From the repository root:

```sh
python3 -I -O -B research/p112-costar-crown-obstruction/verify.py
python3 -I -O -B research/p112-costar-crown-obstruction/test_portability.py
```

Expected lines:

```text
PASS_P112_COSTAR_CROWN_PREMISES equations=39 controls=13 written_proof=PROOF.md no_kappa
PASS_CROWN_PORTABILITY controls=24 no_checkout read_only deterministic
```

Copy this directory alone anywhere, including a path with spaces, and run
`python3 -I -O -B "/path with spaces/verify.py"` from any working directory.
No checkout, Git, network, third-party dependency or predecessor replay is
needed. The default verifier is read-only; `--json` prints its deterministic
result. There is no elapsed-time field and no artifact-writing option.
The portability test creates and removes an isolated temporary copy, leaving
the source package untouched.

The optional repository metadata/replay hook is:

```sh
python3 scripts/research_package.py --package research/p112-costar-crown-obstruction --check-only
python3.12 scripts/research_package.py --package research/p112-costar-crown-obstruction
```

This generic hook additionally checks historical metadata in Git and uses
Python 3.12. That infrastructure requirement does not apply to the standalone
commands above. [VERIFY.json](VERIFY.json) declares no external proof inputs.

## Evidence and boundaries

- [MODEL.json](MODEL.json) fixes Q, the source ordering, P112, both factor
  support envelopes, capacities, all ordered even-entry equations, and target
  `2G`. It explicitly allows zeros and asymmetric factors.
- [CERTIFICATE.json](CERTIFICATE.json) records nine doubled-coordinate roots,
  support memberships, incidence matrices and the 39 proof equations. The
  verifier derives every field again, including fingerprints of the full
  120-line model, live co-stars and all 6,720 masked entries.
- [EXPECTED.json](EXPECTED.json) is the timing-free expected premise/control
  result. It is compared with a freshly computed result, not trusted as a verdict.
- [PROOF.md](PROOF.md) supplies the universal inference. The Python program
  checks its finite premises; it is not a proof assistant formalization.

The thirteen internal controls include altered capacities, zero target, lost
exclusivity, repeated roots, JSON/certificate tampering, dense asymmetric
rank-two factors, and a full rank-three crown satisfying both oriented edges
and all diagonals with an explicit nonzero escape vector. Three terms also
explicitly realize the residual `4I3`. The 24 CLI/portability checks include
missing and malformed certificates, altered model/support/mask assumptions,
caller-supplied verdicts, paths with spaces and read-only deterministic replay.

This package does not classify other normal sets or capacities. It carries no
historical census, optimization receipt, selected-result dependency or physical
cost screen. No feasibility conclusion for another candidate follows from it.

## Sources and credit

[SOURCES.json](SOURCES.json) pins the retained E8/source-order adapter at
repository commit `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`, with its Git blob
and SHA-256. It is historical provenance; the verifier reconstructs the model
from the bundled immutable definition and never imports or reads that adapter.
The task catalogue is also historical metadata, not a standalone runtime input.

The E8 model follows DreamingOfClouds' [PR717](https://github.com/CrocSwap/integer-mult-bounds/pull/717)
as retained in themilkman216's [PR968](https://github.com/CrocSwap/integer-mult-bounds/pull/968)
frame-pair adapter. Their model attribution is retained without importing the
stronger all-pairs or eight-term hypotheses. The fixed-candidate work was
coordinated in [Discussion 1267](https://github.com/CrocSwap/integer-mult-bounds/discussions/1267).
No novelty claim about all related literature or concurrent work is made.

Substantial AI assistance: GPT-6 Astra derived the obstruction and implemented
this package; Claude Fable 5.1 implemented the preceding co-star gate; a separate
AI-assisted reviewer checked the written argument and reconstructed its finite
premises. This is not human peer review or kernel certification. The separate
review is development provenance, not a required input. See [NOTICE](NOTICE).
New work is Apache-2.0; the license is bundled for standalone distribution.

## Open next questions

Does another specifically preregistered co-star assignment contain an exclusive
rank-two crown and a residual rank obstruction? This matters because the lemma
could cheaply rule out a proposed structural decoder before coefficient
synthesis. A feasible first step is to freeze one assignment and inspect its
exclusive-root incidence graph. The blocker is that no other assignment or
whole-family classification has been established here. This package launches
no additional search. Structured scope and this question are in
[TASK.json](TASK.json).
