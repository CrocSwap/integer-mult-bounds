# Round37 adversarial accounting audit

Seed67; frozen base ce7ad1b6ab09452c3478723a2e96ed5ff212dc08. Audit the full-matrix transpose of the selected R480 FULL cleanup after PR696 primitive lowering. Paid overwrite COPY has a two-primitive transpose (ADD and CLEAR), so mechanical transposition need not preserve cost. Establish the exact primitive count gap, full arbitrary-input scalar boundary, and a shortest two-register witness. Compare with independently lowered transposed macros; do not claim a flaw in PR696, PR830, or selected native code, or a new supplier/profile.

Candidates rejected: arbitrary fixed-exponent profile-root ordering is already refuted by batch1099; generic private-work transpose contracts overlap PR830. This narrow audit concerns the unit-cost overwrite-COPY distinction and exact complete R480 cleanup accounting. PR1032 instead optimizes a contracted factory caching policy.
