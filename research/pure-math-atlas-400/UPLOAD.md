# Browser upload handoff

The deliverable is staged as one batch under **F:/proof/up/pma400/01**. Open the root of the repository you choose, create branch `research/pure-math-atlas-400`, choose Upload files, and drag the **research** folder from that batch. This preserves `research/pure-math-atlas-400/...` and keeps the repository's root README intact. The files have not been uploaded or published.

All intended files are extracted Markdown, JSON and one Python validator; there are no archive substitutes, binaries, caches or logs in the batch. Each staged file is byte-checked against the final source manifest. The union of this single batch is exactly the intended atlas tree.

Our preflight keeps the batch at no more than 80 files, every file below 25 MiB, and every absolute staged path at most 240 characters. GitHub's current documentation allows up to 100 files per browser upload and 25 MiB per file; the stricter local batch cap is retained. See [GitHub's upload documentation](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository), checked 2026-10-15. The structural record is [PREFLIGHT.json](PREFLIGHT.json); the completed staging receipt is F:/proof/up/pma400/UPLOAD-PREFLIGHT.json.

Use the exact title and body in [PR-DRAFT.md](PR-DRAFT.md). These limits and hashes address local packaging; they do not guarantee a browser or network upload will succeed.
