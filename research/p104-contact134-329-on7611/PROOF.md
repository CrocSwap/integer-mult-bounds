# Contact134/329: exact return and complete recursive improvement

Indices below are zero-based in the authenticated #7611 word. Its canonical
JSON SHA256 is `177b74c42ac633aaee21b0bbd5373441ccba8e5bad029d827877cf2d585fd0e3`.
The emitted candidate canonical SHA256 is
`ff380ae02b238bdf41db5247a2278f7e7be391fe49879f91950fdb775a0f983a`.

| Source index | Source operation | Replacement |
|---|---|---|
| 41073 | MOVE134 3->618 | MOVE134 3->373 |
| 41074 | MOVE329 373->618 | Omitted |
| 41075 | ADD134 -=329/2 at618 | Same ADD at373 |
| 41166 | MOVE329 618->733 | MOVE329 373->733 |
| 42110 | MOVE134 618->913 | MOVE134 373->913 |

`build.py` requires each source literal uniquely, and checks the complete
incident windows. Field329 has no additional contact until its restoration at
733; field134 has no additional contact until its restoration at913. The other
instructions retain their relative order. The constructor also preserves every
other public MOVE, external header, scalar opcode/operand/coefficient and ordered
INIT/owned-MOVE/CLEAR event. Intervening-observer controls exercise these guards.

## Arbitrary arrays and absolute phase

Let F_j be the actual canonical phase-bearing chart operator. A MOVE a->b
implements F_b F_a^{-1}. Let x and y be arbitrary arrays initially held by134
at3 and329 at373. The original and replacement windows both return

`134_out = F_913 (F_3^{-1} x - (1/2) F_373^{-1} y)`

and

`329_out = F_733 F_373^{-1} y`.

For the replacement, this follows by expanding
`F_913 F_373^{-1}(F_373 F_3^{-1}x-y/2)`. This is equality of the complete
linear operators, including absolute phase. No clean input or independent-token
promise is used. Each changed field is restored before an exterior observer,
so every other public and owned array, including each actual pre-CLEAR value,
agrees with the immediate source. The argument applies to the values produced
by #7611's earlier premix because x and y are arbitrary.

The new frame bases are
`373=[30,321]`, `733=[30,42,193,321]` and
`913=[6,10,18,32,65,129,256]`; chart3 is empty.
Containment in913 follows from `30=6 xor10 xor18` and `321=65 xor256`.
The actual lowered quotients must have ranks2,2,5, respectively. Nesting alone
is not used as an execution receipt. `physical.py` checks six specified pairs:
the three new pairs `(3,373)`, `(373,733)`, `(373,913)` and the inherited
`(401,922)`, `(513,127)`, `(740,1071)`. It compares all 512 forward and 512
adjoint Gaussian columns with an independently authored canonical interpreter,
including absolute phase, and checks wrong-source, wrong-phase, missing-MOVE
and inverse-order controls.

The application checks the exhaustive union of 66 affected pairs. For each
pair and its adjoint, it compares the signed conjugation action on all 18 Pauli
generators and the exact image of the basis-zero vector. The six pairs above
also receive all 512 forward and 512 adjoint column comparisons in the
application; the other 60 are not claimed as dense column checks.

For unitary Clifford operators U and V, equality of the signed action on every
X and Z generator implies U^{-1}V commutes with the entire Pauli algebra. Its
representation is irreducible, so that commutant consists of scalar operators:
V = λU. Equality on the nonzero image of the basis-zero vector fixes λ = 1.
The argument applies separately to the adjoints and gives exact operator
identity, including global phase, assuming the retained exact interpreters and
unitary circuit semantics. The all-width lift and caller bindings remain
separate application obligations; the physical checks are not a complete
application receipt.

## Complete paid profile

The old four incident ranks are3,1,1,4. The new positive ranks are2,2,5.
Their rank sums both equal9. All external helper targets remain fixed.
Thus native deltaP is `{1:-2,2:+2,3:-1,4:-1,5:+1}` and deltaT is empty.
The complete caller contains17 actual native invocations, giving
`{1:-34,2:+34,3:-17,4:-17,5:+17}`. The caller's other QUERY, IDLE and target
terms must be independently reconstructed by the signed application.

For p=1-kappa in(0,1), the native recursive saving is

`G(p)=2+3^p+4^p-2*2^p-5^p`

`     =(2-2^p)+[(3^p-2^p)-(5^p-4^p)] > 0`.

The first term is positive and strict concavity makes the second positive.
This proves a favorable relative recursive profile throughout that interval.
The actual conditional claim additionally requires a positive complete moment,
directed comparison above the fresh #7611 raw upper, usable compiler slack,
ordinary/precision/tape and all58 outer predicates. `price.py` uses two retained
independent directed engines to test the fixed-invoice crossing and negative
derivative on the BIT interval. Executed results, the certified conditional
claim and separate completion history are recorded in VALIDATION.md and RESULT.json.

## Erasure and full application

The candidate's74 ordered pre-CLEAR rows must equal #7611 exactly. Against
#7605 only the inherited ordinal44 row changes, as stated in README. Both owner
identity and chart are bound at that occurrence. The retained paid reset scans
the whole coded private extent, including admitted residuals; a row-rank lemma
alone is not its physical or numerical admission. The inherited service,
allocation, child completion, precision and error assumptions remain explicit.

`independent.py` uses exact rational forward legality and a separately authored
reverse-output engine for all1569 final rows and all74 erased rows. Actual
candidate mutations exercise scalar delivery, coframes, paid-operation
presence, incident windows and complete17-call invoice validation. COPY retains
its ideal zero-destination guard and is not implemented as numerical overwrite.

`application.py` records counted source replacements, reconstructs the complete
native/signed chain, and requires a fresh candidate native result and matching
adapter ledger before signed execution. The source receipt, word hash,
launcher hash and actual native-result hash are bound; a stale7605 receipt is
rejected. Full application, compiler, ordinary, grid, precision, tape and
conditional analytic/58-outer checks passed on this composed word; the complete
receipts and inherited premises are recorded in VALIDATION.md.

These are finite conditional construction and verification claims. The five
framework assumptions and independent human/formal admission remain separate.

Historical #7610 remains credited as the preceding main46 contribution; #7611 supersedes that word.
