# Compensated birth-read reuse

Author-checked conditional kappa=5519166047173/50000000000000000=1.1038332094346e-4. Independent review pending.

Run from the repository root:

    python3 research/birth-read-reuse/run_checks.py

Python3.11+ standard library only. The runner hashes its four base inputs and reconstructs the graph, matching, frames, birth pairs, exact readout bill, both frame directions and assembly in a temporary directory. Original individual stages took0.3,2.0,16.1,0.8,0.8,7.2 and0.4seconds respectively; each reconstruction stage has a30-second/512-MiB cap. No upstream script is imported or executed. Frozen JSON/gzip inputs and receipts are preserved.

PROOF.md contains the operation and conditional theorem. BIRTH_MATCHES.json.gz contains every donor/recipient/frame pair and the complete paid profile. CANDIDATE.json contains exact moments,47 inequalities,7 margins and all changed guard/row constants. BIRTH_AUDIT.json records the complete forward/reflected frame checks; READOUT_COST.json records exact signed coefficients and their paid literal expansion. Existing base notices and attribution remain in force.
