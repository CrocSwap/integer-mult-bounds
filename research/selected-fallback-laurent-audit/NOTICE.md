# Attribution and retained sources

New audit code and prose: @CubeJerry, with substantial OpenAI Codex assistance.
Apache-2.0, following the repository's root LICENSE.

The following files are preserved byte for byte from Jose Manuel's
(@jmbarrancoml) PR2207, commit
`149d55d90d3c0877ed3d78e1deca8eb2f72e0d00`:

- `vendor/fallback_program.py`: the compiler under test.
- `vendor/descriptor.py`: commdata2338's PR2188 implementation, already
  vendored by PR2207, including its source527, Ross Richardson and Jose
  Manuel attribution.
- `vendor/controlled_normalizer.py`: Jose Manuel's PR2171 arithmetic module,
  already vendored by PR2207, retaining normal-form predecessor attribution.
- `vendor/PROOF.md` and `vendor/NOTICE.md`: PR2207's claim and original
  notice, retained as source evidence. The original notice describes the
  source package's inventory; this package retains the three Python files
  listed above and does not import or retain `controlled_stream.py`.

Exact original paths, commits, Git blob IDs and SHA256 values appear in
SOURCES.json. Their mathematical claims and implementations are not new
audit contributions. The symbolic arithmetic, operator oracle, fixtures,
failure checks and scoped independent evidence are new here.
