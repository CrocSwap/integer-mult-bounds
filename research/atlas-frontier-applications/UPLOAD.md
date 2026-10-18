# Browser upload

Suggested branch: `research/atlas-applications-t372-20261015`.

PR title: **Apply the atlas: T372 concentration, mixed-fibre bounds and exact recovery**.

The exact body is in `PR-BODY.md`. Its first numerical paragraph explicitly distinguishes the improvement over pinned PR #2848 from the stronger PR #2853 claim.

Three extracted batches preserve the repository-relative layout. On the same branch, open the repository root's upload page and drag the **research** folder from each batch, in order:

1. `F:/proof/up/af372/01/research`
2. `F:/proof/up/af372/02/research`
3. `F:/proof/up/af372/03/research`

Do not drag the numbered batch directory itself. The final repository path is `research/atlas-frontier-applications/`. Commit each batch to the same branch. These batches contain the repository files, not archive substitutes. The complete package is available only after all three uploads.

The staging preflight hashes every copied file against the final source manifest and checks the exact union, recursive counts, file sizes and absolute path lengths. Each batch is limited to 80 files, each file below 25 MiB, and each local path below 240 characters. The separate local `PREFLIGHT.json` records measured values. These stricter batch counts fit [GitHub's documented browser limits](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository), rechecked on 2026-10-15. Byte-preserved files need no line-ending conversion during upload.

After downloading or cloning the final upload, run `python -B tools/verify_package.py --hash-only` from the package folder, then the independent offline command in `README.md`. This detects incomplete uploads or altered bytes. Browser and network errors can still occur; the preflight does not promise otherwise.
