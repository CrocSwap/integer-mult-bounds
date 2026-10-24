# Complete native identities from four tensor widths

For an n-axis binary affine map with a quadratic Gaussian phase, a fixed
scalar register identity holds at **every positive tensor width if and only
if it holds at widths 2n+4, 2n+5, 2n+6 and 2n+7**. The full map includes every
dirty input and every returned role. Four widths are necessary for this full
family: three widths always miss a global-phase residue class.

The [proof](PROOF.md) gives a constructive basis witness for every false
identity, encoded in O(n^2) bits. It also proves that phase-residue kernels
stabilize by width 2n+4. For this monomial group, this replaces the general
projective-alphabet bound `|G/Z|-1` used in the retained tensor-separation
argument. It does not give this cutoff for nonmonomial Cliffords.

This is an enabling proof and reusable exact checker. It does **not** change
the complete kappa calculation. Physical placement, cost, precision, stock,
compiler admission and the remaining selected theorem assumptions stay open.
The selected conditional value at the base is `60403/20000000`.

## Use the checker

Python 3.12 or later is sufficient. There are no third-party dependencies.
From the repository root:

```sh
python3 -I -B research/native-tensor-cutoff/native_identity.py \
  research/native-tensor-cutoff/examples/source-conjugation.json \
  --output /tmp/native-certificate.json
python3 -I -B research/native-tensor-cutoff/check_certificate.py \
  research/native-tensor-cutoff/examples/source-conjugation.json \
  /tmp/native-certificate.json
```

Expected output:

```text
IDENTITY_ALL_POSITIVE_WIDTHS
PASS_NATIVE_IDENTITY_ALL_POSITIVE_WIDTHS
```

The first tool compares canonical native group coefficients. It does not
construct the four enormous tensor matrices. If a coefficient remains, it
uses exact Fourier choices and a binary Gram factorization to construct a
counterexample in the proved window. The separate checker uses a different
composition formula for positive certificates and literal tensor basis
execution for negative certificates. It imports no producer or group-algebra
code. Both share `exact.py` and the declared program semantics.

The examples include the complete two-role identity for the actual nine-axis
event8814 recipe, a missing-global-phase mutation, a nine-axis projector that
vanishes at **all widths 1 through 8**, and two CNF reductions. The compact
nine-axis projector witness can be checked directly:

```sh
python3 -I -B research/native-tensor-cutoff/check_certificate.py \
  research/native-tensor-cutoff/examples/late-projector-9.json \
  research/native-tensor-cutoff/examples/late-projector-9.certificate.json
```

It prints `PASS_NATIVE_TENSOR_COUNTEREXAMPLE`. The witness has width 22 and
discrepancy one. Its first possible nonzero width is 9, by the written rank
argument. The generic producer need not expand this large projector to check
the supplied witness.

## Input contract

A problem has `axes`, `roles`, `generators`, `program` and `reference` fields.
Each generator uses the source recipe fields `matrix_rows`, `offset`,
`phase`, `linear_Z4` and `quadratic_rows`. The affine matrix must be invertible.
Quadratic rows use the strict upper entries, as in the pinned source. The
phase is evaluated at the input coordinate. A generator's constant phase
is multiplied by the tensor width; an external scalar coefficient is not.

Instructions are:

| op | Required operands | Meaning |
| --- | --- | --- |
| `add` | `src`, `dst` | `v_dst += coefficient * v_src` |
| `query` | `src`, `dst`, `generator` | Add the generator image of the source |
| `apply` | `dst`, `generator` | Replace the destination by its generator image |
| `scale` | `dst` | Multiply the destination by `coefficient` |
| `swap` | `src`, `dst` | Exchange the roles |

Coefficients default to one. They are integers, explicit rational strings,
or `[real,imaginary]` pairs of such values. Floats and exponent syntax are
rejected. `apply` and `query` accept a Boolean `inverse` flag. It denotes the
actual inverse of that generator. Source and destination can coincide.
The reference is a second program over the same inputs and generators.

All roles start as arbitrary independent inputs. To restore a borrowed role,
retain its identity endpoint in the reference. Explicit zero outputs are
allowed, but do not count as restored dirty inputs. External aliases, changing
recipes or coefficients across widths, nonlinear leaves, Hadamard operations,
and rectangular types require a different contract.

