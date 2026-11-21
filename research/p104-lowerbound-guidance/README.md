# p104-lowerbound-guidance

Follow-up guidance for the swarm on the P104 lower-bound programme, built on the toolkit of PR #7852 (referred to as #7852). It states the open targets precisely, ships the exact witnesses and certificates behind them, and carries our lane notes and scripts as data. No kappa claim. Labels: [P] proved (Lean name where one exists), [C] computed exactly, [CONJ] conjecture.

## Layout
- `OPEN-PROBLEMS.md`: one section per open target (a) NET-D56 in drop form, (b) R side, (c) caller mid-k window, (d) loose decoder rows, (e) general decoder wall; each with the exact statement, strongest partial result and data location. Includes the CERTKIT source-identity open item.
- `CORRECTIONS.md`: statements in the lane notes that were later refuted or withdrawn. Read it before the notes.
- `certs/`: exact weak-duality certificates, stdlib verifiers (pricing DP included).
  - `q0_k71/72/73.json` + `verify_q0.py` [C]: Q = 0 full-LP duals (exact rationals): k72 128.8500719 and k73 128.6813251 (below 128.891), k71 129.0372595 (above). Conditional LP bounds: RC2 is [P] (Lean), the other rows are paper-[P]. This supplies the dual values that the cc2/cert73 logs did not store.
  - `q1_k*.json` + `verify_q1.py` [C]: Q >= 1, e = 0 thin-column LP, k = 13, 76..100, 110, 120 (k >= 77 below the bar, k76 above).
- `data/`: `q0_callers/` (15 legal tight Q = 0 words, k = 3..13, `check_all.py` replays each at 4 q with symbolic D and checks chat), `direct_sum/` (tightness witnesses: direct sums of C1; HP(327) < chat(C1)), `tight55_gap/` (symmetry-breaking gap witnesses, a SAT-methodology note). Other witnesses are run from `code/`: R = 2 < mass 3 run `code/ctcover/ctsplit.py`, DECOMP word `code/decomp/dc1.py`, ZIGZAG network `code/unify/zzcx.py` (recorded output `code/unify/evidence/zzcx.log.txt`; the full run is long).
- `notes/<lane>.md`: all NOVEL-wave lane notes, scrubbed of local paths; `notes/INDEX.md` has one line per lane. They are as written at the time and are not individually re-audited; `CORRECTIONS.md` takes precedence.
- `code/<lane>/`: our own lane scripts (python, shell, C) and small evidence logs (large CNFs, proofs, pickles and logs were left out). Scripts are research code: some read inputs or sibling lanes that are not shipped, some need numpy/scipy/mpmath and paths relative to the lane directory; none of it is run by `verify.py` except the three stdlib witnesses above.
- `lean_extra/`: 11 Lean sources written the same day that are NOT in #7852 (CallerGram, CallerAdj, CallerSupport, CallerDecomp, SplitBound, BlockCompleteT, Price7Pkg, PriceHI16..19). Sources only, not rebuilt in this package; they are token-scanned by `verify.py` (no sorry/native_decide/axiom/opaque/unsafe outside comments). Kernel-check status is that of the lane logs, not re-established here.

## Sharing, in three lines
[P] On every side cost >= the level-cut sum (D: DX cut; carriers: relay-blind; R: through the dual; caller: CROSS/DYADIC/RC2): sharing is free up to the rank of a level slice, never beyond. The level wall and CT-COVER are refuted [C]. The single open question is a network-coding gain on Q96 (slices of rank >= 9): NET-D56 in drop form, ChainWall56@Q96 or a 2-adic tensor bound.

## Checks
`python3 -I -B verify.py` (stdlib, about 1 minute): file pins both directions, lean_extra token scan, scrub scan, both certificate verifiers, the Q = 0 word replays, direct-sum and symmetry-gap witnesses, the R = 2 run and DECOMP word.

## Open next questions
- Network-coding gain on Q96: NET-D56 in drop form (prove JUNK-PAYS-inv or find a legal -I@Q96 network with D <= 55) and, for the R side, ChainWall56@Q96 or a 2-adic tensor bound. See `OPEN-PROBLEMS.md` (a), (b).
- Caller mid-k window k = 5..71 (Q = 0) and k = 5..76 (Q >= 1): a law or construction between the built words (chat <= 115.43) and HP(k) (up to 143.27); a tightness-free Q = 0 law. `OPEN-PROBLEMS.md` (c).
- Loose B-linear rows (d), the general decoder wall (e), and the CERTKIT source-identity theorem (#7864).

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
