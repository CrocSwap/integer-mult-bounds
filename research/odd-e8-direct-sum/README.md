# Odd E8 direct-sum decoder

This construction gives 1,404,928 rank-one binary ports in dimension 25,
an explicit dyadic fitting matrix of rank 20,480, and a decoder factorization
with pairing tariff 311,296. The tariff per port is 76/343, compared with
4/7 for the retained single P112 factor. These are different geometries.
The comparison does not replace any paid job in the selected supplier.

**No complete kappa improvement is established.** The missing step is a
native producer, its complete helper and restoration cost, and physical
COPY at the stated pairing tariff. The exact planning gate leaves less
than 1/9 per port per local call for the omitted work at exponent 0.0031.
This package supplies no complete invoice or multiplication theorem.
A second exact gate charges copies by source dimensions 15 and 22. It still
has positive allowance at 0.0031: between 1/4 and 3/10 per port, or less
than 1/10 per local invocation. This gives a possible alternative to the
smaller pairing-rank service; it does not supply a chronological program.

The [proof](PROOF.md) gives the all-odd-factor construction, the support
pairing formula, a local scalar involution, and the budget assumptions.
The [certificate](RESULT.json) and [verifier](verify.py) give exact finite
checks. [Source pins](SOURCES.json) bind the literal predecessor data to
canonical main `1a3ced60b2f7a46bc70280a04f2eeb8ca027c700`.

For k=2s+1 factors, the construction has 112^k ports in dimension 8k+1.
The fitting matrix uses only products of at least s+1 copies of the
rank-eight base matrix. A term with j active factors has source support
dimension 7j+1 and binary source/reader pairing rank 6j+2. The tariff per
port tends to zero as k grows. This does not bound native production cost.

For three factors, the 14 base sign cubes also give 2,744 product cubes.
On each, an explicit dyadic involution exchanges two orthogonal 256-port
classes. This is the scalar K part of K+H+F=I. A native H program and its
actual target readout order remain unknown.

## Verification

Use Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -I -W error -B research/odd-e8-direct-sum/verify.py
python3.12 -B scripts/research_package.py --package research/odd-e8-direct-sum
```

The direct command prints:

```text
PASS_ODD_E8_DIRECT_SUM_COMPONENT ports=1404928 dimension=25 rank=20480 pairing_mass=311296
```

The verifier checks all 12,544 base entries, all eight feature support
contracts, 7,168 feature-pair/fixed-label supports, 512 feature triples,
all 2,744 product-cube parity spans, and exact majority coefficients and
eigenvalues for odd k from 1 through 15. It regenerates RESULT.json and
compares it in full. Altered root and binary-label data, a reversed cubic
sign and an omitted degree-two layer must fail.

The proof handles the full fitting mask by a tensor support argument.
The enormous fitting matrix is not materialized or exhaustively enumerated.
The all-k statement is a written algebraic proof with finite corroboration,
not formal proof-kernel or independent human verification. No selected
native replay, compiler, Lean or outer admission command is part of this
package. The selected record is provenance only and is not changed.

## Open next questions

Can a direct H producer and its complete helper lifetimes fit the exact
remaining allowance in section 7 of the proof? First give its inputs,
physical charts, dirty reads, returns and paid/target profile. Stop that
schedule if its optimistic complete profile already exceeds the allowance.
The local K involution and decoder tariff cannot stand in for this program.

Can the degenerate source supports be gathered and read at the pairing
tariff with a complete physical COPY word? First implement one actual
rank-14 feature-pair term, including the 15-dimensional source support,
dirty compensation and cleanup. A rank calculation alone does not settle
this question. [TASK.json](TASK.json) records the structured obligations.

## Credit and scope

The input is Dillon's retained `coded-native-caller/NORMALIZERS.json`.
Its [physical source note](../coded-native-caller/PHYSICAL.md) records the
literal E8 normalizers and their lineage. Dugongue's
[PR #4929](https://github.com/CrocSwap/integer-mult-bounds/pull/4929) supplies
the stable rank-eight code and factorization. Retain Cao Yifan, Cinna Davis,
zxv, Jacob Alan Sussman and the E8/native/Clifford/compiler predecessors
credited in that source. None of their native caller results is re-proved
or claimed as new here.

Multilinear majority and tensor eigenspace calculations are standard
algebra. The contribution is their use on these literal direct-sum port
labels, the explicit decoder and support tariff, the product-cube core,
and the exact remaining-cost gate. No claim of a new general majority
identity or a minimum decoder tariff is made.

The [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19164011)
records the overlap check. This changes the port geometry under the
complex-rank-shape card; it does not optimize the old native word or the
peer-owned fused-T/Global120 caller. Bounded repository, PR and Discussion
searches found no matching active scope; this is not an exhaustive novelty
certificate.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
