# Independent finite helper-frame lifetime audit

The standalone `scripts/verify_cold617_interface.py` accepts a scalar-preserving
frame mutation of the archived PR626 CK provider: change only
`tail[34][-1]` from frame 52 to FULL (frame 1). The next touch of helper 234
returns to frame 52. The interface checks its last touch and terminal frame,
so this illegal intermediate descent is invisible to that check.

**This is a gap in the standalone interface's coverage, not a counterexample
to the selected result.** The full transport verifier already enforces frame
monotonicity. The contribution adds an independently implemented, inexpensive
check of that obligation and explicit negative controls. No new kappa is claimed.

## Reproduce

From the repository root, with Python 3.11+:

```sh
python3 -B research/helper-frame-lifetime-audit/verify.py
python3 -B research/helper-frame-lifetime-audit/test_verify.py
python3 -O -B research/helper-frame-lifetime-audit/test_verify.py
python3 -X utf8 -B research/helper-frame-lifetime-audit/reproduce_gap.py
```

The first three commands use only the Python standard library. The last also
runs the existing interface script and therefore needs its dependencies
(including numpy). `-X utf8` avoids the Windows default text encoding when
that existing script reads its Unicode Lean literals. No sources or archived
fixtures are modified. Optional `--out FILE` arguments to `verify.py` and
`reproduce_gap.py` write receipts; the submitted results are `RESULT.json` and
`GAP.json`.

Expected results:

- Both archived PR626 providers pass: 492 helpers each, including 36 entering
  early ends and 22 cold early ends. There are 5,804 CK and 5,732 JP8 helper
  touches in the checked persistent schedule.
- All 17 unit tests pass with normal and optimized Python.
- The frozen interface accepts both the original and mutated CK word. The new
  checker rejects the mutation at `tail[35]`, helper 234, frame `1 -> 52`.

The mutation changes no scalar gate or coefficient. The exact original gate
is `["add", 234, 0, -1, 2, 52]`. Subsequent CK tail touches of helper 234 at
indices 35, 36 and 37 use frame 52. `reproduce_gap.py` confirms unchanged scalar
operations, the old acceptance, and the independent rejection automatically.

## Method and verification boundary

`verify.py` constructs each binary subspace by enumerating every XOR combination
of its basis, then compares sets for inclusion. It imports no constructor,
transport implementation, wrapper checker, or linear-algebra engine. Ambient
dimension is deliberately bounded to 1..12; the audited words have dimension 9.
Equivalent bases are accepted, whereas equal-rank incomparable subspaces fail.

It checks helper frames from `start` through `A`, `B`, and `tail`, then their
final climbs. It also checks the last tail frame for early-ended helpers,
excludes prefix touches before entry wrappers, and excludes cleanup touches of
any register ending below FULL. Both operands of `add` and the target of `scale`
count as touches. Frame bases, register/frame indices, gate arity and rational
coefficient syntax are validated; these are not a complete scalar gate audit.

This is a projection onto persistent helper frames. Center excursions during
`cut` are assumed to restore their entry frames, as in the transport verifier;
the new checker does not independently prove that restoration. It does not
verify scalar endpoints, wrapper identities, costs, physical hosting, tape or
analytic assumptions, or the full multiplication theorem. It supplements the
existing replay and does not replace it.

The existing selected-source inventory check passed after this addition.
The repository-wide `make verify` and cold supplier replay were not run: this
Windows environment has no `make` or configured Linux runtime. This package
does not change a construction, frozen verifier, selected record, or bound.
Validation was performed on Windows with CPython 3.12.14.

## Pins, scope selection, and attribution

- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- OS-random assignment seed: **28**, complex-supplier track. The bounded scope
  is an independent audit of the complex supplier's helper-frame schedule.
- Candidate scopes considered: PR620 portable LP reproduction, PR626 owner-map
  validation, and the helper-interface lifetime check. The lifetime check was
  selected because it yielded a concrete, scalar-preserving negative control
  and requires no new optimization search or claimed exponent improvement.
- The claim was recorded locally; no pinned sprint coordination issue was
  visible during the initial check.
- Provider source: PR626 `660de893d27bb7abd1d5b01b1640207528a5c851`, using PR622's
  providers and PR623's dispatch. Frozen native artifacts are under
  `research/community-k492-audit/pr626/replay/mixed-global/base/providers/`.
  `RESULT.json` records their decompressed payload hashes, matching the supplier
  SPEC's semantic hashes; gzip container bytes are not used as mathematical identity.
- `GAP.json` pins the old interface source SHA-256. The relevant full transport
  is `research/complex-k492-owner-repair/code/hpe_audit_and_transport.py`:
  its prefix exclusions, `climb`, and cleanup checks already state these obligations.

Credit to Jeremy Kothe for the K-triangle and preceding helper constructions;
Chafik Boukhalfa for PR626; DreamingOfClouds for the cold-helper work; icekylinx
and the transport-audit lineage; Douglas Colkitt for the interface and maintainer
review; and the cumulative contributors credited in the frozen packages.
The frame obligation itself is pre-existing. The new contribution is the
independent enumerated-subspace checker and reproducible coverage regression.

Prepared for GitHub user **sk1-j** with substantial OpenAI Codex assistance,
including code, tests, investigation, and this note. Apache-2.0, as in the repository.
