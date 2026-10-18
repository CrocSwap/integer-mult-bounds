# One short, hash-verified browser upload

Branch: `research/kappa-action-theory-400-20261015`

PR title: **400 constructive theorems for changed-contract κ improvements**

The exact PR description is [PR-BODY.md](PR-BODY.md). No remote branch, commit or PR has been created by this package.

1. Open the root of your GitHub fork and select or create the branch above.
2. Choose **Add file → Upload files** at the repository root.
3. Drag **F:/proof/up/ka400/01/research** into that page. Drag the `research` folder, not `01` or `ka400`. The resulting repository paths must begin `research/kappa-action-theory/`.
4. Commit those files on that branch, then create the PR with the title above and PR-BODY.md. Check the preview includes all four `volumes/` files, the full theorem index and the review/source records.

There is one batch, with no archive required. Its 42 files are below the local 80-file target and every file is below 25 MiB; measured paths are below 240 characters. The source and upload copy have identical file sets and SHA-256 hashes. Exact measurements are in the sibling F:/proof/up/ka400/UPLOAD-RECEIPT.json. The sibling staging receipt is outside the draggable batch; UPLOAD.md is part of the repository package.

GitHub's current browser limits are 25 MiB per file and 100 files per upload; the batch uses the stricter local 80-file target. The drag-folder and new-branch workflow were checked against [GitHub's upload documentation](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository). These preflights address file/path issues, without promising every browser or network operation will succeed.

After upload, run `python3 -I -B research/kappa-action-theory/check_collection.py` from any Python-enabled checkout. It checks structure and bytes, not the proofs. Keep Unicode text and ordinary spaces; this collection is not ASCII-only.
