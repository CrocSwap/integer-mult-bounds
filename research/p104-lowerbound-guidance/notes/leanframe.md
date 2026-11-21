# LEANFRAME (Sonnet, Nov 20)
Nov15/FrameCert.lean KERNEL-CHECKED: 61 s, 2.6 GB peak, axioms propext/Classical.choice/Quot.sound, no sorry/native_decide.
[C+P] certs_sound: for ALL 1152 7-dim frame-blocking Lams (normals u1,u2 in F2^9; Lam = ports with label orthogonal to both), F^perp ∩ F2^Lam = {0,1_Lam} (H_frame), F^perp = vectors even on all 759 frames (packed masks).
Cert: per Lam, for each p != p0 a sparse set of frame indices whose XOR restricted to Lam = {p,p0}; check = Nat bitmask decide +kernel; reflection lemma proved once. No Aut(P104) reduction needed.
all_or_nothing_real: AllOrNothing (embedded) instantiated, H_frame discharged; hyps left: H_FS4, A ⊆ Lam.
Non-vacuity: tampered cert rejected; untampered ok; every frame meets Lam0 evenly (parity form); length 1152.
Not certified in Lean: that the 1152 list is ALL 7-dim blockings (enumeration [C] from mod4/block.out), and that 'frames' = 759 frames (data from frames.txt).
Memory lesson: Elab.async false, 24 certs per theorem chunk, packed Nat data, mask-based lamMask/cover check.
gen.py + head/tail_a/tail_b + asm.sh regenerate the file (./asm.sh 0 out.lean 24).
