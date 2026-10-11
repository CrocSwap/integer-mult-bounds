# Whole bit residuals pooled across four replicas

Conditional kappa = 0.001274494971185576, 0.006235410670839051% above PR460.
Submitted after changed-component checks and before completed full verification.
The unchanged complex supplier is PR458; the bit local word is PR459.

```sh
python -m pip install -r research/e8-r740-replica32/parent436/requirements.txt
python -B research/bit-whole-pool4/verify.py /absolute/new/output
```

The default runs the full PR460 composition and all changed checks. To reuse a
completed full PR460 output explicitly, pass --parent-output /absolute/parent;
the resulting receipt labels parent reuse separately. The fresh bit invoice
charges a529-bit physical-family prefix at576bits and the1640-bit composite
coefficient at1664bits. The inherited192/1024 charges are not reused.

Read PROOF.md for the whole-family argument, prefix induction and conditional
scope; SOURCE.json binds the exact parent and unchanged word. GitHub CI is
separate from local receipts. Initial evidence is a component screen only.

Parent portability update: PR460 now retains the terminal initial failure and
normalizes only two inherited discovery-float fields for PR458 reconstruction.
Pinned mathematical sources and exact checks are unchanged. SOURCE.json binds
the repaired parent manifest; full verification is pending.
