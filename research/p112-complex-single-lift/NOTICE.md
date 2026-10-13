# Attribution and license

Prepared for **@woklerx** with substantial **OpenAI Codex** assistance in
mathematics, implementation, independent agent review, testing, and writing.
The independent implementation and reasoning review are delegated AI work,
not independent human review or proof-assistant verification.

New files are contributed under the repository's **Apache-2.0** license.
Existing dependency files are read in place, unmodified. Their original
licenses and notices continue to apply.

- **Mihir Srivastava (@mihir-s-05), #845**: the real P112 single-lift
  theorem, annihilator argument, exact geometry implementation, certificate,
  and independent finite-premise checker. This package replays that evidence
  and extends the scalar domain; it does not claim its real obstruction.
- **DreamingOfClouds, #717**: P112 model, root/label conventions, and the
  open mixed-beta question. The source commit is
  `4150829a2cb66b823f4282da98985959ee448a90`; the inherited source notice is
  `../p112-single-lift/reference/PR717-NOTICE.md`.
- **Joel Pulikkan / GamingPuzzled, #620**, and predecessors: the coordinate
  P112 cost 64. **DreamingOfClouds, #446**: inherited copy-tree interpretation.
- **themilkman216, #968**: concurrent research on exact eight-term
  frame-pair decoders under punctures. It is related context, not a dependency
  or an independently verified result of this package.
- The selected #942 chain retains credit to **Jonathan Capalbo**, **Chafik
  Boukhalfa**, **Jeremy Kothe**, **Hao Yan**, **DreamingOfClouds**, **eumemic**,
  and the wider cited E8 construction community. This package changes none
  of those suppliers or their results.

The new contribution is the support-preserving complex-to-real single-lift
transfer lemma for any finite real matrix, its scoped P112 consequence,
and exact projection/negative-control evidence.