The implementation accepts 1..256 axes and 1..4096 roles. The theorem has no
such finite limits. Both CLIs have `--max-terms`, with a default of 100000
stored terms per program state. A resource failure is **no decision**. Sparse
expansion can be exponential. The proof shows that endpoint equality is
coNP-complete even with five arbitrary dirty roles, reversible instructions,
and commuting native sign generators. It uses Barrington's classical
permutation program construction and an explicit five-step controlled swap.
No clean scratch or erase is needed. It does not claim a fast general solver.

## Evidence

The [receipt](RESULT.json) is from the complete exact replay on macOS
with CPython 3.12.14. Normal and optimized isolated runs have the same output:

```sh
python3 -I -W error -B research/native-tensor-cutoff/verify.py
python3 -I -O -W error -B research/native-tensor-cutoff/verify.py
python3 -I -B research/native-tensor-cutoff/audit_mutations.py
python3 -B scripts/research_package.py --package research/native-tensor-cutoff
```

The replay checks all 33,866 symmetric binary matrices through dimension
five; all 2,192 phase characters through three axes; 100 larger cases through
73 axes; 1,152 native composition pairs and 19,328 literal native points;
120 complete circuits with 11,760 dirty-input basis checks; 4,444 complete
below-rank projector cases; 80 CNF formulas on 992 assignments; 480 reversible
branch pairs on 4,800 dirty basis columns; 120 full CNF circuit columns; five
committed examples; and 37 rejection controls. The actual source check covers all 512
one-column addresses and six tensor phase probes. The phase mutation is
invisible in 512 even-width cases and fails at the generated width-25 witness.

The [mutation receipt](MUTATIONS.json) records four changes to mathematical
code in private package copies. Every change must fail at its stated semantic
check in both normal and optimized Python. These eight failures check the
two-copy phase repair, constant-phase residue, native composition constant,
and final dirty return. The original package is not changed by the audit.

Finite checks corroborate the written uniform proof; they do not replace it.
The tools and proof are author-checked with substantial OpenAI Codex assistance.
No independent human or proof-kernel acceptance is claimed. No selected cold
replay, full native supplier, production packet, Lean or Docker run is included.

## Sources and credit

Base: canonical main `7c472563474e60185e6ca101a17622133d047e56`, priority
revision 7. [SOURCES.json](SOURCES.json) pins historical provenance.
[SOURCE-PINS.json](SOURCE-PINS.json) authenticates the six byte-identical
local source exports used by direct replay. No network or Git is needed by
the standalone verifier. The source fixture is the predecessor's supplied
event8814 recipe; the complete dispatcher/cover chain is not reproduced.

Jose Manuel (@jmbarrancoml) supplied [PR #2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250)'s recipe implementation, with
Douglas Colkitt's compact construction. JoyboyBrian and Cinna Davis supplied
the retained event/caller lineage. Chris R (@Clear1nsight)'s [PR #4928](https://github.com/CrocSwap/integer-mult-bounds/pull/4928) and [PR #4978](https://github.com/CrocSwap/integer-mult-bounds/pull/4978)
retain credit for their finite-alphabet tensor-separation arguments. The
phase-character sector construction in
[Discussion #2106](https://github.com/CrocSwap/integer-mult-bounds/discussions/2106)
also retains Jose Manuel's credit. The
binary-stream affine-basis argument retains @ywz65's credit and its distinct
F_2 scalar contract. The
related independent-operator and inverse certificate interfaces are zxv's
[PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235) and Krzysztof Wójt (@krzysztofwojt)'s [PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262). Lempel's binary Gram factorization, finite
Fourier inversion, Burnside-Brauer tensor generation, Pauli conjugation,
SAT completeness and Barrington's width-five construction are classical.
Exact links and distinctions are
in [PROOF.md](PROOF.md) and [SOURCES.json](SOURCES.json). No global literature
priority is claimed. The retained license notice is in [source/NOTICE.md](source/NOTICE.md).

## Open next questions

The proof lists three concrete next tasks: determine the least stabilized
width, extend the quantitative construction to a specified nonmonomial
Clifford group, or bind another complete native register word. Each requires
its own evidence. None is a completed physical supplier or a kappa claim.
