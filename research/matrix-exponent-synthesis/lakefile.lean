import Lake
open Lake DSL
package matrixExponentSynthesis
@[default_target]
lean_lib MatrixExponentSynthesis where
  roots := #[`CommutingPhases, `DyadicCertificates, `FeasibilityNormalForm, `FiniteRationalChecks, `GaussProduct3, `GaussianLattice, `GaussianScalarCircuits, `LateQuotient, `MatchingDual, `RefinedFrontierCertificate, `SharpQuotient, `AuditAll]
