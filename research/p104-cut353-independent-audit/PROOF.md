# Conditional independent audit of the cut353 retirement

This note audits the logical independent-input boundary in PR6716 at
`a467457692bc9e11113d9b2e2e34ea8ffb553b58`. It does not audit the common-idle
physical bank, native realization, complete invoice, claimed exponent,
compiler or outer transfer. The author-side construction and all earlier
methods retain their credit. The exact serialized controller data, rather
than the source's checker or constructor, are the executable audit inputs.

## Algebra and conventions

Write `u` for the source's operator `Q`, and retain only `u^4=1`. In the
source proof, `q=Q^-1=u^3`. All eighteen stage variables remain distinct
commuting invertible indeterminates. Computation takes place over

`Q(i)[u]/(u^4-1)[t1^+-1,...,t18^+-1]`.

There is no specialization of `u^2` to identity, no merging of stage
variables and no numerical evaluation. Every matrix cell is a finite
canonical Laurent polynomial with exact rational real and imaginary
coefficients. Put

`lambda=((1+i)/2)+((1-i)/2)u^2`,

`S=lambda*u^3=((1+i)/2)u^3+((1-i)/2)u`.

The LOCAL opcode is an assumed algebraic interface: first add `u^3` times
the source row to the destination row, then multiply both rows by their
named fresh stage variable. Its native physical implementation is not
executed or proved by this audit. LAMBDA, QUERY, ordinary row operations
and the one- or two-row IDLE actions use the literal source opcode
specification retained as inert text. An IDLE on two rows is two algebraic
actions; this audit supplies no license to merge two independent arrays.

## Why two-sided separation is sufficient

Let `P` denote the unretired prefix through event353 inclusive. The ordinary
vectors in the actual witness satisfy

`ab=cd=1`, `aP=S c`, `Pd=S b`.

Let `G,J` be the literal ordinary basis words in that witness. Their
required identities are

`e4^T G=c`, `Gd=e4`, `e4^T J=a`, `Jb=e4`.

Consequently `e4^T J P G^-1=S e4^T` and
`J P G^-1 e4=S e4`. Both off-diagonal couplings at the pivot vanish.
Thus this transformed prefix is exactly `S` on pivot4 and an independent
operator on the other 33 inputs. A row identity alone would not establish
this conclusion; the column identity is independently required.

The input basis uses only roles4,20,21. Their complete declared endpoint
targets are identical, so this ordinary basis commutes with that endpoint.
The full final-controller check below independently verifies the resulting
endpoints, rather than inferring them merely from this commutation argument.

## Literal handoff and full endpoint

The audit compares every event of the serialized retired word with the
following surgery on the serialized unretired word: inverse input basis;
prefix through353; middle basis `J`; inverse middle basis with pivot4
renamed to fresh34; remaining unretired suffix with that same renaming;
the three recorded lambda returns; renamed final `G`; and the three
recorded original-group lambda adapters. This is an exact event comparison,
including scalar signs and chronology.

No event through retired index362 uses role34; its first contact is363.
Its arbitrary input therefore remains independent until the handoff.
The original pivot receives `u^3` without stage factors. The new role
receives `t10*t11*t12*t13` without a central factor. All other targets
are taken from the unretired declaration. The final declaration is checked
against this independently assembled list.

The independently implemented forward matrix calculation checks all
35 by35 cells of the actual final word against that diagonal list. The
unretired controller is computed only through the prefix; its remaining
declared targets are the contract used to assemble that expected list.
The entire final controller is checked directly. This
establishes the stated logical endpoint simultaneously for arbitrary
independent inputs, conditional on the declared LOCAL interface and ring
relations. It is stronger than testing selected numerical inputs, but is
not a native supplier or all-size multiplication theorem.

The artifact retains all 68 prefix row/column cells and all 1,225 final
matrix cells. Default replay recomputes and compares those actual cells.
The ordered list of paid-opcode kinds, stage sets and central query signs
is also compared before and after surgery. That structural check is not
a complete price, native-caller or resource audit.

## Evidence boundary and credit

Both separately implemented blind first executions passed on
2026-11-04, finishing at 19:59:36 and 19:59:45 UTC. Every typed common
receipt field and every actual canonical polynomial cell agreed. The
common receipt SHA256 is
`9e9a7b5f05fc9e8824fc6206771625f91acf0aead53aae461cb0fdaf9afff6ef`;
the canonical packet SHA256 is
`ca09e50e074afde1af921461618e2f1d8349c643a16a6db0683f2a7efcd8e579`.
These are complete-value comparisons, not only selected summary counts.

The primary has ten rejection controls. Three execute actual changed
controllers through the full polynomial engine and require the intended
endpoint failure: reverse the first QUERY central sign, change the first
input-basis coefficient to -2, or append a central operation to fresh34.
Before the first execution, static review corrected a no-op dual-pair
control and replaced two expected-object controls with these actual-engine
mutants. Both earlier unexecuted code versions were preserved. These
changes were not reactions to a failed scientific execution.

Execution status and retained receipts are recorded separately in
`VALIDATION.md` and `RUN-RECORDS.json`; this written argument does not
substitute for an execution receipt. The source's existing independent
checker was not imported or executed. Reading its source during task
selection is disclosed in the scout record; the new implementation uses
fresh whole forward matrices rather than that checker's per-column and
reverse-row architecture. Independent AI work is not independent human
acceptance or proof-kernel verification.

Credit thu-nmrc/PR6716 for the exact root, witness, caller application and
complete claimed budget; DreamingOfClouds/PR6702 for the inherited native
word; Ali Romman/PR6348 andPR6398 and Cinna Davis's query/controller lineage
for the binary supplier and normalization; PR6545 and PR5599's dual-pair
retirement lineage for the method; and PR6551 for the earlier rebalanced
comparison. No invention of dual-pair retirement, native normalization,
productive recursion or binary refinement is claimed here. New audit
material was prepared with substantial OpenAI Codex assistance and is
Apache-2.0. The frozen source texts retain their original notices.
