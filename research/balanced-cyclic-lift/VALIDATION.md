# Local validation receipt

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Dependency: PR628 `0768f97d06c623b8211e651543c66135796b62bf`.
Host: macOS arm64; CPython 3.13.2 and 3.9.6; Python standard library only.
Contributor: Wentao Li, with substantial OpenAI Codex assistance.

Completed 2026-10-13:

- Ordinary replay and isolated optimized replay reproduce the exact certificate.
  1,560 factor instances, 7,420 full columns, 4,680 rounded factor executions,
  315 ordered products (each with a cancelling negative call), and 25 controls.
  The isolated optimized replay also passes with the host's CPython 3.9.6.
- Independent dense rational inversion supplies the factor and product references.
  All dirty arrays/scalars and source values restore exactly, including 220-bit dirt.
- The pinned original PR628 dispatcher matches the closed count formula through
  128 factors when run with a counting leaf stub. This is not its numerical replay.
- `python3 -B research/balanced-cyclic-lift/check_package.py` passes on an offline
  directory with spaces under `-I -O -B`. It rejects altered immutable source,
  replacement of the scalar-word invoice integer 1 by Boolean true, and a changed
  pair-shear sign. The last mutation fails the independent full-column identity.
- `make selected-record-check` passes, including exact selected κ, source inventory
  and proof supplement binding.

The finite regression domain and seed are explicit in PROOF.md and CERTIFICATE.json.
The written factorization and error argument cover all L under their exact real
rational/half-stable hypotheses; finite enumeration is not presented as their proof.
No solver search, arbitrary-program optimum, runtime benchmark, full prime-power
kernel, common-label supplier or multiplication theorem is claimed.

Pre-submission coordination refresh at approximately 05:41 UTC covered **612 open
PRs through #793**, and re-fetched main at the same base. No pinned coordination
issue exists. Related heads are recorded in SOURCES.json. In particular, #784
and #788 improve other echo-tree/clean-storage contracts and do not provide this
determinant-balanced in-place leaf. They are credited in NOTICE.md.

The immediate publication refresh at approximately 05:57 UTC covered **621 open
PRs through #802**. PR628 remains at the consumed head, main was freshly fetched
at the exact base again, and no matching in-place cyclic leaf submission was
identified. PR796's root valuations were read separately and credited as context.
An immediate pre-creation check also inspected PR803's analytic inverse bound,
head `d213ac12d4a1ab8f717d942e844df318ceb395fb`; its mechanism is distinct.

The root `make verify` was launched once on an untouched exported base snapshot,
so historical generators cannot change this contribution or the primary checkout.
It passed seven historical groups (`verify-community`, `verify-producers`,
`verify-partial-gauge`, `verify-three-stage-cover`, `verify-paired-cube`,
`verify-recycled-bit`, `verify-entrance-banks`) and stopped at `gen4-bank-verify`:
`ModuleNotFoundError: No module named 'sympy'` in the baseline's verifier, with
make exit status 2. This is an environment limitation on the unchanged base;
no full-suite pass is claimed. The new standalone package requires no SymPy.

Staged whitespace checks pass; every added file is under this package's directory.
All original vendor source bytes match their Git/SHA-256 pins. Selected construction
and `upstream/` files are unchanged. No supplier cold replay, remote/Linux CI or
proof-assistant validation is claimed for this new package.
