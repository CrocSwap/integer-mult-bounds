# A support31 counterexample makes P112 shortening sharp

[PROOF.md](PROOF.md) gives five small pieces and six endpoints in the literal
P112 geometry. Their common small support has size 31, every endpoint has
support twenty, all eleven pieces are independent, and their span meets the
P112 evaluation code in exactly five dimensions. The support-thirty theorem
of [PR3205](https://github.com/CrocSwap/integer-mult-bounds/pull/3205) is
therefore sharp for its general arbitrary-support contract.

The new step realizes the equality left by
[PR3207](https://github.com/CrocSwap/integer-mult-bounds/pull/3207) as actual
independent pieces. [WITNESS.json](WITNESS.json) contains the exact directions,
31 cuts and six sparse endpoints. [RESULT.json](RESULT.json) retains rational
ranks and support checks. No original TWOSIDE profile, decoder floor, supplier
or multiplication-exponent improvement is claimed.

## Reproduce

Python 3.12 and its standard library suffice. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-support31-replay"
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -W error -B \
  scripts/research_package.py --package research/p112-support31-sharpness
```

The registered replay runs rational elimination, a separate lattice/modular
checker and fourteen behavioral tests under optimization. The modular checker
uses nonzero minors only for lower bounds; explicit independent codeword
relations supply the rational upper bound. It does not infer rational rank
from modular zeros. Its lattice enumeration has exactly `5^8` candidates.

Both checkers operate on the new literal witness and do not run historical
supplier suites or inherited classification censuses. The sole external input
is the pinned predecessor geometry source, authenticated for provenance and
coordinate convention. No predecessor module is executed. All mathematical
checks also work in a Git-free export containing the declared input; package
metadata and publication-byte checks require Git.

`verify.py --output NEW_PATH` writes a new receipt outside the checkout and
refuses to overwrite a file. Registered inputs and commands are explicit in
[VERIFY.json](VERIFY.json). See [CHECKS.json](CHECKS.json) for actual runs and
[ENGINEERING.md](ENGINEERING.md) for implementation limits.

## Open next questions

Can a label-span constraint extend shortening to a relevant support31 caller?
The separate check gives small-support label ranks `8,8,8,9,7` and endpoint
ranks `8,9,8,8,9,8`, which already prevent these from being the rank-six
pieces in original TWOSIDE profiles. First bind a named actual caller's
allowed support ranks and test that additional hypothesis against this witness.
The arbitrary-support counterexample does not rule out such a strengthening.

Can an analogous witness use fewer than five small pieces while preserving
collective independence and the support budgets? First derive the required
rank of the cut-restricted code directions. A search needs a named original
caller or a clear new implication before further family expansion.

## Credit and scope

Nick Petalas contributes the balanced support31 witness and its checks.
PR3205 retains priority for the support-thirty theorem; PR3207 supplies the
analytic frame argument and the equality handoff. PR3203/3188/3176 and the
retained E8/P112 lineage supply predecessor geometry and support methods.
DreamingOfClouds/PR3154 supplies TWOSIDE, with joaqcoo's decoder model retained
in that lineage. Exact public heads and source hashes are in
[SOURCES.json](SOURCES.json). Predecessor inputs are unchanged.

The new rational witness works over every characteristic-zero field. Its
checks are finite exact evidence with internal automated review. Human review,
proof-kernel verification and hosted CI are separate. Development used
substantial automated assistance. The selected result is unchanged.
