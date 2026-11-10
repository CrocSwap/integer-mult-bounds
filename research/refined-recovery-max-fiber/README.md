# Exact depth-27 optimum for refined recovery: max fiber = zero fiber

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

**Scoped proof with exact finite corroboration; no κ.** This addresses open
question 1 of Nick Petalas's
[PR6660](https://github.com/CrocSwap/integer-mult-bounds/pull/6660)
(`research/refined-recovery-longer-chains`, head `b6de532e`), which asks for the
exact optimum at t ≥ 27. It also answers open question 1 of
[#6828](https://github.com/CrocSwap/integer-mult-bounds/pull/6828).

**Theorem.** Suppose a frame sequence's zero fiber is within a relative 4.2·10⁻⁴
of its Fourier main term 2^(dim D−4t)·13^(8t), that is, ε₀ ≤ ε*. Then no output
has a larger fiber than 0:

    max_y |fiber(y)| = |fiber(0)|.

**Corollary.** At depth 27,

    min_U max_y |fiber(y)| = (1 + 12ρ₂^25 + 3ρ₂^26) · F^27 ≈ 15.7897746 · F^27,

that is, **696 tag bits**, exactly. This is the first exact value beyond PR6660's
range t ≤ 26. The lower bound is #6828's exact minimum zero fiber. The upper bound
comes from #6828's FRAMES27 frames, whose ε₀ = 5.45·10⁻⁶ is 78 times below the
threshold.

**Why it is not just the box lemma.** For y ≠ 0 the interval boxes of a chain can
depend on its history, and the coupled stage cosets block PR6660's stage-by-stage
count. The proof uses three facts:

1. **Factorization.** The fiber expands over characters h ∈ H^⊥, and each term is
   a product of eight one-coordinate signed chain sums Z_k. The interval at each
   stage depends only on that coordinate's history.
2. **Ties are the only adaptivity.** Without rounding ties, each box is a fixed
   13-interval shifted by an even amount, so |Z_k| equals its value at y = 0.
   With ties, s = 4x+2, and the state follows x ↦ −13x+14r. Only sixteen states
   x ∈ [−8,7] can still meet a 12-element box.
3. **A bound with a matching penalty.** A transfer-matrix analysis with an
   exactly closed interval family on the 1/12 grid gives |Z_k| ≤ (23/12)·13^(zeros)
   at every depth. The constant 23/12 is attained in the limit, and the naive bound
   with constant 1 is false. Every coordinate whose ratio exceeds 1 starts with a
   12-element box, which costs the main term a factor 12/13. That loss outweighs
   (23/12)^8·ε₀ whenever ε₀ ≤ ε*.

See [PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -I -W error -B research/refined-recovery-max-fiber/verify.py
python3.12 -I -O -W error -B research/refined-recovery-max-fiber/verify.py
python3.12 -B scripts/research_package.py --package research/refined-recovery-max-fiber
```

Each run prints `PASS_REFINED_RECOVERY_MAX_FIBER` in under a minute. It checks
the following:

* C and the coset sum ρ₂, derived from the pinned matrix;
* the box lemma for |s| ≤ 3000;
* the transfer matrices against direct chain recursion (|s| ≤ 150, depth ≤ 4);
* the closed interval family (exact rationals), the caps per state, and the
  near-attainment at depth 27;
* the Poisson identity on six random t = 2 instances, with random D and tie
  coordinates;
* ε* and ε₀(t = 27) exactly, and the 696-bit count;
* two controls: the failing naive majorant, and t = 26 direct sums lying outside
  the threshold.

## Limitations

The corollary uses #6828's exact zero-fiber minimum and its FRAMES27.json
realization. Both are open and unmerged, and this package does not replay them.
Like #6828, it also cites PR6660's chain bijection (§2) and PR6327's box facts.
Neither fork commit is reachable here, so SOURCES.json does not pin them.

The theorem needs ε₀ ≤ ε*. It does not cover t ≤ 26 direct sums (ε₀ ≈ 0.0128),
which PR6660 handles by its box lemma. Nor does it cover frames with heavy
overlap. The exact optimum at t ≥ 28 remains open: #6828's floor is not known to
be attained there. The package supplies no codec, physical tag, caller or
restoration cost. κ, the selected frontier and its five assumptions are unchanged.
No independent human or proof-kernel review is claimed.

## Open next questions

1. **Depth 28 and beyond.** Find frames attaining (or approaching) #6828's floor at
   t ≥ 28. If the attaining frames satisfy ε₀ ≤ ε*, this theorem gives the exact
   optimum there too.
2. **Sharper threshold.** Use the per-state caps (13/12 to 23/12) together with
   the actual H^⊥ weight distribution to widen ε*. Then frames with heavier
   overlap would be covered as well.

## Credit

Nick Petalas's PR6660 supplies the chain bijection, the depth law and the open
question. CubeJerry's PR6327 supplies the chain model, F and the box facts. zxv's
#5444 supplies M. #6828 supplies the exact depth-27 zero-fiber minimum and the
FRAMES27 frames. Poisson summation and transfer matrices are classical.
