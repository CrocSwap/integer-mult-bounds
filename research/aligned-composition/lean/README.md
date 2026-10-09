# Rational arithmetic supplement

The unchanged `AlignedFrameComposition.lean` is generated from `input.json` by `generate.py`. Its 197 theorems cover supplied count formulas, width/rank, accepted/rejected rational Taylor bounds, 47 slacks and seven margins. `audit_aligned_composition_lean.py` regenerates exact source bytes and compares the input to the recomposed certificate. Historical `sources.py` lists all 295 declarations, while `AuditAll.lean` explicitly audits every new theorem. The compile and independent audit receipts bind the exact original module and input.

This is rational arithmetic only. The actual physical profile derivation, real logarithm and exponential enclosure validity, and all-size multiplication transfer remain external hypotheses.
