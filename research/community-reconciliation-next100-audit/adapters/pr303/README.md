# PR303 historical-log manifest repair

The submitted tree omits `validation/supplier-verify.log`, but its outer manifest
requires that file. No scientific program reads it. The standalone helper removes
only that missing historical stdout-log entry; every scientific source, input,
expected certificate and assertion stays unchanged. The full original tree and
original manifest remain in the source-retention tag. REPAIR.json and manifest.patch
bind the exact before/after change.

After materializing PR303, run:

```sh
python3 repair_manifest.py --package /path/to/research/five-stage-gen5b-full-fixed-prime
python3 -B /path/to/research/five-stage-gen5b-full-fixed-prime/verify.py --output /fresh/output
```

This is a reproducibility repair, not a mathematical change. The review's execution
receipt states the result of the complete replay; merely applying this patch is not
verification. No Lean build or unconditional multiplication theorem is claimed.
