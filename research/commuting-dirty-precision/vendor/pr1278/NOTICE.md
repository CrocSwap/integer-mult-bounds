# Attribution

New proof, verifier, tests and documentation: Charles Bethin, with substantial
OpenAI Codex assistance, 2026. Apache-2.0.

The unchanged `vendor/dirty.py` and `PR905-PROOF.md` come from Chafik
Boukhalfa's retained PR628 and PR905 packages. Their notices remain in
`PR628-NOTICE.md` and `PR905-NOTICE.md`.
`PR1085-PROOF.md` and `PR1244-README.md` retain Hanson Sun's source text
and its AI disclosure. `SOURCES.json` records exact source commits,
original paths, Git blobs and SHA256 digests. The repository license
is retained as `vendor/LICENSE`.

The new recursive word constructor and polynomial/dense checkers are separately
written. AST isolation of the predecessor dispatcher follows the method
used in Hanson Sun's PR1244; the original function itself stays byte-exact.
Independent models do not constitute independent human review.
