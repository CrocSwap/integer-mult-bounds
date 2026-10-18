# Claim (recorded locally; no sprint coordination issue exists)

- Track: complex supplier (assignment seed 29, from OS randomness,
  `RNGCryptoServiceProvider`, value 29 in 0-99).
- Base commit: `f567884aeb8851b6e794af1184119a3bfbe1e631`
  (origin/main at assignment time).
- Object: the pinned P6k4 complex word
  (`0390ec65dc4d47df1887aabdc2ec5b6ddea3cfc8e65582873fdfeba81d100073`,
  input of `research/complex-sw4-frame8/construction/sw4/SW4-RECIPE-P6k4.json`),
  specifically simultaneous FULL entering-copy read-set exchanges.
- Method: independent pair enumeration plus exact one-pass frame refit and
  paid-profile pricing under the credited SW4 rewrite/frame semantics;
  complete enumeration of all C(38,2)=703 pairs and C(38,3)=8436 triples of
  the legal full single-pair exchanges on bare P6k4. Candidate order shuffled
  with `random.Random(29)`; per-candidate outcomes are order-independent.
- Deliverable: this research note with committed evidence
  (`EVIDENCE.json.gz`), an independent verifier (`verify.py`), and either a
  supplier-level improvement or a scoped negative result.
- Overlap: PR #775 (coupled partial read exchanges on P6k4) explicitly
  excludes all-full combinations ("It does not exclude ... simultaneous full
  exchanges"); no other open PR enumerates simultaneous full exchanges.
  PR #873 works on bit-supplier R439 blocks (different object and side).
- Result: scoped negative result, no new kappa. All 9,139 combinations are
  frame-legal; none beats the SW4 word by the credited floating-cost proxy,
  and none dominates it componentwise. See README.md.
