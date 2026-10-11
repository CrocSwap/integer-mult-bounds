# validate715 NOTES (independent validator of R715; Sonnet; Oct 11)
SP=/private/tmp/claude-501/-Users-mason-yarl/378ef358-ade1-45de-8708-27df77339c28/scratchpad ; V=$SP/brain/validate715
Word chain: f2cancel/R715_FP_final.json.gz (md5 de87b3a8..., R=715, pre-kernel bitE8/1) -> kern3 (k/fprg_k3.json.gz, entrances/kernel) -> mix_target_g (w11/fprgm/mx/word-mixed.json, sha256 d3796767...).
Copies in V/copy (originals untouched). My tools: loadh.py (stub unpickler, no producer code), rekid_check.py, rekid_word_trace.py, chain.sh+chk_status.py, checkword_relaxed.py, mutants.py, tape_check.py. Logs in V/logs.
## Results (all independent re-runs)
1. checkword.py (PR370/#443/#436 identical file, md5 dafdc46f): R715 final PASS (955 cols, 947 frames Gram>0, five-stage saving 9.8060969e-4 vs R740 9.6322703e-4).
   stock checkword cannot run on kernel words (asserts y/helper start frame 0 + 'dirt compensation at frame 0'): checkword_relaxed.py drops exactly those two asserts -> k3 and mixed PASS (955 columns, 960 frames Gram>0, y at frame 0 at scatter, finals); price block n/a for kernel words.
   zsh gotcha: INC="-I.. -I.." unquoted does not word-split in zsh (first compile failed on boost include) -> use separate vars.
2. C++ (built from parent436 sources, g++-16): legality PASS (9 COPY / 9 ERASE), columns_h RHELP=715 PASS 1195 cols, columns_k KPAIRS=5 (eleven-stage) PASS 1915 cols, 11 stages, 2880 bridge additions, 24/24 omitted-bridge controls rejected, mutate_records 6/6 rejected, Gram 969 frames PASS: on BOTH k3 and mixed words.
3. rekid: rekid_check.py. 11 rules differ from rebuilt pre-rekid base (710,1072,1077,1078,1082,1083,1085,1087,1090,1094,1231); 8 genuinely cancel (overlap 1-2 sources), 3 are overlap-free re-associations. All legal (content, acyclic, frame(x),frame(y) in frame(w) == join, consumers above, cap containment, targets XOR 63-line cap). rekid_word_trace: each realised by exactly one A gate in the emitted word.
4. mixing: regenerated mixed word byte-identical; mix_check PASS + 4/4 stock mutants rejected; my X1 (non-common frame), X2 (dropped preconditioner), X3, X4 families 84/84 each rejected (python replay), C++ legality rejects X1, columns_h rejects X2.
5. tape_check.py: R=715, profile identical, W=1200, deficit 408, c=1.28512873989e-3 (claimed 642564369945714399381/5e23), digest matches.
## Extras / controls
- relaxed checkword controls: #443's own kernel word passes it (980 cols); dropping one A gate -> ('target',41) rejected; incomparable frame on an A gate -> 'frame not nested' rejected.
- rekid_check negative controls (cycle, wrong operand, shrunken frame[w], read outside cap) all flagged.
- carriers (word level, helper registers ever holding a pure single x_s): R740 272 (112x2 + 8x6) -> R715 240 (120x2): claim (a) confirmed.
- full reproduction: run11w.sh on k3 + iso (rerun/w11): same mixed word, same HiGHS selection, same template/program sha256, kappa 1.265848755025708e-3 complex-bound, bit 1.2851287399e-3.
- caveats (not defects): stock checkword cannot take kernel words (asserts start/after-D frame 0) -> relaxed copy; kappa is complex-bound (R715 adds 0 lemma-less); conditional on inherited PR442 idle-hosting interface/cover assumptions; pre-kernel final word fails columns_h (known, nesttax notes).
## VERDICT: VALID
