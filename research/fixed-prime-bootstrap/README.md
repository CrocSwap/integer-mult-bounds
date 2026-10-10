# Fixed-prime refinement of the five-stage construction

Conditional κ = **354291207342277673841 / 500000000000000000000000 = 7.08582414684555347682 × 10^-4**.

This exceeds PR237's 7.08582410781108 × 10^-4 using its unchanged five-stage geometry and paid finite interfaces. Choose the fixed prime 2^127−1, use the proved rare-class density 2m^3/q in place of 10^-16 while paying the entire fallback, and complete seven finite ordinary bootstrap levels. All prime-dependent costs remain finite paid constants. See [PROOF.md](PROOF.md) for the argument and inherited hypotheses. This is not an unconditional Lean proof of integer multiplication.

Reproduce with Python 3.11 or later:

```sh
git clone https://github.com/CrocSwap/integer-mult-bounds.git /tmp/five-stage-parent
git -C /tmp/five-stage-parent fetch origin af3fe331ca60c936229e060681ffccbc1c208678
git -C /tmp/five-stage-parent checkout --detach af3fe331ca60c936229e060681ffccbc1c208678
git clone https://github.com/CrocSwap/integer-mult-bounds.git /tmp/five-stage-banks
git -C /tmp/five-stage-banks fetch origin a8b0ce212bc9f09353a8161bf8a5cee9cefd600c
git -C /tmp/five-stage-banks checkout --detach a8b0ce212bc9f09353a8161bf8a5cee9cefd600c
python -m pip install -r research/fixed-prime-bootstrap/requirements.txt
python -B research/fixed-prime-bootstrap/verify.py --parent-root /tmp/five-stage-parent --banks-root /tmp/five-stage-banks
make paired-cube-verify
```

The verifier replays all parent stages, checks immutable source pins, verifies two independent rational moment enclosures, records the positive rare density and all fallback children, checks seven acyclic levels and their cutoff gaps, checks all 47 outer constraints, and reproduces `certificate.json`. No historical receipt or numerical experiment is used as proof. Use `--write` only when authoring a new certificate before freezing `SOURCE.json`.

Separately kernel-check prime eligibility with the pinned Lean 4.24.0/mathlib project:

```sh
cp -R research/fixed-prime-bootstrap /tmp/fixed-prime-lean
cd /tmp/fixed-prime-lean
lake update
lake exe cache get Mathlib.NumberTheory.LucasLehmer
lake env lean Prime.lean
```

`#print axioms` discloses dependencies. No `native_decide` or `sorry` is used. Generated `.lake/` and `lake-manifest.json` are excluded from the immutable research package; perform Lean replay in a separate copied package directory so the Python source guard remains strict. CI does this explicitly.
