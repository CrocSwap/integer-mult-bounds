# Validation record

Local validation on 2026-10-15, macOS 27.0.1 arm64.
The scientific baseline is `7f90cb9985624b86b0e9dd8737b4e9ba2f795e31`.
The submission refresh fetched canonical main
`0374b3e6a532dac112813523d605288c416418c1`; the relevant instructions,
priority revision 5, selected record and three pinned predecessor inputs
were unchanged. The branch is isolated from the user's original checkout.

## Completed checks

The complete registered replay passed on CPython **3.12.15** using uv
0.13.1 and no third-party verifier dependencies:

```sh
uv run --python 3.12 --no-project scripts/research_package.py --package research/coxeter-root-tariff
```

It ran both exact engines with `-I -O -B`, followed by all six public-CLI
test groups. Expected final marker:
`PASS_REGISTERED_RESEARCH_PACKAGE research/coxeter-root-tariff outcome=completed`.
The local uv executable was installed in a temporary tooling virtualenv;
the package itself needs only Python's standard library. The same command
is directly reproducible as:

```sh
python3.12 -I -B scripts/research_package.py --package research/coxeter-root-tariff
```

Additional direct replays passed under CPython **3.14.7** (normal and
optimized engines and the six tests) and **3.11.3** (primary engine and
optimized independent engine). The separate reviewer also replayed the
optimized engines and six tests on 3.12.15; see its byte-specific
[REVIEW.md](REVIEW.md).

```sh
python3 -I -O -B research/coxeter-root-tariff/verify.py
python3 -I -O -B research/coxeter-root-tariff/independent.py
python3 -I -B research/coxeter-root-tariff/test_package.py
python3 scripts/research_package.py --package research/coxeter-root-tariff --check-only
python3 -B scripts/research_baseline.py
git diff --check
```

The source-bound baseline check passed at selected kappa
`0.001672660197076918`. It is orientation/binding evidence only.
The fixed primary receipt regenerated explicitly with `verify.py --write`
and was subsequently consumed unchanged by normal/optimized replays.
The read-only export test verifies both direct engines work without Git
and leave the package and all pinned input files byte-identical.

## Deliberate failures and limits

The suite rejected changed predecessor bytes, a dropped source pin,
Boolean/integer and integer/float receipt substitutions, wrong receipt
counts, duplicate JSON keys, and a source mutation that undercharges every
rank at two or above. Formal semantic controls detect every listed omitted
call, dirty-column leakage and reversed noncommuting circuit. The B2 norm
fixture shows why represented equality alone is insufficient.

The universal theorem is the written proof using the explicitly cited
standard root facts. These finite checks do not prove the whole theorem by
enumeration. No Lean/kernel verification, physical/native implementation,
supplier admission, new kappa, or selected full cold replay is claimed.
Hosted CI and maintainer acceptance are separate from this local record.
