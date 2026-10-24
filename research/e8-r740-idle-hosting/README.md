# R740 joint retiming with idle-data hosting

Conditional kappa = 0.001245293130733870. Compose the fully reconstructed R740 word (the same final word as PR441) with PR442's idle-data hosting construction. The bit side has 9,376 live and 9,385 physical families, with 39,712 hosted residuals; the complex side remains PR442's 8,400 live families. Both rank deficits are 2,496.

This uses the additional hosting extension stated in PR442's PROOF.md. Its global operator argument is inherited as an additional mathematical assumption; finite placement checks do not independently prove that extension. All earlier all-size compiler, dirty-bank, restored-work, tape/common-grid, precision and analytic obligations remain.

Run `python -B research/e8-r740-idle-hosting/verify.py /absolute/new/output`. Standard library only for replay. The wrapper first freshly rebuilds the R740 producer, kernel, both joint retiming sweeps and every selected complex phase. It then regenerates the frozen hosting assignment, independently audits the windows, owners, remainders and full banks, and recomputes both moments, invoices and strict assembly. Discovery used scipy; replay uses frozen exact integers without scipy.

Full uninterrupted Python 3.11.15 and 3.14.8 wrappers PASS at commit `5702ed7fc47bc43333da0ccbcc013791c21aaa08`. Both freshly replay the final two-sweep parent and produce identical hashes for all five top-level logs. Receipts, logs and the exact tested manifest are in `local-evidence/`. GitHub CI remains pending. Executable code and witnesses are unchanged by this evidence publication. Exact moment-cost optimization and more general complete-bank constraints found no additional gain; their negative results are retained.
