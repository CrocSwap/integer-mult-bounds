# Direct restoration replay notes

The final source-bound, standard-library replay passes with four worker
processes in 42.60 seconds. It independently rederives every one of the 184
hosted words, verifies the retained literal frame profiles, scans 131,788 scalar
recovery slots, and checks all 8,208 orders in 720 exact commuting-slot classes.
All 8,208 orders have a forced vector outside a target port-hyperplane end.
`RESULT.json` binds the executed source and inputs; `WITNESSES.json.xz` contains
the complete replay receipt and one explicit target-end witness per order.
The replay also passes three positive fixtures and four negative controls.

The source inventory contains 94 distinct retained words and 90 reconstructed
extra-orientation words, covering 92 hostee/host pairs in both orientations.
The archive has 95 original gzip filenames because one base word is duplicated.
All 95 original gzip and canonical-payload hashes were checked against the
frozen J source. All 90 reconstructed words have recorded passing forward and
dual source-auditor receipts. The current portable replay independently checks
all 184 literal derivations, exact frames, and recovery witnesses; it does not
rerun that separate free-operator semantic auditor.

There are 180 cases with minimum necessary recovery rank eight and four with
minimum rank nine. The 35,068 rank-eight slots are exhausted by the 720 classes.
All 115,780 sampled B boundaries are checked for a participating-register warp;
none has one, so sampling before boundary warps and inserting after them agree.

The candidate-frame check uses the zero-frame inverse-prelude repair recorded
in `USED-inverse_prelude.py.txt`. The operator lane separately supplies the
normalized equivalent repair and full-end semantic fixtures. Our negative
result does not depend on the operator normalization saving literal operations.

A target-end witness persists if only other helpers' end caps are enlarged:
those caps are upper constraints and do not feed this forward lower propagation.
This implication applies to the fixed scalar words, fixed warp interfaces, and
contiguous recovery blocks checked here. Staged recovery, a new scalar basis,
precomputed combinations, changed interfaces, or arbitrary hosted circuits are
outside the claim. No new kappa value is claimed.

Run `python3 -I -S -B direct/verify.py --workers 4` from the enclosing package,
or invoke that script by absolute path from any directory. `--workers` accepts
1 through 24, `--quick` selects six representative cases, and `--output` writes
an optional complete receipt outside the verifier directory. No optimizer,
third-party modules, network, git metadata, or source-directory writes are used.
See `PROOF.md` for the precise floor and commuting-class argument.
