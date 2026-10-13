# Final cold verification

The unchanged final package manifest `2b3351b02e4b4e13f0f3c02e5b7c664c01c149f7a85d7f1bcb83709f7fce837a` passed full replay on macOS/Python 3.14.8 in 179.7088 seconds and Linux aarch64/Python 3.12.3 in 229.5120 seconds. Both report κ = 0.001591968902833346.

Every artifact hash in both recorded receipts was checked against these copies. All semantic top-level results and complex canonical-word, emitted-program, phase-recipe and template hashes agree. The bit template's only difference is its geometry hash; the geometry differs only in measured seconds. The expanded bit operator hashes agree. See CROSS-PLATFORM.json; raw bit-template identity is not claimed.

PRELIMINARY-CORRECTIONS.json preserves the initial expected-metadata rejection and its resolution. The final cold runs occurred after both corrections and final documentation/source manifests were frozen. The mathematical audit code was not weakened.

GitHub CI is separate from these observed local/remote runs.
