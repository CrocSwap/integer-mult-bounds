# Validation record

Scientific base: `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`; predecessor
#5079 at `43f558c1b8fc14fb0ed33a4512fbc976beea6b0f`. Priority revision 7.
Krzysztof Wojt with substantial OpenAI Codex assistance and bounded Luna
support. Apache-2.0. Evidence is author-checked, not independent human review.

The universal and real-input statements rest on PROOF.md. The executable
checks independently enumerate bounded lattice problems, verify the literal
two-point error and equivariance, and test larger attaining fixtures. They
do not prove a universal statement by enumeration.

## Executed local mathematical checks

On macOS with CPython 3.12.12, the direct normal replay and the registered
normal/isolated-optimized replays pass. The registered pair took 14.93 seconds
wall time in the measured development run. The metadata/pin check also passes.
All proof-relevant checks use explicit exceptions, not removable assertions.

Both normal and optimized runs report:

- 357 complete grid cases: k=-10..10, m=2..18.
- 44,268 residues and 2,017,390 integer candidates in the independent box oracle.
- 44,982 small rounder/equivariance cases, including translated witnesses.
- 7,380 larger grid attaining fixtures: k=-102..102, m=2..37.
- 205 exact rational real-radius witnesses and 820 integer fixed-point checks.
- Eight rejected variants: omitted reflected error, omitted output transport,
  independent nearest-even ties, omitted canonical orbit tie handling, an
  understated radius, omitted odd-grid gap, ignored grid parity, and dropped
  vertical error at K=1.

The canonical bounded grid table has SHA256
`db6d6ce46bd8df131298924c01d034d26d27bc8d71e9f479b2b0888667a59168`.
Reports bind all eight package files by SHA256. The table and all counts are
recomputed; there is no saved result substituted for an oracle calculation.

The primary agent inspected the separately written box enumerator and checked
the proof, including the odd-grid interval endpoints. A bounded Luna arithmetic
check confirmed the explicit boundary witnesses (K,m)=(3,3),(7,3),(5,5),(101,3)
and the sign-conjugation bookkeeping. This is AI-assisted review, not human
or proof-kernel acceptance.

Reproduction and publication commands:

```sh
python3.12 -W error -B research/reflection-rounding-radius/verify.py
python3.12 -W error -I -O -B research/reflection-rounding-radius/verify.py
python3.12 -B scripts/research_package.py --package research/reflection-rounding-radius
python3.12 -B scripts/check_research_commit.py --package research/reflection-rounding-radius --check-source-history
```

No full selected replay, predecessor verifier, physical caller, Lean, Docker,
independent human or formal proof-kernel review is claimed. Hosted CI is
separate from local execution and will be linked in the PR/Discussion.

## Source and overlap checkpoints

The initial complete overlap snapshot covered 318 open PRs, 4,229 Discussion
records and 6,824 main-tree notes. Submission refresh covers 303 open PRs at
09:43Z and 4,253 Discussion records at 09:44Z on October 23, 2026, with complete
reported pagination and no warnings. The matching current claim is this
investigation #5100; #5079 is the completed predecessor. Live recent PR bodies
and Discussion updates were also checked. Arbitrary diffs and unpublished work
remain outside coverage. Other recent krzysztofwojt topics were excluded.

Canonical main advanced to `20a1e31bc6009b9b3f4d084bbaadc6350e34fcba` at the
submission checkpoint. Governing guidance, priority revision, selected record
and the declared predecessor input are unchanged. Shared replay/publication
helpers acquired repository-environment isolation; the contribution will be
rebased and its focused checks repeated under those helpers. The scientific
base and immutable source pins remain the original fresh-clone commit.

The exact-head publication-byte/source-history preflight, official export
integrity and Git-free replay are separate publication gates run after this
record is committed. Their outcomes and hosted CI are recorded in the PR and
canonical Discussion, without treating transport or CI as scientific acceptance.
