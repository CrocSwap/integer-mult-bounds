# Notice — mixed-point verify masks

Douglas R. Colkitt authored the mixed-point / early-sharing screens, the
`Circuit` recurrence and interning, and the original exact-intersection
support checks consumed by this tooling package.

This package adds an equivalence-preserving closed-form rewrite of the
historical `|source ∩ target| = r` expected-support genexpr inside
`Circuit.verify`, with identical True receipts, matching output supports,
and updated source pins only.

Prepared by Wentao Li with substantial AI assistance, under Apache-2.0.
