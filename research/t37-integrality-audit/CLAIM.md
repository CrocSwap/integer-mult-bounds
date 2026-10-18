# Local sprint claim

- Track: adversarial mathematical audit; OS assignment seed **65**.
- Base: `407d52ff15b2217b6e22bce44728b4c3907b6515` (origin/main fetched
  2026-10-13). Branch: `research/audit-seed65`.
- Object: the integer-count/equality step in PR942's fixed-U8 all-replica
  signed-dual relaxation, especially nonmultiples of 37.
- Method: derive the credit-slack lattice; certify a 37-state residue
  potential with exact rational interval edge bounds; exhibit relaxation
  witnesses and controls that remove one premise at a time.
- Deliverable: scoped proof, deterministic standard-library checker,
  source pins, exact certificate and negative controls. No new kappa,
  supplier, physical owner assignment or frontier edit.
- Expected finish: 2026-10-13 09:25 America/Los_Angeles. Reserve the final
  quarter for verification, independent review and packaging.

The three candidates were (0) the prime-power cyclic inverse circle proof,
(1) the disjoint-helper matching floor, and (2) integer consequences of the
all-replica signed-dual support inequality. Seed `65 % 3 = 2` selects the
third. The inverse family already has several open audits; the matching
floor has a complete integer-dual review. The selected obligation has a
qualitative equality statement, but no quantitative residue certificate.

Curiosity Bot checked the issue listing and current PR metadata immediately
before this local claim. No pinned sprint coordination issue was visible;
the two open issues were #913 and #650. No issue was opened to reserve work.
Queries for integrality and all-replica work found no competing quantitative
residue audit. This is bounded coverage, not a claim to have read every PR.

Overlap: Jonathan Capalbo's #942 proves the all-T support bound and
constructs T37. Chafik Boukhalfa's #890 exhausts a finite T<=22 relaxation.
Joel Pulikkan's open #962 independently constructs T37 and identifies its
optimal normalized profile. This audit credits those results and adds the
slack lattice, a uniform sharp numerator penalty in the arithmetic
relaxation, and all 37 residue-class certificates. It does not repeat their
construction or claim priority for T37 optimality.

Delegated review is confined to this same integrality step and certificate.
Stopping rule: prove/check the finite 37-state certificate and declared
controls, then stop; no broader supplier or parameter search.

## Result and handoff

Completed 2026-10-13. The audit derives the 1200-unit slack lattice and
sharp off-37 numerator penalty, with all 37 residue certificates. Both
checkers passed normally and under `-I -O -B`: 1,163 bin patterns, 1,591
edge inequalities, 37 witnesses, and 8 primary / 10 independent rejection
controls. The fresh overlap check also distinguished PR974's interface
budget study. No physical construction or new kappa is claimed.

Submitted one focused research-audit PR:
[CrocSwap/integer-mult-bounds #992](https://github.com/CrocSwap/integer-mult-bounds/pull/992).
No coordination issue was available, so this is the single local claim
update with the result and link. The selected frontier remains unchanged.
