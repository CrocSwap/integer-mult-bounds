# Disclosed repairs on separate copies

Original submissions remain unchanged in the source-retention tag. Run `repair_source.py PR SOURCE --git-root REPOSITORY` only on a newly materialized copy of that PR's package. The adapter checks all existing executable and data hashes before making changes.

- **#350:** remove the manifest entry for an absent historical `retime/retime.log`. The subsequent full replay regenerates the source-aligned word, geometry, bank and complex certificate checks.
- **#355 and #360:** remove the absent `.gitattributes` entry only. All mathematical inputs and checks are unchanged.
- **#390:** restore 104 missing files from exact Git blobs matching the submitted manifest; move the additional convenience RAR outside the checked root. The submitted manifest is unchanged. `pr390/RESTORE.json` pins every restoration.

`MANIFEST-REPAIRS.json` records original and resulting manifest hashes. `../EXECUTION.json` and `../logs/` retain both original failures and repaired runs. Initial #386 and #388 failures were reviewer invocation errors (missing sibling directories and a required source argument); the corrected #386 replay passes unchanged source. The corrected #388 invocation exposes the original missing-log manifest failure; the separately pinned, complete #391 repair covers that same candidate.

#379 is not repaired this way: its absent receipts accompany a more substantive missing replay of the actual new candidate, and it remains open.
