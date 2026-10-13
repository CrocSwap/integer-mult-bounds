# Attribution and license

New contribution by **Ross Richardson (@RossRichardson)**, with substantial
**OpenAI Codex assistance** for research selection, construction, code, proofs,
verification and writing. A separate AI worker implemented the integer-dyadic
checker and Prim/census check without importing the construction algorithm;
another reviewed the two-sided identity and native interface. This is not
independent human peer review. New files use the repository's **Apache-2.0**
license; see `../../LICENSE`.

The mechanism combines and reprices ideas from:

- **David Awad, PR807**, restored CK helper pairs,
  `b1a5c533a22c2665600102d872f6a84e0664a70d`.
- **@dd-hemant, PR816**, signed CK target forests,
  `133735a2cc2319c12ba5d786214b2217e083e7da`.
- **Sricharan Vagvala, PR749**, rational JP8 restored target pairs; and
  **Oscar Fennell, PR759**, binary target forests and superroot reduction,
  as credited by PR816.

No pending implementation is copied or vendored. The new construction and
checker are written for this experiment. No additive combination of predecessor
savings is assumed, and no priority claim is made for either individual basis
mechanism.

The unchanged retained inputs and native scripts carry their existing notices:
**icekylinx**'s PR425/433 scalar/compiler lineage, **DreamingOfClouds**' framed
extensions, **Jeremy Kothe**'s PR622 supplier and **Chafik Boukhalfa**'s PR626
owner-repair package, with the earlier cold-end, frame, residual, source-gauge,
physical-owner, bit-supplier and recurrence contributors recorded in the
repository's `CONTRIBUTORS.md`. Those notices and source files remain unchanged.
