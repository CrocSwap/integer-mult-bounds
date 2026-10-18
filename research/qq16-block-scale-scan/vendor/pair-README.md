# A bit-circuit invoice for the rounded QQ16 Gaussian pair

The finite QQ16 format in [PR2807](https://github.com/CrocSwap/integer-mult-bounds/pull/2807)
leaves bit arithmetic open. This package supplies one literal Boolean circuit
for its signed nearest-even pair, including a runtime binary rounding exponent.
For four arbitrary signed `w`-bit components, `L=w+2` output bits and
`0<=d<=L-2`, the emitted gate counts are

```
fixed d:    52L-4d+8
runtime d: 24Lk+52L+4*2^k+4k+4,  k=bit_length(L-2).
```

The basis is AND/XOR/OR/NOT, with free wires, constants and fan-out. The sign
is fixed per circuit. The runtime circuit includes exponent-controlled barrel
shifts and discarded-bit tracking; finding the exponent from the input array
is separate. [PROOF.md](PROOF.md) proves exact signed behavior and sufficient
widths for all positive `w`. The counts are constructive, not optimality claims.

Conditional on PR2807's within-line range bound, its 456-bit example fits
`w=453`, `L=455` and needs 124,028 gates per pair with runtime `d`, or
`23668-4d` for fixed `d`. Its 336-line pair-kernel subtotal is at most
`20836704*lambda*N*D` gate evaluations. This closes one explicit arithmetic
term. Scanning, scalar ADDs, wrappers/maps, control, routing, storage and the
consumer are additional work. No recursive child tariff, complete physical
invoice, reversibility, supplier admission or new kappa follows.

## Evidence and reproduction

[circuit.py](circuit.py) emits and evaluates the actual acyclic gate lists.
[verify.py](verify.py) imports no predecessor executable. A separate direct
signed-magnitude rational oracle checks every four-component input for widths
1 through 4, both signs and every legal exponent: 689,728 assignments against
each circuit variant. Another 320 cases per variant cover signed extrema,
ties and seeded wide inputs through 1,024 bits, including the 453-bit example.
The receipt records actual gate-kind counts, rather than just a formula.

Six semantic controls change literal gates or the static sign: forced upward
ties, omitted sticky bits, a corrupted sign-extension wire, broken addition,
omitted runtime shift selection and the wrong native sign. All are detected.
Twelve invalid width/sign/scale/input cases reject. Five artifact groups check a
Git-free read-only replay, altered source bytes, boolean-for-integer receipt
corruption, missing evidence and exclusive deterministic regeneration.

Run from the repository root with standard-library Python 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/qq16-rounded-pair-bit-circuit
```

The registered commands repeat the full replay normally and with `-O`, then
run artifact controls. Direct read-only replay works without Git:

```sh
python3.12 -Werror -I -O -B research/qq16-rounded-pair-bit-circuit/verify.py
```

`--write` creates a missing RESULT.json and refuses an overwrite. No other
command writes artifacts. Source snapshots and their exact Git/SHA256 pins are
in [PREDECESSOR.json](PREDECESSOR.json). The selected record is unchanged.

## Scope, costs and implementation limits

This is an irreversible combinational arithmetic construction. The binary
exponent range is an input contract, not an included validity-check circuit.
All input/output wires have explicit widths. Fan-out, wires, constants and
sign extension cost zero only in the stated Boolean model. Mapping those
wires to physical tapes or reversible gates needs a separate invoice.

The supplied Python builder is a bounded reference, not a fixed-allocation
machine implementation. Power-of-Ten rule 3 deviation applies to its managed
integers and collections. Width is capped at 4,096, each truth batch at 65,536
assignments, source files at 40,000 bytes, JSON artifacts at 100,000 bytes and
verification at the fixed 36 small circuits plus 320 wide cases per variant.
The gate and live-wire capacities follow the displayed formulas; there is no
recursion, external solver or predecessor execution. Follow-up fixed-allocation
or tape work must allocate from these bounds and account for its own accesses.
The bounds constrain the checker, not the quantified theorem. Python warnings,
compilation and the available Ruff diagnostics cover the new executable files;
no hardware synthesis, physical timing or static type proof is claimed.

The independent internal mathematical review used Fraction nearest-even on
81,920 scalar-round cases and a separate pair/range check. It also reviewed
the final source. This is automated internal review, not independent human or
formal-kernel verification. Native semantics and the predecessor's all-cut
error/range bounds remain inherited. No selected cold replay is claimed.

Revision-5 family decision: narrow and stop at this kernel. A finite bit
circuit cannot justify expansion without the actual caller and complete costs.

## Open next questions

Can an admitted recursive child meet this relative rounding contract at a
favorable complete cost? Pin its actual input encoding, compute its exponent
scan and kernel-evaluation cost, and add movement, restoration and consumer
charges before comparison with the caller's allowance. The missing admitted
representation and complete caller budget block that transfer. Further local
gate optimization alone is not the recommended next construction round.
Structured details are in [TASK.json](TASK.json).

## Credit

New circuit, proof and checker by Nick Petalas, under Apache-2.0. The signed
pair and finite range are from Nick Petalas's PR2807/2771 and the PR2736
error contract, retaining ywz65's PR2707/2540, Arham Tahir's PR2681, Ali Romman
and the QQ16/native/geometry lineage. Ross Richardson's floor-grid and
reversible-lifting results in [Discussion2727](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727)
have different rounding/restoration contracts and retain their credit. The
retained source notices are unchanged. Ripple carry, guard/sticky rounding
and barrel shifts are standard; this contribution is their explicit signed
kernel, source-bound application, literal invoice and replay. Substantial AI
assistance was used for analysis, implementation and checking; responsibility
for this author-checked contribution remains with the contributor.

## Maintainer integration note

The historical selected record is provenance only: the circuit, arithmetic
oracle and finite-format snapshots do not read it. Its original hashes remain
in SOURCES.json; it is removed from runtime inputs so unrelated selected-record
maintenance cannot invalidate this local result. Scientific code and RESULT.json
are unchanged. The integration replay runs with that live record absent.
