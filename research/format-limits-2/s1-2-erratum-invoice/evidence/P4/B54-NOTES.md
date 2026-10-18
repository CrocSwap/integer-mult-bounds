# B54: complex s=9 -> 7 joint with R. VERDICT: KILLED at the gate. ship=false
Tools: work/s7.py (+ B15 calc.py/reg.py copies; B15 files untouched). Model: #626 words (ck/jp8 canonical replay), geometry parametrised by P:
m=1+8(2P+1), W=2PTv, D=T[2Pv-(2P+1)cst], calls=T(2P+1), idle I=calls*8(s-3)*v, per-call local = 1856 + sum w (unchanged by P).
## Gate (tooling): PASSED
P=4 gives 73/7168/2560/72; B15 calc.py reproduces b(#626)=0.0016382067123080868626 (mass identity residual 0.0 at s=9 and s=7).
Own fractional-idle s9 baseline is 1.63872e-3 (+0.03% vs exact B0, idle shape only); all ratios below use the same convention at both s.
## s=7 invoice (56 calls, 8 ck + 48 jp8, m=57, W=5376, D=1792)
- I(7)=200,704. Hz(7)=8*3858+48*3902=218,248. Overflow 17,544 (8.7% of Hz). Per call: ck 3858 / jp8 3902 vs 3584 allowed.
- Cheapest legal treatment = minimal helper cut (mass-neutral). The v4 "unhosted slots" convention is the same b with R unchanged, so it is not a separate price.
- Fit needs k=34.6 w9 helpers cut per call (all calls), R 492 -> ~457 (-7.1%). R* = 0.93 R(#626/#643), so inside the 0.85 line.
- ck alone needs 30.4, jp8 alone 35.3 (ck is the lighter provider; the gain is the 4 helpers, ~0.5% b; #643 moved the other way).
## Gate (economics): KILL
| k cut (R) | b9 vs b9(k=0) | b7 | b7 / b9 same R |
| 35 (457) | +5.04% | 1.7249e-3 | +0.21% |
| 40 (452) | +5.80% | 1.7371e-3 | +0.20% |
| 60 (432) | +8.96% | 1.7877e-3 | +0.13% |
Required b7 >= +3% over b9 at R*: got +0.21%. The decay with k continues: helper-free s7 loses.
Deep k (b x1e3, ovf = hosting overflow impossible, all feasible): k=234 s9 2.412 / s7 2.395 / s5 2.303; k=300 2.783/2.749/2.611; k=480 4.793/4.611/4.108.
So in this model the descent is worse than s9 at every R: D/(mW) +19.5% is eaten by mean ln(m/r) (m 73 -> 57, unit climbs dominate), net -0.7..-3.8%. The "+11.7% helper-free ceiling" is not realised with the #626 local profile; it would need the P=3 local program to have a different (fewer-unit) profile, which is the unpriced template risk.
## Joint table (per w9 helper cut, all calls)
s=9 alone: ~0.14%/helper (+5.0% for 35, matches B15 48-merge 0.137%). s=7: the same 35 cut only buys admission (hosting fits), final b7 = b9 + 0.21%. The switch adds ~nothing beyond the cut; the 35 helpers are worth the same +5% at s=9 with no descent. There is no 3x multiplier.
## s=5 line
I(5)=40*16*v=71,680, Sum w <= 1792 per call, i.e. ~234 w9 helpers cut (R ~258); b5/b9 = 0.955 there, 0.857 at k=480. Dead on this model; B20 skeleton prize does NOT gain from the s descent.
## Caps and credit
Capped at +5.72% (B53, #555): b7 tight (1.7249e-3 vs frontier b 1.6392e-3) is +5.2% only because of the 35 helper cut, which is delivered by nothing; the same cut at s9 gives +5.0%. Without the cut: s=7 infeasible (overflow). Uncapped marginal of s=7 over s=9: +0.2%. Credit from the descent itself: 0.
## Not done
Bank legality in the complex verifier (moot after the gate; verifier pins m=73/D=2560/72 calls). P=3 local program not built; the sign could change only if its local profile is far lighter in unit climbs (rescue: build a P=3 template, owner MIP; not worth it at a 0.2% margin vs a -3.8% model slope).
