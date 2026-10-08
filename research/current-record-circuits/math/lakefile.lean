import Lake
open Lake DSL
package currentRecordMath
lean_lib CurrentRecordMath where
  roots := #[`DirtyComplementSafety, `FreshKernelReclaim, `FiniteRationalChecks,
    `CircuitToggleSafety, `CurrentRecordCertificate, `Audit]
