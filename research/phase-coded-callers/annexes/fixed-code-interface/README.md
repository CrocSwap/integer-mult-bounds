# Scoped support appendix

[PROOF.md](PROOF.md) states the accepted result and its limits.
[REVIEW.md](REVIEW.md) gives the separate independent proof review.
The original files under `frozen/` are unchanged and are bound by
[SOURCES.json](SOURCES.json). Historical review status is retained.

Use Python 3.10 or later and the standard library. Run from this appendix
with a new output directory:

```sh
python3 -I -B replay.py --out /tmp/fixed-code-interface-replay
```

The runner uses fresh copies, one process at a time. It runs normal Python
and Python with `-O`. Both complete receipts must match exact bytes.
The final line is `PASS_SCOPED_SUPPORT_PROOF_REPLAY`.
[VALIDATION.json](VALIDATION.json) records the independent publication run.
The replay does not prove the full native or recursive supplier contract.

This appendix preserves campaign work and uses substantial OpenAI Codex
assistance. Its new proof review is a separate agent calculation, not an
independent human review. The parent package retains the upstream source
credit and license. This appendix makes no complete kappa claim.
