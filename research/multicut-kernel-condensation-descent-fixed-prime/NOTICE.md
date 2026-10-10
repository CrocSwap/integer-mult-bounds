# Attribution, source and licence

This extension is distributed under Apache-2.0; the full licence is in `LICENSE`.

- Dugongue's PR263 (whose package is PR259's with the descent retiming stage) supplies the 518-entrance multi-cut kernel construction, physical witness, native checks, and finite invoice. Its source package, proofs, contributor notices, and OpenAI Codex disclosure remain intact at `research/multicut-kernel-condensation/`.
- The construction builds on the pinned PR249 source package and preserves its original author, licence, and assistance notices in `vendor/UPSTREAM-NOTICE.md` and the included source archive.
- The fixed-prime density and finite-level method originate in Gabriele Nespoli's PR235. Rohan Arun's PR252 is credited for the related fixed-prime adaptation to PR249. The later PR255 and PR258 refinements are acknowledged as public work on the predecessor profile; this extension applies the same public arithmetic method to PR259's 518-entrance profile.
- This extension's exact profile recomputation, eight-level certificate, verifier, documentation, and CI integration were prepared by sennemmi with substantial OpenAI Codex assistance.

All new files are Apache-2.0. Original source licences and assistance disclosures remain applicable. These credits do not imply review or endorsement by the named contributors.

This package is sennemmi's PR261 fixed-prime refinement (itself after Gabriele Nespoli's PR235 and Rohan Arun's PR252), retargeted from PR259 to PR263 by Rohan Arun with Anthropic Claude assistance: only the pinned base candidate, profile constants and the resulting exact endpoint change. Apache-2.0.
