# Validation record

Environment: CPython 3.12.16, macOS arm64, standard library only.
Base: `e54523517d0f03e58352e647c403a5af3e525a57`.

The following command passed in normal and optimized isolated modes:

```sh
python3 -B scripts/research_package.py --package research/idempotent-first-factor-kernel
```

Both direct runs printed:

```text
PASS_IDEMPOTENT_FIRST_FACTOR_KERNEL raw_matrix_cases=395316
```

The registered marker was `PASS_REGISTERED_RESEARCH_PACKAGE` with
`outcome=completed`. AST parsing and `tabnanny` also passed.

The complete domains are 14 canonical first factors: every rank at each
dimension from one through four. Each case enumerates all `2^(n^2)`
middle matrices. The named source matrix adds 65,536 cases. No matrix is
sampled and there is no early exit. Every accepted set equals a second
construction from subspaces, fixed complements and maps. Each kernel,
duplicate check, count stratum, rank distribution and idempotence class
is checked. The named accepted-list SHA256 agrees with the pinned PR #7223
receipt. The formula checks through dimension 12 are arithmetic checks,
not full matrix censuses.

Controls check a changed third factor, a non-idempotent first factor,
an impossible injection dimension and the exact kernel of the zero map.
The rank-two witness demonstrates the failure of the rank-one exclusion.
All checks raise exceptions and remain active under `-O`.

The all-dimension claim rests on the proof in [PROOF.md](PROOF.md), not
on extrapolation from these finite checks. No code from the predecessor
is imported. Its coefficient lemma and named result are credited inputs.

The selected binding-only check passed; it is not a full selected replay.
No complete predecessor replay, native or physical replay, selected cold
replay, Lean, Docker, independent human review or proof-kernel check was run.
The exact order, F2 coefficients and first-factor idempotence remain premises.
No paid profile, supplier admission, full multiplication theorem or new
kappa is claimed. All five selected assumptions remain.

Commit-byte, source-history, export, sealed replay and publication checks
are recorded separately in the PR description. Hosted CI status is also
reported separately and does not replace the local scientific evidence.
