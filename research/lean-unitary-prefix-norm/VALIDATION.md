# Observed verification, 2026-10-13

The 13 core and 20 example theorems compiled with Lean 4.21.0
(`6741444a63ee`, Linux x86_64, Release) and Mathlib
`308445d7985027f538e281e18df29ca16ede2ba3`. All nine dependency commits and
tracked source trees matched the inherited manifest before and after each
successful full check. No warning or error occurred in the accepted builds.

## Commands and receipts

The local Lean distribution was on `PATH` as
`/tmp/math-pass07-lean-download/lean-4.21.0-linux/bin`. Each command below
freshly rebuilt `LemmaG.Stream`, `PrefixNorm` and `PrefixNorm.Examples`, printed
all 33 axiom reports, and rejected the semantic partial-store mutation.

```sh
# Python 3.14.4; independently downloaded pinned dependencies/cache already present.
python3 -I -B research/lean-unitary-prefix-norm/verify.py \
  --work /tmp/math-pass25-lean-work --no-cache

# Python 3.12.3; new workspace, explicitly shared immutable dependency sources.
/usr/bin/python3.12 -I -O -B research/lean-unitary-prefix-norm/verify.py \
  --work /tmp/math-pass25-lean-clean \
  --packages /tmp/math-pass25-lean-work/.lake/packages --no-cache

# Final runner, new empty workspace; clones all nine dependency repositories
# and runs the targeted Mathlib cache command through the documented path.
/usr/bin/python3.12 -I -B research/lean-unitary-prefix-norm/verify.py \
  --work /tmp/math-pass25-lean-bootstrap-clean
```

All three successful runs produced:

```text
PASS_LEAN_UNITARY_PREFIX_NORM core=13 examples=20 axioms=33 semantic_mutation=rejected
axioms_sha256=9e0091ab53901725b3f6b1cbd27171fbf3465138467b6cf025d7312e739c986b
```

The canonical complete `RECEIPT.json` SHA256 was identical in all three:
`952d7066ce87a72d14c667d8743cd2a15d7779eee1bad0a6cbf43265f1b79b09`.
Canonical encoding means `json.dumps(value, sort_keys=True,
separators=(",", ":")).encode()`.

The first attempted empty-workspace run exposed setup chatter before Lean's
version line. The final runner parses exactly one exact-version report,
retains `TOOLCHAIN.log`, and rejects wrong/prerelease/duplicate/missing reports.
The third successful run above exercised that fix with real clone messages.
It reused the installed Lean toolchain and the user's downloaded Mathlib
archive cache; this was a fresh dependency workspace and proof build, not an
empty-machine installation or an independent recheck of all Mathlib kernels.

## Axioms, exact examples and semantic rejection

`PrintAxioms.lean` covers every theorem listed in `THEOREMS.json`; the output
matches `AXIOMS.json`. The union is exactly `propext`, `Classical.choice` and
`Quot.sound`. No placeholder, extra axiom or native evaluator is used in the
new proofs or imported Stream source.

The examples prove a valid nonidentity-frame instance, mismatched-frame and
incorrect-recipe discrepancies (`2` versus scalar coefficient `0`), a
nonunitary relabel loop (`8` versus `1`, despite endpoint restoration), and
the half-store squared norm `41/25` between endpoints of squared norm `1`.
The two selected-number corollaries retain their endpoint bounds as premises.

The verifier changes the conclusion of `components_uniform` from `2 * L^2`
to `L^2` in `Undercharged.lean`. Lean exits nonzero with
`linarith failed to find a contradiction` at the altered proof. A subsequent
dependent theorem also reports a type mismatch; acceptance specifically
requires the failure at the altered inequality. The original files are
untouched. The independent `41/25` theorem explains why this strengthening
is false, rather than relying on tactic failure as a mathematical argument.

## Python guards and source integrity

```sh
python3 scripts/research_package.py --package research/lean-unitary-prefix-norm --check-only
/usr/bin/python3.12 -I -B scripts/research_package.py --package research/lean-unitary-prefix-norm
python3 -I -O -B research/lean-unitary-prefix-norm/verify.py --source-only
python3 -I -O -B research/lean-unitary-prefix-norm/test_verifier.py
python3 -I -B scripts/verify_selected_result.py
git diff --check
```

Metadata/provenance/live pins passed. The registered Python 3.12 hook passed
its source guard and seven tests. Direct isolated optimized Python 3.14.4
source/test commands also passed. The generic hook intentionally requires
Python 3.12 and rejects replay under 3.14; its metadata check is version
independent. It is not the full Lean acceptance command.

Tests cover nested comment handling and forbidden proof tokens; missing,
duplicate and unapproved theorem axiom reports; exact-version parsing during
cold setup; preservation of an unrecognized nonempty workspace; missing axiom
requests; and source corruption after a successful read-only, minimal-export,
isolated optimized relocation. File hashes are unchanged by that successful
relocation. Critical verifier checks do not depend on Python `assert`.

The selected-record integrity check retained
`836330098538459/500000000000000000`. The working contribution adds only this
package and its dedicated workflow. The refreshed main
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f` changed historical reconciliation
evidence only; selected inputs, task guidance, catalogue and live proof inputs
remain unchanged from the task base. Fresh overlap counts and exact nearby
heads are in `OVERLAP.json`.

## Coverage limits

The full command proves the stated quantified lemmas using the original Lean
event semantics. It does not encode the selected PR1094 word or check its
concrete signed row table in Lean. It does not formalize the selected exact
physical recipes, coefficient scratch implementation, native/Clifford
execution, HPE/source-to-event translation, hosting, fixed-point roundoff,
compiler/tape costs or all-size analytic transfer. The original supplier cold
replay was not run for this formal lemma package; its selected files are
unchanged. No reduced production precision or new kappa is claimed.

The dedicated GitHub workflow is supplied, but these are local observations;
hosted CI status must be read separately from the PR. No independent human or
subagent review was performed.
