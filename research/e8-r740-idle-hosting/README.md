# R740 joint retiming with idle-data hosting

Conditional kappa = 0.001245293130733870. Compose the fully reconstructed R740 word (the same final word as PR441) with PR442's idle-data hosting construction. The bit side has 9,376 live and 9,385 physical families, with 39,712 hosted residuals; the complex side remains PR442's 8,400 live families. Both rank deficits are 2,496.

This uses the additional hosting extension stated in PR442's PROOF.md. Its global operator argument is inherited as an additional mathematical assumption; finite placement checks do not independently prove that extension. All earlier all-size compiler, dirty-bank, restored-work, tape/common-grid, precision and analytic obligations remain.

Run `python -B research/e8-r740-idle-hosting/verify.py /absolute/new/output`. Standard library only for replay. The wrapper first freshly rebuilds the R740 producer, kernel, both joint retiming sweeps and every selected complex phase. It then regenerates the frozen hosting assignment, independently audits the windows, owners, remainders and full banks, and recomputes both moments, invoices and strict assembly. Discovery used scipy; replay uses frozen exact integers without scipy.

Changed-program checks pass. Full uninterrupted Python 3.11/3.14 wrappers and GitHub CI are pending. The preceding one-sweep R740 retiming passed both full wrappers; those earlier receipts remain historical.
