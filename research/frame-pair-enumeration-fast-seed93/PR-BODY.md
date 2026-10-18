PR968 repeatedly scans eight-element neighborhood lists during its complete
frame-pair split census. An exact mask representation preserves the full
ordered solution stream and makes this kernel 4.57x faster in three paired
trials. A separate D/E/H replay is 2.97x faster on the recorded Windows run;
this is not a whole-repository timing claim.

Both paths retain all 1,260 frames, 7,168 decoders, 57,344 term-rank checks,
25 attainment cases and six inherited controls. Ten additional controls
check source binding, malformed inputs, stream tampering and preservation
of source assertions under an optimized caller. The complete canonical
receipt matches; benchmark timing is excluded from mathematical equality.

Reproduce: `python -I -O -B research/frame-pair-enumeration-fast-seed93/verify.py`.
Only this new package is added. Sections A/B/C/F/G, native suppliers and
the full theorem are outside this replay. No new kappa is claimed.

Credit themilkman216's PR968 enumeration and proof checks; parallel PR1071
and PR1077 address different mathematical questions. Prepared for @woklerx
with substantial OpenAI Codex assistance. Apache-2.0.
