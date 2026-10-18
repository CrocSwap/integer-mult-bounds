# Local route 8 claim

Base: `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`.
Branch: `codex/k9-fast-phases`. Start: 2026-10-13 18:04 UTC.

No pinned sprint issue was supplied. The coordinator records the claim locally.
The current PR metadata lists PR1038 at `99c71d385171480ecc2c43287aa4a04e1027fcd9`
and PR1054 at `6bc675be1554b3a3be771147f21f9dc2c6dae50a`.

Candidate 1: use two reversible rounded complex phase states, a fixed second
difference, and exact backward reconstruction. Pay logarithmic guard precision.
Candidate 2: use exact modular angle state and blocks of polynomial values.
This needs a paid polynomial table or repeated evaluation at block boundaries.
Candidate 3: prove a work/error tradeoff for noninvertible rounded products.
This does not give the requested reversible implementation.

Chosen object: the first candidate, for all integer numerators, positive moduli,
finite positive lengths, and working precision at least two bits. Prove a uniform
quadratic drift bound. Use bounded three-shear charts. Prepare two seeds with
exact rational series, then clear their arithmetic state. Reverse the phase
state after every data pass. Keep the inherited borrowed-array count fixed.

Expected result: an executable scalar phase interface with O(L) stream work,
polynomial seed work, full dirty-target error, and a separate bit/tape bill.
The complete kappa calculation is still complex-supplier bound. This result
can remove a phase-interface expense; it does not change a supplier invoice.
No new kappa is claimed. Expected finish: this research session, after checks.

No random search is used. PR479, PR948, PR985, PR1038 and PR1054 are
predecessor or scope references. PR1054 is not combined by assumption.
