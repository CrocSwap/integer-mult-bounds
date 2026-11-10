# Refined recovery past depth 26: optimum → 13^(8t)/2^104, exact tag at every depth

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

**Scoped proof with exact finite corroboration; no κ.** This continues
[#6849](https://github.com/CrocSwap/integer-mult-bounds/pull/6849), which
answers [PR6660](https://github.com/CrocSwap/integer-mult-bounds/pull/6660)'s
open question 1 up to a fixed window 1+5.5·10⁻⁶. Here the window closes
exponentially:

    1 ≤ OPT(t)·2^104/13^(8t) ≤ 1 + 5.46·10⁻⁶ · 13^(−4⌊(t−27)/26⌋)      (t ≥ 27)

So the optimal worst-case fiber is asymptotically exactly 13^(8t)/2^104. The
minimum tag is **⌈8t·log₂13⌉ − 104 bits for every t ≥ 27**, with no exceptions.
#6849 left sparse depths open, starting at t = 584,977. Together with PR6660
(ceil(t·log₂F) for t ≤ 26), this completes the tag-size depth law for this
interface.

**How.**

- *Frames.* Run #6828's FRAMES27 first, then cycle PR6660's 26 direct-sum frames.
- *Decay.* Each cycle's images span the whole 104-dimensional space, so every
  nonzero character picks up a codeword of weight at least 4. Each cycle therefore
  multiplies ε₀ by at most 13^(−4).
- *Bound.* #6848 (max fiber = zero fiber) and #6849 (main-term lower bound) then
  give the two-sided bound.
- *Tag sizes.* For 27 ≤ t ≤ 1500 the tag sizes are checked exactly with big
  integers. Above that, a 700-digit continued fraction of 8·log₂13 shows
  ‖t·8log₂13‖ ≥ 10^(−202) for all t < 10^200. That is far above the remaining
  window of 10^(−254.8). For t ≥ 10^200, the explicit two-logarithm bound of
  Laurent–Mignotte–Nesterenko (1995) decays only polylogarithmically, while the
  window decays exponentially.

See [PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -I -W error -B research/refined-recovery-asymptotic/verify.py
python3.12 -I -O -W error -B research/refined-recovery-asymptotic/verify.py
python3.12 -B scripts/research_package.py --package research/refined-recovery-asymptotic
```

Each run prints `PASS_REFINED_RECOVERY_ASYMPTOTIC` in about one second.

## Limitations

The result rests on four cited premises, which are not replayed here:

* PR6660's dimension cap and its 26 direct-sum frames;
* #6828's FRAMES27;
* #6848's max-fiber theorem;
* #6849's main-term identity.

All of these are open and unmerged.

For t ≥ 10^200 the LMN (1995) Corollary 2 bound is cited, not formalized; the
margin is enormous. The exact value of OPT(t) for t ≥ 28 is still known only up
to the shrinking window.

The package supplies no codec, physical tag, caller or restoration cost. κ, the
selected frontier and its five assumptions are unchanged. No independent human or
proof-kernel review is claimed.

## Open next questions

1. **Exact OPT(t) at t ≥ 28.** Minimize ε₀ over the 104-dimensional character
   codes in C^t that frames can realize. The answer pins the second-order term.
2. **Other frame classes.** PR6660's open question 2: does the depth law change
   for mode-changing frames, or for extra refinement between calls?

## Credit

Nick Petalas's PR6660 (direct-sum frames, dimension cap, the question);
CubeJerry's PR6327; zxv's #5444; #6828, #6848 and #6849. The two-logarithm bound is
Laurent–Mignotte–Nesterenko (1995).
