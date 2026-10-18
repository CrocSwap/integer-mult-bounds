# Local task card (written before substantial computation)

Task ID / proposed scope key: `bit-new-register-model` (scope key `7084092dd726e7ba1f2f`),
chooser track `bit-mechanisms`, OS nonce `96dd0470d4d1febfb9db9174583232e0`,
refined object: **even (order-3) diagonal targets** `T_t = diag([c],...,[c])`,
`c = ab = (ba)^2` in the formal `F2[GL_2(F2)]` rank-one-idempotent register model.

Base commit; exact predecessor and dependency heads:
- base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`
- predecessors (read-only, pinned): PR1333 `7f25b6d0e1d7e995d4d2840f231d98b1a1a9fec2`
  (Gareth Davidson; model and alphabet), PR1414 `9e1640094f649ba6db9742796825a8d6c238989b`
  and PR1491 (commdata2338; transposition-target line), PR1705
  `ad6b7d641b3e8576a95add7981fa75b6a8278fbc` (Aaron Wang; `t = r = 4` SWAP targets and
  the recorded `r = 4` ball sizes), PR1722 `246cd6b3a795a346bc6a741661ddcdb2d6359103`
  (label saturation, context), PR1478 `b30fdba48f3db70e3589ba740b0782b56ec0ba2e` /
  PR1573 `0b8c5a69297c794f2de22c04494c83e41300ae36` (UT3 commutator line, context).

Concrete object and question:
With `c = ab` the order-3 element of `GL_2(F_2)`, what is the exact paid-call
minimum `q*(t)` for `T_t = diag([c],...,[c])` (`t` copies) at exactly `r = t`
registers (all registers arbitrary dirty inputs restored exactly), paid calls
`I + ([g]+1)N`, `g in {a,b}`, `N = v phi` any binary rank-one idempotent with
`phi(v) = 1`, and free scalar `GL_r(F2)` mixing at zero cost anywhere? The
direct word is `(I+([a]+1)N)(I+([b]+1)N) = I + ([c]+1)N` per target, i.e.
`2t` calls. Can cross-register sharing beat `2t` at `t = 2, 3, 4`?

Scope status: **refined** within the card's allowed variation
"Choose a fixed larger register count or a specified nonabelian operation
family"; the target element class is changed from the studied transposition
targets to even order-3 targets, which flips the sign-quotient invariant.

Existing restriction being changed (or exact claim being audited):
the predecessor line (PR1333/1414/1491/1541/1705/1722) studies transposition
(SWAP) targets, where the sign quotient gives `sum_i N_i = D_t` with `t > 0`.
For even targets the same argument gives `t = 0`, i.e. `q` even and
`sum_i N_i = 0`; the known invariants' premise changes and none of the
predecessor conclusions transfers.

Method; explicit parameter ranges/candidate alphabet:
exact complete meet-in-the-middle censuses in the entrywise natural image
(2-dimensional representation of `S_3`, used only for exclusion), every
accepted word re-verified exactly in `M_r(F2[G])`; written free-layer
(Magnus) invariants with the exact `F2[G]` kernel correction; two separately
written engines cross-check on all small balls. Ranges: `t = r in {1,2,3,4}`,
`g in {a,b}`, all 6 / 28 / 120 binary rank-one idempotents of `F2^r`,
free `GL_r(F2)` mixing anywhere.

Nearest overlapping PRs and why this adds something:
- PR1705 / discussion 1715 / the live balanced ten-call four-SWAP residual:
  transposition targets at `r = 4`; different target parity and invariant.
- PR1478 / PR1573: UT3 commutator targets (different group `UT_3(F2)`), now
  closed at `4k` for all registers; no order-3 `GL_2(F2)` tuple is covered.
- PR1496 / PR1567: `GL_3(F2)` targets and mixed `GL_3` pairs (different group).
- 1337isnot1337's live claims (discussion 1317, 07:09Z-07:24Z): heterogeneous
  `GL_2`/`AGL_2` tuples `diag([a],[b],[aba])`, `diag([h],[h])`, `diag([a],[b],[h])`
  at `r = 2, 3`; different tuples (transposition-bearing), different alphabets.
- `find_overlap.py` refresh for `order-3 target`, `3-cycle target`, `cyclic
  target`, `even target`, `diag([ab]`, `order-three`: no competing claim.

Optimistic full cost budget; required observable improvement:
No kappa and no supplier claim (register-model local bill only). The
optimistic local saving would be `q < 2t`; if no such word exists, the exact
minimum `2t` itself is the deliverable (a scoped negative result closing the
two-calls-per-target tariff question for this tuple class through `t = 4`).

Success evidence; falsification test; time/compute cap:
Success = complete empty meets at every shorter even length in the natural
image, an exactly verified attaining word in `M_r(F2[G])`, and written
invariants checked on the attaining word. Falsification = any shorter formal
word found by the meet (then verified coefficientwise). Positive controls:
PR1705's recorded `r = 4` ball sizes 240 / 32,651 / 3,639,920; minima 2 at
`t = 1` and 6 for two SWAP targets at `r = 2`; drop-one-call mutation fails.
Compute cap: about 40 minutes of engine time (depth-3 ball at `r = 4` is the
measured wall).

Predecessor authors; intended artifact and reproduction command:
Gareth Davidson (@bitplane), commdata2338, Cinna Davis (1337isnot1337),
Aaron Wang (PR1705), Ross Richardson (PR1722), juper997 (PR1478),
steph4n-gh (PR1573). Artifact: `research/even-target-cnot-census/` with
`verify.py`, receipts and source pins; reproduce with
`python3 -I -B research/even-target-cnot-census/verify.py`.
Contributed by Aaron Wang with help from opencode. Apache-2.0.
