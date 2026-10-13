import Lake
open Lake DSL
package communityParitySynthesis
@[default_target]
lean_lib CommunityParity where
  roots := #[`DyadicCertificates, `GaussianLattice, `GaussianScalarCircuits, `CommunityPrecisionProfile, `GaussianTensorExecution, `AuditAll]
