# Refined recovery over longer mode-preserving frame chains

This package answers open question 3 of CubeJerry's
[PR6327](https://github.com/CrocSwap/integer-mult-bounds/pull/6327)
(`research/refined-native-recovery`) for every chain depth. That question
asked for the optimal recovery alphabet of longer parity-changing chains.

The setting is PR6327's. M is the literal 112×8 matrix pinned from #5444.
K(z)=z−M R(Mᵀz/52) uses half-away rounding. The chain is z_1=K(2x),
z_(j+1)=K(U_j z_j), with one precision bit and fixed frames U_j∈GL_112(Z)
satisfying MᵀU_j=Mᵀ and no parity restriction. Put F=51,008,161, PR6327's
one-step maximum.

## Result

**Theorem** (scoped proof with an exact finite certificate):

- For every depth t and every frame sequence, the zero output has at least
  F^t preimages. Equality holds exactly when the t binary images of the
  cumulative framed matrices W_jM form a direct sum.
- When they form a direct sum, every output has at most F^t preimages.
- For this M, all such images lie in one 104-dimensional binary subspace,
  so a direct sum exists only for t≤26. An explicit 26-stage source frame
  sequence attains it.

Hence the optimal worst-case fiber over all mode-preserving frames is
**exactly F^t for 1≤t≤26** and **strictly larger than F^t for t≥27**. The
minimum packed tag is ceil(t·log₂F) bits for t≤26: 26, 52, 77, …, 666 bits.
At t=2 this reproduces PR6327's 52-bit theorem and its separation criterion.
For comparison, PR6327's parity-I chains need ceil(log₂A_t) bits, with
A_t=(13^(8t)+14·13^(4t)+1)/16.

**The new step.** PR6327 shows that its joint Fourier majorant fails for
three quotient parities. The upper bound here does not use a joint majorant.
Under a direct sum, each stage's parity coset is fixed by the output alone.
Conditioning stage by stage then leaves a box of at most 13 values per mode,
and that box holds at most F points of one C-coset. The dimension cap comes
from 2Z^8⊂MᵀZ^112, which puts im(M mod 2) inside the reduction of
ker_Z Mᵀ, a space of dimension at most 104.

[PROOF.md](PROOF.md) gives the argument. [FRAMES.json](FRAMES.json) holds
the 25 sparse integer blocks V_j. The frames are U_j=I+(V_j−V_(j+1))E,
with E the rows 0,1,2,4 of PR6327's construction.
[build_frames.py](build_frames.py) regenerates the blocks deterministically.

## Reproduce

From the repository root, with CPython 3.12 and the standard library only:

```sh
python3.12 -I -W error -B research/refined-recovery-longer-chains/verify.py
python3.12 -I -W error -O -B research/refined-recovery-longer-chains/verify.py
python3.12 -B scripts/research_package.py --package research/refined-recovery-longer-chains
python3.12 -B research/refined-recovery-longer-chains/build_frames.py "$SCRATCH/FRAMES.json"
cmp "$SCRATCH/FRAMES.json" research/refined-recovery-longer-chains/FRAMES.json
```

Each verifier run prints `PASS_REFINED_RECOVERY_LONGER_CHAINS` in under a
second. It checks the following exactly:

- the fixture hash, MᵀM=56I, the code C and F=W_C(13,1)/16;
- that Q(s) is an interval of at most 13 integers on s∈[−4000,4000];
- the box-coset maximum F, over every start parity and coset;
- an integer expression of each 2e_i in source rows;
- the frame blocks: MᵀV_j=0, E V_j=0, and rank 104 of all 26 binary images;
- the inverse identity 2x=Σ W_jMq_j+W_t y on random inputs at depths 3 and 26;
- that the zero-fiber formula reproduces PR6327's A_t for parity-I chains at t=1,2,3.

Controls confirm that a perturbed block breaks MᵀV=0 and a repeated frame
breaks the direct sum.

## Limitations

The all-depth statements are proved in PROOF.md. The finite checks cover the
source facts, the box lemma at maximal length and the explicit frames. The
predecessor's interval lemma (Q(s) has at most 13 elements for every s) is
cited from PR6327's CHAIN_PROOF and only rechecked on a window. For t≥27,
only the strict inequality is proved. The interface assumptions are PR6327's:
fixed known frames, unbounded exact integers and complete output access. The
output function changes with the frames. No codec, physical tag, caller or
restoration cost is supplied. **No κ change.** The selected frontier and its
five assumptions are unchanged. No independent human review or formal proof
kernel check has been done.

## Open next questions

1. **What is the exact optimum at t≥27?** The images must overlap there. The
   zero-fiber kernel formula in PROOF.md Section 5 gives a lower bound for
   each overlap pattern. First step: minimize that sum at t=27 over image
   configurations in the 104-dimensional space. Blocker: with overlapping
   images, stage cosets are coupled, so the stage-wise box bound no longer
   applies as stated.
2. **Mode-changing frames or extra refinement between calls.** First step:
   derive the coupled quotient congruences for one mode-changing frame at
   depth two. Blocker: the per-mode scalar recursion no longer separates.
3. **A physical caller.** Can a caller accept the framed output and use the
   t·log₂F tag at a favorable complete cost? Blocker: no accepting caller or
   restoration invoice is known.

## Credit

This package was produced by Nick Petalas. CubeJerry's PR6327 supplies the
chain model, the scalar interval lemma, the t=2 theorem, the E rows and the
open question. zxv's #5444 supplies the matrix and the one-step code facts.
Ali Romman's #5323 and Brian's #5035 are credited for the same-grid counts
and the rounded kernel, as in PR6327. Character sums over self-dual codes
are classical. New work is Apache-2.0.
