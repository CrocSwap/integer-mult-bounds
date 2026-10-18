# QQ16 obstruction with normalized Clifford+T coefficients

The alternative unread set from [PR2546](https://github.com/CrocSwap/integer-mult-bounds/pull/2546)
still cannot support complete-input recovery when its decoder gains normalized
Hadamards and eighth-root phases. The new result extends that work's explicit
Gaussian-dyadic boundary to `Z[zeta_8,1/2]`; it reuses and credits its full-input
witness. No read minimum, minor census, native controller or supplier is claimed.

## Result

Keep the unchanged F0/B1 pair, all arbitrary original inputs, and exactly the
PR2443 two-cut observations with unread set `H=[1,25,3,4,5,6,8,12]`.
All 224 granted observation arrays in the inherited witness have every entry
divisible by five, but the required original port `x_1` is one. The proper ideal
persists in the larger ring: reduction to `F25=F5[t]/(t^2-2)` sends
`zeta_8 -> 4t`, `i -> 2`, `sqrt(2) -> t` and `1/sqrt(2) -> 3t`.

[PROOF.md](PROOF.md) proves the ring homomorphism and ideal invariance under
every fixed finite linear circuit over that ring, including arbitrary finite
workspace with identical initial values in the two executions. Its explicit
gate subclass is H, S, T, X, Z, CNOT, SWAP, their inverses, tensor/direct sums,
permutations and dyadic linear operations. It does not assume the specialization
commutes with complex conjugation. Gate inverse identities are exact identities
before reduction.

The original unread set `H0=[1,2,3,4,5,6,8,12]` remains a passing dyadic-inverse
control. The alternative has a rational inverse with entry `1/10`, so this is
not an information-loss result over Q. Allowing an odd-denominator gate such
as `1/5`, nonlinear division, postselection, additional observations or a changed
first pair lies outside the result. The displayed family does not obstruct
selected-only recovery. Binding a complete native alphabet, chronological access,
retention, precision and a favorable total invoice remain separate obligations.

## Exact evidence

The checker independently evaluates the literal constant-array F0/B1 equations
from the authenticated retained packet, without importing predecessor code.
[RESULT.json](RESULT.json) retains all 224 original input values
(112 X and 112 Y), all 224 observation values, both eight-by-eight
inverse matrices, the field specialization and seven gate-prefix vectors.
It checks 56 individual inverse basis columns and a complete mixed word return.
The normalized H prefix actually leaves the earlier Gaussian-dyadic subring.

Six failure boundaries catch a wrong field relation, an odd denominator,
admission of inverse five, an omitted Hadamard normalization, a wrong phase
inverse and a changed unread witness. Separate export tests reject changed source
bytes, typed and semantic receipt changes and a missing receipt; an explicit
`--emit` mode prints a recomputation without writing package files.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/qq16-clifford-ring-obstruction
python3.12 -I -O -B research/qq16-clifford-ring-obstruction/verify.py
```

Expected primary output starts `PASS: source-bound 224 observations`.
[VERIFY.json](VERIFY.json) registers the primary checker and four export/control
groups. [SOURCES.json](SOURCES.json) pins main inputs by Git blob and SHA256 and
retains exact source READMEs for PR2546 at
`3aff4ccbfaa1005e5093e95535e4d99aa3813e54` and PR2443 at
`545c05e17243c962b112b91e7f84b4c1a41de7b8`.

The standalone replay also works in a Git-free export with the listed source
files. Default replay writes no artifacts and keeps checks active under `-O`.
The source-bound finite checks support the written proof; they do not replace
its induction for arbitrary finite circuits. Python uses dynamic allocation and
arbitrary-size integers, a managed-runtime deviation from fixed allocation.
Replay dimensions are fixed at 112 ports, eight centre coordinates, four ring
basis coefficients and eight gate rows; source input sizes are bounded before
parsing. No floating-point arithmetic or external mathematical library is used.

## Open next questions

Does a concrete proposed native gate or frame leave this ring and actually
permit the odd denominator? First derive its exact coefficients at the real cut,
then check whether five remains a nonunit. The current result does not bind every
native primitive. Alternatively, use the already admissible H0 basis and price
its complete chronological reads, frame maps, retention and cleanup. Neither
route follows from scalar invertibility alone. [TASK.json](TASK.json) records
the changed task scope, overlap coverage and structured handoffs.

## Credit

Nick Petalas's PR2546 supplies the alternative unread set, modular full-input
witness and prior Gaussian-dyadic obstruction; its explicit normalized-Clifford
exclusion is the boundary resolved here. starship-s's PR2443 supplies the
arbitrary-input rational decoder and two-cut contract. Gareth Davidson's PR2432
supplies the unread-column criterion and H0. Ali Romman and the retained QQ16
contributors supply the packet, conserved maps and cover semantics. Earlier
compiler/supplier attribution remains in the unchanged
[QQ16 notice](../joint-query/NOTICE.md).

Prepared by ywz65 with substantial OpenAI Codex assistance in mathematics, code,
checking and prose. New work is Apache-2.0. No human or proof-assistant
certification, native implementation or new kappa is claimed.
