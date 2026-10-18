# R480 private-center adjoint audit and CLEAR/COPY omission atlas

**Independent finite verification. No new kappa.**
Both intact R480 scalar programs erase arbitrary private-center input and restore
all dirty helpers. Their complete maps pass on all **712 input and output coordinates**.
The complete private-center CLEAR/COPY omission atlas contains **40 sites** and **32 rank-one defects**.

Eight backward initial clears are invisible to an endpoint check that initializes
every private center to zero. With arbitrary incoming center contents, those
mutants corrupt **103–111 persistent outputs**. This is additional fault coverage,
not an error in the intact construction or a claim that full admission accepts mutants.

| Orientation | CLEAR/COPY sites | Rank-zero sites | Ordinary-input visible | Private-input only |
| --- | ---: | ---: | ---: | ---: |
| Forward | 24 | 8 | 16 | 0 |
| Backward / inverse transpose | 16 | 0 | 8 | 8 |
| Total | 40 | 8 | 24 | 8 |

The exact base is `c0e3631dc24e3c24a861f7d3d79e0608481cccec`.
Its selected result is PR1094, with conditional kappa
`836330098538459/500000000000000000`.
The [review](../../docs/research/community-batch1099-review.md) and
[reproduction script](../../scripts/verify_frontier1094.py) retain PR1042's
seven-slot R480 local word unchanged. The source here is the actual `slots/local/`
program inside `research/community-frontier1042-audit/selected-replay.tar.gz`.
The historical R492 `evidence/local/` files are not used.

## Reproduce

From the repository root, run this offline command with Python 3.12:

```sh
python3 -I -O -B research/r480-private-center-adjoint80/check.py
```

Expected final line:

```text
PASS_R480_PRIVATE_CENTER_PACKAGE coordinates=712 matrices=42 omissions=40 private_only=8 no_new_kappa
```

The command writes nothing and needs only the standard library.
It reconstructs every certificate field and checks every mutant matrix twice.
Both implementations retain their acceptance conditions with Python optimization enabled.

Run the additional failure and portability checks:

```sh
python3 -I -O -B research/r480-private-center-adjoint80/test_package.py
```

Expected: four tests pass. They include all eight private-only witnesses,
singular COPY/CLEAR laws, 2,000 integer arithmetic comparisons, certificate
corruption, source corruption and optimized minimal offline relocation.

## Precise obligation and new evidence

Coordinates `0..703` represent `L0..L703`: 112 data registers, 112 targets
and 480 dirty helpers. Coordinates `704..711` represent `C0..C7`.
The forward map is `T_i <- T_i + S_i`. The backward map is
`S_i <- S_i - T_i`. Other persistent coordinates retain identity.
Every private output and every private input column is zero in the intact map.
The inverse-transpose description applies to the persistent block.
The full 712-coordinate map is singular because it erases eight private coordinates.

This package interprets literal scalar macros. It omits non-scalar events from
the scalar projection and does not execute their frame, phase or child semantics.
Private coefficient-work primitives are outside this macro-level 712-coordinate model.
The intact maps certify the stated finite scalar obligation, not the physical compiler.

The domain contains every CLEAR or COPY with a private-center target in both
frozen programs. Each mutant deletes exactly one such macro.
No other event, frame field, scalar coefficient or instruction order changes.
The atlas stores the exact defect, its source sensitivity and its output response.
It classifies detection on all ordinary input columns, including private output rows.

For example, delete backward event **12551**, `clear C0`.
Set initial `C0 = 1` and every other input to zero.
The intact program returns zero in every coordinate.
The mutant returns `L0 = -1` and 110 other nonzero persistent values.
Every private output still equals zero.
The defect is zero on all 704 ordinary input columns.

| Center | Backward initial-clear event | Persistent outputs affected by `C_k = 1` |
| --- | ---: | ---: |
| C0 | 12551 | 111 |
| C1 | 12577 | 106 |
| C2 | 12603 | 110 |
| C3 | 12629 | 107 |
| C4 | 12655 | 104 |
| C5 | 12681 | 105 |
| C6 | 12707 | 103 |
| C7 | 12733 | 106 |

