# LEANUPHASE (Nov 20) - lean/decoder-duality/Nov15/FutureAttr.lean (~830 lines, ~12 s, 2.1 GB via runlean.sh)
Kernel-checked; axioms of every headline = [propext, Classical.choice, Quot.sound]. Imports Nov15.PriceLemma (olean built into .lake/build/lib/lean/Nov15/PriceLemma.olean).
Landed: ARun (run + attribution bookkeeping, class F = GTD + cold intake as constructor premises), Inv/inv_of_run (exact identity
 v(X t)-v0(X t) = sum_r W r t * v r + closed rows, chart invariant, lifetime potential dim(A+B+Z) <= dim A + lc), price_le (rank <= dim B - dim(B^A) <= lc via PriceLemma.exact_price),
 attribution_decoder (decoder, Sum price <= R), mass_le_R, R_ge_of_wall (Wall N explicit hypothesis), Toy.toy_run (1 port, one GTD lifetime, R=1, mass<=1).
NOT done: item 3 (transpose / class P).
Gaps / sharpenings vs UP.md: (1) ADD needs d != e (self-add breaks the telescoping). (2) chart condition chart d <= chart e suffices (same-chart special case).
(3) cold-intake is needed at the OWNED register's chart at intake (weaker than the public's); owned->owned reads carry zero weight but are intakes of the reader (must be cold, GTD).
(4) any read of an owned register into a public counts as an output (sets B, forbids later intake) even if its weight is 0; relaxing to nonzero weight is a different class.
(5) final-data hypotheses used: x-parts of finals (target 1 on own x, 0 elsewhere), non-target publics cold at their FINAL chart, target y-part Fy (side info allowed; eff uses full Fy), receipts zero x-part, X injective, owned start 0, publics never descend, no public INIT.
(6) The decoder identity is for receipts = final - start on odd cells; the "-I" form needs start y on odd cells = 0 (data, not used by the law).
(7) Q96 and the value 56 are not in the file: Wall N Q Rec is a hypothesis.
