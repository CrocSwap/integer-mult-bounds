# Kernel + early resets on #433's bit word: conditional κ = 0.001133508328719775

κ = 1133508328719775/10¹⁸ = 0.001133508328719775: **+0.414 % over #435** (0.001128832830332521, kernel on R758),
**+0.465 % over #434** (0.001128250848293019, resets), +1.13 % over #433. The bit supplier binds; #433's split-centre complex
supplier (b = 0.001183986549206329) is unchanged.

Bit word: #433's R758 source-centre word → #434's eleven chronological clean resets (R747; #434's own reconstruction,
`vendor/pr434/`, `code/bit_reset.py`) → #417's shared-donor response kernel re-derived on the R747 word (118 entries,
total entrance rank 160, 119 donor slots, no new frames; `code/bit_kernel.py`, `stages/kernel-selection.json`) → #386's
compressed nine-stage geometry with exact mixed-width bank tiling (727 banks per stage; live stock 14,223; deficit 2,496).
Bit lower 0.001134794627881866 (R747 alone: 0.001129525236; R758 + kernel: 0.001130108534).

Verify: `python3 -B research/split-centres-kernel-r747/verify.py /tmp/out` (~30 s) → `PASS conditional kappa 0.001133508328719775`.

Credits: icekylinx (#433), rohanarun / OpenAI Codex (#434 resets), chafreaky (#417 kernel, vendored), ai-nanachi (#426),
Zhihao Chen / jacklightChen (#425, #386), Dylan Crow (#370), J. Sussman (E8); this composition rohanarun with Anthropic Claude.

---

# Conditional κ = 0.001120864952258278

This package combines a split-centre Hamming complex construction with a
source-centre bit construction in compressed nine-stage windows. The resulting
conditional exponent saving is

$$
\kappa=\frac{560432476129139}{500000000000000000}
       =0.001120864952258278.
$$

This is approximately **6.9522% above PR425**. Both components change:

| Component | Helpers | Ambient width | Certified saving |
|---|---:|---:|---:|
| Complex | 560 | 73 | 0.001183986549206329 |
| Bit | 758 | 64 | 0.001122122700265139220566 |

The bit component limits the final assembly. The complex construction removes
coordinate contributions that cancel in the decoder, replacing eight full
centres with eight rank-eight and eight rank-one copies. The bit construction
starts from PR426's R767 word, computes its nine retained forms reversibly in
source rows, and uses PR386's compressed windows.

## Verification

Python 3.11+ and its standard library suffice. Use a new output directory:

```sh
python3 -B research/split-centres-global/verify.py /tmp/split-centres-check
```

The default replays both changed words, reflected/inverse-transpose programs,
bank ownership, costs, two rational moment engines and 47 strict outer
inequalities. Exact complex phase evidence is reused only when the regenerated
canonical word and complete recipe hashes match. To regenerate every selected
Gaussian phase pair as well:

```sh
python3 -B research/split-centres-global/verify.py /tmp/split-centres-full-phases --replay-phases
```

The unchanged historical repository suite and PDF build are not required by
this package. `EXPECTED.json` binds the result to both emitted global templates;
`MANIFEST.json` binds the package files; `SOURCES.json` pins imported sources.

## Scope

[PROOF.md](PROOF.md) supplies the changed finite construction. The all-size
compressed-window and correlated dirty-bank semantics, recursive compiler,
restored-work/tape/common-grid precision, and analytic transfer interfaces remain
conditional. This does not claim unchanged legacy gx/gxcore acceptance, a new
Lean proof, or an unconditional multiplication theorem.

Contributor history and AI assistance are recorded in [NOTICE.md](NOTICE.md).
Original notices and the inherited proofs are retained separately.