For all eight cases, the exact defect is `u_k e_Ck^T`.
Thus the mutant agrees on every input with `C_k = 0` and differs on the
recorded unit private input. A caller that guarantees zero incoming centers
uses a restricted contract. This audit distinguishes that contract from arbitrary
private input. It does not require the stronger contract everywhere.

The eight rank-zero cases are forward initial clears overwritten by the next COPY.
Their deletion preserves the scalar map on all inputs.
This scalar redundancy does not establish legal native gate removal or a supplier gain.

## Independent methods and certificate

[verify.py](verify.py) uses reverse-mode covectors with exact rational arithmetic.
It imports no construction, production checker or predecessor implementation.
It checks the two complete endpoints and all 40 omission matrices.
For each omission, a separate prefix/suffix calculation verifies
`Delta = u v^T`, followed by direct scalar-value execution of its witness.

[forward_check.py](forward_check.py) independently constructs all **42 complete
matrices** with normalized integer rows and dyadic denominators.
It imports neither `Fraction` nor the primary checker.
It checks every matrix digest, defect factorization, classification, site and witness.
The two implementations share only the pinned data and certificate format.
Both are part of the same AI-assisted contribution.

[CERTIFICATE.json](CERTIFICATE.json) contains every exact factor and nonzero
counterexample vector. Sparse-vector entries use one line each for review.
Regenerated certificate comparison uses all canonical JSON fields.
[PROOF.md](PROOF.md) derives the adjoint rules and the rank-one deletion identity.

## Selection, sources and scope

The fresh OS assignment seed is **80**, selecting independent verification.
It selects candidate three and C0 as the first witness.
The complete 40-site domain is covered, with no sampling, timeout or pruning.
The stopping rule is one census, exact verification and handoff.
[CLAIM.json](CLAIM.json) records the three candidates and the local claim.
No pinned coordination issue existed.

[SOURCE-PINS.json](SOURCE-PINS.json) binds the published archive, its replay
receipt, the PR1042 checkpoint and four consumed archive members.
The original archive has a byte pin. Compressed member pins cover decompressed payloads.
[BASE-SELECTED.json](BASE-SELECTED.json) preserves the selected context at the base.
The selected PR1094 source head is `0fc329d0bec93ca7cd288eaea1295172e8789810`.

Predecessor credit:

- **Sagar Thakrar, PR745**, head `fc6ebccca3bd61a6eaf6ec3fcbf2e99d2888c35c`:
  historical JP8 reverse-mode audit and one dirty-center witness.
  This adds the actual R480 maps, every private CLEAR/COPY omission, all eight
  private-only defects and exact prefix/suffix factors.
- **Ryan Haines, PR835**, head `333fc042b87da01c8dbac46e9fbe549933242d5c`:
  a different, bounded modular endpoint check on historical SW4.
- **PR1049, PR1149 and PR1153:** leaver scalar/frame, canonical-rank and
  forward primitive checks. This atlas concerns a distinct omission obligation.
- **woklerx, PR1174**, head `5d2d0472a4843bf4b0858453d3eb5931ac19fbbb`:
  paid COPY transposition on cleanup with coefficient-work dirt.
  That audit excludes center lifetimes. This atlas covers private-center macros
  and does not price transposed primitive implementations.
- **Jeremy Kothe's PR1004/1005/1018/1042 construction**, Rohan Arun's PR987
  slot discovery and PR1094 packing, Hao Yan's controller, Chafik Boukhalfa,
  icekylinx, DreamingOfClouds, eumemic and the retained construction lineage.

The programs are scalar-only projections of the selected local word.
The package does not replay native frame/Clifford/phase execution, physical hosting,
the global invoice, precision/tape, coefficient-work lowering or outer assembly.
Full compiler, common-label/mutable-source, analytic and bit-interface assumptions remain inherited.
Finite exact matrices are not a formal proof of the all-size multiplication theorem.
The selected frontier, paid profile and `upstream/` remain unchanged.

Prepared through **@Scratch-net with substantial OpenAI Codex assistance** in
research, implementation, proof, verification and writing. Apache-2.0.
No independent human review is claimed.
