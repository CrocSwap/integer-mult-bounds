# Receipt: register-level retiming package

Fresh output of `python3 -B research/five-stage-gen4-deep-retiming/verify.py` (553 s, Python 3.13,
sympy 1.14.0): status `PASS_IMMUTABLE_PARITY_FUSED_GEN4_FIVE_STAGE_BANKED_CONSTRUCTION`, all nine
mandatory stages fresh, package inputs unchanged, manifest sha256
`de1588de46d957e6a53e2b42e42686c78c6d19637a40a74d9ebd12b29fe063a5`.

κ = 144727257636539/200000000000000000 = 7.236362881826950e-04 (bit supplier binding; bit coarse
362080158564507/500000000000000000). The unmodified PR279 package was replayed in the same environment
and reproduced κ = 90446448750933/125000000000000000. The receipt is finite replay, not a formal proof of
the multiplication theorem; the PR279 conditional scope is unchanged.
