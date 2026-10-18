# PR242 shell-launcher portability repair

The original verify.sh contains CRLF line endings, so Bash rejects pipefail before
running a check. This separate LF launcher takes PR242_SOURCE_ROOT as its source
root. All original package bytes remain unchanged and pass FILES.json checks.
The original tree also omits 28 files already pinned by FILES.json. MISSING-SOURCES.json
identifies exact matching retained Git blobs; restore_sources.py supplies those bytes.
The unmanifested source_inputs.rar convenience archive is retained outside the
checked package root. Its bytes and original location remain in the source tag.
No stage, coefficient, compiler command or assertion is removed.

Run `PR242_SOURCE_ROOT=/path/to/source527-five-stage-crossover bash verify-lf.sh`
with the original package requirements and the platform C++ include configuration.

After materializing PR242 and fetching the source-retention tag, run
`python3 restore_sources.py --package /path/to/source527-five-stage-crossover --repository /path/to/repository`
before the LF launcher. This does not change any verifier or replace a differing file.
