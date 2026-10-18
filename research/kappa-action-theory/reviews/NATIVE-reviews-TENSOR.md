# Independent cross-review of T001–T100

Result: no unresolved theorem-level finding in the corrected final draft. This is an independent informal mathematical review by the native-volume worker, not a kernel audit, physical supplier admission, or numerical κ verification.

## Checked scope and corrections

I read every statement and complete proof of T001–T100 and their shared conventions. I checked coefficient identities, arbitrary-input extension arguments, returned reconstruction data, finite-search qualifications, arithmetic versus bit charges, and the distinction between bilinear queries and the actual linear native operator. I then read all corrected blocks back; T008 and T068 received one additional conservative readback after the final hash changed.

The following findings are resolved:

- T008 now retains both a right-form/product temporary and a separate decoder accumulator: r+kq+2 field cells. It assumes no hidden fused multiply-add instruction.
- T042 specifies a K-linear output functional extended to L-valued coefficients and includes qd base-field work for the readout contraction.
- T049 requires integers p ≥ 2 and s ≥ 1 before its logarithmic Newton-lift count. The two-sided inverse argument over the final commutative residue ring is present.
- T068 requires b ≥ 1. Its explicit O(n+1) and O((n+1)(nb+1)²) wrapper bounds include n = 0, where only zero operands satisfy the input bound.
- T079 correctly states that a forward difference lowers degree k to k−1 and multiplies the leading coefficient by k.
- T084 counts inverse generators: at most 2t(q−1)^3 directed edges. It assumes no complete stabilizer generating oracle.

These changes correct storage, parameters or arithmetic accounting without changing the intended identities.

## Native and source interfaces

The F1 opening explicitly says that a low-rank bilinear table is not automatically an implementation of the incumbent's linear arbitrary-column C word. Actual source embedding, input/output adapters, native realization and the complete charged consumer remain required. T006 and T038 rely on bilinearity already established from the construction; basis probes do not prove an arbitrary black box bilinear. T021 and T040 return or verify actual mode matrices instead of using bare orbit existence as a free adapter.

The restricted and quotient-source entries retain their explicit embedding/section maps and either recover every required label or state the changed consumer. T033–T035 start from verified matrix units; they do not assume algebra recognition free. T082–T090 give actual finite witness searches, supplied roots and coefficient checks, without solving unrestricted TI/TI_SL by assumption. The transpose statements have explicit fanout accounting and are algebraic duality, not automatic physical quantum duals.

I independently read the canonical source bodies listed below. The ratio relation and row map in T037 match CodeMatrixRecovery; T045–T046 retain CodePrimeFieldDescent's actual graph equations and nonzero private maps; T086 retains the actual determinant-product and recovered-root hypotheses. No scope was expanded to unrestricted GL/SL orbit equality. Other source records were read in the author's ledger but were not independently replayed here.

## Exact recovery, complexity and scope

The extension-descent chapter pays for base-field coordinates and actual recovery. T042 does not infer simultaneous dr descent for every output. T049 lifts a known matrix inverse, not arbitrary nonlinear tensor equations. Interpolation, jets and border extraction construct the finite decoders they use; they do not equate border rank and exact rank. The strict CRT/height inequalities, explicit denominator data, signed-centred convention and rational uniqueness proofs in T057–T070 are sound. T059 costs polynomially in D rather than log D; T062/T083 retain their stated motif-scale or exponential preprocessing.

T061 gives an actual denominator-cleared bit invoice and exact final division. T098/T099 retain their scaled-residue and fixed-modulus conventions. T100 requires actual prime/root data and returns signed multiplication through ordinary convolution, CRT and carries; it supplies no free prime generator or new exponent claim. T091–T095 use exact structured-product identities on their specified domains. Their selected-address or parameter transforms do not authorize mixing the independent cover label, a distinction the volume states explicitly.

The proofs therefore supply local actionable constructions and sufficient interfaces. They do not infer a complete paid κ gain merely from a lower variable-product count. Global recurrence, actual native realization, recovery and whole-package admission remain distinct mathematical results.

## Exact reviewed-source ledger

```json
[
  {
    "path": "drafts/TENSOR.md",
    "sha256": "91c2071736aba07084610ed404a8ce6ce171ddc7924f6cdd371f8b3329f04761",
    "review": "Complete manuscript and source-ledger read; final index hash bound"
  },
  {
    "path": "drafts/TENSOR-index.json",
    "sha256": "e096b806b1d9b6a256f3a7265025558eb7f0979f033beebaf4087e1e24992250",
    "review": "Complete manuscript and source-ledger read; final index hash bound"
  },
  {
    "path": "reviews/TENSOR-self-review.md",
    "sha256": "57cb2514e18d8116febee5066ba4efa2e0e8cae0c0dfb9130fe14d00924a73ef",
    "review": "Complete manuscript and source-ledger read; final index hash bound"
  },
  {
    "path": "D:/proof/lean/mathproof/Mathproof/Meta/CodePrimeFieldDescent20260913.lean",
    "sha256": "5921e1d6510f5465e2b21f3b79032d10ab20870fa409220a91a820258ddcc40f",
    "review": "Read actual source bodies: map_eq_mul_of_generator_commutes; private_generator_commutes; two_graph_rigidity; no new kernel execution"
  },
  {
    "path": "D:/proof/lean/mathproof/Mathproof/Meta/CodeMatrixRecovery20260913.lean",
    "sha256": "ddbf5968a7ef5667139dec9f6075e6ac5a9badae8ea55c998583261a70342231",
    "review": "Read actual source bodies: diagonal_relation_of_ratios; reconstruct; reconstruct_from_ratios; no new kernel execution"
  },
  {
    "path": "D:/proof/lean/mathproof/Mathproof/Meta/TISLTwoPowerCertificates20260909.lean",
    "sha256": "cb83e43d573fbbb61be0585a9fad31b3c5f248ae2da97d21b6b526ddb129a169",
    "review": "Read actual source bodies: certificates_iff_two_powers; slRel_of_product_and_tensor; slRel_iff_exists_product_tensor; no new kernel execution"
  }
]
```

The final manuscript hash was checked before and after writing this review. All 100 numbered entries were reviewed; this does not claim review of every registered theorem, historical PR or transitive dependency of the inspected Lean files. No Lean process, Jev request, canonical source edit or live DAG edit was used.
