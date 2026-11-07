# Verification evidence

The frozen research base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The audited pending caller is CrocSwap/integer-mult-bounds#6833 head
`ad24ad966b857dbfed50d9121624db84b2eccc92`. The live caller and all proof-contract
snapshots are retained in this package and authenticated by `SOURCE-PINS.json`.

## Executed checks

Environment: Python **3.12.14**, Linux, standard library only.

```sh
python3 -B research/p104-chain-idle-applicability/verify.py --write research/p104-chain-idle-applicability/RESULT.json
python3 -B scripts/research_package.py --package research/p104-chain-idle-applicability --check-only
python3 -B scripts/research_package.py --package research/p104-chain-idle-applicability
```

The registered replay executes both normal Python and `python -O -B`, compares
the complete generated result to `RESULT.json`, and reports:

```text
PASS_PACKAGE_METADATA_AND_PINS
PASS_CHAIN_IDLE_APPLICABILITY
PASS_CHAIN_IDLE_APPLICABILITY
PASS_REGISTERED_RESEARCH_PACKAGE research/p104-chain-idle-applicability outcome=completed
```

Both mathematical runs check sixteen idle lines, 72 covered incidences,
56 carrier transitions, sixteen host-to-idle ordinary segments, 1,664 paid
jobs and 100,464 two-axis boundary exchanges. Each runs all ten targeted
negative controls. `require` checks remain active with assertions disabled.

The package was also copied to a fresh temporary directory outside every Git
worktree and replayed there with `--check RESULT.json`; it reports
`PASS_GIT_FREE_RETAINED_EXPORT`. This verifies the declared standalone source
availability, not remote Git-history ancestry.

## Method and scientific scope

The independent implementation imports no predecessor Python. It derives the
ordinary frames by multiplying the actual scalar instructions, factors complete
four-event kernels without evaluating their address operators, and checks unit
image/dual carrier transport. Gaussian lowering is checked using the complete
coordinate permutation and every coefficient of its Fourier phase polynomial,
including the absolute phase. The all-positive-multiplicity claim comes from
the proof in `PROOF.md`, not extrapolation from finite tensor-width checks.

A separate OpenAI research agent inspected the proof, the source-bound
interpreter, and the retained compiler reading. That review requested explicit
checks for intervening thin kernels and for the ordinary segment between a
host kernel and its actual paid idle occurrence. Both were added and the whole
registered replay was repeated. This is AI-assisted review; no independent
human acceptance or proof-kernel theorem is claimed.

The review and replay do not run the complete native word, reprove the uniform
compiler, check global product/completion ambient constants, or establish the
five inherited framework assumptions. They resolve the finite whole-idle
application question stated by the exact pending caller. **No new κ.**
