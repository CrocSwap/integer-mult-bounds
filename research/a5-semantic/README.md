# A contiguous A5 block with the semantic/bulk transfer

The conditional multiplication saving is **κ=11447067/10^12=1.1447067×10^-5 > 2^-17**, about **4.159% above PR23's 1.099×10^-5**. This is an asymptotic exponent comparison, not a practical speedup claim.

The change exposes one width-21 contiguous block already present in icekylinx's PR18 prescribed common basis. Each of the 2N A5 corners previously charged as 47 singleton children now uses **26 singleton children plus widths 21 and 481**; the width-481 child is retained. Physical rank mass, producers, source frames, other profiles and maximum child width remain unchanged.

The [general proof](a5-block.tex) derives the ordered pivots `(i,i+24)` for i=1,...,21 after an exact rank-one cancellation. Existing nonzero-coordinate and tree-minor conditions give one simultaneous rational basis. [Exact rational controls](controls.py) reconstruct four actual corners and test the full Schur formula, ordered pivots, sign convention and two failure modes. Finite samples supplement the general argument.

The unchanged finite quantities permit reuse of **Zhihao Chen's PR23** semantic precision and joint row-stock bridge, including C1=1 and degree 89000, built on **RaD/PR20**. The [new manuscript](../../notes/a5-semantic-note.tex) and [PDF](../../artifacts/a5-semantic-note.pdf) explain this compatibility and the complete 47-constraint assembly. PR21 and PR23 source files and their certificates are retained unchanged and hash checked.

## Exact parameters and checks

The bit saving is a=1144733/10^11, with certified rational moment gap greater than 3×10^-14. The complex saving remains b=18/10^6. Use h=10^-8, beta=1/4, delta=h/8, q=a(1−2h), c=q(1+h), epsilon=(1−h)/(1+c+q), lambda-prime=1−q and lambda=(1−a+lambda-prime)/2. All 47 strict constraints and seven margins pass exact arithmetic; the final absorption gap exceeds 5×10^-13.

The next 10^-12 bit-saving grid point fails the chosen rational upper-enclosure certificate. That does not prove failure of the actual moment or unrestricted optimality. Negative controls also reject omission of the A5 block, reuse of the old quadratic guard or separate-exposure margins, and the next 10^-12 kappa grid point.

```sh
python3 research/a5-semantic/witness.py
python3 -m unittest discover -s tests -p test_a5_semantic.py -v
python3 research/a5-semantic/make_patch.py
make verify
```

[Validation status](validation.json) distinguishes focused checks from the full repository rerun. The [focused patch](../../patches/a5-semantic.patch) applies to the pinned **PR23 source** in [SOURCE.json](SOURCE.json), not the original OpenAI upstream manuscript. Inherited upstream patches remain unchanged. General analytic and fixed-tape proofs remain mathematical dependencies requiring independent review; this is not formal verification.

## Attribution

Rohan Arun, with substantial OpenAI Codex assistance, contributed the newly exposed A5 block, its proof and exact controls, and this composition. The prescribed basis and partial-swap construction are **icekylinx's PR18**. The translated finite interfaces and semantic/bulk composition are **Zhihao Chen's PR21 and PR23**. Semantic precision and bulk resampling are inherited from **RaD/PR20**; source-frame ideas include **eumemic's PR13**. All preceding contributions and AI-assistance notices remain credited in NOTICE. No new producer, complex guard or worldwide priority is claimed.
