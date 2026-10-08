# Exact scalar 16 × 16 circuit: portable replay

The serialized circuit has 2,208 mixed-input scalar product gates in 512 variables. Each of its 256 output numerator polynomials equals eight times the corresponding classical matrix-product entry, including exact cancellation of all A–A and B–B terms. All gates are nonzero and used. This independent executable certificate is separate from the actual Lean construction and its public proof-scope records under `evidence/`.

Use Python 3.10 or later. The two tools use only the standard library; they do not install packages, import the donor implementation, invoke Lean or call resource guards. Run the commands below from the **project root**, the directory containing `verify_flat16_polynomials.py`, `generate_flat16_circuit.py`, `lean/` and `circuit/`.

## Verify the retained circuit

```sh
python verify_flat16_polynomials.py circuit/flat16_2208_integer_circuit.json --expected-sha256 f265866665cb707a463b39c067875af9e7d6bedac82a8377c10d217e7ccc922f --receipt circuit/new_independent_replay.json
```

The verifier independently expands every output using integer dictionaries and unordered variable pairs. It compares the complete quadratic polynomial, including pure A–A and B–B terms, with `8 * sum_k A[r,k]B[k,c]`. It writes a receipt only after all checks pass and refuses to replace an existing receipt. Choose a new receipt filename for each replay. The historical circuit and historical first verification receipt are unchanged.

## Regenerate from public inputs

```sh
python generate_flat16_circuit.py --output circuit/new_generated_circuit.json
```

The public generator reads only `input/outer48_exact_rational_and_integer_data.json`, `lean/Outer48Data.lean` and the sanitized `evidence/actual_nine_sources_35_standard_public_projection.json`. It verifies their exact hashes, reads the actual Outer48 PASS source/projection binding and checks that the Lean integer coefficient tables equal the extracted mathematical data. Private raw invocation receipts are not required. The exact P/R/Q/M mathematical generation loop is unchanged from the original generator; `portable_python_replay_preparation.json` and `portable_generator_path_provenance_only.diff` disclose the path/provenance adapter.

Generation prints the **actual SHA-256 of the new file**. Use that value in a separate verification command:

```sh
python verify_flat16_polynomials.py circuit/new_generated_circuit.json --expected-sha256 ACTUAL_PRINTED_SHA256 --receipt circuit/new_generated_replay.json
```

Timestamps and public provenance fields may change the file digest. Mathematical gates, coefficients, variable order and output rows must match the retained circuit. This was actually checked for the prepared public payload, not inferred from successful generation.

## Coordinates and fixed reconstruction

- `A(r,c)` is variable `16*r+c`; `B(r,c)` is `256+16*r+c`.
- Full row/column coordinates use `4*outer_coordinate + inner_coordinate`.
- Gate ID is `46*outer_term + leaf_gate`.
- Leaf order is P[8], R[8], Q[6], M[24]. For `i=0..3`, `h=0..1`, `j0=0..2`, the indices are `2*i+h`, `8+2*i+h`, `16+3*h+j0` and `22+3*(2*i+h)+j0`.
- Inner contraction coordinate is `2*h+Bool`; the distinguished column is zero and the others are `j0+1`.

The exact identity is `sum(output_numerator[o,g] * left[g] * right[g]) = 8 * (A*B)[o]`. The scalar polynomial semantics require commutativity. Recovery by fixed division requires eight invertible, implied by two invertible; the actual core Lean theorem uses that ring domain. No tensor-rank-2,208, optimality, numerical-stability, speed or global-priority claim follows.

## Actual portable checks and provenance

`portable_replay_original_actual.json` records a fresh independent check of the unchanged retained circuit. `portable_replay_regenerated_actual.json` records a fresh independent check of the newly generated temporary circuit. `portable_regeneration_content_identity_actual.json` records literal equality of all 2,208 gate forms and all 256 output coefficient rows. `../portable_public_replay_manifest.json` supplies their hashes without machine paths. The temporary generated circuit is a reproducibility check, not a second algorithm.

The independent verifier is copied byte-for-byte, SHA-256 `8189b5655e0ce3d4e77ea9fc16b435e11925f6ada5b87a11b2d6b0c1c3030846`. The original generator hash is `c3b501f5ed92e3f90fa5210e941283a91b745d17671a3a552552c41fc7a48efe`; the portable path/provenance adapter hash is `971d4b3daa8342cd22058386ba08310f48f667269c8249cad39554118654466e`.

The coefficient facts originate in the [pinned spicylemonade reference](https://github.com/spicylemonade/faster_16x16/blob/7743ee6848ed876615012c4edb3bc46a1f870afd/main.py), with the outer attributed to Dumas, Pernet and Sedoglavic. The leaf is [Rosowski's known division-free construction](https://arxiv.org/html/1904.07683v2). The original Archivara Research Team implementation/manuscript and Alejandro's subsequent generalization, certificate extraction and formalization keep their respective attribution. No donor executable code or integer-truncating test routine is shipped by these tools.
