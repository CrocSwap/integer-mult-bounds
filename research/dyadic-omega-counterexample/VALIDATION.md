# Validation record

Environment: CPython 3.12.14, Linux x86_64, standard library only.
Canonical source base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Prepared for @CubeJerry with substantial OpenAI Codex assistance; Apache-2.0.

The following checks were actually executed on 2026-11-06:

| Check | Observed result |
| --- | --- |
| `python3 -B scripts/research_selected_baseline.py`, in a read-only same-base checkout with the selected closure present | `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; not a supplier/theorem replay |
| `python3 -I -B scripts/research_package.py --package research/dyadic-omega-counterexample --check-only` | `PASS_PACKAGE_METADATA_AND_PINS` |
| `python3 -I -B -W error scripts/research_package.py --package research/dyadic-omega-counterexample` | All three registered commands passed; exit 0; 59.609 seconds on this host |

The primary replay reported 134 exact source-order comparisons, 32 literal
profiles, 28 literal generalized-family cases, 4950 integer recurrence/formula
pairs, and ten successful negative controls. It matched the typed witness,
including both signed channel digests and the first strict winning budget.

The separate forward implementation executed all 16384 leaves and matched
both signed channel digests, checked 1954 paired-prefix/readout cases, and
passed four controls. Cold replay copied only the package and five declared
inputs to a Git-free tree and ran both engines with `-I -B -O -W error`.
Actual byte corruption of each of the five source inputs failed at source
authentication; an actual one-unit understatement in the witness failed the
exact receipt comparison. These six corrupted runs were expected failures.

No claim of human independent review, proof-kernel acceptance or a full
multiplication-theorem audit is made. In particular, recurrence checks through
height 100 and small all-cut replay do not establish universal quantifiers;
those rely on the written induction and limiting argument in PROOF.md.
The two mathematical implementations were written in this same AI-assisted
session and use different propagation directions, word construction and
monomial representations; they are not separate reviewers.

The checkout is deliberately shallow. Source bytes at the pinned parent are
available and authenticated, but the optional full-history ancestry audit is
not claimed. Package commit-byte/mode checks and whole-tree comparison against
the published fork are publication checks recorded in the PR handoff; they
are not mathematical validation or a hosted-CI result.
