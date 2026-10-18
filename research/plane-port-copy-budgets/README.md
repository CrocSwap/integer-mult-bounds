# Plane-port coverage law: certified decoder copy budgets on both suppliers

**Planning screen, no new κ, no construction.** The selected record is unchanged.

ctoth's FINDING in [discussion 1587](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-18914510)
shows that a *plane-port* local contract (source E → FULL, target 0 → E⊥ for a plane E = ⟨q, r⟩) leaves two
unpaid coordinates per live family and is exact on small dirty instances. Its first-order estimate says a plane-port
decoder beats the incumbent if its copy charge C per call is below 1472/9 ≈ 163.6. That estimate holds the rest of
the word unchanged and covers the complex side only.

This package prices the same lever exactly, on **both** suppliers, in the predecessors' coverage-law relaxations.
It answers: how large may the decoder's per-call copy charge be, by copy rank, for each target saving?

## Model and premises

- **Engines, imported unchanged and hash-pinned:** `research/complex-local-word-ceiling/ceiling.py` (complex,
  m = 73, w = 896/9, idle cap R = 51) and `research/bit-revision3-levers-seed03/levers.py` (bit, m = 64, w = 888/9,
  idle cap R = 45 as admitted by the record's PR510 row bound, and 53 as the most permissive elementary-cover cap).
  The bit word is the PR589 per-call histogram replayed in that package's `RESULT.json`.
- **Plane-port coverage law:** unpaid = 2, so per-call paid mass is (m − 2)·w + C.
- **Copies:** today's copies (complex 8 rank-8, bit 9 rank-7) are removed. k decoder copies of a single rank
  r ∈ {1, 2, 7, 8} replace them, so C = r·k.
- **Data shrink:** every data incidence climbs one coordinate less (complex 8 → 7, bit 7 → 6). That removes 224
  (complex, 2 × 112) or 222 (bit, 2 × 111) units of local mass per call. Which children shrink is not known, so it
  is bracketed:
  - `unchanged` keeps the shipped word (pessimistic);
  - `shrink` removes the drop as rank-1 children (favorable).
- **All other local children are kept.** Remaining mass goes to idle children at the cap, fractional counts allowed.

**Why the bracket holds.** With f(x) = (x/m)^(1−a), shortening a child from rank r to r − 1 lowers the moment by
f(r) − f(r − 1) ≥ m^(a−1)(1 − a) r^(−a). The freed unit goes to idle at rank R and costs m^(a−1) R^(−a). The removal
wins when (1 − a)(R/r)^a ≥ 1. For r ≤ 8, R ≥ 45 (so ln(R/r) > 1.7) and a ≤ 0.4 this holds, so leaving the word
unchanged never undercounts. Removing whole rank-1 children gives the largest cost removal per unit of mass (f is
concave). Every shrink pattern lies between the two scenarios, provided the plane-port data children are the shipped
ones with ranks lowered.

A budget is the largest integer k whose relaxed moment is certified < 1 at the target saving a*, with k + 1
certified > 1 (the moment increases with k). All numbers are exact rational interval verdicts. As in the
predecessors, **a fail rules out every construction under these premises; a pass is only a necessary target.**

## Results ([RESULT.json](RESULT.json))

Largest per-call copy charge C = r·k (range = `unchanged`–`shrink`; bit at cap 45):

| side | copy rank | tie incumbent ceiling | beat selected endpoint | +10% κ | a = 1/99 |
|---|---:|---:|---:|---:|---:|
| complex | 1 | 162–164 | 162–164 | 159–160 | none |
| complex | 2 | 162–164 | 162–164 | 158–160 | none |
| complex | 7 | 161 | 161 | 154–161 | none |
| complex | 8 | 160 | 160 | 152–160 | none |
| bit | 1 | 160–162 | (already above) | 162–164 | 11–20 |
| bit | 2 | 160–162 | | 162–164 | 10–20 |
| bit | 7 | 161 | | 161 | 7–14 |
| bit | 8 | 160 | | 160 | 8–16 |

Incumbent ceilings: complex 0.001690054, bit 0.001955919 (cap 45). Selected a = κ/(1 − κ) = 0.0016755; +10% κ
gives a = 0.0018433. The bit relaxation already passes +10% with the shipped word, since its ceiling is not tight
(PR1791 measures the actual histogram), so on the bit side only the tie and 1/99 columns constrain.

1. **The first-order break-even survives.** Exact budgets are 160–164 per call on both sides, against
   1472/9 ≈ 163.6. The data shrink is worth at most 2 units at the tie (8 at +10%), and lowering the copy rank from 8 to 1 gains 2 to 8.
2. **The +10% point is only 2 to 8 units below the break-even.** Near C ≈ 160 the deficit 2w − C is about 39
   per call against 35.6 today, so every unit of copy charge moves κ by roughly 3%.
3. **Plane ports alone cannot reach a = 1/99 on the complex side**, even with a free decoder. The complex
   plane-port ceiling at C = 0 is 0.009410 (`unchanged`) to 0.009821 (`shrink`), below 1/99 ≈ 0.010101. The rest
   of the complex word has to change as well. The bit side reaches 1/99 only with C ≤ 7 to 22 (bit C = 0 ceiling
   0.01076 to 0.01128).
4. **ctoth's naive realization (112 rank-2 queries, C = 224) fails every target**, as reported in 1587.
5. **For orientation:** at today's charges (complex 64, bit 63) the plane-port ceilings are 0.006378 to 0.006656
   (complex) and 0.007312 to 0.007666 (bit, cap 45).

## Reproduce

```sh
python3 -B research/plane-port-copy-budgets/verify.py      # prints PASS_PLANE_PORT_COPY_BUDGETS, ~17 s
python3 -B research/plane-port-copy-budgets/verify.py --write   # regenerate RESULT.json
```

Standard library only, Python 3.10+. It refuses `-O`. Checks and controls:

- source sha256 pins for both engines and the bit receipt;
- the selected κ;
- the complex incumbent ceiling 0.001690054 and the bit cap-45 ceiling 0.001955918756 are reproduced;
- the complex idle mass 1646 per call and the bit local mass 5129 per call;
- sharpness of every budget (k passes, k + 1 fails, both certified);
- line-law controls: the complex incumbent passes the selected point and fails +10%; the centre-free complex line
  law passes +10%; the bit incumbent relaxation passes +10% and fails 1/99 at cap 53;
- the recomputed receipt must equal `RESULT.json` byte for byte.

## Scope and limits

- **Not established:** any plane-port decoder, any decoder floor, admission, hosting, precision, or the plane-port
  bit template. The plane-port contract's exactness is ctoth's small-instance check, not re-run here.
- **Premises, not consequences:** that the plane-port word keeps every non-data child of the shipped words, that
  the copy profile has one rank, and the outer recipe and halving-guard caps. A changed A/B or helper word is
  outside scope (point 3 says that the complex side needs one for 1/99).
- **Relaxation only:** the idle remainder is ideally packed and the bit surcharge is omitted.

## Open next questions

1. **Is there a plane-port decoder with C ≤ 160 per call on P112 (complex) and the P111 bit labels?**
   - Why it matters: this is the binding number for the plane-port lever on both sides.
   - First step: @philippeVV's halves in 1587: the per-centre pairing-rank floor dim F − dim(F ∩ E_t⊥) over choices
     of the second plane vector r_t, and small exact decoders priced with this package's targets.
   - Blocker: the plane-port decoder (pairing matrix and term cost on planes) is not yet formally specified.
     ctoth notes that ports may need 2×2 blocks instead of scalars.
2. **Which complex word change, combined with plane ports, reaches a = 1/99?**
   - Why it matters: point 3 shows that plane ports with a free decoder still stop below 0.00982.
   - First step: rerun `ceiling.ceiling(..., unpaid=2)` with rank-16 local children (lever table ×2.31).

## Credit

- **Plane-port contract, first-order break-even and naive realization:** ctoth's 1587 team (Claude Opus 5.5,
  GPT-6 via Codex, Gemini 3.8 Flash).
- **Complex ceiling model:** Douglas Colkitt (`complex-local-word-ceiling`).
- **Bit levers model and PR589 replay:** `bit-revision3-levers-seed03` and its authors.
- **Coverage identity:** PR1012.
- **Decoder question halves:** posed by @philippeVV in 1587.

Prepared by Claude Code (Claude Opus 5.5) for JosieElliston in one donated session; no independent human review.
Apache-2.0.
