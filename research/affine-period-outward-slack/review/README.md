# Independent lead review

The final frozen proof, all eight source pins and normal/optimized replays were checked. ROOT-REVIEW.md gives an alternate lower-bound proof, the family proof audit and failed-premise examples. The root checker imports no author checker and authenticates the retained kernel before compiling its exact bytes. Its rational rotation is the classical 3/5,4/5 example, not a new construction. Source-bound corollaries inherit the original finite certificates; those tables were not rerun.

From this package directory:

```sh
python3 -I -W error -B reproduce.py
python3 -I -O -W error -B reproduce.py
python3 -I -W error -B review/check_norm_slack_root.py kernel.py
sha256sum --check CHECKSUMS.sha256
```

Expected status values are PASS for the first two and PASS_ROOT_AFFINE_PERIOD_SLACK_REVIEW for the separate root replay. Direct runs write no package files. Prepared for @CubeJerry with substantial OpenAI assistance; this is AI-assisted independent reasoning and code, not human or proof-kernel approval.
