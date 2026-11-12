# Fixed-map paid child consolidation stock on #7161

**NO VERIFIED GAIN.** The complete native inventory exhausts **6,279 of 6,279** paid MOVEs with zero pending. The directed saving upper is **0 per stage and 0 over all 17 stages** for the tested whole-output pooling and contact-free serial composition. The independently reproduced #7161 witness used for this census has κ = 0.003644890067940. At κ* = 10018846261809/2500000000000000, the directed raw margin upper is exactly −702586314754571446562148763/5000000000000000000000000, approximately **−140.51726295091429**. [#7161 exact science](https://github.com/Clear1nsight/integer-mult-bounds/tree/e3f8d39c43b07063dfc5b800f71c5d21015259e6/research/p104-rank8-exit-funded-split), [#7113 signed caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)

## The finite census

Authenticate the exact compressed native word, result and signed caller. The reconstructed invoice has 110,519 paid positions and 22,427 productive fields. For each literal MOVE, record the actual role and ownership, source and destination charts, canonical binary spans, dimension difference, nearest earlier and later role contacts, and exact normalized incoming row on 1,499 arbitrary public input fields. The scalar replay preserves `COPY` source and destination incidences and checks that its original destination is zero. `INIT` and `CLEAR` explicitly reset owned rows. Every MOVE has a nonzero row.

There are 2,950 classes by literal or canonical directed source/destination and rank, with maximum occupancy 19. Compute the signed Pauli tableau of the complete quotient (T_G T_F^{-1}) on all nine axes. This groups 2,229 physical quotient classes with maximum occupancy 48. Allow a free global phase correction, since equal signed tableaus determine the operator up to a scalar. The direct quotient's active rank independently agrees with the paid dimension difference. Every class has full rational row rank, including classes containing different source and destination pairs.

## A broader whole-output lower bound

Allow an original MOVE output to be reconstructed from any other already-paid outputs that can be transported to its chart by ordinary whole-factor monomials, even from different sources and ranks. Grant arbitrary scalar linear combinations, all clocks, free holding, free exact monomial adapters, free zero retyping and restoration of the old owner. The target charts (T_A,T_B) share such a class exactly when (T_A^{-1} Z T_A=T_B^{-1} Z T_B) as unsigned Pauli subspaces, where (Z) is the diagonal Pauli subspace. The quotient preserves (Z) precisely in this case, which is equivalent to a Clifford monomial. Canonicalize the resulting binary subspaces exactly.

There are 978 target monomial cosets, with maximum occupancy 1,050. All are full row rank over the rationals, so the cheapest all-clock target basis and chronological target basis each retain all 6,279 paid positions. This uses no assumption that old input values are random or that different owners always hold different values. For each coset, put every desired output in the same ordinary chart and denote the scalar row matrix by R. At any fixed allowed column multiplicity let V be the complete common array space. The map of these outputs is (R\otimes I_V) up to invertible output frames, and its rank is the number of required outputs times dim V. Any reconstruction whose only channels for that coset are its retained whole child outputs has at least this total volume. A wider execution of the same child family costs in proportion to that volume, so merely concatenating complete independent arrays has no exponent credit under the existing interface. Returning a new mixed-rank shared result across distinct cosets, accessing independent free source channels in the reconstruction, or applying paid permutations to selected subarrays changes this contract.

For the serial component, two old MOVEs of the same carrier can telescope to a direct quotient only if no intervening mandatory contact is skipped. Enumerate maximal chains between any source, destination, SCALE, INIT or CLEAR contact, and count each original MOVE once. Every one of the 6,279 chains has length one. The combined upper counts each singleton in its quotient class, so there is no overlap or doubled credit. More general serial fusion across an actual read with compensating support remains the distinct #7171 family. [#7171](https://github.com/CrocSwap/integer-mult-bounds/pull/7171)

At p=1−κ*, each original child retains its original rank-r charge r^p. Give all additional ordinary work, setup, routing, restoration, precision and tape free in the relaxation. Their actual nonnegative charges cannot raise the zero saving bound. The result does not price a new multi-output recursive primitive that changes the full paid family or its shape.

## Verification and next decision

The audit uses the separate signed Pauli interpreter, a different pivot order over the prime field F65537 and independently reconstructed role windows. Every scalar denominator is invertible in the field. Full modular row rank proves full rational row rank. The nonzero-pair, dependent-row and zero controls exercise the rank logic. A one-MOVE cap retains the remaining 6,278 at full possible savings and is inconclusive. The SHA-256 check rejects a changed caller byte. No local site, new child or candidate verifier was launched. Hosted checks were unrun for this scoped result.

Retire fixed-map and target-monomial pooling. The first concrete step for a new complex route is to specify a typed multi-output child across distinct monomial cosets. Write the exact input embedding, output decoder, selected axis sets, simultaneous volume and restoration contract before choosing sites. Price one inventory of eligible *distinct* whole jobs at the recorded per-stage deficit, over 8.26572 raw units. A new route needs both a whole-construction optimistic saving above that deficit and a comparable independent-input interface. The existing zero stock cannot supply either.

## Exact source scope

The word, paid inventory and exclusion in this package are scoped to #7161's scientific commit. The later #7244 proposal uses two additional funded exits and a different paid and productive profile. Its exact head 4156504fa39efb51c550d218a9b94fe69dbce8f6 is a separate candidate. No #7244 word or coefficient check enters this result. [#7244 proposed change](https://github.com/CrocSwap/integer-mult-bounds/pull/7244)

## Clean replay and credit

Use CPython 3.12 with assertions, tested on 3.12.14. From the package directory:

```sh
python3.12 -I -B replay.py
```

The command checks ten path-keyed replay files and supports explicit `--inputs` and `--deps` roots. The default paths are relative to the package. It generates the complete 4,194,679-byte row receipt, checks its frozen SHA-256 `39a33d2ddcff886fd4be1591bcf15f94cc317f1f7aa09a85c3ac6a2529fb09ad` and summary, and runs the independent modular audit on the regenerated data. The 645-byte [AUDIT.json](AUDIT.json) must match byte for byte. The full row output is regenerated on demand and [SUMMARY.json](SUMMARY.json) preserves the scope and seven directed price cases. [Exact sources](SOURCES.tsv) · [Replay hashes](REPLAY.sha256)

To retain every regenerated row for inspection, run:

```sh
python3.12 -I -B stock.py inputs deps --cap 6279 --seconds 600 > stock-replay.json
shasum -a 256 stock-replay.json
python3.12 -I -B audit.py inputs deps stock-replay.json
```

The prior clean replay and cap-one control retain their sealed results. The packaging replay also authenticates the caller before executing the scientific scripts.

Credit Clear1nsight #7161, Rohan Arun #7113, #7165 for exact scalar/native interfaces, #7171 for adjacent across-read serial fusion, and the original and independent Clifford authors. #7207 is adjacent fixed globally independent IDLE coalescing. Original attribution is preserved in [NOTICE](NOTICE), [NOTICE-7161](NOTICE-7161) and [NOTICE-CLIFFORD](NOTICE-CLIFFORD). OpenAI Codex and subagents materially assisted. [#7165](https://github.com/CrocSwap/integer-mult-bounds/pull/7165) · [#7207](https://github.com/CrocSwap/integer-mult-bounds/pull/7207) · [Canonical Clifford review](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)
