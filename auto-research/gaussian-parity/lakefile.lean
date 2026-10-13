import Lake
open Lake DSL

package gaussianParityCertificates where

@[default_target]
lean_lib GaussianParity where
  roots := #[`DyadicCertificates, `GaussianLattice, `AuditAll]
