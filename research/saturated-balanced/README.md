# Saturated readouts with complete signed and balanced integration

Conditional **κ = 6398282083297/10¹⁷ = 6.398282083297×10⁻⁵**, with exact bit saving **31993457448237/500000000000000000**.

This integrates **Divjot Singh Manchanda's PR99 nondegenerate readout saturation** with **Zhihao Chen's PR97 complete reflected and signed interfaces**, then applies the **PR100 balanced positional transfer and refined exact arithmetic**. It exceeds PR100 by approximately 0.00609757%. It is effectively the same numerical saving as PR99's alternative A–E transfer; the contribution here is a complete reproducible integration into the retained signed/balanced interfaces, not a meaningful numerical improvement over that alternative headline.

The physical change is exactly PR99's: 22 readout frames expand by 25 dimensions. The complete histogram removes 177,100 singleton children while keeping recursive rank 57,403,754,177, width 108,516,254, 28,866 auxiliary roles and 32,408 formal input/scratch basis columns. No extra frame changes are claimed. Both tensor connectors, all copied centers, entrance/exit gauges, the signed complex correction and all intermediate gates remain paid.

The complete original PR97 forward/reflected bit ledger is regenerated on the changed frames. Both its scalar complete-basis replay and its full paid histogram are checked, alongside PR99's exact frame review. Full mode additionally reruns PR99's complete rational/generic-pivot/negative-control and scalar checks, and PR97's original native geometry checks. The complex physical word, correction, scalar envelope and complex saving 36926111/500000000000 are unchanged. All 47 strict constraints, seven margins, eventual cutoffs and two independently enclosed moments are recomputed. The next bit-saving and κ grid points are rejected.

```sh
python -m pip install sympy==1.14.0
python research/saturated-balanced/verify.py
python research/saturated-balanced/test_controls.py
python research/saturated-balanced/verify.py --full
make verify
```

Validation status: focused integration PASSED in 62.701 seconds, including both parent physical ledgers, PR99 exact review, the fresh candidate forward/reflected ledger, exact arithmetic and six controls. Repository-wide rerun pending. Independent pre-integration PR99 full checks passed in 231.150 seconds and PR97 candidate ledger replay passed in 12.414 seconds; these are preserved as prior evidence and do not substitute for the new committed-package checks.

See [PROOF.md](PROOF.md) for the extension and inherited assumptions. All-size ordered-frame compilation, exact routing/recovery, scalar control and the analytic fixed-alphabet/tape transfer remain conditional. No new formal Lean theorem, global optimum or measured runtime gain is claimed.

**Credit:** Divjot Singh Manchanda / djsmanchanda and Codex for nondegenerate saturation; Zhihao Chen / jacklightChen and Codex for PR97's fan ordering, full reflection, gauged endpoints, signed phase correction and integration; Swapnil Jain and the retained Claude disclosure for round7/round6 networks; James Chang/PR34 and RaD/hipotures for the balanced layout; Avi Eisenberg/ikeboy, Paureel, icekylinx, Chafik Boukhalfa, Dominik Scholz, eumemic, Douglas Colkitt, OpenAI and all predecessors. PR99 is vendored without source changes, retaining its Apache license, notices and original authorship. The same sharper baseline moment also appears independently in SovereignSteak's PR102. This composition was prepared by Rohan Arun with OpenAI Codex assistance.
