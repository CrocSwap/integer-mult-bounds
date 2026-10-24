# Complete partial signed-Pauli native contracts

A set of partial native-chart conjugation constraints can match all binary
labels and commutators and still be impossible because its exact central
Pauli relations disagree. This package gives the complete all-size criterion,+a constructive literal dyadic Clifford word, and the exact number of
**projective** Clifford completions. It does not infer an absolute-phase target
from conjugation data.

For Hermitian equations `U P_i U^-1 = Q_i`, compatibility means equal label
relation spaces, matching symplectic pairings, and equal actual central phases
in all generator relations. [PROOF.md](PROOF.md) reduces the latter check to a
basis and proves sufficiency using at most two transvections per independent
label followed by a Pauli sign correction. It constructs actual source `turn`,
`x` and `s` gates, with no clean ancilla or discarded data. A one-qubit example
`X→X, Z→Z, Y→−Y` passes the unsigned tests but fails because `X Z Y=−iI`.

If the label span has dimension `k=2r+t`, symplectic rank `2r` and radical
dimension `t`, the compatible count is

```
2^(2n-k) |Sp_(2(n-r))(2)| /
    product_(j=0)^(t-1)(2^(2(n-r)-j)-2^j).
```

The theorem covers every nonnegative n. The reference implementation is
explicitly bounded to `n≤9` for native-source calibration. This is a scoped
written proof with finite exact corroboration, prepared for **JoyboyBrian**
with substantial OpenAI Codex assistance. Classical Witt, symplectic and
Clifford structure retain credit; no literature-priority, independent human
or proof-kernel acceptance is claimed.

[Canonical claim and status](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19140242).

## Actual caller and phase contract

Dugongue's retained native Clifford compiler (#4841) accepts a full literal
word or an unsigned Lagrangian, then emits phase-exact free adapters around
one rank-d Gaussian call. This supplies its missing entry contract from
incomplete signed operator constraints. Every live dependency is pinned at
main `f259dabc7d70e0db8d6d36bfda888f008bbfecc1` in
[SOURCES.json](SOURCES.json). Source files remain unchanged; the original NOTICE.md and LICENSE are also
exported byte for byte with their full predecessor attribution.

The checker authenticates the source before loading that exact file with
`runpy.run_path`, which reads source bytes directly rather than an imported
bytecode cache. It calls the actual `tableau`, `compile_word`, `replay`, `state`
and `lift_word` functions on eleven newly completed words. Nine small cases
have all input columns checked; the additional three-bit case has eight
columns, and the nine-bit case has the complete signed tableau plus its exact
zero-state column checked by the source compiler. These are focused calls,
not a replay of the predecessor's complete historical suite.

`I` and `−I` have the same signed tableau. The API chooses one literal word;
it does not promise equality to a separately supplied word with that tableau.
The source's actual negative-identity word and exact amplitude anchor witness
this distinction. Tensor controls retain global phase `i^(a*f)`, and the
all-width conclusion tensorizes each base letter separately. No sum is
silently tensorized as one letter.

## Independent finite evidence

The separate literal oracle builds full Pauli monomial matrices and computes
conjugations by matrix composition, independently of the implementation's
phase formula. Complete closures give all 24 one-qubit and 11,520 two-qubit
projective signed Clifford tableaus. For a canonical representative of every
possible source-span symplectic type, it compares **every distinct target
restriction** and its realization multiplicity:

| n | Source index sets | Distinct restrictions |
|---|---|---:|
| 1 | empty; X1; X1,Z1 | 31 |
| 2 | empty; X1; X1,X2; X1,Z1; X1,Z1,X2; full | 15,271 |

All **15,302** returned words are independently evaluated gate by gate by the
literal oracle, not merely tested for membership in a full group. Five semantic
rejections, five malformed-input rejections, scalar/zero-dimensional controls,
the negative-identity anchor and widths-two/three global-phase controls are
recorded in [RESULT.json](RESULT.json). This is the precise bounded coverage;
it is not enumeration of arbitrary-dimensional input constraints.

## Reproduce

Use Python 3.12 and its standard library:

```sh
python3.12 -W error -B scripts/research_package.py --package research/signed-pauli-partial-extension
python3.12 -W error -B scripts/check_research_commit.py --package research/signed-pauli-partial-extension --check-source-history
```

The registered hook runs normal and optimized Python. Direct `verify.py`
works in an official committed export without Git or network access. It reads
the deterministic type-sensitive receipt and never modifies it. To generate a
fresh receipt use `verify.py --write /a/new/file.json`; an occupied path fails.
The receipt authenticates local proof/code/metadata and live source bytes.
Python managed allocation and arbitrary-precision arithmetic are diagnostic
software, not physical constant-time operations.

## Full ledger and stopping decision

The uniform compatibility, construction and projective count are proved in
the written argument. The literal gates and phase boundary are constructively
specified and bound to the source compiler. One rank-d lowering is an inherited
conditional compiler statement; the constructed word gives `d≤n`, not an
optimal paid-rank theorem. A profitable changed consumer, all owner endpoints,
physical movement, precision, stock, source-uniform funding and outer supplier
admission remain unknown. The selected κ stays 0.00302015.

The decision is **narrow**: stop at this complete partial operator entry API.

## Open next questions

1. Minimize paid rank among compatible completions. First specify actual
   partial operator constraints from a changed chronological caller and its
   complete allowance. The present existence/count theorem does not optimize
   Fourier rank or prove a net paid saving.
2. Match a supplied absolute-phase target. First provide its exact nonzero
   amplitude anchor; a full signed tableau still leaves its scalar free.
3. Bind one useful completion into a whole owner-typed caller, retaining
   frozen endpoints and every incident transition. Missing physical costs,
   precision and stock block any supplier or κ conclusion.

Credit Dugongue for #4841's native compiler and explicit phase/anchor contract;
Cao Yifan / intqwq #4610, Cinna Davis, zxv, Jacob Alan Sussman, the retained
Clifford/native/owner/compiler lineage and Bravyi–Maslov normal-form background.
Source notices remain intact; new material is Apache-2.0.
