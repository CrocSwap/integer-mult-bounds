# Attribution and license

Prepared for **@woklerx** with substantial **OpenAI Codex assistance** in
mathematics, implementation, independent computational checking, tests, and
writing. Two delegated Codex workers stayed within the supporting-inequality
scope: one checked the mathematics and wrote the proof and independent checker;
another reviewed the proof and implementations. No independent human peer
review or proof-assistant verification is claimed.

New files in this directory are contributed under the repository's
**Apache-2.0** license. No upstream source or predecessor notice is replaced.

- **Chafik Boukhalfa (@chafreaky), PR795 and PR890:** signed helper prices,
  capacity bonuses, fixed-family inventory, and owner-relaxation ledger.
- **Jonathan Capalbo (@jon314159), PR942:** the pointwise supporting inequality,
  formal T37 equality profile, all-replica bound, and separately verified T37
  owner construction. This package extends the inequality to a real interval;
  it does not repeat the owner construction or claim its kappa improvement.
- **Charles Bethin (@cbethin), PR850:** the earlier continuum result for the
  fixed 72-call (T=8) integer owner optimum. Its stronger fixed-T conclusion
  remains distinct from this package's all-T fractional envelope.
- **Joel Pulikkan (@GamingPuzzled), concurrent PR962:** independent T37 owner
  reconstruction inspected for overlap. This package does not consume its code
  or depend on its pending review status.
- The retained U8/T16/T21 family credits **Jeremy Kothe, Hao Yan, icekylinx,
  NewBArch**, and the earlier controller, supplier, and arithmetic contributors
  identified in `research/complex-t37-owners/NOTICE.md`. Their construction
  results are inherited context, not newly reproduced evidence here.

Source bytes and relevant dependency heads are recorded in `SOURCES.json`.
The two new checkers use only the Python standard library and import neither
the predecessor arithmetic engines nor one another.
